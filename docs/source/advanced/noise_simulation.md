# 噪声模拟

QPanda-lite 支持在本地模拟中加入噪声模型，模拟真实量子硬件上的错误。

## 概述

噪声模拟通过密度矩阵后端实现，支持：

- **量子门错误**：模拟量子门操作中的噪声
- **读出错误**：模拟测量时的读出偏差

## 使用 Noisy 模拟器

### OriginIR 噪声模拟器

```python
from qpandalite.simulator import OriginIR_NoisySimulator
from qpandalite.simulator.error_model import ErrorLoader

# 定义错误模型
error_loader = ErrorLoader(...)
readout_error = {0: [0.01, 0.02], 1: [0.01, 0.02]}

sim = OriginIR_NoisySimulator(
    backend_type='density_matrix',
    error_loader=error_loader,
    readout_error=readout_error
)

prob = sim.simulate_pmeasure(circuit.originir)
```

### QASM 噪声模拟器

```python
from qpandalite.simulator import QASM_Noisy_Simulator

sim = QASM_Noisy_Simulator(
    backend_type='density_matrix',
    error_loader=error_loader,
    readout_error=readout_error
)

prob = sim.simulate_pmeasure(qasm_str)
```

## 错误通道类型

详见 [Opcode 文档](opcode.md) 中的错误通道部分。

## 注意事项

- 噪声模拟需要使用 `density_matrix` 或 `density_matrix_qutip` 后端
- `statevector` 后端不支持噪声模拟
- 密度矩阵模拟的计算开销大于状态向量模拟
