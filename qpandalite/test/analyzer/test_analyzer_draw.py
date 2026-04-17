"""Tests for qpandalite/analyzer/draw.py"""

import pytest

from qpandalite.analyzer.draw import (
    _parse_measured_result,
    plot_histogram,
    plot_distribution,
)


# ---------------------------------------------------------------------------
# Mock axes – provides all methods called by plot_histogram / plot_distribution
# ---------------------------------------------------------------------------

class _MockAxes:
    """Minimal mock for matplotlib Axes."""

    def __init__(self):
        self.calls = []

    def bar(self, x, values, **kwargs):
        self.calls.append(("bar", x, values, kwargs))
        return self

    def axhline(self, y, **kwargs):
        self.calls.append(("axhline", y, kwargs))
        return self

    def set_xticks(self, ticks):
        self.calls.append(("set_xticks", ticks))

    def set_xticklabels(self, labels, rotation=None, ha=None):
        self.calls.append(("set_xticklabels", labels, rotation, ha))

    def set_xlabel(self, label):
        self.calls.append(("set_xlabel", label))

    def set_ylabel(self, label):
        self.calls.append(("set_ylabel", label))

    def set_title(self, title):
        self.calls.append(("set_title", title))

    def set_ylim(self, bottom, top=None):
        self.calls.append(("set_ylim", bottom, top))

    def grid(self, axis=None, linestyle=None, alpha=None):
        self.calls.append(("grid", axis, linestyle, alpha))

    def legend(self, loc=None):
        self.calls.append(("legend", loc))


class _MockFigure:
    """Minimal mock for matplotlib Figure."""

    def __init__(self):
        self.calls = []

    def tight_layout(self):
        self.calls.append(("tight_layout",))

    def show(self):
        self.calls.append(("show",))


# ---------------------------------------------------------------------------
# Monkeypatch fixture – prevent plt.show() / plt.subplots() from opening windows
#
# We patch matplotlib.pyplot.subplots directly (not via a string path) because
# pytest's monkeypatch.resolve() cannot traverse through a non-package module
# file like qpandalite/analyzer/draw.py to find submodules.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _patch_matplotlib(monkeypatch):
    """Patches plt.show and plt.subplots to return mock objects."""
    import matplotlib.pyplot as plt

    # Keep a reference to the real plt so we can patch it
    _real_pyplot = plt

    def _mock_subplots(**kwargs):
        fig = _MockFigure()
        ax = _MockAxes()
        return fig, ax

    # Patch in-place on the module object
    monkeypatch.setattr(_real_pyplot, "show", lambda: None)
    monkeypatch.setattr(_real_pyplot, "subplots", _mock_subplots)


# ---------------------------------------------------------------------------
# _parse_measured_result – dict format
# ---------------------------------------------------------------------------

class TestParseDictFormat:
    """Tests for dict input to _parse_measured_result."""

    def test_valid_dict_two_qubits(self):
        result = {"00": 0.5, "11": 0.5}
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(result, (10, 6))
        assert labels == ["00", "11"]
        assert values == [0.5, 0.5]
        assert nqubit == 2
        assert adj_figsize == (10, 6)
        assert rot == 0  # nqubit < 7

    def test_valid_dict_three_qubits(self):
        result = {"000": 0.125, "011": 0.25, "101": 0.375, "111": 0.25}
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(result, (10, 6))
        assert len(labels) == 4
        assert nqubit == 3
        assert rot == 0

    def test_empty_dict(self):
        result = {}
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(result, (10, 6))
        assert labels == []
        assert values == []
        assert nqubit == 0
        assert adj_figsize == (10, 6)
        assert rot == 0


# ---------------------------------------------------------------------------
# _parse_measured_result – list format
# ---------------------------------------------------------------------------

