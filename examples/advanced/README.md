# Advanced Examples

This directory contains advanced examples demonstrating QPanda-lite features.

## Examples

### `parametric_circuit.py`

Demonstrates PR #179 features:
- **Named Registers** (`QReg`/`Qubit`/`QRegSlice`): Organize qubits with semantic names
- **Parameters** (`Parameter`/`Parameters`): Symbolic parameters for variational circuits
- **Named Circuits** (`@circuit_def`): Reusable subroutines

```bash
python parametric_circuit.py
```

### `pytorch_integration.py`

Demonstrates PyTorch integration for quantum machine learning:
- **QuantumLayer**: Wrap parametric circuits as `nn.Module`
- **Parameter-Shift Gradient**: Automatic differentiation for quantum parameters
- **Batch Execution**: Parallel circuit evaluation

```bash
pip install qpandalite[pytorch]
python pytorch_integration.py
```

## Related Documentation

- [Building Quantum Circuits](../../docs/source/guide/circuit.md)
- [PyTorch Integration](../../docs/source/guide/pytorch.md)
- [OriginIR Format](../../docs/source/guide/originir.md)
