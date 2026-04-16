# 本地模拟 {#guide-simulation}

## 什么时候进入本页 {#guide-simulation-when-to-read}

当你已经有一条线路，想在本地验证结果、查看概率分布、做多次采样，或比较不同模拟后端时，进入本页。

本页解决的核心问题是：**如何把已经写好的线路跑起来，并根据目标选择合适的模拟方式与后端**。

## 本页解决的问题 {#guide-simulation-problems}

- 如何把已有线路送入模拟器
- 如何查看概率测量、状态向量、多次采样等不同输出
- 如何区分 OriginIR、QASM、Opcode 等不同模拟入口
- 如何根据目标选择 statevector、density matrix、density matrix_qutip 等后端
- 如何在本地验证时识别已知限制与风险

## 前置条件

阅读本页前，默认你已经完成以下至少一项：

- 已经会使用 `Circuit` 构建基础线路
- 已经拿到了 `originir` 或 `qasm` 字符串
- 已经完成 [快速上手](quickstart.md) 中的最小示例

如果你还不清楚如何创建线路、添加量子门或导出线路格式，建议先阅读 [构建量子线路](circuit.md)。

## 推荐阅读顺序 {#guide-simulation-reading-order}

建议按以下顺序阅读本页内容：

1. **OriginIR 模拟器** — 先跑通最常见的本地模拟路径
2. **概率测量 / 状态向量 / 多次采样** — 理解不同输出类型分别回答什么问题
3. **QASM 模拟器** — 当你的输入是 OpenQASM 2.0 时使用
4. **Opcode 模拟器** — 需要底层控制或特定后端时再进入
5. **带噪声模拟** — 当你需要加入噪声模型时阅读
6. **后端对比** — 根据验证目标选择不同后端
7. **已知限制** — 在使用 density matrix 或复杂噪声路径前优先确认

## 本地模拟入口总览 {#guide-simulation-entry-overview}

在 QPanda-lite 中，“本地模拟”指的是**不提交远端任务、直接在当前环境运行线路并查看结果**。常见入口可以先按输入格式与验证目标来分：

| 本地模拟入口 | 输入形式 | 适合先看什么问题 |
| --- | --- | --- |
| {class}`qpandalite.simulator.OriginIR_Simulator` | `originir` 字符串 | 已经用 {class}`qpandalite.circuit_builder.Circuit` 构好线路，想先快速验证概率分布、状态向量或采样结果 |
| {class}`qpandalite.simulator.QASM_Simulator` | `qasm` 字符串 | 你的线路来自 OpenQASM 2.0，或准备沿着 QASM 路径与外部工具互操作 |
| {class}`qpandalite.simulator.OpcodeSimulator` | opcode 列表 | 需要更底层控制、特定后端或排查后端差异 |
| {class}`qpandalite.simulator.OriginIR_NoisySimulator` | `originir` 字符串 + 噪声配置 | 想在本地模拟阶段加入噪声模型并观察结果变化 |

如果你还在决定线路该如何表达，先回到 [构建量子线路](circuit.md#guide-circuit-when-to-read)；如果你已经完成本地验证，准备提交到云平台或真机执行，转到 [提交任务](submit_task.md#guide-submit-task-entry-overview)。

## OriginIR 模拟器 {#guide-simulation-originir}

最常用的模拟器，直接模拟 OriginIR 格式的线路。

```python
from qpandalite.circuit_builder import Circuit
from qpandalite.simulator import OriginIR_Simulator

circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)

sim = OriginIR_Simulator()
```

### 概率测量

```python
prob = sim.simulate_pmeasure(circuit.originir)
# 返回各测量结果的概率分布
```

### 状态向量

```python
sv = sim.simulate_statevector(circuit.originir)
# 返回状态向量
```

### 多次采样

```python
result = sim.simulate_shots(circuit.originir, shots=1000)
# 返回 1000 次采样的统计结果
```

## QASM 模拟器 {#guide-simulation-qasm}

模拟 OpenQASM 2.0 格式的线路。

```python
from qpandalite.simulator import QASM_Simulator

sim = QASM_Simulator()
prob = sim.simulate_pmeasure(qasm_str)
```

## Opcode 模拟器与本地模拟后端 {#guide-simulation-opcode}

底层模拟器，直接操作 opcode 列表。支持多后端：

- `statevector` — 状态向量（无噪声）
- `density_matrix` — 密度矩阵（支持噪声）
- `density_matrix_qutip` — 基于 Qutip 的密度矩阵

```python
from qpandalite.simulator import OpcodeSimulator

sim = OpcodeSimulator(backend_type='statevector')
```

> Opcode 的详细文档见 [Opcode](../advanced/opcode.md)。

## 带噪声的本地模拟 {#guide-simulation-noisy}

```python
from qpandalite.simulator import OriginIR_NoisySimulator

sim = OriginIR_NoisySimulator(
    error_loader=my_error_loader,
    readout_error={0: [0.01, 0.02], 1: [0.01, 0.02]}
)
prob = sim.simulate_pmeasure(circuit.originir)
```

> 噪声模型的详细配置见 [噪声模拟](../advanced/noise_simulation.md)。

## 后端对比

| 后端 | 适用场景 | 噪声支持 | 性能 |
|------|---------|---------|------|
| `statevector` | 无噪声快速模拟，小规模线路（< 30 量子比特） | ❌ | 最快 |
| `density_matrix` | 含噪声模拟，双比特门为主 | ✅ | 较慢（内存 O(4^n)） |
| `density_matrix_qutip` | 复杂噪声模型，高精度需求 | ✅ | 较慢，依赖 Qutip |

**选择建议**：
- 一般无噪声模拟 → {class}`qpandalite.simulator.OriginIR_Simulator`（基于 statevector）
- 需要噪声模拟 → {class}`qpandalite.simulator.OriginIR_NoisySimulator`（基于 density_matrix）
- 复杂多比特噪声模型 → `density_matrix_qutip`

## 已知限制 {#guide-simulation-known-limitations}

- `statevector` 后端无法模拟噪声。
- 多比特门（> 2）在 density matrix 后端支持有限。

## API 参考

完整的模拟器 API 见：

- {mod}`qpandalite.simulator` — 模拟器模块
- {class}`qpandalite.simulator.OpcodeSimulator`
- {class}`qpandalite.simulator.OriginIR_Simulator`
- {class}`qpandalite.simulator.QASM_Simulator`

## 下一步

- 如果你发现自己仍不清楚线路该如何表达、量子门如何组织，回看 [构建量子线路](circuit.md)。
- 如果你已经完成本地验证，并准备把线路提交到云平台或真机执行，进入 [提交任务](submit_task.md)。这一步开始关注的将不再是本地后端选择，而是平台配置、任务提交、状态查询与远端结果获取。

## 相关测试

- `test_simulator.py`：噪声模拟器单元测试
- `test_random_OriginIR.py`：随机回归测试（密度矩阵对比）
- `test_random_QASM.py`：随机回归测试（statevector/density matrix 对比）
- `test_demos.py`：示例端到端测试

详见 [测试覆盖说明](testing.md)。
