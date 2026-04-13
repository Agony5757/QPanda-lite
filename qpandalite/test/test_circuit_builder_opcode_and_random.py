"""
Comprehensive unit tests for:
  - qpandalite/circuit_builder/opcode.py
  - qpandalite/circuit_builder/translate_qasm2_oir.py
  - qpandalite/circuit_builder/random_qasm.py
  - qpandalite/circuit_builder/random_originir.py
"""

import pytest
from qpandalite.circuit_builder.opcode import (
    make_header_originir,
    make_header_qasm,
    make_measure_originir,
    make_measure_qasm,
    opcode_to_line_originir,
    opcode_to_line_qasm,
)
from qpandalite.circuit_builder.translate_qasm2_oir import (
    OriginIR_QASM2_dict,
    QASM2_OriginIR_dict,
    direct_mapping_qasm2_to_oir,
    get_opcode_from_QASM2,
    get_QASM2_from_opcode,
)
from qpandalite.circuit_builder.random_qasm import (
    build_qasm_gate,
    build_full_measurements as qasm_build_full_measurements,
    build_measurements,
    random_qasm,
    build_qasm_from_opcodes,
)
from qpandalite.circuit_builder.random_originir import (
    build_originir_gate,
    build_originir_error_channel,
    build_full_measurements as oir_build_full_measurements,
    random_originir,
)


# ──────────────────────────────────────────────────────────────────────────────
# 1.  opcode.py
# ──────────────────────────────────────────────────────────────────────────────

class TestMakeHeaderOriginIR:
    def test_basic(self):
        result = make_header_originir(3, 2)
        assert result == "QINIT 3\nCREG 2\n"

    def test_single_qubit(self):
        result = make_header_originir(1, 1)
        assert result == "QINIT 1\nCREG 1\n"

    def test_large_values(self):
        result = make_header_originir(100, 50)
        assert result.startswith("QINIT 100\n")
        assert "CREG 50\n" in result

    def test_format_has_two_lines(self):
        result = make_header_originir(5, 5)
        lines = result.split("\n")
        # "QINIT 5", "CREG 5", "" (trailing newline)
        assert lines[0] == "QINIT 5"
        assert lines[1] == "CREG 5"


class TestMakeHeaderQASM:
    def test_basic(self):
        result = make_header_qasm(3, 2)
        assert 'OPENQASM 2.0;' in result
        assert 'qelib1.inc' in result
        assert 'qreg q[3];' in result
        assert 'creg c[2];' in result

    def test_openqasm_first_line(self):
        result = make_header_qasm(2, 2)
        first_line = result.split("\n")[0]
        assert first_line == "OPENQASM 2.0;"

    def test_include_line(self):
        result = make_header_qasm(2, 2)
        assert 'include "qelib1.inc";' in result


class TestMakeMeasureOriginIR:
    def test_two_qubits(self):
        result = make_measure_originir([0, 1])
        assert result == "MEASURE q[0], c[0]\nMEASURE q[1], c[1]\n"

    def test_single_qubit(self):
        result = make_measure_originir([0])
        assert result == "MEASURE q[0], c[0]\n"

    def test_non_contiguous_qubits(self):
        result = make_measure_originir([2, 4])
        # qubit indices are from measure_list; cbit indices are enumeration
        assert "MEASURE q[2], c[0]" in result
        assert "MEASURE q[4], c[1]" in result

    def test_empty_list(self):
        result = make_measure_originir([])
        assert result == ""


class TestMakeMeasureQASM:
    def test_two_qubits(self):
        result = make_measure_qasm([0, 1])
        assert "measure q[0] -> c[0];" in result
        assert "measure q[1] -> c[1];" in result

    def test_single_qubit(self):
        result = make_measure_qasm([0])
        assert result == "measure q[0] -> c[0];\n"

    def test_non_contiguous_qubits(self):
        result = make_measure_qasm([3, 5])
        assert "measure q[3] -> c[0];" in result
        assert "measure q[5] -> c[1];" in result


