"""Unit tests for qpandalite/analyzer/result_adapter.py"""

import numpy as np
import pytest

from qpandalite.analyzer.result_adapter import (
    convert_originq_result,
    convert_quafu_result,
    shots2prob,
    kv2list,
    list2kv,
    normalize_result,
    QASMResultAdapter,
)


# =============================================================================
# Test data (module-level constants)
# =============================================================================

ORIGINQ_SINGLE = {"key": ["0x1", "0x2", "0x7"], "value": [10, 20, 9970]}
QUAFU_SINGLE = [{"res": '{"00": 512, "11": 488}'}]
QUAFU_MULTI = [
    {"res": '{"00": 512, "11": 488}'},
    {"res": '{"01": 300, "10": 700}'},
]


# =============================================================================
# convert_originq_result
# =============================================================================

class TestConvertOriginqResult:
    """Tests for convert_originq_result."""

    def test_single_keyvalue_prob_reverse_bin(self):
        """style='keyvalue', prob_or_shots='prob', reverse_key=True, key_style='bin'.
        
        Keys are reversed binary strings: 0x1->'001'->'100'->'100', 0x2->'010'->'010',
        0x7->'111'->'111'. Values normalized by total=10000.
        """
        result = convert_originq_result(
            ORIGINQ_SINGLE,
            style="keyvalue",
            prob_or_shots="prob",
            reverse_key=True,
            key_style="bin",
        )
        assert result["100"] == pytest.approx(0.001)
        assert result["010"] == pytest.approx(0.002)
        assert result["111"] == pytest.approx(0.997)

    def test_single_keyvalue_prob_reverse_dec(self):
        """style='keyvalue', prob_or_shots='prob', reverse_key=True, key_style='dec'.
        
        Keys are reversed then converted to integers:
        0x1=1->'001'->'100'->int 4
        0x2=2->'010'->'010'->int 2
        0x7=7->'111'->'111'->int 7
        """
        result = convert_originq_result(
            ORIGINQ_SINGLE,
            style="keyvalue",
            prob_or_shots="prob",
            reverse_key=True,
            key_style="dec",
        )
        assert result[4] == pytest.approx(0.001)
        assert result[2] == pytest.approx(0.002)
        assert result[7] == pytest.approx(0.997)

    def test_single_keyvalue_prob_no_reverse(self):
        """style='keyvalue', prob_or_shots='prob', reverse_key=False.
        
        Keys are binary strings (not reversed):
        0x1=1->'001', 0x2=2->'010', 0x7=7->'111'
        """
        result = convert_originq_result(
            ORIGINQ_SINGLE,
            style="keyvalue",
            prob_or_shots="prob",
            reverse_key=False,
        )
        assert result["001"] == pytest.approx(0.001)
        assert result["010"] == pytest.approx(0.002)
        assert result["111"] == pytest.approx(0.997)

    def test_single_keyvalue_shots(self):
        """style='keyvalue', prob_or_shots='shots', reverse_key=True."""
        result = convert_originq_result(
            ORIGINQ_SINGLE,
            style="keyvalue",
            prob_or_shots="shots",
            reverse_key=True,
        )
        assert result["100"] == 10
        assert result["010"] == 20
        assert result["111"] == 9970

    def test_single_keyvalue_no_reverse_shots(self):
        """style='keyvalue', prob_or_shots='shots', reverse_key=False."""
        result = convert_originq_result(
            ORIGINQ_SINGLE,
            style="keyvalue",
            prob_or_shots="shots",
            reverse_key=False,
        )
        assert result["001"] == 10
        assert result["010"] == 20
        assert result["111"] == 9970

    def test_single_list_style(self):
        """style='list', prob_or_shots='prob', reverse_key=True.
        
        When style='list', key_style becomes 'dec' internally.
        Keys after reverse (dec): 0x1=1->4, 0x2=2->2, 0x7=7->7.
        List length = 2**3 = 8.
        """
        result = convert_originq_result(
            ORIGINQ_SINGLE,
            style="list",
            prob_or_shots="prob",
            reverse_key=True,
        )
        assert len(result) == 8
        assert result[4] == pytest.approx(0.001)
        assert result[2] == pytest.approx(0.002)
        assert result[7] == pytest.approx(0.997)
        assert result[0] == 0
        assert result[1] == 0

    def test_single_list_style_no_reverse(self):
        """style='list', prob_or_shots='prob', reverse_key=False."""
        result = convert_originq_result(
            ORIGINQ_SINGLE,
            style="list",
            prob_or_shots="prob",
            reverse_key=False,
        )
        assert len(result) == 8
        assert result[1] == pytest.approx(0.001)
        assert result[2] == pytest.approx(0.002)
        assert result[7] == pytest.approx(0.997)

    def test_qubit_num_override(self):
        """qubit_num parameter overrides the guessed qubit number."""
        result = convert_originq_result(
            {"key": ["0x1", "0x2"], "value": [1, 1]},
            style="list",
            prob_or_shots="prob",
            reverse_key=False,
            qubit_num=4,  # 4 qubits -> length 16
        )
        assert len(result) == 16

    def test_invalid_style_raises(self):
        with pytest.raises(ValueError, match="style only accepts"):
            convert_originq_result(ORIGINQ_SINGLE, style="invalid")

    def test_invalid_prob_or_shots_raises(self):
        with pytest.raises(ValueError, match="prob_or_shots only accepts"):
            convert_originq_result(ORIGINQ_SINGLE, prob_or_shots="invalid")

    def test_invalid_key_style_raises(self):
        with pytest.raises(ValueError, match="key_style must be either"):
            convert_originq_result(ORIGINQ_SINGLE, key_style="invalid")

    # --- input type: list of dicts ---

    def test_list_input_returns_list(self):
        """List input returns a list of results."""
        results = convert_originq_result([ORIGINQ_SINGLE, ORIGINQ_SINGLE])
        assert isinstance(results, list)
        assert len(results) == 2
        assert isinstance(results[0], dict)

    def test_list_input_list_style(self):
        """List of results with style='list'."""
        results = convert_originq_result([ORIGINQ_SINGLE], style="list")
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], list)

    def test_list_input_shots(self):
        """List input with prob_or_shots='shots'."""
        results = convert_originq_result(
            [ORIGINQ_SINGLE, ORIGINQ_SINGLE],
            style="keyvalue",
            prob_or_shots="shots",
            reverse_key=True,
        )
        assert len(results) == 2
        assert results[0]["100"] == 10
        assert results[1]["100"] == 10


