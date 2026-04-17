"""
Comprehensive unit tests for qpandalite.circuit_builder.named_circuit.

Tests cover:
- @circuit_def decorator
- NamedCircuit class
- Circuit apply/invocation
- Parameter binding
- Nested circuit definitions
"""

import pytest
import math
from qpandalite.circuit_builder import Circuit, QReg
from qpandalite.circuit_builder.parameter import Parameter
from qpandalite.circuit_builder.named_circuit import circuit_def, NamedCircuit


# =============================================================================
# TestCircuitDefDecorator
# =============================================================================


class TestCircuitDefDecorator:
    """Tests for @circuit_def decorator."""

    def test_basic_decorator(self):
        """@circuit_def creates a NamedCircuit."""
        @circuit_def(name="bell_pair")
        def bell_pair(circ, q):
            circ.h(q[0])
            circ.cnot(q[0], q[1])
            return circ

        assert isinstance(bell_pair, NamedCircuit)
        assert bell_pair.name == "bell_pair"

    def test_decorator_with_qregs_dict(self):
        """@circuit_def with qregs dict."""
        @circuit_def(name="test", qregs={"q": 2})
        def test_circ(circ, q):
            circ.h(q[0])
            return circ

        assert test_circ.qregs == {"q": 2}

    def test_decorator_with_params(self):
        """@circuit_def with params list."""
        @circuit_def(name="rot", params=["theta"])
        def rot_circ(circ, q, theta):
            circ.rx(q[0], theta)
            return circ

        assert rot_circ.params == ["theta"]
        assert rot_circ.num_parameters == 1


# =============================================================================
# TestNamedCircuitSignature
# =============================================================================


class TestNamedCircuitSignature:
    """Tests for NamedCircuit signature introspection."""

    def test_num_qubits_from_qregs_dict(self):
        """num_qubits is sum of qregs sizes."""
        @circuit_def(name="test", qregs={"a": 3, "b": 2})
        def test_circ(circ, a, b):
            return circ

        assert test_circ.num_qubits == 5

    def test_num_parameters(self):
        """num_parameters matches params list length."""
        @circuit_def(name="test", params=["theta", "phi"])
        def test_circ(circ, q, theta, phi):
            return circ

        assert test_circ.num_parameters == 2


# =============================================================================
# TestNamedCircuitApply
# =============================================================================


class TestNamedCircuitApply:
    """Tests for applying NamedCircuit to a parent circuit."""

    def test_apply_basic(self):
        """Apply NamedCircuit to parent circuit."""
        @circuit_def(name="bell_pair", qregs={"q": 2})
        def bell_pair(circ, q):
            circ.h(q[0])
            circ.cnot(q[0], q[1])
            return circ

        # Parent circuit with 4 qubits
        c = Circuit(qregs={"data": 4})
        data = c.get_qreg("data")

        # Apply bell_pair to qubits 0,1
        bell_pair(c, qreg_mapping={"q": [data[0], data[1]]})

        # Check gates were added
        assert len(c.opcode_list) == 2
        assert "H q[0]" in c.originir
        assert "CNOT q[0], q[1]" in c.originir

    def test_apply_with_qreg_slice(self):
        """Apply NamedCircuit using QRegSlice mapping."""
        @circuit_def(name="bell_pair", qregs={"q": 2})
        def bell_pair(circ, q):
            circ.h(q[0])
            circ.cnot(q[0], q[1])
            return circ

        c = Circuit(qregs={"a": 4})
        qa = c.get_qreg("a")

        # Apply to qubits 1,2 using slice
        bell_pair(c, qreg_mapping={"q": qa[1:3]})

        assert "H q[1]" in c.originir
        assert "CNOT q[1], q[2]" in c.originir


# =============================================================================
# TestNamedCircuitParams
# =============================================================================


class TestNamedCircuitParams:
    """Tests for parameter binding in NamedCircuit."""

    def test_apply_with_param_dict(self):
        """Apply NamedCircuit with parameter values."""
        @circuit_def(name="rx_gate", qregs={"q": 1}, params=["theta"])
        def rx_gate(circ, q, theta):
            circ.rx(q[0], theta)
            return circ

        c = Circuit(1)
        rx_gate(c, qreg_mapping={"q": [0]}, param_values={"theta": math.pi/2})

        assert "RX q[0]" in c.originir

    def test_apply_with_param_list(self):
        """Apply NamedCircuit with parameter list."""
        @circuit_def(name="rot", qregs={"q": 1}, params=["theta", "phi"])
        def rot_circ(circ, q, theta, phi):
            circ.rx(q[0], theta)
            circ.ry(q[0], phi)
            return circ

        c = Circuit(1)
        rot_circ(c, qreg_mapping={"q": [0]}, param_values=[0.5, 1.0])

        assert len(c.opcode_list) == 2


# =============================================================================
# TestNamedCircuitStandalone
# =============================================================================


class TestNamedCircuitStandalone:
    """Tests for building standalone circuits from NamedCircuit."""

    def test_build_standalone(self):
        """Build standalone Circuit from NamedCircuit."""
        @circuit_def(name="bell_pair", qregs={"q": 2})
        def bell_pair(circ, q):
            circ.h(q[0])
            circ.cnot(q[0], q[1])
            return circ

        c = bell_pair.build_standalone()
        assert c.qubit_num == 2
        assert len(c.opcode_list) == 2

    def test_build_standalone_with_params(self):
        """Build standalone with parameter values."""
        @circuit_def(name="rot", qregs={"q": 1}, params=["theta"])
        def rot_circ(circ, q, theta):
            circ.rx(q[0], theta)
            return circ

        c = rot_circ.build_standalone(param_values={"theta": 0.5})
        assert len(c.opcode_list) == 1


# =============================================================================
# TestNestedNamedCircuits
# =============================================================================


class TestNestedNamedCircuits:
    """Tests for nested NamedCircuit calls."""

    def test_nested_circuit(self):
        """NamedCircuit can call another NamedCircuit."""
        @circuit_def(name="h_gate", qregs={"q": 1})
        def h_gate(circ, q):
            circ.h(q[0])
            return circ

        @circuit_def(name="h_on_two", qregs={"q": 2})
        def h_on_two(circ, q):
            h_gate(circ, qreg_mapping={"q": [q[0]]})
            h_gate(circ, qreg_mapping={"q": [q[1]]})
            return circ

        c = Circuit(2)
        h_on_two(c, qreg_mapping={"q": [0, 1]})

        assert len(c.opcode_list) == 2
        assert "H q[0]" in c.originir
        assert "H q[1]" in c.originir
