"""
Comprehensive unit tests for qpandalite.circuit_builder.qcircuit.Circuit.
"""

import pytest
from qpandalite.circuit_builder import Circuit


# =============================================================================
# TestSingleQubitGates
# =============================================================================


class TestSingleQubitGates:
    """Tests for non-parametric single-qubit gates."""

    @pytest.mark.parametrize(
        "gate_method,op_name",
        [
            ("h", "H"),
            ("x", "X"),
            ("y", "Y"),
            ("z", "Z"),
            ("sx", "SX"),
            ("s", "S"),
            ("t", "T"),
            ("identity", "I"),
        ],
    )
    def test_gate_adds_opcode(self, gate_method, op_name):
        """Each gate appends a correctly-formed opcode to opcode_list."""
        c = Circuit()
        getattr(c, gate_method)(0)
        assert len(c.opcode_list) == 1
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == op_name
        assert qubits == 0
        assert cbits is None
        assert params is None
        assert dagger is False
        assert ctrl is None

    def test_sxdg_adds_daggered_sx(self):
        """sxdg adds SX with dagger=True."""
        c = Circuit()
        c.sxdg(0)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "SX"
        assert dagger is True

    def test_sdg_adds_daggered_s(self):
        """sdg adds S with dagger=True."""
        c = Circuit()
        c.sdg(0)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "S"
        assert dagger is True

    def test_tdg_adds_daggered_t(self):
        """tdg adds T with dagger=True."""
        c = Circuit()
        c.tdg(0)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "T"
        assert dagger is True

    @pytest.mark.parametrize(
        "gate_method,op_name",
        [
            ("h", "H"),
            ("x", "X"),
            ("y", "Y"),
            ("z", "Z"),
            ("sx", "SX"),
            ("sxdg", "SX"),
            ("s", "S"),
            ("sdg", "S"),
            ("t", "T"),
            ("tdg", "T"),
            ("identity", "I"),
        ],
    )
    def test_originir_format(self, gate_method, op_name):
        """originir output contains the expected gate line."""
        c = Circuit()
        getattr(c, gate_method)(0)
        originir = c.originir
        # Header + one gate line + possible measure lines
        lines = originir.strip().split("\n")
        assert lines[0].startswith("QINIT")
        assert lines[1].startswith("CREG")
        # Gate line should contain "q[0]" and the operation name
        gate_line = lines[2] if len(lines) > 2 else lines[-1]
        assert f"q[0]" in gate_line
        # For daggered gates the keyword "dagger" appears; for others just op name
        if "dg" in gate_method:
            assert "dagger" in gate_line
        else:
            assert op_name in gate_line

    @pytest.mark.parametrize(
        "gate_method,op_name",
        [
            ("h", "h"),
            ("x", "x"),
            ("y", "y"),
            ("z", "z"),
            ("sx", "sx"),
            ("s", "s"),
            ("t", "t"),
            ("identity", "id"),
        ],
    )
    def test_qasm_format(self, gate_method, op_name):
        """qasm output contains the expected gate line."""
        c = Circuit()
        getattr(c, gate_method)(0)
        qasm = c.qasm
        lines = qasm.strip().split("\n")
        assert "OPENQASM 2.0" in lines[0]
        assert any("qreg" in l for l in lines)
        assert any("creg" in l for l in lines)
        gate_lines = [l for l in lines if "q[0]" in l and "measure" not in l]
        assert len(gate_lines) >= 1
        assert op_name in gate_lines[0]


# =============================================================================
# TestParametricSingleQubitGates
# =============================================================================


class TestParametricSingleQubitGates:
    """Tests for parametric single-qubit rotation gates."""

    def test_rx_adds_opcode_with_param(self):
        """RX stores the angle in params."""
        c = Circuit()
        c.rx(0, 1.23)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "RX"
        assert qubits == 0
        assert params == 1.23

    def test_ry_adds_opcode_with_param(self):
        """RY stores the angle in params."""
        c = Circuit()
        c.ry(0, 0.5)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "RY"
        assert params == 0.5

    def test_rz_adds_opcode_with_param(self):
        """RZ stores the angle in params."""
        c = Circuit()
        c.rz(0, -1.0)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "RZ"
        assert params == -1.0

    def test_rphi_adds_opcode_with_params_list(self):
        """RPhi stores [theta, phi] as params."""
        c = Circuit()
        c.rphi(0, 0.7, 1.4)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "RPhi"
        assert params == [0.7, 1.4]

    def test_rx_originir_contains_angle(self):
        """originir output for RX includes the angle parameter."""
        c = Circuit()
        c.rx(0, 1.5)
        originir = c.originir
        assert "RX" in originir
        assert "q[0]" in originir
        assert "1.5" in originir

    def test_rphi_originir_contains_both_angles(self):
        """originir output for RPhi includes both theta and phi."""
        c = Circuit()
        c.rphi(0, 0.3, 0.6)
        originir = c.originir
        assert "RPhi" in originir
        assert "0.3" in originir
        assert "0.6" in originir


