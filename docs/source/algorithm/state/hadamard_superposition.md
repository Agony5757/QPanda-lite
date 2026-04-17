# Hadamard 叠加态制备

## 背景

Hadamard 门 $H$ 从计算基态创建等概率叠加态：

$$H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} = |+\rangle$$

对所有 $n$ 个比特施加 Hadamard 门可产生均匀叠加态：

$$H^{\otimes n}|0\rangle^{\otimes n} = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle$$

这是最基本的量子态之一，被用作 Grover 搜索、QAOA、Deutsch-Jozsa 等众多算法的起始态。

## 运行示例

```bash
python examples/state_preparation/hadamard_superposition.py --n-qubits 3
```

## 代码解析

```python
from qpandalite.algorithmics.state_preparation import hadamard_superposition

c = Circuit()
hadamard_superposition(c, qubits=[0, 1, 2])
# 电路现在在所有指定比特上都有 H 门
```

### 主要特性

- **子集选择**：仅对特定比特施加 Hadamard 门，其余比特保持在 $|0\rangle$。
- **自动分配**：根据指定的索引自动分配比特。

## 输出

示例程序打印态矢量振幅和概率分布，
验证所有振幅具有相等的幅值 $1/\sqrt{2^n}$。
