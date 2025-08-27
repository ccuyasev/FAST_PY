from typing import List
from TSN.Device.Component.Slot import Slot
from TSN.Device.Component.Queue import Queue, TTQueue, AVBQueue
from TSN.Constants import *

class Port:
    def __init__(self, id: int, owner):
        """_summary_

        Args:
            idSL (float): _description_
            sdSL (float): _description_
            credit_max (float): _description_
            credit_min (float): _description_
            bandwidth (float): _description_
            p_GCL (float): period
            GCL (List[TT]): _description_
        """
        self.id = id
        self.owner = owner
        
        self.bandwidth = BANDWIDTH       # 1Gbps
        self.to = None
        self.preemption = PREEMPTION_MODE
        
        # 抢占 开销 24B
        self.OH = 24 * 8 / self.bandwidth
        
        # 非抢占 保护带大小 1542B 最大帧
        self.GB_size = 1542 * 8
        self.GB: List['Slot'] = []
        
        self.GCL: List['Slot'] = []

        # 默认队列
        config_avb_a = {
            "bandwidth": BANDWIDTH,
            "idSL": 600,
            "sdSL": 600 - BANDWIDTH,
            "credit_max": 10000,
            "credit_min": -10000
        }
        
        config_avb_b = {
            "bandwidth": BANDWIDTH,
            "idSL": 300,
            "sdSL": 300 - BANDWIDTH,
            "credit_max": 10000,
            "credit_min": -10000
        }
        self.queues = [TTQueue(), AVBQueue(config_avb_a), AVBQueue(config_avb_b), Queue()]
        

    def set_avbqueue_config(self, config):
        self.queues
        
    def set_GCL(self, p_GCL: float, GCL: List['Slot']):
        self.p_GCL = p_GCL
        self.GCL = GCL
        self.compute_GB()
        
    def add_GCL(self, slot: Slot):
        self.GCL.append(slot)

    def add_flow(self, flow):
        if flow.__class__.__name__ == "AVBFlow":
            self.queues[flow.priority].add_flow(flow)
        elif flow.__class__.__name__ == "TTFlow":  
            self.queues[TT].add_flow(flow)
        
    def add_flows(self, flows):
        for flow in flows:
            self.add_flow(flow)
    
    def compute_GB(self):
        for i in range(len(self.GCL)):
            L = self.GB_size / self.bandwidth
            o = (self.GCL[i].o - L + self.p_GCL) % self.p_GCL
            # # 防止保护带越界
            # if i == 0:
            #     o_ = (self.GCL[-1].o + self.GCL[-1].L) % self.p_GCL
            # else:
            #     o_ = self.GCL[i-1].o + self.GCL[i-1].L
                
            # if o < o_:
            #     o = o_
            #     L = (self.GCL[i].o - o)  % self.p_GCL

            self.GB.append(Slot(o, L))
            
    def print_info(self):
        if self.to is None:
            return
        print(f"{self.owner}-{self.id} to {self.to.owner}-{self.to.id}")
        if self.GCL == []:
            return
        print(f"GCL period: {self.p_GCL}")
        print("GCL:")
        for slot in self.GCL:
            print(slot, end=", ")
        print()

            
    def __repr__(self):
        return f"Port {self.owner}-{self.id}"