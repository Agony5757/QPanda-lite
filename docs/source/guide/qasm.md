# OpenQASM 2.0支持

QPanda-lite对QASM2.0有不完整的支持。

## Explicit look-up table for all operations in QASM 2.0 and OriginIR

OriginIR | QASM指令 | 矩阵形式 |
|----------|----------|----------|
| **1q operation** |
| `X`      | `x`      | $\begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}$ |
| `Y`      | `y`      | $\begin{bmatrix} 0 & -i \\ i & 0 \end{bmatrix}$ |
| `Z`      | `z`      | $\begin{bmatrix} 1 & 0 \\0 & -1 \end{bmatrix}$ |
| `H`      | `h`      | $\frac{1}{\sqrt{2}} \begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix}$ |
| `S`      | `s`      | $\begin{bmatrix} 1 & 0 \\ 0 & i \end{bmatrix}$ |
| `T`      | `t`      | $\begin{bmatrix} 1 & 0 \\ 0 & e^{i\pi/4} \end{bmatrix}$ |
| **2q operation** |
| `CNOT`   | `cx`      | $\begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 1 & 0 \end{bmatrix}$ |
| **3q operation** |
| `TOFFOLI` | `ccx`    | $\begin{bmatrix} 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\ 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \end{bmatrix}$ |
| **1q1p operation**|
| `rx(θ)`  | $\begin{bmatrix} \cos(\theta/2) & -i\sin(\theta/2) \\ -i\sin(\theta/2) & \cos(\theta/2) \end{bmatrix}$ |
| `ry(θ)`  | $\begin{bmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{bmatrix}$ |
| `rz(θ)`  | $\begin{bmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{bmatrix}$ |
| `p(θ)`   | $\begin{bmatrix} 1 & 0 \\ 0 & e^{i\theta} \end{bmatrix}$ |
| `u1(λ)`  | $\begin{bmatrix} 1 & 0 \\ 0 & e^{i\lambda} \end{bmatrix}$ |
| **1q2p operation**|
| `u2(φ, λ)` | $\frac{1}{\sqrt{2}} \begin{bmatrix} 1 & -e^{i\lambda} \\ e^{i\varphi} & e^{i(\varphi + \lambda)} \end{bmatrix}$ |
| **1q3p operation**|
| `u3(θ, φ, λ)` | $\begin{bmatrix} \cos(\theta/2) & -e^{i\lambda}\sin(\theta/2) \\ e^{i\varphi}\sin(\theta/2) & e^{i(\varphi + \lambda)}\cos(\theta/2) \end{bmatrix}$ |
| **2q1p operation**|
| `rxx(θ)` | $e^{-i \frac{\theta}{2} X \otimes X} = \begin{bmatrix} \cos(\theta/2) & 0 & 0 & -i\sin(\theta/2) \\ 0 & \cos(\theta/2) & -i\sin(\theta/2) & 0 \\ 0 & -i\sin(\theta/2) & \cos(\theta/2) & 0 \\ -i\sin(\theta/2) & 0 & 0 & \cos(\theta/2) \end{bmatrix}$ |
| `rzz(θ)` | $e^{-i \frac{\theta}{2} Z \otimes Z} = \begin{bmatrix} e^{-i\theta/2} & 0 & 0 & 0 \\ 0 & e^{i\theta/2} & 0 & 0 \\ 0 & 0 & e^{i\theta/2} & 0 \\ 0 & 0 & 0 & e^{-i\theta/2} \end{bmatrix}$ |