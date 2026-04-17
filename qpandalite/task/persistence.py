"""Task persistence using JSONL format.

This module provides persistent storage for quantum task metadata and results.
Tasks are stored in JSONL (JSON Lines) format where each line is a complete
JSON object representing one task record.

Storage location: ~/.qpandalite/tasks/tasks.jsonl

The JSONL format provides:
- Simple append-only writes for new tasks
- Line-by-line reading for efficient lookups
- Human-readable format for debugging
- No external database dependencies

Usage:
    from qpandalite.task.persistence import TaskPersistence

    # Create persistence manager
    persistence = TaskPersistence()

    # Save a task
    persistence.save(
        task_id="task-123",
        platform="originq",
        status="success",
        result={"counts": {"00": 512, "11": 488}},
        shots=1000
    )

    # Load a task
    record = persistence.load("task-123")

    # List all tasks for a platform
    tasks = persistence.list_all(platform="originq")
"""

from __future__ import annotations

__all__ = ["TaskPersistence", "DEFAULT_CACHE_DIR"]

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

# Default storage directory
DEFAULT_CACHE_DIR = Path.home() / ".qpandalite" / "tasks"


class TaskPersistence:
    """JSONL-based task storage manager.

    Manages persistent storage of quantum task records in JSONL format.
    Each record is a JSON object on a single line, enabling efficient
    append operations and line-by-line reading.

    Attributes:
        cache_dir: Directory containing the tasks.jsonl file.
        tasks_file: Path to the tasks.jsonl file.

    Example:
        >>> persistence = TaskPersistence()
        >>> persistence.save("task-1", "originq", "running")
        >>> record = persistence.load("task-1")
        >>> print(record['status'])
        'running'
    """

    def __init__(self, cache_dir: Optional[Path] = None) -> None:
        """Initialize the persistence manager.

        Args:
            cache_dir: Optional custom cache directory. Defaults to
                ~/.qpandalite/tasks/
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_file = self.cache_dir / "tasks.jsonl"

    def save(
        self,
        task_id: str,
        platform: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        **metadata: Any,
    ) -> None:
        """Save a new task record.

        Creates a new record with the provided information and appends it
        to the tasks.jsonl file. The timestamp is automatically set.

        Args:
            task_id: Unique task identifier.
            platform: Platform name ('originq', 'quafu', 'ibm', 'dummy').
            status: Task status ('pending', 'running', 'success', 'failed').
            result: Optional result dict (counts, probabilities, etc.).
            **metadata: Additional metadata fields to store.

        Example:
            >>> persistence.save(
            ...     "task-123",
            ...     "originq",
            ...     "success",
            ...     result={"counts": {"00": 512}},
            ...     shots=1000
            ... )
        """
        timestamp = datetime.now().isoformat()
        record: Dict[str, Any] = {
            "task_id": task_id,
            "platform": platform,
            "status": status,
            "submit_time": timestamp,
            "update_time": timestamp,
            "result": result,
            **metadata,
        }

        with open(self.tasks_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def load(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load a task record by ID.

        Searches through all records to find the one with matching task_id.
        Returns the most recent record if there are duplicates.

        Args:
            task_id: The task identifier to look up.

        Returns:
            The task record dict, or None if not found.

        Example:
            >>> record = persistence.load("task-123")
            >>> if record:
            ...     print(record['status'])
        """
        if not self.tasks_file.exists():
            return None

        # Search from end to get most recent entry
        records = list(self._iter_records())
        for record in reversed(records):
            if record.get("task_id") == task_id:
                return record
        return None

    def update(self, task_id: str, **updates: Any) -> bool:
        """Update an existing task record.

        Reads all records, updates the matching one, and rewrites the file.
        The update_time is automatically set.

        Args:
            task_id: The task identifier to update.
            **updates: Fields to update in the record.

        Returns:
            True if the task was found and updated, False otherwise.

        Example:
            >>> success = persistence.update("task-123", status="success",
            ...                               result={"counts": {"00": 512}})
        """
        if not self.tasks_file.exists():
            return False

        records = list(self._iter_records())
        found = False

        for record in records:
            if record.get("task_id") == task_id:
                record.update(updates)
                record["update_time"] = datetime.now().isoformat()
                found = True
                break

        if found:
            self._write_all(records)
        return found

    def upsert(
        self,
        task_id: str,
        platform: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        **metadata: Any,
    ) -> None:
        """Update existing record or insert new one.

        Convenience method that checks if a record exists and either
        updates it or creates a new one.

        Args:
            task_id: Unique task identifier.
            platform: Platform name.
            status: Task status.
            result: Optional result dict.
            **metadata: Additional metadata.
        """
        existing = self.load(task_id)
        if existing:
            self.update(task_id, status=status, result=result, **metadata)
        else:
            self.save(task_id, platform, status, result=result, **metadata)

    def list_all(
        self,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List all tasks with optional filtering.

        Args:
            platform: Filter by platform name.
            status: Filter by task status.
            limit: Maximum number of records to return.

        Returns:
            List of task records, most recent first.

        Example:
            >>> # Get all successful OriginQ tasks
            >>> tasks = persistence.list_all(platform="originq", status="success")
        """
        results = []
        for record in self._iter_records():
            if platform and record.get("platform") != platform:
                continue
            if status and record.get("status") != status:
                continue
            results.append(record)

        # Return most recent first
        results.reverse()

        if limit:
            results = results[:limit]
        return results

    def list_by_platform(self, platform: str) -> List[Dict[str, Any]]:
        """List all tasks for a specific platform.

        Args:
            platform: Platform name to filter by.

        Returns:
            List of task records for the platform.
        """
        return self.list_all(platform=platform)

    def list_pending(self) -> List[Dict[str, Any]]:
        """List all pending or running tasks.

        Returns:
            List of tasks with status 'pending' or 'running'.
        """
        results = []
        for record in self._iter_records():
            if record.get("status") in ("pending", "running"):
                results.append(record)
        return results

    def clear_completed(self) -> int:
        """Remove all completed tasks from storage.

        Removes tasks with status 'success', 'failed', or 'cancelled'.

        Returns:
            Number of tasks removed.

        Example:
            >>> removed = persistence.clear_completed()
            >>> print(f"Removed {removed} completed tasks")
        """
        if not self.tasks_file.exists():
            return 0

        kept = []
        removed = 0
        terminal_states = ("success", "failed", "cancelled")

        for record in self._iter_records():
            if record.get("status") in terminal_states:
                removed += 1
            else:
                kept.append(record)

        self._write_all(kept)
        return removed

    def delete(self, task_id: str) -> bool:
        """Delete a specific task record.

        Args:
            task_id: The task identifier to delete.

        Returns:
            True if the task was found and deleted, False otherwise.
        """
        if not self.tasks_file.exists():
            return False

        records = list(self._iter_records())
        original_len = len(records)
        records = [r for r in records if r.get("task_id") != task_id]

        if len(records) < original_len:
            self._write_all(records)
            return True
        return False

    def count(self, platform: Optional[str] = None, status: Optional[str] = None) -> int:
        """Count tasks with optional filtering.

        Args:
            platform: Filter by platform name.
            status: Filter by task status.

        Returns:
            Number of matching tasks.
        """
        return len(self.list_all(platform=platform, status=status))

    def _iter_records(self) -> Iterator[Dict[str, Any]]:
        """Iterate over all records in the storage file.

        Yields:
            Each record as a dict.
        """
        if not self.tasks_file.exists():
            return

        with open(self.tasks_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue

    def _write_all(self, records: List[Dict[str, Any]]) -> None:
        """Write all records to the storage file.

        Args:
            records: List of records to write.
        """
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")