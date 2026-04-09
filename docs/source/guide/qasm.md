# OpenQASM 2.0

## 什么时候看本页

当你需要将线路导出为 OpenQASM 2.0 格式，或者需要在 OriginIR 与 QASM 之间进行格式互转时，看本页。

## 本页解决的问题

- 想用 `circuit.qasm` 导出 OpenQASM 2.0 格式的线路文本
- 想将已有的 QASM 文本转换为 OriginIR 格式
- 需要提交到 Quafu、IBM 等要求 QASM 格式的平台
- 想查阅某个门在 OriginIR 和 QASM 之间的对应关系

> 如果你还不知道如何构建线路，请先阅读 [构建量子线路](circuit.md)。

## QASM 在 QPanda-lite 中的角色

OpenQASM 2.0 是量子计算领域广泛使用的跨平台线路描述标准。在 QPanda-lite 中，QASM 主要用于以下场景：

- **跨平台提交**：Quafu、IBM 等平台接受 QASM 格式的线路
- **外部互操作**：导入已有的 QASM 文件并转换为 QPanda-lite 可处理的格式

> **注意**：QPanda-lite 对 OpenQASM 2.0 的支持目前**不完整**——并非所有 QASM 2.0 指令都能被解析或互转。使用前请确认你需要的门在下方的对照表中列出。详见 `qpandalite.qasm` 模块的 API 参考。

## 格式互转操作

QPanda-lite 支持在 Circuit 对象、OriginIR 和 QASM 之间进行格式互转。以下是核心互转路径：

### Circuit → QASM

构建完线路后，直接获取 OpenQASM 2.0 文本：

```python
from qpandalite.circuit_builder import Circuit

circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)

qasm_str = circuit.qasm
print(qasm_str)
```

### Circuit → OriginIR

同一线路也可导出为 OriginIR 格式：

```python
originir_str = circuit.originir
print(originir_str)
```

> 关于线路构建与格式导出的完整 API，见 [构建量子线路](circuit.md)。关于 OriginIR 格式的详细说明，见 [OriginIR](originir.md)。

### QASM → OriginIR

如果你有外部 QASM 文本（例如从其他工具生成），可以将其转换为 OriginIR：

```python
from qpandalite.qasm.translate_qasm2_oir import translate_qasm2_to_originir

originir_str = translate_qasm2_to_originir(qasm_str)
```

### 互转边界

并非所有门都能在 OriginIR 和 QASM 之间互转。当前的互转能力覆盖了常见的单比特门、双比特门和三比特门，具体对照见下方参考区。如果互转过程中遇到不支持的门，会抛出异常并提示。

## QASM 2.0 与 OriginIR 门对照表

> 以下是 QASM 2.0 与 OriginIR 之间支持的操作对照表（含矩阵形式）。日常使用中通常无需手动查阅，仅在排查格式问题或确认互转范围时参考。

