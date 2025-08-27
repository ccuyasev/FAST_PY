from TSN.Topology import example_topo
from Schedule.Compute import Compute, random_flow
from Schedule.TTSched import TTFast
from TSN.Constants import *
import time
import random

random.seed(0)
G = example_topo('CEV')
# G.draw()
ES = G.get_ESs()

flownum = 1000
flows = random_flow(flownum, TT, ES)

cpt = Compute(G)
cpt.compute_shortest_routes(flows)

solver = TTFast(G, flows)
t1 = time.time()
solver.run()
t2 = time.time()

sched_flows = [f for f in flows if f.status == FLOW_SCHEDULABLE]

TTdelays = [f.delay for f in sched_flows]
TTddls = [f.ddl for f in sched_flows]


print("TT avg delay: ", sum(TTdelays) / len(TTdelays))
print("TT Schedulable rate: ", len(sched_flows) / len(flows))
print("Time cost: ", t2 - t1)


# 打印不可调度流的信息

# invalid_flows = [f for f in flows if f.status == FLOW_UNSCHEDULABLE]
# for f in invalid_flows:
#     f.print_info()

# 验证调度结果

# from Schedule.Checker import ILPChecker
# checker = ILPChecker(G, sched_flows)
# print(checker.check())
