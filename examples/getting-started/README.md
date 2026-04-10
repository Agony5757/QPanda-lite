# Getting Started with QPanda-Lite

Step-by-step tutorials for the core QPanda-Lite workflows.

## Contents

| File | Description |
|------|-------------|
| [1_circuit_remap.py](1_circuit_remap.py) | Build a circuit and remap qubits for real hardware |
| [2_dummy_server.py](2_dummy_server.py) | Submit tasks to the local dummy simulator |
| [3_result_postprocess.py](3_result_postprocess.py) | Convert and analyze results with result adapters |

## Quick Start

```bash
# 1. Build and remap a circuit
python examples/getting-started/1_circuit_remap.py

# 2. Submit to dummy simulator
python examples/getting-started/2_dummy_server.py

# 3. Post-process results
python examples/getting-started/3_result_postprocess.py
```

## Topics Covered

- **Circuit building** — using `qpandalite.Circuit` to construct quantum programs
- **Qubit remapping** — mapping logical qubits to physical device topology
- **Dummy backend** — testing locally without consuming cloud resources
- **Result adaptation** — converting results between key-value, list, probability, and shots styles
