# 构建量子线路 {#guide-circuit}

## 什么时候先看本页 {#guide-circuit-when-to-read}

当你还没把量子线路表达出来——还不确定如何用 {class}`qpandalite.circuit_builder.Circuit` 把一个量子算法或实验想法写成可执行的线路表示时，先看本页。

本页解决的核心问题是：**如何从空线路开始，构建一个可以交给模拟器或真机的量子程序**。

## 本页解决的问题 {#guide-circuit-problems}

- 如何创建空线路并添加量子门（{class}`qpandalite.circuit_builder.Circuit`）
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

{func}`qpandalite.transpiler.draw.draw` 用于绘制线路图：

```python
from qpandalite.transpiler.draw import draw

draw(circuit.originir)
```

> 可视化功能详见 [线路分析](../advanced/circuit_analysis.md)。

## 命名量子寄存器 {#guide-circuit-named-qreg}

除了使用整数索引，还可以通过命名寄存器来组织量子比特。这在构建复杂电路时尤其有用。

### 创建带命名寄存器的电路

```python
from qpandalite.circuit_builder import Circuit

# 创建带有两个命名寄存器的电路
c = Circuit(qregs={"data": 4, "ancilla": 2})
```

这会创建一个 6 量子比特的电路，其中 `data` 寄存器包含 4 个比特，`ancilla` 寄存器包含 2 个比特。

### 使用命名寄存器

```python
# 获取寄存器引用
data = c.get_qreg("data")
ancilla = c.get_qreg("ancilla")

# 使用寄存器索引
c.h(data[0])           # 对 data[0] 应用 H 门
c.cnot(data[0], data[1])  # 对 data[0], data[1] 应用 CNOT

# 支持切片
c.x(data[1:3])         # 对 data[1], data[2] 应用 X 门
```

### QReg 类型

- **QReg**：命名量子寄存器，支持索引和切片
- **Qubit**：单个量子比特的命名引用
- **QRegSlice**：寄存器切片视图，用于多量子比特操作

## 参数化电路 {#guide-circuit-parametric}

QPanda-lite 支持符号化参数，可以在运行时绑定具体值。这对于变分算法（如 VQE、QAOA）非常有用。

### 创建参数

```python
from qpandalite.circuit_builder import Parameter

# 创建命名参数
theta = Parameter("theta")
phi = Parameter("phi")
```

### 参数运算

参数支持算术运算，会自动创建符号表达式（基于 sympy）：

```python
expr = theta * 2 + phi / 3
```

### 绑定和求值

```python
# 绑定具体值
theta.bind(1.0)
phi.bind(0.5)

# 求值
value = theta.evaluate()  # 返回 1.0

# 或通过字典传入值
result = theta.evaluate({"theta": 2.0})  # 返回 2.0
```

### 在电路中使用参数

```python
c = Circuit()
c.rx(0, theta)  # 参数化 RX 门
c.ry(1, phi)
c.measure(0, 1)

# 绑定参数后执行
theta.bind(0.5)
phi.bind(0.3)
```

### 参数数组

使用 `Parameters` 创建参数数组：

```python
from qpandalite.circuit_builder import Parameters

# 创建 4 个参数：alpha_0, alpha_1, alpha_2, alpha_3
alphas = Parameters("alpha", size=4)

# 批量绑定
alphas.bind([0.1, 0.2, 0.3, 0.4])

# 索引访问
c.rx(0, alphas[0])
```

## Named Circuit（可复用子程序） {#guide-circuit-named-circuit}

`@circuit_def` 装饰器用于定义可复用的量子子程序，类似 QASM3 的 gate 定义。

### 定义子程序

```python
from qpandalite.circuit_builder import circuit_def, Circuit

@circuit_def(name="bell_pair", qregs={"q": 2})
def bell_pair(circ, q):
    circ.h(q[0])
    circ.cnot(q[0], q[1])
    return circ
```

### 应用子程序

```python
# 创建父电路
c = Circuit(qregs={"data": 4})
data = c.get_qreg("data")

# 应用子程序，映射量子比特
bell_pair(c, qreg_mapping={"q": [data[0], data[1]]})
```

### 带参数的子程序

```python
@circuit_def(name="rot_x", qregs={"q": 1}, params=["theta"])
def rot_x(circ, q, theta):
    circ.rx(q[0], theta)
    return circ

# 应用并传入参数
rot_x(c, qreg_mapping={"q": [data[2]]}, param_values={"theta": 0.5})
```

### 导出为 OriginIR DEF 块

```python
# 导出子程序定义
def_block = bell_pair.to_originir_def()
print(def_block)
# DEF bell_pair(q[0], q[1])
#   H q[0]
#   CNOT q[0] q[1]
# ENDDEF
```

### 嵌套子程序

子程序可以调用其他子程序，构建层次化的电路结构：

```python
@circuit_def(name="h_gate", qregs={"q": 1})
def h_gate(circ, q):
    circ.h(q[0])
    return circ

@circuit_def(name="h_all", qregs={"q": 4})
def h_all(circ, q):
    # 调用其他子程序
    for i in range(4):
        h_gate(circ, qreg_mapping={"q": [q[i]]})
    return circ

# 应用嵌套子程序
c = Circuit(4)
h_all(c, qreg_mapping={"q": [0, 1, 2, 3]})
```

### 独立构建电路

使用 `build_standalone()` 方法可以创建一个独立的电路实例：

```python
# 直接构建独立电路
standalone = bell_pair.build_standalone()
print(standalone.originir)
# QINIT 2
# CREG 0
# H q[0]
# CNOT q[0], q[1]

# 带参数绑定构建
circuit = rot_x.build_standalone(param_values={"theta": 0.5})
```

### 子程序属性

NamedCircuit 对象提供以下属性：

```python
print(bell_pair.name)           # "bell_pair"
print(bell_pair.qregs)          # {"q": 2}
print(bell_pair.params)         # []
print(bell_pair.num_qubits)     # 2
print(bell_pair.num_parameters) # 0
```

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
