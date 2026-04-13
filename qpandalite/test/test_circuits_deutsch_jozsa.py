"""Tests for Deutsch-Jozsa circuit and oracle builder."""

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import deutsch_jozsa_circuit, deutsch_jozsa_oracle


class TestDeutschJozsaOracle:
    """Tests for deutsch_jozsa_oracle."""

    def test_constant_oracle_returns_circuit(self):
        """Constant oracle should return a non-empty Circuit object."""
        oracle = deutsch_jozsa_oracle(3, balanced=False)
        assert isinstance(oracle, Circuit)

    def test_balanced_oracle_has_gates(self):
        """Balanced oracle with n=3 should contain CNOT gates."""
        oracle = deutsch_jozsa_oracle(3, balanced=True)
        assert len(oracle.opcode_list) > 0
        op_names = [op[0] for op in oracle.opcode_list]
        assert all(name == "CNOT" for name in op_names)

    def test_n_qubits_less_than_1_raises(self):
        """n_qubits < 1 should raise ValueError."""
        with pytest.raises(ValueError):
            deutsch_jozsa_oracle(0)
        with pytest.raises(ValueError):
            deutsch_jozsa_oracle(-1)

    def test_1qubit_oracle(self):
        """1-qubit (simplest) Deutsch oracle should work."""
        oracle = deutsch_jozsa_oracle(1, balanced=True)
        assert len(oracle.opcode_list) == 1


class TestDeutschJozsaCircuit:
    """Tests for deutsch_jozsa_circuit."""

    def test_constant_oracle_measures_all_zero(self):
        """Constant oracle → measurement result should be all zeros."""
        pytest.importorskip("qpandalite.simulator.qasm_simulator")
        from qpandalite.simulator.qasm_simulator import QASM_Simulator

        n = 3
        oracle = deutsch_jozsa_oracle(n, balanced=False)
        c = Circuit()
        # Use explicit qubits: data qubits 0,1,2 and ancilla qubit 3
        deutsch_jozsa_circuit(c, oracle, qubits=[0, 1, 2], ancilla=3)

        sim = QASM_Simulator(backend_type="statevector", n_qubits=n + 1)
        result = sim.simulate_statevector(c.qasm)
        probs = np.abs(result) ** 2
        # |000⟩ on data qubits (ancilla in |−⟩ state)
        # States |0000⟩ (idx 0) and |0001⟩ (idx 1) for ancilla in |0⟩/|1⟩
        p_all_zero = probs[0] + probs[1]
        assert np.isclose(p_all_zero, 1.0, atol=1e-6), f"p_all_zero={p_all_zero}"

    def test_balanced_oracle_measures_non_zero(self):
        """Balanced oracle → measurement result should NOT be all zeros."""
        pytest.importorskip("qpandalite.simulator.qasm_simulator")
        from qpandalite.simulator.qasm_simulator import QASM_Simulator

        n = 3
        oracle = deutsch_jozsa_oracle(n, balanced=True)
        c = Circuit()
        deutsch_jozsa_circuit(c, oracle, qubits=[0, 1, 2], ancilla=3)

        sim = QASM_Simulator(backend_type="statevector", n_qubits=n + 1)
        result = sim.simulate_statevector(c.qasm)
        probs = np.abs(result) ** 2

        # For balanced, |000⟩ on data qubits should have probability ~0
        p_all_zero = probs[0] + probs[1]
        assert np.isclose(p_all_zero, 0.0, atol=1e-6), f"p_all_zero={p_all_zero}"

    def test_1qubit_deutsch_balanced(self):
        """1-qubit Deutsch problem with balanced oracle should give non-zero."""
        pytest.importorskip("qpandalite.simulator.qasm_simulator")
        from qpandalite.simulator.qasm_simulator import QASM_Simulator

        oracle = deutsch_jozsa_oracle(1, balanced=True)
        c = Circuit()
        deutsch_jozsa_circuit(c, oracle, qubits=[0], ancilla=1)

        sim = QASM_Simulator(backend_type="statevector", n_qubits=2)
        result = sim.simulate_statevector(c.qasm)
        probs = np.abs(result) ** 2

        # Data qubit measured → should NOT be |0⟩ for balanced
        p_data_zero = probs[0] + probs[1]
        assert np.isclose(p_data_zero, 0.0, atol=1e-6)
