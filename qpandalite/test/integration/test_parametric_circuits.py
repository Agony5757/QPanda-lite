"""
Integration tests for parametric quantum circuits.

Tests the full workflow:
- Named registers (QReg/Qubit)
- Symbolic parameters (Parameter)
- Named circuits (circuit_def)
- DEF export/import
"""

import math
from qpandalite.circuit_builder import Circuit, QReg, Qubit
from qpandalite.circuit_builder.parameter import Parameter, Parameters
from qpandalite.circuit_builder.named_circuit import circuit_def, NamedCircuit


def test_full_parametric_workflow():
    """Test the complete parametric circuit workflow."""
    # Step 1: Create a circuit with named registers
    c = Circuit(qregs={"ancilla": 1, "data": 4})

    ancilla = c.get_qreg("ancilla")
    data = c.get_qreg("data")

    # Step 2: Define a reusable circuit
    @circuit_def(name="entangle_pair", qregs={"q": 2})
    def entangle_pair(circ, q):
        circ.h(q[0])
        circ.cnot(q[0], q[1])
        return circ

    # Step 3: Apply the named circuit to different qubit pairs
    entangle_pair(c, qreg_mapping={"q": [data[0], data[1]]})
    entangle_pair(c, qreg_mapping={"q": [data[2], data[3]]})

    # Step 4: Create entanglement with ancilla
    c.cnot(data[0], ancilla[0])

    # Step 5: Measure
    c.measure(ancilla[0])
    for i in range(4):
        c.measure(data[i])

    # Verify circuit structure
    assert len(c.opcode_list) == 5  # 4 from 2 entangle_pair calls + 1 cnot
    assert len(c.measure_list) == 5

    # Verify OriginIR output
    originir = c.originir
    assert "QINIT 5" in originir
    assert "H q[1]" in originir  # data[0] is qubit 1 (ancilla is qubit 0)
    assert "CNOT q[1], q[2]" in originir  # data[0], data[1]
    assert "CNOT q[3], q[4]" in originir  # data[2], data[3]
    assert "CNOT q[1], q[0]" in originir  # data[0], ancilla[0]

    return True


def test_parametric_circuit_with_binding():
    """Test parametric circuit with parameter binding."""
    # Create parameter
    theta = Parameter("theta")
    theta.bind(math.pi / 4)

    # Create circuit with parameterized rotation
    c = Circuit(2)
    c.h(0)
    c.rx(0, theta.evaluate())  # Use bound value
    c.cnot(0, 1)

    originir = c.originir
    assert "H q[0]" in originir
    assert "RX q[0]" in originir
    assert "CNOT q[0], q[1]" in originir

    return True


def test_parameters_array():
    """Test Parameters array for variational circuits."""
    # Create parameter array
    angles = Parameters("theta", size=4)
    values = [0.1, 0.2, 0.3, 0.4]
    angles.bind(values)

    # Create circuit using parameter array
    c = Circuit(4)
    for i in range(4):
        c.ry(i, angles[i].evaluate())

    assert len(c.opcode_list) == 4
    return True


def test_nested_named_circuits():
    """Test nested named circuit definitions."""
    @circuit_def(name="h_gate", qregs={"q": 1})
    def h_gate(circ, q):
        circ.h(q[0])
        return circ

    @circuit_def(name="h_all", qregs={"q": 4})
    def h_all(circ, q):
        for i in range(4):
            h_gate(circ, qreg_mapping={"q": [q[i]]})
        return circ

    c = Circuit(4)
    h_all(c, qreg_mapping={"q": [0, 1, 2, 3]})

    assert len(c.opcode_list) == 4
    assert all("H q[" in c.originir for i in range(4))
    return True


def test_def_roundtrip():
    """Test DEF block export and parse."""
    @circuit_def(name="bell", qregs={"q": 2})
    def bell(circ, q):
        circ.h(q[0])
        circ.cnot(q[0], q[1])
        return circ

    # Export to DEF
    def_str = bell.to_originir_def()

    # Parse DEF header
    from qpandalite.originir.originir_line_parser import OriginIR_LineParser

    for line in def_str.split("\n"):
        if line.startswith("DEF "):
            op, qubits, params, name = OriginIR_LineParser.handle_def(line)
            assert name == "bell"
            assert qubits == [0, 1]
            assert params == []
            break

    return True


def run_all_tests():
    """Run all integration tests."""
    tests = [
        ("Full parametric workflow", test_full_parametric_workflow),
        ("Parametric circuit with binding", test_parametric_circuit_with_binding),
        ("Parameters array", test_parameters_array),
        ("Nested named circuits", test_nested_named_circuits),
        ("DEF roundtrip", test_def_roundtrip),
    ]

    results = []
    for name, test_fn in tests:
        try:
            test_fn()
            results.append((name, "PASS"))
            print(f"✓ {name}")
        except Exception as e:
            results.append((name, f"FAIL: {e}"))
            print(f"✗ {name}: {e}")

    print()
    passed = sum(1 for _, r in results if r == "PASS")
    total = len(results)
    print(f"Integration tests: {passed}/{total} passed")

    return all(r == "PASS" for _, r in results)


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
