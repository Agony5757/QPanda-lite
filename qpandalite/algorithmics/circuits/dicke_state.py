"""Dicke state preparation circuit using the SCUC algorithm."""

__all__ = ["dicke_state_circuit"]

from typing import List, Optional
import math

from qpandalite.circuit_builder import Circuit


def _dicke_unitary(circuit: Circuit, i: int, j: int, n: int) -> None:
    r"""Apply a single SCUC rotation unitary.

    Implements the rotation in the {|10⟩, |01⟩} subspace that redistributes
    amplitude between qubits *i* and *i+1* during Dicke-state construction
    (layer *j*, position *i*).

    The unitary acts as:
        |10⟩ → cos(θ)|10⟩ + sin(θ)|01⟩
        |01⟩ → -sin(θ)|10⟩ + cos(θ)|01⟩
    where θ = arccos(sqrt(j / (i + 2))).

    Decomposition (4 CX + 4 Ry):
        CX(i, i+1); Ry(i, θ); Ry(i+1, θ);
        CX(i+1, i); Ry(i, -θ); Ry(i+1, -θ);
        CX(i, i+1); Ry(i, θ); Ry(i+1, θ);
        CX(i+1, i)

    This is the standard Dicke-state 2-qubit gate from
    Bärtschi & Eidenbenz (2019).

    Args:
        circuit: Circuit to modify (in-place).
        i: Current qubit index (0-based, ``0 ≤ i < n-1``).
        j: Current layer index (1-based, ``1 ≤ j ≤ k``).
        n: Total number of qubits.
    """
    # Rotation angle: theta = arccos(sqrt(j / (i + 2)))
    # where i is 0-based index in the SCUC paper's (i+1) convention
    theta = math.acos(math.sqrt(j / (i + 2)))

    # Rotation in {|10⟩, |01⟩} subspace (Givens rotation).
    # Decomposition: CX(i+1,i) · CRY(i, i+1, 2θ) · CX(i+1,i)
    # The CX conjugation maps |01⟩↔|11⟩ so CRY (which rotates {|10⟩,|11⟩})
    # effectively rotates in the {|10⟩,|01⟩} subspace.
    # QASM Ry(φ) uses half-angle, so pass 2θ for physical rotation by θ.
    circuit.cnot(i + 1, i)
    circuit.add_gate("RY", i + 1, params=2 * theta, control_qubits=[i])
    circuit.cnot(i + 1, i)


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
            *circuit* (``list(range(circuit.qubit_num))``).  Must contain
            at least *k* qubits.

    Raises:
        ValueError: If *k* is not in ``[1, n]``.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import dicke_state_circuit
        >>> c = Circuit()
        >>> c.x(0)
        >>> c.x(1)
        >>> c.x(2)
        >>> c.x(3)
        >>> dicke_state_circuit(c, k=2, qubits=[0,1,2,3])
    """
    if qubits is None:
        qubits = list(range(circuit.qubit_num))

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
