"""Computational basis-state preparation."""

__all__ = ["basis_state"]

from typing import List, Optional

from qpandalite.circuit_builder import Circuit


def basis_state(
    circuit: Circuit,
    state: int,
    qubits: Optional[List[int]] = None,
) -> None:
    """Prepare a computational basis state ``|state>`` on the given qubits.

    Applies X gates to the qubits whose corresponding bit in the binary
    representation of *state* is 1.  All other qubits are left in ``|0>``.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        state: Non-negative integer whose binary representation specifies
            the target basis state.  Qubit 0 corresponds to the
            **least-significant bit**.
        qubits: Qubit indices to use.  ``None`` means ``list(range(n_bits))``
            where *n_bits* is the number of bits needed.

    Raises:
        ValueError: *state* is negative.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.state_preparation import basis_state
        >>> c = Circuit()
        >>> basis_state(c, state=5, qubits=[0, 1, 2])  # |101>
    """
    if state < 0:
        raise ValueError(f"state must be non-negative, got {state}")

    n_bits = max(1, state.bit_length())
    if qubits is None:
        qubits = list(range(n_bits))

    for i, q in enumerate(qubits):
        if (state >> i) & 1:
            circuit.x(q)
