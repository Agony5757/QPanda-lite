"""Tests for qpandalite.task_manager module.

This module tests:
- TaskInfo dataclass
- Cache management functions
- Error mapping
- Task submission/query/wait
- TaskManager class
"""

import json
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from qpandalite.task_manager import (
    TaskInfo,
    TaskStatus,
    TaskManager,
    _get_cache_file,
    _load_tasks_cache,
    _save_tasks_cache,
    _map_adapter_error,
    _get_adapter,
    save_task,
    get_task,
    list_tasks,
    clear_completed_tasks,
    clear_cache,
)
from qpandalite.exceptions import (
    AuthenticationError,
    BackendNotFoundError,
    InsufficientCreditsError,
    NetworkError,
    QuotaExceededError,
    TaskFailedError,
    TaskNotFoundError,
    TaskTimeoutError,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Create a temporary cache directory."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def sample_task_info() -> TaskInfo:
    """Create a sample TaskInfo for testing."""
    return TaskInfo(
        task_id="test-task-123",
        backend="quafu",
        status=TaskStatus.RUNNING,
        shots=1000,
        metadata={"test": True},
    )


# =============================================================================
# Test TaskInfo
# =============================================================================

class TestTaskInfo:
    """Tests for TaskInfo dataclass."""

    def test_task_info_creation(self):
        """Test TaskInfo can be created with required fields."""
        task = TaskInfo(
            task_id="test-123",
            backend="quafu",
        )
        assert task.task_id == "test-123"
        assert task.backend == "quafu"
        assert task.status == TaskStatus.PENDING
        assert task.shots == 1000
        assert task.result is None

    def test_task_info_to_dict(self, sample_task_info: TaskInfo):
        """Test TaskInfo.to_dict()."""
        data = sample_task_info.to_dict()
        assert data["task_id"] == "test-task-123"
        assert data["backend"] == "quafu"
        assert data["status"] == TaskStatus.RUNNING
        assert isinstance(data, dict)

    def test_task_info_from_dict(self):
        """Test TaskInfo.from_dict()."""
        data = {
            "task_id": "test-456",
            "backend": "originq",
            "status": "success",
            "result": {"counts": {"00": 512}},
            "shots": 2000,
            "submit_time": "2024-01-01T00:00:00",
            "update_time": "2024-01-01T00:01:00",
            "metadata": {},
        }
        task = TaskInfo.from_dict(data)
        assert task.task_id == "test-456"
        assert task.backend == "originq"
        assert task.status == "success"
        assert task.result == {"counts": {"00": 512}}

    def test_task_info_roundtrip(self, sample_task_info: TaskInfo):
        """Test TaskInfo serialization roundtrip."""
        data = sample_task_info.to_dict()
        restored = TaskInfo.from_dict(data)
        assert restored.task_id == sample_task_info.task_id
        assert restored.backend == sample_task_info.backend
        assert restored.status == sample_task_info.status


# =============================================================================
# Test Cache Management
# =============================================================================

class TestCacheManagement:
    """Tests for cache management functions."""

    def test_get_cache_file_default(self):
        """Test _get_cache_file with default directory."""
        with patch("qpandalite.task_manager.DEFAULT_CACHE_DIR", Path("/tmp/test_cache")):
            cache_file = _get_cache_file()
            assert cache_file.name == "tasks.json"

    def test_get_cache_file_custom(self, temp_cache_dir: Path):
        """Test _get_cache_file with custom directory."""
        cache_file = _get_cache_file(temp_cache_dir)
        assert cache_file == temp_cache_dir / "tasks.json"

    def test_load_tasks_cache_empty(self, temp_cache_dir: Path):
        """Test loading from non-existent cache."""
        tasks = _load_tasks_cache(temp_cache_dir)
        assert tasks == {}

    def test_load_tasks_cache_with_data(self, temp_cache_dir: Path):
        """Test loading from cache with data."""
        cache_file = _get_cache_file(temp_cache_dir)
        test_data = {
            "task-1": {"task_id": "task-1", "backend": "quafu", "status": "success"}
        }
        cache_file.write_text(json.dumps(test_data))

        tasks = _load_tasks_cache(temp_cache_dir)
        assert "task-1" in tasks
        assert tasks["task-1"]["backend"] == "quafu"

    def test_load_tasks_cache_corrupted(self, temp_cache_dir: Path):
        """Test loading from corrupted cache file."""
        cache_file = _get_cache_file(temp_cache_dir)
        cache_file.write_text("not valid json {")

        with pytest.warns(UserWarning):
            tasks = _load_tasks_cache(temp_cache_dir)
        assert tasks == {}

    def test_save_tasks_cache(self, temp_cache_dir: Path):
        """Test saving to cache."""
        tasks = {
            "task-1": {"task_id": "task-1", "backend": "quafu", "status": "running"}
        }
        _save_tasks_cache(tasks, temp_cache_dir)

        cache_file = _get_cache_file(temp_cache_dir)
        assert cache_file.exists()

        loaded = json.loads(cache_file.read_text())
        assert loaded == tasks

    def test_save_task(self, sample_task_info: TaskInfo, temp_cache_dir: Path):
        """Test save_task function."""
        save_task(sample_task_info, temp_cache_dir)

        loaded = _load_tasks_cache(temp_cache_dir)
        assert "test-task-123" in loaded

    def test_get_task_found(self, sample_task_info: TaskInfo, temp_cache_dir: Path):
        """Test get_task when task exists."""
        save_task(sample_task_info, temp_cache_dir)

        task = get_task("test-task-123", temp_cache_dir)
        assert task is not None
        assert task.task_id == "test-task-123"

    def test_get_task_not_found(self, temp_cache_dir: Path):
        """Test get_task when task doesn't exist."""
        task = get_task("nonexistent", temp_cache_dir)
        assert task is None

    def test_list_tasks_no_filter(self, temp_cache_dir: Path):
        """Test list_tasks without filters."""
        # Add multiple tasks
        for i in range(3):
            task = TaskInfo(
                task_id=f"task-{i}",
                backend="quafu" if i % 2 == 0 else "originq",
                status=TaskStatus.RUNNING if i < 2 else TaskStatus.SUCCESS,
            )
            save_task(task, temp_cache_dir)

        tasks = list_tasks(cache_dir=temp_cache_dir)
        assert len(tasks) == 3

    def test_list_tasks_filter_by_status(self, temp_cache_dir: Path):
        """Test list_tasks filtered by status."""
        for i, status in enumerate([TaskStatus.RUNNING, TaskStatus.SUCCESS, TaskStatus.FAILED]):
            task = TaskInfo(task_id=f"task-{i}", backend="quafu", status=status)
            save_task(task, temp_cache_dir)

        running_tasks = list_tasks(status=TaskStatus.RUNNING, cache_dir=temp_cache_dir)
        assert len(running_tasks) == 1
        assert running_tasks[0].status == TaskStatus.RUNNING

    def test_list_tasks_filter_by_backend(self, temp_cache_dir: Path):
        """Test list_tasks filtered by backend."""
        for i, backend in enumerate(["quafu", "originq", "quafu"]):
            task = TaskInfo(task_id=f"task-{i}", backend=backend)
            save_task(task, temp_cache_dir)

        quafu_tasks = list_tasks(backend="quafu", cache_dir=temp_cache_dir)
        assert len(quafu_tasks) == 2

    def test_clear_completed_tasks(self, temp_cache_dir: Path):
        """Test clear_completed_tasks."""
        # Add tasks with different statuses
        for i, status in enumerate([TaskStatus.RUNNING, TaskStatus.SUCCESS, TaskStatus.FAILED]):
            task = TaskInfo(task_id=f"task-{i}", backend="quafu", status=status)
            save_task(task, temp_cache_dir)

        removed = clear_completed_tasks(temp_cache_dir)
        assert removed == 2

        remaining = list_tasks(cache_dir=temp_cache_dir)
        assert len(remaining) == 1
        assert remaining[0].status == TaskStatus.RUNNING

    def test_clear_cache(self, temp_cache_dir: Path):
        """Test clear_cache removes all tasks."""
        task = TaskInfo(task_id="task-1", backend="quafu")
        save_task(task, temp_cache_dir)

        clear_cache(temp_cache_dir)

        cache_file = _get_cache_file(temp_cache_dir)
        assert not cache_file.exists()


# =============================================================================
# Test Error Mapping
# =============================================================================

class TestErrorMapping:
    """Tests for _map_adapter_error function."""

    def test_map_authentication_error(self):
        """Test mapping authentication errors."""
        error = Exception("Unauthorized: invalid token")
        mapped = _map_adapter_error(error, "quafu")
        assert isinstance(mapped, AuthenticationError)

    def test_map_insufficient_credits_error(self):
        """Test mapping credit errors."""
        error = Exception("Insufficient credits in account")
        mapped = _map_adapter_error(error, "originq")
        assert isinstance(mapped, InsufficientCreditsError)

    def test_map_quota_exceeded_error(self):
        """Test mapping quota errors."""
        error = Exception("Rate limit exceeded")
        mapped = _map_adapter_error(error, "ibm")
        assert isinstance(mapped, QuotaExceededError)

    def test_map_network_error(self):
        """Test mapping network errors."""
        error = Exception("Connection timeout")
        mapped = _map_adapter_error(error, "quafu")
        assert isinstance(mapped, NetworkError)

    def test_map_unknown_error(self):
        """Test that unknown errors are returned as-is."""
        error = Exception("Some unknown error")
        mapped = _map_adapter_error(error, "quafu")
        assert mapped is error


# =============================================================================
# Test Adapter Mapping
# =============================================================================

class TestAdapterMapping:
    """Tests for _get_adapter function."""

    def test_get_adapter_valid_backend(self):
        """Test getting adapter for valid backend."""
        adapter = _get_adapter("quafu")
        assert adapter is not None

    def test_get_adapter_invalid_backend(self):
        """Test getting adapter for invalid backend."""
        with pytest.raises(BackendNotFoundError):
            _get_adapter("invalid_backend")


# =============================================================================
# Test TaskManager Class
# =============================================================================

class TestTaskManager:
    """Tests for TaskManager class."""

    def test_task_manager_init(self, temp_cache_dir: Path):
        """Test TaskManager initialization."""
        manager = TaskManager(cache_dir=temp_cache_dir)
        assert manager._cache_dir == temp_cache_dir

    def test_task_manager_list_tasks(self, temp_cache_dir: Path, sample_task_info: TaskInfo):
        """Test TaskManager.list_tasks."""
        save_task(sample_task_info, temp_cache_dir)

        manager = TaskManager(cache_dir=temp_cache_dir)
        tasks = manager.list_tasks()
        assert len(tasks) == 1

    def test_task_manager_clear_completed(self, temp_cache_dir: Path):
        """Test TaskManager.clear_completed."""
        task = TaskInfo(task_id="task-1", backend="quafu", status=TaskStatus.SUCCESS)
        save_task(task, temp_cache_dir)

        manager = TaskManager(cache_dir=temp_cache_dir)
        removed = manager.clear_completed()
        assert removed == 1

    def test_task_manager_clear_cache(self, temp_cache_dir: Path, sample_task_info: TaskInfo):
        """Test TaskManager.clear_cache."""
        save_task(sample_task_info, temp_cache_dir)

        manager = TaskManager(cache_dir=temp_cache_dir)
        manager.clear_cache()

        tasks = manager.list_tasks()
        assert len(tasks) == 0


# =============================================================================
# Test submit_task with mocks
# =============================================================================

class TestSubmitTask:
    """Tests for submit_task function with mocked backends.

    Note: Due to variable name collision (backend is both a module and parameter name),
    we test the underlying functions that submit_task calls instead.
    """

    def test_submit_task_raises_backend_not_found(self):
        """Test that _get_adapter raises BackendNotFoundError for invalid backend."""
        with pytest.raises(BackendNotFoundError):
            _get_adapter("invalid_backend_name")


# =============================================================================
# Test query_task with mocks
# =============================================================================

class TestQueryTask:
    """Tests for query_task function."""

    def test_query_task_not_found_no_backend(self, temp_cache_dir: Path):
        """Test query_task when task not found and no backend provided."""
        from qpandalite.task_manager import query_task

        with patch("qpandalite.task_manager.get_task") as mock_get_task:
            mock_get_task.return_value = None
            with pytest.raises(TaskNotFoundError):
                query_task("nonexistent-task")


# =============================================================================
# Test wait_for_result with mocks
# =============================================================================

class TestWaitForResult:
    """Tests for wait_for_result function."""

    @patch("qpandalite.task_manager.query_task")
    def test_wait_for_result_success(self, mock_query, temp_cache_dir: Path):
        """Test wait_for_result with successful completion."""
        from qpandalite.task_manager import wait_for_result

        # Mock successful result
        success_task = TaskInfo(
            task_id="task-1",
            backend="quafu",
            status=TaskStatus.SUCCESS,
            result={"counts": {"00": 512, "11": 488}},
        )
        mock_query.return_value = success_task

        with patch("qpandalite.task_manager.DEFAULT_CACHE_DIR", temp_cache_dir):
            result = wait_for_result("task-1", backend="quafu", timeout=1)

        assert result == {"counts": {"00": 512, "11": 488}}

    @patch("qpandalite.task_manager.query_task")
    def test_wait_for_result_failure_raise(self, mock_query, temp_cache_dir: Path):
        """Test wait_for_result with failure and raise_on_failure=True."""
        from qpandalite.task_manager import wait_for_result

        failed_task = TaskInfo(
            task_id="task-1",
            backend="quafu",
            status=TaskStatus.FAILED,
        )
        mock_query.return_value = failed_task

        with patch("qpandalite.task_manager.DEFAULT_CACHE_DIR", temp_cache_dir):
            with pytest.raises(TaskFailedError):
                wait_for_result("task-1", backend="quafu", timeout=1)

    @patch("qpandalite.task_manager.query_task")
    def test_wait_for_result_failure_no_raise(self, mock_query, temp_cache_dir: Path):
        """Test wait_for_result with failure and raise_on_failure=False."""
        from qpandalite.task_manager import wait_for_result

        failed_task = TaskInfo(
            task_id="task-1",
            backend="quafu",
            status=TaskStatus.FAILED,
        )
        mock_query.return_value = failed_task

        with patch("qpandalite.task_manager.DEFAULT_CACHE_DIR", temp_cache_dir):
            result = wait_for_result("task-1", backend="quafu", timeout=1, raise_on_failure=False)

        assert result is None

    @patch("qpandalite.task_manager.query_task")
    def test_wait_for_result_timeout(self, mock_query, temp_cache_dir: Path):
        """Test wait_for_result with timeout."""
        from qpandalite.task_manager import wait_for_result

        # Mock running task that never completes
        running_task = TaskInfo(
            task_id="task-1",
            backend="quafu",
            status=TaskStatus.RUNNING,
        )
        mock_query.return_value = running_task

        with patch("qpandalite.task_manager.DEFAULT_CACHE_DIR", temp_cache_dir):
            with pytest.raises(TaskTimeoutError):
                wait_for_result("task-1", backend="quafu", timeout=0.1, poll_interval=0.05)


# =============================================================================
# Test submit_batch with mocks
# =============================================================================

class TestSubmitBatch:
    """Tests for submit_batch function.

    Note: Full integration tests require backend setup. Here we test
    the component functions that submit_batch uses.
    """

    def test_submit_batch_uses_get_adapter(self):
        """Test that submit_batch would use correct adapter."""
        # Verify adapter exists for valid backends
        adapter = _get_adapter("quafu")
        assert adapter is not None

        adapter = _get_adapter("originq")
        assert adapter is not None

        adapter = _get_adapter("ibm")
        assert adapter is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
