"""Entangled state preparation circuits: GHZ, W, and Cluster states."""

__all__ = [
    "ghz_state",
    "w_state",
    "cluster_state",
]

from typing import List, Optional, Tuple
import math

from qpandalite.circuit_builder import Circuit


def ghz_state(
    circuit: Circuit,
    qubits: Optional[List[int]] = None,
) -> None:
    r"""Prepare a GHZ (Greenberger–Horne–Zeilinger) state.

    Produces the state:

    .. math::

        \frac{1}{\sqrt{2}}(|00\ldots0\rangle + |11\ldots1\rangle)

    Implementation:

    1. Hadamard on the first qubit: :math:`\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)`
    2. Chain of CNOT gates: ``CNOT(q[0], q[1])``, ``CNOT(q[1], q[2])``, ...

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        qubits: Qubit indices. ``None`` means all qubits of *circuit*.

    Raises:
        ValueError: Fewer than 2 qubits.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import ghz_state
        >>> c = Circuit(3)
        >>> ghz_state(c)
    """
    if qubits is None:
        qubits = list(range(circuit.qubit_num))

    n = len(qubits)
    if n < 2:
        raise ValueError("ghz_state requires at least 2 qubits")

    circuit.h(qubits[0])
    for i in range(n - 1):
        circuit.cnot(qubits[i], qubits[i + 1])


def w_state(
    circuit: Circuit,
    qubits: Optional[List[int]] = None,
) -> None:
    r"""Prepare a W state.

    Produces the state:

    .. math::

        \frac{1}{\sqrt{n}}(|10\ldots0\rangle + |01\ldots0\rangle +
        \ldots + |00\ldots1\rangle)

    Uses a recursive controlled-rotation cascade decomposition
    (Cruz et al., 2019). For *n* qubits the circuit depth is O(n)
    and requires no ancillas.

    The algorithm works by distributing amplitude from qubit 0
    to subsequent qubits via controlled rotation + CNOT pairs.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        qubits: Qubit indices. ``None`` means all qubits of *circuit*.

    Raises:
        ValueError: Fewer than 2 qubits.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import w_state
        >>> c = Circuit(4)
        >>> w_state(c)
    """
    if qubits is None:
        qubits = list(range(circuit.qubit_num))

    n = len(qubits)
    if n < 2:
        raise ValueError("w_state requires at least 2 qubits")

    # Start with |100...0⟩
    circuit.x(qubits[0])

    # Recursive decomposition:
    # For n qubits, distribute the excitation from q[0] to q[1], q[2], ...
    _w_state_recursive(circuit, qubits, 0, n)


def _w_state_recursive(
    circuit: Circuit,
    qubits: List[int],
    start: int,
    length: int,
) -> None:
    """Recursively distribute excitation for W state preparation.

    Uses controlled rotations to split amplitude from qubits[start]
    across qubits[start..start+length-1]. Transfers amplitude
    sqrt((length-1)/length) from qubits[start] to qubits[start+1]
    via F-gate (controlled-Ry + disentangling CNOT), then recurses
    on qubits[start+1..start+length-1].
    """
    if length <= 1:
        return

    control = qubits[start]
    target = qubits[start + 1]

    # theta chosen so that amplitude on |control=1⟩ becomes 1/sqrt(length)
    # and amplitude on |target=1⟩ becomes sqrt((length-1)/length).
    theta = 2 * math.acos(1.0 / math.sqrt(length))

    # Decompose controlled-Ry(theta) (control -> target) as
    # Ry(theta/2) on target, CNOT, Ry(-theta/2) on target, CNOT.
    circuit.ry(target, theta / 2)
    circuit.cnot(control, target)
    circuit.ry(target, -theta / 2)
    circuit.cnot(control, target)

    # Disentangle: if target is now |1⟩, flip control back to |0⟩ so
    # the excitation is uniquely located on exactly one qubit.
    circuit.cnot(target, control)

    _w_state_recursive(circuit, qubits, start + 1, length - 1)


def cluster_state(
    circuit: Circuit,
    qubits: Optional[List[int]] = None,
    edges: Optional[List[Tuple[int, int]]] = None,
) -> None:
    r"""Prepare a cluster state (graph state).

    A cluster state is prepared by:

    1. Applying Hadamard to all qubits: :math:`H^{\otimes n}`
    2. Applying CZ (controlled-Z) on each edge of the graph

    The resulting state is:

    .. math::

        \frac{1}{\sqrt{2^n}} \sum_{x \in \{0,1\}^n} (-1)^{\sum_{(i,j) \in E}
        x_i x_j} |x\rangle

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        qubits: Qubit indices. ``None`` means all qubits of *circuit*.
        edges: List of (source, target) pairs defining the entanglement graph.
            Indices refer to positions in *qubits*. ``None`` uses a linear
            nearest-neighbor chain: ``(0,1), (1,2), (2,3), ...``.

    Raises:
        ValueError: Fewer than 1 qubit.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import cluster_state
        >>> c = Circuit(4)
        >>> cluster_state(c)  # linear chain
        >>> # Custom graph (square)
        >>> c2 = Circuit(4)
        >>> cluster_state(c2, edges=[(0,1), (1,2), (2,3), (3,0)])
    """
    if qubits is None:
        qubits = list(range(circuit.qubit_num))

    n = len(qubits)
    if n < 1:
        raise ValueError("cluster_state requires at least 1 qubit")

    # Step 1: Hadamard on all qubits
    for q in qubits:
        circuit.h(q)

    # Step 2: CZ on each edge
    if edges is None:
        # Linear chain
        edges = [(i, i + 1) for i in range(n - 1)]

    for src_idx, tgt_idx in edges:
        if src_idx >= n or tgt_idx >= n:
            raise ValueError(
                f"Edge ({src_idx}, {tgt_idx}) out of range for {n} qubits"
            )
        circuit.cz(qubits[src_idx], qubits[tgt_idx])
