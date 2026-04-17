"""Comprehensive unit tests for qpandalite.analyzer.expectation."""

import numpy as np
import pytest

from qpandalite.analyzer.expectation import (
    calculate_expectation,
    calculate_exp_X,
    calculate_exp_Y,
    calculate_multi_basis_expectation,
)


# =============================================================================
# TestCalculateExpectation
# =============================================================================
class TestCalculateExpectation:
    """Tests for calculate_expectation."""

    # -------------------------------------------------------------------------
    # Parameter validation
    # -------------------------------------------------------------------------
    def test_invalid_hamiltonian_char(self):
        """Hamiltonian with invalid characters raises ValueError."""
        result = {"00": 1.0}
        with pytest.raises(ValueError, match="only containing Z or I"):
            calculate_expectation(result, "XZ")

    def test_empty_hamiltonian_no_raise(self):
        """Empty string Hamiltonian is valid for empty result (nqubit=0)."""
        # Empty string hamiltonian means nqubit=0, matches empty-dict result
        result = {"": 1.0}
        assert np.isclose(calculate_expectation(result, ""), 1.0)

    def test_hamiltonian_length_mismatch_dict(self):
        """Hamiltonian length != number of qubits raises ValueError."""
        result = {"000": 1.0}  # 3 qubits
        with pytest.raises(ValueError, match="same size"):
            calculate_expectation(result, "ZZ")  # 2-qubit Hamiltonian

    def test_hamiltonian_length_mismatch_list(self):
        """List result length mismatch with Hamiltonian raises ValueError."""
        result = [1.0, 0.0]  # 2**1 = 2 entries = 1 qubit
        with pytest.raises(ValueError, match="same size"):
            calculate_expectation(result, "ZZ")  # 2-qubit Hamiltonian

    def test_wrong_input_type(self):
        """Non-dict/non-list measured_result raises ValueError."""
        with pytest.raises(ValueError, match="Dict or a List"):
            calculate_expectation("invalid", "Z")

    def test_hamiltonian_not_string_or_list(self):
        """Hamiltonian that is neither str nor list raises ValueError."""
        result = {"0": 1.0}
        with pytest.raises(ValueError, match="must be a str"):
            calculate_expectation(result, 42)

    # -------------------------------------------------------------------------
    # Numerical correctness - eigenstates
    # -------------------------------------------------------------------------
    def test_z_on_zero_state(self):
        """Z on |0> = +1."""
        result = {"0": 1.0}
        assert np.isclose(calculate_expectation(result, "Z"), 1.0)

    def test_z_on_one_state(self):
        """Z on |1> = -1."""
        result = {"1": 1.0}
        assert np.isclose(calculate_expectation(result, "Z"), -1.0)

    def test_z_on_plus_state(self):
        """Z on |+> = 0 (equal superposition)."""
        result = {"0": 0.5, "1": 0.5}
        assert np.isclose(calculate_expectation(result, "Z"), 0.0)

    def test_z_on_minus_state(self):
        """Z on |-> = 0 (equal superposition)."""
        result = {"0": 0.5, "1": 0.5}
        assert np.isclose(calculate_expectation(result, "Z"), 0.0)

    def test_zz_on_bell_state_00_11(self):
        """ZZ on Bell state |Phi+> = (|00>+|11>)/sqrt(2) = +1."""
        result = {"00": 0.5, "11": 0.5}
        assert np.isclose(calculate_expectation(result, "ZZ"), 1.0)

    def test_zi_on_bell_state(self):
        """ZI on Bell state |Phi+> = 0 (reduced density matrix maximally mixed)."""
        result = {"00": 0.5, "11": 0.5}
        assert np.isclose(calculate_expectation(result, "ZI"), 0.0)

    def test_iz_on_bell_state(self):
        """IZ on Bell state |Phi+> = 0."""
        result = {"00": 0.5, "11": 0.5}
        assert np.isclose(calculate_expectation(result, "IZ"), 0.0)

    def test_zz_on_product_state_00(self):
        """ZZ on |00> = +1."""
        result = {"00": 1.0}
        assert np.isclose(calculate_expectation(result, "ZZ"), 1.0)

    def test_zz_on_product_state_11(self):
        """ZZ on |11> = +1 (two Z flips = positive)."""
        result = {"11": 1.0}
        assert np.isclose(calculate_expectation(result, "ZZ"), 1.0)

    def test_zz_on_product_state_01(self):
        """ZZ on |01> = -1 (one Z flip)."""
        result = {"01": 1.0}
        assert np.isclose(calculate_expectation(result, "ZZ"), -1.0)

    def test_zz_on_product_state_10(self):
        """ZZ on |10> = -1 (one Z flip)."""
        result = {"10": 1.0}
        assert np.isclose(calculate_expectation(result, "ZZ"), -1.0)

    def test_i_identity_term(self):
        """I on any state = 1 (identity does nothing)."""
        assert np.isclose(calculate_expectation({"0": 1.0}, "I"), 1.0)
        assert np.isclose(calculate_expectation({"00": 1.0}, "II"), 1.0)
        assert np.isclose(calculate_expectation({"0": 0.5, "1": 0.5}, "I"), 1.0)

    def test_zi_identity_mix(self):
        """ZI on |00> = +1 (Z on qubit 0 which is 0, I on qubit 1)."""
        result = {"00": 1.0}
        assert np.isclose(calculate_expectation(result, "ZI"), 1.0)

    def test_iz_identity_mix(self):
        """IZ on |00> = +1."""
        result = {"00": 1.0}
        assert np.isclose(calculate_expectation(result, "IZ"), 1.0)

    def test_iz_on_01(self):
        """IZ on |01> = -1 (Z on qubit 1 which is 1)."""
        result = {"01": 1.0}
        assert np.isclose(calculate_expectation(result, "IZ"), -1.0)

    # -------------------------------------------------------------------------
    # List input format
    # -------------------------------------------------------------------------
    def test_z_on_zero_state_list(self):
        """Z on |0> = +1 (list format [P(0), P(1)])."""
        result = [1.0, 0.0]
        assert np.isclose(calculate_expectation(result, "Z"), 1.0)

    def test_z_on_one_state_list(self):
        """Z on |1> = -1 (list format)."""
        result = [0.0, 1.0]
        assert np.isclose(calculate_expectation(result, "Z"), -1.0)

    def test_zz_on_bell_state_list(self):
        """ZZ on Bell state = +1 (list format: [P(00), P(01), P(10), P(11)])."""
        result = [0.5, 0.0, 0.0, 0.5]
        assert np.isclose(calculate_expectation(result, "ZZ"), 1.0)

    def test_zi_on_bell_state_list(self):
        """ZI on Bell state = 0 (list format)."""
        result = [0.5, 0.0, 0.0, 0.5]
        assert np.isclose(calculate_expectation(result, "ZI"), 0.0)

    def test_zz_on_product_state_00_list(self):
        """ZZ on |00> = +1 (list format)."""
        result = [1.0, 0.0, 0.0, 0.0]
        assert np.isclose(calculate_expectation(result, "ZZ"), 1.0)

    def test_zz_on_product_state_01_list(self):
        """ZZ on |01> = -1 (list format)."""
        result = [0.0, 1.0, 0.0, 0.0]
        assert np.isclose(calculate_expectation(result, "ZZ"), -1.0)

    # -------------------------------------------------------------------------
    # Lowercase z/i
    # -------------------------------------------------------------------------
    def test_lowercase_z(self):
        """Lowercase 'z' is treated same as 'Z'."""
        result = {"0": 1.0}
        assert np.isclose(calculate_expectation(result, "z"), 1.0)

    def test_lowercase_z_on_one(self):
        """Lowercase 'z' on |1> = -1."""
        result = {"1": 1.0}
        assert np.isclose(calculate_expectation(result, "z"), -1.0)

    def test_mixed_case_zZ(self):
        """Mixed 'zZ' on |0> = +1 (z on q0=0, Z on q1=0)."""
        result = {"00": 1.0}
        assert np.isclose(calculate_expectation(result, "zZ"), 1.0)

    # -------------------------------------------------------------------------
    # List of hamiltonians
    # -------------------------------------------------------------------------
    def test_list_of_hamiltonians(self):
        """Passing a list of Hamiltonians returns a list of results."""
        result = {"00": 0.5, "11": 0.5}
        out = calculate_expectation(result, ["ZZ", "ZI", "IZ", "II"])
        assert isinstance(out, list)
        assert len(out) == 4
        assert np.isclose(out[0], 1.0)
        assert np.isclose(out[1], 0.0)
        assert np.isclose(out[2], 0.0)
        assert np.isclose(out[3], 1.0)

    def test_list_of_hamiltonians_empty(self):
        """Empty list of Hamiltonians returns empty list."""
        result = {"0": 1.0}
        out = calculate_expectation(result, [])
        assert out == []

    def test_list_of_hamiltonians_mixed_case(self):
        """List of Hamiltonians with mixed case works."""
        result = {"0": 1.0}
        out = calculate_expectation(result, ["Z", "z", "I"])
        assert np.isclose(out[0], 1.0)
        assert np.isclose(out[1], 1.0)
        assert np.isclose(out[2], 1.0)

    # -------------------------------------------------------------------------
    # Boundary: single qubit
    # -------------------------------------------------------------------------
    def test_single_qubit_various_states(self):
        """Single qubit: test |0>, |1>, |+>, |->."""
        assert np.isclose(calculate_expectation({"0": 1.0}, "Z"), 1.0)
        assert np.isclose(calculate_expectation({"1": 1.0}, "Z"), -1.0)
        assert np.isclose(calculate_expectation({"0": 0.5, "1": 0.5}, "Z"), 0.0)

    # -------------------------------------------------------------------------
    # Boundary: 3+ qubits
    # -------------------------------------------------------------------------
    def test_three_qubit_zzz_on_000(self):
        """ZZZ on |000> = +1."""
        result = {"000": 1.0}
        assert np.isclose(calculate_expectation(result, "ZZZ"), 1.0)

    def test_three_qubit_zzz_on_001(self):
        """ZZZ on |001> = -1 (one qubit flipped)."""
        result = {"001": 1.0}
        assert np.isclose(calculate_expectation(result, "ZZZ"), -1.0)

    def test_three_qubit_zzz_on_011(self):
        """ZZZ on |011> = +1 (two qubits flipped: (+)(+)(-)=+)."""
        result = {"011": 1.0}
        assert np.isclose(calculate_expectation(result, "ZZZ"), 1.0)

    def test_three_qubit_zzz_on_111(self):
        """ZZZ on |111> = -1 (three qubits flipped)."""
        result = {"111": 1.0}
        assert np.isclose(calculate_expectation(result, "ZZZ"), -1.0)

    def test_three_qubit_zzi(self):
        """ZZI on |000> = +1, on |101> = -1."""
        assert np.isclose(calculate_expectation({"000": 1.0}, "ZZI"), 1.0)
        assert np.isclose(calculate_expectation({"001": 1.0}, "ZZI"), 1.0)
        assert np.isclose(calculate_expectation({"101": 1.0}, "ZZI"), -1.0)


