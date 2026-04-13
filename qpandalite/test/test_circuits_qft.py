"""Tests for QFT circuit construction."""

import math

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import qft_circuit


class TestQFTCircuit:
    """Tests for qft_circuit."""

    def test_3qubit_qft_uniform_distribution(self):
        """3-qubit QFT on |0⟩ should produce uniform probability 1/8 for each basis state."""
        pytest.importorskip("qpandalite.simulator.qasm_simulator")
        from qpandalite.simulator.qasm_simulator import QASM_Simulator

        c = Circuit()
        qft_circuit(c, qubits=[0, 1, 2])

        sim = QASM_Simulator(backend_type="statevector", n_qubits=3)
        result = sim.simulate_statevector(c.qasm)
        probs = np.abs(result) ** 2

        expected = np.full(8, 1.0 / 8.0)
        assert np.allclose(probs, expected, atol=1e-6), f"probs={probs}"

    def test_1qubit_qft_is_hadamard(self):
        """1-qubit QFT on |0⟩ is equivalent to a single H gate."""
        pytest.importorskip("qpandalite.simulator.qasm_simulator")
        from qpandalite.simulator.qasm_simulator import QASM_Simulator

        # QFT circuit
        c_qft = Circuit()
        qft_circuit(c_qft, qubits=[0])

        # H gate circuit
        c_h = Circuit()
        c_h.h(0)

        sim = QASM_Simulator(backend_type="statevector", n_qubits=1)
        r_qft = sim.simulate_statevector(c_qft.qasm)
        r_h = sim.simulate_statevector(c_h.qasm)

        assert np.allclose(np.abs(r_qft) ** 2, np.abs(r_h) ** 2, atol=1e-6)

    def test_swaps_true_produces_gates(self):
        """With swaps=True, the circuit should contain SWAP gates for n >= 2."""
        c = Circuit()
        qft_circuit(c, qubits=[0, 1, 2], swaps=True)
        op_names = [op[0] for op in c.opcode_list]
        assert "SWAP" in op_names

    def test_swaps_false_no_swap_gates(self):
        """With swaps=False, no SWAP gates should appear."""
        c = Circuit()
        qft_circuit(c, qubits=[0, 1, 2], swaps=False)
        op_names = [op[0] for op in c.opcode_list]
        assert "SWAP" not in op_names

    def test_qft_then_iqft_identity(self):
        """QFT followed by inverse QFT should return to |0⟩."""
        pytest.importorskip("qpandalite.simulator.qasm_simulator")
        from qpandalite.simulator.qasm_simulator import QASM_Simulator

        c = Circuit()
        qft_circuit(c, qubits=[0, 1, 2], swaps=True)

        # Apply inverse QFT (dagger of QFT)
        n = 3
        qubits = [0, 1, 2]

        # Inverse swaps first
        for i in range(n // 2):
            c.swap(qubits[i], qubits[n - 1 - i])

        # Inverse controlled phases and Hadamards (reverse order)
        for j in reversed(range(n)):
            for k in reversed(range(j + 1, n)):
                angle = math.pi / (2 ** (k - j))
                c.cnot(qubits[j], qubits[k])
                c.rz(angle / 2, qubits[k])
                c.cnot(qubits[j], qubits[k])
                c.rz(-angle / 2, qubits[k])
            c.h(qubits[j])

        sim = QASM_Simulator(backend_type="statevector", n_qubits=3)
        result = sim.simulate_statevector(c.qasm)
        probs = np.abs(result) ** 2

        # Should be |000⟩
        assert np.isclose(probs[0], 1.0, atol=1e-6), f"probs[0]={probs[0]}"

    def test_default_qubits_uses_all(self):
        """When circuit has gates and qubits=None, QFT should use all used qubits."""
        c = Circuit()
        c.h(0)
        c.h(1)
        c.h(2)
        # After adding gates, qubit_num=3
        qft_circuit(c)
        # Should have gates (Hadamards + controlled phases + swaps)
        assert len(c.opcode_list) > 3

    def test_empty_qubits_raises(self):
        """Empty qubits list should raise ValueError."""
        c = Circuit()
        with pytest.raises(ValueError):
            qft_circuit(c, qubits=[])

    def test_single_qubit_no_swaps(self):
        """1-qubit QFT with swaps=True should not add SWAP (n//2=0)."""
        c = Circuit()
        qft_circuit(c, qubits=[0], swaps=True)
        op_names = [op[0] for op in c.opcode_list]
        assert "SWAP" not in op_names