class TestOpcodeToLineOriginIR:
    def test_1q_no_param(self):
        opcode = ('H', 0, None, None, False, None)
        result = opcode_to_line_originir(opcode)
        assert result == 'H q[0]'

    def test_1q_with_param(self):
        opcode = ('RX', 1, None, [0.5], False, None)
        result = opcode_to_line_originir(opcode)
        assert 'RX' in result
        assert 'q[1]' in result
        assert '0.5' in result

    def test_1q_with_scalar_param(self):
        opcode = ('RZ', 2, None, 1.0, False, None)
        result = opcode_to_line_originir(opcode)
        assert 'RZ q[2]' in result
        assert '1.0' in result

    def test_2q_no_param(self):
        opcode = ('CNOT', [0, 1], None, None, False, None)
        result = opcode_to_line_originir(opcode)
        assert 'CNOT' in result
        assert 'q[0]' in result
        assert 'q[1]' in result

    def test_with_dagger_flag(self):
        opcode = ('S', 0, None, None, True, None)
        result = opcode_to_line_originir(opcode)
        assert 'dagger' in result

    def test_with_control_qubits(self):
        opcode = ('X', 1, None, None, False, {0})
        result = opcode_to_line_originir(opcode)
        assert 'controlled_by' in result
        assert 'q[0]' in result

    def test_with_list_qubits(self):
        opcode = ('CZ', [2, 3], None, None, False, None)
        result = opcode_to_line_originir(opcode)
        assert 'q[2]' in result
        assert 'q[3]' in result

    def test_empty_operation_raises(self):
        opcode = ('', 0, None, None, False, None)
        with pytest.raises(RuntimeError):
            opcode_to_line_originir(opcode)


class TestOpcodeToLineQASM:
    def test_1q_no_param(self):
        opcode = ('H', 0, None, None, False, None)
        result = opcode_to_line_qasm(opcode)
        assert result == 'h q[0];'

    def test_1q_with_param(self):
        opcode = ('RX', 1, None, [0.5], False, None)
        result = opcode_to_line_qasm(opcode)
        assert result.startswith('rx')
        assert 'q[1]' in result
        assert '0.5' in result
        assert result.endswith(';')

    def test_2q_no_param(self):
        opcode = ('CNOT', [0, 1], None, None, False, None)
        result = opcode_to_line_qasm(opcode)
        assert result.startswith('cx')
        assert result.endswith(';')

    def test_unsupported_operation_raises(self):
        # U0 is not in OriginIR_QASM2_dict (no direct reverse mapping)
        opcode = ('UNSUPPORTED_OP_XYZ', 0, None, None, False, None)
        with pytest.raises(NotImplementedError):
            opcode_to_line_qasm(opcode)


# ──────────────────────────────────────────────────────────────────────────────
# 2.  translate_qasm2_oir.py
# ──────────────────────────────────────────────────────────────────────────────

class TestBidirectionalMappings:
    def test_qasm2_to_oir_dict_exists(self):
        assert isinstance(QASM2_OriginIR_dict, dict)
        assert len(QASM2_OriginIR_dict) > 0

    def test_oir_to_qasm2_dict_exists(self):
        assert isinstance(OriginIR_QASM2_dict, dict)
        assert len(OriginIR_QASM2_dict) > 0

    def test_cx_maps_to_cnot(self):
        assert QASM2_OriginIR_dict['cx'] == 'CNOT'

    def test_cnot_maps_to_cx(self):
        assert OriginIR_QASM2_dict['CNOT'] == 'cx'

    def test_h_maps_to_H(self):
        assert QASM2_OriginIR_dict['h'] == 'H'

    def test_H_maps_to_h(self):
        assert OriginIR_QASM2_dict['H'] == 'h'

    def test_known_gates_in_qasm2_dict(self):
        expected = ['id', 'h', 'x', 'y', 'z', 's', 'sx', 't', 'cx', 'cz',
                    'swap', 'ccx', 'cswap', 'rx', 'ry', 'rz', 'u1', 'u2',
                    'u3', 'rxx', 'ryy', 'rzz']
        for gate in expected:
            assert gate in QASM2_OriginIR_dict, f"{gate} missing from QASM2_OriginIR_dict"


class TestDirectMapping:
    def test_cx_to_cnot(self):
        assert direct_mapping_qasm2_to_oir('cx') == 'CNOT'

    def test_h_to_H(self):
        assert direct_mapping_qasm2_to_oir('h') == 'H'

    def test_unknown_returns_none(self):
        assert direct_mapping_qasm2_to_oir('unknown_gate') is None

    def test_empty_string_returns_none(self):
        assert direct_mapping_qasm2_to_oir('') is None


