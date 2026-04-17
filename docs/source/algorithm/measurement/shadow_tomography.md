# 经典阴影层析

## 背景

经典阴影层析（Huang, Kueng & Preskill, 2020）是一种高效方法，可以从少量测量中预测量子系统的许多性质。

### 核心思想

不同于需要 $O(4^n)$ 次测量的完整态层析，经典阴影收集 $N$ 次随机 Pauli 测量（"快照"），利用它们预测 $M$ 个可观测量，样本复杂度为：

$$N = O\left(\log(M) \cdot \max_i \|O_i\|_{\text{shadow}}^2 / \epsilon^2\right)$$

对于预测局部可观测量而言，这比完整层析**指数级更高效**。

### 协议流程

1. **随机基测量**：对每次快照，为每个比特随机选择 $X$、$Y$ 或 $Z$ 基进行测量并记录结果。
2. **经典后处理**：重建"经典阴影"——密度矩阵的一个快照。
3. **预测**：对所有快照取平均以估计任意可观测量。

## 运行示例

```bash
python examples/measurement/shadow_tomography.py --n-shadow 100 --n-shots 1000
```

## 代码讲解

```python
from qpandalite.algorithmics.measurement import classical_shadow, shadow_expectation

# 收集阴影快照
shadows = classical_shadow(circuit, qubits=[0, 1], shots=1000, n_shadow=100)

# 估计可观测量
est = shadow_expectation(shadows, {"Z0Z1": 1.0})
```

### 主要特性

- **高效**：从少量测量中预测多个可观测量。
- **灵活**：适用于任意 Pauli 可观测量。
- **无需校准**：随机 Pauli 测量可直接在设备上执行。

## References

1. Huang, H.-Y., Kueng, R., & Preskill, J. (2020). "Predicting many properties
   of a quantum system from very few measurements." *Nature Physics* 16, 1050–1057.
2. Aaronson, S. & Rothblum, G. N. (2019). "Gentle Measurement of Quantum States
   and Differential Privacy." STOC '19.
