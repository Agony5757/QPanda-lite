# 基于旋转的任意态制备

## 背景

**Shende–Bullock–Markov (SBM)** 算法通过一系列多路旋转，从 $|0\rangle^{\otimes n}$ 制备任意 $n$ 比特量子态。其核心思想是：

1. 从目标态出发，逐一**解纠缠**各比特，最终退化为 $|00\ldots0\rangle$。
2. 收集逆操作对应的门。
3. 按**逆序**施加这些门，即可从 $|00\ldots0\rangle$ 得到目标态。

### 门复杂度

SBM 分解需要 $O(2^n)$ 个 CNOT 门和 $O(2^n)$ 个单比特旋转——这是通用态制备的最优复杂度。

## 运行示例

```bash
# Bell 态
python examples/state_preparation/rotation_prepare.py --state bell

# GHZ 态（3 比特）
python examples/state_preparation/rotation_prepare.py --state ghz

# W 态（3 比特）
python examples/state_preparation/rotation_prepare.py --state w

# 随机态
python examples/state_preparation/rotation_prepare.py --state random
```

## 代码讲解

```python
import numpy as np
from qpandalite.algorithmics.state_preparation import rotation_prepare

target = np.array([1, 0, 0, 1]) / np.sqrt(2)  # Bell 态
c = Circuit()
rotation_prepare(c, target)
```

### 主要特性

- **自动归一化**：目标向量会在需要时自动归一化。
- **任意维度**：支持 $n$ 比特态（$2^n$ 维向量）。
- **高保真度**：在模拟中可实现保真度 > $1 - 10^{-8}$。

## 演示的量子态

| 量子态 | 描述 |
|--------|------|
| Bell | $(|00\rangle + |11\rangle)/\sqrt{2}$ |
| GHZ | $(|0\rangle^{\otimes n} + |1\rangle^{\otimes n})/\sqrt{2}$ |
| W | 单激发态的等幅叠加 |
| Random | Haar 随机归一化态 |

## References

1. Shende, V. V., Bullock, S. S., & Markov, I. L. (2006). "Synthesis of
   Quantum Logic Circuits." *IEEE Transactions on CAD* 25(6).
2. Möttönen, M. et al. (2004). "Transformation of quantum states using
   uniformly controlled rotations." *Quantum Information & Computation* 5(6).
