"""Tests for the optional_deps module.

Run with: pytest qpandalite/test/test_optional_deps.py --ignore-glob='qpandalite/test/__init__.py' -v
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# Mock qpandalite_cpp before importing any qpandalite modules
if 'qpandalite_cpp' not in sys.modules:
    mock_cpp = MagicMock()
    sys.modules['qpandalite_cpp'] = mock_cpp

# Also mock pyqpanda3
if 'pyqpanda3' not in sys.modules:
    mock_pyqpanda3 = MagicMock()
    sys.modules['pyqpanda3'] = mock_pyqpanda3
    sys.modules['pyqpanda3.core'] = MagicMock()
    sys.modules['pyqpanda3.intermediate_compiler'] = MagicMock()

import pytest

from qpandalite.task.optional_deps import (
    MissingDependencyError,
    require,
    check_quafu,
    check_qiskit,
    check_pyqpanda3,
    check_simulation,
    QUAFU_AVAILABLE,
    QISKIT_AVAILABLE,
    PYQPANDA3_AVAILABLE,
    SIMULATION_AVAILABLE,
)


class TestMissingDependencyError:
    """Tests for MissingDependencyError."""

    def test_error_message_format(self):
        """Test that error message includes install instructions."""
        error = MissingDependencyError("quafu", "quafu")
        assert "quafu" in str(error)
        assert "pip install qpandalite[quafu]" in str(error)

    def test_error_attributes(self):
        """Test error attributes are set correctly."""
        error = MissingDependencyError("qiskit", "qiskit")
        assert error.package == "qiskit"
        assert error.extra == "qiskit"

    def test_is_import_error_subclass(self):
        """Test that MissingDependencyError is an ImportError."""
        error = MissingDependencyError("test", "test")
        assert isinstance(error, ImportError)


class TestRequireFunction:
    """Tests for the require function."""

    def test_require_missing_module(self):
        """Test require raises MissingDependencyError for missing module."""
        with pytest.raises(MissingDependencyError) as exc_info:
            require("nonexistent_module_xyz", "test")
        assert exc_info.value.package == "nonexistent_module_xyz"

    def test_require_existing_module(self):
        """Test require returns module for existing module."""
        import os
        mod = require("os", "test")
        assert mod is os


class TestCheckFunctions:
    """Tests for availability check functions."""

    def test_check_quafu_returns_bool(self):
        """Test check_quafu returns boolean."""
        result = check_quafu()
        assert isinstance(result, bool)

    def test_check_qiskit_returns_bool(self):
        """Test check_qiskit returns boolean."""
        result = check_qiskit()
        assert isinstance(result, bool)

    def test_check_pyqpanda3_returns_bool(self):
        """Test check_pyqpanda3 returns boolean."""
        result = check_pyqpanda3()
        assert isinstance(result, bool)

    def test_check_simulation_returns_bool(self):
        """Test check_simulation returns boolean."""
        result = check_simulation()
        assert isinstance(result, bool)


class TestAvailabilityFlags:
    """Tests for pre-computed availability flags."""

    def test_quafu_available_is_bool(self):
        """Test QUAFU_AVAILABLE is boolean."""
        assert isinstance(QUAFU_AVAILABLE, bool)

    def test_qiskit_available_is_bool(self):
        """Test QISKIT_AVAILABLE is boolean."""
        assert isinstance(QISKIT_AVAILABLE, bool)

    def test_pyqpanda3_available_is_bool(self):
        """Test PYQPANDA3_AVAILABLE is boolean."""
        assert isinstance(PYQPANDA3_AVAILABLE, bool)

    def test_simulation_available_is_bool(self):
        """Test SIMULATION_AVAILABLE is boolean."""
        assert isinstance(SIMULATION_AVAILABLE, bool)
