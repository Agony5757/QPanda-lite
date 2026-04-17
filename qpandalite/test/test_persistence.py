"""Tests for the persistence module."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# Mock qpandalite_cpp before importing any qpandalite modules
if 'qpandalite_cpp' not in sys.modules:
    sys.modules['qpandalite_cpp'] = MagicMock()

import pytest

from qpandalite.task.persistence import TaskPersistence


class TestTaskPersistence:
    """Tests for TaskPersistence class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def persistence(self, temp_dir):
        """Create a TaskPersistence instance with temp directory."""
        return TaskPersistence(cache_dir=temp_dir)

    def test_init_creates_directory(self, temp_dir):
        """Test that initialization creates the cache directory."""
        cache_dir = temp_dir / "new_cache"
        TaskPersistence(cache_dir=cache_dir)

        assert cache_dir.exists()

    def test_save_and_load(self, persistence):
        """Test saving and loading a task record."""
        persistence.save(
            task_id="test-123",
            platform="originq",
            status="success",
            result={"counts": {"00": 512}},
            shots=1000,
        )

        record = persistence.load("test-123")

        assert record is not None
        assert record["task_id"] == "test-123"
        assert record["platform"] == "originq"
        assert record["status"] == "success"
        assert record["result"]["counts"]["00"] == 512

    def test_load_nonexistent_task(self, persistence):
        """Test loading a task that doesn't exist."""
        record = persistence.load("nonexistent")

        assert record is None

    def test_update_task(self, persistence):
        """Test updating an existing task."""
        persistence.save("task-1", "quafu", "running")

        success = persistence.update("task-1", status="success", result={"counts": {}})

        assert success
        record = persistence.load("task-1")
        assert record["status"] == "success"

    def test_update_nonexistent_task(self, persistence):
        """Test updating a task that doesn't exist."""
        success = persistence.update("nonexistent", status="success")

        assert not success

    def test_upsert_new_task(self, persistence):
        """Test upsert creates new task if not exists."""
        persistence.upsert("new-task", "ibm", "success", result={"counts": {}})

        record = persistence.load("new-task")
        assert record is not None
        assert record["platform"] == "ibm"

    def test_upsert_existing_task(self, persistence):
        """Test upsert updates existing task."""
        persistence.save("task-2", "originq", "running")
        persistence.upsert("task-2", "originq", "success")

        record = persistence.load("task-2")
        assert record["status"] == "success"

    def test_list_all(self, persistence):
        """Test listing all tasks."""
        persistence.save("task-1", "originq", "success")
        persistence.save("task-2", "quafu", "running")
        persistence.save("task-3", "ibm", "success")

        all_tasks = persistence.list_all()

        assert len(all_tasks) == 3

    def test_list_all_filter_by_platform(self, persistence):
        """Test filtering tasks by platform."""
        persistence.save("task-1", "originq", "success")
        persistence.save("task-2", "quafu", "success")

        tasks = persistence.list_all(platform="originq")

        assert len(tasks) == 1
        assert tasks[0]["platform"] == "originq"

    def test_list_all_filter_by_status(self, persistence):
        """Test filtering tasks by status."""
        persistence.save("task-1", "originq", "success")
        persistence.save("task-2", "originq", "running")

        tasks = persistence.list_all(status="success")

        assert len(tasks) == 1
        assert tasks[0]["status"] == "success"

    def test_list_all_with_limit(self, persistence):
        """Test limiting number of results."""
        for i in range(5):
            persistence.save(f"task-{i}", "originq", "success")

        tasks = persistence.list_all(limit=3)

        assert len(tasks) == 3

    def test_list_by_platform(self, persistence):
        """Test list_by_platform convenience method."""
        persistence.save("task-1", "originq", "success")
        persistence.save("task-2", "quafu", "success")

        tasks = persistence.list_by_platform("originq")

        assert len(tasks) == 1

    def test_list_pending(self, persistence):
        """Test listing pending/running tasks."""
        persistence.save("task-1", "originq", "success")
        persistence.save("task-2", "originq", "running")
        persistence.save("task-3", "quafu", "pending")

        pending = persistence.list_pending()

        assert len(pending) == 2

    def test_clear_completed(self, persistence):
        """Test clearing completed tasks."""
        persistence.save("task-1", "originq", "success")
        persistence.save("task-2", "originq", "failed")
        persistence.save("task-3", "quafu", "running")

        removed = persistence.clear_completed()

        assert removed == 2
        remaining = persistence.list_all()
        assert len(remaining) == 1
        assert remaining[0]["status"] == "running"

    def test_delete(self, persistence):
        """Test deleting a specific task."""
        persistence.save("task-1", "originq", "success")

        success = persistence.delete("task-1")

        assert success
        assert persistence.load("task-1") is None

    def test_delete_nonexistent(self, persistence):
        """Test deleting a nonexistent task."""
        success = persistence.delete("nonexistent")

        assert not success

    def test_count(self, persistence):
        """Test counting tasks."""
        persistence.save("task-1", "originq", "success")
        persistence.save("task-2", "originq", "running")
        persistence.save("task-3", "quafu", "success")

        total = persistence.count()
        originq = persistence.count(platform="originq")
        success_count = persistence.count(status="success")

        assert total == 3
        assert originq == 2
        assert success_count == 2

    def test_jsonl_format(self, persistence):
        """Test that storage uses valid JSONL format."""
        persistence.save("task-1", "originq", "success")
        persistence.save("task-2", "quafu", "success")

        # Read raw file
        with open(persistence.tasks_file) as f:
            lines = f.readlines()

        assert len(lines) == 2

        # Each line should be valid JSON
        for line in lines:
            record = json.loads(line)
            assert "task_id" in record
            assert "platform" in record

    def test_timestamps_set(self, persistence):
        """Test that timestamps are automatically set."""
        persistence.save("task-1", "originq", "success")

        record = persistence.load("task-1")

        assert "submit_time" in record
        assert "update_time" in record
