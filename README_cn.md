# TSN时间敏感网络的 FAST 快速调度算法

## 项目简介

本项目实现了基于时间触发机制（Time-Triggered, TT）的时间敏感网络（Time-Sensitive Networking, TSN）调度算法——FAST（Fast Scheduling Algorithm）。该算法旨在为大规模TT流提供高效、可扩展的调度能力，提升调度速度与可调度率，适用于工业互联网、车载以太网等对确定性时延有严格要求的场景。

> 相关算法参考文献：
> 
> "FastScheduler: Polynomial-Time Scheduling for Time-Triggered Flows in TSN"  
> DOI: [10.1109/TNSM.2025.3603844](https://doi.org/10.1109/TNSM.2025.3603844)

## 主要特性
- 支持TSN网络拓扑建模与仿真
- 实现TT流的快速调度算法FAST
- 支持大规模流的调度与性能评估
- 可扩展，便于集成其他调度策略

## 目录结构
```
├── tb_TT.py                # 主测试脚本，示例如何生成拓扑、流并调度
├── Schedule/               # 调度相关模块
│   ├── Compute.py          # 路由与流生成等辅助函数
│   └── TTSched/TTFast.py   # FAST调度算法核心实现
├── TSN/                    # TSN网络基础设施
│   ├── Topology.py         # 网络拓扑建模
│   └── Constants.py        # 常量定义
├── Flow/                   # 流模型定义
└── requirements.txt        # 依赖包列表
```

## 快速开始
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 运行示例：
   ```bash
   python tb_TT.py
   ```
   输出包括TT流的平均时延、可调度率和调度耗时。

## FAST算法简介
FAST算法针对TT流的调度问题，采用DAG（有向无环图）建模流间依赖关系，通过拓扑排序与紧急度优先策略，快速分配时隙，支持环检测与破环处理，显著提升调度效率。

- **调度流程**：
  1. 初始化DAG，建模流间依赖
  2. 拓扑排序确定调度顺序
  3. 计算流的紧急度，优先调度紧急流
  4. 检查并打破调度环，保证可调度性
  5. 输出调度结果与性能指标
