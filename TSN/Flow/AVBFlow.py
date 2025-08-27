from TSN.Flow.Flow import Flow
from TSN.Device.Switch import Switch
from TSN.Constants import *

class AVBFlow(Flow):
    def __init__(self, id: int, length: float, period: float, ddl: float, src: Switch, dst: Switch, priority: int):
        super().__init__(id, length, period, ddl, src, dst)
        self.priority = priority
        
    def __repr__(self):
        return f"AVB-{self.priority}-{self.id}"