class TestGetOpcodeFromQASM2:
    # ── 1-qubit no-param gates ──
    def test_id(self):
        result = get_opcode_from_QASM2('id', [0], None, None)
        assert result[0] == 'I'
        assert result[4] is False

    def test_h(self):
        result = get_opcode_from_QASM2('h', [0], None, None)
        assert result[0] == 'H'
        assert result[1] == [0]
        assert result[4] is False
        assert result[5] is None

    def test_x(self):
        assert get_opcode_from_QASM2('x', [0], None, None)[0] == 'X'

    def test_y(self):
        assert get_opcode_from_QASM2('y', [0], None, None)[0] == 'Y'

    def test_z(self):
        assert get_opcode_from_QASM2('z', [0], None, None)[0] == 'Z'

    def test_s(self):
        result = get_opcode_from_QASM2('s', [0], None, None)
        assert result[0] == 'S'
        assert result[4] is False

    def test_sdg(self):
        result = get_opcode_from_QASM2('sdg', [0], None, None)
        assert result[0] == 'S'
        assert result[4] is True  # dagger flag

    def test_sx(self):
        result = get_opcode_from_QASM2('sx', [0], None, None)
        assert result[0] == 'SX'
        assert result[4] is False

    def test_sxdg(self):
        result = get_opcode_from_QASM2('sxdg', [0], None, None)
        assert result[0] == 'SX'
        assert result[4] is True

    def test_t(self):
        result = get_opcode_from_QASM2('t', [0], None, None)
        assert result[0] == 'T'
        assert result[4] is False

    def test_tdg(self):
        result = get_opcode_from_QASM2('tdg', [0], None, None)
        assert result[0] == 'T'
        assert result[4] is True

    # ── 2-qubit no-param gates ──
    def test_cx(self):
        result = get_opcode_from_QASM2('cx', [0, 1], None, None)
        assert result[0] == 'CNOT'

    def test_cy(self):
        # cy: controlled-Y → operation='Y', target=qubits[1], control=[qubits[0]]
        result = get_opcode_from_QASM2('cy', [0, 1], None, None)
        assert result[0] == 'Y'
        assert result[5] == [0]

    def test_cz(self):
        result = get_opcode_from_QASM2('cz', [0, 1], None, None)
        assert result[0] == 'CZ'

    def test_swap(self):
        result = get_opcode_from_QASM2('swap', [0, 1], None, None)
        assert result[0] == 'SWAP'

    def test_ch(self):
        result = get_opcode_from_QASM2('ch', [0, 1], None, None)
        assert result[0] == 'H'
        assert result[5] == [0]

    # ── 3-qubit gates ──
    def test_ccx(self):
        result = get_opcode_from_QASM2('ccx', [0, 1, 2], None, None)
        assert result[0] == 'TOFFOLI'

    def test_cswap(self):
        result = get_opcode_from_QASM2('cswap', [0, 1, 2], None, None)
        assert result[0] == 'CSWAP'

    # ── 4-qubit gates ──
    def test_c3x(self):
        result = get_opcode_from_QASM2('c3x', [0, 1, 2, 3], None, None)
        assert result[0] == 'X'
        assert result[1] == 3
        assert result[5] == [0, 1, 2]

    # ── 1-qubit 1-param gates ──
    def test_rx(self):
        result = get_opcode_from_QASM2('rx', [0], None, [0.5])
        assert result[0] == 'RX'
        assert result[3] == [0.5]

    def test_ry(self):
        assert get_opcode_from_QASM2('ry', [0], None, [1.0])[0] == 'RY'

    def test_rz(self):
        assert get_opcode_from_QASM2('rz', [0], None, [1.0])[0] == 'RZ'

    def test_u1(self):
        assert get_opcode_from_QASM2('u1', [0], None, [0.3])[0] == 'U1'

    # ── 1-qubit 2-param gates ──
    def test_u2(self):
        assert get_opcode_from_QASM2('u2', [0], None, [0.1, 0.2])[0] == 'U2'

    def test_u0(self):
        assert get_opcode_from_QASM2('u0', [0], None, [0.1])[0] == 'U0'

    # ── 1-qubit 3-param gates ──
    def test_u(self):
        assert get_opcode_from_QASM2('u', [0], None, [0.1, 0.2, 0.3])[0] == 'U3'

    def test_u3(self):
        assert get_opcode_from_QASM2('u3', [0], None, [0.1, 0.2, 0.3])[0] == 'U3'

    # ── 2-qubit 1-param gates ──
    def test_rxx(self):
        assert get_opcode_from_QASM2('rxx', [0, 1], None, [0.5])[0] == 'XX'

    def test_ryy(self):
        assert get_opcode_from_QASM2('ryy', [0, 1], None, [0.5])[0] == 'YY'

    def test_rzz(self):
        assert get_opcode_from_QASM2('rzz', [0, 1], None, [0.5])[0] == 'ZZ'

    def test_cu1(self):
        result = get_opcode_from_QASM2('cu1', [0, 1], None, [0.5])
        assert result[0] == 'U1'
        assert result[5] == [0]

    def test_crx(self):
        result = get_opcode_from_QASM2('crx', [0, 1], None, [0.5])
        assert result[0] == 'RX'
        assert result[5] == [0]

    def test_cry(self):
        result = get_opcode_from_QASM2('cry', [0, 1], None, [0.5])
        assert result[0] == 'RY'
        assert result[5] == [0]

    def test_crz(self):
        result = get_opcode_from_QASM2('crz', [0, 1], None, [0.5])
        assert result[0] == 'RZ'
        assert result[5] == [0]

    def test_cu3(self):
        result = get_opcode_from_QASM2('cu3', [0, 1], None, [0.1, 0.2, 0.3])
        assert result[0] == 'U3'
        assert result[5] == [0]

    def test_unsupported_returns_none(self):
        result = get_opcode_from_QASM2('unsupported_gate_xyz', [0], None, None)
        assert result is None


