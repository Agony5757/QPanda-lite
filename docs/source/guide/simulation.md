# 本地模拟

QPanda-lite 提供多种本地模拟器，支持无噪声和带噪声的量子线路模拟。

## OriginIR 模拟器

最常用的模拟器，直接模拟 OriginIR 格式的线路。

```python
from qpandalite.circuit_builder import Circuit
from qpandalite.simulator import OriginIR_Simulator

circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)

sim = OriginIR_Simulator()
```

### 概率测量

```python
prob = sim.simulate_pmeasure(circuit.originir)
# 返回各测量结果的概率分布
```

### 状态向量

```python
sv = sim.simulate_statevector(circuit.originir)
# 返回状态向量
```

### 多次采样

```python
result = sim.simulate_shots(circuit.originir, shots=1000)
# 返回 1000 次采样的统计结果
```

## QASM 模拟器

模拟 OpenQASM 2.0 格式的线路。

```python
from qpandalite.simulator import QASM_Simulator

sim = QASM_Simulator()
prob = sim.simulate_pmeasure(qasm_str)
```

## Opcode 模拟器

底层模拟器，直接操作 opcode 列表。支持多后端：

- `statevector` — 状态向量（无噪声）
- `density_matrix` — 密度矩阵（支持噪声）
- `density_matrix_qutip` — 基于 Qutip 的密度矩阵

```python
from qpandalite.simulator import OpcodeSimulator

sim = OpcodeSimulator(backend_type='statevector')
```

> Opcode 的详细文档见 [Opcode](../advanced/opcode.md)。

## 带噪声模拟

```python
from qpandalite.simulator import OriginIR_NoisySimulator

sim = OriginIR_NoisySimulator(
    error_loader=my_error_loader,
    readout_error={0: [0.01, 0.02], 1: [0.01, 0.02]}
)
prob = sim.simulate_pmeasure(circuit.originir)
```

> 噪声模型的详细配置见 [噪声模拟](../advanced/noise_simulation.md)。

## 后端对比

| 后端 | 适用场景 | 噪声支持 |
|------|---------|---------|
| `statevector` | 无噪声快速模拟 | ❌ |
| `density_matrix` | 含噪声模拟 | ✅ |
| `density_matrix_qutip` | 复杂噪声模型 | ✅ |

## API 参考

完整的模拟器 API 见：

- `qpandalite.simulator` — 模拟器模块
- `qpandalite.simulator.OpcodeSimulator`
- `qpandalite.simulator.OriginIR_Simulator`
- `qpandalite.simulator.QASM_Simulator`
