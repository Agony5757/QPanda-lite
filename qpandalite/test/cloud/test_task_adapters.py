"""Tests for the task adapter layer.

These tests verify that:
1. Each adapter correctly translates OriginIR to provider-native circuits.
2. Config is loaded from environment variables (with deprecated file fallback).
3. Task modules delegate to adapters (no raw REST in task modules).

Tests use mocked HTTP responses so they run without real credentials or
network access.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
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


# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------

class RunTestConfigEnvVars:
    """Config loading from environment variables (preferred)."""

    def run_test_originq_config_from_env(self, monkeypatch, tmp_path):
        """OriginQ config is read from QPANDA_* env vars."""
        monkeypatch.setenv("QPANDA_API_KEY", "test_key_123")
        monkeypatch.setenv("QPANDA_SUBMIT_URL", "https://example.com/submit")
        monkeypatch.setenv("QPANDA_QUERY_URL", "https://example.com/query")
        monkeypatch.setenv("QPANDA_TASK_GROUP_SIZE", "100")

        # Ensure no config file exists
        monkeypatch.chdir(tmp_path)

        from qpandalite.task.config import load_originq_config

        config = load_originq_config()
        assert config["api_key"] == "test_key_123"
        assert config["submit_url"] == "https://example.com/submit"
        assert config["query_url"] == "https://example.com/query"
        assert config["task_group_size"] == 100

    def run_test_quafu_config_from_env(self, monkeypatch, tmp_path):
        """Quafu config is read from QUAHU_API_TOKEN env var."""
        monkeypatch.setenv("QUAFU_API_TOKEN", "quafu_secret_token")
        monkeypatch.chdir(tmp_path)

        from qpandalite.task.config import load_quafu_config

        config = load_quafu_config()
        assert config["api_token"] == "quafu_secret_token"

    def run_test_ibm_config_from_env(self, monkeypatch, tmp_path):
        """IBM config is read from IBM_TOKEN env var."""
        monkeypatch.setenv("IBM_TOKEN", "ibm_secret_token")
        monkeypatch.chdir(tmp_path)

        from qpandalite.task.config import load_ibm_config

        config = load_ibm_config()
        assert config["api_token"] == "ibm_secret_token"

    def run_test_dummy_config_from_env(self, monkeypatch, tmp_path):
        """OriginQ Dummy config is read from ORIGINQ_* env vars."""
        monkeypatch.setenv(
            "ORIGINQ_AVAILABLE_QUBITS", json.dumps([0, 1, 2, 3])
        )
        monkeypatch.setenv(
            "ORIGINQ_AVAILABLE_TOPOLOGY",
            json.dumps([[0, 1], [1, 2], [2, 3]]),
        )
        monkeypatch.setenv("ORIGINQ_TASK_GROUP_SIZE", "50")
        monkeypatch.chdir(tmp_path)

        from qpandalite.task.config import load_dummy_config

        config = load_dummy_config()
        assert config["available_qubits"] == [0, 1, 2, 3]
        assert config["available_topology"] == [[0, 1], [1, 2], [2, 3]]
        assert config["task_group_size"] == 50

    def run_test_originq_config_deprecated_file_fallback(self, monkeypatch, tmp_path):
        """File fallback is no longer supported - ImportError raised when env vars absent."""
        monkeypatch.delenv("QPANDA_API_KEY", raising=False)
        monkeypatch.delenv("QPANDA_SUBMIT_URL", raising=False)
        monkeypatch.delenv("QPANDA_QUERY_URL", raising=False)

        # Create a config file (should NOT be used anymore)
        config_file = tmp_path / "originq_cloud_config.json"
        config_file.write_text(
            json.dumps(
                {
                    "apitoken": "file_key",
                    "submit_url": "https://file.com/submit",
                    "query_url": "https://file.com/query",
                    "task_group_size": 50,
                }
            )
        )
        monkeypatch.chdir(tmp_path)

        # Clear module cache to force re-import
        if "qpandalite.task.config" in sys.modules:
            del sys.modules["qpandalite.task.config"]

        from qpandalite.task.config import load_originq_config

        # Should raise ImportError - file fallback is no longer supported
        with pytest.raises(ImportError, match="QPANDA_API_KEY"):
            load_originq_config()

    def run_test_originq_config_import_error_without_config(self, monkeypatch, tmp_path):
        """ImportError raised when neither env vars nor config file exist."""
        monkeypatch.delenv("QPANDA_API_KEY", raising=False)
        monkeypatch.delenv("QPANDA_SUBMIT_URL", raising=False)
        monkeypatch.delenv("QPANDA_QUERY_URL", raising=False)
        monkeypatch.chdir(tmp_path)

        # Force re-import by clearing module cache
        if "qpandalite.task.config" in sys.modules:
            del sys.modules["qpandalite.task.config"]

        from qpandalite.task.config import load_originq_config

        with pytest.raises(ImportError, match="QPANDA_API_KEY"):
            load_originq_config()


# ---------------------------------------------------------------------------
# OriginQ adapter tests
# ---------------------------------------------------------------------------

class RunTestOriginQAdapterCircuitTranslation:
    """OriginQAdapter.translate_circuit passes OriginIR through unchanged."""

    def run_test_translate_circuit_returns_string(self):
        with patch(
            "qpandalite.task.adapters.originq_adapter.load_originq_config",
            return_value={
                "api_key": "k",
                "submit_url": "https://x.com/s",
                "query_url": "https://x.com/q",
                "task_group_size": 200,
            },
        ):
            from qpandalite.task.adapters import OriginQAdapter

            adapter = OriginQAdapter()
            result = adapter.translate_circuit(ORIGINIR_BELL)
            assert result == ORIGINIR_BELL

    def run_test_submit_calls_http_client(self):
        with patch(
            "qpandalite.task.adapters.originq_adapter.load_originq_config",
            return_value={
                "api_key": "k",
                "submit_url": "https://x.com/s",
                "query_url": "https://x.com/q",
                "task_group_size": 200,
            },
        ):
            from qpandalite.task.adapters import OriginQAdapter

            adapter = OriginQAdapter()
            with patch.object(
                adapter._client, "submit", return_value="task_abc123"
            ) as mock_submit:
                task_id = adapter.submit(
                    ORIGINIR_BELL, shots=1000, chip_id=72
                )
                mock_submit.assert_called_once()
                args, kwargs = mock_submit.call_args
                assert kwargs["circuits"] == [ORIGINIR_BELL]
                assert task_id == "task_abc123"

    def run_test_submit_batch_splits_large_groups(self):
        with patch(
            "qpandalite.task.adapters.originq_adapter.load_originq_config",
            return_value={
                "api_key": "k",
                "submit_url": "https://x.com/s",
                "query_url": "https://x.com/q",
                "task_group_size": 2,
            },
        ):
            from qpandalite.task.adapters import OriginQAdapter

            adapter = OriginQAdapter()
            with patch.object(
                adapter._client, "submit", return_value="subtask_xyz"
            ) as mock_submit:
                circuits = [ORIGINIR_BELL] * 3
                taskids = adapter.submit_batch(circuits, shots=1000)
                # 3 circuits with group_size=2 should produce 2 subgroups
                assert mock_submit.call_count == 2
                assert len(taskids) == 2

    def run_test_query_single_success(self):
        with patch(
            "qpandalite.task.adapters.originq_adapter.load_originq_config",
            return_value={
                "api_key": "k",
                "submit_url": "https://x.com/s",
                "query_url": "https://x.com/q",
                "task_group_size": 200,
            },
        ):
            from qpandalite.task.adapters import OriginQAdapter

            adapter = OriginQAdapter()
            with patch.object(
                adapter._client,
                "query_single",
                return_value={
                    "taskid": "task_abc",
                    "status": "success",
                    "result": [{"key": ["00", "11"], "value": [0.5, 0.5]}],
                },
            ) as mock_query:
                result = adapter.query("task_abc")
                mock_query.assert_called_once_with("task_abc")
                assert result["status"] == "success"


# ---------------------------------------------------------------------------
# Quafu adapter tests
# ---------------------------------------------------------------------------

class RunTestQuafuAdapterCircuitTranslation:
    """QuafuAdapter correctly translates OriginIR to quafu.QuantumCircuit."""

    def run_test_translate_simple_gates(self):
        originir = """
