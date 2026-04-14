"""Tests for Grover oracle and diffusion operator circuits."""

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import grover_oracle, grover_diffusion


def _simulate_probs(circuit, n_qubits):
    """Helper: run statevector simulation and return probability dict."""
    from qpandalite.simulator.qasm_simulator import QASM_Simulator
    sim = QASM_Simulator(backend_type='statevector', n_qubits=n_qubits)
    result = sim.simulate_statevector(circuit.qasm)
    probs = np.abs(result) ** 2
    prob_dict = {}
    for i, p in enumerate(probs):
        if p > 1e-10:
            prob_dict[i] = p
    return prob_dict


class TestGroverOracle:
    """Tests for grover_oracle function."""

    def test_oracle_marked_state_zero(self):
        """Oracle with marked_state=0 should produce a valid circuit."""
        c = Circuit()
        c.h(0)
        c.h(1)
        c.h(2)
        anc = grover_oracle(c, marked_state=0, qubits=[0, 1, 2])
        # Circuit should have gates beyond the initial Hadamards
        assert len(c.opcode_list) > 3
        assert isinstance(anc, int)
        assert anc == 3  # max(qubits) + 1

    def test_oracle_marked_state_five(self):
        """Oracle with marked_state=5 (binary 101) should generate correctly."""
        c = Circuit()
        c.h(0)
        c.h(1)
        c.h(2)
        anc = grover_oracle(c, marked_state=5, qubits=[0, 1, 2])
        assert len(c.opcode_list) > 3
        assert anc == 3

    def test_oracle_negative_marked_state_raises(self):
        """Negative marked_state should raise ValueError."""
        c = Circuit()
        with pytest.raises(ValueError, match="non-negative"):
            grover_oracle(c, marked_state=-1)

    def test_oracle_marked_state_exceeds_qubits_raises(self):
        """marked_state exceeding qubit capacity should raise ValueError."""
        c = Circuit()
        with pytest.raises(ValueError, match="bits"):
            grover_oracle(c, marked_state=8, qubits=[0, 1, 2])

    def test_oracle_one_qubit(self):
        """1-qubit oracle should work for marked_state=0 and marked_state=1."""
        for marked in [0, 1]:
            c = Circuit()
            c.h(0)
            anc = grover_oracle(c, marked_state=marked, qubits=[0])
            assert len(c.opcode_list) > 1
            assert anc == 1


class TestGroverDiffusion:
    """Tests for grover_diffusion function."""

    def test_diffusion_nonempty(self):
        """Diffusion operator should produce a non-empty circuit."""
        c = Circuit()
        grover_diffusion(c, qubits=[0, 1, 2], ancilla=3)
        assert len(c.opcode_list) > 0

    def test_diffusion_single_qubit(self):
        """Single-qubit diffusion should work without ancilla."""
        c = Circuit()
        grover_diffusion(c, qubits=[0])
        assert len(c.opcode_list) > 0

    def test_diffusion_default_qubits(self):
        """Default qubits should be [0, 1]."""
        c = Circuit()
        grover_diffusion(c)
        assert len(c.opcode_list) > 0


class TestGroverFullSearch:
    """Integration test: full Grover search should amplify target state."""

    def test_grover_amplifies_target_3qubit(self):
        """After Grover iteration, marked state should have highest probability."""
        marked = 5  # |101⟩
        n = 3
        total_qubits = n + 1  # +1 for ancilla

        c = Circuit()
        # Uniform superposition on data qubits
        for i in range(n):
            c.h(i)

        # One Grover iteration: oracle + diffusion
        anc = grover_oracle(c, marked_state=marked, qubits=list(range(n)))
        
        print(c.originir)
        
        grover_diffusion(c, qubits=list(range(n)), ancilla=anc)
        
        print(c.originir)
        # Simulate (ignore ancilla, look at data qubits)
        prob_dict = _simulate_probs(c, total_qubits)

        # Aggregate probabilities by data qubit state (sum over ancilla)
        data_probs = {}
        for state_idx, p in prob_dict.items():
            data_state = state_idx >> 1  # remove ancilla bit (highest)
            data_probs[data_state] = data_probs.get(data_state, 0) + p

        print(prob_dict)
        print(data_probs)
        # Marked state should have the highest probability
        assert data_probs[marked] > data_probs.get(0, 0)
        assert data_probs[marked] > data_probs.get(1, 0)
        assert data_probs[marked] > data_probs.get(2, 0)
