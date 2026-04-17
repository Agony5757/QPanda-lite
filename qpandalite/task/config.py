"""Unified configuration management for task backends.

All configuration is read from environment variables.

Environment variables
---------------------
OriginQ Cloud:
    QPANDA_API_KEY       : API authentication token (required)
    QPANDA_SUBMIT_URL    : Task submission endpoint URL (required)
    QPANDA_QUERY_URL     : Task query endpoint URL (required)
    QPANDA_TASK_GROUP_SIZE: Max circuits per submission (default: 200)

Quafu:
    QUAFU_API_TOKEN       : Quafu API token (required)

IBM:
    IBM_TOKEN             : IBM Quantum API token (required)

OriginQ Dummy (local simulation):
    ORIGINQ_AVAILABLE_QUBITS   : JSON list of available qubit indices
    ORIGINQ_AVAILABLE_TOPOLOGY: JSON list of [u, v] edge pairs
    ORIGINQ_TASK_GROUP_SIZE    : Max circuits per group (default: 200)

"""

from __future__ import annotations

__all__ = ["load_originq_config", "load_quafu_config", "load_ibm_config", "load_dummy_config"]

import json
import os
import warnings
from typing import Any


# ---------------------------------------------------------------------------
# OriginQ Cloud
# ---------------------------------------------------------------------------

def load_originq_config() -> dict[str, Any]:
    """Load OriginQ Cloud configuration from environment variables.

    Returns:
        dict with keys: api_key, submit_url, query_url, task_group_size,
                        available_qubits

    Raises:
        ImportError: If required environment variables are not set.
    """
    api_key = os.getenv("QPANDA_API_KEY")
    submit_url = os.getenv("QPANDA_SUBMIT_URL")
    query_url = os.getenv("QPANDA_QUERY_URL")
    task_group_size_str = os.getenv("QPANDA_TASK_GROUP_SIZE")

    if api_key and submit_url and query_url:
        return {
            "api_key": api_key,
            "submit_url": submit_url,
            "query_url": query_url,
            "task_group_size": int(task_group_size_str) if task_group_size_str else 200,
            "available_qubits": [],
        }

    raise ImportError(
        "OriginQ Cloud config not found. "
        "Set QPANDA_API_KEY, QPANDA_SUBMIT_URL, QPANDA_QUERY_URL "
        "environment variables."
    )


# ---------------------------------------------------------------------------
# Quafu
# ---------------------------------------------------------------------------

def load_quafu_config() -> dict[str, Any]:
    """Load Quafu configuration from environment variables.

    Returns:
        dict with key: api_token

    Raises:
        ImportError: If the environment variable is not set.
    """
    api_token = os.getenv("QUAFU_API_TOKEN")

    if api_token:
        return {"api_token": api_token}

    raise ImportError(
        "Quafu config not found. "
        "Set QUAFU_API_TOKEN environment variable."
    )


# ---------------------------------------------------------------------------
# IBM Quantum
# ---------------------------------------------------------------------------

def load_ibm_config() -> dict[str, Any]:
    """Load IBM Quantum configuration from environment variables.

    Returns:
        dict with key: api_token

    Raises:
        ImportError: If the environment variable is not set.
    """
    api_token = os.getenv("IBM_TOKEN")

    if api_token:
        return {"api_token": api_token}

    raise ImportError(
        "IBM Quantum config not found. "
        "Set IBM_TOKEN environment variable."
    )


# ---------------------------------------------------------------------------
# OriginQ Dummy (local simulation)
# ---------------------------------------------------------------------------

def load_dummy_config() -> dict[str, Any]:
    """Load OriginQ Dummy simulation configuration from environment variables.

    Returns:
        dict with keys: available_qubits, available_topology, task_group_size
    """
    qubits_str = os.getenv("ORIGINQ_AVAILABLE_QUBITS")
    topology_str = os.getenv("ORIGINQ_AVAILABLE_TOPOLOGY")
    group_size_str = os.getenv("ORIGINQ_TASK_GROUP_SIZE")

    available_qubits: list[int] = []
    available_topology: list[list[int]] = []

    if qubits_str:
        available_qubits = json.loads(qubits_str)
    if topology_str:
        available_topology = json.loads(topology_str)

    if available_qubits or available_topology:
        return {
            "available_qubits": available_qubits,
            "available_topology": available_topology,
            "task_group_size": int(group_size_str) if group_size_str else 200,
        }

    # No config — use empty defaults (dummy works without chip info)
    return {
        "available_qubits": [],
        "available_topology": [],
        "task_group_size": 200,
    }
