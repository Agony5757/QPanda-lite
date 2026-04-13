# 变分量子本征求解器（VQE）

## 背景与理论

变分量子本征求解器（Variational Quantum Eigensolver, VQE）是一种混合量子-经典算法，用于求解分子哈密顿量的基态能量。该算法由 Peruzzo 等人（2014）首次演示。

### 核心思想

VQE 利用**变分原理**：对于任意参数化试探态 $|\psi(\boldsymbol{\theta})\rangle$，

$$\langle\psi(\boldsymbol{\theta})|H|\psi(\boldsymbol{\theta})\rangle
\geq E_0$$

其中 $E_0$ 是真实的基态能量。通过在 $\boldsymbol{\theta}$ 上最小化能量期望值，我们可以逼近 $E_0$。

### 算法流程

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  制备        │───▶│  测量         │───▶│  经典         │
│  |ψ(θ)⟩      │    │  ⟨ψ|H|ψ⟩     │    │  优化器       │
│  (拟设)      │    │  (期望值)     │    │  (更新 θ)     │
└─────────────┘    └──────────────┘    └──────────────┘
       ▲                                       │
       └───────────────────────────────────────┘
                    重复直至收敛
```

1. **拟设（Ansatz）**：使用参数化线路（如 UCCSD）制备 $|\psi(\boldsymbol{\theta})\rangle$。
2. **测量**：通过测量每个 Pauli 串来估计 $\langle H \rangle = \sum_i h_i \langle P_i \rangle$。
3. **经典优化**：更新 $\boldsymbol{\theta}$ 以最小化能量。

### 使用的主要组件

| 组件 | 模块 | 功能 |
|------|------|------|
| `uccsd_ansatz` | `algorithmics.ansatz` | 参数化试探态 |
| `pauli_expectation` | `algorithmics.measurement` | 能量测量 |
| `OriginIR_Simulator` | `simulator` | 态矢量模拟 |

### H₂ 分子

本示例求解最小 STO-3G 基组下 H₂ 的基态（4 个自旋轨道，2 个电子）。哈密顿量经过 Bravyi–Kitaev 变换：

$$H = \sum_i h_i P_i + E_{\text{nuclear}}$$

**预期结果**：$E_0 \approx -1.137$ Ha（精确 FCI 值）。

## 运行示例

```bash
# 默认：H₂，100 次迭代
python examples/algorithms/vqe.py

# 自定义迭代次数
python examples/algorithms/vqe.py --maxiter 200
```

## 代码讲解

### 1. 定义哈密顿量

```python
H2_HAMILTONIAN = [
    ("I0", -0.8105),
    ("Z0", +0.1720),
    ("Z0Z1", +0.1205),
    ("X0X1Y2Y3", -0.0455),
    # ... 更多项
]
```

### 2. 构建拟设

```python
from qpandalite.algorithmics.ansatz import uccsd_ansatz

circuit = uccsd_ansatz(n_qubits=4, n_electrons=2, params=theta)
```

UCCSD 生成由 $\boldsymbol{\theta}$ 参数化的单激发和双激发门。

### 3. 计算能量

```python
energy = sum(
    coeff * expectation_value(pauli_str, circuit)
    for pauli_str, coeff in hamiltonian
)
```

### 4. 优化

使用简单的坐标下降优化器逐个更新参数以最小化能量。在实际应用中，可使用 scipy 的 `COBYLA` 或 `SLSQP`。

## 扩展方向

- **更大分子**：通过扩展哈密顿量，可以求解 LiH、BeH₂、H₂O 等分子。
- **更好的拟设**：尝试硬件高效拟设（`hea`），适用于 NISQ 设备。
- **噪声缓解**：使用 `classical_shadow` 进行高效测量。
- **基于采样的模拟**：将态矢量模拟替换为 `QASM_Simulator`，获得更真实的测量统计。

## References

1. Peruzzo, A. et al. (2014). "A variational eigenvalue solver on a photonic
   quantum processor." *Nature Communications* 5, 4213.
2. McClean, J. R. et al. (2016). "The theory of variational hybrid
   quantum-classical algorithms." *New Journal of Physics* 18, 023023.