# =============================================================================
# TestTwoQubitGates
# =============================================================================


class TestTwoQubitGates:
    """Tests for two-qubit gates."""

    @pytest.mark.parametrize(
        "gate_method,op_name",
        [
            ("cnot", "CNOT"),
            ("cx", "CNOT"),
            ("cz", "CZ"),
            ("iswap", "ISWAP"),
            ("swap", "SWAP"),
        ],
    )
    def test_gate_adds_opcode(self, gate_method, op_name):
        """Each 2q gate appends a correctly-formed opcode."""
        c = Circuit()
        getattr(c, gate_method)(0, 1)
        assert len(c.opcode_list) == 1
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == op_name
        assert qubits == [0, 1]

    def test_cnot_originir_format(self):
        """CNOT originir contains q[0], q[1]."""
        c = Circuit()
        c.cnot(0, 1)
        originir = c.originir
        assert "CNOT" in originir
        assert "q[0]" in originir
        assert "q[1]" in originir

    def test_swap_originir_format(self):
        """SWAP originir contains q[0], q[1]."""
        c = Circuit()
        c.swap(0, 1)
        originir = c.originir
        assert "SWAP" in originir
        assert "q[0]" in originir
        assert "q[1]" in originir

    def test_cz_qasm_format(self):
        """CZ qasm contains cz q[0], q[1]."""
        c = Circuit()
        c.cz(0, 1)
        qasm = c.qasm
        assert "cz" in qasm
        assert "q[0]" in qasm
        assert "q[1]" in qasm


# =============================================================================
# TestThreeQubitGates
# =============================================================================


class TestThreeQubitGates:
    """Tests for three-qubit gates."""

    def test_cswap_adds_opcode(self):
        """CSWAP gate appends correctly-formed opcode."""
        c = Circuit()
        c.cswap(0, 1, 2)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "CSWAP"
        assert qubits == [0, 1, 2]

    def test_toffoli_adds_opcode(self):
        """TOFFOLI gate appends correctly-formed opcode."""
        c = Circuit()
        c.toffoli(0, 1, 2)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "TOFFOLI"
        assert qubits == [0, 1, 2]

    def test_cswap_originir_format(self):
        """CSWAP originir contains all three qubits."""
        c = Circuit()
        c.cswap(0, 1, 2)
        originir = c.originir
        assert "CSWAP" in originir
        assert "q[0]" in originir
        assert "q[1]" in originir
        assert "q[2]" in originir

    def test_toffoli_originir_format(self):
        """TOFFOLI originir contains all three qubits."""
        c = Circuit()
        c.toffoli(0, 1, 2)
        originir = c.originir
        assert "TOFFOLI" in originir
        assert "q[0]" in originir
        assert "q[1]" in originir
        assert "q[2]" in originir


# =============================================================================
# TestParametricTwoQubitGates
# =============================================================================


