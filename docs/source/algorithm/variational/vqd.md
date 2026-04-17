# VQD（变分量子压缩）算法

## 背景与理论

VQD（Variational Quantum Deflation）是一种混合量子-经典算法，用于**逐个寻找哈密顿量的激发态**。由 Higgott、Wang 和 Brierley 于 2019 年提出。

在许多物理和化学问题中，不仅需要基态能量，还需要激发态信息——例如分子的吸收光谱、材料的能带结构等。VQD 正是为此而设计。

### 核心思想

VQD 的代价函数在 VQE 的基础上增加了一个**惩罚项**，用于将变分状态推离已找到的低能态：

$$C(\boldsymbol{\theta}) = \langle\psi(\boldsymbol{\theta})|H|\psi(\boldsymbol{\theta})\rangle + \sum_{i} \beta_i\,|\langle\psi(\boldsymbol{\theta})|\phi_i\rangle|^2$$

其中：

- $H$ 是目标哈密顿量
- $|\psi(\boldsymbol{\theta})\rangle$ 是参数化 ansatz 生成的量子态
- $|\phi_i\rangle$ 是已找到的第 $i$ 个低能态
- $\beta_i$ 是惩罚系数，需足够大以保证正交性

### 算法流程

1. **基态搜索**：用标准 VQE 找到基态 $|\phi_0\rangle$
2. **第 $k$ 激发态**：将前面找到的所有态 $|\phi_0\rangle, \ldots, |\phi_{k-1}\rangle$ 加入惩罚项，优化 $C(\boldsymbol{\theta})$
3. **重叠计算**：$|\langle\psi(\boldsymbol{\theta})|\phi_i\rangle|^2$ 通过 swap test 或 Hadamard test 在量子电路上估计

### 重叠测量：Swap Test

计算两个 $n$-qubit 态 $|\psi\rangle$ 和 $|\phi\rangle$ 的重叠 $|\langle\psi|\phi\rangle|^2$，可以使用 swap test：

1. 准备辅助比特于 $|+\rangle$ 态
2. 以辅助比特为控制，对两个寄存器执行受控 SWAP
3. 测量辅助比特

测量辅助比特得 $|0\rangle$ 的概率 $P(0) = \frac{1 + |\langle\psi|\phi\rangle|^2}{2}$，因此：

$$|\langle\psi|\phi\rangle|^2 = 2P(0) - 1$$

### Hardware Efficient Ansatz（HEA）

VQD 使用 HEA 作为参数化 ansatz，每层包含：

1. **单比特旋转**：每个 qubit 上施加 $R_y(\theta)$ 门
2. **纠缠层**：相邻 qubit 之间的 CNOT 链

参数数量为 $n_{\text{qubits}} \times n_{\text{layers}}$。

## 代码解析

### 构建电路

```python
from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import vqd_circuit
import numpy as np

# 2-qubit 系统
c = Circuit(2)

# 假设已通过 VQE 找到基态
ground_state = np.array([1, 0, 0, 0], dtype=complex)

# 构建 VQD 电路
params = [0.1, 0.2, 0.3, 0.4]
vqd_circuit(c, params, prev_states=[ground_state], n_layers=2)
```

### 构建重叠测量电路

```python
from qpandalite.algorithmics.circuits import vqd_overlap_circuit

# 构建 swap test 电路
overlap_circ = vqd_overlap_circuit(
    prev_state=ground_state,
    ansatz_params=[0.1, 0.2, 0.3, 0.4],
    n_layers=2,
)
```

## 运行示例

完整的 VQD 示例位于 `examples/circuits/vqd.py`，演示了 2-qubit 系统 $H = Z_0 + Z_1$ 的基态和第一激发态搜索：

```bash
# 默认参数
python examples/circuits/vqd.py

# 自定义参数
python examples/circuits/vqd.py --n-qubits 2 --n-layers 3 --penalty 15.0
```

运行输出示例：

```
=== VQD Example: H = Z₀ + ... + Z_{n-1} on 2 qubits ===
Exact eigenvalues: [-2.  0.  0.  2.]

--- Step 1: VQE (ground state) ---
VQE ground state energy: -2.000000  (exact: -2.000000)

--- Step 2: VQD (first excited state) ---
VQD first excited state energy: 0.000000  (exact: 0.000000)
Overlap with ground state: 0.000000
```

## 参考文献

- Higgott, O., Wang, D. & Brierley, S. (2019). "Variational Quantum Computation of Excited States." *Quantum* 3, 156.
- Kandala, A. et al. (2017). "Hardware-efficient variational quantum eigensolver for small molecules and quantum magnets." *Nature* 549, 242–246.
