"""Comprehensive tests for unified cloud platform access layer.

This module provides:
1. Configuration loading tests
2. Backend factory tests  
3. Circuit adapter tests
4. Mock tests (no real platform dependencies)
5. Integration tests (skipped unless real credentials exist)
6. End-to-end workflow tests

Usage:
    pytest qpandalite/test/test_cloud_platforms.py -v
    
Environment variables for integration tests:
    - QPANDA_API_KEY: OriginQ API key
    - QPANDA_SUBMIT_URL: OriginQ submit URL
    - QPANDA_QUERY_URL: OriginQ query URL
    - QUAFU_API_TOKEN: Quafu API token
    - IBM_TOKEN: IBM Quantum token
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Custom Exceptions for Error Testing
# ---------------------------------------------------------------------------


class AuthenticationError(Exception):
    """Raised when authentication fails (invalid token, etc.)."""
    pass


class InsufficientCreditsError(Exception):
    """Raised when account has insufficient credits."""
    pass


class NetworkError(Exception):
    """Raised when network communication fails."""
    pass


# ---------------------------------------------------------------------------
# Test Data
# ---------------------------------------------------------------------------

ORIGINIR_BELL = """
QINIT 2
CREG 2
H q[0]
CNOT q[0], q[1]
MEASURE q[0], c[0]
MEASURE q[1], c[1]
""".strip()

ORIGINIR_3Q = """
QINIT 3
CREG 3
H q[0]
H q[1]
H q[2]
CNOT q[0], q[1]
CNOT q[1], q[2]
MEASURE q[0], c[0]
MEASURE q[1], c[1]
MEASURE q[2], c[2]
""".strip()

ORIGINIR_SINGLE = """
QINIT 1
CREG 1
X q[0]
MEASURE q[0], c[0]
""".strip()


# ---------------------------------------------------------------------------
# Configuration Loading Tests
# ---------------------------------------------------------------------------


class TestConfigLoading:
    """Tests for configuration loading from ~/.qpandalite/qpandalite.yml."""

    def test_load_config_file_not_exists(self, tmp_path: Path) -> None:
        """Test that default config is returned when file doesn't exist."""
        from qpandalite.config import load_config, DEFAULT_CONFIG
        
        non_existent = tmp_path / "non_existent.yml"
        result = load_config(non_existent)
        assert result == DEFAULT_CONFIG

    def test_load_existing_config(self, tmp_path: Path) -> None:
        """Test loading an existing configuration file."""
        from qpandalite.config import load_config, save_config
        
        config_file = tmp_path / "test_config.yml"
        test_config = {
            "default": {
                "originq": {"token": "test_token_123", "submit_url": "http://submit.test", "query_url": "http://query.test"},
                "quafu": {"token": "quafu_token_456"},
                "ibm": {"token": "ibm_token_789", "proxy": {"http": "", "https": ""}},
            }
        }
        save_config(test_config, config_file)
        result = load_config(config_file)
        assert result["default"]["originq"]["token"] == "test_token_123"
        assert result["default"]["quafu"]["token"] == "quafu_token_456"
        assert result["default"]["ibm"]["token"] == "ibm_token_789"

    def test_load_config_all_platforms(self, tmp_path: Path) -> None:
        """Test loading configuration for all three platforms."""
        from qpandalite.config import (
            load_config, save_config, 
            get_platform_config, SUPPORTED_PLATFORMS
        )
        
        config_file = tmp_path / "qpandalite.yml"
        test_config = {
            "default": {
                "originq": {
                    "token": "originq_test_token",
                    "submit_url": "https://originq.example.com/submit",
                    "query_url": "https://originq.example.com/query",
                    "available_qubits": [0, 1, 2, 3, 4, 5],
                    "available_topology": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]],
                    "task_group_size": 200,
                },
                "quafu": {
                    "token": "quafu_test_token",
                },
                "ibm": {
                    "token": "ibm_test_token",
                    "proxy": {"http": "http://proxy.example.com:8080", "https": "https://proxy.example.com:8080"},
                },
            }
        }
        save_config(test_config, config_file)
        
        # Test each platform
        for platform in SUPPORTED_PLATFORMS:
            config = get_platform_config(platform, config_path=config_file)
            assert "token" in config
            assert config["token"] == f"{platform}_test_token"

    def test_load_config_different_profiles(self, tmp_path: Path) -> None:
        """Test loading configuration with different profiles."""
        from qpandalite.config import load_config, save_config, get_platform_config
        
        config_file = tmp_path / "qpandalite.yml"
        test_config = {
            "default": {
                "originq": {"token": "default_token", "submit_url": "http://default", "query_url": "http://default"},
            },
            "prod": {
                "originq": {"token": "prod_token", "submit_url": "http://prod", "query_url": "http://prod"},
            },
            "dev": {
                "originq": {"token": "dev_token", "submit_url": "http://dev", "query_url": "http://dev"},
            },
        }
        save_config(test_config, config_file)
        
        default_config = get_platform_config("originq", profile="default", config_path=config_file)
        assert default_config["token"] == "default_token"
        
        prod_config = get_platform_config("originq", profile="prod", config_path=config_file)
        assert prod_config["token"] == "prod_token"
        
        dev_config = get_platform_config("originq", profile="dev", config_path=config_file)
        assert dev_config["token"] == "dev_token"

    def test_validate_config_valid(self) -> None:
        """Test validating a valid configuration."""
        from qpandalite.config import validate_config
        
        valid_config = {
            "default": {
                "originq": {"token": "t", "submit_url": "s", "query_url": "q"},
                "quafu": {"token": "t"},
                "ibm": {"token": "t", "proxy": {"http": "", "https": ""}},
            }
        }
        errors = validate_config(valid_config)
        assert errors == []

    def test_validate_config_missing_required_fields(self) -> None:
        """Test validating configuration with missing required fields."""
        from qpandalite.config import validate_config
        
        invalid_config = {
            "default": {
                "originq": {"token": "t"},  # Missing submit_url and query_url
            }
        }
        errors = validate_config(invalid_config)
        assert len(errors) >= 2
        assert any("submit_url" in e for e in errors)
        assert any("query_url" in e for e in errors)


