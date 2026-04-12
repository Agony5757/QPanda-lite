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
|---------|-------------|----------------|
| [Grover Search](algorithms/grover.md) | Unstructured search with quadratic speedup | `circuit_builder`, `measurement.pauli_expectation` |
| [Quantum Phase Estimation](algorithms/qpe.md) | Eigenvalue phase estimation | `circuit_builder`, `measurement.basis_rotation_measurement` |
| [VQE](algorithms/vqe.md) | Variational Quantum Eigensolver for H₂ | `ansatz.uccsd`, `measurement` |
| [QAOA](algorithms/qaoa.md) | Quantum Approximate Optimization for MaxCut | `ansatz.qaoa_ansatz` |

### State Preparation

> Demonstrations of the `state_preparation` module.

| Example | Description | Key Components |
|---------|-------------|----------------|
| [Hadamard Superposition](state_preparation/hadamard_superposition.md) | Uniform superposition via Hadamard gates | `state_preparation.hadamard_superposition` |
| [Rotation Prepare](state_preparation/rotation_prepare.md) | Arbitrary state preparation via SBM decomposition | `state_preparation.rotation_prepare` |

### Measurement

> Demonstrations of the `measurement` module.

| Example | Description | Key Components |
|---------|-------------|----------------|
| [Classical Shadow](measurement/shadow_tomography.md) | Efficient state characterisation via shadow snapshots | `measurement.classical_shadow`, `measurement.shadow_expectation` |
| [State Tomography](measurement/state_tomography.md) | Full density-matrix reconstruction | `measurement.state_tomography`, `measurement.tomography_summary` |

## Quick Start

All examples are standalone Python scripts. Run them directly from the
**repository root**:

```bash
# From the repo root directory
cd QPanda-lite

# Grover search
python examples/algorithms/grover.py --n-qubits 3 --marked-state 5

# VQE for H₂
python examples/algorithms/vqe.py --maxiter 100

# QAOA MaxCut
python examples/algorithms/qaoa.py -p 2 --maxiter 80

# State preparation
python examples/state_preparation/rotation_prepare.py --state bell

# Measurement
python examples/measurement/shadow_tomography.py --n-shadow 100
```

> **Note on `sys.path.insert`**: Example scripts include a
> `sys.path.insert(0, ...)` line at the top so they can be executed
> directly (e.g. `python examples/algorithms/vqe.py`) without installing
> `qpandalite` as a package.  If you have installed qpandalite via
> `pip install -e .`, this line is harmless and can be ignored.

## Architecture

These examples demonstrate how to compose `qpandalite` components:

```
qpandalite/
├── algorithmics/
│   ├── ansatz/              ← parameterised circuit templates
│   │   ├── hea.py           ← Hardware-Efficient Ansatz
│   │   ├── qaoa_ansatz.py   ← QAOA ansatz
│   │   └── uccsd.py         ← UCCSD ansatz
│   ├── measurement/         ← measurement strategy components
│   │   ├── pauli_expectation.py
│   │   ├── state_tomography.py
│   │   ├── classical_shadow.py
│   │   └── basis_rotation.py
│   └── state_preparation/   ← state preparation methods
│       ├── basis_state.py
│       ├── hadamard_superposition.py
│       ├── rotation_prepare.py
│       ├── thermal_state.py
│       └── dicke_state.py
```

Examples live at the top level `examples/` to keep the package and
demonstrations clearly separated.
