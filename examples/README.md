# QPanda-Lite Examples

Runnable demonstrations of quantum algorithms and core workflows.

## Contents

### Getting Started

| Example | Description |
|---------|-------------|
| [Circuit Remapping](getting-started/1_circuit_remap.py) | Build a circuit and remap qubits for real hardware |
| [Dummy Server](getting-started/2_dummy_server.py) | Submit tasks to the local dummy simulator |
| [Result Post-Processing](getting-started/3_result_postprocess.py) | Convert and analyze results with result adapters |

### Algorithms

> Built on top of the `qpandalite.algorithmics` component library.

| Example | Description | Key Components |
|---------|-------------|-----------------|
| [Grover Search](algorithms/grover.md) | Unstructured search with quadratic speedup | `circuit_builder`, `measurement.pauli_expectation` |
| [Quantum Phase Estimation](algorithms/qpe.md) | Eigenvalue phase estimation | `circuit_builder`, `measurement.basis_rotation_measurement` |

## Quick Start

All examples are standalone Python scripts. Run them directly:

```bash
# Grover search
python examples/algorithms/grover.py --n-qubits 3 --marked-state 5

# Quantum Phase Estimation
python examples/algorithms/qpe.py --n-precision 4 --unitary t
```

## Coming Soon

- [ ] `hadamard_superposition.py` — Hadamard superposition tutorial
- [ ] `shadow_tomography.py` — Classical Shadow tomography demo
- [ ] `vqe.py` — Variational Quantum Eigensolver
- [ ] `qaoa.py` — Quantum Approximate Optimization Algorithm (QAOA)
- [ ] `qft.py` — Quantum Fourier Transform and applications
- [ ] `deutsch-jozsa.py` — Deutsch-Jozsa algorithm
- [ ] `state_tomography.py` — Full density-matrix tomography demo
- [ ] `rotation_prepare.py` — Arbitrary state preparation via rotation
- [ ] `thermal_state.py` — Thermal/Boltzmann state preparation
- [ ] `dicke_state.py` — Dicke symmetric states

## Architecture

These examples demonstrate how to compose `qpandalite` components:

```
qpandalite/
├── algorithmics/
│   ├── measurement/         ← measurement strategy components
│   │   ├── pauli_expectation.py
│   │   ├── state_tomography.py
│   │   ├── classical_shadow.py
│   │   └── basis_rotation.py
│   └── circuits/           ← (planned) circuit primitives
│   └── ansatz/             ← (planned) parameterized templates
│   └── state_preparation/   ← (planned) state preparation
```

Examples live at the top level `examples/` to keep the package and
demonstrations clearly separated.