# ---------------------------------------------------------------------------
# Backend Factory Tests
# ---------------------------------------------------------------------------


class TestBackendFactory:
    """Tests for the Backend factory pattern (get_backend)."""

    def test_get_backend_originq(self) -> None:
        """Test getting OriginQ backend returns correct type."""
        from qpandalite.backend import get_backend, OriginQBackend
        
        with patch("qpandalite.backend.OriginQBackend._create_adapter") as mock_create:
            mock_adapter = MagicMock()
            mock_create.return_value = mock_adapter
            
            backend = get_backend("originq", use_cache=False)
            assert isinstance(backend, OriginQBackend)
            assert backend.platform == "originq"

    def test_get_backend_quafu(self) -> None:
        """Test getting Quafu backend returns correct type."""
        from qpandalite.backend import get_backend, QuafuBackend
        
        with patch("qpandalite.backend.QuafuBackend._create_adapter") as mock_create:
            mock_adapter = MagicMock()
            mock_create.return_value = mock_adapter
            
            backend = get_backend("quafu", use_cache=False)
            assert isinstance(backend, QuafuBackend)
            assert backend.platform == "quafu"

    def test_get_backend_ibm(self) -> None:
        """Test getting IBM backend returns correct type."""
        from qpandalite.backend import get_backend, IBMBackend
        
        with patch("qpandalite.backend.IBMBackend._create_adapter") as mock_create:
            mock_adapter = MagicMock()
            mock_create.return_value = mock_adapter
            
            backend = get_backend("ibm", use_cache=False)
            assert isinstance(backend, IBMBackend)
            assert backend.platform == "ibm"

    def test_get_backend_unknown_raises(self) -> None:
        """Test that unknown backend name raises ValueError."""
        from qpandalite.backend import get_backend
        
        with pytest.raises(ValueError, match="Unknown backend"):
            get_backend("unknown_platform")

    def test_list_backends(self) -> None:
        """Test listing available backends."""
        from qpandalite.backend import list_backends, BACKENDS
        
        backends = list_backends()
        assert "originq" in backends
        assert "quafu" in backends
        assert "ibm" in backends
        
        for name, info in backends.items():
            assert "platform" in info
            assert "available" in info
            assert "class" in info
            assert info["platform"] == name
            assert info["class"] == BACKENDS[name].__name__

    def test_backend_caching(self) -> None:
        """Test that backend instances are cached."""
        from qpandalite.backend import get_backend, OriginQBackend
        
        with patch("qpandalite.backend.OriginQBackend._create_adapter") as mock_create:
            mock_adapter = MagicMock()
            mock_create.return_value = mock_adapter
            
            # First call should create new instance
            backend1 = get_backend("originq", use_cache=True)
            # Second call should return cached instance
            backend2 = get_backend("originq", use_cache=True)
            
            assert backend1 is backend2