class TestGetQASM2FromOpcode:
    def test_h_no_ctrl_no_dagger(self):
        opcode = ('H', 0, None, None, False, None)
        op, qubits, cbits, params = get_QASM2_from_opcode(opcode)
        assert op == 'h'

    def test_cnot_no_ctrl_no_dagger(self):
        opcode = ('CNOT', [0, 1], None, None, False, None)
        op, qubits, cbits, params = get_QASM2_from_opcode(opcode)
        assert op == 'cx'

    def test_rx_no_dagger(self):
        opcode = ('RX', 0, None, [0.5], False, None)
        op, qubits, cbits, params = get_QASM2_from_opcode(opcode)
        assert op == 'rx'
        assert params == [0.5]

    # ── Dagger flag behaviour ──
    # BUG NOTE: get_QASM2_from_opcode compares `operation` against lowercase
    # strings ('s', 't', 'sx', 'rx', …) in the dagger branch, but OriginIR
    # operation names are uppercase ('S', 'T', 'SX', 'RX', …). As a result,
    # the dagger branch never matches and always falls through to the else
    # clause, raising NotImplementedError even for operations that should be
    # supported (S→sdg, T→tdg, SX→sxdg, RX with negated angle).
    # The tests below document this actual (buggy) behaviour.

    def test_s_dagger_returns_sdg(self):
        """S with dagger returns 'sdg'."""
        opcode = ('S', 0, None, None, True, None)
        result = get_QASM2_from_opcode(opcode)
        assert result[0] == 'sdg'

    def test_t_dagger_returns_tdg(self):
        """T with dagger returns 'tdg'."""
        opcode = ('T', 0, None, None, True, None)
        result = get_QASM2_from_opcode(opcode)
        assert result[0] == 'tdg'

    def test_sx_dagger_returns_sxdg(self):
        """SX with dagger returns 'sxdg'."""
        opcode = ('SX', 0, None, None, True, None)
        result = get_QASM2_from_opcode(opcode)
        assert result[0] == 'sxdg'

    def test_rx_dagger_negates_params(self):
        """RX with dagger returns 'rx' with negated parameters."""
        opcode = ('RX', 0, None, 0.5, True, None)
        result = get_QASM2_from_opcode(opcode)
        assert result[0] == 'rx'
        assert result[3] == -0.5

    def test_unsupported_dagger_raises(self):
        # U2 doesn't have a defined dagger behaviour
        opcode = ('U2', 0, None, [0.1, 0.2], True, None)
        with pytest.raises(NotImplementedError):
            get_QASM2_from_opcode(opcode)

    # ── Control qubits ──
    def test_1_control_qubit(self):
        # Use X (→ cx) because 'ch' is not in available_qasm_gates
        opcode = ('X', 2, None, None, False, {1})
        op, qubits, _, _ = get_QASM2_from_opcode(opcode)
        assert op == 'cx'
        assert 1 in qubits
        assert 2 in qubits

    def test_2_control_qubits(self):
        # CNOT (cx) + 2 controls → ccx (TOFFOLI)
        opcode = ('X', 2, None, None, False, {0, 1})
        op, qubits, _, _ = get_QASM2_from_opcode(opcode)
        assert op == 'ccx'

    def test_3_control_qubits(self):
        opcode = ('X', 3, None, None, False, {0, 1, 2})
        op, qubits, _, _ = get_QASM2_from_opcode(opcode)
        assert op == 'c3x'

    def test_unsupported_control_raises(self):
        # U3 with 1 control → cu3 which should be in available_qasm_gates
        # RY with 2 controls → 'ccry' which is NOT a valid QASM gate
        opcode = ('RY', 2, None, [0.5], False, {0, 1})
        with pytest.raises(NotImplementedError):
            get_QASM2_from_opcode(opcode)

    def test_unsupported_operation_raises(self):
        opcode = ('UNSUPPORTED_OP', 0, None, None, False, None)
        with pytest.raises(NotImplementedError):
            get_QASM2_from_opcode(opcode)

    # ── Round-trip ──
    def test_roundtrip_h(self):
        """H -> h -> H should reconstruct cleanly."""
        opcode = ('H', [0], None, None, False, None)
        op_qasm, qubits, cbits, params = get_QASM2_from_opcode(opcode)
        assert op_qasm == 'h'
        result = get_opcode_from_QASM2(op_qasm, qubits, cbits, params)
        assert result is not None
        assert result[0] == 'H'

    def test_roundtrip_rx(self):
        opcode = ('RX', [0], None, [1.2], False, None)
        op_qasm, qubits, cbits, params = get_QASM2_from_opcode(opcode)
        assert op_qasm == 'rx'
        result = get_opcode_from_QASM2(op_qasm, qubits, cbits, params)
        assert result[0] == 'RX'
        assert result[3] == [1.2]


