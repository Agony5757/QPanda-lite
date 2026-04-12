"""Tests for the ansatz module."""

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.originir_simulator import OriginIR_Simulator
from qpandalite.algorithmics.ansatz import hea, qaoa_ansatz, uccsd_ansatz


def _statevector(circuit: Circuit) -> np.ndarray:
    sim = OriginIR_Simulator(backend_type='statevector', least_qubit_remapping=False)
    return sim.simulate_statevector(circuit.originir)


class TestHEA:

    def test_basic(self):
        c = hea(n_qubits=3, depth=1)
        assert c.max_qubit + 1 == 3

    def test_custom_params(self):
        params = np.zeros(2 * 4 * 2)
        c = hea(n_qubits=4, depth=2, params=params)
        assert c.max_qubit + 1 == 4

    def test_wrong_params_raises(self):
        with pytest.raises(ValueError):
            hea(n_qubits=3, depth=1, params=np.zeros(5))

    def test_produces_statevector(self):
        c = hea(n_qubits=2, depth=1, params=np.array([0.5, 0.3, 0.7, 0.1]))
        sv = _statevector(c)
        assert len(sv) == 4
        assert abs(np.linalg.norm(sv) - 1.0) < 1e-10

    def test_depth_0(self):
        params = np.array([])
        c = hea(n_qubits=2, depth=0, params=params)
        # No gates → empty circuit, skip simulation
        # Just verify it doesn't crash and returns a circuit
        assert isinstance(c, Circuit)


class TestQAOAAnsatz:

    def test_basic(self):
        H = [("Z0Z1", 1.0)]
        c = qaoa_ansatz(H, p=1, betas=np.array([0.5]), gammas=np.array([0.3]))
        assert c.max_qubit + 1 == 2

    def test_produces_statevector(self):
        H = [("Z0Z1", 1.0), ("Z1Z2", 0.5)]
        c = qaoa_ansatz(H, p=1, betas=np.array([0.5]), gammas=np.array([0.3]))
        sv = _statevector(c)
        assert abs(np.linalg.norm(sv) - 1.0) < 1e-10

    def test_wrong_betas_raises(self):
        H = [("Z0Z1", 1.0)]
        with pytest.raises(ValueError):
            qaoa_ansatz(H, p=2, betas=np.array([0.5]), gammas=np.array([0.3, 0.2]))

    def test_multi_layer(self):
        H = [("Z0Z1", 1.0)]
        c = qaoa_ansatz(H, p=3, betas=np.zeros(3), gammas=np.zeros(3))
        sv = _statevector(c)
        # With β=0, γ=0: only Hadamards applied → uniform superposition
        expected = np.ones(4, dtype=complex) / 2.0
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-8)

    def test_x_hamiltonian(self):
        H = [("X0", 1.0)]
        c = qaoa_ansatz(H, p=1, betas=np.array([0.0]), gammas=np.array([np.pi]))
        sv = _statevector(c)
        # With γ=π, exp(-iπ X) flips |+> → |->, so uniform → still uniform
        expected = np.ones(2, dtype=complex) / np.sqrt(2)
        np.testing.assert_allclose(np.abs(sv), np.abs(expected), atol=1e-8)


class TestUCCSD:

    def test_basic(self):
        c = uccsd_ansatz(n_qubits=4, n_electrons=2)
        # X(0), X(1) → max_qubit at least 1
        assert c.max_qubit + 1 >= 2

    def test_zero_params_hf(self):
        # With zero params, should be Hartree-Fock: |0011> (first 2 occupied)
        c = uccsd_ansatz(n_qubits=4, n_electrons=2, params=np.zeros(5))
        # Only X(0) and X(1) are applied
        sim = OriginIR_Simulator(backend_type='statevector', least_qubit_remapping=False)
        # Need to ensure 4 qubits — touch all
        c.x(2); c.x(2)
        c.x(3); c.x(3)
        sv = sim.simulate_statevector(c.originir)
        expected = np.zeros(16, dtype=complex)
        expected[3] = 1.0  # |0011> = q0=1,q1=1
        np.testing.assert_allclose(sv, expected, atol=1e-10)

    def test_n_electrons_exceeds_n_qubits(self):
        with pytest.raises(ValueError):
            uccsd_ansatz(n_qubits=2, n_electrons=3)

    def test_wrong_params_raises(self):
        with pytest.raises(ValueError):
            uccsd_ansatz(n_qubits=4, n_electrons=2, params=np.zeros(3))

    def test_produces_statevector(self):
        c = uccsd_ansatz(n_qubits=4, n_electrons=2, params=np.ones(5) * 0.1)
        sv = _statevector(c)
        assert abs(np.linalg.norm(sv) - 1.0) < 1e-10
