
class Queue:
    def __init__(self):
        self.flows: list = []
  
    def add_flow(self, flow):
        self.flows.append(flow)
        
    def add_flows(self, flows):
        for flow in flows:
            self.add_flow(flow)