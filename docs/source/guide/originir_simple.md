# OriginIR 语言规范

OriginIR 是一种用于描述量子线路的语言，它通过一系列量子逻辑门的操作来构建量子线路。OriginIR 的语法规则和量子门的定义如下：

## 量子逻辑门分类

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

## 量子门的参数化

每个量子门都可以通过 `qubit` 和 `param` 两个属性来描述：
- `qubit`：表示该门操作的量子比特数。
- `param`：表示该门所需的参数数量。

例如：
- `H` 门是一个单量子比特门，无参数：`{'qubit': 1, 'param': 0}`
- `RX` 门是一个单量子比特门，需要一个参数：`{'qubit': 1, 'param': 1}`
- `CNOT` 门是一个双量子比特门，无参数：`{'qubit': 2, 'param': 0}`

## 错误通道（Error Channels）

OriginIR 还支持定义量子错误通道，用于模拟量子计算中的噪声和错误。错误通道也根据操作的量子比特数和参数数量进行分类：

1. **单量子比特错误通道（1Q Error Channels）**：
   - 单参数错误通道：`Depolarizing`, `BitFlip`, `PhaseFlip`, `AmplitudeDamping`
   - 3参数错误通道：`PauliError1Q`
   - 无固定参数错误通道：`Kraus1Q`

2. **双量子比特错误通道（2Q Error Channels）**：
   - 单参数错误通道：`TwoQubitDepolarizing`
   - 15参数错误通道：`PauliError2Q`

## OriginIR量子线路的解析

OriginIR 程序是以行为单位进行解析的，每一行描述一个量子操作或控制结构。解析器通过正则表达式匹配每一行的内容，并根据操作类型调用相应的处理函数。

### QINIT 语句

QINIT 语句用于定义量子线路的初始状态，语法如下：

```
QINIT <qubit_count>
```

其中 `<qubit_count>` 表示量子比特的数量。

### CREG 语句

CREG 语句用于定义测量结果的寄存器，语法如下：

```
CREG <cbit_count>
```

其中 `<cbit_count>` 表示测量结果的比特数。

### 逻辑门

#### 无参数门

无参数门的语法如下：

```
<gate_name> <qubit_index> (, <qubit_index>)*
```

例如：

```
H q[0]
CNOT q[0], q[1]
```

#### 参数门

参数门的语法如下：

```
<gate_name> <qubit_index> (, <qubit_index>)*  LEFT_BRACKET <param_value> (, <qubit_index>)* RIGHT_BRACKET
```

例如：
```
RX q[0] 0.5
RZ q[1] 0.2
```

#### 控制结构
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

## 示例
以下是一个简单的 OriginIR 程序示例，展示了如何使用 OriginIR 描述量子线路：
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

**解释**
1. QINIT 5：初始化 5 个量子比特。
2. CREG 2：初始化 2 个经典寄存器。
3. H q[0]：在量子比特 0 上应用 Hadamard 门。
4. RX q[1], (1.57)：在量子比特 1 上应用 RX 门，参数为 1.57。
5. CNOT q[0], q[1]：在量子比特 0 和 1 上应用 CNOT 门。
6. RY q[2], (0.785)：在量子比特 2 上应用 RY 门，参数为 0.785。
7. CZ q[1], q[2]：在量子比特 1 和 2 上应用 CZ 门。
8. U3 q[3], (1.57, 0.785, 0.392)：在量子比特 3 上应用 U3 门，参数为 (1.57, 0.785, 0.392)。
9. TOFOLI q[0], q[1], q[3]：在量子比特 0、1 和 3 上应用 Toffoli 门。
10. BARRIER q[0], q[1], q[2], q[3]：插入一个屏障，用于同步量子比特 0、1、2、3 的操作。
11. CONTROL q[0], q[1]：开始一个控制块，控制量子比特 0 和 1。
12. X q[2]：在量子比特 2 上应用 X 门。
13. Y q[3]：在量子比特 3 上应用 Y 门。
14. ENDCONTROL q[0], q[1]：结束一个控制块。
15. DAGGER：开始一个 DAGGER 块。
16. H q[4]：在量子比特 4 上应用 Hadamard 门。
17. CNOT q[4], q[0]：在量子比特 4 和 0 上应用 CNOT 门。
18. ENDDAGGER：结束一个 DAGGER 块。
19. MEASURE q[0], c[0]：在量子比特 0 上测量，结果存入经典比特 0。
20. MEASURE q[1], c[1]：在量子比特 1 上测量，结果存入经典比特 1。