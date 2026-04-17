# Grover 搜索算法

## 背景与理论

Grover 搜索算法（Grover, 1996）为非结构化搜索提供了二次加速。
给定一个预言机 $f : \{0,1\}^n \to \{0,1\}$，满足 $f(x) = 1$ 当且仅当 $x$ 是目标态 $|w\rangle$，
Grover 算法只需 $O(\sqrt{N})$ 次预言机调用即可找到 $|w\rangle$，
而非经典算法所需的 $O(N)$ 次，其中 $N = 2^n$。

### 核心组件

**1. 预言机 $U_\omega$**
相位翻转预言机，将目标态的振幅乘以 $-1$：

$$U_\omega |x\rangle = (-1)^{f(x)} |x\rangle$$

标准构造使用一个处于魔术态 $|-\rangle = (|0\rangle - |1\rangle)/\sqrt{2}$ 的辅助比特：

$$U_\omega |x\rangle |-\rangle = |x\rangle \otimes (-1)^{f(x)} |-\rangle$$

**2. 扩散算子 $D$**
也称为*振幅放大*算子：

$$D = 2|s\rangle\langle s| - I$$

其中 $|s\rangle = H^{\otimes n}|0\rangle^{\otimes n}$ 是均匀叠加态。
$D$ 将任意向量关于 $|s\rangle$ 做反射，将非目标态的振幅转移到目标态。

**3. Grover 迭代**
组合的预言机 + 扩散步：

$$G = D \cdot U_\omega$$

对 $|s\rangle$ 施加 $R \approx \frac{\pi}{4}\sqrt{N}$ 次后，振幅将集中于目标态。

### 状态演化

从 $|s\rangle = \frac{1}{\sqrt{N}} \sum_x |x\rangle$ 出发：

经过一次 Grover 迭代后，状态处于由 $\{|w\rangle, |s'\rangle\}$ 张成的二维子空间中，
其中 $|s'\rangle$ 是所有非目标态的叠加。

$|w\rangle$ 上的振幅按 $\sin((2R+1)\theta)$ 增长，其中 $\sin\theta = 1/\sqrt{N}$。

## 代码解析

### `build_oracle`

```python
def build_oracle(n_qubits, marked_state):
```

为给定目标态构建相位翻转预言机：

1. **辅助比特准备**：将辅助比特初始化为 $|-\rangle = X \cdot H |0\rangle$
2. **目标态编码**：翻转目标态中处于 $|0\rangle$ 的数据比特
3. **相位回踢**：从数据比特到辅助比特施加多控 Z（CCZ）
4. **逆计算**：恢复之前翻转的比特

### `build_diffusion`

实现 $D = H^{\otimes n} \cdot Z^{\otimes n} \cdot H^{\otimes n}$：

1. 施加 $H^{\otimes n}$ 将 $|s\rangle \to |0\rangle^{\otimes n}$
2. 施加 $Z^{\otimes n}$ 翻转 $|0\rangle^{\otimes n}$ 的相位
3. 再次施加 $H^{\otimes n}$——净效果是关于 $|s\rangle$ 的反射

### `run_grover`

端到端的 Grover 搜索：

1. 将数据比特初始化为 $|+\rangle$（对 $|0\rangle$ 施加 Hadamard）
2. 施加最优迭代次数 $R = \lfloor \frac{\pi}{4}\sqrt{N} \rfloor$ 次 Grover 迭代
3. 测量所有数据比特

## 运行示例

```bash
# 基本运行：3 个比特，目标态 = 5
python examples/algorithms/grover.py --n-qubits 3 --marked-state 5

# 更大的搜索空间
python examples/algorithms/grover.py --n-qubits 4 --marked-state 10 --shots 8192
```

预期输出：
```
 Grover's Search — 3 data qubits
 Marked state: 5 (101)
 Search space: 8 states

 Results (top 5 most probable states):
   |101⟩  95.2% ← TARGET
   |010⟩   1.8%
   |000⟩   1.2%
   |110⟩   0.8%
   |001⟩   0.6%

 Target probability: 95.2%
 Expected (ideal): ~95.0% (after optimal iterations)
```

## 设计说明

- **辅助比特**：预言机使用一个额外的辅助比特来实现相位回踢。这是标准的"辅助比特"方法，适用于任意数量的比特。
- **多控 Z 门**：对于 2 比特情况，使用 `ccx`（Toffoli）加末尾的 Z 门实现 CCZ。对于超过 2 个比特，使用线性深度的 CNOT 级联配合目标比特上的 H 门来实现 MCZ。
- **最优迭代次数**：迭代次数 $R = \lfloor \frac{\pi}{4}\sqrt{N} \rfloor$ 可最大化成功概率。对于较小的 $N$，取整和上限可以防止过冲。
- **测量**：仅测量数据比特（辅助比特不测量）。

## 扩展方向

- **多目标 Grover**：将单个目标替换为 $M$ 个目标态；最优迭代次数变为 $\frac{\pi}{4}\sqrt{N/M}$
- **非均匀 Grover**：对每个状态使用不同的预言机强度
- **振幅估计**：使用 `state_tomography` 表征测量前的状态，并解析地估计成功概率

## References

- Grover, L. K. (1996). "A fast quantum mechanical algorithm for database search."
  STOC '96. https://arxiv.org/abs/quant-ph/9605043
- Brassard, G., Høyer, P., Mosca, M., & Tapp, A. (2002). "Quantum Amplitude Amplification
  and Estimation." AMS. https://arxiv.org/abs/quant-ph/0005055