class TestParseListFormat:
    """Tests for list input to _parse_measured_result."""

    def test_valid_list_1qubit(self):
        result = [0.6, 0.4]
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(result, (10, 6))
        assert labels == ["0", "1"]
        assert values == [0.6, 0.4]
        assert nqubit == 1
        assert adj_figsize == (10, 6)
        assert rot == 0  # nqubit < 7 → no rotation

    def test_valid_list_2qubits(self):
        result = [0.5, 0.0, 0.0, 0.5]
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(result, (10, 6))
        assert labels == ["00", "01", "10", "11"]
        assert nqubit == 2
        assert rot == 0

    def test_valid_list_7qubits(self):
        # 7 qubits → 128 outcomes
        n = 128
        result = [1.0 / n] * n
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(result, (10, 6))
        assert nqubit == 7
        assert rot == 30
        # figsize: max(10, 7 * 0.6) = max(10, 4.2) = 10
        assert adj_figsize == (10, 6)

    def test_valid_list_10qubits(self):
        # 10 qubits → 1024 outcomes
        n = 1024
        result = [1.0 / n] * n
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(result, (10, 6))
        assert nqubit == 10
        assert rot == 45
        # figsize: max(10, 10 * 0.4) = max(10, 4) = 10
        assert adj_figsize == (10, 6)

    def test_valid_list_12qubits_figsize_adjusted(self):
        # 12 qubits → figsize
        n = 4096
        result = [1.0 / n] * n
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(result, (10, 6))
        assert nqubit == 12
        assert rot == 45
        assert adj_figsize == (10, 6)

    def test_valid_list_20qubits_figsize_expanded(self):
        # 20 qubits → figsize: max(10, 20*0.4) = max(10, 8) = 10
        n = 1 << 20  # 1048576
        result = [1.0 / n] * n
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(result, (10, 6))
        assert nqubit == 20
        assert rot == 45
        assert adj_figsize == (10, 6)

    @pytest.mark.parametrize("non_power_of_two", [3, 5, 6, 7, 9, 10, 100])
    def test_list_not_power_of_two_raises(self, non_power_of_two):
        with pytest.raises(ValueError, match="not a power of 2"):
            _parse_measured_result([0.1] * non_power_of_two, (10, 6))

    def test_empty_list_raises(self):
        with pytest.raises(ValueError, match="not a power of 2"):
            _parse_measured_result([], (10, 6))

    def test_single_element_list_is_valid(self):
        # n=1 (2^0) is a power of 2: 1 & 0 == 0
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result([1.0], (10, 6))
        assert labels == ["0"]
        assert nqubit == 0
        assert rot == 0


# ---------------------------------------------------------------------------
# _parse_measured_result – wrong type
# ---------------------------------------------------------------------------

class TestParseWrongType:
    """Tests for invalid type input to _parse_measured_result."""

    @pytest.mark.parametrize("wrong_type", [42, 3.14, "00", set([1, 2]), None])
    def test_wrong_type_raises(self, wrong_type):
        with pytest.raises(TypeError, match="must be a dict or a list"):
            _parse_measured_result(wrong_type, (10, 6))


# ---------------------------------------------------------------------------
# _parse_measured_result – rotation angle and figsize adjustment
# ---------------------------------------------------------------------------

class TestParseRotationAndFigsize:
    """Tests for rotation angle and figsize adjustment logic."""

    def test_nqubit_1_no_rotation(self):
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(
            {"0": 1.0}, (10, 6)
        )
        assert nqubit == 1
        assert rot == 0

    def test_nqubit_7_rotation_30(self):
        # 7 qubits → 128 outcomes
        n = 128
        result = {f"{i:07b}": 1.0 / n for i in range(n)}
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(result, (10, 6))
        assert nqubit == 7
        assert rot == 30

    def test_nqubit_10_rotation_45(self):
        # 10 qubits → 1024 outcomes
        n = 1024
        result = {f"{i:010b}": 1.0 / n for i in range(n)}
        labels, values, nqubit, adj_figsize, rot = _parse_measured_result(result, (10, 6))
        assert nqubit == 10
        assert rot == 45

    def test_nqubit_7_figsize_adjusted(self):
        n = 128
        result = {f"{i:07b}": 1.0 / n for i in range(n)}
        _, _, _, adj_figsize, _ = _parse_measured_result(result, (8, 5))
        # max(8, 7 * 0.6) = max(8, 4.2) = 8
        assert adj_figsize == (8, 5)

    def test_nqubit_10_figsize_adjusted(self):
        n = 1024
        result = {f"{i:010b}": 1.0 / n for i in range(n)}
        _, _, _, adj_figsize, _ = _parse_measured_result(result, (8, 5))
        # max(8, 10 * 0.4) = max(8, 4) = 8
        assert adj_figsize == (8, 5)


