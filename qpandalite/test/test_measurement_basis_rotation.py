"""Additional tests for basis_rotation_measurement covering defaults,
3-qubit, all-I basis, edge cases, and multi-basis."""

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.measurement import basis_rotation_measurement


class TestDefaultBehavior:
    """Default qubits=None and basis=None behavior."""

    def test_default_basis_is_z(self):
        """With basis=None, all qubits are measured in Z basis.

        |+⟩|0⟩ in Z basis: P(00)=0.5, P(10)=0.5.
        """
        c = Circuit()
        c.h(0)
        c.measure(0, 1)
        result = basis_rotation_measurement(c, basis=None, shots=None)
        assert np.isclose(result["00"], 0.5)
        assert np.isclose(result["10"], 0.5)

    def test_default_qubits_all(self):
        """With qubits=None, all circuit qubits are measured."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        result = basis_rotation_measurement(c, basis="ZZ", shots=None)
        assert np.isclose(result["00"], 0.5)
        assert np.isclose(result["11"], 0.5)


class TestAllIdentityBasis:
    """All-I basis should behave like Z basis (no rotation)."""

    def test_all_i_on_plus(self):
        """Basis 'I' on |+⟩ should give same as Z basis: P(0)=0.5, P(1)=0.5."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="I", shots=None)
        assert np.isclose(result["0"], 0.5)
        assert np.isclose(result["1"], 0.5)


class TestThreeQubitBasisRotation:
    """3-qubit basis rotation tests."""

    def test_xxz_on_ghz3(self):
        """3-qubit GHZ measured in XXZ basis.

        GHZ = (|000⟩+|111⟩)/√2.
        X basis on qubits 0,1 and Z on qubit 2:
        After H on q0,q1: |000⟩→|+00⟩→(0+1+0+0+0+0+0+0)/2 → complex.
        Actually, XXZ measurement: apply H on q0,q1, no rotation on q2.
        Probability of outcome 000 = |⟨000|H⊗H⊗I|ψ⟩|² where |ψ⟩ = (|000⟩+|111⟩)/√2.
        """
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.cx(0, 2)
        c.measure(0, 1, 2)
        result = basis_rotation_measurement(c, basis="XXZ", shots=None)
        # Just verify it's a valid distribution
        assert np.isclose(sum(result.values()), 1.0)

    def test_zyx_on_computational(self):
        """|000⟩ measured in ZYX basis should give a valid distribution."""
        c = Circuit()
        c.measure(0, 1, 2)
        result = basis_rotation_measurement(c, basis="ZYX", shots=None)
        assert np.isclose(sum(result.values()), 1.0)

    def test_xxx_on_ghz3(self):
        """GHZ measured in XXX basis: |+++,--+⟩ or similar structure."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.cx(0, 2)
        c.measure(0, 1, 2)
        result = basis_rotation_measurement(c, basis="XXX", shots=None)
        assert np.isclose(sum(result.values()), 1.0)


class TestSingleQubitMultiBasis:
    """Single qubit measured in different bases."""

    def test_z_basis_on_one(self):
        """Z basis on |1⟩: P(1)=1."""
        c = Circuit()
        c.x(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="Z", shots=None)
        assert np.isclose(result["1"], 1.0)

    def test_y_basis_on_iminus(self):
        """Y basis on |i−⟩ = (|0⟩−i|1⟩)/√2: should be P(1)=1.

        |i−⟩ = X H S |0⟩ (up to global phase).
        After Sdg·H rotation (Y→Z), |i−⟩ maps to |1⟩ in Z basis.
        """
        c = Circuit()
        c.x(0)
        c.h(0)
        c.s(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="Y", shots=None)
        assert np.isclose(result["1"], 1.0, atol=1e-6)


class TestBasisRotationEdgeCases:
    """Edge cases for basis_rotation_measurement."""

    def test_shots_zero_raises(self):
        """shots=0 should raise ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError):
            basis_rotation_measurement(c, basis="Z", shots=0)

    def test_shots_negative_raises(self):
        """shots=-1 should raise ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError):
            basis_rotation_measurement(c, basis="Z", shots=-1)

    def test_invalid_basis_char_raises(self):
        """Invalid basis character should raise ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError):
            basis_rotation_measurement(c, basis="A", shots=None)

    def test_basis_length_mismatch_raises(self):
        """Basis string length ≠ n_qubits should raise ValueError."""
        c = Circuit()
        c.measure(0, 1)
        with pytest.raises(ValueError):
            basis_rotation_measurement(c, basis="Z", shots=None)

    def test_shots_mode_sum(self):
        """Shots mode total count should equal shots parameter."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        result = basis_rotation_measurement(c, basis="ZZ", shots=500)
        assert sum(result.values()) == 500

    def test_list_basis(self):
        """Basis as list should work."""
        c = Circuit()
        c.h(0)
        c.measure(0, 1)
        result = basis_rotation_measurement(c, basis=["X", "Z"], shots=None)
        assert np.isclose(result["00"], 0.5)
        assert np.isclose(result["10"], 0.5)
