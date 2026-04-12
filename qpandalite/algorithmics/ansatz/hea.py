"""Hardware-Efficient Ansatz (HEA).

Generates a parameterised circuit with alternating layers of single-qubit
rotations and entangling CNOT gates, suitable for NISQ devices.
"""

__all__ = ["hea"]

from typing import List, Optional

import numpy as np
from qpandalite.circuit_builder import Circuit


def hea(
    n_qubits: int,
    depth: int = 1,
    qubits: Optional[List[int]] = None,
    params: Optional[np.ndarray] = None,
) -> Circuit:
    """Build a Hardware-Efficient Ansatz (HEA) circuit.

    The ansatz consists of *depth* repeated layers.  Each layer applies:

    1. ``Rz(q, θ) → Ry(q, θ)`` on every qubit (parameterised).
    2. A ring of CNOT gates: ``CNOT(i, (i+1) % n)`` for i = 0..n-1.

    The total number of parameters is ``2 * n_qubits * depth``.

    Args:
        n_qubits: Number of qubits.
        depth: Number of repeated layers (default 1).
        qubits: Qubit indices.  ``None`` → ``list(range(n_qubits))``.
        params: 1-D array of rotation angles.  ``None`` → random initialisation.

    Returns:
        A :class:`Circuit` object containing the ansatz gates.

    Raises:
        ValueError: *params* length does not match ``2 * n_qubits * depth``.

    Example:
        >>> from qpandalite.algorithmics.ansatz import hea
        >>> c = hea(n_qubits=4, depth=2)
        >>> c.max_qubit + 1
        4
    """
    if qubits is None:
        qubits = list(range(n_qubits))
    else:
        qubits = list(qubits)

    n_params = 2 * n_qubits * depth
    if params is None:
        params = np.random.uniform(0, 2 * np.pi, size=n_params)
    else:
        params = np.asarray(params)
        if len(params) != n_params:
            raise ValueError(
                f"Expected {n_params} parameters, got {len(params)}"
            )

    circuit = Circuit()
    idx = 0

    for _ in range(depth):
        # Single-qubit rotations
        for q in qubits:
            if abs(params[idx]) > 1e-15:
                circuit.rz(q, float(params[idx]))
            idx += 1
            if abs(params[idx]) > 1e-15:
                circuit.ry(q, float(params[idx]))
            idx += 1

        # Entangling layer (ring topology)
        for i in range(n_qubits):
            circuit.cx(qubits[i], qubits[(i + 1) % n_qubits])

    return circuit
