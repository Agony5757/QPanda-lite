"""Tests for the dummy_adapter module."""

from __future__ import annotations

import os
import sys
import pytest
from unittest.mock import MagicMock

from qpandalite.task.optional_deps import SIMULATION_AVAILABLE


# Check if we can actually run simulations (not just check deps)
def _can_run_simulation():
    """Check if simulation can actually run (not just deps installed)."""
    try:
        from qpandalite.simulator import OriginIR_Simulator
        # Try to create a simple simulator to verify it works
        return True
    except ImportError:
        return False


CAN_RUN_SIMULATION = _can_run_simulation()


@pytest.mark.skipif(
    not SIMULATION_AVAILABLE,
    reason="simulation dependencies not installed"
)
class TestDummyAdapter:
    """Tests for DummyAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create a DummyAdapter instance."""
        from qpandalite.task.adapters.dummy_adapter import DummyAdapter
        return DummyAdapter()

    def test_name(self, adapter):
        """Test adapter name."""
        assert adapter.name == "dummy"

    def test_is_available(self, adapter):
        """Test is_available returns True."""
        assert adapter.is_available()

    def test_translate_circuit(self, adapter):
        """Test translate_circuit returns circuit unchanged."""
        circuit = "QINIT 2\nH q[0]"
        result = adapter.translate_circuit(circuit)
        assert result == circuit

    @pytest.mark.skipif(
        not CAN_RUN_SIMULATION,
        reason="Cannot run simulation (qpandalite_cpp not available)"
    )
    def test_query_returns_result(self, adapter):
        """Test query returns a result dict."""
        circuit = "QINIT 2\nH q[0]\nMEASURE q[0]"
        task_id = adapter.submit(circuit, shots=1000)

        result = adapter.query(task_id)

        assert "status" in result
        assert result["status"] == "success"
        assert "result" in result

    def test_query_nonexistent_task(self, adapter):
        """Test query for nonexistent task returns failed."""
        result = adapter.query("nonexistent-task-id")

        assert result["status"] == "failed"
        assert "error" in result

    @pytest.mark.skipif(
        not CAN_RUN_SIMULATION,
        reason="Cannot run simulation (qpandalite_cpp not available)"
    )
    def test_deterministic_task_id(self, adapter):
        """Test that same circuit produces same task ID."""
        circuit = "QINIT 2\nH q[0]\nMEASURE q[0]"

        task_id1 = adapter.submit(circuit)
        task_id2 = adapter.submit(circuit)

        assert task_id1 == task_id2

    @pytest.mark.skipif(
        not CAN_RUN_SIMULATION,
        reason="Cannot run simulation (qpandalite_cpp not available)"
    )
    def test_different_circuits_different_ids(self, adapter):
        """Test that different circuits produce different task IDs."""
        circuit1 = "QINIT 2\nH q[0]\nMEASURE q[0]"
        circuit2 = "QINIT 2\nX q[0]\nMEASURE q[0]"

        task_id1 = adapter.submit(circuit1)
        task_id2 = adapter.submit(circuit2)

        assert task_id1 != task_id2

    def test_submit_batch(self, adapter):
        """Test submitting multiple circuits."""
        circuits = [
            "QINIT 2\nH q[0]\nMEASURE q[0]",
            "QINIT 2\nX q[0]\nMEASURE q[0]",
        ]

        task_ids = adapter.submit_batch(circuits, shots=1000)

        assert len(task_ids) == 2
        assert all(isinstance(tid, str) for tid in task_ids)

    @pytest.mark.skipif(
        not CAN_RUN_SIMULATION,
        reason="Cannot run simulation (qpandalite_cpp not available)"
    )
    def test_query_batch(self, adapter):
        """Test querying multiple tasks."""
        circuits = [
            "QINIT 2\nH q[0]\nMEASURE q[0]",
            "QINIT 2\nX q[0]\nMEASURE q[0]",
        ]
        task_ids = adapter.submit_batch(circuits, shots=1000)

        result = adapter.query_batch(task_ids)

        assert result["status"] == "success"
        assert len(result["result"]) == 2

    def test_clear_cache(self, adapter):
        """Test clearing the cache."""
        circuit = "QINIT 2\nH q[0]\nMEASURE q[0]"
        task_id = adapter.submit(circuit)

        adapter.clear_cache()

        result = adapter.query(task_id)
        assert result["status"] == "failed"


class TestQPANDALITEDummyEnv:
    """Tests for QPANDALITE_DUMMY environment variable."""

    def test_env_variable_true(self, monkeypatch):
        """Test QPANDALITE_DUMMY=true is recognized."""
        monkeypatch.setenv("QPANDALITE_DUMMY", "true")
        # Re-import to pick up new env var
        import importlib
        import qpandalite.task.adapters.dummy_adapter as dummy_mod
        importlib.reload(dummy_mod)

        assert dummy_mod.QPANDALITE_DUMMY is True

    def test_env_variable_false(self, monkeypatch):
        """Test QPANDALITE_DUMMY=false is recognized as false."""
        monkeypatch.setenv("QPANDALITE_DUMMY", "false")
        import importlib
        import qpandalite.task.adapters.dummy_adapter as dummy_mod
        importlib.reload(dummy_mod)

        assert dummy_mod.QPANDALITE_DUMMY is False

    def test_env_variable_1(self, monkeypatch):
        """Test QPANDALITE_DUMMY=1 is recognized as true."""
        monkeypatch.setenv("QPANDALITE_DUMMY", "1")
        import importlib
        import qpandalite.task.adapters.dummy_adapter as dummy_mod
        importlib.reload(dummy_mod)

        assert dummy_mod.QPANDALITE_DUMMY is True


class TestMissingSimulationDeps:
    """Test error handling when simulation deps are missing."""

    def test_init_without_simulation_raises(self, monkeypatch):
        """Test that DummyAdapter raises error without simulation deps."""
        # Mock check_simulation to return False
        import qpandalite.task.optional_deps as deps_mod
        original_check = deps_mod.check_simulation
        deps_mod.check_simulation = lambda: False
        deps_mod.SIMULATION_AVAILABLE = False

        try:
            with pytest.raises(deps_mod.MissingDependencyError) as exc_info:
                from qpandalite.task.adapters.dummy_adapter import DummyAdapter
                DummyAdapter()

            assert "simulation" in str(exc_info.value)
        finally:
            # Restore original function
            deps_mod.check_simulation = original_check
            deps_mod.SIMULATION_AVAILABLE = original_check()
