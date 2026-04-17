# 热态制备电路组件

## 背景与理论

在统计力学中，量子系统在温度 $T$ 下处于热平衡时，其状态由 **Gibbs 态（热态）** 描述：

$$\rho_\beta = \frac{e^{-\beta H}}{Z}, \quad Z = \mathrm{Tr}(e^{-\beta H})$$

其中 $\beta = 1/(k_B T)$ 是逆温度，$H$ 是系统哈密顿量，$Z$ 是配分函数。

### 可分哈密顿量的热态

对于无横向场的 Ising 型哈密顿量 $H = \sum_{i=0}^{n-1} Z_i$，热态可以分解为各量子比特的直积态：

$$\rho_\beta = \bigotimes_{i=0}^{n-1} \begin{pmatrix} p_0 & 0 \\ 0 & p_1 \end{pmatrix}$$

其中：

$$p_0 = \frac{e^{\beta}}{e^{\beta} + e^{-\beta}}, \qquad p_1 = \frac{e^{-\beta}}{e^{\beta} + e^{-\beta}}$$

这是 **Boltzmann 分布** 在量子比特上的体现：$\beta$ 越大（温度越低），$p_0$ 越接近 1，系统更倾向于处于 $|0\rangle$ 态。

### 电路实现

由于热态是直积态，每个量子比特可以独立制备。对每个量子比特施加旋转门：

$$R_y(\theta)|0\rangle = \cos\frac{\theta}{2}|0\rangle + \sin\frac{\theta}{2}|1\rangle$$

选择 $\theta = 2\arccos(\sqrt{p_0})$，即可得到正确的概率分布：

$$|\cos\frac{\theta}{2}|^2 = p_0, \qquad |\sin\frac{\theta}{2}|^2 = p_1$$

## 代码解析

### `thermal_state_circuit`

```python
from qpandalite.algorithmics.circuits import thermal_state_circuit
```

函数签名：

```python
def thermal_state_circuit(
    circuit: Circuit,
    beta: float,
    qubits: Optional[List[int]] = None,
) -> None:
```

**参数**：
- `circuit`：量子线路对象（原地修改）
- `beta`：逆温度（$\beta \geq 0$）
- `qubits`：目标量子比特索引列表

**实现逻辑**：
1. 计算 $p_0 = e^\beta / (e^\beta + e^{-\beta})$
2. 计算旋转角 $\theta = 2\arccos(\sqrt{p_0})$
3. 对每个目标量子比特施加 $R_y(\theta)$

### 与 `state_preparation.thermal_state` 的关系

`state_preparation` 模块中的 `thermal_state` 支持任意哈密顿量，通过矩阵对角化计算热态。本电路组件是 $H = \sum Z_i$ 特例的轻量级实现，不依赖矩阵运算，仅使用单量子比特旋转门。

## 运行示例

```bash
# 默认参数：3 个比特，β = 1.0
python examples/circuits/thermal_state.py

# 自定义参数
python examples/circuits/thermal_state.py --n-qubits 4 --beta 2.0 --shots 4096
```

预期输出：
```
Thermal State Preparation — 3 qubits, β = 1.0
Single-qubit probabilities: p₀ = 0.880797, p₁ = 0.119203

Measured probability distribution (shots=8192):
  State         Measured     Theory
  ------------ ---------- ----------
  |000⟩      0.679932   0.682121
  |001⟩      0.092041   0.092378
  |010⟩      0.091187   0.092378
  |011⟩      0.012329   0.012514
  |100⟩      0.090576   0.092378
  |101⟩      0.012085   0.012514
  |110⟩      0.012085   0.012514
  |111⟩      0.001953   0.001700
```

## 扩展方向

- **含横向场的热态**：$H = \sum Z_i + h\sum X_i$ 不再可分，需要更复杂的电路
- **变分热态制备**：使用 VQE 类方法近似任意哈密顿量的热态
- **量子 Metropolis 算法**：通用热态采样方法

## References

- Preskill, J. (1998). *Lecture Notes on Quantum Computation*. Caltech.
- Wiebe, N., & Granade, C. (2016). "Can basis states be prepared
  efficiently on a quantum computer?" Phys. Rev. Lett.
