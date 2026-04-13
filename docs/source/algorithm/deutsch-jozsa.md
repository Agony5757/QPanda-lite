# Deutsch-Jozsa 算法

## 背景与理论

Deutsch-Jozsa 算法（Deutsch & Jozsa, 1992）是量子计算中最早展示相对于经典计算指数加速的算法之一。

给定一个黑盒函数 $f: \{0,1\}^n \to \{0,1\}$，已知 $f$ 要么是**恒定的**（constant，对所有输入返回相同值），要么是**均衡的**（balanced，对一半输入返回 0，另一半返回 1）。Deutsch-Jozsa 算法仅需**一次**量子查询即可确定 $f$ 的类型，而经典确定性算法在最坏情况下需要 $2^{n-1} + 1$ 次查询。

### 电路结构

算法步骤如下：

1. **初始化**：将 $n$ 个数据比特置于 $|+\rangle$ 态，辅助比特置于 $|-\rangle$ 态：

$$|\psi_0\rangle = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle \otimes |-\rangle$$

2. **Oracle 查询**：应用预言机 $U_f$：

$$U_f|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle$$

利用相位回踢（phase kickback），效果等价于：

$$|\psi_1\rangle = \frac{1}{\sqrt{2^n}} \sum_{x} (-1)^{f(x)} |x\rangle \otimes |-\rangle$$

3. **Hadamard 变换**：对数据比特施加 $H^{\otimes n}$：

$$|\psi_2\rangle = \frac{1}{2^n} \sum_{x,z} (-1)^{x \cdot z + f(x)} |z\rangle \otimes |-\rangle$$

4. **测量**：测量数据比特。若 $f$ 恒定，输出必为 $|0\rangle^{\otimes n}$；若 $f$ 均衡，输出必不为全零。

### Oracle 构造

**恒定 Oracle**：不施加任何门（输出恒为 0）。

**均衡 Oracle**：对选定的数据比特施加 CNOT 到辅助比特。当输入中有奇数个目标比特为 1 时，辅助比特翻转。这保证了一半输入映射到 0，一半映射到 1。

## 代码解析

### `deutsch_jozsa_oracle`

```python
from qpandalite.algorithmics.circuits import deutsch_jozsa_oracle

# 构建均衡 oracle（3 个数据比特）
oracle = deutsch_jozsa_oracle(n_qubits=3, balanced=True)

# 构建恒定 oracle
oracle = deutsch_jozsa_oracle(n_qubits=3, balanced=False)
```

参数说明：

- `n_qubits`: 数据比特数，oracle 总共使用 `n_qubits + 1` 个比特（含辅助比特）
- `balanced`: `True` 构建均衡 oracle，`False` 构建恒定 oracle
- `target_bits`: 控制辅助比特翻转的数据比特索引，`None` 表示全部数据比特

### `deutsch_jozsa_circuit`

```python
from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import deutsch_jozsa_circuit, deutsch_jozsa_oracle

n = 3
oracle = deutsch_jozsa_oracle(n, balanced=True)
c = Circuit(n + 1)
deutsch_jozsa_circuit(c, oracle)
```

函数自动完成：

1. 数据比特初始化为 $|+\rangle$，辅助比特初始化为 $|-\rangle$
2. 嵌入 oracle 电路
3. 数据比特施加 Hadamard 门
4. 测量数据比特

### 判定逻辑

```python
result = run_simulation(c)
if all_zero_probability > 0.9:
    print("CONSTANT")
else:
    print("BALANCED")
```

## 运行示例

```bash
# 均衡 oracle（默认）
python examples/circuits/deutsch-jozsa.py --n-qubits 3 --oracle-type balanced

# 恒定 oracle
python examples/circuits/deutsch-jozsa.py --n-qubits 3 --oracle-type constant

# 更大比特数
python examples/circuits/deutsch-jozsa.py --n-qubits 5 --oracle-type balanced --shots 8192
```

预期输出（balanced）：
```
 Deutsch-Jozsa Algorithm — 3 data qubits
 Oracle type: balanced

 Results (top outcomes):
   |101⟩  25.0%
   |011⟩  25.0%
   ...

  → BALANCED function (non-zero measurements detected)
```

预期输出（constant）：
```
 Deutsch-Jozsa Algorithm — 3 data qubits
 Oracle type: constant

 Results (top outcomes):
   |000⟩ 100.0% ← all zeros

  → CONSTANT function (all measurements = |000⟩)
```

## 设计说明

- **Oracle 构造**：均衡 oracle 通过 CNOT 门实现，结构简单且通用。用户可以通过 `target_bits` 参数自定义哪些数据比特参与控制。
- **辅助比特**：使用标准的相位回踢技术，辅助比特初始化为 $|-\rangle$。
- **原地修改**：`deutsch_jozsa_circuit` 直接修改传入的 Circuit 对象，与项目 API 风格一致。
- **确定性结果**：Deutsch-Jozsa 算法在无噪声情况下结果是确定性的——恒定函数必然测量到全零。

## References

- Deutsch, D. & Jozsa, R. (1992). "Rapid solutions of problems by quantum computation."
  Proceedings of the Royal Society of London A, 439, 553–558.
- Nielsen, M. A. & Chuang, I. L. (2010). "Quantum Computation and Quantum Information."
  Cambridge University Press, Section 1.4.
