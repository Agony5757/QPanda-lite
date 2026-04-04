# 噪声模拟

QPanda-lite 支持在密度矩阵后端上进行带噪声的量子线路模拟。相比理想模拟器，带噪声模拟可以更真实地反映实际量子硬件的行为。

## 快速开始

```python
from qpandalite.circuit_builder import Circuit
from qpandalite.simulator import OriginIR_NoisySimulator
from qpandalite.simulator.error_model import Depolarizing

# 定义噪声模型
error_loader = ErrorLoader_GenericError([Depolarizing(0.01)])

# 创建带噪声的模拟器
sim = OriginIR_NoisySimulator(
    backend_type='density_matrix',
    error_loader=error_loader,
    readout_error={0: [0.01, 0.02], 1: [0.01, 0.02]}
)

# 构建量子线路
circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)

# 运行模拟
prob = sim.simulate_pmeasure(circuit.originir)
```

## 错误模型（Error Model）

QPanda-lite 提供了多种预设错误模型，位于 `qpandalite.simulator.error_model` 模块中。

| 错误模型 | 说明 | 参数 |
|---------|------|------|
| `BitFlip` | 位翻转错误 | `p` — 翻转概率 |
| `PhaseFlip` | 相位翻转错误 | `p` — 翻转概率 |
| `Depolarizing` | 去极化噪声 | `p` — 噪声强度 |
| `TwoQubitDepolarizing` | 双比特去极化噪声 | `p` — 噪声强度 |
| `AmplitudeDamping` | 振幅阻尼 | `gamma` — 阻尼系数 |
| `PauliError1Q` | 单比特泡利噪声 | `p_x, p_y, p_z` — 各泡利算子概率 |
| `PauliError2Q` | 双比特泡利噪声 | `ps` — 概率列表 |
| `Kraus1Q` | 通用 Kraus 算子 | `kraus_ops` — Kraus 算子列表 |

### 使用示例

```python
from qpandalite.simulator.error_model import BitFlip, Depolarizing

# 单比特位翻转噪声，概率 1%
bitflip = BitFlip(0.01)

# 双比特去极化噪声，概率 0.5%
dep = TwoQubitDepolarizing(0.005)
```

## 错误加载器（Error Loader）

错误加载器负责将噪声应用到量子线路的每一步操作上。共有三个层级：

### ErrorLoader_GenericError

对所有门应用相同的噪声模型。

```python
from qpandalite.simulator.error_model import ErrorLoader_GenericError, Depolarizing

error_loader = ErrorLoader_GenericError([Depolarizing(0.01)])
```

### ErrorLoader_GateTypeError

根据门的类型应用不同的噪声。

```python
from qpandalite.simulator.error_model import ErrorLoader_GateTypeError, Depolarizing, AmplitudeDamping

error_loader = ErrorLoader_GateTypeError(
    generic_error=[Depolarizing(0.01)],          # 所有门的基础噪声
    gatetype_error={
        'H': [AmplitudeDamping(0.02)],           # H 门额外添加幅阻尼
        'CNOT': [Depolarizing(0.03)],            # CNOT 门更高噪声
    }
)
```

### ErrorLoader_GateSpecificError

针对特定门和特定量子比特应用不同的噪声。

```python
from qpandalite.simulator.error_model import (
    ErrorLoader_GateSpecificError, Depolarizing
)

error_loader = ErrorLoader_GateSpecificError(
    generic_error=[Depolarizing(0.01)],
    gatetype_error={},
    gate_specific_error={
        ('CNOT', (0, 1)): [Depolarizing(0.05)],  # 仅针对 qubit 0-1 上的 CNOT
        ('CZ', (1, 2)): [Depolarizing(0.05)],    # 仅针对 qubit 1-2 上的 CZ
    }
)
```

## readout_error

`readout_error` 用于模拟测量时的读取误差，格式为字典：

```python
readout_error = {
    qubit: [p(0|1), p(1|0)],  # p(0|1) 为实际 1 但测到 0 的概率，p(1|0) 为实际 0 但测到 1 的概率
    ...
}
```

### 示例

```python
# qubit 0: 测量结果翻转概率为 1%（读出 0 但实际为 1）和 2%（读出 1 但实际为 0）
# qubit 1: 同样配置
readout_error = {
    0: [0.01, 0.02],
    1: [0.01, 0.02],
}

sim = OriginIR_NoisySimulator(
    backend_type='density_matrix',
    error_loader=error_loader,
    readout_error=readout_error
)
```

## 创建带噪声模拟器

```python
from qpandalite.simulator import OriginIR_NoisySimulator
from qpandalite.simulator.error_model import ErrorLoader_GenericError, Depolarizing

error_loader = ErrorLoader_GenericError([Depolarizing(0.01)])
readout_error = {0: [0.01, 0.02], 1: [0.01, 0.02]}

sim = OriginIR_NoisySimulator(
    backend_type='density_matrix',  # 必须使用 density_matrix 后端
    error_loader=error_loader,
    readout_error=readout_error
)
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `backend_type` | `str` | 必须是 `'density_matrix'`，状态向量后端不支持噪声 |
| `error_loader` | `ErrorLoader` | 错误加载器实例，如 `ErrorLoader_GenericError` |
| `readout_error` | `Dict[int, List[float]]` | 测量读取错误配置，键为量子比特编号 |

## 完整示例

```python
from qpandalite.circuit_builder import Circuit
from qpandalite.simulator import OriginIR_NoisySimulator
from qpandalite.simulator.error_model import ErrorLoader_GenericError, Depolarizing

# 1. 定义噪声模型：所有门应用 1% 去极化噪声
error_loader = ErrorLoader_GenericError([Depolarizing(0.01)])

# 2. 配置测量误差
readout_error = {
    0: [0.01, 0.02],  # qubit 0 读取误差
    1: [0.01, 0.02],  # qubit 1 读取误差
}

# 3. 创建模拟器
sim = OriginIR_NoisySimulator(
    backend_type='density_matrix',
    error_loader=error_loader,
    readout_error=readout_error
)

# 4. 构建量子线路
circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)

# 5. 运行模拟
prob = sim.simulate_pmeasure(circuit.originir)
print(prob)
```

## 已知限制

- 使用 `crx`/`crz`/`cy` 受控旋转门时存在已知 bug（density matrix 后端多门组合时出错，单门测试正常），测试线路时应注意规避。
- 噪声模拟目前仅支持单比特和双比特门。
