# OpenQASM 2.0支持

QPanda-lite对QASM2.0有不完整的支持。

## Explicit look-up table for all operations in QASM 2.0 and OriginIR

| QASM指令 | 矩阵形式 |
|----------|----------|
| `X`      | $\begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}$ |
| `Y`      | $\begin{bmatrix} 0 & -i \\ i & 0 \end{bmatrix}$ |
| `Z`      | $\begin{bmatrix} 1 & 0 \\0 & -1 \end{bmatrix}$ |
| `H`      | $\frac{1}{\sqrt{2}} \begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix}$ |
| `S`      | $\begin{bmatrix} 1 & 0 \\ 0 & i \end{bmatrix}$ |
| `T`      | $\begin{bmatrix} 1 & 0 \\ 0 & e^{i\pi/4} \end{bmatrix}$ |
| `CNOT`   | $\begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 1 & 0 \end{bmatrix}$ |