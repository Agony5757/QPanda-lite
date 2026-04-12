"""Dicke state preparation.

Prepares the symmetric Dicke state |D(n,k)> — the equal superposition
of all n-qubit basis states with exactly k excitations (ones).
"""

__all__ = ["dicke_state"]

from typing import List, Optional
import numpy as np
from qpandalite.circuit_builder import Circuit


def dicke_state(
    circuit: Circuit,
    qubits: Optional[List[int]] = None,
    k: int = 1,
) -> None:
    """Prepare the symmetric Dicke state |D(n,k)>.

    The Dicke state is the equal superposition of all weight-k computational
    basis states on n qubits:

    .. math::

        |D(n,k)\\rangle = \\frac{1}{\\sqrt{\\binom{n}{k}}}
        \\sum_{\\substack{x \\in \\{0,1\\}^n \\\\
        |x|=k}} |x\\rangle

    The target state vector is constructed directly and prepared using
    :func:`rotation_prepare`.

    Args:
        circuit: Quantum circuit (mutated in-place).
        qubits: Qubit indices to use.  ``None`` → all circuit qubits.
        k: Number of excitations (0 ≤ k ≤ n).

    Raises:
        ValueError: *k* is negative or exceeds the number of qubits.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.state_preparation import dicke_state
        >>> c = Circuit()
        >>> dicke_state(c, qubits=[0, 1, 2], k=1)  # |D(3,1)>
    """
    if qubits is None:
        qubits = list(range(circuit.max_qubit + 1))

    n = len(qubits)

    if k < 0:
        raise ValueError(f"k must be non-negative, got {k}")
    if k > n:
        raise ValueError(f"k ({k}) must not exceed n ({n})")
    if k == 0:
        return  # |00...0> already prepared
    if k == n:
        for q in qubits:
            circuit.x(q)
        return

    # Build the target state vector
    d = 2**n
    target = np.zeros(d, dtype=complex)
    count = 0
    for i in range(d):
        if bin(i).count('1') == k:
            target[i] = 1.0
            count += 1
    target /= np.sqrt(count)

    from .rotation_prepare import rotation_prepare
    rotation_prepare(circuit, target, qubits)
