# 线路分析

## 线路信息

```python
circuit.depth          # 线路深度
circuit.circuit_info   # {'qubits': int, 'gates': {...}, 'measurements': [...]}
```

## 线路分析

```python
from qpandalite.analyzer import analyze_circuit

# 分析线路中的门类型和数量
info = analyze_circuit(circuit.originir)
```

## 量子比特重映射

```python
# 将线路中的量子比特索引重新映射
remapped = circuit.remapping({0: 3, 1: 5})
```

> 注意：当前 `remapping` 不支持部分重映射。

## 可视化

```python
from qpandalite.transpiler.draw import draw_circuit

draw_circuit(circuit)
```

## 线路转译

QPanda-lite 支持在 OriginIR 和 QASM 格式之间互相转换。

```python
# Circuit 同时支持两种格式输出
originir_str = circuit.originir
qasm_str = circuit.qasm
```

> 详细的门对照表见 [QASM 2.0 文档](../guide/qasm.md)。
