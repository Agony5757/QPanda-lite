"""Tests for VQD circuit components."""

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import vqd_circuit, vqd_overlap_circuit


class TestVQDCircuit:
    """Tests for vqd_circuit function."""

    def test_vqd_circuit_nonempty(self):
        """vqd_circuit should produce a non-empty circuit."""
        c = Circuit()
        gs = np.array([1, 0, 0, 0], dtype=complex)
        vqd_circuit(c, ansatz_params=[0.1, 0.2, 0.3, 0.4], prev_states=[gs], qubits=[0, 1], n_layers=2)
        assert len(c.opcode_list) > 0

    def test_vqd_different_param_counts(self):
        """Different parameter counts should match n_qubits * n_layers."""
        gs = np.array([1, 0, 0, 0], dtype=complex)

        # 2 qubits, 1 layer = 2 params
        c1 = Circuit()
        vqd_circuit(c1, [0.1, 0.2], prev_states=[gs], qubits=[0, 1], n_layers=1)
        assert len(c1.opcode_list) > 0

        # 2 qubits, 3 layers = 6 params
        c2 = Circuit()
        vqd_circuit(c2, [0.1] * 6, prev_states=[gs], qubits=[0, 1], n_layers=3)
        assert len(c2.opcode_list) > len(c1.opcode_list)

    def test_vqd_wrong_param_count_raises(self):
        """Wrong number of parameters should raise ValueError."""
        c = Circuit()
        gs = np.array([1, 0, 0, 0], dtype=complex)
        with pytest.raises(ValueError, match="Expected"):
            vqd_circuit(c, [0.1], prev_states=[gs], qubits=[0, 1], n_layers=2)

    def test_vqd_empty_prev_states_raises(self):
        """Empty prev_states should raise ValueError (use VQE instead)."""
        c = Circuit()
        with pytest.raises(ValueError, match="VQE"):
            vqd_circuit(c, [0.1, 0.2, 0.3, 0.4], prev_states=[], qubits=[0, 1], n_layers=2)


class TestVQDOverlapCircuit:
    """Tests for vqd_overlap_circuit function."""

    def test_overlap_returns_circuit(self):
        """vqd_overlap_circuit should return a Circuit object."""
        gs = np.array([1, 0, 0, 0], dtype=complex)
        circ = vqd_overlap_circuit(gs, [0.1, 0.2, 0.3, 0.4], n_layers=2)
        assert isinstance(circ, Circuit)

    def test_overlap_nonempty(self):
        """Overlap circuit should have gates."""
        gs = np.array([1, 0, 0, 0], dtype=complex)
        circ = vqd_overlap_circuit(gs, [0.1, 0.2, 0.3, 0.4], n_layers=2)
        assert len(circ.opcode_list) > 0

    def test_overlap_invalid_state_dimension_raises(self):
        """Non-power-of-2 state dimension should raise ValueError."""
        state = np.array([1, 0, 0], dtype=complex)  # length 3
        with pytest.raises(ValueError, match="power of 2"):
            vqd_overlap_circuit(state, [0.1, 0.2], n_layers=1)

    def test_overlap_custom_qubits(self):
        """Custom qubit indices should be accepted."""
        gs = np.array([1, 0, 0, 0], dtype=complex)
        circ = vqd_overlap_circuit(gs, [0.1, 0.2, 0.3, 0.4], n_layers=2, qubits=[0, 1])
        assert isinstance(circ, Circuit)
