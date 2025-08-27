
# 默认队列, 优先级


TT = 0
AVB_A = 1
AVB_B = 2
BE = 3

# 带宽
BANDWIDTH = 1000 # 1Gbps

# 抢占 开销 24B
OH = 24 * 8 / BANDWIDTH

# 非抢占 保护带大小 1542B 最大帧
GB_size = 1542 * 8

PREEMPTION_MODE = False

SLOT_SIZE = 20
MEMBOUND = 28 * 1e3

# Flow Schedulable Status
FLOW_PENDING = 0       # 待调度
FLOW_SCHEDULABLE = 1   # 可调度
FLOW_UNSCHEDULABLE = -1  # 不可调度
FLOW_BREAKING_RING = 9  # 破环

# 破环边选择
EDGE_FIRST = 0
EDGE_LOWEST_FLOWS = 1
EDGE_LOWEST_URGENCY = 2

