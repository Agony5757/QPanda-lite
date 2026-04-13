"""Additional tests for pauli_expectation covering single-qubit Pauli,
identity, mixed Pauli, 3-qubit, and edge cases."""

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.measurement import pauli_expectation


class TestSingleQubitPauli:
    """Single-qubit Pauli expectation values on eigenstates."""

    def test_z_on_zero(self):
        """⟨Z⟩ on |0⟩ should be +1."""
        c = Circuit()
        c.measure(0)
        assert np.isclose(pauli_expectation(c, "Z", shots=None), 1.0)

    def test_z_on_one(self):
        """⟨Z⟩ on |1⟩ should be -1."""
        c = Circuit()
        c.x(0)
        c.measure(0)
        assert np.isclose(pauli_expectation(c, "Z", shots=None), -1.0)

    def test_x_on_plus(self):
        """⟨X⟩ on |+⟩ = (|0⟩+|1⟩)/√2 should be +1."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        assert np.isclose(pauli_expectation(c, "X", shots=None), 1.0)

    def test_x_on_minus(self):
        """⟨X⟩ on |−⟩ = (|0⟩−|1⟩)/√2 should be -1."""
        c = Circuit()
        c.x(0)
        c.h(0)
        c.measure(0)
        assert np.isclose(pauli_expectation(c, "X", shots=None), -1.0)

    def test_y_on_iplus(self):
        """⟨Y⟩ on |i+⟩ = S|+⟩ should be +1.

        |i+⟩ = (|0⟩ + i|1⟩)/√2, which is the +1 eigenstate of Y.
        We prepare it as H then S on |0⟩.
        """
        c = Circuit()
        c.h(0)
        c.s(0)
        c.measure(0)
        assert np.isclose(pauli_expectation(c, "Y", shots=None), 1.0)

    def test_y_on_iminus(self):
        """⟨Y⟩ on |i−⟩ should be -1.

        |i−⟩ = (|0⟩ − i|1⟩)/√2, which is the -1 eigenstate of Y.
        Prepare as X then H then S.
        """
        c = Circuit()
        c.x(0)
        c.h(0)
        c.s(0)
        c.measure(0)
        assert np.isclose(pauli_expectation(c, "Y", shots=None), -1.0)

    def test_z_on_plus_is_zero(self):
        """⟨Z⟩ on |+⟩ should be 0 (uniform superposition)."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        assert np.isclose(pauli_expectation(c, "Z", shots=None), 0.0)


class TestIdentityPauli:
    """Identity operator should always give expectation +1."""

    def test_i_on_zero(self):
        """⟨I⟩ on |0⟩ = 1."""
        c = Circuit()
        c.measure(0)
        assert np.isclose(pauli_expectation(c, "I", shots=None), 1.0)

    def test_ii_on_zerozero(self):
        """⟨II⟩ on |00⟩ = 1."""
        c = Circuit()
        c.measure(0, 1)
        assert np.isclose(pauli_expectation(c, "II", shots=None), 1.0)

    def test_ii_on_bell(self):
        """⟨II⟩ on Bell state = 1."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        assert np.isclose(pauli_expectation(c, "II", shots=None), 1.0)


class TestMixedPauli:
    """Mixed Pauli strings like XI, IZ, etc."""

    def test_xi_on_plus_zero(self):
        """⟨XI⟩ on |+⟩|0⟩: ⟨X⟩⊗⟨I⟩ = 1*1 = 1."""
        c = Circuit()
        c.h(0)
        c.measure(0, 1)
        assert np.isclose(pauli_expectation(c, "XI", shots=None), 1.0)

    def test_iz_on_plus_zero(self):
        """⟨IZ⟩ on |+⟩|0⟩: ⟨I⟩⊗⟨Z⟩ = 1*1 = 1."""
        c = Circuit()
        c.h(0)
        c.measure(0, 1)
        assert np.isclose(pauli_expectation(c, "IZ", shots=None), 1.0)

    def test_zi_on_plus_zero(self):
        """⟨ZI⟩ on |+⟩|0⟩: ⟨Z⟩⊗⟨I⟩ = 0*1 = 0."""
        c = Circuit()
        c.h(0)
        c.measure(0, 1)
        assert np.isclose(pauli_expectation(c, "ZI", shots=None), 0.0)

    def test_ix_on_zero_plus(self):
        """⟨IX⟩ on |0⟩|+⟩: ⟨I⟩⊗⟨X⟩ = 1*1 = 1."""
        c = Circuit()
        c.h(1)
        c.measure(0, 1)
        assert np.isclose(pauli_expectation(c, "IX", shots=None), 1.0)


class TestThreeQubitPauli:
    """3-qubit Pauli string tests."""

    def test_zzz_on_zerozerozero(self):
        """⟨ZZZ⟩ on |000⟩ = +1."""
        c = Circuit()
        c.measure(0, 1, 2)
        assert np.isclose(pauli_expectation(c, "ZZZ", shots=None), 1.0)

    def test_zzi_on_ghz3(self):
        """⟨ZZI⟩ on 3-qubit GHZ state: should equal ⟨ZZ⟩ on first two qubits = 1."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.cx(0, 2)
        c.measure(0, 1, 2)
        assert np.isclose(pauli_expectation(c, "ZZI", shots=None), 1.0)

    def test_xxx_on_ghz3(self):
        """⟨XXX⟩ on 3-qubit GHZ: should be +1."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.cx(0, 2)
        c.measure(0, 1, 2)
        assert np.isclose(pauli_expectation(c, "XXX", shots=None), 1.0)

    def test_ixx_on_ghz3(self):
        """⟨IXX⟩ on 3-qubit GHZ: ⟨X₂X₃⟩ = +1."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.cx(0, 2)
        c.measure(0, 1, 2)
        assert np.isclose(pauli_expectation(c, "IXX", shots=None), 1.0)


class TestPauliEdgeCases:
    """Edge cases: invalid shots, empty string, custom qubit number."""

    def test_shots_zero_raises(self):
        """shots=0 should raise ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError, match="positive"):
            pauli_expectation(c, "Z", shots=0)

    def test_shots_negative_raises(self):
        """shots=-1 should raise ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError, match="positive"):
            pauli_expectation(c, "Z", shots=-1)

    def test_empty_pauli_string_raises(self):
        """Empty pauli_string should raise ValueError (length mismatch)."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError):
            pauli_expectation(c, "", shots=None)

    def test_case_insensitive(self):
        """Lowercase pauli_string should work."""
        c = Circuit()
        c.measure(0)
        assert np.isclose(pauli_expectation(c, "z", shots=None), 1.0)

    def test_3qubit_circuit_2qubit_pauli_raises(self):
        """Pauli string shorter than circuit qubits should raise."""
        c = Circuit()
        c.measure(0, 1, 2)
        with pytest.raises(ValueError, match="length"):
            pauli_expectation(c, "ZZ", shots=None)

    def test_shots_single_qubit(self):
        """Shots mode on single qubit should be close to exact."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        exact = pauli_expectation(c, "X", shots=None)
        sampled = pauli_expectation(c, "X", shots=8192)
        assert abs(sampled - exact) < 0.05
