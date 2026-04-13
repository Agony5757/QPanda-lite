"""Dicke state preparation circuit using the SCUC algorithm."""

__all__ = ["dicke_state_circuit"]

from typing import List, Optional
import math

from qpandalite.circuit_builder import Circuit


def _dicke_unitary(circuit: Circuit, i: int, j: int, n: int) -> None:
    r"""Apply a single SCUC rotation unitary.

    Implements the controlled rotation that redistributes amplitude
    between basis states differing at positions *i* and *i+1* during
    the Dicke-state construction (layer *j*, position *i*).

    The gate sequence is equivalent to a controlled :math:`R_y(2\theta)`
    where :math:`\theta = \arccos\!\sqrt{(j)/(i+2)}`, decomposed into
    elementary CNOT + single-qubit rotations.

    Args:
        circuit: Circuit to modify (in-place).
        i: Current qubit index (0-based, ``0 ≤ i < n-1``).
        j: Current layer index (1-based, ``1 ≤ j ≤ k``).
        n: Total number of qubits.
    """
    # Rotation angle: theta = arccos(sqrt(j / (i + 2)))
    # where i is 0-based index in the SCUC paper's (i+1) convention
    theta = math.acos(math.sqrt(j / (i + 2)))

    # Decompose controlled-Ry(2*theta) using CNOT sandwich
    # Controlled-Ry = Ry(theta) on target, CNOT ctrl->tgt, Ry(-theta) on target, CNOT ctrl->tgt
    circuit.ry(theta, i + 1)
    circuit.cnot(i, i + 1)
    circuit.ry(-theta, i + 1)
    circuit.cnot(i, i + 1)


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

    This implementation uses the **SCUC** (Sequential Conditional Unitary
    Cascade) algorithm from Bärtschi & Eidenbenz (2019), which constructs
    the state using only CNOT and single-qubit rotation gates in
    :math:`O(nk)` depth.

    Algorithm outline:
      1. Initialize the first *k* qubits to :math:`|1\rangle` (X gates).
      2. For each layer ``j = k, k-1, …, 1`` and each position
         ``i = j-1, j, …, n-2``, apply a controlled rotation that
         redistributes weight to basis states with a ``1`` at position
         ``i+1`` instead of position ``i``.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        k: Number of excitations (``1``s) in the target Dicke state.
            Must satisfy ``1 <= k <= n``.
        qubits: Qubit indices to use.  ``None`` means all qubits of
            *circuit* (``list(range(circuit.n_qubits))``).  Must contain
            at least *k* qubits.

    Raises:
        ValueError: If *k* is not in ``[1, n]``.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import dicke_state_circuit
        >>> c = Circuit(4)
        >>> dicke_state_circuit(c, k=2)
    """
    if qubits is None:
        qubits = list(range(circuit.n_qubits))

    n = len(qubits)

    if k < 1 or k > n:
        raise ValueError(f"k must satisfy 1 <= k <= n (got k={k}, n={n})")

    # Step 1: Initialize first k qubits to |1⟩
    for i in range(k):
        circuit.x(qubits[i])

    # Step 2: SCUC cascade
    # For each layer j from k down to 1
    for j in range(k, 0, -1):
        # For each position i from j-1 to n-2
        for i in range(j - 1, n - 1):
            _dicke_unitary(circuit, i, j, n)
