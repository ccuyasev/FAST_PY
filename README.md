
# FAST Scheduling Algorithm for Time-Sensitive Networking (TSN)

*For Chinese version, see [README_cn.md](./README_cn.md)*

## Project Introduction

This project implements the FAST (Fast Scheduling Algorithm) for Time-Triggered (TT) flows in Time-Sensitive Networking (TSN). The algorithm is designed to provide efficient and scalable scheduling for large-scale TT flows, improving scheduling speed and schedulability, and is suitable for scenarios such as industrial internet and automotive Ethernet where deterministic latency is required.

> Reference:
> 
> "FastScheduler: Polynomial-Time Scheduling for Time-Triggered Flows in TSN"  
> DOI: [10.1109/TNSM.2025.3603844](https://doi.org/10.1109/TNSM.2025.3603844)

## Features
- TSN network topology modeling and simulation
- Implementation of the FAST scheduling algorithm for TT flows
- Large-scale flow scheduling and performance evaluation
- Extensible and easy to integrate with other scheduling strategies

## Directory Structure
```
├── tb_TT.py                # Main test script, example for topology/flow generation and scheduling
├── Schedule/               # Scheduling modules
│   ├── Compute.py          # Routing and flow generation utilities
│   └── TTSched/TTFast.py   # Core implementation of FAST algorithm
├── TSN/                    # TSN network infrastructure
│   ├── Topology.py         # Network topology modeling
│   └── Constants.py        # Constants definition
├── Flow/                   # Flow model definitions
└── requirements.txt        # Dependency list
```

## Quick Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the example:
   ```bash
   python tb_TT.py
   ```
   The output includes average TT delay, schedulable rate, and scheduling time cost.

## FAST Algorithm Overview
The FAST algorithm addresses the scheduling problem of TT flows by modeling flow dependencies as a Directed Acyclic Graph (DAG). It uses topological sorting and urgency-based priority to quickly allocate time slots, supports cycle detection and breaking, and significantly improves scheduling efficiency.

- **Scheduling Process**:
  1. Initialize DAG to model flow dependencies
  2. Topological sort to determine scheduling order
  3. Calculate urgency and schedule urgent flows first
  4. Detect and break cycles to ensure schedulability
  5. Output scheduling results and performance metrics