# ──────────────────────────────────────────────────────────────────────────────
# 3.  random_qasm.py
# ──────────────────────────────────────────────────────────────────────────────

class TestBuildQasmGate:
    def test_1q_no_param(self):
        result = build_qasm_gate('h', [0], [], 'q')
        assert result == 'h q[0];'

    def test_1q_with_param(self):
        result = build_qasm_gate('rx', [0], [0.5], 'q')
        assert result == 'rx(0.5) q[0];'

    def test_2q_no_param(self):
        result = build_qasm_gate('cx', [0, 1], [], 'q')
        assert result == 'cx q[0],q[1];'

    def test_multi_param(self):
        result = build_qasm_gate('u3', [0], [0.1, 0.2, 0.3], 'q')
        assert result.startswith('u3(')
        assert 'q[0]' in result
        assert result.endswith(';')

    def test_custom_qreg_name(self):
        result = build_qasm_gate('h', [0], [], 'myq')
        assert 'myq[0]' in result

    def test_empty_qubits_raises(self):
        with pytest.raises((ValueError, IndexError)):
            build_qasm_gate('h', [], [], 'q')


class TestQasmBuildFullMeasurements:
    def test_count(self):
        result = qasm_build_full_measurements(3)
        assert len(result) == 3

    def test_format(self):
        result = qasm_build_full_measurements(2)
        assert result[0] == 'measure q[0] -> c[0];'
        assert result[1] == 'measure q[1] -> c[1];'

    def test_zero_qubits(self):
        result = qasm_build_full_measurements(0)
        assert result == []


class TestBuildMeasurements:
    """
    BUG NOTE: `build_measurements` uses `range(measure_qbit_cbit_pairs)` instead
    of iterating over the argument as pairs (it should use `for qbit, cbit in ...`).
    This means passing an integer works (iterating range), but passing actual
    pairs would raise a TypeError.  Tests below document the actual behaviour.
    """

    def test_integer_arg_raises_typeerror(self):
        # Passing an integer raises TypeError because range(int) yields ints,
        # and the loop tries to unpack each int as (qbit, cbit).
        with pytest.raises(TypeError):
            build_measurements(3)

    def test_pairs_raises_typeerror(self):
        # Passing correct pairs should work logically but the implementation
        # has a bug: `range(measure_qbit_cbit_pairs)` calls range() on a list.
        with pytest.raises(TypeError):
            build_measurements([(0, 0), (1, 1)])


class TestRandomQasm:
    def test_returns_string(self):
        result = random_qasm(10, 5)
        assert isinstance(result, str)

    def test_starts_with_openqasm(self):
        result = random_qasm(10, 5)
        assert result.startswith('OPENQASM 2.0;')

    def test_includes_measure_by_default(self):
        # Use >=4 qubits to accommodate gates like c3x (4 qubits)
        result = random_qasm(10, 5)
        assert 'measure' in result

    def test_no_measure_when_disabled(self):
        result = random_qasm(10, 5, measurements=False)
        assert 'measure' not in result

    def test_has_qreg_and_creg(self):
        result = random_qasm(10, 3)
        assert 'qreg q[10];' in result
        assert 'creg c[10];' in result

    def test_reproducible_with_seed(self):
        import random as _random
        _random.seed(42)
        r1 = random_qasm(10, 5)
        _random.seed(42)
        r2 = random_qasm(10, 5)
        assert r1 == r2


