"""Quantum computing task management module.

This package provides a unified interface for submitting and querying
quantum computing tasks across multiple backend platforms:

- ``origin_qcloud`` — Origin Quantum Cloud (本源量子云), the primary production backend.
- ``originq_dummy`` — Local simulator that mimics the Origin Quantum Cloud API,
  useful for testing without consuming real quantum resources.
- ``originq`` — Legacy OriginQ QPilot interface (currently unavailable; raises
  ``ImportError`` on import).
- ``quafu`` — BAQIS ScQ quantum cloud platform (Quafu).
- ``ibm`` — IBM Quantum (Qiskit) backend.

Each platform sub-module exposes a consistent set of public functions:

- ``submit_task`` — Submit one or more quantum circuits for execution.
- ``query_by_taskid`` — Asynchronously query task status by task ID.
- ``query_by_taskid_sync`` — Synchronously query task status, blocking until
  completion or timeout.
- ``query_all_tasks`` — Query all tasks recorded in the local save directory.
"""
