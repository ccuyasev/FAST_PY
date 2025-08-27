from TSN.Flow.Flow import Flow
from TSN.Device.Switch import Device
from typing import Dict, Tuple
from TSN.Constants import *


class TTFlow(Flow):
    def __init__(self, id: int, length: float, period: float, ddl: float, src: Device, dst: Device):
        super().__init__(id, length, period, ddl, src, dst)
        self.offset: Dict[Tuple['Device', 'Device'], float] = {}
        self.jitter = 0
        # self.syb: Dict[Tuple['Device', 'Device'], z3.Int] = {}

    def reset_schedule(self):
        self.status = FLOW_PENDING
        for h in self.hops:
            self.offset[h] = 0

        
    def __repr__(self):
        return f"TT{self.id}"
    
    def set_route(self, route, G):
        super().set_route(route, G)
        # 初始化offset
        for hop in self.hops:
            self.offset[hop] = 0
    
    def print_info(self):
        print(f"Flow-{self.id} from {self.src} to {self.dst}")
        print(f"Length: {self.length}, Period: {self.period}, Deadline: {self.ddl}")
        print(f"Route: {self.route}")
        print(f"Offset: {self.offset}")
        print(f"Delay: {self.delay}")
        print(f"Jitter: {self.jitter}")
        print(f"Status: {self.status}")
        print()