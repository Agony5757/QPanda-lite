"""Tests for transpiler qiskit_transpiler module."""
import pytest

from qpandalite.test._utils import qpandalite_test, NotMatchError


@pytest.fixture(scope="module")
def qiskit_available():
    """Check if qiskit is available."""
    try:
        pytest.importorskip("qiskit")
        return True
    except pytest.skip.Exception:
        return False


@qpandalite_test('Test Transpiler Qiskit: transpile_qasm')
def run_test_transpile_qasm():
    """Test QASM transpilation."""
    pytest.importorskip("qiskit")
    from qpandalite.transpiler.qiskit_transpiler import transpile_qasm
    from qpandalite.transpiler._utils import CompilationFailedException

    qasm_str = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
cx q[0], q[1];
rz(pi/4) q[1];
cx q[1], q[2];
"""

    # Test with topology
    topology = [[0, 1], [1, 0], [1, 2], [2, 1]]
    transpiled = transpile_qasm(qasm_str, topology=topology, optimization_level=1)
    assert isinstance(transpiled, str)
    assert 'OPENQASM 2.0' in transpiled
    print(f"Transpiled QASM:\n{transpiled}")

    # Test with list of QASM strings
    qasm_list = [qasm_str, qasm_str]
    transpiled_list = transpile_qasm(qasm_list, topology=topology)
    assert len(transpiled_list) == 2
    print(f"Transpiled {len(transpiled_list)} circuits")

    # Test empty input
    empty_result = transpile_qasm([])
    assert empty_result == []

    # Test custom basis gates
    transpiled_custom = transpile_qasm(qasm_str, topology=topology, basis_gates=['cx', 'u3'])
    assert 'OPENQASM 2.0' in transpiled_custom
    print(f"Transpiled with custom basis gates")


@qpandalite_test('Test Transpiler Qiskit: transpile_originir')
def run_test_transpile_originir():
    """Test OriginIR transpilation."""
    pytest.importorskip("qiskit")
    from qpandalite.transpiler.qiskit_transpiler import transpile_originir
    from qpandalite.circuit_builder import Circuit

    circ = Circuit(2)
    circ.h(0)
    circ.cx(0, 1)
    originir_str = circ.originir

    topology = [[0, 1], [1, 0]]
    transpiled = transpile_originir(originir_str, topology=topology, optimization_level=1)
    assert isinstance(transpiled, str)
    assert 'QINIT' in transpiled
    print(f"Transpiled OriginIR:\n{transpiled}")


@qpandalite_test('Test Transpiler Qiskit: Error Handling')
def run_test_qiskit_error_handling():
    """Test error handling."""
    pytest.importorskip("qiskit")
    from qpandalite.transpiler.qiskit_transpiler import transpile_qasm
    from qpandalite.transpiler._utils import CompilationFailedException

    # Test invalid optimization level
    try:
        transpile_qasm("OPENQASM 2.0; qreg q[1];", optimization_level=5)
        raise AssertionError("Should have raised ValueError")
    except (CompilationFailedException, ValueError) as e:
        print(f"Caught expected error for invalid optimization level: {e}")

    # Test invalid QASM
    try:
        transpile_qasm("INVALID QASM")
    except CompilationFailedException as e:
        print(f"Caught expected error for invalid QASM: {e}")


@qpandalite_test('Test Transpiler Qiskit: Different Optimization Levels')
def run_test_optimization_levels():
    """Test different optimization levels."""
    pytest.importorskip("qiskit")
    from qpandalite.transpiler.qiskit_transpiler import transpile_qasm

    qasm_str = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0], q[1];
h q[0];
cx q[0], q[1];
"""

    topology = [[0, 1], [1, 0]]

    for level in [0, 1, 2, 3]:
        transpiled = transpile_qasm(qasm_str, topology=topology, optimization_level=level)
        assert 'OPENQASM 2.0' in transpiled
        print(f"Optimization level {level} OK")


if __name__ == '__main__':
    run_test_transpile_qasm()
    run_test_transpile_originir()
    run_test_qiskit_error_handling()
    run_test_optimization_levels()