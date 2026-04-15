"""Dicke state preparation circuit using the SCUC algorithm."""

__all__ = ["dicke_state_circuit"]

from typing import List, Optional
import math

from qpandalite.circuit_builder import Circuit


def dicke_state_circuit(
    circuit: Circuit,
    k: int,
    qubits: Optional[List[int]] = None,
) -> None:
    r"""Prepare the Dicke state :math:`|D(n,k)\rangle`.

    The Dicke state :math:`|D(n,k)\rangle` is the equal superposition of
    all :math:`\binom{n}{k}` computational basis states with exactly *k*
    qubits in :math:`|1\rangle`.

    This implementation uses the SCUC (Single Combination Step) algorithm,
    which constructs the state using only CNOT and single-qubit rotation gates.

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

    # Step 1: initialize the last k qubits to |1>
    for i in range(n - k, n):
        circuit.x(qubits[i])

    # Step 2: SCS (Single Combination Step) cascade
    # Outer loop 1: reduce n down to k+1
    for current_n in range(n, k, -1):
        _scs_layer(circuit, current_n, k, qubits)

    # Outer loop 2: reduce k down to 2
    for current_k in range(k, 1, -1):
        _scs_layer(circuit, current_k, current_k - 1, qubits)


def _scs_layer(circuit: Circuit, m: int, l: int, qubits: list) -> None:
    """Apply one Single Combination Step layer.

    Args:
        m: Current block size.
        l: Maximum number of excitations in the current block.
    """
    # Base case (k=1): one control qubit
    theta = math.acos(math.sqrt(1 / m))
    tgt = qubits[m - 2]
    ctrl = qubits[m - 1]

    circuit.cx(tgt, ctrl)
    _cry(circuit, ctrl, tgt, 2 * theta)
    circuit.cx(tgt, ctrl)

    # General case (k>=2): two control qubits
    for i in range(2, l + 1):
        theta = math.acos(math.sqrt(i / m))
        tgt = qubits[m - 1 - i]
        ctrl1 = qubits[m - 1]
        ctrl2 = qubits[m - i]

        circuit.cx(tgt, ctrl1)
        _ccry(circuit, ctrl1, ctrl2, tgt, 2 * theta)
        circuit.cx(tgt, ctrl1)


def _cry(circuit: Circuit, ctrl: int, tgt: int, angle: float) -> None:
    """Decompose a Controlled-Ry gate."""
    circuit.ry(tgt, angle / 2)
    circuit.cx(ctrl, tgt)
    circuit.ry(tgt, -angle / 2)
    circuit.cx(ctrl, tgt)


def _ccry(circuit: Circuit, ctrl1: int, ctrl2: int, tgt: int, angle: float) -> None:
    """Decompose a doubly-Controlled-Ry gate."""
    _cry(circuit, ctrl2, tgt, angle / 2)
    circuit.cx(ctrl1, ctrl2)
    _cry(circuit, ctrl2, tgt, -angle / 2)
    circuit.cx(ctrl1, ctrl2)
    _cry(circuit, ctrl1, tgt, angle / 2)
