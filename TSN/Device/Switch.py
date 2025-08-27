from TSN.Device.Component import Port
from TSN.Device.Device import Device

class Switch(Device):
    def __init__(self,id: int):
        super().__init__(id)
        self.ports = [Port(i, self) for i in range(16)]

            
    def __repr__(self):
        return f"SW-{self.id}"

        
    