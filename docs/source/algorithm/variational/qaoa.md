# 量子近似优化算法（QAOA）

## 背景与理论

QAOA（Farhi 等人，2014）是一种用于求解组合优化问题的量子-经典混合算法。
它通过交替施加代价酉和混合酉来逼近最优解。

### MaxCut 问题

给定图 $G = (V, E)$，MaxCut 寻求将 $V$ 划分为两个集合，
使得跨越分割的边数最大化。

**代价哈密顿量：**

$$H_C = -\frac{1}{2} \sum_{(i,j) \in E} (1 - Z_i Z_j)$$

最大化 $-H_C$ 等价于最大化切割数。

### QAOA 拟设

QAOA 态的制备方式为：

$$|\psi(\boldsymbol{\beta}, \boldsymbol{\gamma})\rangle
= \prod_{l=1}^{p} e^{-i\beta_l H_M} e^{-i\gamma_l H_C} |+\rangle^{\otimes n}$$

其中 $H_M = \sum_i X_i$ 是混合哈密顿量，$p$ 是层数（$p$ 越大 → 近似效果越好）。

### 算法流程

```
初始化 |+⟩⊗n → 施加 e^{-iγ₁ Hc} → 施加 e^{-iβ₁ Hm} → ... → 测量 ⟨Hc⟩
                     ↑                                                    ↓
                     └──────── 经典优化器（更新 β, γ） ←────────────────┘
```

### 使用的组件

| 组件 | 模块 | 功能 |
|-----------|--------|------|
| `qaoa_ansatz` | `algorithmics.ansatz` | 参数化 QAOA 电路 |
| `OriginIR_Simulator` | `simulator` | 态矢量模拟 |

## 运行示例

```bash
# 默认：p=2 层，三角形图
python examples/algorithms/qaoa.py

# 更多层数
python examples/algorithms/qaoa.py -p 3

# 更多迭代次数
python examples/algorithms/qaoa.py -p 2 --maxiter 200
```

## 代码解析

### 1. 定义代价哈密顿量

```python
def maxcut_hamiltonian(edges, n_nodes):
    terms = []
    for i, j in edges:
        terms.append((f"Z{i}Z{j}", 0.5))
    return terms
```

### 2. 构建拟设

```python
from qpandalite.algorithmics.ansatz import qaoa_ansatz

circuit = qaoa_ansatz(
    cost_hamiltonian=[("Z0Z1", 0.5), ("Z1Z2", 0.5), ("Z0Z2", 0.5)],
    p=2,
    betas=[0.5, 0.3],
    gammas=[0.7, 0.2],
)
```

### 3. 评估与优化

能量 $\langle H_C \rangle$ 由态矢量计算得出，
并输入坐标下降优化器。

### 预期结果

对于三角形图（3 条边）：
- 最优切割：2 条边（将一个顶点与其余两个分开）
- $p=2$ 的 QAOA 应以高概率达到最优切割

## 扩展方向

- **加权 MaxCut**：在哈密顿量中添加边权重。
- **不同图结构**：尝试随机图、平面图等。
- **更高的 $p$**：更多层数可将近似比提升至接近 1.0。
- **基于采样的模拟**：使用 `QASM_Simulator` 进行真实噪声测量模拟。

## References

1. Farhi, E., Goldstone, J., & Gutmann, S. (2014). "A Quantum Approximate
   Optimization Algorithm." arXiv:1411.4028.
2. Zhou, L. et al. (2020). "Quantum Approximate Optimization Algorithm:
   Performance, Mechanism, and Implementation on Near-Term Devices."
   *Frontiers in Physics* 10, 585524.
