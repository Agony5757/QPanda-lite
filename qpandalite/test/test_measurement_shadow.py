"""Additional tests for classical_shadow and shadow_expectation covering
single-qubit, Y expectation, high precision, all-I, 3-qubit, and edge cases."""

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.measurement import classical_shadow, shadow_expectation


class TestSingleQubitShadow:
    """Single-qubit classical shadow tests."""

    def test_z_on_zero(self):
        """⟨Z⟩ on |0⟩ via shadow should be ≈ +1 with enough snapshots."""
        c = Circuit()
        c.measure(0)
        shadows = classical_shadow(c, shots=4096, n_shadow=100)
        est = shadow_expectation(shadows, "Z")
        assert abs(est - 1.0) < 0.15

    def test_x_on_plus(self):
        """⟨X⟩ on |+⟩ via shadow should be ≈ +1."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        shadows = classical_shadow(c, shots=4096, n_shadow=100)
        est = shadow_expectation(shadows, "X")
        assert abs(est - 1.0) < 0.15

    def test_z_on_plus_is_zero(self):
        """⟨Z⟩ on |+⟩ via shadow should be ≈ 0."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        shadows = classical_shadow(c, shots=4096, n_shadow=100)
        est = shadow_expectation(shadows, "Z")
        assert abs(est) < 0.2


class TestYExpectationShadow:
    """Y expectation via classical shadow."""

    def test_y_on_iplus(self):
        """⟨Y⟩ on |i+⟩ via shadow should be ≈ +1.

        |i+⟩ = H then S on |0⟩.
        """
        c = Circuit()
        c.h(0)
        c.s(0)
        c.measure(0)
        shadows = classical_shadow(c, shots=4096, n_shadow=200)
        est = shadow_expectation(shadows, "Y")
        assert abs(est - 1.0) < 0.15


class TestHighPrecisionShadow:
    """Higher precision with more snapshots."""

    def test_zz_bell_high_precision(self):
        """⟨ZZ⟩ on Bell with many snapshots should be closer to 1.0."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=4096, n_shadow=500)
        est = shadow_expectation(shadows, "ZZ")
        assert abs(est - 1.0) < 0.1


class TestShadowAllIdentity:
    """shadow_expectation with all-I Pauli string."""

    def test_ii_on_bell(self):
        """⟨II⟩ via shadow should be exactly 1.0 (identity)."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=512, n_shadow=16)
        est = shadow_expectation(shadows, "II")
        assert np.isclose(est, 1.0)

    def test_i_on_zero(self):
        """⟨I⟩ via shadow should be 1.0."""
        c = Circuit()
        c.measure(0)
        shadows = classical_shadow(c, shots=512, n_shadow=16)
        est = shadow_expectation(shadows, "I")
        assert np.isclose(est, 1.0)


class TestThreeQubitShadow:
    """3-qubit classical shadow tests."""

    def test_zzz_on_computational(self):
        """⟨ZZZ⟩ on |000⟩ via shadow should be ≈ +1."""
        c = Circuit()
        c.measure(0, 1, 2)
        shadows = classical_shadow(c, shots=4096, n_shadow=100)
        est = shadow_expectation(shadows, "ZZZ")
        assert abs(est - 1.0) < 0.15

    def test_shadow_count_3qubit(self):
        """Shadow count should match n_shadow for 3-qubit circuit."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.cx(0, 2)
        c.measure(0, 1, 2)
        shadows = classical_shadow(c, shots=512, n_shadow=32)
        assert len(shadows) == 32
        # Each snapshot should have 3 entries
        assert len(shadows[0].unitary_indices) == 3
        assert len(shadows[0].outcomes) == 3


class TestShadowEdgeCases:
    """Edge cases for classical_shadow and shadow_expectation."""

    def test_n_shadow_zero_raises(self):
        """n_shadow=0 should raise ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError, match="positive"):
            classical_shadow(c, shots=512, n_shadow=0)

    def test_n_shadow_negative_raises(self):
        """n_shadow=-1 should raise ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError, match="positive"):
            classical_shadow(c, shots=512, n_shadow=-1)

    def test_shots_zero_raises(self):
        """shots=0 should raise ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError, match="positive"):
            classical_shadow(c, shots=0, n_shadow=10)

    def test_invalid_pauli_in_shadow_expectation(self):
        """Invalid Pauli character in shadow_expectation should raise."""
        c = Circuit()
        c.measure(0)
        shadows = classical_shadow(c, shots=512, n_shadow=8)
        with pytest.raises(ValueError):
            shadow_expectation(shadows, "A")

    def test_snapshot_repr(self):
        """ShadowSnapshot should have a readable repr."""
        c = Circuit()
        c.measure(0)
        shadows = classical_shadow(c, shots=512, n_shadow=4)
        r = repr(shadows[0])
        assert "Shadow" in r
        assert "unitary_indices" in r
        assert "outcomes" in r
