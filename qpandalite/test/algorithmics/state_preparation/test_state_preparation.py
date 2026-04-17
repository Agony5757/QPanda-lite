"""Tests for the state_preparation module."""

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.originir_simulator import OriginIR_Simulator


def _statevector(circuit: Circuit) -> np.ndarray:
    """Simulate a circuit and return its statevector (no qubit remapping)."""
    sim = OriginIR_Simulator(backend_type='statevector', least_qubit_remapping=False)
    return sim.simulate_statevector(circuit.originir)


def _ensure_n_qubits(circuit: Circuit, n: int) -> None:
    """Ensure circuit has at least n qubits by touching them."""
    for i in range(n):
        circuit.x(i)
        circuit.x(i)


# ---- basis_state ----

class TestBasisState:

    def run_test_zero_state(self):
        from qpandalite.algorithmics.state_preparation import basis_state
        c = Circuit()
        _ensure_n_qubits(c, 3)
        c2 = Circuit()
        basis_state(c2, 0, qubits=[0, 1, 2])
        _ensure_n_qubits(c2, 3)
        sv = _statevector(c2)
        expected = np.zeros(8, dtype=complex)
        expected[0] = 1.0
        np.testing.assert_allclose(sv, expected, atol=1e-10)

    def run_test_single_bit(self):
        from qpandalite.algorithmics.state_preparation import basis_state
        c = Circuit()
        basis_state(c, 1, qubits=[0])
        sv = _statevector(c)
        expected = np.array([0, 1], dtype=complex)
        np.testing.assert_allclose(sv, expected, atol=1e-10)

    def run_test_multi_qubit(self):
        from qpandalite.algorithmics.state_preparation import basis_state
        c = Circuit()
        _ensure_n_qubits(c, 3)
        c2 = Circuit()
        basis_state(c2, 5, qubits=[0, 1, 2])
        # Touch unused qubit to ensure 3-qubit allocation
        c2.x(1); c2.x(1)
        sv = _statevector(c2)
        expected = np.zeros(8, dtype=complex)
        expected[5] = 1.0
        np.testing.assert_allclose(sv, expected, atol=1e-10)

    def run_test_negative_raises(self):
        c = Circuit()
        _ensure_n_qubits(c, 1)
        from qpandalite.algorithmics.state_preparation import basis_state
        with pytest.raises(ValueError):
            basis_state(c, -1)

    def run_test_custom_qubits(self):
        from qpandalite.algorithmics.state_preparation import basis_state
        c = Circuit()
        _ensure_n_qubits(c, 4)
        c2 = Circuit()
        basis_state(c2, 3, qubits=[2, 3])
        _ensure_n_qubits(c2, 4)
        sv = _statevector(c2)
        expected = np.zeros(16, dtype=complex)
        expected[12] = 1.0
        np.testing.assert_allclose(sv, expected, atol=1e-10)


# ---- hadamard_superposition ----

class TestHadamardSuperposition:

    def run_test_single_qubit(self):
        from qpandalite.algorithmics.state_preparation import hadamard_superposition
        c = Circuit()
        hadamard_superposition(c, qubits=[0])
        sv = _statevector(c)
        expected = np.array([1, 1], dtype=complex) / np.sqrt(2)
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-10)

    def run_test_two_qubit(self):
        from qpandalite.algorithmics.state_preparation import hadamard_superposition
        c = Circuit()
        hadamard_superposition(c, qubits=[0, 1])
        sv = _statevector(c)
        expected = np.ones(4, dtype=complex) / 2.0
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-10)

    def run_test_custom_qubits(self):
        from qpandalite.algorithmics.state_preparation import hadamard_superposition
        c = Circuit()
        _ensure_n_qubits(c, 3)
        hadamard_superposition(c, qubits=[0, 2])
        sv = _statevector(c)
        expected = np.zeros(8, dtype=complex)
        for i in [0, 1, 4, 5]:
            expected[i] = 0.5
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-10)


# ---- rotation_prepare ----

