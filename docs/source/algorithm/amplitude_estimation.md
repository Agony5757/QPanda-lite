# 量子振幅估计（Quantum Amplitude Estimation）

## 背景与理论

量子振幅估计（Quantum Amplitude Estimation, QAE）是量子振幅放大
（Brassard et al., 2002）与量子相位估计的结合，用于估计某个量子态
被测量为"好"结果的概率 $a$。

经典蒙特卡洛方法的估计误差为 $O(1/\sqrt{M})$（$M$ 为采样数），
而 QAE 可达到 $O(1/M)$ 的二次加速。

### 数学原理

设 $A|0\rangle = \sqrt{1-a}|坏\rangle + \sqrt{a}|好\rangle$，其中 $|好\rangle$
是由预言机标记的目标子空间。

定义 Grover 算子：

$$G = (2|ψ\rangle\langleψ| - I) \cdot U_f$$

其中 $U_f$ 是相位翻转预言机，$|ψ\rangle = A|0\rangle$。

$G$ 的本征值为 $e^{\pm 2i\theta}$，其中 $\sin^2(\theta) = a$。

通过量子相位估计（QPE），可以精确估计 $\theta$，从而得到 $a = \sin^2(\theta)$。

### 算法流程

1. **初始化**：评估寄存器 $m$ 个量子比特施加 $H^{\otimes m}$，
   搜索寄存器施加 $A|0\rangle$（通常 $A = H^{\otimes n}$）

2. **受控 Grover 迭代**：对第 $j$ 个评估量子比特施加 $2^j$ 次
   受控 Grover 操作

3. **逆 QFT**：对评估寄存器施加逆量子傅里叶变换

4. **测量**：测量评估寄存器，结果 $m$ 对应 $\theta = \pi m / 2^M$，
   估计值 $\hat{a} = \sin^2(\theta)$

### 精度

使用 $M$ 个评估量子比特时，相位精度为 $\pi / 2^M$，
概率估计的精度为 $O(\pi / 2^M)$。

## 代码解析

### `amplitude_estimation_circuit`

```python
def amplitude_estimation_circuit(
    circuit: Circuit,
    oracle: Circuit,
    qubits: Optional[List[int]] = None,
    n_eval_qubits: int = 3,
) -> None:
```

构建完整的 QAE 电路：

1. 评估寄存器（前 `n_eval_qubits` 个量子比特）施加 Hadamard
2. 搜索寄存器施加 Hadamard（均匀叠加）
3. 受控 Grover 迭代级联
4. 逆 QFT + 测量评估寄存器

### `grover_operator`

```python
def grover_operator(
    circuit: Circuit,
    oracle: Circuit,
    qubits: List[int],
) -> None:
```

构造单次 Grover 迭代：$G = A \cdot S_0 \cdot A^\dagger \cdot S_f$

- $S_f$：预言机相位翻转
- $A^\dagger = H^{\otimes n}$（H 自逆）
- $S_0$：关于 $|0\rangle$ 的反射
- $A = H^{\otimes n}$

### `amplitude_estimation_result`

```python
def amplitude_estimation_result(
    counts: dict,
    n_eval_qubits: int,
) -> float:
```

从测量结果中提取概率估计：取出现频率最高的测量结果 $m$，
计算 $\theta = \pi m / 2^M$，返回 $\sin^2(\theta)$。

## 使用示例

```python
from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import (
    amplitude_estimation_circuit,
    amplitude_estimation_result,
)

# 构造预言机（标记 |00⟩ 态）
oracle = Circuit(2)
oracle.h(1)
oracle.toffoli(0, 1, 1)  # 示例
oracle.h(1)

# 构建 QAE 电路
c = Circuit(5)  # 3 eval + 2 search
amplitude_estimation_circuit(c, oracle, n_eval_qubits=3)
```

## 参考文献

- Brassard, G., Høyer, P., Mosca, M. & Tapp, A. (2002).
  "Quantum Amplitude Amplification and Estimation."
  *AMS Contemporary Mathematics*, 305, 53–74.
