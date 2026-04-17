"""Tests for qpandalite.qcloud_config.originq_online_config."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


class RunTestOriginQOnlineConfig:
    """Tests for create_originq_config, create_originq_online_config, create_originq_dummy_config."""

    # ----- create_originq_config -----

    def run_test_create_originq_config_success(self, tmp_path):
        """Valid params write correct originq_online_config.json."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_config,
        )

        create_originq_config(
            login_apitoken="login_key",
            login_url="https://login.example.com",
            submit_url="https://submit.example.com",
            query_url="https://query.example.com",
            available_qubits=[0, 1, 2],
            available_topology=[[0, 1], [1, 2]],
            task_group_size=150,
            savepath=tmp_path,
        )

        config_file = tmp_path / "originq_online_config.json"
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["login_apitoken"] == "login_key"
        assert data["login_url"] == "https://login.example.com"
        assert data["submit_url"] == "https://submit.example.com"
        assert data["query_url"] == "https://query.example.com"
        assert data["available_qubits"] == [0, 1, 2]
        assert data["available_topology"] == [[0, 1], [1, 2]]
        assert data["task_group_size"] == 150

    def run_test_create_originq_config_missing_login_apitoken_raises(self, tmp_path):
        """Missing login_apitoken raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_config,
        )

        with pytest.raises(RuntimeError, match="You should input your token"):
            create_originq_config(
                login_apitoken=None,
                login_url="https://login.com",
                submit_url="https://s.com",
                query_url="https://q.com",
                available_qubits=[0],
                available_topology=[[0, 1]],
                savepath=tmp_path,
            )

    def run_test_create_originq_config_missing_login_url_raises(self, tmp_path):
        """Missing login_url raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_config,
        )

        with pytest.raises(RuntimeError, match="login url"):
            create_originq_config(
                login_apitoken="key",
                login_url=None,
                submit_url="https://s.com",
                query_url="https://q.com",
                available_qubits=[0],
                available_topology=[[0, 1]],
                savepath=tmp_path,
            )

    def run_test_create_originq_config_missing_submit_url_raises(self, tmp_path):
        """Missing submit_url raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_config,
        )

        with pytest.raises(RuntimeError, match="submitting url"):
            create_originq_config(
                login_apitoken="key",
                login_url="https://l.com",
                submit_url=None,
                query_url="https://q.com",
                available_qubits=[0],
                available_topology=[[0, 1]],
                savepath=tmp_path,
            )

    def run_test_create_originq_config_missing_query_url_raises(self, tmp_path):
        """Missing query_url raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_config,
        )

        with pytest.raises(RuntimeError, match="querying url"):
            create_originq_config(
                login_apitoken="key",
                login_url="https://l.com",
                submit_url="https://s.com",
                query_url=None,
                available_qubits=[0],
                available_topology=[[0, 1]],
                savepath=tmp_path,
            )

    def run_test_create_originq_config_qubits_not_list_raises(self, tmp_path):
        """available_qubits as non-list raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_config,
        )

        with pytest.raises(RuntimeError, match="Available qubits must be a list"):
            create_originq_config(
                login_apitoken="key",
                login_url="https://l.com",
                submit_url="https://s.com",
                query_url="https://q.com",
                available_qubits="0,1",
                available_topology=[[0, 1]],
                savepath=tmp_path,
            )

    def run_test_create_originq_config_topology_not_list_raises(self, tmp_path):
        """available_topology as non-list raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_config,
        )

        with pytest.raises(RuntimeError, match="Available topology must be a list"):
            create_originq_config(
                login_apitoken="key",
                login_url="https://l.com",
                submit_url="https://s.com",
                query_url="https://q.com",
                available_qubits=[0, 1],
                available_topology={0: 1},
                savepath=tmp_path,
            )

    def run_test_create_originq_config_task_group_size_not_int_raises(self, tmp_path):
        """task_group_size as non-int raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_config,
        )

        with pytest.raises(RuntimeError, match="Task group size"):
            create_originq_config(
                login_apitoken="key",
                login_url="https://l.com",
                submit_url="https://s.com",
                query_url="https://q.com",
                available_qubits=[0],
                available_topology=[[0, 1]],
                task_group_size=100.0,
                savepath=tmp_path,
            )

    def run_test_create_originq_config_custom_task_group_size(self, tmp_path):
        """Custom task_group_size is written correctly."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_config,
        )

        create_originq_config(
            login_apitoken="key",
            login_url="https://l.com",
            submit_url="https://s.com",
            query_url="https://q.com",
            available_qubits=[0],
            available_topology=[[0, 1]],
            task_group_size=75,
            savepath=tmp_path,
        )

        data = json.loads((tmp_path / "originq_online_config.json").read_text())
        assert data["task_group_size"] == 75

    # ----- create_originq_online_config -----

    def run_test_create_originq_online_config_success(self, tmp_path):
        """Valid params write correct originq_online_config.json with None qubits/topology."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_online_config,
        )

        create_originq_online_config(
            login_apitoken="online_key",
            login_url="https://login.example.com",
            submit_url="https://submit.example.com",
            query_url="https://query.example.com",
            task_group_size=300,
            savepath=tmp_path,
        )

        config_file = tmp_path / "originq_online_config.json"
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["login_apitoken"] == "online_key"
        assert data["submit_url"] == "https://submit.example.com"
        assert data["query_url"] == "https://query.example.com"
        assert data["available_qubits"] is None
        assert data["available_topology"] is None
        assert data["task_group_size"] == 300

    def run_test_create_originq_online_config_missing_login_apitoken_raises(self, tmp_path):
        """Missing login_apitoken raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_online_config,
        )

        with pytest.raises(RuntimeError, match="You should input your token"):
            create_originq_online_config(
                login_apitoken=None,
                login_url="https://l.com",
                submit_url="https://s.com",
                query_url="https://q.com",
                savepath=tmp_path,
            )

    def run_test_create_originq_online_config_task_group_size_not_int_raises(self, tmp_path):
        """task_group_size as non-int raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_online_config,
        )

        with pytest.raises(RuntimeError, match="Task group size"):
            create_originq_online_config(
                login_apitoken="key",
                login_url="https://l.com",
                submit_url="https://s.com",
                query_url="https://q.com",
                task_group_size="200",
                savepath=tmp_path,
            )

    def run_test_create_originq_online_config_custom_task_group_size(self, tmp_path):
        """Custom task_group_size is written correctly."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_online_config,
        )

        create_originq_online_config(
            login_apitoken="key",
            login_url="https://l.com",
            submit_url="https://s.com",
            query_url="https://q.com",
            task_group_size=250,
            savepath=tmp_path,
        )

        data = json.loads((tmp_path / "originq_online_config.json").read_text())
        assert data["task_group_size"] == 250

    # ----- create_originq_dummy_config -----

    def run_test_create_originq_dummy_config_success(self, tmp_path):
        """Valid params write correct originq_online_config.json with DUMMY placeholders."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_dummy_config,
        )

        create_originq_dummy_config(
            available_qubits=[0, 1, 2, 3, 4],
            available_topology=[[0, 1], [1, 2], [2, 3], [3, 4]],
            task_group_size=10,
            savepath=tmp_path,
        )

        config_file = tmp_path / "originq_online_config.json"
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["login_apitoken"] == "DUMMY"
        assert data["login_url"] == "DUMMY"
        assert data["submit_url"] == "DUMMY"
        assert data["query_url"] == "DUMMY"
        assert data["available_qubits"] == [0, 1, 2, 3, 4]
        assert data["available_topology"] == [[0, 1], [1, 2], [2, 3], [3, 4]]
        assert data["task_group_size"] == 10

    def run_test_create_originq_dummy_config_qubits_not_list_raises(self, tmp_path):
        """available_qubits as non-list raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_dummy_config,
        )

        with pytest.raises(RuntimeError, match="Available qubits must be a list"):
            create_originq_dummy_config(
                available_qubits="all",
                available_topology=[[0, 1]],
                savepath=tmp_path,
            )

    def run_test_create_originq_dummy_config_topology_not_list_raises(self, tmp_path):
        """available_topology as non-list raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_dummy_config,
        )

        with pytest.raises(RuntimeError, match="Available topology must be a list"):
            create_originq_dummy_config(
                available_qubits=[0, 1],
                available_topology="[[0,1]]",
                savepath=tmp_path,
            )

    def run_test_create_originq_dummy_config_task_group_size_not_int_raises(self, tmp_path):
        """task_group_size as non-int raises RuntimeError."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_dummy_config,
        )

        with pytest.raises(RuntimeError, match="Task group size"):
            create_originq_dummy_config(
                available_qubits=[0],
                available_topology=[[0, 1]],
                task_group_size=5.5,
                savepath=tmp_path,
            )

    def run_test_create_originq_dummy_config_custom_task_group_size(self, tmp_path):
        """Custom task_group_size is written correctly."""
        from qpandalite.qcloud_config.originq_online_config import (
            create_originq_dummy_config,
        )

        create_originq_dummy_config(
            available_qubits=[0],
            available_topology=[[0, 1]],
            task_group_size=20,
            savepath=tmp_path,
        )

        data = json.loads((tmp_path / "originq_online_config.json").read_text())
        assert data["task_group_size"] == 20