class TestRotationPrepare:

    def run_test_zero_state(self):
        from qpandalite.algorithmics.state_preparation import rotation_prepare
        c = Circuit()
        target = np.array([1, 0, 0, 0], dtype=complex)
        rotation_prepare(c, target)
        sv = _statevector(c)
        expected = np.array([1, 0, 0, 0], dtype=complex)
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-8)

    def run_test_bell_state(self):
        from qpandalite.algorithmics.state_preparation import rotation_prepare
        c = Circuit()
        target = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        rotation_prepare(c, target)
        sv = _statevector(c)
        np.testing.assert_allclose(np.abs(sv), np.abs(target), atol=1e-8)

    def run_test_normalisation(self):
        from qpandalite.algorithmics.state_preparation import rotation_prepare
        c = Circuit()
        target = np.array([3, 4], dtype=complex)
        rotation_prepare(c, target)
        sv = _statevector(c)
        expected = np.array([3, 4], dtype=complex) / 5.0
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-8)

    def run_test_non_power_of_2_raises(self):
        c = Circuit()
        from qpandalite.algorithmics.state_preparation import rotation_prepare
        with pytest.raises(ValueError):
            rotation_prepare(c, np.array([1, 0, 0]))

    def run_test_zero_vector_raises(self):
        c = Circuit()
        from qpandalite.algorithmics.state_preparation import rotation_prepare
        with pytest.raises(ValueError):
            rotation_prepare(c, np.array([0, 0]))


# ---- thermal_state ----

class TestThermalState:

    def run_test_zero_beta(self):
        from qpandalite.algorithmics.state_preparation import thermal_state
        c = Circuit()
        thermal_state(c, beta=0.0, qubits=[0])
        sv = _statevector(c)
        expected = np.array([1, 1], dtype=complex) / np.sqrt(2)
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-10)

    def run_test_large_beta(self):
        from qpandalite.algorithmics.state_preparation import thermal_state
        c = Circuit()
        _ensure_n_qubits(c, 1)
        c2 = Circuit()
        thermal_state(c2, beta=100.0, qubits=[0])
        _ensure_n_qubits(c2, 1)
        sv = _statevector(c2)
        expected = np.array([1, 0], dtype=complex)
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-8)

    def run_test_negative_beta_raises(self):
        c = Circuit()
        _ensure_n_qubits(c, 1)
        from qpandalite.algorithmics.state_preparation import thermal_state
        with pytest.raises(ValueError):
            thermal_state(c, beta=-1.0)

    def run_test_custom_hamiltonian(self):
        from qpandalite.algorithmics.state_preparation import thermal_state
        c = Circuit()
        H = np.array([[0, 1], [1, 0]], dtype=complex)
        thermal_state(c, beta=100.0, hamiltonian=H, qubits=[0])
        sv = _statevector(c)
        expected = np.array([1, -1], dtype=complex) / np.sqrt(2)
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-8)


# ---- dicke_state ----

class TestDickeState:

    def run_test_k0(self):
        from qpandalite.algorithmics.state_preparation import dicke_state
        c = Circuit()
        _ensure_n_qubits(c, 3)
        c2 = Circuit()
        _ensure_n_qubits(c2, 3)
        dicke_state(c2, qubits=[0, 1, 2], k=0)
        sv = _statevector(c2)
        expected = np.zeros(8, dtype=complex)
        expected[0] = 1.0
        np.testing.assert_allclose(sv, expected, atol=1e-10)

    def run_test_kn(self):
        from qpandalite.algorithmics.state_preparation import dicke_state
        c = Circuit()
        dicke_state(c, qubits=[0, 1, 2], k=3)
        sv = _statevector(c)
        expected = np.zeros(8, dtype=complex)
        expected[7] = 1.0
        np.testing.assert_allclose(sv, expected, atol=1e-10)

    def run_test_d31(self):
        from qpandalite.algorithmics.state_preparation import dicke_state
        c = Circuit()
        dicke_state(c, qubits=[0, 1, 2], k=1)
        sv = _statevector(c)
        expected = np.zeros(8, dtype=complex)
        expected[1] = 1.0 / np.sqrt(3)
        expected[2] = 1.0 / np.sqrt(3)
        expected[4] = 1.0 / np.sqrt(3)
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-8)

    def run_test_d42(self):
        from qpandalite.algorithmics.state_preparation import dicke_state
        c = Circuit()
        dicke_state(c, qubits=[0, 1, 2, 3], k=2)
        sv = _statevector(c)
        amp = 1.0 / np.sqrt(6)
        expected = np.zeros(16, dtype=complex)
        for i in range(16):
            if bin(i).count('1') == 2:
                expected[i] = amp
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-8)

    def run_test_k_exceeds_n_raises(self):
        c = Circuit()
        _ensure_n_qubits(c, 2)
        from qpandalite.algorithmics.state_preparation import dicke_state
        with pytest.raises(ValueError):
            dicke_state(c, k=3)

    def run_test_negative_k_raises(self):
        c = Circuit()
        _ensure_n_qubits(c, 2)
        from qpandalite.algorithmics.state_preparation import dicke_state
        with pytest.raises(ValueError):
            dicke_state(c, k=-1)
