"""
Unit tests for circuit_builder specification files.

Covers:
  - qpandalite/circuit_builder/qasm_spec.py
  - qpandalite/circuit_builder/originir_spec.py

Tests are pure data-structure assertions; no simulator is needed.
"""

import pytest
from qpandalite.circuit_builder.qasm_spec import (
    available_qasm_gates,
    generate_sub_gateset_qasm,
    available_qasm_1q_gates,
    available_qasm_1q1p_gates,
    available_qasm_1q2p_gates,
    available_qasm_1q3p_gates,
    available_qasm_2q_gates,
    available_qasm_3q_gates,
    available_qasm_4q_gates,
    available_qasm_2q1p_gates,
)
from qpandalite.circuit_builder.originir_spec import (
    available_originir_gates,
    angular_gates,
    available_originir_error_channels,
    available_originir_error_channels_without_kraus,
    generate_sub_gateset_originir,
    generate_sub_error_channel_originir,
    available_originir_1q_gates,
    available_originir_1q1p_gates,
    available_originir_1q2p_gates,
    available_originir_1q3p_gates,
    available_originir_2q_gates,
    available_originir_2q1p_gates,
    available_originir_2q3p_gates,
    available_originir_2q15p_gates,
    available_originir_3p_gates,
    available_barrier_gates,
    available_originir_error_channel_1q1p,
    available_originir_error_channel_1q3p,
    available_originir_error_channel_1qnp,
    available_originir_error_channel_2q1p,
    available_originir_error_channel_2q15p,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assert_gate_entry(gate_dict, gate_name, expected_qubit, expected_params_key, expected_params_value):
    """Assert a single gate entry has the correct structure and values."""
    assert gate_name in gate_dict, f"Gate '{gate_name}' not found in dict"
    entry = gate_dict[gate_name]
    assert isinstance(entry, dict), f"Entry for '{gate_name}' is not a dict"
    assert 'qubit' in entry, f"'qubit' key missing for gate '{gate_name}'"
    assert expected_params_key in entry, f"'{expected_params_key}' key missing for gate '{gate_name}'"
    assert entry['qubit'] == expected_qubit, (
        f"Gate '{gate_name}': expected qubit={expected_qubit}, got {entry['qubit']}"
    )
    assert entry[expected_params_key] == expected_params_value, (
        f"Gate '{gate_name}': expected {expected_params_key}={expected_params_value}, "
        f"got {entry[expected_params_key]}"
    )


# ===========================================================================
# QASM Spec Tests
# ===========================================================================

class TestQASMSpecStructure:
    """Tests for the top-level structure of available_qasm_gates."""

    def test_available_qasm_gates_is_dict(self):
        assert isinstance(available_qasm_gates, dict)

    def test_available_qasm_gates_not_empty(self):
        assert len(available_qasm_gates) > 0

    def test_every_entry_is_dict(self):
        for name, entry in available_qasm_gates.items():
            assert isinstance(entry, dict), f"Entry for '{name}' is not a dict"

    def test_every_entry_has_qubit_key(self):
        for name, entry in available_qasm_gates.items():
            assert 'qubit' in entry, f"'qubit' key missing for gate '{name}'"

    def test_every_entry_has_params_key(self):
        for name, entry in available_qasm_gates.items():
            assert 'params' in entry, f"'params' key missing for gate '{name}'"

    def test_qubit_values_are_positive_integers(self):
        for name, entry in available_qasm_gates.items():
            assert isinstance(entry['qubit'], int), f"'qubit' is not int for '{name}'"
            assert entry['qubit'] > 0, f"'qubit' is not positive for '{name}'"

    def test_params_values_are_non_negative_integers(self):
        for name, entry in available_qasm_gates.items():
            assert isinstance(entry['params'], int), f"'params' is not int for '{name}'"
            assert entry['params'] >= 0, f"'params' is negative for '{name}'"

    def test_keys_are_strings(self):
        for name in available_qasm_gates:
            assert isinstance(name, str), f"Gate key '{name}' is not a string"


class TestQASMGateCoverage:
    """Tests that all gate lists are present in available_qasm_gates."""

    def test_1q_gates_present(self):
        for gate in available_qasm_1q_gates:
            assert gate in available_qasm_gates, f"1q gate '{gate}' missing"

    def test_1q1p_gates_present(self):
        for gate in available_qasm_1q1p_gates:
            assert gate in available_qasm_gates, f"1q1p gate '{gate}' missing"

    def test_1q2p_gates_present(self):
        for gate in available_qasm_1q2p_gates:
            assert gate in available_qasm_gates, f"1q2p gate '{gate}' missing"

    def test_1q3p_gates_present(self):
        for gate in available_qasm_1q3p_gates:
            assert gate in available_qasm_gates, f"1q3p gate '{gate}' missing"

    def test_2q_gates_present(self):
        for gate in available_qasm_2q_gates:
            assert gate in available_qasm_gates, f"2q gate '{gate}' missing"

    def test_3q_gates_present(self):
        for gate in available_qasm_3q_gates:
            assert gate in available_qasm_gates, f"3q gate '{gate}' missing"

    def test_4q_gates_present(self):
        for gate in available_qasm_4q_gates:
            assert gate in available_qasm_gates, f"4q gate '{gate}' missing"

    def test_2q1p_gates_present(self):
        for gate in available_qasm_2q1p_gates:
            assert gate in available_qasm_gates, f"2q1p gate '{gate}' missing"

    # Spot-check specific well-known gates
    def test_common_gates_present(self):
        common = ['id', 'h', 'x', 'y', 'z', 's', 'sx', 't',
                  'cx', 'cz', 'swap', 'ccx', 'rx', 'ry', 'rz',
                  'u1', 'u2', 'u3', 'rxx', 'rzz']
        for gate in common:
            assert gate in available_qasm_gates, f"Common gate '{gate}' missing"


class TestQASMGateValues:
    """Tests for correct qubit/params values for each gate category."""

    def test_1q_gates_have_qubit1_params0(self):
        for gate in available_qasm_1q_gates:
            _assert_gate_entry(available_qasm_gates, gate, 1, 'params', 0)

    def test_1q1p_gates_have_qubit1_params1(self):
        for gate in available_qasm_1q1p_gates:
            _assert_gate_entry(available_qasm_gates, gate, 1, 'params', 1)

    def test_1q2p_gates_have_qubit1_params2(self):
        for gate in available_qasm_1q2p_gates:
            _assert_gate_entry(available_qasm_gates, gate, 1, 'params', 2)

    def test_1q3p_gates_have_qubit1_params3(self):
        for gate in available_qasm_1q3p_gates:
            _assert_gate_entry(available_qasm_gates, gate, 1, 'params', 3)

    def test_2q_gates_have_qubit2_params0(self):
        for gate in available_qasm_2q_gates:
            _assert_gate_entry(available_qasm_gates, gate, 2, 'params', 0)

    def test_3q_gates_have_qubit3_params0(self):
        for gate in available_qasm_3q_gates:
            _assert_gate_entry(available_qasm_gates, gate, 3, 'params', 0)

    def test_4q_gates_have_qubit4_params0(self):
        for gate in available_qasm_4q_gates:
            _assert_gate_entry(available_qasm_gates, gate, 4, 'params', 0)

    def test_2q1p_gates_have_qubit2_params1(self):
        for gate in available_qasm_2q1p_gates:
            _assert_gate_entry(available_qasm_gates, gate, 2, 'params', 1)

    # Spot-check individual gates
    def test_h_gate(self):
        _assert_gate_entry(available_qasm_gates, 'h', 1, 'params', 0)

    def test_cx_gate(self):
        _assert_gate_entry(available_qasm_gates, 'cx', 2, 'params', 0)

    def test_ccx_gate(self):
        _assert_gate_entry(available_qasm_gates, 'ccx', 3, 'params', 0)

    def test_rx_gate(self):
        _assert_gate_entry(available_qasm_gates, 'rx', 1, 'params', 1)

    def test_u2_gate(self):
        _assert_gate_entry(available_qasm_gates, 'u2', 1, 'params', 2)

    def test_u3_gate(self):
        _assert_gate_entry(available_qasm_gates, 'u3', 1, 'params', 3)

    def test_rxx_gate(self):
        _assert_gate_entry(available_qasm_gates, 'rxx', 2, 'params', 1)

    def test_rzz_gate(self):
        _assert_gate_entry(available_qasm_gates, 'rzz', 2, 'params', 1)


class TestGenerateSubGatesetQasm:
    """Tests for generate_sub_gateset_qasm."""

    def test_returns_dict(self):
        result = generate_sub_gateset_qasm(['h', 'cx'])
        assert isinstance(result, dict)

    def test_returns_only_requested_gates(self):
        gate_list = ['h', 'cx', 'rx']
        result = generate_sub_gateset_qasm(gate_list)
        assert set(result.keys()) == set(gate_list)

    def test_values_match_original(self):
        gate_list = ['h', 'cx', 'rx']
        result = generate_sub_gateset_qasm(gate_list)
        for gate in gate_list:
            assert result[gate] == available_qasm_gates[gate]

    def test_empty_list_returns_empty_dict(self):
        result = generate_sub_gateset_qasm([])
        assert result == {}

    def test_single_gate(self):
        result = generate_sub_gateset_qasm(['ccx'])
        assert result == {'ccx': available_qasm_gates['ccx']}

    def test_unknown_gate_not_in_result(self):
        result = generate_sub_gateset_qasm(['h', 'nonexistent_gate'])
        assert 'nonexistent_gate' not in result
        assert 'h' in result

    def test_all_gates_subset(self):
        all_keys = list(available_qasm_gates.keys())
        result = generate_sub_gateset_qasm(all_keys)
        assert result == available_qasm_gates

    def test_does_not_mutate_original(self):
        original_copy = dict(available_qasm_gates)
        generate_sub_gateset_qasm(['h', 'cx'])
        assert available_qasm_gates == original_copy

    def test_result_has_correct_structure(self):
        result = generate_sub_gateset_qasm(['rx', 'cz'])
        for name, entry in result.items():
            assert 'qubit' in entry
            assert 'params' in entry

    def test_no_error_for_valid_comprehensive_list(self):
        gate_list = ['id', 'h', 'x', 'y', 'z', 's', 'sx', 't',
                     'cx', 'cz', 'swap', 'ccx', 'rx', 'ry', 'rz',
                     'u1', 'u2', 'u3', 'rxx', 'rzz', 'c3x']
        # Should not raise
        result = generate_sub_gateset_qasm(gate_list)
        assert isinstance(result, dict)


# ===========================================================================
# OriginIR Spec Tests
# ===========================================================================

class TestOriginIRGatesStructure:
    """Tests for the top-level structure of available_originir_gates."""

    def test_available_originir_gates_is_dict(self):
        assert isinstance(available_originir_gates, dict)

    def test_available_originir_gates_not_empty(self):
        assert len(available_originir_gates) > 0

    def test_every_entry_is_dict(self):
        for name, entry in available_originir_gates.items():
            assert isinstance(entry, dict), f"Entry for '{name}' is not a dict"

    def test_every_entry_has_qubit_key(self):
        for name, entry in available_originir_gates.items():
            assert 'qubit' in entry, f"'qubit' key missing for gate '{name}'"

    def test_every_entry_has_param_key(self):
        # OriginIR uses 'param' (singular) unlike QASM's 'params'
        for name, entry in available_originir_gates.items():
            assert 'param' in entry, f"'param' key missing for gate '{name}'"

    def test_qubit_values_are_integers(self):
        for name, entry in available_originir_gates.items():
            assert isinstance(entry['qubit'], int), f"'qubit' is not int for '{name}'"

    def test_param_values_are_integers(self):
        for name, entry in available_originir_gates.items():
            assert isinstance(entry['param'], int), f"'param' is not int for '{name}'"

    def test_keys_are_strings(self):
        for name in available_originir_gates:
            assert isinstance(name, str), f"Gate key '{name}' is not a string"

    def test_no_params_key_present(self):
        # OriginIR uses 'param' not 'params'; verify no accidental 'params' key
        for name, entry in available_originir_gates.items():
            assert 'params' not in entry, (
                f"Gate '{name}' has unexpected 'params' key (should be 'param')"
            )


class TestOriginIRGateCoverage:
    """Tests that all OriginIR gate lists appear in available_originir_gates."""

    def test_1q_gates_present(self):
        for gate in available_originir_1q_gates:
            assert gate in available_originir_gates, f"1q gate '{gate}' missing"

    def test_1q1p_gates_present(self):
        for gate in available_originir_1q1p_gates:
            assert gate in available_originir_gates, f"1q1p gate '{gate}' missing"

    def test_1q2p_gates_present(self):
        for gate in available_originir_1q2p_gates:
            assert gate in available_originir_gates, f"1q2p gate '{gate}' missing"

    @pytest.mark.xfail(
        reason="BUG: available_originir_1q3p_gates (e.g. 'U3') is defined but "
               "never added to available_originir_gates in originir_spec.py"
    )
    def test_1q3p_gates_present(self):
        for gate in available_originir_1q3p_gates:
            assert gate in available_originir_gates, f"1q3p gate '{gate}' missing"

    def test_2q_gates_present(self):
        for gate in available_originir_2q_gates:
            assert gate in available_originir_gates, f"2q gate '{gate}' missing"

    def test_2q1p_gates_present(self):
        for gate in available_originir_2q1p_gates:
            assert gate in available_originir_gates, f"2q1p gate '{gate}' missing"

    def test_2q3p_gates_present(self):
        for gate in available_originir_2q3p_gates:
            assert gate in available_originir_gates, f"2q3p gate '{gate}' missing"

    def test_2q15p_gates_present(self):
        for gate in available_originir_2q15p_gates:
            assert gate in available_originir_gates, f"2q15p gate '{gate}' missing"

    def test_3q_gates_present(self):
        for gate in available_originir_3p_gates:
            assert gate in available_originir_gates, f"3q gate '{gate}' missing"

    def test_barrier_gate_present(self):
        for gate in available_barrier_gates:
            assert gate in available_originir_gates, f"Barrier gate '{gate}' missing"


class TestOriginIRGateValues:
    """Tests for correct qubit/param values in available_originir_gates."""

    def test_1q_gates_have_qubit1_param0(self):
        for gate in available_originir_1q_gates:
            _assert_gate_entry(available_originir_gates, gate, 1, 'param', 0)

    def test_1q1p_gates_have_qubit1_param1(self):
        for gate in available_originir_1q1p_gates:
            _assert_gate_entry(available_originir_gates, gate, 1, 'param', 1)

    def test_1q2p_gates_have_qubit1_param2(self):
        for gate in available_originir_1q2p_gates:
            _assert_gate_entry(available_originir_gates, gate, 1, 'param', 2)

    @pytest.mark.xfail(
        reason="BUG: 'U3' in available_originir_1q3p_gates is absent from "
               "available_originir_gates (update block missing in originir_spec.py)"
    )
    def test_1q3p_gates_have_qubit1_param3(self):
        for gate in available_originir_1q3p_gates:
            _assert_gate_entry(available_originir_gates, gate, 1, 'param', 3)

    def test_2q_gates_have_qubit2_param0(self):
        for gate in available_originir_2q_gates:
            _assert_gate_entry(available_originir_gates, gate, 2, 'param', 0)

    def test_2q1p_gates_have_qubit2_param1(self):
        for gate in available_originir_2q1p_gates:
            _assert_gate_entry(available_originir_gates, gate, 2, 'param', 1)

    def test_2q3p_gates_have_qubit2_param3(self):
        for gate in available_originir_2q3p_gates:
            _assert_gate_entry(available_originir_gates, gate, 2, 'param', 3)

    def test_2q15p_gates_have_qubit2_param15(self):
        for gate in available_originir_2q15p_gates:
            _assert_gate_entry(available_originir_gates, gate, 2, 'param', 15)

    def test_3q_gates_have_qubit3_param0(self):
        for gate in available_originir_3p_gates:
            _assert_gate_entry(available_originir_gates, gate, 3, 'param', 0)

    def test_barrier_has_qubit_minus1_param0(self):
        for gate in available_barrier_gates:
            _assert_gate_entry(available_originir_gates, gate, -1, 'param', 0)

    # Spot-check individual gates
    def test_H_gate(self):
        _assert_gate_entry(available_originir_gates, 'H', 1, 'param', 0)

    def test_CNOT_gate(self):
        _assert_gate_entry(available_originir_gates, 'CNOT', 2, 'param', 0)

    def test_RX_gate(self):
        _assert_gate_entry(available_originir_gates, 'RX', 1, 'param', 1)

    def test_RPhi_gate(self):
        _assert_gate_entry(available_originir_gates, 'RPhi', 1, 'param', 2)

    @pytest.mark.xfail(
        reason="BUG: 'U3' is absent from available_originir_gates; "
               "the 1q3p update block is missing in originir_spec.py"
    )
    def test_U3_gate(self):
        _assert_gate_entry(available_originir_gates, 'U3', 1, 'param', 3)

    def test_XX_gate(self):
        _assert_gate_entry(available_originir_gates, 'XX', 2, 'param', 1)

    def test_PHASE2Q_gate(self):
        _assert_gate_entry(available_originir_gates, 'PHASE2Q', 2, 'param', 3)

    def test_UU15_gate(self):
        _assert_gate_entry(available_originir_gates, 'UU15', 2, 'param', 15)

    def test_TOFFOLI_gate(self):
        _assert_gate_entry(available_originir_gates, 'TOFFOLI', 3, 'param', 0)

    def test_BARRIER_gate(self):
        _assert_gate_entry(available_originir_gates, 'BARRIER', -1, 'param', 0)


class TestAngularGates:
    """Tests for the angular_gates list."""

    def test_angular_gates_is_list(self):
        assert isinstance(angular_gates, list)

    def test_angular_gates_not_empty(self):
        assert len(angular_gates) > 0

    def test_angular_gates_elements_are_strings(self):
        for gate in angular_gates:
            assert isinstance(gate, str), f"'{gate}' in angular_gates is not a string"

    def test_1q1p_gates_in_angular_gates(self):
        for gate in available_originir_1q1p_gates:
            assert gate in angular_gates, f"1q1p gate '{gate}' not in angular_gates"

    def test_2q1p_gates_in_angular_gates(self):
        for gate in available_originir_2q1p_gates:
            assert gate in angular_gates, f"2q1p gate '{gate}' not in angular_gates"

    def test_1q2p_gates_in_angular_gates(self):
        for gate in available_originir_1q2p_gates:
            assert gate in angular_gates, f"1q2p gate '{gate}' not in angular_gates"

    def test_1q3p_gates_in_angular_gates(self):
        for gate in available_originir_1q3p_gates:
            assert gate in angular_gates, f"1q3p gate '{gate}' not in angular_gates"

    def test_2q3p_gates_in_angular_gates(self):
        for gate in available_originir_2q3p_gates:
            assert gate in angular_gates, f"2q3p gate '{gate}' not in angular_gates"

    def test_2q15p_gates_in_angular_gates(self):
        for gate in available_originir_2q15p_gates:
            assert gate in angular_gates, f"2q15p gate '{gate}' not in angular_gates"

    # Explicit spot-checks for documented angular gates
    def test_RX_in_angular_gates(self):
        assert 'RX' in angular_gates

    def test_RY_in_angular_gates(self):
        assert 'RY' in angular_gates

    def test_RZ_in_angular_gates(self):
        assert 'RZ' in angular_gates

    def test_U1_in_angular_gates(self):
        assert 'U1' in angular_gates

    def test_RPhi_in_angular_gates(self):
        assert 'RPhi' in angular_gates

    def test_U2_in_angular_gates(self):
        assert 'U2' in angular_gates

    def test_U3_in_angular_gates(self):
        assert 'U3' in angular_gates

    def test_XX_in_angular_gates(self):
        assert 'XX' in angular_gates

    def test_YY_in_angular_gates(self):
        assert 'YY' in angular_gates

    def test_ZZ_in_angular_gates(self):
        assert 'ZZ' in angular_gates

    def test_PHASE2Q_in_angular_gates(self):
        assert 'PHASE2Q' in angular_gates

    def test_UU15_in_angular_gates(self):
        assert 'UU15' in angular_gates

    def test_0q_gates_not_in_angular_gates(self):
        # Gates with no parameters should NOT be in angular_gates
        zero_param_gates = available_originir_1q_gates + available_originir_2q_gates + available_originir_3p_gates
        for gate in zero_param_gates:
            assert gate not in angular_gates, (
                f"Zero-param gate '{gate}' should not be in angular_gates"
            )


class TestGenerateSubGatesetOriginir:
    """Tests for generate_sub_gateset_originir."""

    def test_returns_dict(self):
        result = generate_sub_gateset_originir(['H', 'CNOT'])
        assert isinstance(result, dict)

    def test_returns_only_requested_gates(self):
        gate_list = ['H', 'CNOT', 'RX']
        result = generate_sub_gateset_originir(gate_list)
        assert set(result.keys()) == set(gate_list)

    def test_values_match_original(self):
        gate_list = ['H', 'CNOT', 'RX']
        result = generate_sub_gateset_originir(gate_list)
        for gate in gate_list:
            assert result[gate] == available_originir_gates[gate]

    def test_empty_list_returns_empty_dict(self):
        result = generate_sub_gateset_originir([])
        assert result == {}

    def test_single_gate(self):
        result = generate_sub_gateset_originir(['UU15'])
        assert result == {'UU15': available_originir_gates['UU15']}

    def test_unknown_gate_not_in_result(self):
        result = generate_sub_gateset_originir(['H', 'FAKE_GATE'])
        assert 'FAKE_GATE' not in result
        assert 'H' in result

    def test_all_gates_subset(self):
        all_keys = list(available_originir_gates.keys())
        result = generate_sub_gateset_originir(all_keys)
        assert result == available_originir_gates

    def test_does_not_mutate_original(self):
        original_copy = dict(available_originir_gates)
        generate_sub_gateset_originir(['H', 'CNOT'])
        assert available_originir_gates == original_copy

    def test_result_has_correct_structure(self):
        result = generate_sub_gateset_originir(['RX', 'CZ'])
        for name, entry in result.items():
            assert 'qubit' in entry
            assert 'param' in entry

    def test_no_error_for_valid_comprehensive_list(self):
        gate_list = ['H', 'X', 'Y', 'Z', 'S', 'SX', 'T', 'I',
                     'RX', 'RY', 'RZ', 'U1', 'RPhi', 'U2', 'U3',
                     'CNOT', 'CZ', 'ISWAP',
                     'XX', 'YY', 'ZZ', 'XY',
                     'PHASE2Q', 'UU15',
                     'TOFFOLI', 'CSWAP',
                     'BARRIER']
        result = generate_sub_gateset_originir(gate_list)
        assert isinstance(result, dict)


class TestOriginIRErrorChannelsStructure:
    """Tests for available_originir_error_channels structure."""

    def test_error_channels_is_dict(self):
        assert isinstance(available_originir_error_channels, dict)

    def test_error_channels_not_empty(self):
        assert len(available_originir_error_channels) > 0

    def test_every_entry_is_dict(self):
        for name, entry in available_originir_error_channels.items():
            assert isinstance(entry, dict), f"Entry for '{name}' is not a dict"

    def test_every_entry_has_qubit_key(self):
        for name, entry in available_originir_error_channels.items():
            assert 'qubit' in entry, f"'qubit' key missing for channel '{name}'"

    def test_every_entry_has_param_key(self):
        for name, entry in available_originir_error_channels.items():
            assert 'param' in entry, f"'param' key missing for channel '{name}'"

    def test_qubit_values_are_integers(self):
        for name, entry in available_originir_error_channels.items():
            assert isinstance(entry['qubit'], int), f"'qubit' is not int for '{name}'"

    def test_param_values_are_integers(self):
        for name, entry in available_originir_error_channels.items():
            assert isinstance(entry['param'], int), f"'param' is not int for '{name}'"

    def test_keys_are_strings(self):
        for name in available_originir_error_channels:
            assert isinstance(name, str), f"Channel key '{name}' is not a string"

    def test_1q1p_channels_present(self):
        for ch in available_originir_error_channel_1q1p:
            assert ch in available_originir_error_channels, f"1q1p channel '{ch}' missing"

    def test_1q3p_channels_present(self):
        for ch in available_originir_error_channel_1q3p:
            assert ch in available_originir_error_channels, f"1q3p channel '{ch}' missing"

    def test_1qnp_channels_present(self):
        for ch in available_originir_error_channel_1qnp:
            assert ch in available_originir_error_channels, f"1qnp channel '{ch}' missing"

    def test_2q1p_channels_present(self):
        for ch in available_originir_error_channel_2q1p:
            assert ch in available_originir_error_channels, f"2q1p channel '{ch}' missing"

    def test_2q15p_channels_present(self):
        for ch in available_originir_error_channel_2q15p:
            assert ch in available_originir_error_channels, f"2q15p channel '{ch}' missing"


class TestOriginIRErrorChannelValues:
    """Tests for correct qubit/param values in available_originir_error_channels."""

    def test_1q1p_channels_qubit1_param1(self):
        for ch in available_originir_error_channel_1q1p:
            _assert_gate_entry(available_originir_error_channels, ch, 1, 'param', 1)

    def test_1q3p_channels_qubit1_param3(self):
        for ch in available_originir_error_channel_1q3p:
            _assert_gate_entry(available_originir_error_channels, ch, 1, 'param', 3)

    def test_1qnp_channels_qubit1_param_minus1(self):
        # Kraus1Q uses param=-1 as a sentinel for "n params"
        for ch in available_originir_error_channel_1qnp:
            _assert_gate_entry(available_originir_error_channels, ch, 1, 'param', -1)

    def test_2q1p_channels_qubit2_param1(self):
        for ch in available_originir_error_channel_2q1p:
            _assert_gate_entry(available_originir_error_channels, ch, 2, 'param', 1)

    def test_2q15p_channels_qubit2_param15(self):
        for ch in available_originir_error_channel_2q15p:
            _assert_gate_entry(available_originir_error_channels, ch, 2, 'param', 15)

    # Spot-check
    def test_Depolarizing(self):
        _assert_gate_entry(available_originir_error_channels, 'Depolarizing', 1, 'param', 1)

    def test_BitFlip(self):
        _assert_gate_entry(available_originir_error_channels, 'BitFlip', 1, 'param', 1)

    def test_PhaseFlip(self):
        _assert_gate_entry(available_originir_error_channels, 'PhaseFlip', 1, 'param', 1)

    def test_AmplitudeDamping(self):
        _assert_gate_entry(available_originir_error_channels, 'AmplitudeDamping', 1, 'param', 1)

    def test_PauliError1Q(self):
        _assert_gate_entry(available_originir_error_channels, 'PauliError1Q', 1, 'param', 3)

    def test_Kraus1Q(self):
        _assert_gate_entry(available_originir_error_channels, 'Kraus1Q', 1, 'param', -1)

    def test_TwoQubitDepolarizing(self):
        _assert_gate_entry(available_originir_error_channels, 'TwoQubitDepolarizing', 2, 'param', 1)

    def test_PauliError2Q(self):
        _assert_gate_entry(available_originir_error_channels, 'PauliError2Q', 2, 'param', 15)


class TestOriginIRErrorChannelsWithoutKraus:
    """Tests for available_originir_error_channels_without_kraus."""

    def test_is_dict(self):
        assert isinstance(available_originir_error_channels_without_kraus, dict)

    def test_not_empty(self):
        assert len(available_originir_error_channels_without_kraus) > 0

    def test_kraus1q_excluded(self):
        for ch in available_originir_error_channel_1qnp:
            assert ch not in available_originir_error_channels_without_kraus, (
                f"Kraus channel '{ch}' should be excluded from without_kraus dict"
            )

    def test_non_kraus_channels_present(self):
        non_kraus = (available_originir_error_channel_1q1p +
                     available_originir_error_channel_1q3p +
                     available_originir_error_channel_2q1p +
                     available_originir_error_channel_2q15p)
        for ch in non_kraus:
            assert ch in available_originir_error_channels_without_kraus, (
                f"Non-Kraus channel '{ch}' should be in without_kraus dict"
            )

    def test_is_subset_of_full_channels(self):
        for key in available_originir_error_channels_without_kraus:
            assert key in available_originir_error_channels, (
                f"'{key}' in without_kraus but not in full channels dict"
            )

    def test_values_match_full_channels(self):
        for key, val in available_originir_error_channels_without_kraus.items():
            assert val == available_originir_error_channels[key], (
                f"Value mismatch for '{key}' between without_kraus and full channels"
            )

    def test_smaller_than_full_channels(self):
        assert len(available_originir_error_channels_without_kraus) < len(available_originir_error_channels)

    def test_every_entry_has_qubit_and_param(self):
        for name, entry in available_originir_error_channels_without_kraus.items():
            assert 'qubit' in entry
            assert 'param' in entry


class TestGenerateSubErrorChannelOriginir:
    """Tests for generate_sub_error_channel_originir."""

    def test_returns_dict(self):
        result = generate_sub_error_channel_originir(['Depolarizing'])
        assert isinstance(result, dict)

    def test_returns_only_requested_channels(self):
        channel_list = ['Depolarizing', 'BitFlip']
        result = generate_sub_error_channel_originir(channel_list)
        assert set(result.keys()) == set(channel_list)

    def test_values_match_original(self):
        channel_list = ['Depolarizing', 'BitFlip', 'PauliError1Q']
        result = generate_sub_error_channel_originir(channel_list)
        for ch in channel_list:
            assert result[ch] == available_originir_error_channels[ch]

    def test_empty_list_returns_empty_dict(self):
        result = generate_sub_error_channel_originir([])
        assert result == {}

    def test_single_channel(self):
        result = generate_sub_error_channel_originir(['Kraus1Q'])
        assert result == {'Kraus1Q': available_originir_error_channels['Kraus1Q']}

    def test_unknown_channel_not_in_result(self):
        result = generate_sub_error_channel_originir(['Depolarizing', 'FAKE_CHANNEL'])
        assert 'FAKE_CHANNEL' not in result
        assert 'Depolarizing' in result

    def test_all_channels_subset(self):
        all_keys = list(available_originir_error_channels.keys())
        result = generate_sub_error_channel_originir(all_keys)
        assert result == available_originir_error_channels

    def test_does_not_mutate_original(self):
        original_copy = dict(available_originir_error_channels)
        generate_sub_error_channel_originir(['Depolarizing'])
        assert available_originir_error_channels == original_copy

    def test_result_has_correct_structure(self):
        result = generate_sub_error_channel_originir(['Depolarizing', 'TwoQubitDepolarizing'])
        for name, entry in result.items():
            assert 'qubit' in entry
            assert 'param' in entry

    def test_no_error_for_valid_comprehensive_list(self):
        all_channels = (available_originir_error_channel_1q1p +
                        available_originir_error_channel_1q3p +
                        available_originir_error_channel_1qnp +
                        available_originir_error_channel_2q1p +
                        available_originir_error_channel_2q15p)
        result = generate_sub_error_channel_originir(all_channels)
        assert isinstance(result, dict)
        assert len(result) == len(available_originir_error_channels)
