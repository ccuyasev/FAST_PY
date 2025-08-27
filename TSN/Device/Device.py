from TSN.Device.Component import Port
from typing import List
from TSN.Constants import *

class Device:
    def __init__(self,id: int):
        self.ports: List['Port'] = []
        self.portid = 0
        self.membound = MEMBOUND
        self.id = id
        self.process_delay = 0
            
    def __repr__(self):
        return f"Device-{self.id}"
    
    def print_info(self):
        print(f"Device-{self.id}")
        for port in self.ports:
            port.print_info()
        print()
        

        
    