| OriginIR | QASM 指令 | 矩阵形式 |
|----------|----------|----------|
| **1q operation** |
| `X`      | `x`      | $\begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}$ |
| `Y`      | `y`      | $\begin{bmatrix} 0 & -i \\ i & 0 \end{bmatrix}$ |
| `Z`      | `z`      | $\begin{bmatrix} 1 & 0 \\0 & -1 \end{bmatrix}$ |
| `H`      | `h`      | $\frac{1}{\sqrt{2}} \begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix}$ |
| `SX`     | `sx`     | $\frac{1}{2} \begin{bmatrix} 1+i & 1-i \\ 1-i & 1+i \end{bmatrix}$ |
| `SX` (.dagger) | `sxdg`   | $\frac{1}{2} \begin{bmatrix} 1-i & 1+i \\ 1+i & 1-i \end{bmatrix}$ |
| `S`      | `s`      | $\begin{bmatrix} 1 & 0 \\ 0 & i \end{bmatrix}$ |
| `S`  (.dagger) | `sdg`    | $\begin{bmatrix} 1 & 0 \\ 0 & -i \end{bmatrix}$ |
| `T`      | `t`      | $\begin{bmatrix} 1 & 0 \\ 0 & e^{i\pi/4} \end{bmatrix}$ |
| `T`  (.dagger) | `tdg`    | $\begin{bmatrix} 1 & 0 \\ 0 & e^{-i\pi/4} \end{bmatrix}$ |
| **2q operation** |
| `CNOT`   | `cx`     | $\begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 1 & 0 \end{bmatrix}$ |
| `CY`     | `cy`     | $\begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & -i \\ 0 & 0 & i & 0 \end{bmatrix}$ |
| `CZ`     | `cz`     | $\begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & -1 \end{bmatrix}$ |
| `SWAP`   | `swap`   | $\begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$ |
| `CH`     | `ch`     | $\begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & \frac{1}{\sqrt{2}} & \frac{1}{\sqrt{2}} \\ 0 & 0 & \frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{2}} \end{bmatrix}$ |
| **3q operation** |
| `TOFFOLI` | `ccx`    | $\begin{bmatrix} 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\ 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \end{bmatrix}$ |
| `CSWAP`   | `cswap`  | $\begin{bmatrix} 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \end{bmatrix}$ |
| **4q operation** |
| `X` (with 3 controls) | `c3x` | $\begin{bmatrix} 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \end{bmatrix}$ |
| **1q1p operation**|
| RX        | `rx(θ)`  | $\begin{bmatrix} \cos(\theta/2) & -i\sin(\theta/2) \\ -i\sin(\theta/2) & \cos(\theta/2) \end{bmatrix}$ |
| RY        | `ry(θ)`  | $\begin{bmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{bmatrix}$ |
| RZ        | `rz(θ)`  | $\begin{bmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{bmatrix}$ |
| P         | `p(θ)`   | $\begin{bmatrix} 1 & 0 \\ 0 & e^{i\theta} \end{bmatrix}$ |
| U1        | `u1(λ)`  | $\begin{bmatrix} 1 & 0 \\ 0 & e^{i\lambda} \end{bmatrix}$ |
| **1q2p operation**|
| U2        | `u2(φ, λ)` | $\frac{1}{\sqrt{2}} \begin{bmatrix} 1 & -e^{i\lambda} \\ e^{i\varphi} & e^{i(\varphi + \lambda)} \end{bmatrix}$ |
| **1q3p operation**|
| U3        | `u3(θ, φ, λ)` | $\begin{bmatrix} \cos(\theta/2) & -e^{i\lambda}\sin(\theta/2) \\ e^{i\varphi}\sin(\theta/2) & e^{i(\varphi + \lambda)}\cos(\theta/2) \end{bmatrix}$ |
| **2q1p operation**|
| XX        | `rxx(θ)` | $e^{-i \frac{\theta}{2} X \otimes X} = \begin{bmatrix} \cos(\theta/2) & 0 & 0 & -i\sin(\theta/2) \\ 0 & \cos(\theta/2) & -i\sin(\theta/2) & 0 \\ 0 & -i\sin(\theta/2) & \cos(\theta/2) & 0 \\ -i\sin(\theta/2) & 0 & 0 & \cos(\theta/2) \end{bmatrix}$ |
| YY        | `ryy(θ)` | $e^{-i \frac{\theta}{2} Y \otimes Y} = \begin{bmatrix} \cos(\theta/2) & 0 & 0 & i\sin(\theta/2) \\ 0 & \cos(\theta/2) & -i\sin(\theta/2) & 0 \\ 0 & -i\sin(\theta/2) & \cos(\theta/2) & 0 \\ i\sin(\theta/2) & 0 & 0 & \cos(\theta/2) \end{bmatrix}$ |
| ZZ        | `rzz(θ)` | $e^{-i \frac{\theta}{2} Z \otimes Z} = \begin{bmatrix} e^{-i\theta/2} & 0 & 0 & 0 \\ 0 & e^{i\theta/2} & 0 & 0 \\ 0 & 0 & e^{i\theta/2} & 0 \\ 0 & 0 & 0 & e^{-i\theta/2} \end{bmatrix}$ |
| XY        | `rxy(θ)` | $e^{-i \frac{\theta}{2} \left(\frac{1}{2}(X\otimes X+Y\otimes Y)\right)} = \begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & \cos(\theta/2) & -i\sin(\theta/2) & 0 \\ 0 & -i\sin(\theta/2) & \cos(\theta/2) & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$ |

## 下一步

- 如果你还不知道如何构建线路，先阅读 [构建量子线路](circuit.md)
- 如果你想用 QASM 文本直接模拟，见 [本地模拟](simulation.md)
- 如果你想提交到 Quafu 或 IBM 平台，见 [提交任务](submit_task.md)
- 如果你需要了解 OriginIR 格式，见 [OriginIR](originir.md)
