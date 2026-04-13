"""Tests for entangled state preparation circuits: GHZ, W, Cluster."""

import math

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import ghz_state, w_state, cluster_state


def _simulate_probs(circuit, n_qubits):
    """Helper: run statevector simulation and return probability array."""
    from qpandalite.simulator.qasm_simulator import QASM_Simulator
    sim = QASM_Simulator(backend_type='statevector', n_qubits=n_qubits)
    result = sim._simulate_qasm(circuit.qasm)
    return result['prob']


class TestGHZState:
    """Tests for ghz_state function."""

    def test_ghz_3qubit(self):
        """GHZ(3) → p(000)≈0.5, p(111)≈0.5, other states≈0."""
        c = Circuit(3)
        ghz_state(c)
        probs = _simulate_probs(c, 3)

        assert np.isclose(probs[0], 0.5, atol=0.05), f"p(000)={probs[0]}"
        assert np.isclose(probs[7], 0.5, atol=0.05), f"p(111)={probs[7]}"
        for i in range(1, 7):
            assert probs[i] < 0.01, f"p({i:03b})={probs[i]} should be ≈0"

    def test_ghz_2qubit_bell_state(self):
        """2-qubit GHZ = Bell state: p(00)≈0.5, p(11)≈0.5."""
        c = Circuit(2)
        ghz_state(c)
        probs = _simulate_probs(c, 2)

        assert np.isclose(probs[0], 0.5, atol=0.05)
        assert np.isclose(probs[3], 0.5, atol=0.05)
        assert probs[1] < 0.01
        assert probs[2] < 0.01

    def test_ghz_single_qubit_raises(self):
        """GHZ with 1 qubit should raise ValueError."""
        c = Circuit(1)
        with pytest.raises(ValueError, match="at least 2"):
            ghz_state(c)

    def test_ghz_custom_qubits(self):
        """GHZ on custom qubit indices should work."""
        c = Circuit(4)
        ghz_state(c, qubits=[1, 2, 3])
        probs = _simulate_probs(c, 4)
        # |0000⟩ and |1110⟩ in the 4-qubit space
        assert probs[0] > 0.1  # |0000⟩
        assert probs[14] > 0.1  # |1110⟩


class TestWState:
    """Tests for w_state function."""

    def test_w_3qubit(self):
        """W(3) → p(100)≈1/3, p(010)≈1/3, p(001)≈1/3."""
        c = Circuit(3)
        w_state(c)
        probs = _simulate_probs(c, 3)

        expected = 1.0 / 3.0
        assert np.isclose(probs[4], expected, atol=0.05), f"p(100)={probs[4]}"
        assert np.isclose(probs[2], expected, atol=0.05), f"p(010)={probs[2]}"
        assert np.isclose(probs[1], expected, atol=0.05), f"p(001)={probs[1]}"
        assert probs[0] < 0.01  # |000⟩
        assert probs[7] < 0.01  # |111⟩

    def test_w_2qubit(self):
        """2-qubit W = (|10⟩+|01⟩)/√2: p≈0.5 each."""
        c = Circuit(2)
        w_state(c)
        probs = _simulate_probs(c, 2)

        assert np.isclose(probs[2], 0.5, atol=0.05), f"p(10)={probs[2]}"
        assert np.isclose(probs[1], 0.5, atol=0.05), f"p(01)={probs[1]}"
        assert probs[0] < 0.01
        assert probs[3] < 0.01

    def test_w_single_qubit_raises(self):
        """W with 1 qubit should raise ValueError."""
        c = Circuit(1)
        with pytest.raises(ValueError, match="at least 2"):
            w_state(c)


class TestClusterState:
    """Tests for cluster_state function."""

    def test_cluster_linear_chain(self):
        """Linear chain cluster state should produce non-zero probabilities."""
        c = Circuit(4)
        cluster_state(c)
        probs = _simulate_probs(c, 4)

        # All basis states should have non-zero probability (superposition)
        nonzero = sum(1 for p in probs if p > 1e-6)
        assert nonzero > 1, "Cluster state should be entangled"

        # Probabilities should sum to 1
        assert np.isclose(sum(probs), 1.0, atol=1e-6)

    def test_cluster_custom_edges(self):
        """Custom edges (square) should produce a valid state."""
        c = Circuit(4)
        cluster_state(c, edges=[(0, 1), (1, 2), (2, 3), (3, 0)])
        probs = _simulate_probs(c, 4)

        assert np.isclose(sum(probs), 1.0, atol=1e-6)
        nonzero = sum(1 for p in probs if p > 1e-6)
        assert nonzero > 1

    def test_cluster_single_qubit(self):
        """Single qubit cluster = just Hadamard → p(0)=p(1)=0.5."""
        c = Circuit(1)
        cluster_state(c)
        probs = _simulate_probs(c, 1)

        assert np.isclose(probs[0], 0.5, atol=0.01)
        assert np.isclose(probs[1], 0.5, atol=0.01)

    def test_cluster_edge_out_of_range_raises(self):
        """Edge index out of range should raise ValueError."""
        c = Circuit(3)
        with pytest.raises(ValueError, match="out of range"):
            cluster_state(c, edges=[(0, 5)])
