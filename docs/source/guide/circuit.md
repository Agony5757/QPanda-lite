# 构建量子线路

`Circuit` 类用于构建量子线路，支持常见量子门、控制结构、DAGGER 操作、线路分析和格式转换。

## 基本用法

```python
from qpandalite.circuit_builder import Circuit

circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)
```

## 量子门

### 单量子比特门

`h`, `x`, `y`, `z`, `sx`, `s`, `t`（无参数）

`rx`, `ry`, `rz`, `u1`（1 参数）, `u2`（2 参数）, `u3`（3 参数）, `rphi`

```python
circuit.h(0)
circuit.rx(0, 0.5)    # RX 门，参数 0.5
circuit.u3(0, 1.57, 0.785, 0.392)
```

### 双量子比特门

`cnot`, `cx`, `cz`, `iswap`, `swap`, `cswap`, `toffoli`, `xx`, `yy`, `zz`, `xy`, `phase2q`, `uu15`

```python
circuit.cnot(0, 1)
circuit.cz(1, 2)
```

### 三量子比特门

`toffoli`, `cswap`

```python
circuit.toffoli(0, 1, 2)
```

### 测量

```python
circuit.measure(0, 1, 2)  # 测量指定量子比特
```

## 控制结构

### CONTROL 块

```python
with circuit.control(0, 1):
    circuit.x(2)
```

### DAGGER 块

```python
with circuit.dagger():
    circuit.h(0)
    circuit.cnot(0, 1)
```

## 格式转换

```python
# 获取 OriginIR 格式
originir_str = circuit.originir

# 获取 OpenQASM 2.0 格式
qasm_str = circuit.qasm
```

## 线路信息

```python
circuit.depth        # 线路深度
circuit.circuit      # 完整线路字符串（含头和测量）
circuit.circuit_info # {'qubits': int, 'gates': {...}, 'measurements': [...]}
```

## 量子比特重映射

```python
# 将线路中的量子比特映射到新的索引
remapped = circuit.remapping({0: 3, 1: 5})
```

## 可视化

```python
from qpandalite.transpiler.draw import draw_circuit

draw_circuit(circuit)
```

> 可视化功能详见 [线路分析](../advanced/circuit_analysis.md)。
