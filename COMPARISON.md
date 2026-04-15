# 与 PR #140 的对比：我们的修复 vs Agony 的 PR #140

Agony 的开放 PR：`Agony5757/QPanda-lite#140`（`fix/issue#133#134`）  
我们的分支：`fix/ci-r1r3r10`（评估分支 `fix/ci-r1r3r10-merge-agony` 已于 2026-04-15 合并回来）

---

## 维度一 — 量子比特列表设计模式（R3 / R6）

Agony 将多个算法电路函数签名改为要求传入显式量子比特列表（`qubits: List[int]`，不再有默认值），将 `n_eval_qubits: int` 这类整数参数替换为 `eval_qubits: List[int]`。其设计哲学是：*寄存器布局由调用方负责，函数内部不读取 `circuit.qubit_num`*，从而在结构上从根本防止了 R6 的空电路 bug。

**决策：采用 Agony 的设计。** 他的"调用方持有寄存器布局"方式比我们逐个打补丁的 `qubits=None` 防御性判断在结构上更简洁——R6 通过设计本身变为不可能，而不是逐个修补。拒绝他的 API 只是为了回避 breaking change，这并不明智；项目仍处于 pre-1.0 阶段，新的接口约定在语义上更健全。

**采用他的 API 的同时，我们保留了以下内容：**

- **R3 QAE 相位公式修正**（`theta = π·m / 2^(M+1)`）。Agony 的 PR 保留了错误的公式，并修改了测试来匹配；我们保留正确的公式，并保持我们的测试断言。移植到他的签名后，测试会改写为传入显式列表，但数值断言仍然是 `sin²(π·7/16)`。
- **R9 Grover oracle 修正**（正确的 `H·MCX·H` MCZ 分解 + LSB 位序）。与量子比特列表 API 无关。
- **`w_state` None 默认值修正。** Agony 的函数体中有 `isinstance(qubits, list)` 断言，而签名仍保留 `qubits=None` 默认值——使用默认值时会直接崩溃。我们采用他的 SCUC dispatch 函数体，但要求 `qubits` 必须为显式列表（去掉默认值或在断言前处理 `None`）。

**同时 cherry-pick 了以下非破坏性改动：**

1. `qcircuit.py` 中的 `Circuit.add_circuit(other)` ——通过 `add_gate(*op)` 重放 opcodes。✅ 已完成（`b1924d6`）。
2. `dicke_state_circuit` 的 SCUC 重写——算法更简洁（仅用 CNOT + Ry，不依赖 `rotation_prepare`），公共签名不变。✅ 已完成（`b1924d6`）；在 `dc5a47d` 中进一步精化（拆分为论文对应的辅助函数 `_gate_i` / `_ccry` / `_gate_ii_l` / `_scs`，并增加了 `test_dicke_5_3_exact` / `test_dicke_6_2_exact` 回归测试，覆盖非 Hamming 权重 k 的振幅泄漏情况）。

---

## 维度二 — 经典 Shadow（R2）

**Agony 的修复（约 25 行实质改动）：** 对 `shadow_expectation` 中反演公式的精确修正：

```python
# 修改前（错误）          修改后（Agony）
s = 3.0 * ev - 1.0  →  s = 3.0 * ev   # 对齐基底
s = -1.0            →  s = 0.0        # 未对齐基底
```

同时修正了中位数-均值估计器的结构（内层统计量应为 `mean`，外层为 `median`），并将批次切分改为 `np.array_split`。

**我们的修复（约 80 行实质改动，净增 12 行）：** 对 `classical_shadow.py` 进行了算法级重构：

1. **`ShadowSnapshot.counts`** ——每个 snapshot 存储完整的 shot 直方图，而非单次采样的 bitstring。
2. **分层基底采样** ——当 `n_shadow ≥ 3^n` 时，通过 `itertools.product(range(3), repeat=n)` 均匀遍历所有 Pauli 基底组合，彻底消除基底选择方差（`3^n` 项）。
3. **LSB-first 位序** ——`(outcomes_int >> i) & 1`。Agony 未修改原有的 MSB-first 约定（对非对称 Pauli 字符串如 `IZX` 是潜在 bug）。
4. **反演公式** ——使用单一前缀因子 `3^m`（m = 非恒等 Pauli 个数）+ 对完整 counts 分布求 Born 期望，而非单次采样结果。