# =============================================================================
# convert_quafu_result
# =============================================================================

class TestConvertQuafuResult:
    """Tests for convert_quafu_result."""

    def test_json_parsing(self):
        """JSON string in 'res' field is correctly parsed.
        
        convert_quafu_result always wraps output in a list (even for single input).
        With style='keyvalue', returns [[{key: value}]].
        """
        result = convert_quafu_result(
            QUAFU_SINGLE,
            style="keyvalue",
            prob_or_shots="shots",
            reverse_key=False,
        )
        # Result is [[dict]] — extra list wrapping for single input
        assert isinstance(result, list)
        inner = result[0]
        assert isinstance(inner, list)
        inner_dict = inner[0]
        assert inner_dict["00"] == 512
        assert inner_dict["11"] == 488

    def test_keyvalue_prob_reverse_bin(self):
        """style='keyvalue', prob_or_shots='prob', reverse_key=True.
        
        Keys are binary strings from JSON: '00', '11'.
        With reverse=True: '00' reversed='00' (same), '11' reversed='11' (same).
        """
        result = convert_quafu_result(
            QUAFU_SINGLE,
            style="keyvalue",
            prob_or_shots="prob",
            reverse_key=True,
            key_style="bin",
        )
        inner_dict = result[0][0]
        assert inner_dict["00"] == pytest.approx(0.512)
        assert inner_dict["11"] == pytest.approx(0.488)

    def test_keyvalue_prob_no_reverse(self):
        result = convert_quafu_result(
            QUAFU_SINGLE,
            style="keyvalue",
            prob_or_shots="prob",
            reverse_key=False,
        )
        inner_dict = result[0][0]
        assert inner_dict["00"] == pytest.approx(0.512)
        assert inner_dict["11"] == pytest.approx(0.488)

    def test_keyvalue_shots(self):
        result = convert_quafu_result(
            QUAFU_SINGLE,
            style="keyvalue",
            prob_or_shots="shots",
            reverse_key=False,
        )
        inner_dict = result[0][0]
        assert inner_dict["00"] == 512
        assert inner_dict["11"] == 488

    def test_list_style(self):
        """style='list', prob_or_shots='prob', reverse_key=False.
        
        When style='list', key_style becomes 'dec' internally.
        Keys: '00'->0, '11'->3.
        List length = 2**2 = 4.
        """
        result = convert_quafu_result(
            QUAFU_SINGLE,
            style="list",
            prob_or_shots="prob",
            reverse_key=False,
        )
        assert isinstance(result, list)
        inner = result[0]
        assert isinstance(inner, list)
        assert len(inner) == 4
        assert inner[0] == pytest.approx(0.512)
        assert inner[3] == pytest.approx(0.488)
        assert inner[1] == 0
        assert inner[2] == 0

    def test_list_style_reverse(self):
        """With symmetric strings '00' and '11', reversal has no effect."""
        result = convert_quafu_result(
            QUAFU_SINGLE,
            style="list",
            prob_or_shots="prob",
            reverse_key=True,
        )
        inner = result[0]
        assert inner[0] == pytest.approx(0.512)
        assert inner[3] == pytest.approx(0.488)

    def test_qubit_num_override(self):
        """qubit_num=3 overrides to length 8 even though only 2 qubits in data."""
        quafu_result = [{"res": '{"0": 1, "1": 1}'}]  # 1 qubit
        result = convert_quafu_result(
            quafu_result,
            style="list",
            prob_or_shots="prob",
            reverse_key=False,
            qubit_num=3,  # 3 qubits -> list length 8
        )
        assert len(result[0]) == 8

    def test_multi_result_list(self):
        """Multiple Quafu results each wrapped in an extra list."""
        results = convert_quafu_result(
            QUAFU_MULTI,
            style="keyvalue",
            prob_or_shots="shots",
            reverse_key=False,
        )
        assert len(results) == 2
        # First: '00'->0, '11'->3
        assert results[0][0]["00"] == 512
        assert results[0][0]["11"] == 488
        # Second: '01'->1, '10'->2
        assert results[1][0]["01"] == 300
        assert results[1][0]["10"] == 700

    def test_invalid_style_raises(self):
        with pytest.raises(ValueError, match="style only accepts"):
            convert_quafu_result(QUAFU_SINGLE, style="invalid")

    def test_invalid_prob_or_shots_raises(self):
        with pytest.raises(ValueError, match="prob_or_shots only accepts"):
            convert_quafu_result(QUAFU_SINGLE, prob_or_shots="invalid")

    def test_invalid_key_style_raises(self):
        with pytest.raises(ValueError, match="key_style must be either"):
            convert_quafu_result(QUAFU_SINGLE, key_style="invalid")


