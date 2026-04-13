# 量子傅里叶变换（QFT）

## 背景与理论

量子傅里叶变换（Quantum Fourier Transform, QFT）是许多量子算法的核心子程序，
包括 Shor 大数分解算法和量子相位估计。QFT 将计算基态 $|j\rangle$ 映射为：

$$\text{QFT}|j\rangle = \frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i\, jk/N} |k\rangle$$

其中 $N = 2^n$，$n$ 为量子比特数。

### 电路结构

对 $n$ 个量子比特的 QFT，电路按如下方式构建：

对于第 $j$ 个量子比特（从最高位到最低位）：

1. 施加 Hadamard 门 $H$
2. 对每个后续量子比特 $k > j$，施加受控相位旋转 $R_k$，角度为 $\pi / 2^{k-j}$

最后，通过 SWAP 门层反转量子比特顺序，使输出符合标准的大端序约定。

### 受控相位门

$$R_k = \begin{pmatrix} 1 & 0 \\ 0 & e^{2\pi i / 2^k} \end{pmatrix}$$

在实现中，受控相位门通过 CNOT + Rz 分解实现：

$$CR_z(\theta) = R_z(\theta/2) \cdot \text{CNOT} \cdot R_z(-\theta/2) \cdot \text{CNOT}$$

### 逆 QFT

逆量子傅里叶变换（inverse QFT）可通过将 QFT 电路取逆（dagger）得到。
在 QPanda-lite 中，可以对 QFT 子电路调用 `dagger()` 方法。

## 代码解析

### `qft_circuit`

```python
from qpandalite.algorithmics.circuits import qft_circuit

c = Circuit(3)
qft_circuit(c, qubits=[0, 1, 2], swaps=True)
```

函数签名：

- `circuit`: 量子电路对象（原地修改）
- `qubits`: 目标量子比特索引列表，`None` 表示使用所有比特
- `swaps`: 是否添加 SWAP 门反转比特顺序（默认 `True`）

实现逻辑：

1. 对每个量子比特 $j$ 施加 Hadamard 门
2. 对每个 $k > j$ 施加受控相位旋转 $R(\pi/2^{k-j})$
3. 若 `swaps=True`，添加 SWAP 层

### 完整示例

```python
from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.state_preparation import basis_state
from qpandalite.algorithmics.circuits import qft_circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator

# 准备输入态 |5⟩ 并做 QFT
c = Circuit(3)
basis_state(c, state=5)
qft_circuit(c, swaps=True)
c.measure(0, 1, 2)

# 模拟
sim = QASM_Simulator()
result = sim.simulate_shots(c.qasm, shots=4096)
```

## 运行示例

```bash
# 基本运行：3 个比特，输入态 |5⟩
python examples/circuits/qft.py --n-qubits 3 --input-state 5

# 4 个比特，输入态 |7⟩
python examples/circuits/qft.py --n-qubits 4 --input-state 7 --shots 8192
```

预期输出：
```
 Quantum Fourier Transform — 3 qubits
 Input state: |5⟩ = |101⟩

 Results (top 8):
   |000⟩  12.5%
   |001⟩  12.5%
   |010⟩  12.5%
   ...

 Ideal: each basis state has probability 12.50%
 (QFT of |j⟩ produces equal-amplitude superposition with phase encoding)
```

## 设计说明

- **CNOT + Rz 分解**：受控相位门通过 CNOT 和单比特 Rz 门实现，避免了需要原生受控相位门的要求。
- **SWAP 层**：默认启用，确保输出遵循大端序约定。在作为子程序使用时（如 Shor 算法）可以关闭。
- **原地修改**：函数直接修改传入的 Circuit 对象，与项目中其他电路组件的 API 风格一致。

## References

- Nielsen, M. A. & Chuang, I. L. (2010). "Quantum Computation and Quantum Information."
  Cambridge University Press, Section 5.1.
- Shor, P. W. (1994). "Algorithms for quantum computation: discrete logarithms and factoring."
  FOCS '94.
