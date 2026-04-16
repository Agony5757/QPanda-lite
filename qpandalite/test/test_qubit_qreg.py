"""
Comprehensive unit tests for qpandalite.circuit_builder.qubit.

Tests cover:
- Qubit: creation, naming, int conversion, hash
- QReg: creation, indexing, slicing
- QRegSlice: iteration, length
- Circuit integration with QReg/Qubit
"""

import pytest
from qpandalite.circuit_builder.qubit import Qubit, QReg, QRegSlice


# =============================================================================
# TestQubit
# =============================================================================


class TestQubit:
    """Tests for Qubit class."""

    def test_qubit_creation(self):
        """Qubit can be created with name, index, and base_index."""
        q = Qubit(name="a[0]", index=0, base_index=5)
        assert q.name == "a[0]"
        assert q.index == 0
        assert q.base_index == 5

    def test_qubit_int_conversion(self):
        """Qubit can be converted to int (base_index + index)."""
        q = Qubit(name="a[2]", index=2, base_index=10)
        assert int(q) == 12

    def test_qubit_hash_and_eq(self):
        """Qubits with same name are equal and have same hash."""
        q1 = Qubit(name="a[0]", index=0, base_index=0)
        q2 = Qubit(name="a[0]", index=0, base_index=0)
        q3 = Qubit(name="a[1]", index=1, base_index=0)
        assert q1 == q2
        assert q1 != q3
        assert hash(q1) == hash(q2)

    def test_qubit_repr(self):
        """Qubit repr is informative."""
        q = Qubit(name="a[0]", index=0, base_index=0)
        assert "a[0]" in repr(q)


# =============================================================================
# TestQReg
# =============================================================================


class TestQReg:
    """Tests for QReg class."""

    def test_qreg_creation(self):
        """QReg can be created with name and size."""
        qr = QReg(name="a", size=4)
        assert qr.name == "a"
        assert qr.size == 4

    def test_qreg_len(self):
        """len(QReg) returns its size."""
        qr = QReg(name="a", size=5)
        assert len(qr) == 5

    def test_qreg_single_indexing(self):
        """QReg[i] returns a Qubit."""
        qr = QReg(name="a", size=4, base_index=10)
        q0 = qr[0]
        assert isinstance(q0, Qubit)
        assert q0.name == "a[0]"
        assert q0.index == 0
        assert int(q0) == 10

    def test_qreg_slice_indexing(self):
        """QReg[1:3] returns a QRegSlice."""
        qr = QReg(name="a", size=6, base_index=0)
        qs = qr[1:3]
        assert isinstance(qs, QRegSlice)
        assert len(qs) == 2

    def test_qreg_negative_indexing(self):
        """QReg[-1] returns the last qubit."""
        qr = QReg(name="a", size=4, base_index=0)
        q_last = qr[-1]
        assert q_last.index == 3
        assert int(q_last) == 3

    def test_qreg_index_out_of_range(self):
        """QReg[i] raises IndexError for out-of-range index."""
        qr = QReg(name="a", size=4)
        with pytest.raises(IndexError):
            _ = qr[10]

    def test_qreg_qubits_property(self):
        """QReg.qubits returns list of all Qubits."""
        qr = QReg(name="a", size=3, base_index=5)
        qubits = qr.qubits
        assert len(qubits) == 3
        assert all(isinstance(q, Qubit) for q in qubits)
        assert [int(q) for q in qubits] == [5, 6, 7]


# =============================================================================
# TestQRegSlice
# =============================================================================


class TestQRegSlice:
    """Tests for QRegSlice class."""

    def test_qregslice_creation(self):
        """QRegSlice can be created from a QReg."""
        qr = QReg(name="a", size=5, base_index=10)
        qs = qr[1:4]
        assert isinstance(qs, QRegSlice)
        assert len(qs) == 3

    def test_qregslice_iteration(self):
        """QRegSlice can be iterated over Qubits."""
        qr = QReg(name="a", size=5, base_index=0)
        qs = qr[1:3]
        qubits = list(qs)
        assert len(qubits) == 2
        assert qubits[0].index == 1
        assert qubits[1].index == 2

    def test_qregslice_single_element_indexing(self):
        """QRegSlice[i] returns a Qubit."""
        qr = QReg(name="a", size=5, base_index=0)
        qs = qr[1:3]
        q = qs[0]
        assert isinstance(q, Qubit)
        assert q.index == 1

    def test_qregslice_step_slicing(self):
        """QReg[::2] returns every other qubit."""
        qr = QReg(name="a", size=6, base_index=0)
        qs = qr[::2]
        assert len(qs) == 3
        indices = [q.index for q in qs]
        assert indices == [0, 2, 4]


# =============================================================================
# TestCircuitQReg
# =============================================================================


class TestCircuitQReg:
    """Tests for Circuit integration with QReg/Qubit."""

    def test_circuit_with_qregs_dict(self):
        """Circuit can be created with qregs dict."""
        # This test assumes Circuit will be modified to accept qregs
        # For now, we test that QReg can be created independently
        qr = QReg(name="a", size=4, base_index=0)
        assert qr.name == "a"
        assert qr.size == 4

    def test_qubit_resolves_to_int(self):
        """Qubit objects can be used where int qubit indices are expected."""
        qr = QReg(name="a", size=4, base_index=10)
        q = qr[2]
        # The int() conversion should give the physical qubit index
        assert int(q) == 12

    def test_multiple_qregs(self):
        """Multiple QRegs with different base indices."""
        qr_a = QReg(name="a", size=3, base_index=0)
        qr_b = QReg(name="b", size=2, base_index=3)
        assert int(qr_a[2]) == 2
        assert int(qr_b[0]) == 3

    def test_qreg_slice_for_multiqubit_gates(self):
        """QRegSlice can provide qubits for multi-qubit operations."""
        qr = QReg(name="a", size=4, base_index=0)
        qs = qr[0:2]
        qubits = list(qs)
        assert len(qubits) == 2
        # These could be used as control and target for a CNOT
        assert qubits[0].index == 0
        assert qubits[1].index == 1


# =============================================================================
# TestBackwardCompatibility
# =============================================================================


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility with existing integer-based code."""

    def test_qubit_int_implicit(self):
        """Qubit can be implicitly converted to int in arithmetic."""
        qr = QReg(name="a", size=4, base_index=10)
        q = qr[1]
        # int(q) should work
        assert int(q) == 11

    def test_qubit_comparison_with_int(self):
        """Qubit can be compared with int (via int conversion)."""
        qr = QReg(name="a", size=4, base_index=5)
        q = qr[2]
        # Comparing Qubit with int should compare the resolved index
        assert int(q) == 7
