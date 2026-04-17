"""Unit tests for qpandalite/analyzer/result_adapter.py"""

import numpy as np
import pytest

from qpandalite.analyzer.result_adapter import (
    shots2prob,
    kv2list,
    list2kv,
    normalize_result,
    QASMResultAdapter,
)


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