QINIT 2
H q[0]
CNOT q[0], q[1]
MEASURE q[0], c[0]
""".strip()

        with patch(
            "qpandalite.task.adapters.quafu_adapter.load_quafu_config",
            return_value={"api_token": "tok"},
        ):
            # Mock quafu module
            mock_qc = MagicMock()
            mock_quafu = MagicMock()
            mock_quafu.QuantumCircuit.return_value = mock_qc

            with patch.dict(sys.modules, {"quafu": mock_quafu}):
                # Need to reimport to pick up the mock
                from qpandalite.task.adapters import QuafuAdapter

                # Replace _quafu, _QuantumCircuit etc on the instance
                adapter = QuafuAdapter.__new__(QuafuAdapter)
                adapter._api_token = "tok"
                adapter._quafu = mock_quafu
                adapter._QuantumCircuit = mock_quafu.QuantumCircuit
                adapter._Task = MagicMock()
                adapter._User = MagicMock()

                result = adapter.translate_circuit(originir)
                # Verify QuantumCircuit was created with 2 qubits
                mock_quafu.QuantumCircuit.assert_called_with(2)

    def run_test_translate_unknown_gate_raises(self):
        originir = """
QINIT 1
UNKNOWN_GATE q[0]
""".strip()

        with patch(
            "qpandalite.task.adapters.quafu_adapter.load_quafu_config",
            return_value={"api_token": "tok"},
        ):
            mock_quafu = MagicMock()
            mock_quafu.QuantumCircuit.return_value = MagicMock()

            with patch.dict(sys.modules, {"quafu": mock_quafu}):
                from qpandalite.task.adapters import QuafuAdapter

                adapter = QuafuAdapter.__new__(QuafuAdapter)
                adapter._api_token = "tok"
                adapter._quafu = mock_quafu
                adapter._QuantumCircuit = mock_quafu.QuantumCircuit
                adapter._Task = MagicMock()
                adapter._User = MagicMock()

                with pytest.raises(RuntimeError, match="UNKNOWN_GATE"):
                    adapter.translate_circuit(originir)


# ---------------------------------------------------------------------------
# IBM adapter tests
# ---------------------------------------------------------------------------

class RunTestIBMAdapterCircuitTranslation:
    """IBMAdapter translates OriginIR to qiskit.QuantumCircuit via QASM."""

    def run_test_translate_calls_circuit_qasm(self):
        originir = """