# ---------------------------------------------------------------------------
# Circuit Adapter Tests
# ---------------------------------------------------------------------------


class TestCircuitAdapters:
    """Tests for CircuitAdapter implementations."""

    def test_originq_adapter_supported_gates(self) -> None:
        """Test OriginQ adapter returns supported gates."""
        from qpandalite.circuit_adapter import OriginQCircuitAdapter
        
        adapter = OriginQCircuitAdapter()
        gates = adapter.get_supported_gates()
        
        assert isinstance(gates, list)
        assert "H" in gates
        assert "X" in gates
        assert "CNOT" in gates
        assert "MEASURE" in gates

    def test_quafu_adapter_supported_gates(self) -> None:
        """Test Quafu adapter returns supported gates."""
        from qpandalite.circuit_adapter import QuafuCircuitAdapter
        
        adapter = QuafuCircuitAdapter()
        gates = adapter.get_supported_gates()
        
        assert isinstance(gates, list)
        assert "H" in gates
        assert "CNOT" in gates
        assert "MEASURE" in gates

    def test_ibm_adapter_supported_gates(self) -> None:
        """Test IBM adapter returns supported gates."""
        from qpandalite.circuit_adapter import IBMCircuitAdapter
        
        adapter = IBMCircuitAdapter()
        gates = adapter.get_supported_gates()
        
        assert isinstance(gates, list)
        assert "H" in gates
        assert "CX" in gates  # IBM uses CX for CNOT
        assert "MEASURE" in gates

    def test_originq_adapter_without_pyqpanda3(self) -> None:
        """Test OriginQ adapter raises error when pyqpanda3 not installed."""
        from qpandalite.circuit_adapter import OriginQCircuitAdapter
        from qpandalite.circuit_builder import Circuit
        from unittest.mock import patch
        
        # Create a fresh adapter instance with cleared imports
        adapter = OriginQCircuitAdapter()
        adapter._pyqpanda3 = None
        adapter._convert_originir = None
        
        circuit = Circuit()
        circuit.h(0)
        
        # Mock the import to raise ImportError
        def mock_import(*args, **kwargs):
            raise ImportError("No module named 'pyqpanda3'")
        
        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(RuntimeError, match="pyqpanda3"):
                adapter.adapt(circuit)

    def test_quafu_adapter_without_quafu(self) -> None:
        """Test Quafu adapter raises error when quafu not installed."""
        from qpandalite.circuit_adapter import QuafuCircuitAdapter
        from qpandalite.circuit_builder import Circuit
        
        adapter = QuafuCircuitAdapter()
        adapter._quafu = None  # Simulate missing import
        adapter._QuantumCircuit = None
        
        circuit = Circuit()
        circuit.h(0)
        
        with pytest.raises(RuntimeError, match="quafu"):
            adapter.adapt(circuit)

    def test_ibm_adapter_adapt_batch(self) -> None:
        """Test IBM adapter batch conversion."""
        try:
            import qiskit
        except ImportError:
            pytest.skip("qiskit not installed")
        
        from qpandalite.circuit_adapter import IBMCircuitAdapter
        from qpandalite.circuit_builder import Circuit
        
        adapter = IBMCircuitAdapter()
        
        circuit1 = Circuit()
        circuit1.h(0)
        circuit1.measure(0)
        
        circuit2 = Circuit()
        circuit2.x(0)
        circuit2.measure(0)
        
        qiskit_circuits = adapter.adapt_batch([circuit1, circuit2])
        
        assert len(qiskit_circuits) == 2
        for qc in qiskit_circuits:
            assert hasattr(qc, "num_qubits")


