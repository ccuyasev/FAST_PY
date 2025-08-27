
from TSN import Topology
from TSN.Flow import TTFlow
from Schedule.Compute import lcm
from typing import List
import z3

class ILPChecker():
    def __init__(self, G: Topology, flows: List['TTFlow']):
        self.G = G
        self.flows = flows
        self.membound = flows[0].src.membound
        
    # 添加调度变量
    def add_schedule_variable(self):
        for flow in self.flows:
            flow.syb ={}
            for i in range(len(flow.hops)):
                hop = flow.hops[i]
                flow.syb[hop] = z3.Int(f"{flow.id}-{i}")

    # 为流添加约束
    def add_flow_constraint(self, solver: z3.Solver, f_i: TTFlow, scheduled_flows: List[TTFlow]):
        solver.add(f_i.syb[f_i.hops[0]] < f_i.period)
        if solver.check() != z3.sat:
            f_i.print_info()
            print('Flow', f_i.id, ': offset at', f_i.hops[0],'is invalid')
            return solver, False  
        
        for hop_i in f_i.hops:         
            solver.add(f_i.syb[hop_i] >= 0)
            if solver.check() != z3.sat:
                f_i.print_info()
                print('Flow', f_i.id, ': offset at', hop_i,'is negative')
                return solver, False  
            
            # 多周期业务流无冲突约束
            for f_j in scheduled_flows:
                for hop_j in f_j.hops:
                    if hop_i == hop_j:
                        lcm_period = lcm(f_i.period, f_j.period)
                        a_range = lcm_period // f_i.period
                        b_range = lcm_period // f_j.period

                        for a in range(a_range):
                            for b in range(b_range):
                                solver.add(z3.Or(
                                            (a * f_i.period + f_i.syb[hop_i]) % lcm_period >=
                                            (b * f_j.period + f_j.syb[hop_j] + f_j.pdelay) % lcm_period,
                                            (b * f_j.period + f_j.syb[hop_j]) % lcm_period >=
                                            (a * f_i.period + f_i.syb[hop_i] + f_i.pdelay) % lcm_period
                                        ))
                                if solver.check() != z3.sat:
                                    f_i.print_info()
                                    f_j.print_info()
                                    print('Flow', f_i.id, 'and Flow', f_j.id, 'conflict at', hop_i)
                                    return solver, False
                        break
                    
                    
        for hop_i, hop_j in zip(f_i.hops[:-1], f_i.hops[1:]):
            # 路径依赖约束
            solver.add(f_i.syb[hop_j] >= f_i.syb[hop_i] + f_i.pdelay)
            if solver.check() != z3.sat:
                f_i.print_info()
                print('Flow', f_i.id, 'does not satisfy path dependency conflict at', hop_i, hop_j)
                return solver, False
            
            # 缓存占用约束
            solver.add(f_i.syb[hop_j] - (f_i.syb[hop_i] + f_i.pdelay) <= self.membound)
            if solver.check() != z3.sat:
                f_i.print_info()
                print('Flow', f_i.id, 'does not satisfy memory bound conflict at', hop_i, hop_j)
                return solver, False
            
        # 端到端时延约束
        solver.add(f_i.syb[f_i.hops[-1]] + f_i.pdelay - f_i.syb[f_i.hops[0]] <= f_i.ddl)
        if solver.check() != z3.sat:
            f_i.print_info()
            print('Flow', f_i.id, 'does not satisfy end-to-end delay constraint')
            return solver, False
        
        return solver, True

    
    def check(self):
        flows = self.flows
        scheduled_flows = []
        self.add_schedule_variable()
        solver = z3.Solver()

        # 为每个流添加约束
        for f in flows:
            for hop in f.hops:
                solver.add(f.syb[hop] == f.offset[hop])
            solver, flag = self.add_flow_constraint(solver, f, scheduled_flows)
            if not flag:
                return False
            scheduled_flows.append(f)
            
        return True