# Quantum State Tomography

## Background

Quantum state tomography reconstructs the full density matrix $\rho$ of a quantum
state from a complete set of measurements. For $n$ qubits, this requires
measuring in all $3^n$ Pauli bases (XX, XY, XZ, YX, ..., ZZ).

### Protocol

For each of the $3^n$ combinations of single-qubit Pauli bases:

1. **Rotate**: Apply basis-change gates to map the measurement basis to
   the computational ($Z$) basis.
2. **Measure**: Collect shot-based measurement outcomes.
3. **Reconstruct**: Combine all measurement results to build the density matrix
   via linear inversion or maximum-likelihood estimation.

### Complexity

- Measurements: $O(3^n \cdot S)$ where $S$ is shots per basis
- Classical post-processing: $O(4^n)$ for density matrix reconstruction
- **Limitation**: Exponential scaling makes this practical only for small systems

For larger systems, consider **Classical Shadow tomography** (see
`shadow_tomography.py`) which has much better scaling.

## Running the Example

```bash
python examples/measurement/state_tomography.py --n-shots 2000
```

## Code Walkthrough

```python
from qpandalite.algorithmics.measurement import state_tomography, tomography_summary

# Run tomography
results = state_tomography(circuit, qubits=[0, 1], shots=2000)

# Get reconstructed density matrix
rho = tomography_summary(results, n_qubits=2)
```

### Key Features

- **Full reconstruction**: Recovers the complete density matrix including
  off-diagonal coherences.
- **Shot-based**: Works with realistic (noisy) measurement outcomes.
- **Fidelity estimation**: Compare reconstructed state with target.

## Output

The demo shows:
- Reconstructed density matrix
- Fidelity with the exact state
- Population comparison (diagonal elements)

## References

1. James, D. F. V. et al. (2001). "Measurement of qubits." *Physical Review A*
   64, 052312.
2. Smolin, J. A. et al. (2012). "Efficient method for computing the
   maximum-likelihood quantum state from measurements with additive Gaussian
   noise." *Physical Review Letters* 108, 070502.
