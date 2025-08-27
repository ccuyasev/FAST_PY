from TSN.Device.Component import Port
from TSN.Device.Device import Device

class EndSystem(Device):
    def __init__(self,id: int):
        super().__init__(id)
        self.ports = [Port(i, self) for i in range(1)]
        self.gap_send = 0 # Gap time for sending frames, in us
            
    def __repr__(self):
        return f"ES-{self.id}"
