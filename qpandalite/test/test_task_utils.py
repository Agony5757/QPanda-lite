"""Tests for qpandalite.task.task_utils.

Covers: load_circuit, load_circuit_group, make_savepath,
load_all_online_info, get_last_taskid, write_taskinfo, timestr, timestr_ymd_hms.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CIRCUIT_A = "QINIT 2\nH q[0]\nCNOT q[0], q[1]\nMEASURE q[0], c[0]"
CIRCUIT_B = "QINIT 3\nH q[0]\nH q[1]\nH q[2]\nCNOT q[0], q[1]\nCNOT q[1], q[2]"


# ---------------------------------------------------------------------------
# load_circuit
# ---------------------------------------------------------------------------

class RunTestLoadCircuit:
    """load_circuit loads all .txt files under basepath as {filename: content}."""

    def run_test_load_circuit_normal(self, tmp_path):
        (tmp_path / "circuit1.txt").write_text(CIRCUIT_A)
        (tmp_path / "circuit2.txt").write_text(CIRCUIT_B)

        from qpandalite.task.task_utils import load_circuit

        result = load_circuit(tmp_path)
        assert result["circuit1.txt"] == CIRCUIT_A
        assert result["circuit2.txt"] == CIRCUIT_B

    def run_test_load_circuit_ignores_non_txt(self, tmp_path):
        (tmp_path / "circuit1.txt").write_text(CIRCUIT_A)
        (tmp_path / "readme.md").write_text("# Notes")
        (tmp_path / "data.json").write_text("{}")

        from qpandalite.task.task_utils import load_circuit

        result = load_circuit(tmp_path)
        assert "circuit1.txt" in result
        assert "readme.md" not in result
        assert "data.json" not in result

    def run_test_load_circuit_empty_dir(self, tmp_path):
        from qpandalite.task.task_utils import load_circuit

        result = load_circuit(tmp_path)
        assert result == {}

    def run_test_load_circuit_default_path(self, tmp_path, monkeypatch):
        """When basepath is None, defaults to <cwd>/output_circuits."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output_circuits").mkdir()
        (tmp_path / "output_circuits" / "a.txt").write_text("hello")

        from qpandalite.task.task_utils import load_circuit

        result = load_circuit()
        assert "a.txt" in result
        assert result["a.txt"] == "hello"


# ---------------------------------------------------------------------------
# load_circuit_group
# ---------------------------------------------------------------------------

