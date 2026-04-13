# Variational Quantum Eigensolver (VQE)

## Background and Theory

The Variational Quantum Eigensolver (VQE) is a hybrid quantum-classical algorithm
for finding the ground-state energy of molecular Hamiltonians. It was first
demonstrated by Peruzzo et al. (2014).

### Core Idea

VQE exploits the **variational principle**: for any parameterised trial state
$|\psi(\boldsymbol{\theta})\rangle$,

$$\langle\psi(\boldsymbol{\theta})|H|\psi(\boldsymbol{\theta})\rangle
\geq E_0$$

where $E_0$ is the true ground-state energy. By minimising the energy
expectation value over $\boldsymbol{\theta}$, we approach $E_0$.

### Algorithm Flow

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  Prepare     │───▶│  Measure      │───▶│  Classical    │
│  |ψ(θ)⟩      │    │  ⟨ψ|H|ψ⟩     │    │  Optimiser    │
│  (ansatz)    │    │  (expectation)│    │  (update θ)   │
└─────────────┘    └──────────────┘    └──────────────┘
       ▲                                       │
       └───────────────────────────────────────┘
                    repeat until convergence
```

1. **Ansatz**: Prepare $|\psi(\boldsymbol{\theta})\rangle$ using a parameterised
   circuit (e.g., UCCSD).
2. **Measurement**: Estimate $\langle H \rangle = \sum_i h_i \langle P_i \rangle$
   by measuring each Pauli string.
3. **Classical optimisation**: Update $\boldsymbol{\theta}$ to minimise energy.

### Components Used

| Component | Module | Role |
|-----------|--------|------|
| `uccsd_ansatz` | `algorithmics.ansatz` | Parameterised trial state |
| `pauli_expectation` | `algorithmics.measurement` | Energy measurement |
| `OriginIR_Simulator` | `simulator` | Statevector simulation |

### H₂ Molecule

This example solves for the ground state of H₂ in a minimal STO-3G basis
(4 spin-orbitals, 2 electrons). The Hamiltonian is Bravyi–Kitaev mapped:

$$H = \sum_i h_i P_i + E_{\text{nuclear}}$$

**Expected result**: $E_0 \approx -1.137$ Ha (exact FCI).

## Running the Example

```bash
# Default: H₂, 100 iterations
python examples/algorithms/vqe.py

# Custom iterations
python examples/algorithms/vqe.py --maxiter 200
```

## Code Walkthrough

### 1. Define the Hamiltonian

```python
H2_HAMILTONIAN = [
    ("I0", -0.8105),
    ("Z0", +0.1720),
    ("Z0Z1", +0.1205),
    ("X0X1Y2Y3", -0.0455),
    # ... more terms
]
```

### 2. Build the ansatz

```python
from qpandalite.algorithmics.ansatz import uccsd_ansatz

circuit = uccsd_ansatz(n_qubits=4, n_electrons=2, params=theta)
```

UCCSD generates single and double excitation gates parameterised by $\boldsymbol{\theta}$.

### 3. Evaluate energy

```python
energy = sum(
    coeff * expectation_value(pauli_str, circuit)
    for pauli_str, coeff in hamiltonian
)
```

### 4. Optimise

A simple coordinate-descent optimiser updates each parameter to minimise energy.
In production, use scipy's `COBYLA` or `SLSQP`.

## Extensions

- **Larger molecules**: Extend to LiH, BeH₂, H₂O by expanding the Hamiltonian.
- **Better ansätze**: Try Hardware-Efficient Ansatz (`hea`) for NISQ devices.
- **Noise mitigation**: Use `classical_shadow` for efficient measurement.
- **Shot-based simulation**: Replace statevector with `QASM_Simulator` for
  realistic measurement statistics.

## References

1. Peruzzo, A. et al. (2014). "A variational eigenvalue solver on a photonic
   quantum processor." *Nature Communications* 5, 4213.
2. McClean, J. R. et al. (2016). "The theory of variational hybrid
   quantum-classical algorithms." *New Journal of Physics* 18, 023023.
