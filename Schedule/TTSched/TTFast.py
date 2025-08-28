
from typing import Dict, List
from Schedule import Schedule
from TSN import Topology
from TSN.Topology import HOP
from TSN.Flow import TTFlow
from TSN.Constants import *
import networkx as nx
from Schedule.Compute import init_DAG, toposort_DAG, get_p_GCL, normalize_dict

    
def process_result(flows: List['TTFlow'], slot: int):
    for f in flows:
        for hop in f.hops:
            f.offset[hop] *= slot
        f.delay = f.offset[f.hops[-1]] - f.offset[f.hops[0]] + f.pdelay

            
class TTFast(Schedule):
    def __init__(self, G: Topology, flows: List['TTFlow']):
        self.G = G
        self.flows = flows
        for f in flows:
            f.status = FLOW_SCHEDULABLE
        
        self.membound = flows[0].src.membound
        self.slot = SLOT_SIZE
        self.p_GCL = get_p_GCL(flows)
        
        self.DAG = init_DAG(flows)  # 初始化调度 DAG
        
        self.slots_status: Dict[HOP, List[bool]] = {v: [False for _ in range(self.p_GCL//self.slot)] for v in self.DAG.nodes}
        
        # 维护调度信息
        self.urgency: Dict['TTFlow', int] = {} # 紧急程度
        self.accumu: Dict['TTFlow', int] = {}  # 累计延迟
        self.remain: Dict['TTFlow', int] = {}  # 剩余最小延迟

    def get_flows_on_hop(self, h: HOP):
        p = self.G.links[h][0]
        flows: List['TTFlow'] = p.queues[TT].flows
        flows = [f for f in flows if f.status == FLOW_SCHEDULABLE and f in self.flows]
        return flows
        
    def is_conflict(self, f: TTFlow, h: HOP):     
        p_GCL = self.p_GCL
        a_range = p_GCL // f.period
        for i in range(a_range):
            offset = f.offset[h] % (f.period // self.slot) + i * f.period // self.slot
            if self.slots_status[h][offset]:
                return True
        return False

    def get_accumu(self, f: TTFlow, h: HOP):
        # 计算 f 在 h 上的累计延迟
        idx = f.hops.index(h)
        if idx == 0:
            return 0
        else:
            return f.offset[f.hops[idx-1]] - f.offset[f.hops[0]] + 1
        
    def get_remain(self, f: TTFlow, h: HOP):
        # 计算 f 在 v 上的剩余最小延迟
        idx = f.hops.index(h)
        return len(f.hops) - idx
    
    def compute_urgency(self, h: HOP):
        # 计算当前端口上的流的紧急度
        flows = self.get_flows_on_hop(h)
        slot = self.slot
        
        for f in flows:
            self.accumu[f] = self.get_accumu(f, h)
            self.remain[f] = self.get_remain(f, h)
            self.urgency[f] = f.ddl // slot - (self.accumu[f] + self.remain[f])
 
    def sort_urgency(self, h: HOP):
        """根据紧急度对 h 进行排序"""
        flows = self.get_flows_on_hop(h)
        flows.sort(key=lambda f: self.urgency[f])
        
    def update_slot_status(self, f: TTFlow, h: HOP, status=True):
        p_GCL = self.p_GCL
        a_range = p_GCL // f.period
        for i in range(a_range):
            offset = f.offset[h] % (f.period // self.slot) + i * f.period // self.slot
            self.slots_status[h][offset] = status
            
            if f.hops.index(h) == 0:
                # 终端要的发送时间点间隔要大于gap_send
                gap_size = h[0].gap_send // self.slot
                for j in range(gap_size):
                    self.slots_status[h][(offset + j) % (self.p_GCL//self.slot)] = status


    def schedule_hop(self, h: HOP):
        """调度 hop h 上的流"""
        flows = self.get_flows_on_hop(h)
        
        for f in flows:
            # 如果 f 无法调度
            if self.urgency[f] < 0 or (self.urgency[f] == 0 and f.hops.index(h) != len(f.hops) - 1):
                f.status = FLOW_UNSCHEDULABLE
                continue
            
            # 初始化 offset 范围
            if f.hops.index(h) == 0:
                offset_st = 1 # 预留1 slot给 给端系统发送
                offset_ed = f.period // self.slot - 1                    
            else:
                h_pre = f.hops[f.hops.index(h) - 1]
                offset_st = f.offset[h_pre] + 1 + h[0].process_delay // self.slot
                offset_ed = offset_st + min(self.urgency[f], self.membound // self.slot)
                
            # 找到第一个不冲突的 offset
            for o in range(int(offset_st), int(offset_ed) + 1):
                f.offset[h] = o
                if not self.is_conflict(f, h):
                    break

            # 更新 slot status
            if not self.is_conflict(f, h):
                self.update_slot_status(f, h)
            else:
                f.status = FLOW_UNSCHEDULABLE
        
    def schedule(self):
        """执行 FAST 调度算法"""
        flows = self.flows
        computeRoute = toposort_DAG(self.DAG)
        for h in computeRoute:
            self.compute_urgency(h)
            self.sort_urgency(h)
            self.schedule_hop(h)

        process_result(flows, self.slot)
        
    def select_edge_to_remove(self, cycle):
        """返回环中最紧急的边"""
        urgency_on_edges = {}
        
        for edge in cycle:
            hop_from = edge[0]
            hop_to = edge[1]
            port = self.G.links[hop_from][0]
            flows = [f for f in port.queues[TT].flows if f.status == FLOW_SCHEDULABLE and hop_to in f.hops and f in self.flows]
            if len(flows) == len(self.flows):
                continue
            urgency_on_edges[edge] = sum([f.ddl / len(f.hops) for f in flows]) / len(flows)
        
        return max(urgency_on_edges, key=urgency_on_edges.get)                 

    def run(self):
        while self.flows != []:
            # 检查并打破所有环
            flows_rb = []
            while True:
                try:
                    cycle = nx.find_cycle(self.DAG)
                except nx.NetworkXNoCycle:
                    break  # 没有环，跳出循环

                # 选出一条要删除的前序边
                edge_to_remove = self.select_edge_to_remove(cycle)
                
                # 给前序边上的流标记为 FLOW_BREAKING_RING
                h_u, h_v = edge_to_remove
                port = self.G.links[h_u][0]
                flows_rb += [f for f in port.queues[TT].flows if f.status == FLOW_SCHEDULABLE and h_v in f.hops and f in self.flows]
                for f in flows_rb:
                    f.status = FLOW_BREAKING_RING
                
                # 删除前序边
                self.DAG.remove_edge(h_u, h_v)
            
            self.flows = [f for f in self.flows if f.status == FLOW_SCHEDULABLE]
            self.schedule()
            self.flows = flows_rb
            for f in self.flows:
                f.status = FLOW_SCHEDULABLE # 恢复状态
            self.DAG = init_DAG(self.flows)
            print("Breaking ring flows:", len(self.flows))
