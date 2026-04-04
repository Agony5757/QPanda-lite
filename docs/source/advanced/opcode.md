# Opcode 文档

Opcode（操作码）是量子计算中用于表示量子门操作的基本指令，是 QPanda-lite 底层模拟器的核心数据结构。

## 数据结构

每个 Opcode 是一个元组：

```python
(operation, qubit, cbit, parameter, is_dagger, control_qubits_set)
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `operation` | str | 量子门类型，如 `'H'`, `'CNOT'`, `'RX'` |
| `qubit` | int / list[int] | 作用量子比特 |
| `cbit` | int / list[int] / None | 经典比特（保留） |
| `parameter` | float / list[float] / None | 门参数 |
| `is_dagger` | bool | 是否共轭转置 |
| `control_qubits_set` | set | 控制量子比特集合 |

## 示例

```python
# H 门作用在 qubit 0
('H', 0, None, None, False, set())

# CNOT 门，控制 qubit 0，目标 qubit 1
('CNOT', [0, 1], None, None, False, set())

# RX 门，参数 0.5
('RX', 0, None, 0.5, False, set())

# 带控制位的 X 门
('X', 2, None, None, False, {0, 1})
```

## 支持的操作

### 量子门

- **单量子比特门**：`H`, `X`, `Y`, `Z`, `S`, `SX`, `T`, `RX`, `RY`, `RZ`, `U1`, `U2`, `U3`, `RPhi90`, `RPhi180`, `RPhi`
- **双量子比特门**：`CNOT`, `CZ`, `SWAP`, `ISWAP`, `TOFFOLI`, `CSWAP`, `XX`, `YY`, `ZZ`, `XY`, `PHASE2Q`, `UU15`
- **三量子比特门**：`TOFFOLI`, `CSWAP`

### 错误通道

- **单量子比特**：`PauliError1Q`, `Depolarizing`, `BitFlip`, `PhaseFlip`, `AmplitudeDamping`, `Kraus1Q`
- **双量子比特**：`PauliError2Q`, `TwoQubitDepolarizing`

## 与模拟器配合

Opcode 通常由 `Circuit` 类自动生成，或通过解析器从 OriginIR/QASM 解析得到。

```python
from qpandalite.simulator import OpcodeSimulator

sim = OpcodeSimulator(backend_type='statevector')

program_body = [
    ('H', 0, None, None, False, set()),
    ('CNOT', [0, 1], None, None, False, set()),
]

prob = sim.simulate_opcodes_pmeasure(n_qubit=2, program_body=program_body, measure_qubits=[0, 1])
```
