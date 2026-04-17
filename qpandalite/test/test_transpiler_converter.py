"""Tests for transpiler converter module."""
from qpandalite.test._utils import qpandalite_test, NotMatchError
from qpandalite.transpiler.converter import convert_oir_to_qasm, convert_qasm_to_oir
from qpandalite.transpiler._utils import IRConversionFailedException
from qpandalite.circuit_builder import Circuit


@qpandalite_test('Test Transpiler Converter: OIR to QASM')
def run_test_oir_to_qasm():
    """Test OriginIR to QASM conversion."""
    # Test simple circuit
    circ = Circuit(2)
    circ.h(0)
    circ.cx(0, 1)
    originir_str = circ.originir

    qasm_str = convert_oir_to_qasm(originir_str)

    assert 'OPENQASM 2.0' in qasm_str
    assert 'qreg' in qasm_str
    print(f"Converted QASM:\n{qasm_str}")

    # Test circuit with parameters
    circ2 = Circuit(1)
    circ2.rx(0, 1.57)
    originir_str2 = circ2.originir

    qasm_str2 = convert_oir_to_qasm(originir_str2)
    assert 'rx' in qasm_str2.lower()
    print(f"Parameterized QASM:\n{qasm_str2}")


@qpandalite_test('Test Transpiler Converter: QASM to OIR')
def run_test_qasm_to_oir():
    """Test QASM to OriginIR conversion."""
    qasm_str = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
measure q -> c;
"""
    originir_str = convert_qasm_to_oir(qasm_str)

    assert 'QINIT' in originir_str
    assert 'CREG' in originir_str
    print(f"Converted OriginIR:\n{originir_str}")


@qpandalite_test('Test Transpiler Converter: Roundtrip')
def run_test_roundtrip():
    """Test roundtrip conversion OIR -> QASM -> OIR."""
    circ = Circuit(3)
    circ.h(0)
    circ.cx(0, 1)
    circ.cx(1, 2)
    circ.ry(1, 0.5)

    original_oir = circ.originir
    qasm_str = convert_oir_to_qasm(original_oir)
    converted_oir = convert_qasm_to_oir(qasm_str)

    print(f"Original OIR:\n{original_oir}")
    print(f"Converted OIR:\n{converted_oir}")


@qpandalite_test('Test Transpiler Converter: Error Handling')
def run_test_error_handling():
    """Test error handling for invalid inputs."""
    # Test invalid OriginIR
    try:
        convert_oir_to_qasm("INVALID ORIGINIR SYNTAX")
    except IRConversionFailedException as e:
        print(f"Caught expected error for invalid OriginIR: {e}")

    # Test invalid QASM
    try:
        convert_qasm_to_oir("INVALID QASM SYNTAX")
    except IRConversionFailedException as e:
        print(f"Caught expected error for invalid QASM: {e}")


if __name__ == '__main__':
    run_test_oir_to_qasm()
    run_test_qasm_to_oir()
    run_test_roundtrip()
    run_test_error_handling()
