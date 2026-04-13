# Grover's Search Algorithm

## Background and Theory

Grover's search algorithm (Grover, 1996) provides a quadratic speedup for unstructured search.
Given an oracle $f : \{0,1\}^n \to \{0,1\}$ such that $f(x) = 1$ iff $x$ is the marked
state $|w\rangle$, Grover's algorithm finds $|w\rangle$ in $O(\sqrt{N})$ oracle calls
instead of $O(N)$, where $N = 2^n$.

### Key Components

**1. Oracle $U_\omega$**
Phase-flip oracle that multiplies the amplitude of the marked state by $-1$:

$$U_\omega |x\rangle = (-1)^{f(x)} |x\rangle$$

The standard construction uses an ancilla qubit in the magic state $|-\rangle = (|0\rangle - |1\rangle)/\sqrt{2}$:

$$U_\omega |x\rangle |-\rangle = |x\rangle \otimes (-1)^{f(x)} |-\rangle$$

**2. Diffusion Operator $D$**
Also called the *amplitude amplification* operator:

$$D = 2|s\rangle\langle s| - I$$

where $|s\rangle = H^{\otimes n}|0\rangle^{\otimes n}$ is the uniform superposition.
$D$ reflects any vector about $|s\rangle$, transferring amplitude from unmarked
to marked states.

**3. Grover Iteration**
The combined oracle + diffusion step:

$$G = D \cdot U_\omega$$

Applied $R \approx \frac{\pi}{4}\sqrt{N}$ times to $|s\rangle$, this concentrates
the amplitude on the marked state.

### State Evolution

Starting from $|s\rangle = \frac{1}{\sqrt{N}} \sum_x |x\rangle$:

After one Grover iteration, the state is in a 2D subspace spanned by $\{|w\rangle, |s'\rangle\}$
where $|s'\rangle$ is the superposition over all non-marked states.

The amplitude on $|w\rangle$ grows as $\sin((2R+1)\theta)$ where $\sin\theta = 1/\sqrt{N}$.

## Code Walkthrough

### `build_oracle`

```python
def build_oracle(n_qubits, marked_state):
```

Builds the phase-flip oracle for the given marked state:

1. **Ancilla preparation**: Initialise ancilla qubit to $|-\rangle = X \cdot H |0\rangle$
2. **Marked-state encoding**: Flip data qubits that are $|0\rangle$ in the marked state
3. **Phase kickback**: Apply multi-controlled Z (CCZ) from data qubits to ancilla
4. **Uncompute**: Restore the flipped qubits

### `build_diffusion`

Implements $D = H^{\otimes n} \cdot Z^{\otimes n} \cdot H^{\otimes n}$:

1. Apply $H^{\otimes n}$ to convert $|s\rangle \to |0\rangle^{\otimes n}$
2. Apply $Z^{\otimes n}$ to flip the phase of $|0\rangle^{\otimes n}$
3. Apply $H^{\otimes n}$ again — net effect is reflection about $|s\rangle$

### `run_grover`

End-to-end Grover search:

1. Initialise data qubits to $|+\rangle$ (Hadamard on $|0\rangle$)
2. Apply optimal number $R = \lfloor \frac{\pi}{4}\sqrt{N} \rfloor$ of Grover iterations
3. Measure all data qubits

## Running the Example

```bash
# Basic run with 3 qubits, marked state = 5
python examples/algorithms/grover.py --n-qubits 3 --marked-state 5

# Larger search space
python examples/algorithms/grover.py --n-qubits 4 --marked-state 10 --shots 8192
```

Expected output:
```
 Grover's Search — 3 data qubits
 Marked state: 5 (101)
 Search space: 8 states

 Results (top 5 most probable states):
   |101⟩  95.2% ← TARGET
   |010⟩   1.8%
   |000⟩   1.2%
   |110⟩   0.8%
   |001⟩   0.6%

 Target probability: 95.2%
 Expected (ideal): ~95.0% (after optimal iterations)
```

## Design Notes

- **Ancilla qubit**: One extra qubit is used for the oracle to enable phase kickback.
  This is the standard "auxiliary qubit" approach and works for any number of qubits.
- **Multi-controlled Z**: For 2-qubit case, `ccx` (Toffoli) with a final Z implements CCZ.
  For >2 qubits, a linear-depth CNOT cascade with H on the target implements MCZ.
- **Optimal iterations**: The iteration count $R = \lfloor \frac{\pi}{4}\sqrt{N} \rfloor$
  maximises the success probability. For small $N$, rounding and a small cap
  prevent overshooting.
- **Measurement**: Only the data qubits are measured (ancilla is not measured).

## Extension Ideas

- **Multi-target Grover**: Replace single target with $M$ marked states;
  optimal iterations become $\frac{\pi}{4}\sqrt{N/M}$
- **Inhomogeneous Grover**: Different oracle strengths per state
- **Amplitude estimation**: Use `state_tomography` to characterise the
  pre-measurement state and estimate success probability analytically

## References

- Grover, L. K. (1996). "A fast quantum mechanical algorithm for database search."
  STOC '96. https://arxiv.org/abs/quant-ph/9605043
- Brassard, G., Høyer, P., Mosca, M., & Tapp, A. (2002). "Quantum Amplitude Amplification
  and Estimation." AMS. https://arxiv.org/abs/quant-ph/0005055
