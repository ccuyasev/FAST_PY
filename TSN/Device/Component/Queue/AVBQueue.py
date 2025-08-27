from TSN.Device.Component.Queue import Queue

class AVBQueue(Queue):
    def __init__(self, config: dict):
        super().__init__()
        self.idSL = config["idSL"]
        self.sdSL = config["sdSL"]
        self.credit_max = config["credit_max"]
        self.credit_min = config["credit_min"]
        self.bandwidth = config["bandwidth"]

        
        