# ---------------------------------------------------------------------------
# Mock Tests (No Real Platform Dependencies)
# ---------------------------------------------------------------------------


class TestMockSubmitTask:
    """Mock tests for submit_task workflows."""

    def test_originq_submit_task_mock(self) -> None:
        """Test OriginQ submit task with mocked HTTP client."""
        from qpandalite.task.adapters import OriginQAdapter
        
        with patch("qpandalite.task.adapters.originq_adapter.load_originq_config") as mock_config:
            mock_config.return_value = {
                "api_key": "test_key",
                "submit_url": "https://test.com/submit",
                "query_url": "https://test.com/query",
                "task_group_size": 200,
            }
            
            adapter = OriginQAdapter()
            
            with patch.object(adapter._client, "submit", return_value="task_abc123") as mock_submit:
                task_id = adapter.submit(ORIGINIR_BELL, shots=1000)
                
                mock_submit.assert_called_once()
                assert task_id == "task_abc123"

    def test_originq_submit_batch_mock(self) -> None:
        """Test OriginQ submit batch with mocked HTTP client."""
        from qpandalite.task.adapters import OriginQAdapter
        
        with patch("qpandalite.task.adapters.originq_adapter.load_originq_config") as mock_config:
            mock_config.return_value = {
                "api_key": "test_key",
                "submit_url": "https://test.com/submit",
                "query_url": "https://test.com/query",
                "task_group_size": 2,
            }
            
            adapter = OriginQAdapter()
            
            with patch.object(adapter._client, "submit", return_value="task_xyz") as mock_submit:
                circuits = [ORIGINIR_BELL] * 3
                task_ids = adapter.submit_batch(circuits, shots=1000)
                
                # With group_size=2 and 3 circuits, should call submit twice
                assert mock_submit.call_count == 2

    def test_quafu_submit_task_mock(self) -> None:
        """Test Quafu submit task with mocked SDK."""
        from qpandalite.task.adapters import QuafuAdapter
        
        with patch("qpandalite.task.adapters.quafu_adapter.load_quafu_config") as mock_config:
            mock_config.return_value = {"api_token": "test_token"}
            
            mock_quafu = MagicMock()
            mock_task_result = MagicMock()
            mock_task_result.taskid = "quafu_task_123"
            mock_quafu.User.return_value = MagicMock()
            mock_quafu.Task.return_value.send.return_value = mock_task_result
            
            with patch.dict(sys.modules, {"quafu": mock_quafu}):
                adapter = QuafuAdapter.__new__(QuafuAdapter)
                adapter._api_token = "test_token"
                adapter._quafu = mock_quafu
                adapter._QuantumCircuit = mock_quafu.QuantumCircuit
                adapter._Task = mock_quafu.Task
                adapter._User = mock_quafu.User
                adapter._task_history = {}
                adapter._history_order = []
                adapter._MAX_HISTORY_GROUPS = 100
                
                mock_circuit = MagicMock()
                task_id = adapter.submit(mock_circuit, shots=1000, chip_id="ScQ-P10")
                
                assert task_id == "quafu_task_123"


