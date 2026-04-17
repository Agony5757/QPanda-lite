# Dicke 态制备电路组件

## 背景与理论

**Dicke 态** $|D(n,k)\rangle$ 是 $n$ 个量子比特上所有 Hamming 权重为 $k$ 的计算基态的等权叠加：

$$|D(n,k)\rangle = \frac{1}{\sqrt{\binom{n}{k}}} \sum_{\substack{x \in \{0,1\}^n \\ |x| = k}} |x\rangle$$

其中 $|x|$ 表示比特串 $x$ 中 1 的个数。

Dicke 态在量子信息中有广泛应用：
- **量子计量学**：作为 GHZ 态的噪声鲁棒替代，用于参数估计
- **量子纠错**：与纠错码的码字态密切相关
- **多体物理**：描述自旋系统的对称态

### SCUC 算法

本实现采用 Bärtschi & Eidenbenz (2019) 提出的 **SCUC**（Sequential Conditional Unitary Cascade）确定性算法，电路深度为 $O(nk)$，仅使用 CNOT 和单量子比特旋转门。

算法步骤：

1. **初始化**：将前 $k$ 个量子比特置为 $|1\rangle$（施加 X 门），得到 $|1\cdots10\cdots0\rangle$
2. **逐层传播**：对每一层 $j = k, k-1, \ldots, 1$，从左到右扫描：
   - 对位置 $i = j-1, j, \ldots, n-2$，施加受控旋转门
   - 该门将部分振幅从"位置 $i$ 为 1"重新分配到"位置 $i+1$ 为 1"
3. **结果**：经过全部 $k$ 层后，所有 $\binom{n}{k}$ 个基态获得等权振幅

核心子程序是受控旋转 $U(i,j)$，等价于以量子比特 $i$ 为控制、量子比特 $i+1$ 为目标的 $CR_y(2\theta)$，其中 $\theta = \arccos\sqrt{j/(i+2)}$。

## 代码解析

### `dicke_state_circuit`

```python
from qpandalite.algorithmics.circuits import dicke_state_circuit
```

函数签名：

```python
def dicke_state_circuit(
    circuit: Circuit,
    k: int,
    qubits: Optional[List[int]] = None,
) -> None:
```

**参数**：
- `circuit`：量子线路对象（原地修改）
- `k`：激发数（目标态中 $|1\rangle$ 的个数），满足 $1 \leq k \leq n$
- `qubits`：目标量子比特索引列表

**实现要点**：
1. 对前 $k$ 个量子比特施加 X 门，初始化为 $|1^k 0^{n-k}\rangle$
2. 受控旋转 $U(i,j)$ 分解为 4 个基本门：$R_y(\theta)$ → CNOT → $R_y(-\theta)$ → CNOT
3. 层循环 $j$ 从 $k$ 递减到 1，位置循环 $i$ 从 $j-1$ 递增到 $n-2$

### 门数分析

总门数为 $O(nk)$：
- X 门：$k$ 个
- 受控旋转：$\sum_{j=1}^{k}(n - j) = kn - k(k+1)/2$ 个，每个分解为 4 个基本门
- 总基本门数约 $4kn - 2k(k+1) + k$

## 运行示例

```bash
# 默认：|D(4,2)⟩，6 个基态各有 1/6 概率
python examples/circuits/dicke_state.py

# 自定义参数
python examples/circuits/dicke_state.py --n-qubits 5 --k 2 --shots 4096
```

预期输出：
```
Dicke State |D(4,2)⟩ Preparation
Expected: 6 basis states, each with probability 0.166667

Measured probability distribution (shots=8192):
  State         Measured   Weight     Theory
  ------------ ---------- -------- ----------
  |0011⟩      0.166626     2✓  0.166667
  |0101⟩      0.167358     2✓  0.166667
  |0110⟩      0.165894     2✓  0.166667
  |1001⟩      0.166382     2✓  0.166667
  |1010⟩      0.167236     2✓  0.166667
  |1100⟩      0.166504     2✓  0.166667

Total weight on Hamming-weight-2 subspace: 1.000000 (expected: 1.0)
```

## 扩展方向

- **广义 Dicke 态**：对每个基态赋予不同权重（非均匀叠加）
- **噪声鲁棒性分析**：研究 Dicke 态在退相干下的纠缠保持能力
- **对称性保持子空间**：利用 Dicke 态构造更大的对称态子空间

## References

- Bärtschi, A., & Eidenbenz, S. (2019). "Deterministic Preparation of Dicke States."
  Lecture Notes in Computer Science, vol 11644. Springer.
  https://arxiv.org/abs/1904.07358
- Dicke, R. H. (1954). "Coherence in Spontaneous Radiation Processes."
  Physical Review, 93(1), 99–110.