# =============================================================================
# shots2prob
# =============================================================================

class TestShots2Prob:
    """Tests for shots2prob."""

    def test_basic(self):
        result = shots2prob({"00": 512, "11": 488})
        assert result["00"] == pytest.approx(0.512)
        assert result["11"] == pytest.approx(0.488)

    def test_with_total_shots(self):
        result = shots2prob({"00": 512, "11": 488}, total_shots=1000)
        assert result["00"] == pytest.approx(0.512)
        assert result["11"] == pytest.approx(0.488)

    def test_total_shots_override(self):
        """total_shots can be different from sum of values."""
        result = shots2prob({"00": 500, "11": 500}, total_shots=2000)
        assert result["00"] == pytest.approx(0.25)
        assert result["11"] == pytest.approx(0.25)

    def test_empty_dict(self):
        result = shots2prob({})
        assert result == {}

    def test_single_entry(self):
        result = shots2prob({"00": 1000})
        assert result["00"] == pytest.approx(1.0)


# =============================================================================
# kv2list
# =============================================================================

class TestKv2List:
    """Tests for kv2list."""

    def test_standard(self):
        # 2-qubit system: length 4, keys 0 and 3 have values
        result = kv2list({0: 0.1, 3: 0.9}, 2)
        assert len(result) == 4
        assert result[0] == 0.1
        assert result[3] == 0.9
        assert result[1] == 0
        assert result[2] == 0

    def test_some_zero_entries(self):
        result = kv2list({0: 0.25, 1: 0.25, 2: 0.25, 3: 0.25}, 2)
        assert result == [0.25, 0.25, 0.25, 0.25]

    def test_all_zeros(self):
        result = kv2list({0: 0, 1: 0, 2: 0, 3: 0}, 2)
        assert result == [0, 0, 0, 0]

    def test_3_qubits(self):
        result = kv2list({1: 0.5, 7: 0.5}, 3)
        assert len(result) == 8
        assert result[1] == 0.5
        assert result[7] == 0.5
        assert result[0] == 0


# =============================================================================
# list2kv
# =============================================================================

class TestList2Kv:
    """Tests for list2kv."""

    def test_standard(self):
        result = list2kv(["00", "01", "10", "00", "11", "00"])
        assert result["00"] == 3
        assert result["01"] == 1
        assert result["10"] == 1
        assert result["11"] == 1

    def test_empty_list(self):
        result = list2kv([])
        assert result == {}

    def test_single_item(self):
        result = list2kv(["00"])
        assert result["00"] == 1

    def test_all_same(self):
        result = list2kv(["00", "00", "00"])
        assert result["00"] == 3

    def test_decimal_string_keys(self):
        result = list2kv(["0", "1", "2"])
        assert result["0"] == 1
        assert result["1"] == 1
        assert result["2"] == 1