QINIT 2
H q[0]
CNOT q[0], q[1]
MEASURE q[0], c[0]
MEASURE q[1], c[1]
""".strip()

        mock_qiskit = MagicMock()
        mock_qc = MagicMock()
        mock_qiskit.QuantumCircuit.from_qasm_str.return_value = mock_qc

        with patch.dict(sys.modules, {"qiskit": mock_qiskit, "qiskit_ibm_provider": MagicMock()}):
            with patch(
                "qpandalite.task.adapters.qiskit_adapter.load_ibm_config",
                return_value={"api_token": "ibm_tok"},
            ):
                from qpandalite.task.adapters import QiskitAdapter

                adapter = QiskitAdapter.__new__(QiskitAdapter)
                adapter._api_token = "ibm_tok"
                adapter._provider = MagicMock()
                adapter._backends = []
                adapter._provider.backends = MagicMock(return_value=[])

                with patch(
                    "qpandalite.circuit_builder.qcircuit.Circuit"
                ) as mock_circuit_cls:
                    mock_circuit = MagicMock()
                    mock_circuit.qasm = "OPENQASM 2.0; ..."
                    mock_circuit_cls.return_value = mock_circuit

                    result = adapter.translate_circuit(originir)

                mock_qiskit.QuantumCircuit.from_qasm_str.assert_called_once_with(
                    "OPENQASM 2.0; ..."
                )


# ---------------------------------------------------------------------------
# Adapter availability tests
# ---------------------------------------------------------------------------

class RunTestAdapterAvailability:
    """Each adapter reports availability based on installed packages / config."""

    def run_test_originq_adapter_available_with_config(self):
        with patch(
            "qpandalite.task.adapters.originq_adapter.load_originq_config",
            return_value={
                "api_key": "k",
                "submit_url": "https://x.com/s",
                "query_url": "https://x.com/q",
                "task_group_size": 200,
            },
        ):
            from qpandalite.task.adapters import OriginQAdapter

            adapter = OriginQAdapter()
            assert adapter.is_available() is True

    def run_test_quafu_adapter_available_with_quafu_installed(self):
        with patch(
            "qpandalite.task.adapters.quafu_adapter.load_quafu_config",
            return_value={"api_token": "tok"},
        ):
            with patch.dict(sys.modules, {"quafu": MagicMock()}):
                from qpandalite.task.adapters import QuafuAdapter

                adapter = QuafuAdapter.__new__(QuafuAdapter)
                adapter._api_token = "tok"
                adapter._quafu = MagicMock()  # Not None → available
                adapter._QuantumCircuit = MagicMock()
                adapter._Task = MagicMock()
                adapter._User = MagicMock()

                assert adapter.is_available() is True
