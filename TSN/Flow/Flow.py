from TSN import Topology
from TSN.Constants import FLOW_PENDING
from TSN.Device.Component import Port
from TSN.Device.Device import Device
from typing import List, Tuple
from TSN.Topology import HOP
import math


class Flow:
    def __init__(self, id: int, length: float, period: float, ddl: float, src: Device, dst: Device):
        self.id = id
        self.length = length        # bit
        self.period = period        # us
        self.delay = 0              # us
        self.ddl = ddl              # us
        self.src = src
        self.dst = dst
        
        self.route: List['Device'] = []
        self.hops: List[HOP] = []
        self.ports: List['Port'] = []
        
        self.pdelay = math.ceil(length / src.ports[0].bandwidth) + 10 # 10us for processing delay
        
        self.status = FLOW_PENDING
        
        
    def set_route(self, route: List['Device'], G: Topology):
        self.route = route
        self.get_hops()
        self.get_ports(G)
    
    def get_hops(self):
        hops = []
        for i in range(len(self.route) - 1):
            hops.append((self.route[i], self.route[i+1]))
        
        self.hops = hops
        return hops
    
    def get_ports(self, G):
        ports = []
        for h in self.hops:
            port = G.links[h][0]
            ports.append(port)
        self.ports = ports
        return ports
    
    def __repr__(self):
        return f"Flow{self.id}"
        