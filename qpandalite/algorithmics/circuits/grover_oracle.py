"""Grover oracle and diffusion operator construction.

Provides reusable building blocks for Grover's quantum search algorithm:

* :func:`grover_oracle` — phase-flip oracle for a marked computational basis state.
* :func:`grover_diffusion` — Grover diffusion (amplitude amplification) operator.

Both functions operate on a :class:`~qpandalite.circuit_builder.Circuit` object
passed in by the caller, following the standard circuit-building convention of
``qpandalite.algorithmics.circuits``.

References:
    Grover, L. K. (1996). "A fast quantum mechanical algorithm for database
    search." STOC '96.  https://arxiv.org/abs/quant-ph/9605043
"""

__all__ = ["grover_oracle", "grover_diffusion"]

from typing import List, Optional

from qpandalite.circuit_builder import Circuit


def _apply_mcz(
    circuit: Circuit,
    controls: List[int],
    target: int,
) -> None:
    """Apply a multi-controlled Z gate.

    Decomposes MCZ as H(target) + MCX + H(target), where MCX uses
    Toffoli decomposition for 2 controls or native multi-controlled
    gate support for more.

    Args:
        circuit: Circuit to append gates to (mutated in-place).
        controls: List of control qubit indices.
        target: Target qubit index.
    """
    n = len(controls)
    if n == 0:
        circuit.z(target)
        return
    if n == 1:
        circuit.cz(controls[0], target)
        return

    circuit.h(target)

    # Multi-controlled X using Toffoli chain
    _apply_mcx(circuit, controls, target)

    circuit.h(target)


def _apply_mcx(
    circuit: Circuit,
    controls: List[int],
    target: int,
) -> None:
    """Apply a multi-controlled X gate using Toffoli decomposition.

    For 2 controls: direct Toffoli gate.
    For 3+ controls: uses native multi-controlled gate support via
    circuit.add_gate with control_qubits parameter.
    """
    n = len(controls)
    if n == 0:
        circuit.x(target)
    elif n == 1:
        circuit.cnot(controls[0], target)
    elif n == 2:
        circuit.toffoli(controls[0], controls[1], target)
    else:
        # Use native multi-controlled gate support
        circuit.add_gate("X", target, control_qubits=controls)


def grover_oracle(
    circuit: Circuit,
    marked_state: int,
    qubits: Optional[List[int]] = None,
    ancilla: Optional[int] = None,
) -> int:
    r"""Construct a phase-flip oracle for a marked basis state.

    The oracle flips the phase of the computational basis state whose integer
    encoding is *marked_state*, leaving all other states unchanged:

    .. math::

        U_f |x\rangle = (-1)^{[x = \text{marked}]} |x\rangle

    The implementation uses an ancilla qubit prepared in :math:`|-\rangle` and
    a multi-controlled Z gate.  X gates are applied before and after the MCZ to
    match the bit pattern of *marked_state*.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        marked_state: Non-negative integer encoding the marked basis state.
        qubits: Data qubit indices.  ``None`` means ``list(range(n_bits))``
            where *n_bits* is the number of bits needed to represent
            *marked_state* (at least 1).
        ancilla: Ancilla qubit index for the MCZ target.  ``None`` means
            ``max(qubits) + 1`` (auto-allocated).

    Returns:
        The ancilla qubit index that was used.

    Raises:
        ValueError: *marked_state* is negative or exceeds the addressable
            space of *qubits*.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import grover_oracle
        >>> c = Circuit()
        >>> for i in range(3):
        ...     c.h(i)          # uniform superposition
        >>> anc = grover_oracle(c, marked_state=5, qubits=[0, 1, 2])
    """
    if marked_state < 0:
        raise ValueError(f"marked_state must be non-negative, got {marked_state}")

    n_bits = max(1, marked_state.bit_length())
    if qubits is None:
        qubits = list(range(n_bits))
    n = len(qubits)

    if marked_state >= (1 << n):
        raise ValueError(
            f"marked_state {marked_state} requires {marked_state.bit_length()} "
            f"bits but only {n} qubits were provided"
        )

    if ancilla is None:
        ancilla = max(qubits) + 1

    # Initialise ancilla to |−⟩ = X·H·|0⟩
    circuit.x(ancilla)
    circuit.h(ancilla)

    # Bit pattern of marked_state (MSB first, aligned to qubits)
    marked_bits = [(marked_state >> (n - 1 - i)) & 1 for i in range(n)]

    # Flip qubits that should be |0⟩ in the marked state
    for i, bit in enumerate(marked_bits):
        if bit == 0:
            circuit.x(qubits[i])

    # Multi-controlled Z targeting the ancilla
    _apply_mcz(circuit, qubits, ancilla)

    # Flip back
    for i, bit in enumerate(marked_bits):
        if bit == 0:
            circuit.x(qubits[i])

    # Restore ancilla from |−⟩ back to |0⟩ (optional but keeps state clean)
    circuit.h(ancilla)
    circuit.x(ancilla)

    return ancilla


def grover_diffusion(
    circuit: Circuit,
    qubits: Optional[List[int]] = None,
    ancilla: Optional[int] = None,
) -> None:
    r"""Construct the Grover diffusion (amplitude amplification) operator.

    The diffusion operator is:

    .. math::

        D = 2|s\rangle\langle s| - I

    where :math:`|s\rangle = H^{\otimes n}|0\rangle^{\otimes n}` is the
    uniform superposition.  It is equivalent to:

    .. math::

        D = H^{\otimes n} \cdot \bigl(2|0\rangle\langle 0| - I\bigr)
            \cdot H^{\otimes n}

    The ``2|0⟩⟨0| - I`` part is implemented as X gates followed by a
    multi-controlled Z and X gates again.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        qubits: Data qubit indices.  ``None`` means ``[0, 1]`` (2 qubits).
        ancilla: Ancilla qubit for the MCZ decomposition.  ``None`` means
            ``max(qubits) + 1``.  Not needed when *qubits* has length 1
            (a single Z gate suffices).

    Raises:
        ValueError: Fewer than 1 qubit specified.
    """
    if qubits is None:
        qubits = [0, 1]
    n = len(qubits)
    if n < 1:
        raise ValueError("At least 1 qubit is required")

    # H on all qubits
    for q in qubits:
        circuit.h(q)

    # X on all qubits
    for q in qubits:
        circuit.x(q)

    # Multi-controlled Z
    if n == 1:
        circuit.z(qubits[0])
    else:
        if ancilla is None:
            ancilla = max(qubits) + 1
        _apply_mcz(circuit, qubits, ancilla)

    # X on all qubits (undo)
    for q in qubits:
        circuit.x(q)

    # H on all qubits (undo)
    for q in qubits:
        circuit.h(q)
