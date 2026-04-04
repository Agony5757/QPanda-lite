# 快速上手

本指南帮助你在 5 分钟内完成：构建量子线路 → 本地模拟 → 查看结果。

## 安装

```bash
pip install qpandalite
```

详细安装方式见 [安装指南](installation.md)。

## 构建量子线路

```python
from qpandalite.circuit_builder import Circuit

# 创建线路
circuit = Circuit()

# 添加量子门
circuit.h(0)          # Hadamard 门
circuit.cnot(0, 1)    # CNOT 门
circuit.measure(0, 1) # 测量

# 查看 OriginIR 格式
print(circuit.originir)
```

## 本地模拟

```python
from qpandalite.simulator import OriginIR_Simulator

sim = OriginIR_Simulator()

# 概率测量
prob = sim.simulate_pmeasure(circuit.originir)
print("测量概率分布:", prob)
```

## 下一步

- [构建量子线路](circuit.md) — 详细的线路构建 API
- [本地模拟](simulation.md) — 模拟器功能详解
- [提交任务](submit_task.md) — 将线路提交到真机运行