# =============================================================================
# normalize_result
# =============================================================================

class TestNormalizeResult:
    """Tests for normalize_result."""

    def test_dict_input(self):
        result = normalize_result({"00": 512, "11": 488})
        assert result["00"] == pytest.approx(0.512)
        assert result["11"] == pytest.approx(0.488)

    def test_list_input(self):
        result = normalize_result(["00", "01", "10", "00", "11", "00"])
        assert result["00"] == pytest.approx(3 / 6)
        assert result["01"] == pytest.approx(1 / 6)
        assert result["10"] == pytest.approx(1 / 6)
        assert result["11"] == pytest.approx(1 / 6)

    def test_empty_dict(self):
        result = normalize_result({})
        assert result == {}

    def test_empty_list(self):
        result = normalize_result([])
        assert result == {}

    def test_dict_already_sums_to_one(self):
        result = normalize_result({"00": 0.5, "11": 0.5})
        assert result["00"] == pytest.approx(0.5)
        assert result["11"] == pytest.approx(0.5)

    def test_single_entry(self):
        result = normalize_result({"00": 100})
        assert result["00"] == pytest.approx(1.0)


# =============================================================================
# QASMResultAdapter
# =============================================================================

class TestQASMResultAdapter:
    """Tests for QASMResultAdapter class."""

    def test_counts_only(self):
        adapter = QASMResultAdapter(counts={"00": 512, "11": 488})
        assert adapter.counts == {"00": 512, "11": 488}
        assert adapter.shots == 1000
        assert adapter.metadata["simulator"] == "qasm_simulator"
        assert adapter.metadata["shots"] == 1000
        assert adapter.probabilities["00"] == pytest.approx(0.512)
        assert adapter.probabilities["11"] == pytest.approx(0.488)

    def test_counts_plus_shots(self):
        """When shots is provided, probabilities are computed against that total."""
        adapter = QASMResultAdapter(counts={"00": 512, "11": 488}, shots=2000)
        assert adapter.shots == 2000
        # Probabilities are always computed from counts / total_counts (not provided shots)
        assert adapter.probabilities["00"] == pytest.approx(0.512)
        assert adapter.probabilities["11"] == pytest.approx(0.488)

    def test_counts_plus_metadata(self):
        adapter = QASMResultAdapter(
            counts={"00": 512, "11": 488},
            metadata={"simulator": "custom_sim", "noise": "none"},
        )
        assert adapter.metadata["simulator"] == "custom_sim"
        assert adapter.metadata["noise"] == "none"
        assert adapter.metadata["shots"] == 1000  # default shots still set

    def test_counts_plus_shots_and_metadata(self):
        adapter = QASMResultAdapter(
            counts={"00": 512, "11": 488},
            shots=2000,
            metadata={"simulator": "custom_sim"},
        )
        assert adapter.shots == 2000
        assert adapter.metadata["simulator"] == "custom_sim"
        assert adapter.metadata["shots"] == 2000

    def test_probabilities_computed_correctly(self):
        adapter = QASMResultAdapter(counts={"00": 1, "01": 2, "10": 3, "11": 4})
        total = 10
        assert adapter.probabilities["00"] == pytest.approx(0.1)
        assert adapter.probabilities["01"] == pytest.approx(0.2)
        assert adapter.probabilities["10"] == pytest.approx(0.3)
        assert adapter.probabilities["11"] == pytest.approx(0.4)
        total_prob = sum(adapter.probabilities.values())
        assert total_prob == pytest.approx(1.0)

    def test_to_dict(self):
        adapter = QASMResultAdapter(
            counts={"00": 512, "11": 488},
            metadata={"simulator": "my_sim"},
        )
        d = adapter.to_dict()
        assert d["counts"] == {"00": 512, "11": 488}
        assert d["probabilities"]["00"] == pytest.approx(0.512)
        assert d["probabilities"]["11"] == pytest.approx(0.488)
        assert d["shots"] == 1000
        assert d["metadata"]["simulator"] == "my_sim"

    def test_repr(self):
        adapter = QASMResultAdapter(
            counts={"00": 512, "11": 488},
            metadata={"simulator": "my_sim"},
        )
        r = repr(adapter)
        assert "QASMResultAdapter" in r
        assert "shots=1000" in r
        assert "outcomes=2" in r
        assert "metadata" in r

    def test_repr_with_custom_metadata(self):
        adapter = QASMResultAdapter(
            counts={"00": 1},
            metadata={"note": "test"},
        )
        r = repr(adapter)
        assert "QASMResultAdapter" in r
        assert "shots=1" in r