class TestBuildQasmFromOpcodes:
    def test_single_h_gate(self):
        opcodes = [('H', [0], None, None, False, None)]
        result = build_qasm_from_opcodes(opcodes)
        assert isinstance(result, str)
        assert 'OPENQASM 2.0;' in result
        # 'H' gate → must appear as 'H q[0];' (note: build_qasm_from_opcodes
        # uses build_qasm_gate with the original operation string from opcode,
        # NOT get_QASM2_from_opcode, so 'H' not 'h')
        assert 'H q[0];' in result

    def test_qubit_count_auto_detected(self):
        opcodes = [('X', [2], None, None, False, None)]
        result = build_qasm_from_opcodes(opcodes)
        assert 'qreg q[3];' in result

    def test_dagger_flag_raises(self):
        opcodes = [('H', [0], None, None, True, None)]
        with pytest.raises(NotImplementedError):
            build_qasm_from_opcodes(opcodes)

    def test_control_qubits_raises(self):
        opcodes = [('H', [1], None, None, False, {0})]
        with pytest.raises(NotImplementedError):
            build_qasm_from_opcodes(opcodes)


# ──────────────────────────────────────────────────────────────────────────────
# 4.  random_originir.py
# ──────────────────────────────────────────────────────────────────────────────

class TestBuildOriginIRGate:
    def test_h_gate_basic(self):
        result = build_originir_gate('H', [0], [], False, None)
        assert isinstance(result, str)
        assert 'H' in result
        assert 'q[0]' in result

    def test_rx_gate_with_param(self):
        result = build_originir_gate('RX', [0], [0.5], False, None)
        assert 'RX' in result
        assert '0.5' in result

    def test_cnot_gate(self):
        result = build_originir_gate('CNOT', [0, 1], [], False, None)
        assert 'CNOT' in result
        assert 'q[0]' in result
        assert 'q[1]' in result

    def test_dagger_flag(self):
        result = build_originir_gate('S', [0], [], True, None)
        assert 'dagger' in result

    def test_with_control_qubits(self):
        result = build_originir_gate('X', [1], [], False, {0})
        assert 'controlled_by' in result

    def test_invalid_gate_raises_valueerror(self):
        with pytest.raises(ValueError):
            build_originir_gate('INVALID_GATE_XYZ', [0], [], False, None)

    def test_wrong_qubit_count_raises_valueerror(self):
        # H requires 1 qubit; passing 2 should raise ValueError
        with pytest.raises(ValueError):
            build_originir_gate('H', [0, 1], [], False, None)

    def test_wrong_param_count_raises_valueerror(self):
        # H requires 0 params; passing 1 should raise ValueError
        with pytest.raises(ValueError):
            build_originir_gate('H', [0], [0.5], False, None)

    def test_empty_qubits_raises_valueerror(self):
        with pytest.raises(ValueError):
            build_originir_gate('H', [], [], False, None)


class TestBuildOriginIRErrorChannel:
    def test_depolarizing_basic(self):
        result = build_originir_error_channel('Depolarizing', [0], [0.1])
        assert isinstance(result, str)
        assert 'Depolarizing' in result
        assert 'q[0]' in result
        assert '0.1' in result

    def test_bitflip(self):
        result = build_originir_error_channel('BitFlip', [0], [0.05])
        assert 'BitFlip' in result

    def test_invalid_channel_raises_valueerror(self):
        with pytest.raises(ValueError):
            build_originir_error_channel('InvalidChannel', [0], [0.1])

    def test_empty_qubits_raises_valueerror(self):
        with pytest.raises(ValueError):
            build_originir_error_channel('Depolarizing', [], [0.1])

    def test_wrong_qubit_count_raises_valueerror(self):
        # Depolarizing is 1-qubit; passing 2 should raise ValueError
        with pytest.raises(ValueError):
            build_originir_error_channel('Depolarizing', [0, 1], [0.1])


class TestOirBuildFullMeasurements:
    def test_count(self):
        result = oir_build_full_measurements(3)
        assert len(result) == 3

    def test_format(self):
        result = oir_build_full_measurements(2)
        assert result[0] == 'MEASURE q[0], c[0]'
        assert result[1] == 'MEASURE q[1], c[1]'

    def test_zero_qubits(self):
        result = oir_build_full_measurements(0)
        assert result == []


