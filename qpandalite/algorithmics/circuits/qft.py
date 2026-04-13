"""Quantum Fourier Transform (QFT) circuit."""

__all__ = ["qft_circuit"]

from typing import List, Optional
import math

from qpandalite.circuit_builder import Circuit


def qft_circuit(
    circuit: Circuit,
    qubits: Optional[List[int]] = None,
    swaps: bool = True,
) -> None:
    r"""Apply the Quantum Fourier Transform (QFT) to the given qubits.

    The QFT maps the computational basis state :math:`|j\rangle` to:

    .. math::

        \frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i\, jk/N} |k\rangle

    where :math:`N = 2^n` and *n* is the number of qubits.

    The circuit applies, for each qubit *j* (from most-significant to
    least-significant):

    1. A Hadamard gate on qubit *j*.
    2. Controlled phase rotations :math:`R_k` from every later qubit *k* > *j*
       with angle :math:`\pi / 2^{k-j}`.

    If *swaps* is ``True`` (the default), a layer of SWAP gates is appended
    to reverse the qubit order so that the output follows the standard
    big-endian convention.

    To obtain the inverse QFT, use ``circuit.dagger()`` on a copy of the
    QFT sub-circuit, or apply ``qft_circuit`` and then call
    ``circuit.dagger()`` on the relevant gates.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        qubits: Qubit indices to apply QFT on.  ``None`` means all qubits
            of *circuit* (``list(range(circuit.qubit_num))``).
        swaps: Whether to append SWAP gates to reverse qubit order.
            Defaults to ``True``.

    Raises:
        ValueError: Fewer than 1 qubit is specified.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import qft_circuit
        >>> c = Circuit(3)
        >>> qft_circuit(c, qubits=[0, 1, 2])
    """
    if qubits is None:
        qubits = list(range(circuit.qubit_num))

    n = len(qubits)
    if n < 1:
        raise ValueError("qft_circuit requires at least 1 qubit")

    for j in range(n):
        # Hadamard on qubit j
        circuit.h(qubits[j])
        # Controlled phase rotations from qubits k > j
        for k in range(j + 1, n):
            angle = math.pi / (2 ** (k - j))
            # Controlled-Rz using CNOT decomposition:
            # CRz(θ) = Rz(θ/2) on target, CNOT, Rz(-θ/2) on target, CNOT
            # Equivalently, we can use controlled-phase via CNOT + Rz
            circuit.rz(qubits[k], angle / 2)
            circuit.cnot(qubits[j], qubits[k])
            circuit.rz(qubits[k], -angle / 2)
            circuit.cnot(qubits[j], qubits[k])

    if swaps:
        for i in range(n // 2):
            circuit.swap(qubits[i], qubits[n - 1 - i])
