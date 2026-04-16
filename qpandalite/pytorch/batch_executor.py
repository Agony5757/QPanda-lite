"""
Batch execution utilities for quantum circuits.

Provides parallel execution of multiple circuits using ThreadPoolExecutor
or multiprocessing for performance optimization.
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from qpandalite.circuit_builder import Circuit

__all__ = ["batch_execute"]


def batch_execute(
    circuits: list[Circuit],
    executor: Callable[[Circuit], np.ndarray],
    n_workers: int = 4,
) -> list[np.ndarray]:
    """Execute multiple circuits in parallel.

    Args:
        circuits: List of circuits to execute
        executor: Function that executes a single circuit and returns results
        n_workers: Number of parallel workers (threads)

    Returns:
        List of results from each circuit execution

    Example:
        >>> def simulate(c):
        ...     sim = OriginIR_Simulator()
        ...     return sim.simulate(c.originir)
        >>> results = batch_execute([c1, c2, c3], simulate, n_workers=4)
    """
    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        results = list(pool.map(executor, circuits))
    return results


def batch_execute_with_params(
    circuit_template: Circuit,
    param_values: list[dict[str, float]],
    executor: Callable[[Circuit], np.ndarray],
    n_workers: int = 4,
) -> list[np.ndarray]:
    """Execute a circuit template with different parameter bindings.

    Creates multiple bound circuits from a template and executes them
    in parallel.

    Args:
        circuit_template: Circuit template with symbolic parameters
        param_values: List of parameter value dictionaries to bind
        executor: Function that executes a single circuit
        n_workers: Number of parallel workers

    Returns:
        List of results from each parameter binding

    Example:
        >>> params = [{'theta': 0.1}, {'theta': 0.2}, {'theta': 0.3}]
        >>> results = batch_execute_with_params(circuit, params, simulate)
    """
    circuits = []
    for values in param_values:
        bound_circuit = circuit_template.copy()
        if hasattr(bound_circuit, "_parameters"):
            for name, value in values.items():
                if name in bound_circuit._parameters:
                    bound_circuit._parameters[name].bind(value)
        circuits.append(bound_circuit)

    return batch_execute(circuits, executor, n_workers)
