# 量子态层析

## 背景

量子态层析通过一组完整的测量来重建量子态的完整密度矩阵 $\rho$。对于 $n$ 个比特，需要在所有 $3^n$ 种 Pauli 基（XX, XY, XZ, YX, ..., ZZ）下进行测量。

### 协议流程

对于 $3^n$ 种单比特 Pauli 基的每种组合：

1. **旋转**：施加基变换门，将测量基映射到计算基（$Z$ 基）。
2. **测量**：收集基于采样的测量结果。
3. **重建**：通过线性反演或最大似然估计，将所有测量结果组合起来构建密度矩阵。

### 复杂度

- 测量次数：$O(3^n \cdot S)$，其中 $S$ 为每个基的采样次数
- 经典后处理：密度矩阵重建需要 $O(4^n)$
- **局限性**：指数级增长使其仅适用于小规模系统

对于更大规模的系统，可以考虑**经典阴影层析**（参见 `shadow_tomography.py`），它具有更好的扩展性。

## 运行示例

```bash
python examples/measurement/state_tomography.py --n-shots 2000
```

## 代码讲解

```python
from qpandalite.algorithmics.measurement import state_tomography, tomography_summary

# 执行层析
results = state_tomography(circuit, qubits=[0, 1], shots=2000)

# 获取重建的密度矩阵
rho = tomography_summary(results, n_qubits=2)
```

### 主要特性

- **完整重建**：恢复完整密度矩阵，包括非对角相干项。
- **基于采样**：适用于真实的（含噪声的）测量结果。
- **保真度估计**：可将重建态与目标态进行对比。

## 输出

演示程序展示：
- 重建的密度矩阵
- 与精确态的保真度
- 布居数对比（对角元素）

## References

1. James, D. F. V. et al. (2001). "Measurement of qubits." *Physical Review A*
   64, 052312.
2. Smolin, J. A. et al. (2012). "Efficient method for computing the
   maximum-likelihood quantum state from measurements with additive Gaussian
   noise." *Physical Review Letters* 108, 070502.
