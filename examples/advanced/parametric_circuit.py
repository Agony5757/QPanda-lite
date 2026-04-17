#!/usr/bin/env python
"""Parametric circuit example with named registers and named circuits.

Demonstrates:
  * Using QReg/Qubit for named quantum registers
  * Creating symbolic Parameters for variational circuits
  * Defining reusable subroutines with @circuit_def
  * Exporting to OriginIR DEF blocks

Usage:
    python parametric_circuit.py

This example builds a variational circuit similar to those used in VQE/QAOA,
showing how to organize complex circuits with named registers and subroutines.
"""

import math
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qpandalite.circuit_builder import Circuit
from qpandalite.circuit_builder.parameter import Parameter, Parameters
from qpandalite.circuit_builder.named_circuit import circuit_def


def demo_named_registers():
    """Demonstrate named quantum registers."""
    print("=" * 60)
    print("Named Quantum Registers (QReg/Qubit/QRegSlice)")
    print("=" * 60)

    # Create circuit with named registers
    c = Circuit(qregs={"data": 4, "ancilla": 1})

    # Access registers by name
    data = c.get_qreg("data")
    ancilla = c.get_qreg("ancilla")

    print(f"\nCircuit with registers: data (4 qubits), ancilla (1 qubit)")
    print(f"Total qubits: {c.qubit_num}")

    # Use named qubits in gates
    c.h(data[0])
    c.cnot(data[0], data[1])
    c.cnot(data[1], data[2])
    c.cnot(data[2], data[3])
    c.cnot(data[3], ancilla[0])

    print(f"\nCreated entanglement chain: data[0] -> data[3] -> ancilla[0]")

    # Slicing support
    print(f"\nSlicing: data[1:3] = {[q.name for q in data[1:3]]}")
    print(f"Negative index: data[-1] = {data[-1].name}")

    # Measure
    for i in range(4):
        c.measure(data[i])
    c.measure(ancilla[0])

    print("\nOriginIR output:")
    print(c.originir)
    return c


def demo_parameters():
    """Demonstrate symbolic parameters."""
    print("\n" + "=" * 60)
    print("Symbolic Parameters (Parameter/Parameters)")
    print("=" * 60)

    # Single parameter
    theta = Parameter("theta")
    phi = Parameter("phi")

    print(f"\nCreated parameters: {theta}, {phi}")

    # Parameter expressions (using sympy internally)
    expr = theta * 2 + phi
    print(f"Expression: theta * 2 + phi = {expr}")

    # Bind values
    theta.bind(math.pi / 4)
    phi.bind(math.pi / 8)

    print(f"\nBound values: theta = {theta.evaluate():.4f}, phi = {phi.evaluate():.4f}")

    # Parameter array
    angles = Parameters("alpha", size=4)
    angles.bind([0.1, 0.2, 0.3, 0.4])

    print(f"\nParameter array: {angles}")
    print(f"Names: {angles.names}")
    print(f"Values: {[angles[i].evaluate() for i in range(4)]}")

    # Use in circuit
    c = Circuit(4)
    for i in range(4):
        c.ry(i, angles[i].evaluate())

    print(f"\nBuilt circuit with {len(c.opcode_list)} parametric RY gates")
    return c, angles


def demo_named_circuit():
    """Demonstrate @circuit_def for reusable subroutines."""
    print("\n" + "=" * 60)
    print("Named Circuits (@circuit_def)")
    print("=" * 60)

    # Define a Bell pair preparation subroutine
    @circuit_def(name="bell_pair", qregs={"q": 2})
    def bell_pair(circ, q):
        """Prepare a Bell pair on two qubits."""
        circ.h(q[0])
        circ.cnot(q[0], q[1])
        return circ

    print(f"\nDefined subroutine: {bell_pair}")
    print(f"  Qubits: {bell_pair.num_qubits}")
    print(f"  Parameters: {bell_pair.num_parameters}")

    # Define a parameterized rotation subroutine
    @circuit_def(name="rot_layer", qregs={"q": 4}, params=["theta"])
    def rot_layer(circ, q, theta):
        """Apply RX rotation to all qubits."""
        for i in range(4):
            circ.rx(q[i], theta)
        return circ

    print(f"\nDefined subroutine: {rot_layer}")
    print(f"  Qubits: {rot_layer.num_qubits}")
    print(f"  Parameters: {rot_layer.num_parameters}")

    # Use in a parent circuit
    c = Circuit(qregs={"data": 4})
    data = c.get_qreg("data")

    # Apply subroutines
    bell_pair(c, qreg_mapping={"q": [data[0], data[1]]})
    bell_pair(c, qreg_mapping={"q": [data[2], data[3]]})
    rot_layer(c, qreg_mapping={"q": [data[0], data[1], data[2], data[3]]}, param_values={"theta": 0.5})

    print(f"\nBuilt parent circuit with {len(c.opcode_list)} operations")

    # Export as DEF block
    print("\nDEF block export:")
    print(bell_pair.to_originir_def())

    return c


def demo_variational_circuit():
    """Build a complete variational circuit combining all features."""
    print("\n" + "=" * 60)
    print("Complete Variational Circuit Example")
    print("=" * 60)

    # Define reusable components
    @circuit_def(name="entangle", qregs={"q": 2})
    def entangle(circ, q):
        """Create entanglement between two qubits."""
        circ.h(q[0])
        circ.cnot(q[0], q[1])
        return circ

    @circuit_def(name="rot_x", qregs={"q": 1}, params=["angle"])
    def rot_x(circ, q, angle):
        """Apply parameterized X rotation."""
        circ.rx(q[0], angle)
        return circ

    @circuit_def(name="rot_z", qregs={"q": 1}, params=["angle"])
    def rot_z(circ, q, angle):
        """Apply parameterized Z rotation."""
        circ.rz(q[0], angle)
        return circ

    # Create parameter array for the variational layer
    params = Parameters("theta", size=6)
    params.bind([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])

    # Build the circuit
    c = Circuit(qregs={"q": 4})
    q = c.get_qreg("q")

    # Initial entanglement
    entangle(c, qreg_mapping={"q": [q[0], q[1]]})
    entangle(c, qreg_mapping={"q": [q[2], q[3]]})
    entangle(c, qreg_mapping={"q": [q[1], q[2]]})

    # Variational layer
    for i in range(4):
        rot_x(c, qreg_mapping={"q": [q[i]]}, param_values={"angle": params[i].evaluate()})
        rot_z(c, qreg_mapping={"q": [q[i]]}, param_values={"angle": params[i + 2].evaluate()})

    # Final entanglement
    entangle(c, qreg_mapping={"q": [q[0], q[3]]})

    # Measure all qubits
    c.measure(*range(4))

    print(f"\nCircuit statistics:")
    print(f"  Qubits: {c.qubit_num}")
    print(f"  Gates: {len(c.opcode_list)}")
    print(f"  Measurements: {len(c.measure_list)}")

    print("\nOriginIR output:")
    print(c.originir)

    return c


def main():
    """Run all demonstrations."""
    print("PR #179 Feature Demonstration")
    print("=" * 60)

    demo_named_registers()
    demo_parameters()
    demo_named_circuit()
    demo_variational_circuit()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