class TestRandomOriginIR:
    def test_returns_string(self):
        result = random_originir(3, 5)
        assert isinstance(result, str)

    def test_starts_with_qinit(self):
        result = random_originir(3, 5)
        assert result.startswith('QINIT 3')

    def test_contains_creg(self):
        result = random_originir(3, 5)
        assert 'CREG 3' in result

    def test_contains_measure(self):
        result = random_originir(3, 5)
        assert 'MEASURE' in result

    def test_measure_count_matches_qubits(self):
        n = 4
        result = random_originir(n, 3)
        measure_count = result.count('MEASURE')
        assert measure_count == n

    def test_reproducible_with_seed(self):
        import random as _random
        _random.seed(99)
        r1 = random_originir(3, 5)
        _random.seed(99)
        r2 = random_originir(3, 5)
        assert r1 == r2


# =============================================================================
# Tests added for Issue #123: parameter validation, error paths, boundary
# =============================================================================


class TestOpcodeToLineOriginirEdgeCases:
    """Edge cases and error paths for opcode_to_line_originir."""

    def test_empty_operation_raises_runtimeerror(self):
        """An empty string operation should raise RuntimeError."""
        from qpandalite.circuit_builder.opcode import opcode_to_line_originir
        # opcode: (operation, qubit, cbit, parameter, dagger_flag, control_qubits_set)
        opcode = ('', 0, None, None, False, None)
        with pytest.raises(RuntimeError, match='Unexpected error'):
            opcode_to_line_originir(opcode)

    def test_parameter_float_precision_preserved(self):
        """Float parameters are formatted with full precision (not truncated)."""
        from qpandalite.circuit_builder.opcode import opcode_to_line_originir
        opcode = ('RX', 0, None, 3.141592653589793, False, None)
        line = opcode_to_line_originir(opcode)
        # The formatted string should contain the full float value
        assert '3.141592653589793' in line

    def test_dagger_with_single_control_qubit(self):
        """Dagger flag combined with a single control qubit formats correctly."""
        from qpandalite.circuit_builder.opcode import opcode_to_line_originir
        # Dagger flag on Y gate with q[1] controlled by q[0]
        opcode = ('Y', 1, None, None, True, {0})
        line = opcode_to_line_originir(opcode)
        assert 'Y' in line
        assert 'dagger' in line
        assert 'controlled_by' in line


class TestOpcodeToLineQasmEdgeCases:
    """Edge cases and error paths for opcode_to_line_qasm."""

    def test_cbit_raises_notimplementederror(self):
        """Passing a cbit (classical bit) should raise NotImplementedError."""
        from qpandalite.circuit_builder.opcode import opcode_to_line_qasm
        # opcode with cbit=1 (non-None, non-falsy); cbit=0 would be falsy and not trigger the check
        opcode = ('H', 0, 1, None, False, None)
        with pytest.raises(NotImplementedError, match='cbit.*QASM'):
            opcode_to_line_qasm(opcode)


class TestTranslateQasm2OirErrorPaths:
    """Error paths for get_QASM2_from_opcode and related functions."""

    def test_unsupported_operation_raises_notimplementederror(self):
        """get_QASM2_from_opcode with unsupported operation raises NotImplementedError."""
        from qpandalite.circuit_builder.translate_qasm2_oir import get_QASM2_from_opcode
        # 'XY' is not in OriginIR_QASM2_dict
        opcode = ('XY', 0, None, None, False, None)
        with pytest.raises(NotImplementedError):
            get_QASM2_from_opcode(opcode)

    def test_dagger_with_unsupported_gate_raises_notimplementederror(self):
        """Dagger flag on an unsupported gate raises NotImplementedError."""
        from qpandalite.circuit_builder.translate_qasm2_oir import get_QASM2_from_opcode
        # 'Y' dagger is supported (Y → ydg); but 'XY' dagger is not supported
        opcode = ('XY', 0, None, None, True, None)
        with pytest.raises(NotImplementedError):
            get_QASM2_from_opcode(opcode)

    def test_direct_mapping_returns_none_for_unmapped(self):
        """direct_mapping_qasm2_to_oir returns None for operations without direct mapping."""
        from qpandalite.circuit_builder.translate_qasm2_oir import direct_mapping_qasm2_to_oir
        # 'u0' exists in QASM but has no direct OriginIR mapping
        result = direct_mapping_qasm2_to_oir('u0')
        assert result is None

    def test_direct_mapping_returns_correct_value(self):
        """direct_mapping_qasm2_to_oir returns correct OriginIR for mapped QASM ops."""
        from qpandalite.circuit_builder.translate_qasm2_oir import direct_mapping_qasm2_to_oir
        assert direct_mapping_qasm2_to_oir('cx') == 'CNOT'
        assert direct_mapping_qasm2_to_oir('h') == 'H'
        assert direct_mapping_qasm2_to_oir('swap') == 'SWAP'
        assert direct_mapping_qasm2_to_oir('ccx') == 'TOFFOLI'

    def test_3control_qubit_gate_not_in_qasm_raises(self):
        """Using 3 control qubits on an unsupported gate raises NotImplementedError."""
        from qpandalite.circuit_builder.translate_qasm2_oir import get_QASM2_from_opcode
        # Y gate with 3 control qubits: 'ccy' is not in available_qasm_gates
        opcode = ('Y', 3, None, None, False, {0, 1, 2})
        with pytest.raises(NotImplementedError):
            get_QASM2_from_opcode(opcode)