class RunTestLoadCircuitGroup:
    """load_circuit_group splits on '//////////', keeps non-empty QINIT fragments."""

    def run_test_load_circuit_group_normal(self, tmp_path):
        content = (
            "QINIT 2\nH q[0]\n//////////\n"
            "QINIT 3\nH q[0]\nH q[1]\n//////////\n"
            "QINIT 2\nCNOT q[0], q[1]"
        )
        (tmp_path / "originir.txt").write_text(content)

        from qpandalite.task.task_utils import load_circuit_group

        result = load_circuit_group(tmp_path / "originir.txt")
        assert 0 in result
        assert result[0].startswith("QINIT 2")
        assert 1 in result
        assert result[1].startswith("QINIT 3")
        assert 2 in result
        assert result[2].startswith("QINIT 2")

    def run_test_load_circuit_group_skips_empty(self, tmp_path):
        content = (
            "//////////\n"
            "//////////\n"
            "QINIT 1\nH q[0]"
        )
        (tmp_path / "originir.txt").write_text(content)

        from qpandalite.task.task_utils import load_circuit_group

        result = load_circuit_group(tmp_path / "originir.txt")
        # Only the non-empty QINIT fragment should remain; keys preserve original indices
        assert len(result) == 1
        assert 2 in result  # original index of the 3rd fragment
        assert result[2].startswith("QINIT 1")

    def run_test_load_circuit_group_skips_non_qinit(self, tmp_path):
        content = (
            "NOT_QINIT content\n//////////\n"
            "QINIT 1\nH q[0]\n//////////\n"
            "ALSO_NOT_QINIT"
        )
        (tmp_path / "originir.txt").write_text(content)

        from qpandalite.task.task_utils import load_circuit_group

        result = load_circuit_group(tmp_path / "originir.txt")
        assert len(result) == 1
        assert 1 in result  # original index of the QINIT fragment
        assert result[1].startswith("QINIT 1")

    def run_test_load_circuit_group_no_valid_circuits(self, tmp_path):
        content = "//////////\n//////////"
        (tmp_path / "originir.txt").write_text(content)

        from qpandalite.task.task_utils import load_circuit_group

        result = load_circuit_group(tmp_path / "originir.txt")
        assert result == {}

    def run_test_load_circuit_group_default_path(self, tmp_path, monkeypatch):
        """When path is None, defaults to <cwd>/output_circuits/originir.txt."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output_circuits").mkdir()
        (tmp_path / "output_circuits" / "originir.txt").write_text(
            "QINIT 1\nH q[0]\n//////////\nQINIT 2\nH q[1]"
        )

        from qpandalite.task.task_utils import load_circuit_group

        result = load_circuit_group()
        assert len(result) == 2


# ---------------------------------------------------------------------------
# make_savepath
# ---------------------------------------------------------------------------

class RunTestMakeSavepath:
    """make_savepath creates the directory and online_info.txt if they don't exist."""

    def run_test_make_savepath_creates_dir_and_file(self, tmp_path):
        from qpandalite.task.task_utils import make_savepath

        make_savepath(tmp_path)
        assert (tmp_path / "online_info.txt").exists()
        assert (tmp_path / "online_info.txt").read_text() == ""

    def run_test_make_savepath_idempotent(self, tmp_path):
        from qpandalite.task.task_utils import make_savepath

        make_savepath(tmp_path)
        make_savepath(tmp_path)  # call twice — should not raise
        assert (tmp_path / "online_info.txt").exists()

    def run_test_make_savepath_nested_dir(self, tmp_path):
        nested = tmp_path / "a" / "b" / "c"
        from qpandalite.task.task_utils import make_savepath

        make_savepath(nested)
        assert nested.exists()
        assert (nested / "online_info.txt").exists()

    def run_test_make_savepath_default(self, tmp_path, monkeypatch):
        """When savepath is None, defaults to <cwd>/online_info."""
        monkeypatch.chdir(tmp_path)
        from qpandalite.task.task_utils import make_savepath

        make_savepath()
        assert (tmp_path / "online_info" / "online_info.txt").exists()


# ---------------------------------------------------------------------------
# load_all_online_info
# ---------------------------------------------------------------------------

class RunTestLoadAllOnlineInfo:
    """load_all_online_info reads online_info.txt, each line parsed as JSON."""

    def run_test_load_all_online_info_normal(self, tmp_path):
        lines = [
            json.dumps({"taskid": "t1", "status": "success"}),
            json.dumps({"taskid": "t2", "status": "pending"}),
            json.dumps({"taskid": "t3", "status": "failed"}),
        ]
        (tmp_path / "online_info.txt").write_text("\n".join(lines))

        from qpandalite.task.task_utils import load_all_online_info

        result = load_all_online_info(tmp_path)
        assert len(result) == 3
        assert result[0]["taskid"] == "t1"
        assert result[1]["taskid"] == "t2"
        assert result[2]["taskid"] == "t3"

    def run_test_load_all_online_info_empty_file(self, tmp_path):
        (tmp_path / "online_info.txt").write_text("")

        from qpandalite.task.task_utils import load_all_online_info

        result = load_all_online_info(tmp_path)
        assert result == []

    def run_test_load_all_online_info_single_entry(self, tmp_path):
        (tmp_path / "online_info.txt").write_text(json.dumps({"taskid": "only"}))

        from qpandalite.task.task_utils import load_all_online_info

        result = load_all_online_info(tmp_path)
        assert len(result) == 1
        assert result[0]["taskid"] == "only"

    def run_test_load_all_online_info_default(self, tmp_path, monkeypatch):
        """When savepath is None, defaults to <cwd>/online_info."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "online_info").mkdir()
        (tmp_path / "online_info" / "online_info.txt").write_text(
            json.dumps({"taskid": "default_path"})
        )

        from qpandalite.task.task_utils import load_all_online_info

        result = load_all_online_info()
        assert result[0]["taskid"] == "default_path"


# ---------------------------------------------------------------------------
# get_last_taskid
# ---------------------------------------------------------------------------

class RunTestGetLastTaskid:
    """get_last_taskid returns the taskid field from the last line of online_info.txt."""

    def run_test_get_last_taskid_normal(self, tmp_path):
        lines = [
            json.dumps({"taskid": "task_001", "shots": 1000}),
            json.dumps({"taskid": "task_002", "shots": 2000}),
            json.dumps({"taskid": "task_003", "shots": 3000}),
        ]
        (tmp_path / "online_info.txt").write_text("\n".join(lines))

        from qpandalite.task.task_utils import get_last_taskid

        assert get_last_taskid(tmp_path) == "task_003"

    def run_test_get_last_taskid_single_line(self, tmp_path):
        (tmp_path / "online_info.txt").write_text(
            json.dumps({"taskid": "only_task"})
        )

        from qpandalite.task.task_utils import get_last_taskid

        assert get_last_taskid(tmp_path) == "only_task"

    def run_test_get_last_taskid_default(self, tmp_path, monkeypatch):
        """When savepath is None, defaults to <cwd>/online_info."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "online_info").mkdir()
        (tmp_path / "online_info" / "online_info.txt").write_text(
            json.dumps({"taskid": "last_one"})
        )

        from qpandalite.task.task_utils import get_last_taskid

        assert get_last_taskid() == "last_one"


