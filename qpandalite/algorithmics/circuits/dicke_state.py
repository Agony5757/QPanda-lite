"""Dicke state preparation circuit using the SCUC algorithm.

Reference:
    Bärtschi & Eidenbenz, "Deterministic Preparation of Dicke States",
    FCT 2019, arXiv:1904.07358.
"""

__all__ = ["dicke_state_circuit"]

from typing import List, Optional
import math

from qpandalite.circuit_builder import Circuit


def _gate_i(circuit: Circuit, q0: int, q1: int, n: int) -> None:
    """2-qubit Givens rotation in the {|10⟩, |01⟩} subspace.

    Angle θ = 2 * arccos(sqrt(1/n)).
    Decomposition: CX(q0,q1) · CRY(q1→q0, θ) · CX(q0,q1).
    """
    theta = 2.0 * math.acos(math.sqrt(1.0 / n))
    circuit.cnot(q0, q1)
    circuit.add_gate("RY", q0, params=theta, control_qubits=[q1])
    circuit.cnot(q0, q1)


def _ccry(circuit: Circuit, c1: int, c2: int, target: int, theta: float) -> None:
    """Doubly-controlled RY gate, decomposed via Toffoli + CRY.

    Applies RY(theta) on *target* iff both c1 and c2 are |1⟩.
    QPanda-lite has no native ccry, so we use:
        CRY(c2→target, θ/2) · CCX(c1,c2,target) ·
        CRY(c2→target, -θ/2) · CCX(c1,c2,target)
    """
    circuit.add_gate("RY", target, params=theta / 2.0, control_qubits=[c2])
    circuit.toffoli(c1, c2, target)
    circuit.add_gate("RY", target, params=-theta / 2.0, control_qubits=[c2])
    circuit.toffoli(c1, c2, target)


def _gate_ii_l(circuit: Circuit, q0: int, q1: int, q2: int, l: int, n: int) -> None:
    """3-qubit controlled Givens rotation (gate_(ii)_l in SCUC).

    Angle θ = 2 * arccos(sqrt(l/n)).
    Decomposition: CX(q0,q2) · CCRY(q2,q1→q0, θ) · CX(q0,q2).
    """
    theta = 2.0 * math.acos(math.sqrt(float(l) / n))
    circuit.cnot(q0, q2)
    _ccry(circuit, q2, q1, q0, theta)
    circuit.cnot(q0, q2)


def _scs(circuit: Circuit, qubits: List[int], n: int, k: int) -> None:
    """One Split-and-Cyclic-Shift (SCS) unitary SCS_{n,k}.

    *qubits* must have length k+1 (indices q_0 … q_k).
    Applies gate_i on (qubits[k-1], qubits[k]) followed by
    gate_ii_l for l = 2 … k on (qubits[k-l], qubits[k-l+1], qubits[k]).
    """
    _gate_i(circuit, qubits[k - 1], qubits[k], n)
    for l in range(2, k + 1):
        _gate_ii_l(circuit, qubits[k - l], qubits[k - l + 1], qubits[k], l, n)


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
    Cascade) algorithm from Bärtschi & Eidenbenz (2019), built from CNOT,
    CRY, and Toffoli gates in :math:`O(nk)` depth.

    Algorithm outline:
      1. Initialize the **last** *k* qubits to :math:`|1\rangle` (X gates).
      2. first_block: for l = n, n-1, …, k+1 apply SCS_{l,k} on the first
         l qubits.
      3. second_block: for l = k, k-1, …, 2 apply SCS_{l,l-1} on the first
         l qubits.

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

    # Step 1: Initialize last k qubits to |1⟩
    for q in qubits[n - k:]:
        circuit.x(q)

    # Step 2: first_block — propagate excitations leftward
    # Each SCS_{l,k} unit uses exactly k+1 qubits: the LAST k+1 of the first l.
    for l in range(n, k, -1):
        _scs(circuit, qubits[l - k - 1 : l], l, k)

    # Step 3: second_block — balance excitations within the first k qubits
    for l in range(k, 1, -1):
        _scs(circuit, qubits[:l], l, l - 1)
