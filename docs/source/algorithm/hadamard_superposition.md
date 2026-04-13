# Hadamard Superposition State Preparation

## Background

The Hadamard gate $H$ creates an equal superposition from a computational basis state:

$$H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} = |+\rangle$$

Applying Hadamard on all $n$ qubits produces the uniform superposition:

$$H^{\otimes n}|0\rangle^{\otimes n} = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle$$

This is one of the most fundamental quantum states, used as the starting point for
Grover's search, QAOA, Deutsch-Jozsa, and many other algorithms.

## Running the Example

```bash
python examples/state_preparation/hadamard_superposition.py --n-qubits 3
```

## Code Walkthrough

```python
from qpandalite.algorithmics.state_preparation import hadamard_superposition

c = Circuit()
hadamard_superposition(c, qubits=[0, 1, 2])
# Circuit now has H gates on all specified qubits
```

### Key Features

- **Subset selection**: Apply Hadamard only to specific qubits while leaving
  others in $|0\rangle$.
- **Automatic allocation**: Qubits are allocated automatically based on the
  specified indices.

## Output

The demo prints the statevector amplitudes and probability distribution,
verifying that all amplitudes have equal magnitude $1/\sqrt{2^n}$.