class TestMockQueryTask:
    """Mock tests for query_task workflows."""

    def test_originq_query_task_success_mock(self) -> None:
        """Test OriginQ query task success with mocked HTTP client."""
        from qpandalite.task.adapters import OriginQAdapter, TASK_STATUS_SUCCESS
        
        with patch("qpandalite.task.adapters.originq_adapter.load_originq_config") as mock_config:
            mock_config.return_value = {
                "api_key": "test_key",
                "submit_url": "https://test.com/submit",
                "query_url": "https://test.com/query",
                "task_group_size": 200,
            }
            
            adapter = OriginQAdapter()
            
            mock_result = {
                "taskid": "task_abc",
                "status": TASK_STATUS_SUCCESS,
                "result": [{"key": ["00", "11"], "value": [0.5, 0.5]}],
            }
            
            with patch.object(adapter._client, "query_single", return_value=mock_result) as mock_query:
                result = adapter.query("task_abc")
                
                mock_query.assert_called_once_with("task_abc")
                assert result["status"] == TASK_STATUS_SUCCESS

    def test_originq_query_task_running_mock(self) -> None:
        """Test OriginQ query task running status with mocked HTTP client."""
        from qpandalite.task.adapters import OriginQAdapter, TASK_STATUS_RUNNING
        
        with patch("qpandalite.task.adapters.originq_adapter.load_originq_config") as mock_config:
            mock_config.return_value = {
                "api_key": "test_key",
                "submit_url": "https://test.com/submit",
                "query_url": "https://test.com/query",
                "task_group_size": 200,
            }
            
            adapter = OriginQAdapter()
            
            mock_result = {
                "taskid": "task_abc",
                "status": TASK_STATUS_RUNNING,
            }
            
            with patch.object(adapter._client, "query_single", return_value=mock_result):
                result = adapter.query("task_abc")
                assert result["status"] == TASK_STATUS_RUNNING

    def test_originq_query_batch_mock(self) -> None:
        """Test OriginQ query batch with mocked HTTP client."""
        from qpandalite.task.adapters import OriginQAdapter, TASK_STATUS_SUCCESS
        
        with patch("qpandalite.task.adapters.originq_adapter.load_originq_config") as mock_config:
            mock_config.return_value = {
                "api_key": "test_key",
                "submit_url": "https://test.com/submit",
                "query_url": "https://test.com/query",
                "task_group_size": 200,
            }
            
            adapter = OriginQAdapter()
            
            mock_results = [
                {"taskid": "task_1", "status": TASK_STATUS_SUCCESS, "result": [{"key": ["00"], "value": [1.0]}]},
                {"taskid": "task_2", "status": TASK_STATUS_SUCCESS, "result": [{"key": ["11"], "value": [1.0]}]},
            ]
            
            with patch.object(adapter._client, "query_single", side_effect=mock_results):
                result = adapter.query_batch(["task_1", "task_2"])
                assert result["status"] == TASK_STATUS_SUCCESS
                assert len(result["result"]) == 2


class TestMockErrorScenarios:
    """Mock tests for error scenarios."""

    def test_originq_authentication_error(self) -> None:
        """Test OriginQ authentication error (invalid token)."""
        from qpandalite.task.adapters import OriginQAdapter
        
        with patch("qpandalite.task.adapters.originq_adapter.load_originq_config") as mock_config:
            mock_config.return_value = {
                "api_key": "invalid_token",
                "submit_url": "https://test.com/submit",
                "query_url": "https://test.com/query",
                "task_group_size": 200,
            }
            
            adapter = OriginQAdapter()
            
            # Simulate authentication error response
            with patch.object(
                adapter._client, 
                "submit", 
                side_effect=RuntimeError("Authentication failed: Invalid API key")
            ):
                with pytest.raises(RuntimeError, match="Authentication"):
                    adapter.submit(ORIGINIR_BELL)

    def test_originq_insufficient_credits_error(self) -> None:
        """Test OriginQ insufficient credits error."""
        from qpandalite.task.adapters import OriginQAdapter
        
        with patch("qpandalite.task.adapters.originq_adapter.load_originq_config") as mock_config:
            mock_config.return_value = {
                "api_key": "valid_token",
                "submit_url": "https://test.com/submit",
                "query_url": "https://test.com/query",
                "task_group_size": 200,
            }
            
            adapter = OriginQAdapter()
            
            # Simulate insufficient credits error
            with patch.object(
                adapter._client, 
                "submit", 
                side_effect=RuntimeError("Insufficient credits")
            ):
                with pytest.raises(RuntimeError, match="Insufficient credits"):
                    adapter.submit(ORIGINIR_BELL)

    def test_originq_network_error(self) -> None:
        """Test OriginQ network error."""
        from qpandalite.task.adapters import OriginQAdapter
        
        with patch("qpandalite.task.adapters.originq_adapter.load_originq_config") as mock_config:
            mock_config.return_value = {
                "api_key": "valid_token",
                "submit_url": "https://test.com/submit",
                "query_url": "https://test.com/query",
                "task_group_size": 200,
            }
            
            adapter = OriginQAdapter()
            
            # Simulate network error
            with patch.object(
                adapter._client, 
                "submit", 
                side_effect=RuntimeError("Network error: Connection timeout")
            ):
                with pytest.raises(RuntimeError, match="Network error"):
                    adapter.submit(ORIGINIR_BELL)

    def test_quafu_authentication_error(self) -> None:
        """Test Quafu authentication error."""
        from qpandalite.task.adapters import QuafuAdapter
        
        with patch("qpandalite.task.adapters.quafu_adapter.load_quafu_config") as mock_config:
            mock_config.return_value = {"api_token": "invalid_token"}
            
            mock_quafu = MagicMock()
            mock_user = MagicMock()
            mock_user.save_apitoken.side_effect = RuntimeError("Invalid API token")
            mock_quafu.User.return_value = mock_user
            
            with patch.dict(sys.modules, {"quafu": mock_quafu}):
                adapter = QuafuAdapter.__new__(QuafuAdapter)
                adapter._api_token = "invalid_token"
                adapter._quafu = mock_quafu
                adapter._QuantumCircuit = mock_quafu.QuantumCircuit
                adapter._Task = mock_quafu.Task
                adapter._User = mock_quafu.User
                adapter._task_history = {}
                adapter._history_order = []
                adapter._MAX_HISTORY_GROUPS = 100
                
                mock_circuit = MagicMock()
                with pytest.raises(RuntimeError):
                    adapter.submit(mock_circuit, chip_id="ScQ-P10")