# ---------------------------------------------------------------------------
# write_taskinfo
# ---------------------------------------------------------------------------

class RunTestWriteTaskinfo:
    """write_taskinfo writes <taskid>.txt JSON file, skips if savepath is None or file exists."""

    def run_test_write_taskinfo_normal(self, tmp_path):
        from qpandalite.task.task_utils import write_taskinfo

        write_taskinfo("abc123", {"shots": 1000, "chip_id": 72}, tmp_path)
        content = (tmp_path / "abc123.txt").read_text()
        assert json.loads(content) == {"shots": 1000, "chip_id": 72}

    def run_test_write_taskinfo_no_overwrite(self, tmp_path):
        from qpandalite.task.task_utils import write_taskinfo

        write_taskinfo("abc123", {"shots": 1000}, tmp_path)
        write_taskinfo("abc123", {"shots": 9999}, tmp_path)  # should not overwrite
        content = (tmp_path / "abc123.txt").read_text()
        assert json.loads(content) == {"shots": 1000}

    def run_test_write_taskinfo_savepath_none_noop(self):
        from qpandalite.task.task_utils import write_taskinfo

        # Should not raise
        write_taskinfo("any", {"data": 1}, None)

    def run_test_write_taskinfo_multiple_files(self, tmp_path):
        from qpandalite.task.task_utils import write_taskinfo

        write_taskinfo("t1", {"n": 1}, tmp_path)
        write_taskinfo("t2", {"n": 2}, tmp_path)
        write_taskinfo("t3", {"n": 3}, tmp_path)

        assert (tmp_path / "t1.txt").exists()
        assert (tmp_path / "t2.txt").exists()
        assert (tmp_path / "t3.txt").exists()
        assert json.loads((tmp_path / "t2.txt").read_text()) == {"n": 2}


# ---------------------------------------------------------------------------
# timestr / timestr_ymd_hms
# ---------------------------------------------------------------------------

class RunTestTimestr:
    """timestr and timestr_ymd_hms both return YYYYMMDD_HHMMSS format."""

    TIMESTR_PATTERN = re.compile(r"^\d{8}_\d{6}$")

    def run_test_timestr_format(self):
        from qpandalite.task.task_utils import timestr

        result = timestr()
        assert isinstance(result, str)
        assert self.TIMESTR_PATTERN.match(result)

    def run_test_timestr_ymd_hms_format(self):
        from qpandalite.task.task_utils import timestr_ymd_hms

        result = timestr_ymd_hms()
        assert isinstance(result, str)
        assert self.TIMESTR_PATTERN.match(result)

    def run_test_timestr_equals_timestr_ymd_hms(self):
        """timestr() is an alias for timestr_ymd_hms()."""
        from qpandalite.task.task_utils import timestr, timestr_ymd_hms

        # Both call datetime.now().strftime, so they return the same value when called
        # in quick succession (within the same second).
        assert timestr() == timestr_ymd_hms()

    def run_test_timestr_length(self):
        from qpandalite.task.task_utils import timestr

        result = timestr()
        assert len(result) == 15  # YYYYMMDD_HHMMSS = 8 + 1 + 6 = 15
