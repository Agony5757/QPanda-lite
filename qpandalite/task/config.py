"""Unified configuration management for task backends.

All configuration is read from environment variables.  JSON config files
are deprecated and only used as a fallback when the corresponding
environment variables are not set.

Environment variables
---------------------
OriginQ Cloud:
    QPANDA_API_KEY       : API authentication token (required for origin_qcloud)
    QPANDA_SUBMIT_URL    : Task submission endpoint URL
    QPANDA_QUERY_URL     : Task query endpoint URL
    QPANDA_TASK_GROUP_SIZE: Max circuits per submission (default: 200)

Quafu:
    QUAHU_API_TOKEN       : Quafu API token (required for quafu)

IBM:
    IBM_TOKEN             : IBM Quantum API token (required for ibm)

OriginQ Dummy (local simulation):
    ORIGINQ_AVAILABLE_QUBITS   : JSON list of available qubit indices
    ORIGINQ_AVAILABLE_TOPOLOGY: JSON list of [u, v] edge pairs
    ORIGINQ_TASK_GROUP_SIZE    : Max circuits per group (default: 200)

Deprecated config files (fallback only):
    originq_cloud_config.json   -> QPANDA_* env vars
    quafu_online_config.json    -> QUAFU_API_TOKEN
    ibm_online_config.json     -> IBM_TOKEN
    originq_online_config.json -> ORIGINQ_* env vars

"""

from __future__ import annotations

__all__ = ["load_originq_config", "load_quafu_config", "load_ibm_config", "load_dummy_config"]

import json
import os
import warnings
from pathlib import Path
from typing import Any


def _read_json_config(filename: str) -> dict[str, Any] | None:
    """Read a JSON config file as a deprecated fallback.

    Returns None if the file does not exist.
    Raises ImportError if the file exists but cannot be parsed.
    """
    if os.path.exists(filename):
        warnings.warn(
            f"Config file '{filename}' is deprecated. "
            f"Use environment variables instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        with open(filename, encoding="utf-8") as fp:
            return json.load(fp)
    return None


# ---------------------------------------------------------------------------
# OriginQ Cloud
# ---------------------------------------------------------------------------

def load_originq_config() -> dict[str, Any]:
    """Load OriginQ Cloud configuration from environment variables.

    Fallback order:
        1. Environment variables (QPANDA_*)
        2. originq_cloud_config.json (deprecated)

    Returns:
        dict with keys: api_key, submit_url, query_url, task_group_size,
                        available_qubits

    Raises:
        ImportError: If neither env vars nor config file is available.
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

    # Deprecated fallback
    config = _read_json_config("originq_cloud_config.json")
    if config is not None:
        return {
            "api_key": config.get("apitoken", ""),
            "submit_url": config.get("submit_url", ""),
            "query_url": config.get("query_url", ""),
            "task_group_size": config.get("task_group_size", 200),
            "available_qubits": config.get("available_qubits", []),
        }

    raise ImportError(
        "OriginQ Cloud config not found. "
        "Set QPANDA_API_KEY, QPANDA_SUBMIT_URL, QPANDA_QUERY_URL "
        "environment variables, or provide originq_cloud_config.json (deprecated)."
    )


# ---------------------------------------------------------------------------
# Quafu
# ---------------------------------------------------------------------------

def load_quafu_config() -> dict[str, Any]:
    """Load Quafu configuration from environment variables.

    Fallback order:
        1. Environment variables (QUAFU_API_TOKEN)
        2. quafu_online_config.json (deprecated)

    Returns:
        dict with key: api_token

    Raises:
        ImportError: If neither env vars nor config file is available.
    """
    api_token = os.getenv("QUAFU_API_TOKEN")

    if api_token:
        return {"api_token": api_token}

    # Deprecated fallback
    config = _read_json_config("quafu_online_config.json")
    if config is not None:
        return {"api_token": config.get("default_token", "")}

    raise ImportError(
        "Quafu config not found. "
        "Set QUAHU_API_TOKEN environment variable, "
        "or provide quafu_online_config.json (deprecated)."
    )


# ---------------------------------------------------------------------------
# IBM Quantum
# ---------------------------------------------------------------------------

def load_ibm_config() -> dict[str, Any]:
    """Load IBM Quantum configuration from environment variables.

    Fallback order:
        1. Environment variables (IBM_TOKEN)
        2. ibm_online_config.json (deprecated)

    Returns:
        dict with key: api_token

    Raises:
        ImportError: If neither env vars nor config file is available.
    """
    api_token = os.getenv("IBM_TOKEN")

    if api_token:
        return {"api_token": api_token}

    # Deprecated fallback
    config = _read_json_config("ibm_online_config.json")
    if config is not None:
        return {"api_token": config.get("default_token", "")}

    raise ImportError(
        "IBM Quantum config not found. "
        "Set IBM_TOKEN environment variable, "
        "or provide ibm_online_config.json (deprecated)."
    )


# ---------------------------------------------------------------------------
# OriginQ Dummy (local simulation)
# ---------------------------------------------------------------------------

def load_dummy_config() -> dict[str, Any]:
    """Load OriginQ Dummy simulation configuration from environment variables.

    Fallback order:
        1. Environment variables (ORIGINQ_*)
        2. originq_online_config.json (deprecated)

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

    # Deprecated fallback
    config = _read_json_config("originq_online_config.json")
    if config is not None:
        return {
            "available_qubits": config.get("available_qubits", []),
            "available_topology": config.get("available_topology", []),
            "task_group_size": config.get("task_group_size", 200),
        }

    # No config at all — use empty defaults (dummy works without chip info)
    warnings.warn(
        "OriginQ Dummy config not found. Using empty defaults "
        "(all qubits allowed, no topology restriction).",
        ImportWarning,
        stacklevel=2,
    )
    return {
        "available_qubits": [],
        "available_topology": [],
        "task_group_size": 200,
    }
