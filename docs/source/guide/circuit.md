# 构建量子线路 {#guide-circuit}

## 什么时候先看本页 {#guide-circuit-when-to-read}

当你还没把量子线路表达出来——还不确定如何用 QPanda-lite 把一个量子算法或实验想法写成可执行的线路表示时，先看本页。

本页解决的核心问题是：**如何从空线路开始，构建一个可以交给模拟器或真机的量子程序**。

## 本页解决的问题 {#guide-circuit-problems}

- 如何创建空线路并添加量子门
- 如何添加测量指令
- 如何使用 CONTROL / DAGGER 控制结构
- 如何将线路导出为 OriginIR 或 OpenQASM 2.0 字符串
- 如何查看线路结构信息和做基础变换（重映射等）

## 推荐阅读顺序 {#guide-circuit-reading-order}

建议按以下顺序阅读本页内容：

1. **基本用法** — 从空线路到第一个可执行线路
2. **量子门** — 单比特门、双比特门、三比特门
3. **测量** — 如何指定测量比特
4. **控制结构** — CONTROL 块与 DAGGER 块
5. **格式互转** — 导出 OriginIR / QASM 字符串
6. **线路信息** — 查看深度、门统计等
7. **量子比特重映射** — 重新映射比特索引
8. **可视化** — 绘制线路图

## 基本用法

```python
from qpandalite.circuit_builder import Circuit

circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)
```

## 量子门

### 单量子比特门

`h`, `x`, `y`, `z`, `sx`, `s`, `t`（无参数）

`rx`, `ry`, `rz`, `u1`（1 参数）, `u2`（2 参数）, `u3`（3 参数）, `rphi`

```python
circuit.h(0)
circuit.rx(0, 0.5)    # RX 门，参数 0.5
circuit.u3(0, 1.57, 0.785, 0.392)
```

### 双量子比特门

`cnot`, `cx`, `cz`, `iswap`, `swap`, `cswap`, `toffoli`, `xx`, `yy`, `zz`, `xy`, `phase2q`, `uu15`

```python
circuit.cnot(0, 1)
circuit.cz(1, 2)
```

### 三量子比特门

`toffoli`, `cswap`

```python
circuit.toffoli(0, 1, 2)
```

### 测量

```python
circuit.measure(0, 1, 2)  # 测量指定量子比特
```

## 控制结构

### CONTROL 块

```python
with circuit.control(0, 1):
    circuit.x(2)
```

### DAGGER 块

```python
with circuit.dagger():
    circuit.h(0)
    circuit.cnot(0, 1)
```

## 格式互转 {#guide-circuit-format-conversion}

当你需要将线路提交到不同平台、交给不同后端执行，或与外部工具交换数据时，可以使用以下属性导出线路文本：

```python
# 获取 OriginIR 格式（用于 OriginQ 平台提交、本地模拟）
originir_str = circuit.originir

# 获取 OpenQASM 2.0 格式（用于 Quafu、IBM 平台提交、跨工具交互）
qasm_str = circuit.qasm
```

> 关于 OriginIR 格式的详细说明，见 [OriginIR](originir.md)。关于 QASM 格式与格式互转，见 [QASM](qasm.md)。

## 线路信息

```python
circuit.depth        # 线路深度
circuit.circuit      # 完整线路字符串（含头和测量）
circuit.circuit_info # {'qubits': int, 'gates': {...}, 'measurements': [...]}
```

## 量子比特重映射

```python
# 将线路中的量子比特映射到新的索引
remapped = circuit.remapping({0: 3, 1: 5})
```

## 可视化

```python
from qpandalite.transpiler.draw import draw_circuit

draw_circuit(circuit)
```

> 可视化功能详见 [线路分析](../advanced/circuit_analysis.md)。

## 本页不重点解决的问题

本页聚焦于“如何把线路写出来”，以下问题不在本页展开：

- 模拟结果怎么看、如何选择本地模拟后端 → 见 [本地模拟](simulation.md#guide-simulation-entry-overview)
- 噪声模型与性能权衡 → 见 [噪声模拟](../advanced/noise_simulation.md)
- 如何提交到真机或云平台 → 见 [提交任务](submit_task.md#guide-submit-task-entry-overview)

## 下一步

当你已经能生成 `circuit.originir` 或 `circuit.qasm`，且想在本地验证线路结果、比较不同模拟方式或做带噪声测试时，进入 [本地模拟](simulation.md#guide-simulation-entry-overview)。如果你已经完成本地验证，准备把线路提交到云平台或真机执行，则进入 [提交任务](submit_task.md#guide-submit-task-entry-overview)。

## 相关测试

- `test_general.py`：电路构建集成测试

详见 [测试覆盖说明](testing.md)。
