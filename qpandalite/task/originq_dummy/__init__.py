"""OriginQ dummy backend — local simulator emulating the Origin Quantum Cloud."""
__all__ = [
    'set_dummy_path',
    'save_dummy_cache',
    'submit_task',
    'query_by_taskid',
    'query_by_taskid_sync',
    'query_all_tasks',
    'query_all_task',
]
from .task import set_dummy_path, save_dummy_cache, submit_task, query_by_taskid, query_by_taskid_sync, query_all_tasks, query_all_task
