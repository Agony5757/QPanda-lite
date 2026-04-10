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
    def run_test_zz_on_computational(self):
        """⟨ZZ⟩ on |00⟩ should be +1."""
        c = Circuit()
        c.measure(0, 1)
        val = pauli_expectation(c, "ZZ", shots=None)
        assert np.isclose(val, 1.0)

    def run_test_zz_on_one_minus_one(self):
        """⟨ZZ⟩ on |01⟩ should be -1."""
        c = Circuit()
        c.x(0)
        c.measure(0, 1)
        val = pauli_expectation(c, "ZZ", shots=None)
        assert np.isclose(val, -1.0)

    def run_test_xx_on_bell(self):
        """⟨XX⟩ on Bell (|00⟩+|11⟩)/√2 should be +1."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        val = pauli_expectation(c, "XX", shots=None)
        assert np.isclose(val, 1.0)

    def run_test_yy_on_bell(self):
        """⟨YY⟩ on Bell should be +1."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        val = pauli_expectation(c, "YY", shots=None)
        assert np.isclose(val, 1.0)

    def run_test_ix_on_bell(self):
        """⟨IX⟩ on Bell = ⟨X⟩ on qubit 1 should be 0 (uniform)."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        val = pauli_expectation(c, "IX", shots=None)
        assert np.isclose(val, 0.0)

    def run_test_shots_variance(self):
        """shots mode should give a result close to the exact value."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        exact = pauli_expectation(c, "ZZ", shots=None)
        sampled = pauli_expectation(c, "ZZ", shots=10000)
        assert abs(sampled - exact) < 0.1

    def run_test_wrong_length_raises(self):
        c = Circuit()
        c.measure(0, 1)
        with pytest.raises(ValueError, match="length"):
            pauli_expectation(c, "Z", shots=None)

    def run_test_invalid_pauli_char_raises(self):
        c = Circuit()
        c.measure(0, 1)
        with pytest.raises(ValueError, match="I/X/Y/Z"):
            pauli_expectation(c, "AAA", shots=None)


class TestBasisRotationMeasurement:
    def run_test_z_basis_on_plus(self):
        """|+⟩ measured in Z basis: P(0)=0.5, P(1)=0.5."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="Z", shots=None)
        assert np.isclose(result["0"], 0.5)
        assert np.isclose(result["1"], 0.5)

    def run_test_x_basis_on_plus(self):
        """|+⟩ measured in X basis: P(0)=1, P(1)=0."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="X", shots=None)
        assert np.isclose(result["0"], 1.0)

    def run_test_x_basis_on_minus(self):
        """|-⟩ measured in X basis: P(0)=0, P(1)=1."""
        c = Circuit()
        c.x(0)
        c.h(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="X", shots=None)
        assert np.isclose(result["1"], 1.0)

    def run_test_y_basis_on_iplus(self):
        """|i⟩ = S|0⟩ measured in Y basis: P(0)=1 (eigenstate |0⟩_Y)."""
        c = Circuit()
        c.s(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="Y", shots=None)
        assert np.isclose(result["0"], 1.0)

    def run_test_two_qubit_xy(self):
        """2-qubit state |+⟩|0⟩ measured in X,Z basis."""
        c = Circuit()
        c.h(0)
        c.measure(0, 1)
        result = basis_rotation_measurement(c, basis=["X", "Z"], shots=None)
        assert np.isclose(result["00"], 0.5)
        assert np.isclose(result["10"], 0.5)

    def run_test_shots_mode(self):
        """shots mode returns integer counts."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        result = basis_rotation_measurement(c, basis="Z", shots=100)
        total = sum(result.values())
        assert total == 100
        assert all(isinstance(v, int) for v in result.values())


class TestStateTomography:
    def run_test_pure_state_reconstruction(self):
        """|ψ⟩ = (|00⟩+|11⟩)/√2 should reconstruct to a rank-1 density matrix."""
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

    def run_test_mixed_state(self):
        """|0⟩⊗|0⟩ (product state) should have purity 1 after tomography."""
        c = Circuit()
        c.measure(0, 1)
        rho = state_tomography(c, shots=4096)
        purity = np.real(np.trace(rho @ rho))
        assert abs(purity - 1.0) < 0.05

    def run_test_tomography_summary_runs(self):
        """tomography_summary should run without error."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        rho = state_tomography(c, shots=1024)
        # Should not raise
        tomography_summary(rho)

    def run_test_wrong_shots_raises(self):
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError):
            state_tomography(c, shots=-1)


class TestClassicalShadow:
    def run_test_shadow_generates_correct_count(self):
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=1024, n_shadow=16)
        assert len(shadows) == 16

    def run_test_auto_n_shadow(self):
        """Auto n_shadow should scale with qubit count."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=512)  # auto n_shadow
        assert len(shadows) > 0

    def run_test_shadow_expectation_zz_bell(self):
        """|Φ+⟩ = (|00⟩+|11⟩)/√2: ⟨ZZ⟩ ≈ 1."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=1024, n_shadow=64)
        est = shadow_expectation(shadows, "ZZ")
        assert abs(est - 1.0) < 0.2

    def run_test_shadow_expectation_xx_bell(self):
        """|Φ+⟩: ⟨XX⟩ ≈ 1."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=1024, n_shadow=64)
        est = shadow_expectation(shadows, "XX")
        assert abs(est - 1.0) < 0.2

    def run_test_shadow_expectation_identity(self):
        """|Φ+⟩: ⟨II⟩ = 1 always."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=512, n_shadow=16)
        est = shadow_expectation(shadows, "II")
        assert np.isclose(est, 1.0)

    def run_test_shadow_wrong_length_raises(self):
        c = Circuit()
        c.measure(0, 1)
        shadows = classical_shadow(c, shots=512, n_shadow=8)
        with pytest.raises(ValueError, match="length"):
            shadow_expectation(shadows, "Z")   # 1 qubit, shadow has 2

    def run_test_empty_shadows_raises(self):
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError, match="empty"):
            shadow_expectation([], "Z")
