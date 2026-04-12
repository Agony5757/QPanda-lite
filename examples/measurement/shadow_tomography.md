# Classical Shadow Tomography

## Background

Classical Shadow tomography (Huang, Kueng & Preskill, 2020) is a highly efficient
method for predicting many properties of a quantum system from few measurements.

### Key Idea

Instead of full state tomography (which requires $O(4^n)$ measurements), classical
shadow collects $N$ random Pauli measurements ("snapshots") and uses them to
predict $M$ observables with sample complexity:

$$N = O\left(\log(M) \cdot \max_i \|O_i\|_{\text{shadow}}^2 / \epsilon^2\right)$$

This is **exponentially more efficient** than full tomography for predicting
local observables.

### Protocol

1. **Random basis measurement**: For each snapshot, randomly choose $X$, $Y$, or
   $Z$ basis for each qubit. Measure and record outcome.
2. **Classical post-processing**: Reconstruct "classical shadow" — a snapshot
   of the density matrix.
3. **Prediction**: Average over snapshots to estimate any observable.

## Running the Example

```bash
python examples/measurement/shadow_tomography.py --n-shadow 100 --n-shots 1000
```

## Code Walkthrough

```python
from qpandalite.algorithmics.measurement import classical_shadow, shadow_expectation

# Collect shadow snapshots
shadows = classical_shadow(circuit, qubits=[0, 1], shots=1000, n_shadow=100)

# Estimate observables
est = shadow_expectation(shadows, {"Z0Z1": 1.0})
```

### Key Features

- **Efficient**: Predict many observables from few measurements.
- **Flexible**: Works with any Pauli observable.
- **No calibration needed**: Random Pauli measurements are device-ready.

## References

1. Huang, H.-Y., Kueng, R., & Preskill, J. (2020). "Predicting many properties
   of a quantum system from very few measurements." *Nature Physics* 16, 1050–1057.
2. Aaronson, S. & Rothblum, G. N. (2019). "Gentle Measurement of Quantum States
   and Differential Privacy." STOC '19.
