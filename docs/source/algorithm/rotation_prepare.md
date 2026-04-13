# Arbitrary State Preparation via Rotation

## Background

The **Shende–Bullock–Markov (SBM)** algorithm prepares an arbitrary $n$-qubit
quantum state from $|0\rangle^{\otimes n}$ using a sequence of multiplexed
rotations. The key insight is:

1. Start from the target state and **disentangle** qubits one at a time,
   reducing to $|00\ldots0\rangle$.
2. Collect the inverse gates.
3. Apply them in **reverse order** to go from $|00\ldots0\rangle$ to the target.

### Gate Complexity

The SBM decomposition uses $O(2^n)$ CNOT gates and $O(2^n)$ single-qubit
rotations — optimal for general state preparation.

## Running the Example

```bash
# Bell state
python examples/state_preparation/rotation_prepare.py --state bell

# GHZ state (3 qubits)
python examples/state_preparation/rotation_prepare.py --state ghz

# W state (3 qubits)
python examples/state_preparation/rotation_prepare.py --state w

# Random state
python examples/state_preparation/rotation_prepare.py --state random
```

## Code Walkthrough

```python
import numpy as np
from qpandalite.algorithmics.state_preparation import rotation_prepare

target = np.array([1, 0, 0, 1]) / np.sqrt(2)  # Bell state
c = Circuit()
rotation_prepare(c, target)
```

### Key Features

- **Automatic normalisation**: The target vector is normalised if needed.
- **Any dimension**: Supports $n$-qubit states ($2^n$-dimensional vectors).
- **High fidelity**: Achieves fidelity > $1 - 10^{-8}$ in simulation.

## States Demonstrated

| State | Description |
|-------|-------------|
| Bell | $(|00\rangle + |11\rangle)/\sqrt{2}$ |
| GHZ | $(|0\rangle^{\otimes n} + |1\rangle^{\otimes n})/\sqrt{2}$ |
| W | Equal superposition of single-excitation states |
| Random | Haar-random normalised state |

## References

1. Shende, V. V., Bullock, S. S., & Markov, I. L. (2006). "Synthesis of
   Quantum Logic Circuits." *IEEE Transactions on CAD* 25(6).
2. Möttönen, M. et al. (2004). "Transformation of quantum states using
   uniformly controlled rotations." *Quantum Information & Computation* 5(6).
