import networkx as nx
# import matplotlib.pyplot as plt
from typing import List, Dict, Tuple

from TSN.Device import Device, Switch, EndSystem
from TSN.Device.Component import Port

HOP = Tuple['Device', 'Device']
PORTS_CONNECTED = Tuple['Port', 'Port']

class Topology:
    def __init__(self):
        self.G = nx.Graph()
        self.links: Dict[HOP, PORTS_CONNECTED] = {}
        self.linkDelay = 0.05
        self.devices: Dict[int, Device] = {}
        
    def clear_ports_flows(self):
        for node in self.G.nodes:
            for port in node.ports:
                port.TTflows = []
                port.AVBflows = []
                
                
    def get_SWs(self):
        return [node for node in self.G.nodes if isinstance(node, Switch)]

    def get_ESs(self):
        return [node for node in self.G.nodes if isinstance(node, EndSystem)]

    def add_node(self, node: Device):
        self.G.add_node(node)
        self.devices[node.id] = node
        
    def add_nodes(self, nodes: List[Device]):
        for node in nodes:
            self.add_node(node)

    def add_edge(self, node1: Device, node2: Device, port1 = -1, port2 = -1):
        if port1 != -1:
            port1: Port = node1.ports[port1]
        else:
            port1 = node1.ports[node1.portid]
            node1.portid += 1
            
        if port2 != -1:
            port2: Port = node2.ports[port2]
        else:
            port2 = node2.ports[node2.portid]
            node2.portid += 1
        
        
        self.G.add_edge(node1, node2)
        self.G.add_edge(node2, node1)
        
        port1.to = port2
        port2.to = port1
        
        self.links[(node1, node2)] = (port1, port2)
        self.links[(node2, node1)] = (port2, port1)
        



def example_topo(topo = 'line') -> Topology:
    num = 8
    G = Topology()
    
    if topo == 'line':
        """ line topology """
        S = [Switch(i) for i in range(num)]
        ES = [EndSystem(i) for i in range(200, 200 + num)]
        G.add_nodes(S + ES)
        for i in range(len(S)-1):
            G.add_edge(S[i], S[i+1])
        for i in range(len(ES)):
            G.add_edge(S[i], ES[i])
            
    elif topo == 'ring':
        """ ring topology """
        S = [Switch(i) for i in range(num)]
        ES = [EndSystem(i) for i in range(200, 200 + num)]
        G.add_nodes(S + ES)
        for i in range(len(S)):
            G.add_edge(S[i], S[(i+1)%len(S)])
        for i in range(len(ES)):
            G.add_edge(S[i], ES[i])
            
    elif topo == 'tree':
        """ tree topology """
        num = 17
        S = [Switch(i) for i in range(num)]  # 交换机列表
        ES = [EndSystem(i) for i in range(200, 200 + num)]  # 终端系统列表
        G.add_nodes(S + ES)

        # 构建树形拓扑，根交换机为 S[0]
        for i in range(1, len(S)):
            parent = S[(i - 1) // 2]  # 父节点索引
            G.add_edge(parent, S[i])  # 连接父节点与子节点

        # 让终端系统均匀分布到最底层的交换机上
        leaf_switches = [S[i] for i in range(len(S) // 2, len(S))]  # 叶子层交换机
        for i in range(len(ES)):
            G.add_edge(leaf_switches[i % len(leaf_switches)], ES[i])
            
    elif topo == 'CEV':
        """ CEV topology """
        S = [Switch(i) for i in range(13)]
        ES = [EndSystem(i) for i in range(200, 200 + 26)]
        G.add_nodes(S + ES)
        for i in range(13):
            G.add_edge(S[i], ES[i*2])
            G.add_edge(S[i], ES[i*2+1])
        
        G.add_edge(S[0], S[1])
        G.add_edge(S[0], S[2])
        G.add_edge(S[0], S[4])
        G.add_edge(S[0], S[5])
        G.add_edge(S[0], S[6])
        G.add_edge(S[0], S[7])
        G.add_edge(S[0], S[10])
        G.add_edge(S[3], S[1])
        G.add_edge(S[3], S[2])
        G.add_edge(S[3], S[4])
        G.add_edge(S[3], S[5])
        G.add_edge(S[3], S[10])
        G.add_edge(S[3], S[9])
        G.add_edge(S[3], S[12])
        G.add_edge(S[6], S[7])
        G.add_edge(S[6], S[8])
        G.add_edge(S[6], S[10])
        G.add_edge(S[7], S[8])
        G.add_edge(S[9], S[10])
        G.add_edge(S[9], S[11])
        G.add_edge(S[9], S[12])
        G.add_edge(S[11], S[12])

    elif topo == 'SRM':
        """ small ring mesh topology """
        S = [Switch(i) for i in range(2)]
        ES = [EndSystem(i) for i in range(200, 200 + 4)]
        G.add_nodes(S + ES)
        G.add_edge(S[0], S[1])
        G.add_edge(S[0], ES[0])
        G.add_edge(S[0], ES[1])
        G.add_edge(S[1], ES[2])
        G.add_edge(S[1], ES[3])
    elif topo == 'MR':
        """ medium ring topology """
        S = [Switch(i) for i in range(4)]
        ES = [EndSystem(i) for i in range(200, 200 + 12)]
        G.add_nodes(S + ES)
        for i in range(len(S)):
            G.add_edge(S[i], S[(i+1)%len(S)])
        for i in range(len(ES)):
            G.add_edge(S[i%len(S)], ES[i])
    elif topo == 'MM':
        """ medium mesh topology """
        S = [Switch(i) for i in range(4)]
        ES = [EndSystem(i) for i in range(200, 200 + 12)]
        G.add_nodes(S + ES)
        for i in range(len(S)):
            G.add_edge(S[i], S[(i+1)%len(S)])
        G.add_edge(S[0], S[2])
        G.add_edge(S[1], S[3])
        for i in range(len(ES)):
            G.add_edge(S[i%len(S)], ES[i])
    elif topo == 'MT':
        """ medium tree topology """
        S = [Switch(i) for i in range(7)]
        ES = [EndSystem(i) for i in range(200, 200 + 8)]
        G.add_nodes(S + ES)
        for i in range(1, len(S)):
            parent = S[(i - 1) // 2]
            G.add_edge(parent, S[i])
        for i in range(len(ES)):
            G.add_edge(S[i % 4 + 3], ES[i])

    else:
        raise Exception('topo error')
        
    return G