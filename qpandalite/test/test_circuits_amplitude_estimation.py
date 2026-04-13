"""Tests for Quantum Amplitude Estimation circuits."""

import math

import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import (
    amplitude_estimation_circuit,
    amplitude_estimation_result,
    grover_operator,
)


class TestAmplitudeEstimationResult:
    """Tests for amplitude_estimation_result function."""

    def test_result_all_zero_outcome(self):
        """counts={0: 100} with n_eval=3 → a ≈ sin²(0) = 0."""
        a = amplitude_estimation_result({'0': 100}, n_eval_qubits=3)
        assert math.isclose(a, 0.0, abs_tol=1e-10)

    def test_result_all_max_outcome(self):
        """counts={7: 100} with n_eval=3 → a = sin²(π·7/16) ≈ 0.8536."""
        a = amplitude_estimation_result({'111': 100}, n_eval_qubits=3)
        expected = math.sin(math.pi * 7 / 16) ** 2
        assert math.isclose(a, expected, abs_tol=1e-10)

    def test_result_integer_keys(self):
        """Integer keys should also work."""
        a = amplitude_estimation_result({0: 100}, n_eval_qubits=3)
        assert math.isclose(a, 0.0, abs_tol=1e-10)

    def test_result_half_half(self):
        """counts={4: 50, 4: 50} → m=4, a=sin²(π·4/16)=sin²(π/4)=0.5."""
        a = amplitude_estimation_result({4: 50, 0: 50}, n_eval_qubits=3)
        expected = math.sin(math.pi * 4 / 16) ** 2
        assert math.isclose(a, expected, abs_tol=1e-10)

    def test_result_empty_counts(self):
        """Empty counts should return 0."""
        a = amplitude_estimation_result({}, n_eval_qubits=3)
        assert a == 0.0


class TestGroverOperator:
    """Tests for grover_operator function."""

    def test_grover_operator_nonempty(self):
        """grover_operator should add gates to the circuit."""
        oracle = Circuit()
        oracle.z(0)

        c = Circuit()
        c.h(0)
        c.h(1)
        grover_operator(c, oracle, qubits=[0, 1])
        assert len(c.opcode_list) > 2  # more than just initial H gates

    def test_grover_operator_single_qubit(self):
        """grover_operator should work with single qubit."""
        oracle = Circuit()
        oracle.z(0)

        c = Circuit()
        c.h(0)
        grover_operator(c, oracle, qubits=[0])
        assert len(c.opcode_list) > 1

    def test_grover_operator_zero_qubits_raises(self):
        """Empty qubit list should raise ValueError."""
        oracle = Circuit()
        c = Circuit()
        with pytest.raises(ValueError, match="at least 1"):
            grover_operator(c, oracle, qubits=[])


class TestAmplitudeEstimationCircuit:
    """Tests for amplitude_estimation_circuit function."""

    def test_circuit_generation(self):
        """amplitude_estimation_circuit should produce a valid circuit."""
        oracle = Circuit()
        oracle.z(0)

        # 2 eval qubits + 2 search qubits = 4 total
        c = Circuit(4)
        amplitude_estimation_circuit(c, oracle, qubits=[2, 3], n_eval_qubits=2)
        assert len(c.opcode_list) > 0

    def test_circuit_not_enough_qubits_raises(self):
        """Too few qubits should raise ValueError."""
        oracle = Circuit()
        oracle.z(0)

        c = Circuit(1)
        with pytest.raises(ValueError, match="qubits"):
            amplitude_estimation_circuit(c, oracle, n_eval_qubits=3)

    def test_circuit_zero_eval_qubits_raises(self):
        """Zero eval qubits should raise ValueError."""
        oracle = Circuit()
        oracle.z(0)

        c = Circuit(3)
        with pytest.raises(ValueError, match="n_eval_qubits"):
            amplitude_estimation_circuit(c, oracle, n_eval_qubits=0)