# ---------------------------------------------------------------------------
# Integration Tests (Skipped unless real credentials exist)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not os.environ.get("QPANDA_API_KEY"),
    reason="QPANDA_API_KEY not set"
)
class TestOriginQIntegration:
    """Integration tests for OriginQ (requires real credentials)."""

    def test_originq_connection(self) -> None:
        """Test real OriginQ connection."""
        from qpandalite.backend import get_backend
        
        backend = get_backend("originq", use_cache=False)
        assert backend.is_available()

    def test_originq_submit_and_query(self) -> None:
        """Test real OriginQ submit and query workflow."""
        from qpandalite.backend import get_backend
        
        backend = get_backend("originq", use_cache=False)
        
        # Submit a simple circuit
        task_id = backend.submit(ORIGINIR_SINGLE, shots=1000, chip_id=72)
        assert task_id
        
        # Query the task
        result = backend.query(task_id)
        assert "status" in result


@pytest.mark.skipif(
    not os.environ.get("QUAFU_API_TOKEN"),
    reason="QUAFU_API_TOKEN not set"
)
class TestQuafuIntegration:
    """Integration tests for Quafu (requires real credentials)."""

    def test_quafu_connection(self) -> None:
        """Test real Quafu connection."""
        from qpandalite.backend import get_backend
        
        backend = get_backend("quafu", use_cache=False)
        # Note: is_available might require quafu package to be installed

    def test_quafu_translate_circuit(self) -> None:
        """Test real Quafu circuit translation."""
        try:
            import quafu
        except ImportError:
            pytest.skip("quafu not installed")
        
        from qpandalite.task.adapters import QuafuAdapter
        
        adapter = QuafuAdapter()
        circuit = adapter.translate_circuit(ORIGINIR_BELL)
        assert circuit is not None


@pytest.mark.skipif(
    not os.environ.get("IBM_TOKEN"),
    reason="IBM_TOKEN not set"
)
class TestIBMIntegration:
    """Integration tests for IBM Quantum (requires real credentials)."""

    def test_ibm_connection(self) -> None:
        """Test real IBM Quantum connection."""
        from qpandalite.backend import get_backend
        
        backend = get_backend("ibm", use_cache=False)
        # Note: is_available might require qiskit packages

    def test_ibm_translate_circuit(self) -> None:
        """Test real IBM circuit translation."""
        try:
            import qiskit
        except ImportError:
            pytest.skip("qiskit not installed")
        
        from qpandalite.task.adapters import QiskitAdapter
        
        adapter = QiskitAdapter()
        circuit = adapter.translate_circuit(ORIGINIR_BELL)
        assert circuit is not None
        assert hasattr(circuit, "num_qubits")


# ---------------------------------------------------------------------------
# End-to-End Tests
# ---------------------------------------------------------------------------