# =============================================================================
# TestCalculateExpX
# =============================================================================
class TestCalculateExpX:
    """Tests for calculate_exp_X.

    Note: calculate_exp_X/Y work with any dict keys, but the key at
    qubit_index must be '0' or '1' for meaningful results. Non-bit chars
    are treated as '1' (adds negative sign).
    """

    def test_plus_state_x_expectation(self):
        """X on |+> = +1. After H rotation: always measures |0>."""
        result = {"0": 1.0}
        assert np.isclose(calculate_exp_X(result, nqubit=1), 1.0)

    def test_minus_state_x_expectation(self):
        """X on |-> = -1. After H rotation: always measures |1>."""
        result = {"1": 1.0}
        assert np.isclose(calculate_exp_X(result, nqubit=1), -1.0)

    def test_zero_state_x_expectation(self):
        """X on |0> = 0. After H: equal superposition, 50/50."""
        result = {"0": 0.5, "1": 0.5}
        assert np.isclose(calculate_exp_X(result, nqubit=1), 0.0)

    def test_one_state_x_expectation(self):
        """X on |1> = 0. After H: equal superposition, 50/50."""
        result = {"0": 0.5, "1": 0.5}
        assert np.isclose(calculate_exp_X(result, nqubit=1), 0.0)

    # -------------------------------------------------------------------------
    # List input format
    # -------------------------------------------------------------------------
    def test_plus_state_list(self):
        """X on |+> = +1 (list format [P(0), P(1)] = [1, 0])."""
        result = [1.0, 0.0]
        assert np.isclose(calculate_exp_X(result, nqubit=1), 1.0)

    def test_minus_state_list(self):
        """X on |-> = -1 (list format [0, 1])."""
        result = [0.0, 1.0]
        assert np.isclose(calculate_exp_X(result, nqubit=1), -1.0)

    def test_zero_state_list(self):
        """X on |0> = 0 (list format [0.5, 0.5])."""
        result = [0.5, 0.5]
        assert np.isclose(calculate_exp_X(result, nqubit=1), 0.0)

    # -------------------------------------------------------------------------
    # qubit_index on multi-qubit results (using computational basis keys)
    # -------------------------------------------------------------------------
    def test_bell_state_individual_x(self):
        """Bell state |Phi+>: individual <X> = 0 for each qubit.

        After H on one qubit: |Phi+> -> (|00>+|11>)/sqrt(2).
        The measured qubit (q0) is 0 when outcome is '00' and 1 when '11'.
        So P(q0=0)=0.5, P(q0=1)=0.5 -> <X> = 0.
        """
        result = {"00": 0.5, "11": 0.5}
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=0), 0.0)
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=1), 0.0)

    def test_product_state_00_individual_x(self):
        """<X> on |00> after H on both: always +1 for each qubit."""
        # |00> after H on both -> |++> always -> bit 0 = '0', bit 1 = '0'
        result = {"00": 1.0}
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=0), 1.0)
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=1), 1.0)

    def test_product_state_01_individual_x(self):
        """<X> on |01>: qubit 0 = 0 (50% each), qubit 1 = always 1 -> -1."""
        # |01> after H on q0: (|01>+|11>)/sqrt(2). Qubit 0: 50% 0, 50% 1.
        # Qubit 1: always 1.
        result = {"01": 0.5, "11": 0.5}
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=0), 0.0)
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=1), -1.0)

    def test_product_state_10_individual_x(self):
        """<X> on |10>: qubit 0 = 50% 0/1, qubit 1 = always 0 -> +1."""
        # |10> after H on q0: (|00>-|10>)/sqrt(2). Qubit 0: 50% 0, 50% 1.
        # Qubit 1: always 0.
        result = {"00": 0.5, "10": 0.5}
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=0), 0.0)
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=1), 1.0)

    def test_product_state_11_individual_x(self):
        """<X> on |11>: both qubits always 1 -> <X> = -1 each after H."""
        # |11> after H on both -> |--> always -> bit 0 = '1', bit 1 = '1'
        result = {"11": 1.0}
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=0), -1.0)
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=1), -1.0)

    # -------------------------------------------------------------------------
    # List format on multi-qubit
    # -------------------------------------------------------------------------
    def test_product_state_00_list(self):
        """<X> on |00> (list format [P(00), P(01), P(10), P(11)])."""
        # |00> after H on both -> |++> always. List index 0 (="00") = 1.0
        result = [1.0, 0.0, 0.0, 0.0]
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=0), 1.0)
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=1), 1.0)

    def test_product_state_11_list(self):
        """<X> on |11> (list format)."""
        # |11> after H on both -> |--> always. List index 3 (="11") = 1.0
        result = [0.0, 0.0, 0.0, 1.0]
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=0), -1.0)
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=1), -1.0)

    def test_bell_state_list(self):
        """Bell state |Phi+> in list format: individual <X> = 0."""
        # P(00)=0.5, P(11)=0.5 -> qubit 0: 50% 0, 50% 1 -> 0
        result = [0.5, 0.0, 0.0, 0.5]
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=0), 0.0)
        assert np.isclose(calculate_exp_X(result, nqubit=2, qubit_index=1), 0.0)

    # -------------------------------------------------------------------------
    # Default qubit_index = 0
    # -------------------------------------------------------------------------
    def test_default_qubit_index(self):
        """Default qubit_index=0 works correctly."""
        result = {"0": 1.0}
        assert np.isclose(calculate_exp_X(result, nqubit=1), 1.0)
        # For qubit_index=0 on 2-qubit Bell: P(bit0=0) from "00"+"10" - P(bit0=1) from "01"+"11"
        # = 0.5 - 0.5 = 0
        result2 = {"00": 0.5, "11": 0.5}
        assert np.isclose(calculate_exp_X(result2, nqubit=2), 0.0)

    # -------------------------------------------------------------------------
    # Edge: non-'0'/'1' key chars (treated as '1')
    # -------------------------------------------------------------------------
    def test_non_bit_chars_treated_as_one(self):
        """Non-'0'/'1' chars in key at qubit_index are treated as '1' (subtract prob)."""
        # '+' is not '0', so treated as '1' -> subtract prob
        result = {"+": 1.0}
        assert np.isclose(calculate_exp_X(result, nqubit=1), -1.0)

        result2 = {"0": 0.5, "+": 0.5}
        assert np.isclose(calculate_exp_X(result2, nqubit=1), 0.0)  # 0.5 - 0.5 = 0