# ---------------------------------------------------------------------------
# _parse_measured_result – label format
# ---------------------------------------------------------------------------

class TestParseLabelsFormat:
    """Tests for the format of generated labels."""

    def test_labels_are_binary_strings(self):
        result = [0.25] * 4
        labels, _, _, _, _ = _parse_measured_result(result, (10, 6))
        assert labels == ["00", "01", "10", "11"]
        for label in labels:
            assert all(c in "01" for c in label)

    def test_labels_padded_to_nqubit(self):
        result = [0.125] * 8
        labels, _, _, _, _ = _parse_measured_result(result, (10, 6))
        assert labels == ["000", "001", "010", "011", "100", "101", "110", "111"]
        for label in labels:
            assert len(label) == 3  # 3 qubits


# ---------------------------------------------------------------------------
# plot_histogram – valid inputs (no errors raised)
# ---------------------------------------------------------------------------

class TestPlotHistogramValid:
    """Tests that plot_histogram accepts valid inputs without raising."""

    def test_dict_input(self):
        plot_histogram({"00": 0.5, "11": 0.5}, title="Bell State")

    def test_list_input(self):
        plot_histogram([0.5, 0.0, 0.0, 0.5], title="Bell State")

    def test_custom_figsize(self):
        plot_histogram([0.5, 0.5], title="Custom", figsize=(12, 8))


# ---------------------------------------------------------------------------
# plot_histogram – invalid inputs raise
# ---------------------------------------------------------------------------

class TestPlotHistogramInvalid:
    """Tests that plot_histogram raises on invalid inputs."""

    @pytest.mark.parametrize("non_power_of_two", [3, 5, 7])
    def test_list_not_power_of_two_raises(self, non_power_of_two):
        with pytest.raises(ValueError, match="not a power of 2"):
            plot_histogram([0.1] * non_power_of_two)

    def test_empty_list_raises(self):
        with pytest.raises(ValueError, match="not a power of 2"):
            plot_histogram([])

    def test_wrong_type_raises(self):
        with pytest.raises(TypeError, match="must be a dict or a list"):
            plot_histogram(42)


# ---------------------------------------------------------------------------
# plot_distribution – valid inputs (no errors raised)
# ---------------------------------------------------------------------------

class TestPlotDistributionValid:
    """Tests that plot_distribution accepts valid inputs without raising."""

    def test_dict_input(self):
        plot_distribution({"00": 0.5, "11": 0.5}, title="Bell State")

    def test_list_input(self):
        plot_distribution([0.5, 0.0, 0.0, 0.5], title="Bell State")

    def test_custom_figsize(self):
        plot_distribution([0.5, 0.5], title="Custom", figsize=(12, 8))


# ---------------------------------------------------------------------------
# plot_distribution – invalid inputs raise
# ---------------------------------------------------------------------------

class TestPlotDistributionInvalid:
    """Tests that plot_distribution raises on invalid inputs."""

    @pytest.mark.parametrize("non_power_of_two", [3, 5, 7])
    def test_list_not_power_of_two_raises(self, non_power_of_two):
        with pytest.raises(ValueError, match="not a power of 2"):
            plot_distribution([0.1] * non_power_of_two)

    def test_empty_list_raises(self):
        with pytest.raises(ValueError, match="not a power of 2"):
            plot_distribution([])

    def test_wrong_type_raises(self):
        with pytest.raises(TypeError, match="must be a dict or a list"):
            plot_distribution(42)
