"""Pauli string expectation value measurement via basis rotation."""

__all__ = ["pauli_expectation"]

from typing import Optional

import numpy as np

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator


def _parity(bitstring: str, pauli_string: str) -> int:
    """Compute parity contribution of a measurement outcome for a Pauli string.

    For each qubit i:
      Z → contributes 1 if bit[i] == '1'
      X → contributes 1 if bit[i] == '1' (equivalently, XOR of all X positions)
      Y → contributes 1 if bit[i] == '1'
    The total parity is the XOR (sum mod 2) of all contributions.
    Returns 0 for even parity (+1 eigenvalue) or 1 for odd parity (-1 eigenvalue).
    """
    parity = 0
    for i, (pauli, bit) in enumerate(zip(pauli_string, bitstring)):
        if bit == '1':
            if pauli in ('Z', 'z', 'X', 'x', 'Y', 'y'):
                parity ^= 1
    return parity


def _apply_basis_rotation(circuit: Circuit, pauli_string: str) -> Circuit:
    """Add basis-rotation gates to a circuit copy for measuring a Pauli string.

    For each qubit i with pauli_string[i]:
      Z → no rotation
      X → H gate
      Y → Sdag then H (equivalently, Sdg-H sequence)
      I → no rotation
    """
    rot_circuit = circuit.copy()
    for i, pauli in enumerate(pauli_string):
        p = pauli.upper()
        if p == 'X':
            rot_circuit.h(i)
        elif p == 'Y':
            rot_circuit.sdag(i)
            rot_circuit.h(i)
        # Z and I: no rotation needed
    return rot_circuit


def _statevector_expectation(circuit: Circuit, pauli_string: str) -> float:
    """Compute the exact ⟨pauli_string⟩ expectation from the statevector.

    Applies basis-rotation gates to rotate to the measurement basis, then
    computes the expectation analytically from the final statevector.
    """
    rot_circuit = _apply_basis_rotation(circuit, pauli_string)
    n = rot_circuit.max_qubit + 1

    # Use QASM simulator in statevector mode
    sim = QASM_Simulator(backend_type='statevector', n_qubits=n)
    qasm = rot_circuit.qasm
    result = sim._simulate_qasm(qasm)

    # result['prob'] is a list of length 2^n, probabilities in computational basis
    probs = np.array(result['prob'])
    exp_val = 0.0
    for idx, p in enumerate(probs):
        # Build bitstring for this index (big-endian: qubit 0 is MSB)
        bitstring = format(idx, f'0{n}b')
        parity = _parity(bitstring, pauli_string.upper())
        if parity == 0:
            exp_val += p
        else:
            exp_val -= p
    return float(exp_val)


def _shots_expectation(circuit: Circuit, pauli_string: str, shots: int) -> float:
    """Estimate ⟨pauli_string⟩ via basis rotation + shots on QASM simulator."""
    rot_circuit = _apply_basis_rotation(circuit, pauli_string)
    n = rot_circuit.max_qubit + 1

    sim = QASM_Simulator(backend_type='qasm_simulator', n_qubits=n)
    qasm = rot_circuit.qasm
    result = sim._simulate_qasm(qasm, shots=shots)

    # result['int_result'] → dict mapping bitstring -> count
    counts = result['int_result']
    total = sum(counts.values())

    exp_val = 0.0
    for bitstring, count in counts.items():
        # Pad bitstring to n qubits (in case leading zeros are omitted)
        bitstring = bitstring.zfill(n)
        parity = _parity(bitstring, pauli_string.upper())
        p = count / total
        if parity == 0:
            exp_val += p
        else:
            exp_val -= p
    return float(exp_val)


def pauli_expectation(
    circuit: Circuit,
    pauli_string: str,
    shots: Optional[int] = None,
) -> float:
    """Measure the expectation value of a Pauli string on a circuit.

    For each qubit i, the measurement basis is determined by ``pauli_string[i]``:

    - ``'I'``: trace out (identity, contributes trivially)
    - ``'Z'``: measure in the computational (Z) basis — no rotation needed
    - ``'X'``: apply Hadamard before Z measurement
    - ``'Y'``: apply Sdag then Hadamard before Z measurement

    When ``shots`` is ``None``, the statevector simulator is used to compute
    the exact expectation analytically.  When ``shots`` is given, the circuit
    is simulated ``shots`` times and the empirical frequency is used.

    Args:
        circuit: Quantum circuit. Must contain only gates supported by
            ``QASM_Simulator`` and end with measurement instructions.
        pauli_string: Case-insensitive Pauli string (e.g. ``"XYZ"``, ``"IZI"``).
            Characters must be ``I``, ``X``, ``Y``, or ``Z``.
        shots: Number of measurement shots. ``None`` uses statevector mode
            for the exact analytical value.

    Returns:
        Expectation value ⟨psi|P|psi⟩ as a float in the interval ``[-1, 1]``.

    Raises:
        ValueError: ``pauli_string`` contains invalid characters or its length
            does not match the number of qubits in ``circuit``.
        ValueError: ``shots`` is not a positive integer.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.measurement import pauli_expectation
        >>> c = Circuit()
        >>> c.h(0)
        >>> c.cx(0, 1)          # Bell state (|00⟩+|11⟩)/√2
        >>> c.measure(0, 1)
        >>> pauli_expectation(c, "ZZ", shots=None)   # exact: 1.0
        1.0
        >>> abs(pauli_expectation(c, "ZZ", shots=10000) - 1.0) < 0.1
        True
    """
    # Validate pauli_string
    pauli_upper = pauli_string.upper()
    n_qubits = circuit.max_qubit + 1

    if len(pauli_upper) != n_qubits:
        raise ValueError(
            f"pauli_string length ({len(pauli_string)}) must match "
            f"circuit n_qubits ({n_qubits})"
        )

    for ch in pauli_upper:
        if ch not in ('I', 'X', 'Y', 'Z'):
            raise ValueError(
                f"pauli_string must contain only I/X/Y/Z, got: {pauli_string!r}"
            )

    if shots is not None:
        if not isinstance(shots, int) or shots <= 0:
            raise ValueError(f"shots must be a positive integer, got: {shots}")
        return _shots_expectation(circuit, pauli_string, shots)

    return _statevector_expectation(circuit, pauli_string)
