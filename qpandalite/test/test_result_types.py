"""Tests for the result_types module."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# Mock qpandalite_cpp before importing any qpandalite modules
if 'qpandalite_cpp' not in sys.modules:
    sys.modules['qpandalite_cpp'] = MagicMock()

import pytest

from qpandalite.task.result_types import UnifiedResult


class TestUnifiedResult:
    """Tests for UnifiedResult dataclass."""

    def test_from_counts_basic(self):
        """Test creating UnifiedResult from counts."""
        counts = {"00": 512, "11": 488}
        result = UnifiedResult.from_counts(counts, "quafu", "task-1")

        assert result.counts == counts
        assert result.shots == 1000
        assert result.platform == "quafu"
        assert result.task_id == "task-1"

    def test_from_counts_probabilities_computed(self):
        """Test probabilities are computed correctly from counts."""
        counts = {"00": 512, "11": 488}
        result = UnifiedResult.from_counts(counts, "test", "test")

        assert result.probabilities["00"] == pytest.approx(0.512)
        assert result.probabilities["11"] == pytest.approx(0.488)

    def test_from_probabilities_basic(self):
        """Test creating UnifiedResult from probabilities."""
        probs = {"00": 0.5, "11": 0.5}
        result = UnifiedResult.from_probabilities(probs, 1000, "originq", "task-2")

        assert result.probabilities == probs
        assert result.shots == 1000
        assert result.platform == "originq"
        assert result.task_id == "task-2"

    def test_from_probabilities_counts_computed(self):
        """Test counts are computed correctly from probabilities."""
        probs = {"00": 0.5, "11": 0.5}
        result = UnifiedResult.from_probabilities(probs, 1000, "test", "test")

        assert result.counts["00"] == 500
        assert result.counts["11"] == 500

    def test_optional_fields(self):
        """Test optional fields can be set."""
        result = UnifiedResult.from_counts(
            {"0": 1000},
            "ibm",
            "task-3",
            backend_name="ibm_brisbane",
            execution_time=1.5,
        )

        assert result.backend_name == "ibm_brisbane"
        assert result.execution_time == 1.5

    def test_empty_counts(self):
        """Test handling of empty counts."""
        result = UnifiedResult.from_counts({}, "test", "task-4")

        assert result.counts == {}
        assert result.probabilities == {}
        assert result.shots == 0

    def test_get_expectation_z(self):
        """Test Z expectation value computation."""
        # All zeros: <Z> = 1
        result0 = UnifiedResult.from_counts({"0": 1000}, "test", "test")
        assert result0.get_expectation("Z") == pytest.approx(1.0)

        # All ones: <Z> = -1
        result1 = UnifiedResult.from_counts({"1": 1000}, "test", "test")
        assert result1.get_expectation("Z") == pytest.approx(-1.0)

        # Mixed: <Z> = 0
        result_mixed = UnifiedResult.from_counts({"0": 500, "1": 500}, "test", "test")
        assert result_mixed.get_expectation("Z") == pytest.approx(0.0)

    def test_get_expectation_unsupported_observable(self):
        """Test that unsupported observables raise NotImplementedError."""
        result = UnifiedResult.from_counts({"0": 1000}, "test", "test")

        with pytest.raises(NotImplementedError):
            result.get_expectation("X")

    def test_error_message_field(self):
        """Test error_message field."""
        result = UnifiedResult(
            counts={},
            probabilities={},
            shots=0,
            platform="test",
            task_id="failed-task",
            error_message="Connection timeout",
        )

        assert result.error_message == "Connection timeout"

    def test_raw_result_stored(self):
        """Test raw_result can store original result object."""
        raw = {"original": "data"}
        result = UnifiedResult.from_counts(
            {"0": 1000}, "test", "test", raw_result=raw
        )

        assert result.raw_result == raw
