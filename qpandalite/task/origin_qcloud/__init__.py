"""Origin Quantum Cloud (本源量子云) backend — the primary production backend."""
__all__ = [
    'submit_task',
    'query_by_taskid',
    'query_by_taskid_sync',
    'query_all_tasks',
    'query_all_task',
    'TASK_STATUS_FAILED',
    'TASK_STATUS_SUCCESS',
    'TASK_STATUS_RUNNING',
]
from .task import submit_task, query_by_taskid, query_by_taskid_sync, query_all_tasks, query_all_task, TASK_STATUS_FAILED, TASK_STATUS_SUCCESS, TASK_STATUS_RUNNING
