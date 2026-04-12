"""Hadamard superposition preparation.

Creates a uniform superposition over the specified qubits.
"""

__all__ = ["hadamard_superposition"]

from typing import List, Optional

from qpandalite.circuit_builder import Circuit


def hadamard_superposition(
    circuit: Circuit,
    qubits: Optional[List[int]] = None,
) -> None:
    """Create a uniform Hadamard superposition on the given qubits.

    Applies an H gate to every qubit in *qubits*, transforming
    |0...0> into an equal superposition of all 2^n basis states:

    .. math::

        |0\\rangle^{\\otimes n} \\xrightarrow{H^{\\otimes n}}
        \\frac{1}{\\sqrt{2^n}} \\sum_{k=0}^{2^n-1} |k\\rangle

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        qubits: Qubit indices to apply H to.  ``None`` means all qubits
            (``list(range(circuit.max_qubit + 1))``).

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.state_preparation import hadamard_superposition
        >>> c = Circuit()
        >>> c.allocate_qubits(3)
        [0, 1, 2]
        >>> hadamard_superposition(c)       # (|0>+|1>)/√2 ⊗ 3
    """
    if qubits is None:
        qubits = list(range(circuit.max_qubit + 1))

    for q in qubits:
        circuit.h(q)