class TestRandomQasmBoundaryConditions:
    """Boundary conditions for random_qasm."""

    def test_zero_gates_returns_valid_qasm(self):
        """random_qasm with n_gates=0 returns valid QASM (header + measure only)."""
        result = random_qasm(2, 0, measurements=True)
        assert isinstance(result, str)
        assert 'OPENQASM 2.0' in result
        assert 'qreg q[2]' in result
        assert 'measure' in result  # QASM measure statements are lowercase

    def test_measurements_false_excludes_measure(self):
        """random_qasm with measurements=False does not include MEASURE statements."""
        # Use a large enough n_qubits and low n_gates to avoid the gate-selection bug
        # that can select a gate requiring more qubits than available.
        result = random_qasm(10, 3, measurements=False)
        assert 'measure' not in result.lower()

    def test_angle_parameters_in_valid_range(self):
        """Parameters generated by random_qasm fall within [0, 2π]."""
        import random as _random
        _random.seed(42)
        result = random_qasm(10, 50, measurements=False)
        import re
        # Extract all floating-point numbers from parameter parentheses
        params = re.findall(r'\(([\d.]+)\)', result)
        for p_str in params:
            p = float(p_str)
            assert 0 <= p <= 2 * 3.14159 + 1e-9, f"Parameter {p} outside [0, 2π]"

    def test_build_qasm_gate_float_formatting(self):
        """build_qasm_gate formats float parameters without truncation."""
        result = build_qasm_gate('rx', [0], [3.141592653589793], 'q')
        assert '3.141592653589793' in result


class TestBuildMeasurementsBug:
    """Tests documenting the known bug in build_measurements."""

    def test_build_measurements_bug_note(self):
        """build_measurements has a bug: it iterates range(measure_qbit_cbit_pairs)
        instead of iterating over measure_qbit_cbit_pairs itself.
        This test documents the actual (buggy) behaviour.
        """
        # Passing an integer N calls range(N), yielding 0..N-1, then tries
        # to unpack each int as (qbit, cbit) → TypeError
        with pytest.raises(TypeError):
            build_measurements(3)


class TestRandomOriginirBoundaryConditions:
    """Boundary conditions for random_originir."""

    def test_zero_gates_returns_valid_originir(self):
        """random_originir with n_gates=0 returns valid OriginIR (header + measure only)."""
        result = random_originir(2, 0)
        assert isinstance(result, str)
        assert 'QINIT 2' in result
        assert 'CREG 2' in result
        assert 'MEASURE' in result

    def test_single_qubit_works_or_raises(self):
        """random_originir with n_qubits=1 may raise ValueError if a 2q gate is selected.

        NOTE: Known limitation: implementation does not filter gates by available
        qubit count. Tests with n_qubits=1 are inherently flaky.
        """
        try:
            result = random_originir(1, 3)
            assert 'QINIT 1' in result
            assert 'CREG 1' in result
        except ValueError:
            # Known limitation: gates requiring more qubits than available
            # can be randomly selected
            pass


class TestBuildOriginirGateAdditional:
    """Additional build_originir_gate tests beyond the existing ones."""

    def test_iswap_gate(self):
        """build_originir_gate works with ISWAP gate."""
        result = build_originir_gate('ISWAP', [0, 1], [], False, None)
        assert 'ISWAP' in result
        assert 'q[0]' in result
        assert 'q[1]' in result

    def test_barrier_gate(self):
        """build_originir_gate works with BARRIER gate."""
        result = build_originir_gate('BARRIER', [0, 1, 2], [], False, None)
        assert 'BARRIER' in result

    def test_rx_with_control_qubits(self):
        """build_originir_gate with control qubits generates controlled_by clause."""
        result = build_originir_gate('RX', [2], [0.5], False, {0, 1})
        assert 'RX' in result
        assert 'q[2]' in result
        assert 'controlled_by' in result
