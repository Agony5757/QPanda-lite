"""Deutsch-Jozsa algorithm circuit and oracle builder."""

__all__ = ["deutsch_jozsa_circuit", "deutsch_jozsa_oracle"]

from typing import List, Optional

from qpandalite.circuit_builder import Circuit


def deutsch_jozsa_oracle(
    n_qubits: int,
    balanced: bool = True,
    target_bits: Optional[List[int]] = None,
) -> Circuit:
    r"""Build a Deutsch-Jozsa oracle circuit.

    Generates either a **constant** oracle (maps all inputs to 0 or all to 1)
    or a **balanced** oracle (maps half the inputs to 0 and half to 1).

    * **Constant oracle**: does nothing (output = 0) or flips the ancilla
      (output = 1).  Here we implement the identity (output always 0).

    * **Balanced oracle**: applies CNOT from each *target_bit* to the
      ancilla.  If ``target_bits`` is ``None``, all data qubits are used.
      This yields a balanced function because the ancilla flips exactly
      when an odd number of target bits are set.

    The oracle acts on ``n_qubits + 1`` qubits: qubits ``[0, n_qubits-1]``
    are data qubits and qubit ``n_qubits`` is the ancilla.

    Args:
        n_qubits: Number of data qubits.
        balanced: If ``True``, build a balanced oracle; otherwise constant.
        target_bits: Data-qubit indices that control the ancilla flip.
            Only used when *balanced* is ``True``.  ``None`` means
            ``list(range(n_qubits))``.

    Returns:
        A new :class:`Circuit` containing the oracle gates.

    Raises:
        ValueError: *n_qubits* < 1, or *target_bits* contains invalid indices.

    Example:
        >>> oracle = deutsch_jozsa_oracle(3, balanced=True)
        >>> oracle.qubit_num  # 3 data + 1 ancilla
        4
    """
    if n_qubits < 1:
        raise ValueError(f"n_qubits must be >= 1, got {n_qubits}")

    oracle = Circuit()

    if not balanced:
        # Constant oracle: output is always 0 → identity on ancilla
        return oracle

    if target_bits is None:
        target_bits = list(range(n_qubits))

    for idx in target_bits:
        if idx < 0 or idx >= n_qubits:
            raise ValueError(
                f"target_bit {idx} out of range for {n_qubits} data qubits"
            )
        oracle.cnot(idx, n_qubits)

    return oracle


def deutsch_jozsa_circuit(
    circuit: Circuit,
    oracle: Circuit,
    qubits: Optional[List[int]] = None,
    ancilla: Optional[int] = None,
) -> None:
    r"""Apply the Deutsch-Jozsa algorithm to the circuit.

    The Deutsch-Jozsa algorithm determines whether a function
    :math:`f: \{0,1\}^n \to \{0,1\}` is **constant** or **balanced**
    using a single quantum query.

    Circuit steps:

    1. Initialise data qubits to :math:`|+\rangle` and ancilla to
       :math:`|-\rangle` (via ``X`` then ``H``).
    2. Apply the oracle.
    3. Apply Hadamard on all data qubits.
    4. Measure data qubits: all-zeros → constant, otherwise → balanced.

    The caller is responsible for allocating enough qubits:
    ``len(qubits) + 1`` (one ancilla).

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        oracle: Oracle sub-circuit to embed.  Must operate on
            ``len(qubits) + 1`` qubits (data + ancilla).
        qubits: Data-qubit indices.  ``None`` means
            ``list(range(n_data))`` where *n_data* = ``oracle.qubit_num - 1``.
        ancilla: Ancilla qubit index.  ``None`` means the last qubit
            (``oracle.qubit_num - 1``).

    Raises:
        ValueError: Qubit count mismatch between circuit and oracle.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import (
        ...     deutsch_jozsa_circuit, deutsch_jozsa_oracle,
        ... )
        >>> n = 3
        >>> oracle = deutsch_jozsa_oracle(n, balanced=True)
        >>> c = Circuit(n + 1)
        >>> deutsch_jozsa_circuit(c, oracle)
    """
    n_data = oracle.qubit_num - 1

    if qubits is None:
        qubits = list(range(n_data))
    if ancilla is None:
        ancilla = n_data

    if len(qubits) != n_data:
        raise ValueError(
            f"Expected {n_data} data qubits, got {len(qubits)}"
        )

    # Step 1: |+⟩ on data qubits, |−⟩ on ancilla
    for q in qubits:
        circuit.h(q)
    circuit.x(ancilla)
    circuit.h(ancilla)

    # Step 2: Apply oracle
    for op in oracle.opcode_list:
        circuit.add_gate(*op)

    # Step 3: H on data qubits
    for q in qubits:
        circuit.h(q)

    # Step 4: Measure data qubits
    circuit.measure(*qubits)