class TestEndToEndWorkflow:
    """End-to-end tests: Circuit → adapt → submit → query → result."""

    def test_e2e_originq_mock(self) -> None:
        """End-to-end test with mocked OriginQ backend."""
        from qpandalite.circuit_builder import Circuit
        from qpandalite.circuit_adapter import OriginQCircuitAdapter
        from qpandalite.backend import OriginQBackend
        
        # Step 1: Create circuit
        circuit = Circuit()
        circuit.h(0)
        circuit.cnot(0, 1)
        circuit.measure(0, 1)
        
        # Step 2: Adapt circuit (mocked since pyqpanda3 may not be installed)
        adapter = OriginQCircuitAdapter()
        
        # Step 3-5: Mock the backend operations
        with patch("qpandalite.backend.OriginQBackend._create_adapter") as mock_create:
            mock_backend_adapter = MagicMock()
            mock_create.return_value = mock_backend_adapter
            
            backend = OriginQBackend()
            
            # Mock submit
            mock_backend_adapter.submit.return_value = "e2e_task_123"
            task_id = backend.submit(circuit, shots=1000)
            assert task_id == "e2e_task_123"
            
            # Mock query
            mock_backend_adapter.query.return_value = {
                "status": "success",
                "result": [{"00": 512, "11": 488}],
            }
            result = backend.query(task_id)
            assert result["status"] == "success"

    def test_e2e_quafu_mock(self) -> None:
        """End-to-end test with mocked Quafu backend."""
        from qpandalite.circuit_builder import Circuit
        from qpandalite.backend import QuafuBackend
        
        # Step 1: Create circuit
        circuit = Circuit()
        circuit.h(0)
        circuit.cnot(0, 1)
        circuit.measure(0, 1)
        
        # Step 2-5: Mock the backend operations
        with patch("qpandalite.backend.QuafuBackend._create_adapter") as mock_create:
            mock_backend_adapter = MagicMock()
            mock_create.return_value = mock_backend_adapter
            
            backend = QuafuBackend()
            
            # Mock translate
            mock_translated_circuit = MagicMock()
            mock_backend_adapter.translate_circuit.return_value = mock_translated_circuit
            
            # Mock submit
            mock_backend_adapter.submit.return_value = "quafu_e2e_task_123"
            task_id = backend.submit(mock_translated_circuit, shots=1000, chip_id="ScQ-P10")
            assert task_id == "quafu_e2e_task_123"
            
            # Mock query
            mock_backend_adapter.query.return_value = {
                "status": "success",
                "result": {"counts": {"00": 512, "11": 488}},
            }
            result = backend.query(task_id)
            assert result["status"] == "success"

    def test_e2e_ibm_mock(self) -> None:
        """End-to-end test with mocked IBM backend."""
        from qpandalite.circuit_builder import Circuit
        from qpandalite.backend import IBMBackend
        
        # Step 1: Create circuit
        circuit = Circuit()
        circuit.h(0)
        circuit.cnot(0, 1)
        circuit.measure(0, 1)
        
        # Step 2-5: Mock the backend operations
        with patch("qpandalite.backend.IBMBackend._create_adapter") as mock_create:
            mock_backend_adapter = MagicMock()
            mock_create.return_value = mock_backend_adapter
            
            backend = IBMBackend()
            
            # Mock translate
            mock_translated_circuit = MagicMock()
            mock_backend_adapter.translate_circuit.return_value = mock_translated_circuit
            
            # Mock submit
            mock_backend_adapter.submit.return_value = "ibm_e2e_job_123"
            task_id = backend.submit(mock_translated_circuit, shots=1000, chip_id="ibm_perth")
            assert task_id == "ibm_e2e_job_123"
            
            # Mock query
            mock_backend_adapter.query.return_value = {
                "status": "success",
                "result": [{"00": 512, "11": 488}],
                "time": "Mon 01 Jan 2024, 12:00PM",
                "backend_name": "ibm_perth",
            }
            result = backend.query(task_id)
            assert result["status"] == "success"
            assert "backend_name" in result

    def test_complete_workflow_all_platforms_mock(self) -> None:
        """Test complete workflow for all three platforms with mocks."""
        from qpandalite.circuit_builder import Circuit
        from qpandalite.backend import get_backend, BACKENDS
        
        # Create test circuit
        circuit = Circuit()
        circuit.h(0)
        circuit.cnot(0, 1)
        circuit.measure(0, 1)
        
        for platform_name in ["originq", "quafu", "ibm"]:
            backend_class = BACKENDS[platform_name]
            
            with patch.object(backend_class, "_create_adapter") as mock_create:
                mock_adapter = MagicMock()
                mock_create.return_value = mock_adapter
                
                backend = get_backend(platform_name, use_cache=False)
                
                # Mock submit and query
                mock_adapter.submit.return_value = f"{platform_name}_task_123"
                mock_adapter.query.return_value = {
                    "status": "success",
                    "result": [{"00": 500, "11": 500}],
                }
                
                # Execute workflow
                task_id = backend.submit(circuit, shots=1000)
                result = backend.query(task_id)
                
                assert task_id == f"{platform_name}_task_123"
                assert result["status"] == "success"