class TestParametricTwoQubitGates:
    """Tests for parametric two-qubit gates."""

    def test_u1_adds_opcode_with_param(self):
        """U1 stores lambda in params."""
        c = Circuit()
        c.u1(0, 1.1)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "U1"
        assert params == 1.1

    def test_u2_adds_opcode_with_params_list(self):
        """U2 stores [phi, lam] in params."""
        c = Circuit()
        c.u2(0, 0.2, 0.3)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "U2"
        assert params == [0.2, 0.3]

    def test_u3_adds_opcode_with_params_list(self):
        """U3 stores [theta, phi, lam] in params."""
        c = Circuit()
        c.u3(0, 0.1, 0.2, 0.3)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "U3"
        assert params == [0.1, 0.2, 0.3]

    def test_xx_adds_opcode_with_param(self):
        """XX stores theta in params."""
        c = Circuit()
        c.xx(0, 1, 0.5)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "XX"
        assert qubits == [0, 1]
        assert params == 0.5

    def test_yy_adds_opcode_with_param(self):
        """YY stores theta in params."""
        c = Circuit()
        c.yy(0, 1, 0.7)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "YY"
        assert params == 0.7

    def test_zz_adds_opcode_with_param(self):
        """ZZ stores theta in params."""
        c = Circuit()
        c.zz(0, 1, 1.2)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "ZZ"
        assert params == 1.2

    def test_phase2q_adds_opcode_with_params_list(self):
        """PHASE2Q stores [theta1, theta2, thetazz] in params."""
        c = Circuit()
        c.phase2q(0, 1, 0.1, 0.2, 0.3)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "PHASE2Q"
        assert qubits == [0, 1]
        assert params == [0.1, 0.2, 0.3]

    def test_uu15_adds_opcode_with_params_list(self):
        """UU15 stores the 15-parameter list in params."""
        c = Circuit()
        params_15 = [0.1 * i for i in range(1, 16)]
        c.uu15(0, 1, params_15)
        op, qubits, cbits, params, dagger, ctrl = c.opcode_list[0]
        assert op == "UU15"
        assert qubits == [0, 1]
        assert params == params_15

    def test_xx_originir_contains_theta(self):
        """XX originir contains the interaction angle."""
        c = Circuit()
        c.xx(0, 1, 0.45)
        originir = c.originir
        assert "XX" in originir
        assert "0.45" in originir

    def test_u3_originir_contains_three_params(self):
        """U3 originir contains theta, phi, lam."""
        c = Circuit()
        c.u3(0.1, 0.2, 0.3, 0.4)
        originir = c.originir
        assert "U3" in originir
        assert "0.1" in originir
        assert "0.2" in originir
        assert "0.3" in originir
        assert "0.4" in originir


# =============================================================================
# TestMeasurement
# =============================================================================


class TestMeasurement:
    """Tests for the measure() method."""

    def test_measure_single_qubit(self):
        """measure() adds qubit to measure_list and sets cbit_num."""
        c = Circuit()
        c.x(0)
        c.measure(0)
        assert c.measure_list == [0]
        assert c.cbit_num == 1

    def test_measure_multiple_qubits_accumulate(self):
        """Multiple measure() calls accumulate in measure_list."""
        c = Circuit()
        c.h(0)
        c.cnot(1, 2)
        c.measure(0, 1, 2)
        assert c.measure_list == [0, 1, 2]
        assert c.cbit_num == 3

    def test_measure_separate_calls_accumulate(self):
        """Two separate measure() calls accumulate measurements."""
        c = Circuit()
        c.measure(0)
        c.measure(1)
        assert c.measure_list == [0, 1]
        assert c.cbit_num == 2

    def test_measure_originir_format(self):
        """originir output includes MEASURE statements."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        originir = c.originir
        assert "MEASURE" in originir
        assert "q[0]" in originir
        assert "c[0]" in originir

    def test_measure_qasm_format(self):
        """qasm output includes measure statements."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        qasm = c.qasm
        assert "measure" in qasm
        assert "q[0]" in qasm
        assert "c[0]" in qasm

    def test_measure_after_gate(self):
        """Measure correctly records qubits used by prior gates."""
        c = Circuit()
        c.x(5)
        c.measure(5)
        assert c.measure_list == [5]
        assert c.qubit_num == 6  # max_qubit=5 -> qubit_num=6


# =============================================================================
# TestContextManagers
# =============================================================================


