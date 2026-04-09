# OriginIR

## 什么时候进入本页

当你需要理解 `circuit.originir` 输出的文本格式，或者想知道 OriginIR 在 QPanda-lite 中扮演什么角色时，看本页。

## 本页解决的问题

- `circuit.originir` 输出的文本是什么格式、怎么读
- 想手写 OriginIR 文本再交给模拟器运行
- 需要理解向 OriginQ 平台提交任务时的线路格式
- 想查阅 OriginIR 支持的完整门列表与语法规则

> 如果你还不知道如何构建线路，请先阅读 [构建量子线路](circuit.md)。

## 什么是 OriginIR

OriginIR 是本源量子体系下的量子线路描述语言。在 QPanda-lite 中，它是线路的**首选内部表示格式**——当你调用 `circuit.originir` 时，输出的就是这种格式。OriginQ 平台的任务提交也使用该格式。

如果你需要跨平台交互（例如提交到 Quafu 或 IBM），则需要导出为 OpenQASM 2.0 格式，详见 [QASM](qasm.md)。

## 在 QPanda-lite 中使用 OriginIR

### 从 Circuit 导出

构建完线路后，直接获取 OriginIR 文本：

```python
from qpandalite.circuit_builder import Circuit

circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)

originir_str = circuit.originir
print(originir_str)
```

> 关于线路构建的完整 API，见 [构建量子线路](circuit.md)。

### 用 OriginIR 文本直接模拟

你可以将 OriginIR 文本直接传给模拟器，无需先构建 Circuit 对象：

```python
from qpandalite.simulator import OriginIR_Simulator

sim = OriginIR_Simulator()
prob = sim.simulate_pmeasure(originir_str)
```

> 关于模拟器的完整用法，见 [本地模拟](simulation.md)。

### 作为 OriginQ 平台提交格式

提交到 OriginQ 平台时，直接使用 `circuit.originir` 作为线路参数：

```python
from qpandalite.task.origin_qcloud import submit_task

task_id = submit_task(
    circuit=circuit.originir,
    shots=1000
)
```

> 关于任务提交的完整流程，见 [提交任务](submit_task.md)。

## OriginIR 语言规范

> 以下是 OriginIR 的完整语言规范。日常使用中，你通常不需要手写 OriginIR——通过 `Circuit` API 构建线路后调用 `.originir` 即可自动生成。本节供需要直接读写 OriginIR 文本或排查格式问题的用户参考。

### 量子逻辑门分类

OriginIR 支持多种量子逻辑门，根据门的操作对象（量子比特数）和参数数量，可以将量子门分为以下几类：

1. **单量子比特门（1Q Gates）**：
   - 无参数门：`H`, `X`, `Y`, `Z`, `S`, `SX`, `T`
   - 单参数门：`RX`, `RY`, `RZ`, `U1`, `RPhi90`, `RPhi180`
   - 双参数门：`RPhi`, `U2`
   - 三参数门：`U3`

2. **双量子比特门（2Q Gates）**：
   - 无参数门：`CNOT`, `CZ`, `ISWAP`
   - 单参数门：`XX`, `YY`, `ZZ`, `XY`
   - 三参数门：`PHASE2Q`
   - 十五参数门：`UU15`

3. **三量子比特门（3Q Gates）**：
   - 无参数门：`TOFFOLI`, `CSWAP`

### 量子门的参数化

每个量子门都可以通过 `qubit` 和 `param` 两个属性来描述：
- `qubit`：表示该门操作的量子比特数。
- `param`：表示该门所需的参数数量。

例如：
- `H` 门是一个单量子比特门，无参数：`{'qubit': 1, 'param': 0}`
- `RX` 门是一个单量子比特门，需要一个参数：`{'qubit': 1, 'param': 1}`
- `CNOT` 门是一个双量子比特门，无参数：`{'qubit': 2, 'param': 0}`

### 错误通道（Error Channels）