# =============================================================================
# TestCalculateExpY
# =============================================================================
class TestCalculateExpY:
    """Tests for calculate_exp_Y.

    Same formula as X: <Y_k> = P(bit_k=0) - P(bit_k=1).
    The difference is in the circuit rotation (S\\dagger H instead of H).
    """

    def test_plusi_state_y_expectation(self):
        """Y on |+i> = +1. After Sdg H rotation: always measures |0>."""
        result = {"0": 1.0}
        assert np.isclose(calculate_exp_Y(result, nqubit=1), 1.0)

    def test_minusi_state_y_expectation(self):
        """Y on |-i> = -1. After Sdg H rotation: always measures |1>."""
        result = {"1": 1.0}
        assert np.isclose(calculate_exp_Y(result, nqubit=1), -1.0)

    def test_zero_state_y_expectation(self):
        """Y on |0> = 0 (after Sdg H: 50/50)."""
        result = {"0": 0.5, "1": 0.5}
        assert np.isclose(calculate_exp_Y(result, nqubit=1), 0.0)

    def test_one_state_y_expectation(self):
        """Y on |1> = 0 (after Sdg H: 50/50)."""
        result = {"0": 0.5, "1": 0.5}
        assert np.isclose(calculate_exp_Y(result, nqubit=1), 0.0)

    # -------------------------------------------------------------------------
    # List input format
    # -------------------------------------------------------------------------
    def test_plusi_state_list(self):
        """Y on |+i> = +1 (list format)."""
        result = [1.0, 0.0]
        assert np.isclose(calculate_exp_Y(result, nqubit=1), 1.0)

    def test_minusi_state_list(self):
        """Y on |-i> = -1 (list format)."""
        result = [0.0, 1.0]
        assert np.isclose(calculate_exp_Y(result, nqubit=1), -1.0)

    def test_zero_state_list(self):
        """Y on |0> = 0 (list format)."""
        result = [0.5, 0.5]
        assert np.isclose(calculate_exp_Y(result, nqubit=1), 0.0)

    # -------------------------------------------------------------------------
    # qubit_index on multi-qubit results
    # -------------------------------------------------------------------------
    def test_bell_state_individual_y(self):
        """Bell state |Phi+>: individual <Y> = 0 for each qubit."""
        result = {"00": 0.5, "11": 0.5}
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=0), 0.0)
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=1), 0.0)

    def test_product_state_00_individual_y(self):
        """<Y> on |00> after Sdg H on both: always +1 for each qubit."""
        result = {"00": 1.0}
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=0), 1.0)
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=1), 1.0)

    def test_product_state_01_individual_y(self):
        """<Y> on |01>: qubit 0 = 50/50, qubit 1 = always 1 -> -1."""
        result = {"01": 0.5, "11": 0.5}
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=0), 0.0)
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=1), -1.0)

    def test_product_state_10_individual_y(self):
        """<Y> on |10>: qubit 0 = 50/50, qubit 1 = always 0 -> +1."""
        result = {"00": 0.5, "10": 0.5}
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=0), 0.0)
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=1), 1.0)

    def test_product_state_11_individual_y(self):
        """<Y> on |11>: both qubits always 1 -> <Y> = -1 each after Sdg H."""
        result = {"11": 1.0}
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=0), -1.0)
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=1), -1.0)

    # -------------------------------------------------------------------------
    # List format on multi-qubit
    # -------------------------------------------------------------------------
    def test_product_state_00_list(self):
        """<Y> on |00> (list format)."""
        result = [1.0, 0.0, 0.0, 0.0]
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=0), 1.0)
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=1), 1.0)

    def test_product_state_11_list(self):
        """<Y> on |11> (list format)."""
        result = [0.0, 0.0, 0.0, 1.0]
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=0), -1.0)
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=1), -1.0)

    def test_bell_state_list(self):
        """Bell state in list format: individual <Y> = 0."""
        result = [0.5, 0.0, 0.0, 0.5]
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=0), 0.0)
        assert np.isclose(calculate_exp_Y(result, nqubit=2, qubit_index=1), 0.0)

    # -------------------------------------------------------------------------
    # Default qubit_index = 0
    # -------------------------------------------------------------------------
    def test_default_qubit_index(self):
        """Default qubit_index=0 works correctly."""
        result = {"0": 1.0}
        assert np.isclose(calculate_exp_Y(result, nqubit=1), 1.0)
        result2 = {"00": 0.5, "11": 0.5}
        assert np.isclose(calculate_exp_Y(result2, nqubit=2), 0.0)

    # -------------------------------------------------------------------------
    # Edge: non-'0'/'1' key chars
    # -------------------------------------------------------------------------
    def test_non_bit_chars_treated_as_one(self):
        """Non-'0'/'1' chars in key at qubit_index are treated as '1'."""
        result = {"+": 1.0}
        assert np.isclose(calculate_exp_Y(result, nqubit=1), -1.0)

        result2 = {"0": 0.5, "+": 0.5}
        assert np.isclose(calculate_exp_Y(result2, nqubit=1), 0.0)