class TestContextManagers:
    """Tests for control() and dagger() context managers."""

    def test_control_context_wraps_gate(self):
        """Gates inside a control() block appear between CONTROL and ENDCONTROL."""
        c = Circuit()
        with c.control(0):
            c.x(1)
        circuit_str = c.circuit_str
        assert "CONTROL" in circuit_str
        assert "q[0]" in circuit_str
        assert "ENDCONTROL" in circuit_str

    def test_control_single_qubit(self):
        """control() with a single qubit emits CONTROL q[0]."""
        c = Circuit()
        with c.control(0):
            c.h(1)
        assert "CONTROL q[0]" in c.circuit_str

    def test_control_multiple_qubits(self):
        """control() with multiple qubits lists all control qubits."""
        c = Circuit()
        with c.control(0, 1):
            c.x(2)
        assert "CONTROL q[0], q[1]" in c.circuit_str

    def test_control_empty_raises(self):
        """control() with no arguments raises ValueError."""
        c = Circuit()
        with pytest.raises(ValueError):
            c.control()

    def test_dagger_context_wraps_gate(self):
        """Gates inside a dagger() block appear between DAGGER and ENDDAGGER."""
        c = Circuit()
        with c.dagger():
            c.h(0)
        circuit_str = c.circuit_str
        assert "DAGGER" in circuit_str
        assert "ENDDAGGER" in circuit_str

    def test_nested_control_and_dagger(self):
        """control() and dagger() can be nested."""
        c = Circuit()
        with c.control(0):
            with c.dagger():
                c.x(1)
        s = c.circuit_str
        # Verify the expected block structure is present.
        # Use substrings that don't overlap with END markers.
        assert "CONTROL q[0]" in s
        assert "DAGGER" in s and s.count("DAGGER") == 2  # DAGGER + END-DAGGER
        assert "ENDCONTROL" in s
        assert "ENDDAGGER" in s


# =============================================================================
# TestRemapping
# =============================================================================


class TestRemapping:
    """Tests for the remapping() method."""

    def test_remapping_creates_new_circuit(self):
        """remapping() returns a new Circuit instance."""
        c = Circuit()
        c.h(0)
        c.x(1)
        c2 = c.remapping({0: 2, 1: 3})
        assert c2 is not c
        assert c.opcode_list[0][1] == 0  # original unchanged
        assert c2.opcode_list[0][1] == 2  # remapped

    def test_remapping_valid_mapping(self):
        """Valid mapping remaps all qubits correctly."""
        c = Circuit()
        c.h(0)
        c.cnot(1, 2)
        c.measure(0, 1, 2)
        c2 = c.remapping({0: 5, 1: 6, 2: 7})
        assert c2.used_qubit_list == [5, 6, 7]

    def test_remapping_duplicate_values_raises(self):
        """Duplicate target values raise ValueError."""
        c = Circuit()
        c.h(0)
        c.x(1)
        with pytest.raises(ValueError):
            c.remapping({0: 2, 1: 2})

    def test_remapping_missing_qubit_raises(self):
        """A missing qubit in the mapping raises ValueError."""
        c = Circuit()
        c.h(0)
        c.x(1)
        with pytest.raises(ValueError):
            c.remapping({0: 2})  # qubit 1 is missing

    def test_remapping_non_integer_key_raises(self):
        """Non-integer key raises TypeError."""
        c = Circuit()
        c.h(0)
        with pytest.raises(TypeError):
            c.remapping({0.0: 1})

    def test_remapping_non_integer_value_raises(self):
        """Non-integer value raises TypeError."""
        c = Circuit()
        c.h(0)
        with pytest.raises(TypeError):
            c.remapping({0: 1.0})

    def test_remapping_negative_qubit_raises(self):
        """Negative qubit index raises TypeError."""
        c = Circuit()
        c.h(0)
        with pytest.raises(TypeError):
            c.remapping({0: -1})

    def test_remapping_with_measure(self):
        """remapping() also remaps measure_list."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        c2 = c.remapping({0: 3})
        assert c2.measure_list == [3]
        assert c2.cbit_num == 1


# =============================================================================
# TestDepth
# =============================================================================


class TestDepth:
    """Tests for the depth property."""

    def test_empty_circuit_depth(self):
        """Empty circuit should have depth 0.

        NOTE: The current implementation raises ValueError on empty circuit
        (max() on empty sequence). This test asserts the expected correct behaviour
        and is marked xfail until the implementation is fixed.
        """
        c = Circuit()
        pytest.xfail("depth raises ValueError on empty circuit (known gap in implementation)")
        assert c.depth == 0

    def test_sequential_gates_same_qubit(self):
        """Sequential gates on the same qubit give depth == gate count."""
        c = Circuit()
        c.h(0)
        c.x(0)
        c.y(0)
        assert c.depth == 3

    def test_independent_qubits_depth_1(self):
        """Gates on independent (non-overlapping) qubits have depth 1."""
        c = Circuit()
        c.h(0)
        c.x(1)
        c.y(2)
        assert c.depth == 1

    def test_barrier_excluded_from_depth(self):
        """BARRIER does not contribute to circuit depth."""
        c = Circuit()
        c.h(0)
        c.barrier(0)
        c.x(0)
        # barrier is skipped, so depth should still be 2
        assert c.depth == 2

    def test_identity_excluded_from_depth(self):
        """Identity gate (I) does not contribute to circuit depth."""
        c = Circuit()
        c.h(0)
        c.identity(0)
        c.x(0)
        # I is skipped, so depth should be 2
        assert c.depth == 2

    def test_two_qubit_gate_increases_depth(self):
        """A two-qubit gate increases depth when applied after single-qubit gates."""
        c = Circuit()
        c.h(0)
        c.x(1)
        c.cnot(0, 1)
        # h(0) sets q[0]=1, x(1) sets q[1]=1; cnot(0,1) advances both to max(1,1)+1=2
        assert c.depth == 2

    def test_overlapping_gates_depth(self):
        """Gates on overlapping qubit sets chain correctly."""
        c = Circuit()
        c.h(0)
        c.cnot(0, 1)
        c.x(1)  # depends on cnot via qubit 1
        assert c.depth == 3


# =============================================================================
# TestOriginirQasmProperties
# =============================================================================


class TestOriginirQasmProperties:
    """Tests for circuit.originir and circuit.qasm output format."""

    def test_circuit_property_alias(self):
        """circuit property returns the same as originir."""
        c = Circuit()
        c.h(0)
        assert c.circuit == c.originir

    def test_originir_header(self):
        """originir header contains QINIT and CREG."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        originir = c.originir
        assert "QINIT" in originir
        assert "CREG" in originir

    def test_qasm_header(self):
        """qasm header contains OPENQASM, qreg, creg."""
        c = Circuit()
        c.h(0)
        c.measure(0)
        qasm = c.qasm
        assert "OPENQASM 2.0" in qasm
        assert "qreg" in qasm
        assert "creg" in qasm

    def test_empty_circuit_originir(self):
        """Empty circuit produces header with zero qubits and zero cbits."""
        c = Circuit()
        originir = c.originir
        assert "QINIT 0" in originir
        assert "CREG 0" in originir

    def test_empty_circuit_qasm(self):
        """Empty circuit produces header with zero qubits and zero cbits."""
        c = Circuit()
        qasm = c.qasm
        assert "qreg q[0]" in qasm
        assert "creg c[0]" in qasm

    def test_gate_lines_are_separate(self):
        """Each gate appears on its own line in originir."""
        c = Circuit()
        c.h(0)
        c.x(0)
        c.y(0)
        lines = c.originir.strip().split("\n")
        # Skip header (2 lines) and measure lines at end
        gate_lines = [l for l in lines if not l.startswith("QINIT") and not l.startswith("CREG") and not l.startswith("MEASURE")]
        assert len(gate_lines) == 3


