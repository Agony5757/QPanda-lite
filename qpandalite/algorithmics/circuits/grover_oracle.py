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

import warnings
from typing import List, Optional

from qpandalite.circuit_builder import Circuit


def _apply_mcz(
    circuit: Circuit,
    controls: List[int],
    target: int,
) -> None:
    """Apply a multi-controlled Z gate.

    Flips the phase of the computational basis state where every control
    qubit and the target qubit are all in :math:`|1\\rangle`.

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

    # For n>=2, realize MCZ as H·MCX·H on the target.
    circuit.h(target)
    _apply_mcx(circuit, controls, target)
    circuit.h(target)


def _apply_mcx(
    circuit: Circuit,
    controls: List[int],
    target: int,
) -> None:
    """Apply a multi-controlled X gate for any number of controls.

    For n ≤ 3 uses native circuit gates (x / cnot / toffoli / c3x).
    For n ≥ 4 uses a clean-ancilla Toffoli ladder: ``n - 2`` workspace qubits
    are allocated automatically above the highest qubit index currently in the
    circuit.  They are initialised to |0⟩ (circuit convention) and restored to
    |0⟩ after the gate.

    Args:
        circuit: Circuit to append gates to (mutated in-place).
        controls: Ordered list of control qubit indices.
        target: Target qubit index.
    """
    n = len(controls)
    if n == 0:
        circuit.x(target)
        return
    if n == 1:
        circuit.cnot(controls[0], target)
        return
    if n == 2:
        circuit.toffoli(controls[0], controls[1], target)
        return
    if n == 3:
        circuit.add_gate("X", target, control_qubits=list(controls))
        return

    # n >= 4: clean-ancilla Toffoli ladder.
    # Workspace qubits are placed just above the highest index in use so they
    # are always freshly |0⟩ and do not collide with data / ancilla qubits.
    n_workspace = n - 2
    workspace_start = max(list(controls) + [target]) + 1
    workspace = list(range(workspace_start, workspace_start + n_workspace))

    # Declare workspace qubits in the circuit (idempotent if already registered).
    for q in workspace:
        circuit.record_qubit(q)

    # Forward ladder: compute AND(controls[0..n-3]) into workspace.
    circuit.toffoli(controls[0], controls[1], workspace[0])
    for i in range(1, n_workspace):
        circuit.toffoli(controls[i + 1], workspace[i - 1], workspace[i])
    # Apply MCX to target.
    circuit.toffoli(controls[-1], workspace[-1], target)
    # Uncompute workspace.
    for i in range(n_workspace - 1, 0, -1):
        circuit.toffoli(controls[i + 1], workspace[i - 1], workspace[i])
    circuit.toffoli(controls[0], controls[1], workspace[0])


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

    # Bit pattern of marked_state (LSB-first: marked_bits[i] == bit i of marked_state)
    marked_bits = [(marked_state >> i) & 1 for i in range(n)]

    # Flip qubits that should be |0⟩ in the marked state
    for i, bit in enumerate(marked_bits):
        if bit == 0:
            circuit.x(qubits[i])

    # Phase kickback via ancilla |−⟩ requires MCX, not MCZ.
    _apply_mcx(circuit, qubits, ancilla)

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
        ancilla: **Deprecated and unused.**  The current implementation derives
            the MCZ target directly from ``qubits[-1]``, so this argument has
            no effect regardless of its value.  It is retained for API
            compatibility only and will be removed in a future release.

    Raises:
        ValueError: Fewer than 1 qubit specified.
    """
    if ancilla is not None:
        warnings.warn(
            "The 'ancilla' argument of grover_diffusion() is unused and will be "
            "removed in a future release.  Remove it from your call site.",
            DeprecationWarning,
            stacklevel=2,
        )
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

    # Multi-controlled Z on data qubits
    if n == 1:
        circuit.z(qubits[0])
    else:
        # Keep ancilla parameter for API compatibility; current decomposition
        # uses data qubits directly (target = last data qubit).
        _apply_mcz(circuit, qubits[:-1], qubits[-1])

    # X on all qubits (undo)
    for q in qubits:
        circuit.x(q)

    # H on all qubits (undo)
    for q in qubits:
        circuit.h(q)
