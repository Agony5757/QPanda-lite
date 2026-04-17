"""Tests for thermal state preparation circuit."""

import math

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.circuits import thermal_state_circuit


class TestThermalStateCircuit:
    """Tests for thermal_state_circuit."""

    def _simulate_1qubit(self, c):
        """Helper: simulate a 1-qubit circuit and return probabilities."""
        from qpandalite.simulator.qasm_simulator import QASM_Simulator
        sim = QASM_Simulator(backend_type="statevector", n_qubits=1)
        result = sim.simulate_statevector(c.qasm)
        return np.abs(result) ** 2

    def test_beta_zero_maximally_mixed(self):
        """beta=0 → maximally mixed state: p(0) ≈ p(1) ≈ 0.5."""
        pytest.importorskip("qpandalite.simulator.qasm_simulator")

        c = Circuit()
        thermal_state_circuit(c, beta=0.0, qubits=[0])
        probs = self._simulate_1qubit(c)

        assert np.isclose(probs[0], 0.5, atol=1e-6), f"p(0)={probs[0]}"
        assert np.isclose(probs[1], 0.5, atol=1e-6), f"p(1)={probs[1]}"

    def test_beta_large_ground_state(self):
        """beta→∞ → ground state |0⟩: p(0) ≈ 1."""
        pytest.importorskip("qpandalite.simulator.qasm_simulator")

        c = Circuit()
        thermal_state_circuit(c, beta=100.0, qubits=[0])
        probs = self._simulate_1qubit(c)

        assert np.isclose(probs[0], 1.0, atol=1e-3), f"p(0)={probs[0]}"

    def test_beta_one_intermediate(self):
        """beta=1 should give p(0) > p(1) but p(1) > 0."""
        pytest.importorskip("qpandalite.simulator.qasm_simulator")

        c = Circuit()
        thermal_state_circuit(c, beta=1.0, qubits=[0])
        probs = self._simulate_1qubit(c)

        exp_beta = math.exp(1.0)
        expected_p0 = exp_beta / (exp_beta + math.exp(-1.0))
        assert np.isclose(probs[0], expected_p0, atol=1e-6)
        assert probs[0] > probs[1]

    def test_custom_qubits(self):
        """Custom qubits parameter should apply rotation only to specified qubits."""
        c = Circuit()
        thermal_state_circuit(c, beta=1.0, qubits=[2, 3])
        # Should record qubits 2 and 3
        assert 2 in c.used_qubit_list
        assert 3 in c.used_qubit_list
        # Should have 2 RY gates (one per qubit)
        assert len(c.opcode_list) >= 2
        op_names = [op[0] for op in c.opcode_list]
        assert all(name == "RY" for name in op_names)

    def test_beta_negative_raises(self):
        """beta < 0 should raise ValueError."""
        c = Circuit()
        with pytest.raises(ValueError):
            thermal_state_circuit(c, beta=-0.1)

    def test_beta_zero_analytical(self):
        """beta=0 rotation angle: theta = 2*arccos(sqrt(0.5)) = pi/2."""
        c = Circuit()
        thermal_state_circuit(c, beta=0.0, qubits=[0])
        # Check the rotation angle is pi/2
        for op in c.opcode_list:
            if op[0] == "RY":
                params = op[3]
                angle = params if not isinstance(params, list) else params[0]
                assert np.isclose(angle, math.pi / 2, atol=1e-10)
