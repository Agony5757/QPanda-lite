# Grover Oracle 构造

## 概述

Grover 搜索算法是量子计算中最重要的算法之一，可以在无序数据库中以 $O(\sqrt{N})$ 的复杂度搜索目标元素，相比经典算法的 $O(N)$ 提供了二次加速。

Grover 算法的核心由两个组件构成：

1. **Oracle（预言机）**：识别目标态并翻转其相位
2. **Diffusion（扩散算子）**：放大目标态的概率振幅

## Oracle 构造原理

### 相位翻转 Oracle

Oracle 的作用是将标记态 $|w\rangle$ 的相位翻转：

$$U_f |x\rangle = (-1)^{[x = w]} |x\rangle$$

### 实现方法

我们使用辅助比特（ancilla）和相位回踢（phase kickback）技术：

1. 将辅助比特初始化为 $|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$
2. 对数据比特施加 X 门，将标记态的位模式取反（使 0 位变为 1）
3. 施加多控 Z 门（MCZ），当所有控制比特为 $|1\rangle$ 时翻转辅助比特相位
4. 撤销 X 门

### MCZ 分解

多控 Z 门通过线性深度的 CNOT 级联实现：

```
H(target)
CNOT: ctrl[0] → ctrl[1]
CNOT: ctrl[1] → ctrl[2]
...
CNOT: ctrl[-1] → target
CNOT: ctrl[1] → ctrl[2]  (反向)
CNOT: ctrl[0] → ctrl[1]
H(target)
```

这种分解使用 $O(n)$ 个 CNOT 门，不需要额外的辅助比特。

## 扩散算子

扩散算子（又称振幅放大算子）的定义为：

$$D = 2|s\rangle\langle s| - I$$

其中 $|s\rangle = H^{\otimes n}|0\rangle^{\otimes n}$ 是均匀叠加态。

等价实现：

$$D = H^{\otimes n} \cdot (2|0\rangle\langle 0| - I) \cdot H^{\otimes n}$$

其中 $2|0\rangle\langle 0| - I$ 通过 X 门 + MCZ + X 门实现。

## API 使用

### grover_oracle

```python
from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import grover_oracle, grover_diffusion

c = Circuit()
n_qubits = 3

# 均匀叠加
for i in range(n_qubits):
    c.h(i)

# 构造 oracle
ancilla = grover_oracle(c, marked_state=5, qubits=[0, 1, 2])

# 构造扩散算子
grover_diffusion(c, qubits=[0, 1, 2], ancilla=ancilla)
```

### grover_diffusion

```python
grover_diffusion(c, qubits=[0, 1, 2], ancilla=3)
```

- `qubits`：数据比特索引列表，默认 `[0, 1]`
- `ancilla`：辅助比特索引，默认自动分配为 `max(qubits) + 1`

## 完整示例

参见 `examples/circuits/grover_oracle.py`，演示了完整的 Grover 搜索流程：

```bash
python examples/circuits/grover_oracle.py --n-qubits 3 --marked-state 5 --shots 4096
```

## 参考文献

- Grover, L. K. (1996). "A fast quantum mechanical algorithm for database search." STOC '96.
- Nielsen, M. A., & Chuang, I. L. (2010). Quantum Computation and Quantum Information.