# =============================================================================
# TestGateCombinations
# =============================================================================


class TestGateCombinations:
    """Tests for circuits with mixed gate types."""

    def test_full_example_originir(self):
        """A circuit with mixed gates produces a valid-looking originir."""
        c = Circuit()
        c.h(0)
        c.rx(1, 0.5)
        c.cnot(0, 1)
        c.measure(0, 1)
        originir = c.originir
        assert "H" in originir
        assert "RX" in originir
        assert "CNOT" in originir
        assert "MEASURE" in originir

    def test_full_example_qasm(self):
        """A circuit with mixed gates produces a valid-looking qasm."""
        c = Circuit()
        c.h(0)
        c.rx(1, 0.5)
        c.cnot(0, 1)
        c.measure(0, 1)
        qasm = c.qasm
        assert "h" in qasm
        assert "rx" in qasm
        assert "cx" in qasm
        assert "measure" in qasm

    def test_qubit_num_after_various_gates(self):
        """qubit_num is correctly tracked after mixed gate usage."""
        c = Circuit()
        c.h(7)
        assert c.qubit_num == 8
        c.cnot(3, 5)
        assert c.qubit_num == 8  # max is still 7
        c.x(10)
        assert c.qubit_num == 11  # max is now 10

    def test_used_qubit_list(self):
        """used_qubit_list contains all qubits used by gates."""
        c = Circuit()
        c.h(0)
        c.cnot(1, 2)
        assert set(c.used_qubit_list) == {0, 1, 2}