**为什么我们的更好：**

- 修复了**两个** bug（公式 + 位序）；Agony 只修了一个。
- 5 个失败的 shadow 测试从"靠运气通过"变为"确定性通过"——分层采样对小 `n` 完全消除了基底选择方差。
- 向后兼容：`counts` 默认为 `{}`，兜底路径处理旧格式 snapshot。
- 唯一取舍：移除了中位数-均值估计器（已在 docstring 中说明——对单个可观测量是次优选择，仅在从同一 snapshot 集估计多个 Pauli 时才有价值）。

**决策：原样保留我们的 `classical_shadow.py`。**

---

## 维度三 — R7（basis_rotation）/ R8（state_tomography）：LSB-first 修复路径不同

双方都尝试修复了测量栈中的位序问题，但落地到了**相反的约定**。

### R7 — `basis_rotation.py`

| | Agony | 我们（`599fd20`） |
|---|---|---|
| 源码改动 | 5 行索引重映射：在旋转门注入循环中引入 `i = n-1-j` | **源码不变**——保留现有 `basis[i]` ↔ qubit `i` 的映射 |
| 测试改写 | `basis=["Z","X"]` → `"00"=1.0`（MSB 新约定） | `basis=["X","Z"]` → `"00"=1.0`（LSB 约定——与 state_tomography / classical_shadow 一致），并增加了 `basis_list == basis_str` 等价性检查 |
| 最终约定 | **MSB-first**：`basis[0]` 对应 qubit `n-1` | **LSB-first**：`basis[0]` 对应 qubit `0` |

这两个修复在语义上**完全相反**。cherry-pick 他的源码会破坏我们的测试；cherry-pick 他的测试则会迫使我们回退源码。

### R8 — `state_tomography.py`

| | Agony | 我们（`599fd20`） |
|---|---|---|
| 源码改动 | **文件未动** | 三处独立的 LSB-first 位编码修正：(a) 对角 Pauli 符号提取 `(outcome >> i) & 1`，(b) Pauli tensor 操作数顺序 `reversed(p[:-1])`，(c) 密度矩阵元素重建 |
| 测试如何通过 | 推测 Agony 的随机种子未触发；或 R8 被其他改动掩盖 | 测试 `test_ghz3_purity` 实际测试了重建过程——只有三处修正全部到位才能通过 |
| 测试文件差异 | 增加了一行 `print(rho)` 调试语句（无断言变化） | 无测试变更 |

**R8 并未如 CLAUDE.md 所假设的那样从 R7 自动级联过来。** State tomography 有其自身的三处位索引 bug，需要独立修复。

### 决策

**R7 和 R8 均保留我们的版本。** LSB-first 在内部一致性上更好：我们分支上的 `state_tomography.py`、`classical_shadow.py` 和 `grover_oracle.py` 全部使用 LSB-first。采用 Agony 的 MSB-first `basis_rotation.py` 会在模块间制造约定不一致。

在上游 PR #140 评审时，应推动 Agony 调整 `basis_rotation.py` 的约定——或请求项目正式统一采用 LSB-first（这正是我们已经做到的）。

---

## 总结

| 条目 | 决策 | 状态 |
|---|---|---|
| `Circuit.add_circuit()` 辅助方法 | 从 Agony cherry-pick | ✅ 已完成（`b1924d6`） |
| `dicke_state_circuit` SCUC 重写 | 从 Agony cherry-pick | ✅ 已完成（`b1924d6`，`dc5a47d`） |
| AE / DJ / w_state 签名变更 | **采用 Agony**（+ 保留 R3 公式修正 + 修复 w_state None 默认值 bug） | ✅ 已完成（`e3f5ee7`） |
| `basis_rotation.py` R7 源码变更 | 拒绝——LSB 约定冲突（维度三） | — |
| `state_tomography.py` R8 | 保留我们的——Agony 未修改；R8 与 R7 独立（维度三） | ✅ 已在分支中 |
| `classical_shadow.py` 最小修复 | 拒绝——我们的版本严格更优 | — |
| R3（QAE 公式 `2^(M+1)`） | 保留我们的——他的测试匹配了错误公式 | ✅ 已在分支中 |
| R9（Grover MCZ + LSB） | 保留我们的——他的 PR 未涉及 grover_oracle.py | ✅ 已在分支中 |