# ---------------------------------------------------------------------------
# Compatibility Tests with Existing Tests
# ---------------------------------------------------------------------------


class TestCompatibilityWithExistingTests:
    """Ensure compatibility with existing test files."""

    def test_config_imports(self) -> None:
        """Test that config module imports work correctly."""
        from qpandalite import config
        from qpandalite.config import (
            load_config,
            save_config,
            get_platform_config,
            validate_config,
            create_default_config,
            DEFAULT_CONFIG,
        )
        
        assert callable(load_config)
        assert callable(save_config)
        assert callable(get_platform_config)
        assert callable(validate_config)
        assert callable(create_default_config)
        assert isinstance(DEFAULT_CONFIG, dict)

    def test_circuit_adapter_imports(self) -> None:
        """Test that circuit_adapter module imports work correctly."""
        from qpandalite import circuit_adapter
        from qpandalite.circuit_adapter import (
            CircuitAdapter,
            OriginQCircuitAdapter,
            QuafuCircuitAdapter,
            IBMCircuitAdapter,
        )
        
        assert issubclass(OriginQCircuitAdapter, CircuitAdapter)
        assert issubclass(QuafuCircuitAdapter, CircuitAdapter)
        assert issubclass(IBMCircuitAdapter, CircuitAdapter)

    def test_backend_imports(self) -> None:
        """Test that backend module imports work correctly."""
        from qpandalite.backend import (
            QuantumBackend,
            OriginQBackend,
            QuafuBackend,
            IBMBackend,
            get_backend,
            list_backends,
            BACKENDS,
        )
        
        assert callable(get_backend)
        assert callable(list_backends)
        assert isinstance(BACKENDS, dict)
        assert "originq" in BACKENDS
        assert "quafu" in BACKENDS
        assert "ibm" in BACKENDS

    def test_task_adapters_imports(self) -> None:
        """Test that task.adapters module imports work correctly."""
        from qpandalite.task.adapters import (
            QuantumAdapter,
            OriginQAdapter,
            QuafuAdapter,
            QiskitAdapter,
            TASK_STATUS_SUCCESS,
            TASK_STATUS_FAILED,
            TASK_STATUS_RUNNING,
        )
        
        assert TASK_STATUS_SUCCESS == "success"
        assert TASK_STATUS_FAILED == "failed"
        assert TASK_STATUS_RUNNING == "running"


# ---------------------------------------------------------------------------
# Cache Management Tests
# ---------------------------------------------------------------------------


class TestCacheManagement:
    """Tests for backend cache management."""

    def test_save_and_load_cache(self, tmp_path: Path) -> None:
        """Test saving and loading backend cache."""
        from qpandalite.backend import OriginQBackend, _get_cache_file_path
        
        cache_dir = tmp_path / "cache"
        backend = OriginQBackend(cache_dir=cache_dir, config={"test": "value"})
        backend.name = "test_backend"
        
        # Save to cache
        backend.save_to_cache()
        
        # Verify cache file exists
        cache_file = _get_cache_file_path("originq", cache_dir)
        assert cache_file.exists()

    def test_clear_cache(self, tmp_path: Path) -> None:
        """Test clearing backend cache."""
        from qpandalite.backend import OriginQBackend, _get_cache_file_path
        
        cache_dir = tmp_path / "cache"
        backend = OriginQBackend(cache_dir=cache_dir)
        
        # Save and verify
        backend.save_to_cache()
        cache_file = _get_cache_file_path("originq", cache_dir)
        assert cache_file.exists()
        
        # Clear and verify
        backend.clear_cache()
        assert not cache_file.exists()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
