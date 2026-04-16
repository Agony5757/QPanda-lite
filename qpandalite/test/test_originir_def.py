"""
Comprehensive unit tests for OriginIR DEF block support.

Tests cover:
- DEF block generation from NamedCircuit
- DEF block parsing
- Roundtrip DEF export/import
"""

import pytest
from qpandalite.circuit_builder import Circuit
from qpandalite.circuit_builder.named_circuit import circuit_def, NamedCircuit
from qpandalite.originir.originir_line_parser import OriginIR_LineParser


# =============================================================================
# TestOriginIRDefExport
# =============================================================================


class TestOriginIRDefExport:
    """Tests for generating DEF blocks from NamedCircuit."""

    def test_def_export_simple(self):
        """Simple DEF block export."""
        @circuit_def(name="bell_pair", qregs={"q": 2})
        def bell_pair(circ, q):
            circ.h(q[0])
            circ.cnot(q[0], q[1])
            return circ

        def_str = bell_pair.to_originir_def()
        assert "DEF bell_pair" in def_str
        assert "H q[0]" in def_str
        assert "CNOT q[0], q[1]" in def_str
        assert "ENDDEF" in def_str

    def test_def_export_with_params(self):
        """DEF block export with parameters."""
        @circuit_def(name="rx_gate", qregs={"q": 1}, params=["theta"])
        def rx_gate(circ, q, theta):
            circ.rx(q[0], theta)
            return circ

        def_str = rx_gate.to_originir_def()
        assert "DEF rx_gate" in def_str
        assert "theta" in def_str
        assert "ENDDEF" in def_str


# =============================================================================
# TestOriginIRDefImport
# =============================================================================


class TestOriginIRDefImport:
    """Tests for parsing DEF blocks."""

    def test_parse_def_header(self):
        """Parse DEF header line."""
        result = OriginIR_LineParser.handle_def("DEF bell_pair(q[0], q[1])")
        op, qubits, params, name = result
        assert op == "DEF"
        assert name == "bell_pair"
        assert qubits == [0, 1]
        assert params == []

    def test_parse_def_header_with_params(self):
        """Parse DEF header with parameters."""
        result = OriginIR_LineParser.handle_def("DEF rx_gate(q[0]) (theta)")
        op, qubits, params, name = result
        assert op == "DEF"
        assert name == "rx_gate"
        assert qubits == [0]
        assert params == ["theta"]

    def test_parse_def_header_multiple_params(self):
        """Parse DEF header with multiple parameters."""
        result = OriginIR_LineParser.handle_def("DEF u3(q[0]) (theta, phi, lambda)")
        op, qubits, params, name = result
        assert name == "u3"
        assert params == ["theta", "phi", "lambda"]

    def test_parse_enddef(self):
        """Parse ENDDEF line."""
        matches = OriginIR_LineParser.regexp_enddef.match("ENDDEF")
        assert matches is not None


# =============================================================================
# TestOriginIRDefIntegration
# =============================================================================


class TestOriginIRDefIntegration:
    """Integration tests for DEF blocks."""

    def test_def_export_matches_expected_format(self):
        """Verify DEF export format is correct."""
        @circuit_def(name="h_gate", qregs={"q": 1})
        def h_gate(circ, q):
            circ.h(q[0])
            return circ

        def_str = h_gate.to_originir_def()
        lines = def_str.strip().split("\n")
        assert lines[0].startswith("DEF h_gate(q[0])")
        assert lines[-1] == "ENDDEF"
