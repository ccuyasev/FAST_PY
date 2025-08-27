
from TSN.Device.Component import Slot
from TSN import Topology
from TSN.Flow import AVBFlow, TTFlow,  Flow
from typing import List
import networkx as nx
import random
from TSN.Constants import *
from TSN.Device import EndSystem
import math

def normalize_dict(d: dict):
    min_value = min(d.values())
    max_value = max(d.values())
    if max_value == min_value:
        return {k: 1 for k in d.keys()}
    return {k: (v - min_value) / (max_value - min_value) for k, v in d.items()}
        

def get_p_GCL(flows):
    p_GCL = 1
    for f in flows:
        p_GCL = lcm(p_GCL, f.period)
    return p_GCL
    
def lcm(a, b):
    return abs(a * b) // math.gcd(a, b)

def random_flow(num, priority, ESs: List['EndSystem'], periods = [1000, 2000, 4000, 8000]):
    flows = []
    for i in range(num):
        length = random.randint(64, 1500) * 8
        period = random.choice(periods)
        ddl = random.choice(periods)
        
        src = random.choice(ESs)
        dst = random.choice(ESs)
        while src == dst:
            dst = random.choice(ESs)
        if priority == TT:
            f = TTFlow(i, length, period, ddl, src, dst)
        else:
            f = AVBFlow(i, length, period, ddl, src, dst, priority)
        flows.append(f)
    return flows


# 区间排序合并

def merge_slots(slots: List['Slot']) -> List['Slot']:
    if len(slots) <= 1:
        return slots
    slots.sort(key = lambda x : x.o)
    res = []
    st = slots[0].o
    ed = st + slots[0].L
    for i in range(1, len(slots)):
        slot = slots[i]
        if slot.o > ed:
            res.append(Slot(st,  ed - st))
            st = slot.o
            ed = slot.o + slot.L
        else:
            ed = max(ed, slot.o + slot.L)

    res.append(Slot(st,  ed - st))
    return res

def init_DAG(flows: List[Flow]):
    DAG = nx.DiGraph()
    # 根据所有流的路径，每一跳为一个节点，构建DAG
    for f in flows:
        hops = f.hops
        if len(hops) < 2:
            DAG.add_node(hops[0])
        else:
            for i in range(len(hops) - 1):
                DAG.add_node(hops[i])
                DAG.add_node(hops[i+1])
                if not DAG.has_edge(hops[i], hops[i+1]):
                    DAG.add_edge(hops[i], hops[i+1], flows = [f])
                else:
                    DAG[hops[i]][hops[i+1]]['flows'].append(f)
                    
    return DAG   

def toposort_DAG(DAG: nx.DiGraph):
    computeRoute = list(nx.topological_sort(DAG))
    return computeRoute
class Compute:
    def __init__(self, G: Topology):
        self.G = G
        
    def compute_shortest_routes(self, flows: List[Flow]):
        G = self.G
        # 清空原始GCL
        for device in G.G.nodes:
            for port in device.ports:
                port.GCL = []
                port.GB = []
                port.queues[TT].flows = []
                port.queues[AVB_A].flows = []
                port.queues[AVB_B].flows = []
        
        for f in flows:
            route = nx.shortest_path(G.G, f.src, f.dst)
            f.set_route(route, G)
            
        self.update_ports_flows(flows)
        # return flows
    
    def update_ports_flows(self, flows: List[Flow]):
        G = self.G
        for f in flows:
            for i in range(len(f.route) - 1):
                link = G.links[(f.route[i], f.route[i+1])]
                port_from = link[0]
                port_from.add_flow(f)
    
    def update_ports_GCL(self, flows: List[TTFlow], p_GCL: float):
        """ 根据调度结果更新端口的GCL和GB

        Args:
            flows (List[TTFlow]): _description_
        """
        G = self.G
        # 清空原始GCL
        for device in G.G.nodes:
            for port in device.ports:
                port.GCL = []
                port.GB = []
                
        for f in flows:
            for hop, offset in f.offset.items():
                link = G.links[hop]
                port_from = link[0]
                for i in range(p_GCL // f.period):
                    port_from.add_GCL(Slot((offset + i * f.period) % p_GCL, f.pdelay))
                
        # 合并GCL
        for device in G.G.nodes:
            for port in device.ports:
                port.p_GCL = p_GCL
                # port.GCL = merge_slots(port.GCL)
                port.compute_GB()

