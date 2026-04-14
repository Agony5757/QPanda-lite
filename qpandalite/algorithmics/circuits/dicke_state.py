"""Dicke state preparation circuit."""

__all__ = ["dicke_state_circuit"]

from typing import List, Optional
import numpy as np

from qpandalite.circuit_builder import Circuit


def dicke_state_circuit(
    circuit: Circuit,
    k: int,
    qubits: Optional[List[int]] = None,
) -> None:
    r"""Prepare the Dicke state :math:`|D(n,k)\rangle`.

    The Dicke state :math:`|D(n,k)\rangle` is the equal superposition of
    all :math:`\binom{n}{k}` computational basis states with exactly *k*
    qubits in :math:`|1\rangle`:

    .. math::

        |D(n,k)\rangle = \frac{1}{\sqrt{\binom{n}{k}}}
        \sum_{x\,\in\,\{0,1\}^n,\;|x|=k} |x\rangle

    The implementation constructs the target state vector directly and
    prepares it using the Shende–Bullock–Markov rotation-based scheme
    (:func:`rotation_prepare`).

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        k: Number of excitations (``1``s) in the target Dicke state.
            Must satisfy ``1 <= k <= n``.
        qubits: Qubit indices to use.  ``None`` means all qubits of
            *circuit* (``list(range(circuit.qubit_num))``).  Must contain
            at least *k* qubits.

    Raises:
        ValueError: If *k* is not in ``[1, n]``.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import dicke_state_circuit
        >>> c = Circuit()
        >>> dicke_state_circuit(c, k=2, qubits=[0, 1, 2, 3])
    """
    if qubits is None:
        qubits = list(range(circuit.qubit_num))

    n = len(qubits)

    if k < 1 or k > n:
        raise ValueError(f"k must satisfy 1 <= k <= n (got k={k}, n={n})")

    if k == n:
        for q in qubits:
            circuit.x(q)
        return

    d = 2 ** n
    target = np.zeros(d, dtype=complex)
    count = 0
    for i in range(d):
        if bin(i).count('1') == k:
            target[i] = 1.0
            count += 1
    target /= np.sqrt(count)

    from qpandalite.algorithmics.state_preparation.rotation_prepare import rotation_prepare
    rotation_prepare(circuit, target, qubits)
