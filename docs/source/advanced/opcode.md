# Opcode 模拟器详解

OpcodeSimulator 是 QPanda-lite 的底层模拟器，直接操作 opcode 列表进行量子线路模拟。它通过 C++ 扩展（pybind11）实现高性能计算。

## 创建模拟器

```python
from qpandalite.simulator import OpcodeSimulator

# 状态向量后端（默认）
sim = OpcodeSimulator(backend_type='statevector')

# 密度矩阵后端（支持噪声模拟）
sim = OpcodeSimulator(backend_type='density_matrix')

# 基于 QuTip 的密度矩阵后端（用于交叉验证）
sim = OpcodeSimulator(backend_type='density_matrix_qutip')
```

## 支持的后端类型

| 后端 | 类型别名 | 说明 | 噪声支持 |
|------|---------|------|---------|
| `statevector` | `state_vector` | 纯态状态向量模拟 | ❌ |
| `density_matrix` | `density_operator`, `densitymatrix` | C++ 密度矩阵模拟 | ✅ |
| `density_matrix_qutip` | `density_operator_qutip` | QuTip 密度矩阵（验证用） | ✅ |

## 支持的量子门

### 单量子比特门

| 门名 | 操作 | 参数 |
|------|------|------|
| `H` | Hadamard | 无 |
| `X` | Pauli-X (NOT) | 无 |
| `Y` | Pauli-Y | 无 |
| `Z` | Pauli-Z | 无 |
| `S` | S 门 (√Z) | 无 |
| `SDG` | S† | 无 |
| `T` | T 门 (∜Z) | 无 |
| `TDG` | T† | 无 |
| `SX` | √X | 无 |
| `RX` | 绕 X 轴旋转 | `theta` |
| `RY` | 绕 Y 轴旋转 | `theta` |
| `RZ` | 绕 Z 轴旋转 | `theta` |
| `U1` | 相位门 | `lambda` |
| `U2` | U2 门 | `phi`, `lambda` |
| `U3` | 通用单比特门 | `theta`, `phi`, `lambda` |

### 双量子比特门

| 门名 | 操作 | 参数 |
|------|------|------|
| `CNOT` / `CX` | 受控 NOT | 无 |
| `CZ` | 受控 Z | 无 |
| `SWAP` | SWAP | 无 |
| `ISWAP` | iSWAP | 无 |
| `XY` | XY 交互 | `theta` |
| `XX` | XX 交互 | `theta` |
| `YY` | YY 交互 | `theta` |
| `ZZ` | ZZ 交互 | `theta` |

### 三量子比特门

| 门名 | 操作 | 参数 |
|------|------|------|
| `TOFFOLI` / `CCX` | Toffoli | 无 |
| `CSWAP` / `Fredkin` | 受控 SWAP | 无 |

### 特殊门

| 门名 | 操作 | 参数 |
|------|------|------|
| `RPhi` | 绕 Bloch 球面 φ 角旋转 | `theta`, `phi` |
| `RPhi90` | 90° RPhi | `phi` |
| `RPhi180` | 180° RPhi | `phi` |
| `UU15` | 双比特通用门（15 参数） | 15 个角度参数 |
| `PHASE2Q` | 双比特相位 | `theta` |

## 受控门支持

所有门都支持通过 `control_qubits_set` 参数添加控制量子比特：

```python
# 对 qubit 0 施加 X 门，以 qubit 1 为控制位
sim.x(qubit=0, control_qubits_set=[1], is_dagger=False)
```

## 模拟结果获取

```python
# 初始化量子比特数
sim.init_n_qubit(n_qubit)

# ... 施加门操作 ...

# 获取概率分布（指定测量比特）
prob = sim.pmeasure(measure_qubits)

# 获取状态向量（仅 statevector 后端）
sv = sim.state

# 获取密度矩阵（仅 density_matrix 后端）
dm = sim.state
```

## 直接使用 Opcode 列表

Opcode 列表是 `(operation, qubit, cbit, parameter, is_dagger, control_qubits_set)` 元组的列表：

```python
opcodes = [
    ('H', [0], None, None, False, []),
    ('CNOT', [0, 1], None, None, False, []),
    ('RX', [0], None, [1.57], False, []),
]

sim = OpcodeSimulator()
sim.init_n_qubit(2)
for opcode in opcodes:
    operation, qubit, cbit, parameter, is_dagger, control_qubits_set = opcode
    sim.simulate_gate(operation, qubit, cbit, parameter, is_dagger, control_qubits_set)
```

## 已知限制

- **密度矩阵后端**：受控门 `crx`、`crz`、`cy` 在多门线路中结果可能不正确（已知 bug，正在修复中）
- **statevector 后端**：所有门均已通过测试
