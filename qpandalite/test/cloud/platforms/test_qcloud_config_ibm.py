"""Tests for qpandalite.qcloud_config.ibm_online_config."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


class RunTestIBMonlineConfig:
    """Tests for create_ibm_online_config."""

    def run_test_success_with_valid_token(self, tmp_path):
        """Valid default_token writes correct ibm_online_config.json."""
        from qpandalite.qcloud_config.ibm_online_config import (
            create_ibm_online_config,
        )

        create_ibm_online_config(default_token="ibm_secret_123", savepath=tmp_path)

        config_file = tmp_path / "ibm_online_config.json"
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data == {"default_token": "ibm_secret_123"}

    def run_test_success_default_savepath_cwd(self, monkeypatch, tmp_path):
        """Without savepath, file is written to cwd."""
        monkeypatch.chdir(tmp_path)
        from qpandalite.qcloud_config.ibm_online_config import (
            create_ibm_online_config,
        )

        create_ibm_online_config(default_token="ibm_token_abc")

        config_file = tmp_path / "ibm_online_config.json"
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["default_token"] == "ibm_token_abc"

    def run_test_missing_default_token_raises(self, tmp_path):
        """Missing default_token raises RuntimeError."""
        from qpandalite.qcloud_config.ibm_online_config import (
            create_ibm_online_config,
        )

        with pytest.raises(RuntimeError, match="You should input your token"):
            create_ibm_online_config(default_token=None, savepath=tmp_path)

    def run_test_empty_string_token_raises(self, tmp_path):
        """Empty string token raises RuntimeError (falsy check)."""
        from qpandalite.qcloud_config.ibm_online_config import (
            create_ibm_online_config,
        )

        with pytest.raises(RuntimeError, match="You should input your token"):
            create_ibm_online_config(default_token="", savepath=tmp_path)

    def run_test_custom_savepath(self, tmp_path):
        """Custom savepath writes to the specified directory."""
        from qpandalite.qcloud_config.ibm_online_config import (
            create_ibm_online_config,
        )

        subdir = tmp_path / "subdir"
        subdir.mkdir()
        create_ibm_online_config(default_token="ibm_x", savepath=subdir)

        config_file = subdir / "ibm_online_config.json"
        assert config_file.exists()
        assert json.loads(config_file.read_text()) == {"default_token": "ibm_x"}
