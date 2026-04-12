# Quantum Approximate Optimization Algorithm (QAOA)

## Background and Theory

QAOA (Farhi et al., 2014) is a hybrid quantum-classical algorithm for solving
combinatorial optimisation problems. It approximates the solution by applying
alternating layers of cost and mixer unitaries.

### MaxCut Problem

Given a graph $G = (V, E)$, MaxCut seeks a partition of $V$ into two sets
that maximises the number of edges crossing the partition.

**Cost Hamiltonian:**

$$H_C = -\frac{1}{2} \sum_{(i,j) \in E} (1 - Z_i Z_j)$$

Maximising $-H_C$ is equivalent to maximising the cut.

### QAOA Ansatz

The QAOA state is prepared as:

$$|\psi(\boldsymbol{\beta}, \boldsymbol{\gamma})\rangle
= \prod_{l=1}^{p} e^{-i\beta_l H_M} e^{-i\gamma_l H_C} |+\rangle^{\otimes n}$$

where $H_M = \sum_i X_i$ is the mixer Hamiltonian, and $p$ is the number of
layers (higher $p$ → better approximation).

### Algorithm Flow

```
Initialise |+⟩⊗n → Apply e^{-iγ₁ Hc} → Apply e^{-iβ₁ Hm} → ... → Measure ⟨Hc⟩
                     ↑                                                    ↓
                     └──────── Classical optimiser (update β, γ) ←───────┘
```

### Components Used

| Component | Module | Role |
|-----------|--------|------|
| `qaoa_ansatz` | `algorithmics.ansatz` | Parameterised QAOA circuit |
| `OriginIR_Simulator` | `simulator` | Statevector simulation |

## Running the Example

```bash
# Default: p=2 layers, triangle graph
python examples/algorithms/qaoa.py

# More layers
python examples/algorithms/qaoa.py -p 3

# More iterations
python examples/algorithms/qaoa.py -p 2 --maxiter 200
```

## Code Walkthrough

### 1. Define the cost Hamiltonian

```python
def maxcut_hamiltonian(edges, n_nodes):
    terms = []
    for i, j in edges:
        terms.append((f"Z{i}Z{j}", 0.5))
    return terms
```

### 2. Build the ansatz

```python
from qpandalite.algorithmics.ansatz import qaoa_ansatz

circuit = qaoa_ansatz(
    cost_hamiltonian=[("Z0Z1", 0.5), ("Z1Z2", 0.5), ("Z0Z2", 0.5)],
    p=2,
    betas=[0.5, 0.3],
    gammas=[0.7, 0.2],
)
```

### 3. Evaluate and optimise

The energy $\langle H_C \rangle$ is computed from the statevector and
fed to a coordinate-descent optimiser.

### Expected Results

For a triangle graph (3 edges):
- Optimal cut: 2 edges (partition one vertex from the other two)
- QAOA with $p=2$ should achieve the optimal cut with high probability

## Extensions

- **Weighted MaxCut**: Add edge weights to the Hamiltonian.
- **Different graphs**: Try random graphs, planar graphs, etc.
- **Higher $p$**: More layers improve approximation ratio toward 1.0.
- **Shot-based**: Use `QASM_Simulator` for realistic noisy measurement.

## References

1. Farhi, E., Goldstone, J., & Gutmann, S. (2014). "A Quantum Approximate
   Optimization Algorithm." arXiv:1411.4028.
2. Zhou, L. et al. (2020). "Quantum Approximate Optimization Algorithm:
   Performance, Mechanism, and Implementation on Near-Term Devices."
   *Frontiers in Physics* 10, 585524.
