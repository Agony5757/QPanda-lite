# 量子相位估计（QPE）

## 背景与理论

量子相位估计（QPE）用于估计酉算子特征值的相位。
给定酉算子 $U$ 及其一个特征态 $|\psi\rangle$：

$$U|\psi\rangle = e^{2\pi i\varphi}|\psi\rangle$$

QPE 使用 $n$ 个精度比特输出 $\varphi \in [0, 1)$，精度为 $n$ 比特。

### 算法步骤

**步骤 1 — 在 $m$ 个系统比特上制备特征态**：
$$|\psi\rangle = \sum_x \alpha_x |x\rangle$$

**步骤 2 — 在 $n$ 个精度比特上创建叠加态**：
$$H^{\otimes n}|0\rangle^{\otimes n} = \frac{1}{\sqrt{2^n}}\sum_{k=0}^{2^n-1}|k\rangle$$

**步骤 3 — 受控 $U$ 的幂次**：对每个精度比特 $k$（值为 $2^{n-k-1}$）：
$$C-U^{2^{n-k-1}}: \frac{1}{\sqrt{2^n}}\sum_{k,j}|k\rangle|j\rangle \to \frac{1}{\sqrt{2^n}}\sum_{k,j}e^{2\pi i\varphi k \cdot 2^{n-k-1}}|k\rangle|j\rangle$$

**步骤 4 — 对精度寄存器施加逆 QFT**：
$$\text{QFT}^{\dagger}\left(\sum_k e^{2\pi i\varphi k}|k\rangle\right) \approx |\tilde{\varphi}\rangle$$
其中 $\tilde{\varphi}$ 是 $\varphi$ 的二进制表示。

### 逆 QFT（QFTdagger）

QFT 将 $|x\rangle \to \frac{1}{\sqrt{N}}\sum_k e^{2\pi ixk/N}|k\rangle$。
QFTdagger 是其逆变换——通过反转 QFT 电路并使用伴随旋转角度来实现。

### 精度

使用 $n$ 个精度比特时，QPE 可达到 $\pm 1/2^n$ 的精度，最高有效位接近概率为 1。
算法需要将特征态作为输入提供（它不能自行寻找特征态）。

## 代码解析

### `apply_cu1`

实现 $CU_1(\theta)$，其中 $U_1(\theta) = \text{diag}(1, e^{i\theta})$：
$$CU_1(\theta) = \begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&1&0\\0&0&0&e^{i\theta}\end{pmatrix}$$

分解方式：
$$CU_1(\theta) = u_1(\theta/2) \cdot CX \cdot u_1(-\theta/2) \cdot CX$$

### `apply_qft_dagger`

精度寄存器的逆 QFT 电路：
- 以逆序级联施加 $CU_1(-\pi/2^{j-i})$ 门
- 然后在每个比特上施加 Hadamard

### `build_qpe_circuit`

1. 在系统比特上制备特征态（默认为 $|0\rangle^{\otimes m}$）
2. 在精度比特上施加 $H^{\otimes n}$ 产生均匀叠加
3. 对每个精度比特 $k$：施加由该比特控制的 $U^{2^k}$
4. 对精度比特施加 QFTdagger
5. 测量精度寄存器

## 运行示例

```bash
# 估计 T 门的相位（相位 = π/8 ≈ 0.3927）
python examples/algorithms/qpe.py --n-precision 4 --unitary t

# 估计 Z 门的相位（特征值 = -1，即相位 = 0.5）
python examples/algorithms/qpe.py --n-precision 4 --unitary z

# 更多精度比特
python examples/algorithms/qpe.py --n-precision 6 --unitary t --shots 8192
```

预期输出：
```
 Quantum Phase Estimation
 Precision qubits: 4
 Phase precision:  1/16 = 0.0625
 Unitary: t

 Measurement results:
   |0110⟩  prob= 94.2%  phase=0.3750 ← most likely
   |0101⟩   prob=  2.1%  phase=0.3125
   |0111⟩   prob=  1.8%  phase=0.4375

 Estimated phase:  0.3750
 True phase:       0.3927
 Absolute error:   0.0177
  ✓ QPE complete.
```

## 设计说明

- **特征态输入**：QPE 需要一个*已知*的特征态。对于非对角酉算子，输出是对应特征态分解的多个相位的叠加。
- **受控酉算子**：对于对角的 $U$，受控-$U$ 通过编码相位角的 $CU_1$ 门实现。级联分解处理多比特相位编码。
- **二进制相位编码**：QPE 将精度寄存器视为二进制小数 $\varphi = \sum_k b_k / 2^k$。测量得到的整数 $m$ 给出 $\tilde{\varphi} = m / 2^n$。

## 扩展方向

- **HHL 算法**：将 QPE 作为量子线性方程组求解器的核心
- **迭代 QPE（IQPE）**：通过每次迭代测量并重用一个比特来减少比特数量
- **量子计数**：结合 Grover 搜索与 QPE 来计数目标态数量

## References

- Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information*.
  Cambridge University Press. Chapter 5.
- Cleve, R., Ekert, A., Macchiavello, C., & Mosca, M. (1998). "Quantum algorithms
  revisited." Proc. R. Soc. A. https://arxiv.org/abs/quant-ph/9708016
