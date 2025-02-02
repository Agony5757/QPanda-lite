# 构建量子线路
`Circuit` 类用于生成 OriginIR 格式的量子线路。它通过一系列方法构建量子线路，并支持控制结构、DAGGER 操作、量子门操作以及线路分析等功能。`Circuit` 类还提供了将量子线路转换为 OpenQASM 格式的功能。

---

## 核心功能

`Circuit` 类的主要功能包括：
- **量子线路构建**：支持常见的量子门操作（如 `H`, `X`, `CNOT` 等）以及参数化门（如 `RX`, `RY`, `U3` 等）。
- **控制结构**：支持 `CONTROL` 和 `ENDCONTROL` 控制块，用于实现多量子比特控制操作。
- **DAGGER 操作**：支持 `DAGGER` 和 `ENDDAGGER` 块，用于实现量子门的共轭转置操作。
- **线路分析**：提供线路深度计算、量子比特映射、线路展开等功能。
- **格式转换**：支持将量子线路转换为 OriginIR 和 OpenQASM 格式。

---

## 类定义与初始化

### 类定义
```python
def __init__(self) -> None:
    """
    初始化 Circuit 类。

    属性：
    - used_qubit_list: 记录线路中使用的量子比特索引列表。
    - circuit_str: 量子线路的 OriginIR 格式字符串表示。
    - max_qubit: 线路中使用的最大量子比特索引。
    - measure_list: 需要测量的量子比特索引列表。
    - circuit_info: 包含线路信息的字典，如量子比特数、门类型及计数、测量设置等。
    """
    self.used_qubit_list = []
    self.circuit_str = ''
    self.max_qubit = 0
    self.measure_list = []
    self.circuit_info = {
        'qubits': 0,
        'gates': {},
        'measurements': []
    }
```

### 主要方法

#### 量子门操作

`Circuit` 类提供了以下量子门操作：

 - 单量子比特门：h, x, y, z, sx, s, t, rx, ry, rz, rphi, u1, u2, u3
 - 双量子比特门：cnot, cx, cz, iswap, swap, cswap, toffoli, xx, yy, zz, phase2q, uu15
 - 测量操作：measure

示例

```python
circuit = Circuit()
circuit.h(0)  # 在量子比特 0 上应用 Hadamard 门
circuit.cnot(0, 1)  # 在量子比特 0 和 1 上应用 CNOT 门
circuit.measure(0, 1)  # 测量量子比特 0 和 1
```

#### 控制结构
`Circuit` 类支持 `CONTROL` 和 `ENDCONTROL` 控制块，用于实现多量子比特控制操作。

示例

```python
with circuit.dagger():  # 进入 DAGGER 块
    circuit.h(0)  # 在量子比特 0 上应用 Hadamard 门的共轭转置
```



#### 格式转换

 - OriginIR 格式：`originir` 属性返回量子线路的 OriginIR 格式字符串。
 - OpenQASM 格式：`qasm` 属性返回量子线路的 OpenQASM 格式字符串。

```python
originir_str = circuit.originir  # 获取 OriginIR 格式字符串
qasm_str = circuit.qasm  # 获取 OpenQASM 格式字符串
```

### 属性

#### circuit
返回完整的量子线路字符串（包括头信息和测量操作）。
#### originir
返回量子线路的 OriginIR 格式字符串。
#### qasm
返回量子线路的 OpenQASM 格式字符串。
#### depth
返回量子线路的深度。

## 使用示例

以下是一个完整的 `Circuit` 类的使用示例。

```python
from Circuit import Circuit

# 初始化量子线路
circuit = Circuit()

# 构建量子线路
circuit.h(0)  # 在量子比特 0 上应用 Hadamard 门
circuit.cnot(0, 1)  # 在量子比特 0 和 1 上应用 CNOT 门
circuit.measure(0, 1)  # 测量量子比特 0 和 1

# 获取 OriginIR 格式字符串
originir_str = circuit.originir
print("OriginIR 格式：\n", originir_str)

# 获取 OpenQASM 格式字符串
qasm_str = circuit.qasm
print("OpenQASM 格式：\n", qasm_str)
```

## 注意事项

- 在使用 `remapping` 方法时，需要确保映射关系是唯一的且合理的。
- 在设置控制结构时，可以嵌套使用多个控制量子比特。
