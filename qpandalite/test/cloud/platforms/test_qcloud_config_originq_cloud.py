"""Tests for qpandalite.qcloud_config.originq_cloud_config."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


class RunTestOriginQCloudConfig:
    """Tests for create_originq_cloud_config."""

    def run_test_success_with_all_params(self, tmp_path):
        """Valid params write correct originq_cloud_config.json."""
        from qpandalite.qcloud_config.originq_cloud_config import (
            create_originq_cloud_config,
        )

        create_originq_cloud_config(
            apitoken="api_key_123",
            submit_url="https://submit.example.com",
            query_url="https://query.example.com",
            available_qubits=[0, 1, 2, 3],
            available_topology=[[0, 1], [1, 2], [2, 3]],
            task_group_size=100,
            savepath=tmp_path,
        )

        config_file = tmp_path / "originq_cloud_config.json"
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["apitoken"] == "api_key_123"
        assert data["submit_url"] == "https://submit.example.com"
        assert data["query_url"] == "https://query.example.com"
        assert data["available_qubits"] == [0, 1, 2, 3]
        assert data["available_topology"] == [[0, 1], [1, 2], [2, 3]]
        assert data["task_group_size"] == 100

    def run_test_success_default_task_group_size(self, tmp_path):
        """Default task_group_size=200 is used when not specified."""
        from qpandalite.qcloud_config.originq_cloud_config import (
            create_originq_cloud_config,
        )

        create_originq_cloud_config(
            apitoken="key",
            submit_url="https://s.com",
            query_url="https://q.com",
            available_qubits=[0],
            available_topology=[[0, 1]],
            savepath=tmp_path,
        )

        data = json.loads((tmp_path / "originq_cloud_config.json").read_text())
        assert data["task_group_size"] == 200

    def run_test_missing_apitoken_raises(self, tmp_path):
        """Missing apitoken raises RuntimeError."""
        from qpandalite.qcloud_config.originq_cloud_config import (
            create_originq_cloud_config,
        )

        with pytest.raises(RuntimeError, match="You should input your api key"):
            create_originq_cloud_config(
                apitoken=None,
                submit_url="https://s.com",
                query_url="https://q.com",
                available_qubits=[0],
                available_topology=[[0, 1]],
                savepath=tmp_path,
            )

    def run_test_missing_submit_url_raises(self, tmp_path):
        """Missing submit_url raises RuntimeError."""
        from qpandalite.qcloud_config.originq_cloud_config import (
            create_originq_cloud_config,
        )

        with pytest.raises(RuntimeError, match="submitting url"):
            create_originq_cloud_config(
                apitoken="key",
                submit_url=None,
                query_url="https://q.com",
                available_qubits=[0],
                available_topology=[[0, 1]],
                savepath=tmp_path,
            )

    def run_test_missing_query_url_raises(self, tmp_path):
        """Missing query_url raises RuntimeError."""
        from qpandalite.qcloud_config.originq_cloud_config import (
            create_originq_cloud_config,
        )

        with pytest.raises(RuntimeError, match="querying url"):
            create_originq_cloud_config(
                apitoken="key",
                submit_url="https://s.com",
                query_url=None,
                available_qubits=[0],
                available_topology=[[0, 1]],
                savepath=tmp_path,
            )

    def run_test_available_qubits_not_list_raises(self, tmp_path):
        """available_qubits as non-list raises RuntimeError."""
        from qpandalite.qcloud_config.originq_cloud_config import (
            create_originq_cloud_config,
        )

        with pytest.raises(RuntimeError, match="Available qubits must be a list"):
            create_originq_cloud_config(
                apitoken="key",
                submit_url="https://s.com",
                query_url="https://q.com",
                available_qubits={0, 1},
                available_topology=[[0, 1]],
                savepath=tmp_path,
            )

    def run_test_available_qubits_string_raises(self, tmp_path):
        """available_qubits as string raises RuntimeError."""
        from qpandalite.qcloud_config.originq_cloud_config import (
            create_originq_cloud_config,
        )

        with pytest.raises(RuntimeError, match="Available qubits must be a list"):
            create_originq_cloud_config(
                apitoken="key",
                submit_url="https://s.com",
                query_url="https://q.com",
                available_qubits="0,1",
                available_topology=[[0, 1]],
                savepath=tmp_path,
            )

    def run_test_available_topology_not_list_raises(self, tmp_path):
        """available_topology as non-list raises RuntimeError."""
        from qpandalite.qcloud_config.originq_cloud_config import (
            create_originq_cloud_config,
        )

        with pytest.raises(RuntimeError, match="Available topology must be a list"):
            create_originq_cloud_config(
                apitoken="key",
                submit_url="https://s.com",
                query_url="https://q.com",
                available_qubits=[0, 1],
                available_topology="[[0,1]]",
                savepath=tmp_path,
            )

    def run_test_task_group_size_not_int_raises(self, tmp_path):
        """task_group_size as non-int raises RuntimeError."""
        from qpandalite.qcloud_config.originq_cloud_config import (
            create_originq_cloud_config,
        )

        with pytest.raises(RuntimeError, match="Task group size"):
            create_originq_cloud_config(
                apitoken="key",
                submit_url="https://s.com",
                query_url="https://q.com",
                available_qubits=[0],
                available_topology=[[0, 1]],
                task_group_size="100",
                savepath=tmp_path,
            )

    def run_test_task_group_size_float_raises(self, tmp_path):
        """task_group_size as float raises RuntimeError."""
        from qpandalite.qcloud_config.originq_cloud_config import (
            create_originq_cloud_config,
        )

        with pytest.raises(RuntimeError, match="Task group size"):
            create_originq_cloud_config(
                apitoken="key",
                submit_url="https://s.com",
                query_url="https://q.com",
                available_qubits=[0],
                available_topology=[[0, 1]],
                task_group_size=10.5,
                savepath=tmp_path,
            )

    def run_test_custom_task_group_size(self, tmp_path):
        """Custom task_group_size is written correctly."""
        from qpandalite.qcloud_config.originq_cloud_config import (
            create_originq_cloud_config,
        )

        create_originq_cloud_config(
            apitoken="key",
            submit_url="https://s.com",
            query_url="https://q.com",
            available_qubits=[0],
            available_topology=[[0, 1]],
            task_group_size=50,
            savepath=tmp_path,
        )

        data = json.loads((tmp_path / "originq_cloud_config.json").read_text())
        assert data["task_group_size"] == 50
