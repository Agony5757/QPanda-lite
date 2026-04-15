"""Unit tests for the measurement module."""

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.measurement import (
    pauli_expectation,
    state_tomography,
    tomography_summary,
    classical_shadow,
    shadow_expectation,
    basis_rotation_measurement,
)


class TestPauliExpectation:
    """Tests for Pauli string expectation value calculations."""
    def test_zz_on_computational(self):
        """Test ⟨ZZ⟩ expectation on |00⟩ state.

        Verifies that the expectation value of ZZ operator on |00⟩ is +1.
        """
        c = Circuit()
        c.measure(0, 1)
        val = pauli_expectation(c, "ZZ", shots=None)
        assert np.isclose(val, 1.0)

    def test_zz_on_one_minus_one(self):
        """Test ⟨ZZ⟩ expectation on |01⟩ state.

        Verifies that the expectation value of ZZ operator on |01⟩ is -1.
        """
        c = Circuit()
        c.x(0)
        c.measure(0, 1)
        val = pauli_expectation(c, "ZZ", shots=None)
        assert np.isclose(val, -1.0)

    def test_xx_on_bell(self):
        """Test ⟨XX⟩ expectation on Bell state.

        Verifies that the expectation value of XX operator on Bell state
        (|00⟩+|11⟩)/√2 is +1.
        """
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        val = pauli_expectation(c, "XX", shots=None)
        assert np.isclose(val, 1.0)

    def test_yy_on_bell(self):
        """Test ⟨YY⟩ expectation on Bell state.

        Verifies that the expectation value of YY operator on Bell state is +1.
        """
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        val = pauli_expectation(c, "YY", shots=None)
        assert np.isclose(val, 1.0)

    def test_ix_on_bell(self):
        """Test ⟨IX⟩ expectation on Bell state.

        Verifies that ⟨IX⟩ = ⟨X⟩ on qubit 1 equals 0 for uniform distribution.
        """
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        val = pauli_expectation(c, "IX", shots=None)
        assert np.isclose(val, 0.0)

    def test_shots_variance(self):
        """Test finite shots measurement variance.

        Verifies that shots mode produces results close to the exact value
        within expected statistical variance.
        """
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        exact = pauli_expectation(c, "ZZ", shots=None)
        sampled = pauli_expectation(c, "ZZ", shots=10000)
        assert abs(sampled - exact) < 0.1

    def test_wrong_length_raises(self):
        """Test that mismatched Pauli length raises ValueError."""
        c = Circuit()
        c.measure(0, 1)
        with pytest.raises(ValueError, match="length"):
            pauli_expectation(c, "Z", shots=None)

    def test_invalid_pauli_char_raises(self):
        """Test that invalid Pauli characters raise ValueError."""
        c = Circuit()
        c.measure(0, 1)
        with pytest.raises(ValueError, match="I/X/Y/Z"):
            pauli_expectation(c, "AAA", shots=None)


class TestBasisRotationMeasurement:
    """Tests for basis rotation measurement functionality."""
    def test_z_basis_on_plus(self):
        """Test |+⟩ measurement in Z basis.

        Verifies that |+⟩ state measured in Z basis yields P(0)=0.5, P(1)=0.5.
        """
        c = Circuit()
        c.h(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="Z", shots=None)
        assert np.isclose(result["0"], 0.5)
        assert np.isclose(result["1"], 0.5)

    def test_x_basis_on_plus(self):
        """Test |+⟩ measurement in X basis.

        Verifies that |+⟩ state measured in X basis yields P(0)=1, P(1)=0.
        """
        c = Circuit()
        c.h(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="X", shots=None)
        assert np.isclose(result["0"], 1.0)

    def test_x_basis_on_minus(self):
        """Test |-⟩ measurement in X basis.

        Verifies that |-⟩ state measured in X basis yields P(0)=0, P(1)=1.
        """
        c = Circuit()
        c.x(0)
        c.h(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="X", shots=None)
        assert np.isclose(result["1"], 1.0)

    def test_y_basis_on_iplus(self):
        """Test |i⟩ measurement in Y basis.

        Verifies that |i⟩ = S|0⟩ measured in Y basis is eigenstate |0⟩_Y.
        """
        c = Circuit()
        c.s(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="Y", shots=None)
        assert np.isclose(result["0"], 1.0)

    def test_two_qubit_xy(self):
        """Test two-qubit measurement in mixed bases.

        Verifies that |+⟩|0⟩ state measured in X,Z basis yields correct probabilities.
        """
        c = Circuit()
        c.h(0)
        c.measure(0, 1)
        result = basis_rotation_measurement(c, basis=["X", "Z"], shots=None)
        assert np.isclose(result["00"], 0.5)
        assert np.isclose(result["10"], 0.5)

    def test_shots_mode(self):
        """Test shots mode returns integer counts.

        Verifies that finite shots mode returns integer count results
        with correct total sum.
        """
        c = Circuit()
        c.h(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="Z", shots=100)
        total = sum(result.values())
        assert total == 100
        assert all(isinstance(v, int) for v in result.values())


