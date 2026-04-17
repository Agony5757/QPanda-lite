"""Unit tests for the dicke_state circuit component."""

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import dicke_state_circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator


def _simulate(circuit, n):
    """Run statevector simulation and return probability array."""
    sim = QASM_Simulator(backend_type='statevector', n_qubits=n)
    result = sim.simulate_statevector(circuit.qasm)
    return np.abs(result) ** 2


class TestDickeStateCircuit:
    def test_dicke_3_1(self):
        """D(3,1) should give equal probability for |100⟩, |010⟩, |001⟩."""
        c = Circuit()
        dicke_state_circuit(c, k=1, qubits=[0, 1, 2])
        probs = _simulate(c, 3)
        # |100⟩ = index 4, |010⟩ = index 2, |001⟩ = index 1
        assert np.isclose(probs[4], 1.0 / 3, atol=0.01)
        assert np.isclose(probs[2], 1.0 / 3, atol=0.01)
        assert np.isclose(probs[1], 1.0 / 3, atol=0.01)
        # All others should be ~0
        for i in range(8):
            if i not in (1, 2, 4):
                assert np.isclose(probs[i], 0.0, atol=0.01)

    def test_dicke_n_0(self):
        """D(n,0) should be |00...0⟩."""
        c = Circuit()
        with pytest.raises(ValueError):
            dicke_state_circuit(c, k=0, qubits=[0, 1, 2])

    def test_dicke_n_n(self):
        """D(n,n) should be |11...1⟩."""
        c = Circuit()
        dicke_state_circuit(c, k=3, qubits=[0, 1, 2])
        probs = _simulate(c, 3)
        assert np.isclose(probs[7], 1.0, atol=0.01)

    def test_dicke_4_2(self):
        """D(4,2) should have C(4,2)=6 equal-weight basis states."""
        c = Circuit()
        dicke_state_circuit(c, k=2, qubits=[0, 1, 2, 3])
        probs = _simulate(c, 4)
        expected_weight = 1.0 / 6  # 1/C(4,2)
        # States with exactly 2 ones
        weight_sum = 0.0
        for i in range(16):
            if bin(i).count('1') == 2:
                assert np.isclose(probs[i], expected_weight, atol=0.02)
                weight_sum += probs[i]
        assert np.isclose(weight_sum, 1.0, atol=0.02)

    def test_dicke_k_exceeds_n_raises(self):
        """k > n should raise ValueError."""
        c = Circuit()
        with pytest.raises(ValueError):
            dicke_state_circuit(c, k=4, qubits=[0, 1, 2])

    def test_dicke_k_negative_raises(self):
        """Negative k should raise ValueError."""
        c = Circuit()
        with pytest.raises(ValueError):
            dicke_state_circuit(c, k=-1, qubits=[0, 1])

    def test_dicke_2_1(self):
        """D(2,1) = (|10⟩+|01⟩)/√2."""
        c = Circuit()
        dicke_state_circuit(c, k=1, qubits=[0, 1])
        probs = _simulate(c, 2)
        assert np.isclose(probs[1], 0.5, atol=0.01)  # |01⟩
        assert np.isclose(probs[2], 0.5, atol=0.01)  # |10⟩

    def test_dicke_produces_gates(self):
        """Circuit should have non-empty opcode_list after dicke_state_circuit."""
        c = Circuit()
        dicke_state_circuit(c, k=2, qubits=[0, 1, 2, 3])
        assert len(c.opcode_list) > 0

    def test_dicke_5_3_exact(self):
        """D(5,3): uniform over C(5,3)=10 weight-3 states, zero elsewhere.

        Stronger than test_dicke_4_2: explicitly asserts that all Hamming-weight
        ≠ k amplitudes are zero, so the circuit cannot "cheat" by leaking
        probability into non-Dicke sectors.
        """
        c = Circuit()
        dicke_state_circuit(c, k=3, qubits=[0, 1, 2, 3, 4])
        probs = _simulate(c, 5)
        expected_weight = 1.0 / 10  # 1/C(5,3)
        for i in range(32):
            if bin(i).count('1') == 3:
                assert np.isclose(probs[i], expected_weight, atol=0.01)
            else:
                assert np.isclose(probs[i], 0.0, atol=0.01)

    def test_dicke_6_2_exact(self):
        """D(6,2): uniform over C(6,2)=15 weight-2 states, zero elsewhere.

        Exercises a larger n with mid-range k to catch regressions in the
        first_block cascade (n-k = 4 iterations of SCS_{l,k}).
        """
        c = Circuit()
        dicke_state_circuit(c, k=2, qubits=[0, 1, 2, 3, 4, 5])
        probs = _simulate(c, 6)
        expected_weight = 1.0 / 15  # 1/C(6,2)
        for i in range(64):
            if bin(i).count('1') == 2:
                assert np.isclose(probs[i], expected_weight, atol=0.01)
            else:
                assert np.isclose(probs[i], 0.0, atol=0.01)