# =============================================================================
# TestCalculateMultiBasisExpectation
# =============================================================================
class TestCalculateMultiBasisExpectation:
    """Tests for calculate_multi_basis_expectation."""

    def test_single_qubit_z_basis(self):
        """Z basis on |0> gives <Z> = +1."""
        z_result = {"0": 1.0}
        out = calculate_multi_basis_expectation({"Z": z_result}, nqubit=1)
        assert np.isclose(out["Z"], 1.0)

    def test_single_qubit_z_basis_one(self):
        """Z basis on |1> gives <Z> = -1."""
        z_result = {"1": 1.0}
        out = calculate_multi_basis_expectation({"Z": z_result}, nqubit=1)
        assert np.isclose(out["Z"], -1.0)

    def test_single_qubit_x_basis(self):
        """X basis on |+> gives <X> = +1."""
        x_result = {"0": 1.0}
        out = calculate_multi_basis_expectation({"X": x_result}, nqubit=1)
        assert np.isclose(out["X"], 1.0)

    def test_single_qubit_y_basis(self):
        """Y basis on |+i> gives <Y> = +1."""
        y_result = {"0": 1.0}
        out = calculate_multi_basis_expectation({"Y": y_result}, nqubit=1)
        assert np.isclose(out["Y"], 1.0)

    def test_zxz_dispatch(self):
        """X/Y/Z dispatching: |0> in Z=<Z>=1, X=<X>=0, Y=<Y>=0."""
        out = calculate_multi_basis_expectation(
            {
                "Z": {"0": 1.0},
                "X": {"0": 0.5, "1": 0.5},
                "Y": {"0": 0.5, "1": 0.5},
            },
            nqubit=1,
        )
        assert np.isclose(out["Z"], 1.0)
        assert np.isclose(out["X"], 0.0)
        assert np.isclose(out["Y"], 0.0)

    def test_bell_state_z_basis(self):
        """|Phi+> in Z basis: <ZZ> = +1."""
        z_result = {"00": 0.5, "11": 0.5}
        out = calculate_multi_basis_expectation({"Z": z_result}, nqubit=2)
        assert np.isclose(out["Z"], 1.0)

    def test_bell_state_individual_x(self):
        """|Phi+> in X basis (H on both): individual <X> = 0 for each qubit.

        After H on both qubits of |Phi+>, the measurement outcomes are
        |00> and |11> each with 50% (in computational basis representation).
        Qubit 0: P(0)=0.5, P(1)=0.5 -> <X> = 0.
        """
        x_result = {"00": 0.5, "11": 0.5}
        out = calculate_multi_basis_expectation({"X": x_result}, nqubit=2)
        assert np.isclose(out["X"], 0.0)

    def test_bell_state_individual_y(self):
        """|Phi+> in Y basis (Sdg H on both): individual <Y> = 0 for each qubit."""
        y_result = {"00": 0.5, "11": 0.5}
        out = calculate_multi_basis_expectation({"Y": y_result}, nqubit=2)
        assert np.isclose(out["Y"], 0.0)

    def test_product_state_00_xyz(self):
        """|00>: <Z*Z> = +1, individual <X> = +1, individual <Y> = +1."""
        z_result = {"00": 1.0}
        x_result = {"00": 1.0}  # H on both -> |00> (still |00> in comp basis)
        y_result = {"00": 1.0}  # Sdg H on both -> |00>
        out = calculate_multi_basis_expectation(
            {"Z": z_result, "X": x_result, "Y": y_result}, nqubit=2
        )
        assert np.isclose(out["Z"], 1.0)
        assert np.isclose(out["X"], 1.0)
        assert np.isclose(out["Y"], 1.0)

    def test_product_state_11_xyz(self):
        """|11>: <Z*Z> = +1, individual <X> = -1, individual <Y> = -1."""
        z_result = {"11": 1.0}
        x_result = {"11": 1.0}  # H on both -> |-->, key still "11"
        y_result = {"11": 1.0}  # Sdg H on both -> |-->, key still "11"
        out = calculate_multi_basis_expectation(
            {"Z": z_result, "X": x_result, "Y": y_result}, nqubit=2
        )
        assert np.isclose(out["Z"], 1.0)
        assert np.isclose(out["X"], -1.0)
        assert np.isclose(out["Y"], -1.0)

    def test_case_insensitive_labels(self):
        """Basis labels are case-insensitive (x=X, y=Y, z=Z)."""
        out = calculate_multi_basis_expectation(
            {"z": {"0": 1.0}, "x": {"0": 1.0}, "y": {"0": 1.0}}, nqubit=1
        )
        assert np.isclose(out["z"], 1.0)
        assert np.isclose(out["x"], 1.0)
        assert np.isclose(out["y"], 1.0)

    def test_custom_label_uses_z(self):
        """Custom labels not starting with X/Y fall back to Z with ZZ...Z."""
        result = {"00": 1.0}
        out = calculate_multi_basis_expectation({"custom": result}, nqubit=2)
        assert np.isclose(out["custom"], 1.0)  # ZZ on |00> = +1

    def test_multiple_custom_labels(self):
        """Multiple custom labels all treated as Z (ZZZ...Z Hamiltonian)."""
        result = {"000": 1.0}
        out = calculate_multi_basis_expectation(
            {"foo": result, "bar": result}, nqubit=3
        )
        assert np.isclose(out["foo"], 1.0)
        assert np.isclose(out["bar"], 1.0)

    def test_mixed_x_labels(self):
        """X, X0, X1 all dispatched to calculate_exp_X."""
        result = {"0": 1.0}
        out = calculate_multi_basis_expectation(
            {"X": result, "X0": result, "X1": result}, nqubit=1
        )
        assert np.isclose(out["X"], 1.0)
        assert np.isclose(out["X0"], 1.0)
        assert np.isclose(out["X1"], 1.0)

    def test_mixed_y_labels(self):
        """Y and Y0 both dispatched to calculate_exp_Y."""
        result = {"0": 1.0}
        out = calculate_multi_basis_expectation(
            {"Y": result, "Y0": result}, nqubit=1
        )
        assert np.isclose(out["Y"], 1.0)
        assert np.isclose(out["Y0"], 1.0)

    def test_list_format_in_measured_results(self):
        """measured_results can contain list-format inputs for all bases."""
        out = calculate_multi_basis_expectation(
            {"Z": [1.0, 0.0], "X": [1.0, 0.0], "Y": [1.0, 0.0]}, nqubit=1
        )
        assert np.isclose(out["Z"], 1.0)
        assert np.isclose(out["X"], 1.0)
        assert np.isclose(out["Y"], 1.0)

    def test_empty_measured_results(self):
        """Empty measured_results returns empty dict."""
        out = calculate_multi_basis_expectation({}, nqubit=1)
        assert out == {}

    def test_three_qubit_zzz_on_000(self):
        """3-qubit Z basis on |000>: <ZZZ> = +1."""
        result = {"000": 1.0}
        out = calculate_multi_basis_expectation({"Z": result}, nqubit=3)
        assert np.isclose(out["Z"], 1.0)

    def test_three_qubit_zzz_on_001(self):
        """3-qubit Z basis on |001>: <ZZZ> = -1."""
        result = {"001": 1.0}
        out = calculate_multi_basis_expectation({"Z": result}, nqubit=3)
        assert np.isclose(out["Z"], -1.0)

    def test_xz_yz_combined(self):
        """X, Z, and Y bases together on |00>."""
        z_result = {"00": 1.0}
        x_result = {"00": 1.0}  # H on both -> still |00>
        y_result = {"00": 1.0}  # Sdg H on both -> still |00>
        out = calculate_multi_basis_expectation(
            {"Z": z_result, "X": x_result, "Y": y_result}, nqubit=2
        )
        assert np.isclose(out["Z"], 1.0)
        assert np.isclose(out["X"], 1.0)
        assert np.isclose(out["Y"], 1.0)

    def test_xy_on_separate_bell_components(self):
        """X and Y results can be different dicts (different measurement setups)."""
        z_result = {"00": 0.5, "11": 0.5}
        # X basis: H on both, outcomes |00> and |11> -> each qubit 50/50
        x_result = {"00": 0.5, "11": 0.5}
        # Y basis: Sdg H on both -> same outcomes
        y_result = {"00": 0.5, "11": 0.5}
        out = calculate_multi_basis_expectation(
            {"Z": z_result, "X": x_result, "Y": y_result}, nqubit=2
        )
        assert np.isclose(out["Z"], 1.0)
        assert np.isclose(out["X"], 0.0)
        assert np.isclose(out["Y"], 0.0)
