"""Platform template defining the standard task interface.

This module specifies the common API that every platform backend must
implement.  The functions below are stubs (``pass``) and serve only as a
contract reference.  Each platform sub-module (e.g. ``origin_qcloud``,
``quafu``, ``ibm``) provides its own concrete implementation of these
functions.

Public API:
    - submit_task — Submit quantum circuit(s) for execution.
    - query_by_taskid — Asynchronously query task status by task ID.
    - query_by_taskid_sync — Synchronously query task status (blocking).
    - query_all_task — Query status of all locally recorded tasks.
"""

from typing import Any, Union, List, AnyStr
from os import PathLike

def submit_task(
    circuit : Union[List[str], str], 
    task_name : str, 
    tasktype : Any,
    chip_id : Any,
    shots : int,
    circuit_optimize : Union[bool, Any],
    measurement_amend : Union[bool, Any],
    auto_mapping : Union[bool, Any],
    specified_block : Union[bool, Any],
    savepath : PathLike,
    url : Union[str, Any],
    **kwargs
):   
    """Submit one or more quantum circuits for execution on the backend.

    Args:
        circuit (Union[List[str], str]): A single OriginIR circuit string or
            a list of OriginIR circuit strings.
        task_name (str): Human-readable name for the task.
        tasktype (Any): Backend-specific task type identifier.
        chip_id (Any): Identifier for the target quantum chip.
        shots (int): Number of measurement shots per circuit.
        circuit_optimize (Union[bool, Any]): Whether to apply circuit
            optimization / transpilation.
        measurement_amend (Union[bool, Any]): Whether to apply measurement
            error mitigation.
        auto_mapping (Union[bool, Any]): Whether to automatically map logical
            qubits to physical qubits.
        specified_block (Union[bool, Any]): Reserved — specify a physical
            block on the chip.
        savepath (os.PathLike): Directory for persisting local task records.
        url (Union[str, Any]): Backend submission endpoint URL.
        **kwargs: Additional platform-specific keyword arguments.

    Returns:
        str: The task ID assigned by the backend.
    """
    pass

def query_by_taskid(taskid : Union[List[str], str], 
                    url : Union[str, Any], 
                    **kwargs
                    ):
    """Asynchronously query the status of one or more tasks by task ID.

    This function returns immediately without waiting for the task to finish.

    Args:
        taskid (Union[List[str], str]): A single task ID or a list of task
            IDs.
        url (Union[str, Any]): Backend query endpoint URL.
        **kwargs: Additional platform-specific keyword arguments.

    Returns:
        dict: A dict with ``'status'`` (``'success'`` | ``'failed'`` |
        ``'running'``) and ``'result'`` (present when status is
        ``'success'`` or ``'failed'``).
    """
    pass

def query_by_taskid_sync(taskid : Union[List[str], str], 
                         interval : float, 
                         timeout : float, 
                         retry : int,
                         url : Union[str, Any],
                         **kwargs):
    """Synchronously query task status, blocking until completion or timeout.

    Polls the backend at regular intervals until the task finishes,
    times out, or retries are exhausted.

    Args:
        taskid (Union[List[str], str]): A single task ID or a list of task
            IDs.
        interval (float): Polling interval in seconds.
        timeout (float): Maximum total wait time in seconds.
        retry (int): Number of retry attempts on transient errors.
        url (Union[str, Any]): Backend query endpoint URL.
        **kwargs: Additional platform-specific keyword arguments.

    Returns:
        list[dict]: The execution results once the task succeeds.

    Raises:
        TimeoutError: If *timeout* is exceeded.
        RuntimeError: If the task fails or retries are exhausted.
    """
    pass


def query_all_task(url : Union[str, Any], 
                   savepath : Union[str, Any],
                   **kwargs):
    """Query the status of all locally recorded tasks.

    Iterates over tasks saved in *savepath* and queries each one from
    the backend, caching finished results locally.

    Args:
        url (Union[str, Any]): Backend query endpoint URL.
        savepath (Union[str, Any]): Directory containing local task records.
        **kwargs: Additional platform-specific keyword arguments.

    Returns:
        tuple[int, int]: A ``(finished_count, total_count)`` pair.
    """
    pass
