"""Basis-rotation measurement for arbitrary single-qubit measurement bases."""

__all__ = ["basis_rotation_measurement"]

from typing import Optional, List, Union, Dict
import numpy as np

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator


def basis_rotation_measurement(
    circuit: Circuit,
    qubits: Optional[List[int]] = None,
    basis: Optional[Union[str, List[str]]] = None,
    shots: Optional[int] = None,
) -> Union[Dict[str, float], List[float]]:
    """Measure a circuit by applying basis-rotation gates and then
    measuring in the computational (Z) basis.

    For each qubit, the rotation applied before measurement is determined
    by the corresponding entry in ``basis``:

    **``"Z"``**: no rotation (Z basis, default)

    **``"X"``**: Hadamard gate (H) → measures X basis

    **``"Y"``**: ``S^dagger H`` → measures Y basis

    **``"I"``**: no rotation (Z basis, identity)

    When ``shots`` is ``None``, the statevector simulator is used to return
    the exact probability distribution.  When ``shots`` is given, the
    distribution is estimated from that many samples.

    Args:
        circuit: Quantum circuit (must contain MEASURE instructions).
        qubits: Indices of qubits to include.  ``None`` means all qubits.
        basis: Per-qubit measurement basis.  Can be:

            - A single string such as ``"XYZ"`` (applied left-to-right to
              ``qubits``), where each character is ``"I"``, ``"X"``, ``"Y"``,
              or ``"Z"``.
            - A list of strings such as ``["X", "Y", "Z"]``.
            - ``None`` (default), which means all qubits use the Z basis.

        shots: Number of measurement shots.  ``None`` returns the exact
            probability vector from the statevector simulator.

    Returns:
        - If ``shots`` is ``None``: a ``dict`` mapping each computational-basis
          outcome string (e.g. ``"01"``) to its probability.
        - If ``shots`` is given: a ``dict`` mapping outcome strings to
          integer counts (frequency).

    Raises:
        ValueError: ``len(basis)`` does not match ``len(qubits)``.
        ValueError: ``shots`` is not a positive integer.
        ValueError: ``basis`` contains invalid characters.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.measurement import basis_rotation_measurement
        >>> c = Circuit()
        >>> c.h(0)           # |0⟩ → (|0⟩+|1⟩)/√2
        >>> c.cx(0, 1)       # Bell state (|00⟩+|11⟩)/√2
        >>> c.measure(0, 1)
        >>> # Measure qubit 0 in X basis, qubit 1 in Z basis
        >>> probs = basis_rotation_measurement(c, basis="XZ")
        >>> abs(probs["00"] - 0.5) < 1e-6   # P(0) in X basis for |+⟩ is 0.5
        True
    """
    n_qubits = circuit.max_qubit + 1

    if qubits is None:
        qubits = list(range(n_qubits))
    else:
        qubits = list(qubits)

    n = len(qubits)

    # Parse basis argument
    if basis is None:
        basis_strs: list[str] = ["Z"] * n
    elif isinstance(basis, str):
        basis_strs = list(basis.upper())
        if len(basis_strs) != n:
            raise ValueError(
                f"basis string length ({len(basis_strs)}) must match "
                f"len(qubits) ({n})"
            )
    elif isinstance(basis, list):
        if len(basis) != n:
            raise ValueError(
                f"len(basis) ({len(basis)}) must match len(qubits) ({n})"
            )
        basis_strs = [b.upper() for b in basis]
    else:
        raise TypeError(f"basis must be str, list, or None, got {type(basis).__name__}")

    for b in basis_strs:
        if b not in ("I", "X", "Y", "Z"):
            raise ValueError(
                f"basis must only contain I/X/Y/Z, got: {b!r}"
            )

    if shots is not None and (not isinstance(shots, int) or shots <= 0):
        raise ValueError(f"shots must be a positive integer, got {shots}")

    # Build rotation gate injection map per qubit index
    rot_gates: dict[int, list[str]] = {i: [] for i in range(n)}
    for i, b in enumerate(basis_strs):
        if b == "X":
            rot_gates[i].append(f"h q[{i}];")
        elif b == "Y":
            # Sdg then H maps Y eigenstates → Z eigenstates
            rot_gates[i].append(f"sdg q[{i}];")
            rot_gates[i].append(f"h q[{i}];")

    # Inject rotations before each MEASURE line
    lines = circuit.qasm.splitlines()
    new_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("measure "):
            left = stripped.split("->")[0].strip()
            qi = int(left.split("[")[1].split("]")[0])
            for gate in rot_gates[qi]:
                new_lines.append(gate)
        new_lines.append(line)

    modified_qasm = "\n".join(new_lines)

    # Simulate
    sim = QASM_Simulator(least_qubit_remapping=False)
    if shots is None:
        probs = sim.simulate_pmeasure(modified_qasm)
        return {f"{i:0{n}b}": float(p) for i, p in enumerate(probs)}
    else:
        counts = sim.simulate_shots(modified_qasm, shots=shots)
        return {f"{k:0{n}b}": v for k, v in counts.items()}
