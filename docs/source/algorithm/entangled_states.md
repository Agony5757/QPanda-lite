# 纠缠态制备（Entangled State Preparation）

## 背景与理论

量子纠缠是量子计算的核心资源。多体纠缠态在量子通信、量子密钥分发、
量子纠错和单向量子计算中扮演关键角色。本模块实现了三种重要的
多量子比特纠缠态：GHZ 态、W 态和 Cluster 态。

### GHZ 态

GHZ（Greenberger–Horne–Zeilinger）态是最简单的最大纠缠态之一：

$$|GHZ_n\rangle = \frac{1}{\sqrt{2}}(|00\ldots0\rangle + |11\ldots1\rangle)$$

**性质**：
- 所有量子比特完全关联：测量任一量子比特即可确定所有其他量子比特
- 对局域测量具有最大非局域相关性
- 是验证 Bell 不等式违反的理想选择

**制备**：

1. $H(q_0)$：产生 $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
2. $CNOT(q_0, q_1)$, $CNOT(q_1, q_2)$, ...：级联纠缠扩展

电路深度 $O(n)$，仅需 $n-1$ 个 CNOT 门。

### W 态

W 态是另一种本质上不同于 GHZ 态的多体纠缠态：

$$|W_n\rangle = \frac{1}{\sqrt{n}}(|10\ldots0\rangle + |01\ldots0\rangle + \ldots + |00\ldots1\rangle)$$

**性质**：
- 单激发均匀叠加：恰好有一个量子比特处于 $|1\rangle$
- 纠缠鲁棒性：丢失一个量子比特后仍保持纠缠（不同于 GHZ 态）
- 属于 W 类纠缠，不能通过局域操作和经典通信（LOCC）转化为 GHZ 态

**制备**（受控旋转级联）：

采用递归分解方法（Cruz et al., 2019）：

1. 初始化为 $|100\ldots0\rangle$
2. 对最后一个量子比特施加受控旋转：将 $|10\ldots0\rangle$ 分裂为
   $\sqrt{\frac{n-1}{n}}|10\ldots0\rangle + \frac{1}{\sqrt{n}}|00\ldots1\rangle$
3. 递归地对剩余 $n-1$ 个量子比特重复

受控旋转分解为 CNOT + Ry 门，电路深度 $O(n)$，无需辅助量子比特。

### Cluster 态

Cluster 态（图态）是单向量子计算的计算资源：

$$|C_G\rangle = \frac{1}{\sqrt{2^n}} \sum_{x \in \{0,1\}^n} (-1)^{\sum_{(i,j) \in E} x_i x_j} |x\rangle$$

其中 $G = (V, E)$ 是图，$n = |V|$。

**性质**：
- 由图结构决定纠缠模式
- 线性 Cluster 态是 1D 测量based 量子计算的基础
- 2D Cluster 态可实现通用量子计算

**制备**：

1. $H^{\otimes n}$：所有量子比特进入叠加态
2. 对图的每条边 $(i,j)$ 施加 $CZ_{i,j}$

电路深度取决于图的直径，线性链仅需 1 层 CZ 门。

## 代码解析

### `ghz_state`

```python
def ghz_state(circuit: Circuit, qubits: Optional[List[int]] = None) -> None:
```

制备 GHZ 态：Hadamard + CNOT 级联，至少需要 2 个量子比特。

### `w_state`

```python
def w_state(circuit: Circuit, qubits: Optional[List[int]] = None) -> None:
```

制备 W 态：使用递归受控旋转分解，至少需要 2 个量子比特。

### `cluster_state`

```python
def cluster_state(
    circuit: Circuit,
    qubits: Optional[List[int]] = None,
    edges: Optional[List[Tuple[int, int]]] = None,
) -> None:
```

制备 Cluster 态：`edges` 指定纠缠图，`None` 使用线性链。

## 使用示例

```python
from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import ghz_state, w_state, cluster_state

# GHZ 态
c = Circuit(4)
ghz_state(c)

# W 态
c = Circuit(4)
w_state(c)

# Cluster 态（线性链）
c = Circuit(4)
cluster_state(c)

# Cluster 态（环形）
c = Circuit(4)
cluster_state(c, edges=[(0,1), (1,2), (2,3), (3,0)])
```

## 参考文献

- Greenberger, D. M., Horne, M. A. & Zeilinger, A. (1989).
  "Going Beyond Bell's Theorem." In *Bell's Theorem, Quantum Theory
  and Conceptions of the Universe*, 69–72.
- Dür, W., Vidal, G. & Cirac, J. I. (2000).
  "Three qubits can be entangled in two inequivalent ways."
  *Physical Review A*, 62(6), 062314.
- Briegel, H. J. & Raussendorf, R. (2001).
  "Persistent Entanglement in Arrays of Interacting Particles."
  *Physical Review Letters*, 86(5), 910.
- Cruz, D., Fournier, R., Gremion, F. et al. (2019).
  "Efficient Quantum Algorithms for GHZ and W States."
  *Advanced Quantum Technologies*, 2(5-6), 1900015.
