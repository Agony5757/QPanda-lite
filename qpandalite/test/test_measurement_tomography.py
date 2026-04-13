"""Additional tests for state_tomography covering single-qubit states,
density matrix verification, 3-qubit, and edge cases."""

import numpy as np
import pytest

from qpandalite.circuit_builder import Circuit
from qpandalite.algorithmics.measurement import state_tomography, tomography_summary


class TestSingleQubitTomography:
    """Single-qubit state tomography tests."""

    def test_zero_state(self):
        """|0⟩ tomography: ρ = [[1,0],[0,0]]."""
        c = Circuit()
        c.measure(0)
        rho = state_tomography(c, shots=8192)
        assert rho.shape == (2, 2)
        assert abs(rho[0, 0] - 1.0) < 0.05
        assert abs(rho[1, 1]) < 0.05

    def test_one_state(self):
        """|1⟩ tomography: ρ = [[0,0],[0,1]]."""
        c = Circuit()
        c.x(0)
        c.measure(0)
        rho = state_tomography(c, shots=8192)
        assert rho.shape == (2, 2)
        assert abs(rho[1, 1] - 1.0) < 0.05
        assert abs(rho[0, 0]) < 0.05

    def test_plus_state(self):
        """|+⟩ tomography: ρ = [[0.5, 0.5],[0.5, 0.5]]."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        rho = state_tomography(c, shots=8192)
        assert rho.shape == (2, 2)
        # Diagonal elements should be ~0.5
        assert abs(rho[0, 0] - 0.5) < 0.05
        assert abs(rho[1, 1] - 0.5) < 0.05
        # Purity ≈ 1 for pure state
        purity = np.real(np.trace(rho @ rho))
        assert abs(purity - 1.0) < 0.05


class TestDensityMatrixVerification:
    """Verify density matrix properties."""

    def test_bell_diagonal_elements(self):
        """Bell state ρ[0,0] and ρ[3,3] should be ~0.5."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        rho = state_tomography(c, shots=8192)
        assert abs(rho[0, 0] - 0.5) < 0.05
        assert abs(rho[3, 3] - 0.5) < 0.05
        # Off-diagonal ρ[0,3] and ρ[3,0] should be ~0.5
        assert abs(abs(rho[0, 3]) - 0.5) < 0.1

    def test_hermitian(self):
        """Density matrix should be Hermitian."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        rho = state_tomography(c, shots=4096)
        assert np.allclose(rho, rho.conj().T, atol=0.05)

    def test_unit_trace(self):
        """Density matrix trace should be 1."""
        c = Circuit()
        c.h(0)
        c.x(1)
        c.measure(0, 1)
        rho = state_tomography(c, shots=4096)
        assert np.isclose(np.trace(rho).real, 1.0, atol=0.02)


class TestThreeQubitTomography:
    """3-qubit state tomography tests."""

    def test_computational_3qubit(self):
        """|000⟩ tomography: ρ should be diag(1,0,0,...)."""
        c = Circuit()
        c.measure(0, 1, 2)
        rho = state_tomography(c, shots=8192)
        assert rho.shape == (8, 8)
        assert abs(rho[0, 0] - 1.0) < 0.05
        # All other diagonal elements should be ~0
        for i in range(1, 8):
            assert abs(rho[i, i]) < 0.05

    def test_ghz3_purity(self):
        """3-qubit GHZ should have purity ≈ 1."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.cx(0, 2)
        c.measure(0, 1, 2)
        rho = state_tomography(c, shots=8192)
        purity = np.real(np.trace(rho @ rho))
        assert abs(purity - 1.0) < 0.1

    def test_ghz3_shape(self):
        """3-qubit tomography should return 8×8 matrix."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.cx(0, 2)
        c.measure(0, 1, 2)
        rho = state_tomography(c, shots=4096)
        assert rho.shape == (8, 8)
        assert np.isclose(np.trace(rho).real, 1.0, atol=0.05)


class TestTomographySummary:
    """Tests for tomography_summary output format."""

    def test_summary_pure_state(self, capsys):
        """tomography_summary on pure state should print purity info."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        rho = state_tomography(c, shots=4096)
        tomography_summary(rho)
        captured = capsys.readouterr()
        assert "Purity" in captured.out
        assert "Trace" in captured.out
        assert "Eigenvalues" in captured.out

    def test_summary_with_reference(self, capsys):
        """tomography_summary with reference_state should print fidelity."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        rho = state_tomography(c, shots=8192)
        # Use same state as reference
        rho_ref = state_tomography(c, shots=8192)
        tomography_summary(rho, reference_state=rho_ref)
        captured = capsys.readouterr()
        assert "Fidelity" in captured.out


class TestTomographyEdgeCases:
    """Edge cases for state_tomography."""

    def test_shots_one(self):
        """shots=1 should still return a valid density matrix shape."""
        c = Circuit()
        c.measure(0)
        rho = state_tomography(c, shots=1)
        assert rho.shape == (2, 2)

    def test_shots_zero_raises(self):
        """shots=0 should raise ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError):
            state_tomography(c, shots=0)

    def test_empty_qubits_raises(self):
        """Empty qubits list should raise ValueError."""
        c = Circuit()
        c.measure(0)
        with pytest.raises(ValueError):
            state_tomography(c, qubits=[], shots=4096)

    def test_selected_qubits(self):
        """Tomography on selected qubits should return correct shape."""
        c = Circuit()
        c.h(0)
        c.cx(0, 1)
        c.measure(0, 1)
        # Only tomograph qubit 0
        rho = state_tomography(c, qubits=[0], shots=4096)
        assert rho.shape == (2, 2)
        # Qubit 0 of Bell state is maximally mixed: ρ ≈ I/2
        assert abs(rho[0, 0] - 0.5) < 0.1
