"""Deutsch-Jozsa algorithm circuit and oracle builder."""

__all__ = ["deutsch_jozsa_circuit", "deutsch_jozsa_oracle"]

from typing import List, Optional

from qpandalite.circuit_builder import Circuit


def deutsch_jozsa_oracle(
    qubits: List[int],
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

    The oracle acts on the data qubits in *qubits* plus one ancilla qubit
    at ``max(qubits) + 1``.

    Args:
        qubits: Data-qubit indices (explicit list, no default).
        balanced: If ``True``, build a balanced oracle; otherwise constant.
        target_bits: Data-qubit indices (positions within *qubits*) that
            control the ancilla flip.  Only used when *balanced* is ``True``.
            ``None`` means all data qubits.

    Returns:
        A new :class:`Circuit` containing the oracle gates.

    Raises:
        TypeError: *qubits* is not a list.
        ValueError: *qubits* is empty, or *target_bits* contains invalid indices.

    Example:
        >>> oracle = deutsch_jozsa_oracle(qubits=[0, 1, 2], balanced=True)
        >>> oracle.qubit_num  # 3 data + 1 ancilla
        4
    """
    if not isinstance(qubits, list):
        raise TypeError("qubits must be a list of qubit indices")
    if len(qubits) < 1:
        raise ValueError("qubits must contain at least 1 data qubit")

    n_qubits = len(qubits)
    ancilla = max(qubits) + 1

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
        oracle.cnot(qubits[idx], ancilla)

    return oracle


def deutsch_jozsa_circuit(
    circuit: Circuit,
    oracle: Circuit,
    qubits: List[int],
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

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        oracle: Oracle sub-circuit to embed.  Must operate on
            ``len(qubits) + 1`` qubits (data + ancilla), or be empty
            (constant-zero oracle).
        qubits: Data-qubit indices (explicit list, no default).
        ancilla: Ancilla qubit index.  ``None`` means ``max(qubits) + 1``.

    Raises:
        TypeError: *qubits* is not a list.
        ValueError: *qubits* is empty, or oracle qubit count mismatches.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import (
        ...     deutsch_jozsa_circuit, deutsch_jozsa_oracle,
        ... )
        >>> n = 3
        >>> oracle = deutsch_jozsa_oracle(qubits=list(range(n)), balanced=True)
        >>> c = Circuit()
        >>> deutsch_jozsa_circuit(c, oracle, qubits=list(range(n)), ancilla=n)
    """
    if not isinstance(qubits, list):
        raise TypeError("qubits must be a list of qubit indices")
    if len(qubits) < 1:
        raise ValueError("qubits must contain at least 1 data qubit")

    n_data = len(qubits)

    if ancilla is None:
        ancilla = max(qubits) + 1

    # Only validate oracle width when it has gates (empty constant oracle
    # has qubit_num=0 but is still a valid DJ oracle for any n_data).
    if oracle.qubit_num > 0 and oracle.qubit_num != n_data + 1:
        raise ValueError(
            f"Oracle acts on {oracle.qubit_num} qubits, "
            f"expected {n_data + 1} (data + ancilla)"
        )

    # Step 1: |+⟩ on data qubits, |−⟩ on ancilla
    for q in qubits:
        circuit.h(q)
    circuit.x(ancilla)
    circuit.h(ancilla)

    # Step 2: Apply oracle
    circuit.add_circuit(oracle)

    # Step 3: H on data qubits
    for q in qubits:
        circuit.h(q)

    # Step 4: Measure data qubits
    circuit.measure(*qubits)