class TestStateTomography:
    """Tests for quantum state tomography reconstruction."""
    def test_pure_state_reconstruction(self):
        """Test pure Bell state reconstruction.

        Verifies that |ψ⟩ = (|00⟩+|11⟩)/√2 reconstructs to a rank-1 density matrix
        with correct Hermiticity, normalization, and purity.
        """
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        rho = state_tomography(c, shots=8192)
        # Check Hermitian and normalised
        assert np.allclose(rho, rho.conj().T)
        assert np.isclose(np.trace(rho), 1.0)
        # Purity for pure state ≈ 1
        purity = np.real(np.trace(rho @ rho))
        assert abs(purity - 1.0) < 0.05

    def test_mixed_state(self):
        """Test product state tomography.

        Verifies that |0⟩⊗|0⟩ product state reconstructs with purity ≈ 1.
        """
        c = Circuit()
        c.measure(0, 1)
        rho = state_tomography(c, shots=4096)
        purity = np.real(np.trace(rho @ rho))
        assert abs(purity - 1.0) < 0.05

    def test_tomography_summary_runs(self):
        """Test tomography_summary execution.

        Verifies that tomography_summary runs without error on reconstructed state.
        """
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        rho = state_tomography(c, shots=1024)
        # Should not raise
        tomography_summary(rho)

    def test_wrong_shots_raises(self):
        """Test that negative shots raises ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError):
            state_tomography(c, shots=-1)


class TestClassicalShadow:
    """Tests for classical shadow estimation technique."""
    def test_shadow_generates_correct_count(self):
        """Test that shadow generates correct number of snapshots."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=1024, n_shadow=16)
        assert len(shadows) == 16

    def test_auto_n_shadow(self):
        """Test auto n_shadow scaling.

        Verifies that automatic n_shadow calculation scales appropriately
        with qubit count.
        """
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=512)  # auto n_shadow
        assert len(shadows) > 0

    def test_shadow_expectation_zz_bell(self):
        """Test ⟨ZZ⟩ estimation on Bell state.

        Verifies that classical shadow estimates ⟨ZZ⟩ ≈ 1 for Bell state |Φ+⟩.
        """
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=1024, n_shadow=64)
        est = shadow_expectation(shadows, "ZZ")
        assert abs(est - 1.0) < 0.2

    def test_shadow_expectation_xx_bell(self):
        """Test ⟨XX⟩ estimation on Bell state.

        Verifies that classical shadow estimates ⟨XX⟩ ≈ 1 for Bell state |Φ+⟩.
        """
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=1024, n_shadow=64)
        est = shadow_expectation(shadows, "XX")
        assert abs(est - 1.0) < 0.2

    def test_shadow_expectation_identity(self):
        """Test identity operator estimation.

        Verifies that classical shadow always estimates ⟨II⟩ = 1.
        """
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=512, n_shadow=16)
        est = shadow_expectation(shadows, "II")
        assert np.isclose(est, 1.0)

    def test_shadow_wrong_length_raises(self):
        """Test that mismatched operator length raises ValueError."""
        c = Circuit()
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=512, n_shadow=8)
        with pytest.raises(ValueError, match="length"):
            shadow_expectation(shadows, "Z")   # 1 qubit, shadow has 2

    def test_empty_shadows_raises(self):
        """Test that empty shadow list raises ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError, match="empty"):
            shadow_expectation([], "Z")
