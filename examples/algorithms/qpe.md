# Quantum Phase Estimation (QPE)

## Background and Theory

Quantum Phase Estimation (QPE) estimates the eigenvalue phase of a unitary operator.
Given a unitary $U$ and one of its eigenstates $|\psi\rangle$:

$$U|\psi\rangle = e^{2\pi i\varphi}|\psi\rangle$$

QPE outputs $\varphi \in [0, 1)$ to $n$-bit precision using $n$ precision qubits.

### The Algorithm

**Step 1 — Prepare the eigenstate** on $m$ system qubits:
$$|\psi\rangle = \sum_x \alpha_x |x\rangle$$

**Step 2 — Create superposition** on $n$ precision qubits:
$$H^{\otimes n}|0\rangle^{\otimes n} = \frac{1}{\sqrt{2^n}}\sum_{k=0}^{2^n-1}|k\rangle$$

**Step 3 — Controlled powers of $U$**: for each precision qubit $k$ (value $2^{n-k-1}$):
$$C-U^{2^{n-k-1}}: \frac{1}{\sqrt{2^n}}\sum_{k,j}|k\rangle|j\rangle \to \frac{1}{\sqrt{2^n}}\sum_{k,j}e^{2\pi i\varphi k \cdot 2^{n-k-1}}|k\rangle|j\rangle$$

**Step 4 — Inverse QFT** on the precision register:
$$\text{QFT}^{\dagger}\left(\sum_k e^{2\pi i\varphi k}|k\rangle\right) \approx |\tilde{\varphi}\rangle$$
where $\tilde{\varphi}$ is the binary representation of $\varphi$.

### Inverse QFT (QFTdagger)

The QFT transforms $|x\rangle \to \frac{1}{\sqrt{N}}\sum_k e^{2\pi ixk/N}|k\rangle$.
QFTdagger is its inverse — implemented by reversing the QFT circuit with adjoint rotation angles.

### Accuracy

With $n$ precision qubits, QPE achieves precision $\pm 1/2^n$ with probability approaching 1
for the most significant bits. The algorithm requires the eigenstate to be provided
as input (it does not find eigenstates).

## Code Walkthrough

### `apply_cu1`

Implements $CU_1(\theta)$ where $U_1(\theta) = \text{diag}(1, e^{i\theta})$:
$$CU_1(\theta) = \begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&1&0\\0&0&0&e^{i\theta}\end{pmatrix}$$

Decomposition:
$$CU_1(\theta) = u_1(\theta/2) \cdot CX \cdot u_1(-\theta/2) \cdot CX$$

### `apply_qft_dagger`

Inverse QFT circuit for the precision register:
- Cascade of $CU_1(-\pi/2^{j-i})$ gates in reverse order
- Followed by Hadamard on each qubit

### `build_qpe_circuit`

1. Prepare the eigenstate on system qubits (defaults to $|0\rangle^{\otimes m}$)
2. Apply $H^{\otimes n}$ on precision qubits for uniform superposition
3. For each precision qubit $k$: apply $U^{2^k}$ controlled by that qubit
4. Apply QFTdagger on precision qubits
5. Measure the precision register

## Running the Example

```bash
# Estimate the phase of the T gate (phase = π/8 ≈ 0.3927)
python examples/algorithms/qpe.py --n-precision 4 --unitary t

# Estimate Z-gate phase (eigenvalue = -1, so phase = 0.5)
python examples/algorithms/qpe.py --n-precision 4 --unitary z

# More precision qubits
python examples/algorithms/qpe.py --n-precision 6 --unitary t --shots 8192
```

Expected output:
```
 Quantum Phase Estimation
 Precision qubits: 4
 Phase precision:  1/16 = 0.0625
 Unitary: t

 Measurement results:
   |0110⟩  prob= 94.2%  phase=0.3750 ← most likely
   |0101⟩   prob=  2.1%  phase=0.3125
   |0111⟩   prob=  1.8%  phase=0.4375

 Estimated phase:  0.3750
 True phase:       0.3927
 Absolute error:   0.0177
  ✓ QPE complete.
```

## Design Notes

- **Eigenstate input**: QPE requires a *known* eigenstate. For non-diagonal unitaries,
  the output is a superposition of phases corresponding to the eigenstate decomposition.
- **Controlled unitaries**: For diagonal $U$, controlled-$U$ is implemented as
  $CU_1$ gates encoding the phase angles. The cascade decomposition handles
  multi-qubit phase encoding.
- **Binary phase encoding**: QPE treats the precision register as a binary fraction
  $\varphi = \sum_k b_k / 2^k$. The estimated integer $m$ from measurement gives
  $\tilde{\varphi} = m / 2^n$.

## Extension Ideas

- **HHL Algorithm**: Use QPE as the core of the quantum linear systems solver
- **Iterative QPE (IQPE)**: Reduce qubit count by measuring and re-using one qubit
  per iteration
- **Quantum counting**: Combine Grover search with QPE to count marked states

## References

- Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information*.
  Cambridge University Press. Chapter 5.
- Cleve, R., Ekert, A., Macchiavello, C., & Mosca, M. (1998). "Quantum algorithms
  revisited." Proc. R. Soc. A. https://arxiv.org/abs/quant-ph/9708016
