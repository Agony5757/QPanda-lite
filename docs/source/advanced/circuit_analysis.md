# 线路分析

## 什么时候进入本页

当你需要查看线路信息（深度、门统计）、绘制线路图、分析门类型与数量，或了解量子比特重映射时，进入本页。

本页是 [构建量子线路](../guide/circuit.md) 的延伸阅读，适合已经完成线路构建、需要进一步分析或可视化线路结构的读者。

> 如果你还未完成基础线路构建，建议先阅读 [构建量子线路](../guide/circuit.md)。

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

QPanda-lite 支持 OriginIR 和 QASM 格式互转。

```python
# Circuit 同时支持两种格式输出
originir_str = circuit.originir
qasm_str = circuit.qasm
```

> 详细的门对照表见 [QASM 2.0 文档](../guide/qasm.md)。