OriginIR 还支持定义量子错误通道，用于模拟量子计算中的噪声和错误。错误通道也根据操作的量子比特数和参数数量进行分类：

1. **单量子比特错误通道（1Q Error Channels）**：
   - 单参数错误通道：`Depolarizing`, `BitFlip`, `PhaseFlip`, `AmplitudeDamping`
   - 3参数错误通道：`PauliError1Q`
   - 无固定参数错误通道：`Kraus1Q`

2. **双量子比特错误通道（2Q Error Channels）**：
   - 单参数错误通道：`TwoQubitDepolarizing`
   - 15参数错误通道：`PauliError2Q`

### OriginIR 量子线路的解析

OriginIR 程序是以行为单位进行解析的，每一行描述一个量子操作或控制结构。解析器通过正则表达式匹配每一行的内容，并根据操作类型调用相应的处理函数。

#### QINIT 语句

QINIT 语句用于定义量子线路的初始状态，语法如下：

```
QINIT <qubit_count>
```

其中 `<qubit_count>` 表示量子比特的数量。

#### CREG 语句

CREG 语句用于定义测量结果的寄存器，语法如下：

```
CREG <cbit_count>
```

其中 `<cbit_count>` 表示测量结果的比特数。

#### 逻辑门

##### 无参数门

无参数门的语法如下：

```
<gate_name> <qubit_index> (, <qubit_index>)*
```

例如：

```
H q[0]
CNOT q[0], q[1]
```

##### 参数门

参数门的语法如下：

```
<gate_name> <qubit_index> (, <qubit_index>)*  LEFT_BRACKET <param_value> (, <qubit_index>)* RIGHT_BRACKET
```

例如：
```
RX q[0] 0.5
RZ q[1] 0.2
```

##### 控制结构

OriginIR 支持以下控制结构：

- CONTROL：开始一个控制块，指定控制量子比特。
- ENDCONTROL：结束一个控制块。
- DAGGER：开始一个 DAGGER 块，表示操作需要取共轭转置。
- ENDDAGGER：结束一个 DAGGER 块。
- BARRIER：插入一个屏障，用于同步量子比特的操作。

控制结构的语法如下：

- CONTROL：
  ```
  CONTROL <qubit_index> (, <qubit_index>)*
  ```
- ENDCONTROL：
  ```
  ENDCONTROL <qubit_index> (, <qubit_index>)*
  ```
- DAGGER：
  ```
  DAGGER
  ```
- ENDDAGGER：
  ```
  ENDDAGGER
  ```
- BARRIER：
  ```
  BARRIER <qubit_index> (, <qubit_index>)*
  ```

### 示例

以下是一个完整的 OriginIR 程序示例：

```
QINIT 5
CREG 2

H q[0]
RX q[1], (1.57)
CNOT q[0], q[1]
RY q[2], (0.785)
CZ q[1], q[2]
U3 q[3], (1.57, 0.785, 0.392)
TOFFOLI q[0], q[1], q[3]
BARRIER q[0], q[1], q[2], q[3]
CONTROL q[0], q[1]
    X q[2]
    Y q[3]
ENDCONTROL q[0], q[1]
DAGGER
    H q[4]
    CNOT q[4], q[0]
ENDDAGGER
MEASURE q[0], c[0]
MEASURE q[1], c[1]
```

该示例演示了完整流程：先通过 `QINIT` / `CREG` 声明比特和寄存器，然后依次添加单比特门（H、RX）、双比特门（CNOT、CZ）、三比特门（TOFFOLI）和控制结构（CONTROL / DAGGER），最后通过 `MEASURE` 测量目标比特。

## 下一步

- 如果你还不知道如何构建线路，先阅读 [构建量子线路](circuit.md)
- 如果你想用 OriginIR 文本直接模拟，见 [本地模拟](simulation.md)
- 如果你想提交到 OriginQ 平台，见 [提交任务](submit_task.md)
- 如果你需要导出为 QASM 格式或做格式互转，见 [QASM](qasm.md)

