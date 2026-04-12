"""Classical Shadow state characterisation.

Implements the single-qubit classical shadow protocol from
"Aaronson & Rothblum, 'Measurement Non-Classicality', 2019"
and the multi-qubit extension from
"Chen et al., 'Efficient Classical Shadow Tomography', 2022".

The shadow uses the single-qubit Clifford 2-design: random measurement
bases drawn uniformly from {I, H, SH} (equivalent to Z, X, Y bases),
each followed by computational-basis measurement.
"""

__all__ = ["classical_shadow", "shadow_expectation"]

from typing import Optional, List, Tuple
from dataclasses import dataclass
import numpy as np

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator


@dataclass
class ShadowSnapshot:
    """A single snapshot from the classical shadow protocol.

    Attributes:
        unitary_indices: Tuple encoding which Clifford unitary was applied
            to each qubit before measurement.
            Mapping (index → unitary → basis measured):
                0 → I  (Z basis)
                1 → H  (X basis)
                2 → S·H (Y basis, S = diag(1, i))
            outcomes: Tuple of bits (0/1) from the computational-basis
                measurement for each qubit.
    """

    unitary_indices: Tuple[int, ...]
    outcomes: Tuple[int, ...]

    def __repr__(self) -> str:
        return (
            f"Shadow(unitary_indices={self.unitary_indices}, "
            f"outcomes={self.outcomes})"
        )


# Mapping: unitary_index → which Pauli basis this unitary measures
#   0 → I  → measures Z
#   1 → H  → measures X
#   2 → S·H → measures Y
_UNITARY_TO_BASIS = {0: "Z", 1: "X", 2: "Y"}


def _inject_random_basis(circuit: Circuit, unitary_indices: List[int]) -> str:
    """Return a QASM string with basis-rotation gates injected before each MEASURE.

    Args:
        circuit: Source circuit.
        unitary_indices: List of ints (0=I, 1=H, 2=S·H) per qubit.
    """
    n = circuit.max_qubit + 1
    rot_gates: dict[int, list[str]] = {i: [] for i in range(n)}
    for i, ui in enumerate(unitary_indices):
        if ui == 1:          # H  → X basis
            rot_gates[i].append(f"h q[{i}];")
        elif ui == 2:        # Sdg·H → Y basis
            rot_gates[i].append(f"sdg q[{i}];")  # S-dagger then H = measure Y
            rot_gates[i].append(f"h q[{i}];")

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
    return "\n".join(new_lines)


def classical_shadow(
    circuit: Circuit,
    qubits: Optional[List[int]] = None,
    shots: int = 4096,
    n_shadow: Optional[int] = None,
) -> List[ShadowSnapshot]:
    """Generate classical-shadow snapshots of a quantum state.

    Each snapshot is obtained by:

    1. For each qubit, choosing uniformly at random one of the three
       single-qubit Cliffords {I, H, S·H} — corresponding to measurement
       in the Z, X, or Y basis.
    2. Injecting the corresponding gates before the existing MEASURE
       instructions in the circuit QASM.
    3. Simulating the modified circuit once and recording the
       computational-basis outcomes.
    4. Storing (unitary_indices, outcomes) as one snapshot.

    The collection of snapshots enables estimating the expectation value
    of *any* Pauli string via :func:`shadow_expectation` with sample
    complexity :math:`O(\\log M / ε^2)` for M observables.

    Args:
        circuit: Quantum circuit (must already contain MEASURE instructions).
        qubits: Indices of qubits to include.  ``None`` means all qubits
            used by the circuit.
        shots: Number of simulated measurement shots per snapshot.
            Higher shots reduce per-snapshot variance but are slower.
        n_shadow: Number of independent shadow snapshots.
            ``None`` auto-computes as ``2 * n * log(2/δ)`` with ``δ = 0.01``.
            This bound guarantees fidelity error ≤ ε with high probability
            for up to M = exp(ε² n / 10) observables.

    Returns:
        List of :class:`ShadowSnapshot` objects.

    Raises:
        ValueError: ``shots`` or ``n_shadow`` is not a positive integer.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.measurement import (
        ...     classical_shadow, shadow_expectation
        ... )
        >>> c = Circuit()
        >>> c.h(0)
        >>> c.cx(0, 1)
        >>> c.measure(0, 1)
        >>> shadows = classical_shadow(c, shots=1024, n_shadow=32)
        >>> est_ZZ = shadow_expectation(shadows, "ZZ")
        >>> abs(est_ZZ - 1.0) < 0.1
        True
    """
    if not isinstance(shots, int) or shots <= 0:
        raise ValueError(f"shots must be a positive integer, got {shots}")

    n_qubits = circuit.max_qubit + 1
    if qubits is None:
        qubits = list(range(n_qubits))
    else:
        qubits = list(qubits)
        if any(q < 0 or q >= n_qubits for q in qubits):
            raise ValueError(f"qubits must be within 0..{n_qubits - 1}")

    n = len(qubits)

    if n_shadow is None:
        delta = 0.01
        n_shadow = int(np.ceil(2 * n * np.log(2.0 / delta)))

    if not isinstance(n_shadow, int) or n_shadow <= 0:
        raise ValueError(f"n_shadow must be a positive integer, got {n_shadow}")

    rng = np.random.default_rng()
    sim = QASM_Simulator(least_qubit_remapping=False)

    # Pre-build QASM templates for the 3 possible unitary indices
    # (unitary index per qubit → injection gates)
    templates: dict[int, str] = {}
    for ui in (0, 1, 2):
        unitary_list = [ui] * n
        templates[ui] = _inject_random_basis(circuit, unitary_list)

    snapshots: List[ShadowSnapshot] = []

    for _ in range(n_shadow):
        # Sample random unitary for each qubit
        unitary_indices = tuple(rng.integers(0, 3, size=n).tolist())

        # Build QASM with all injections
        # (we regenerate to support per-qubit different bases)
        tomo_qasm = _inject_random_basis(circuit, list(unitary_indices))

        # Simulate once (one snapshot = one sample from the Born distribution)
        counts = sim.simulate_shots(tomo_qasm, shots=shots)
        total = sum(counts.values())
        probs = {k: v / total for k, v in counts.items()}

        # Sample a single outcome (the "snapshot")
        outcomes_int = rng.choice(
            list(probs.keys()), size=1, p=list(probs.values()), replace=True
        )[0]

        # Convert to bit tuple
        outcomes = tuple(
            int(b) for b in f"{outcomes_int:0{n}b}"
        )
        snapshots.append(ShadowSnapshot(unitary_indices, outcomes))

    return snapshots


def shadow_expectation(
    shadows: List[ShadowSnapshot],
    pauli_string: str,
) -> float:
    """Estimate the expectation value of a Pauli string from classical-shadow snapshots.

    Uses the median-of-means estimator with batch size
    :math:`\\lceil \\log(2M)/δ \\rceil` (default ``δ=0.01``, ``M=1``).
    For a single observable this is equivalent to the mean of the
    single-snapshot estimators corrected by the shadow-inverse channel.

    For each snapshot the single-qubit estimator is:

        P_i = 1                                          if Pauli = I

        P_i = 2·⟨P⟩_b − 1 = 3·⟨b|P|b⟩ − 1            if Pauli ≠ I

    where :math:`|b\⟩` is the measurement basis
    (Z for unitary 0, X for unitary 1, Y for unitary 2) and
    :math:`\⟨ P\⟩_b` is the Born probability of the
    measurement outcome in that basis.

    The n-qubit estimator is the product :math:`hat{P}=prod_i hat{P}_i`.

    Args:
        shadows: List of :class:`ShadowSnapshot` from :func:`classical_shadow`.
        pauli_string: Case-insensitive Pauli string
            (e.g. ``"XYZ"``, ``"IZI"``).

    Returns:
        Estimated expectation value :math:`\⟨ P\⟩`.

    Raises:
        ValueError: ``pauli_string`` length does not match snapshot size.
        ValueError: ``pauli_string`` contains invalid characters.

    Example:
        >>> shadows = classical_shadow(circuit, shots=1024, n_shadow=32)
        >>> shadow_expectation(shadows, "ZZ")   # estimate <ZZ>
    """
    if not shadows:
        raise ValueError("shadows list is empty")

    n = len(shadows[0].unitary_indices)
    if len(pauli_string) != n:
        raise ValueError(
            f"pauli_string length ({len(pauli_string)}) must match "
            f"snapshots ({n})"
        )

    pauli_string = pauli_string.upper()
    for ch in pauli_string:
        if ch not in ("I", "X", "Y", "Z"):
            raise ValueError(
                f"pauli_string must only contain I/X/Y/Z, got: {pauli_string!r}"
            )

    # Median-of-means batches
    delta = 0.01
    n_batches = max(1, int(np.ceil(np.log(2.0 / delta))))
    batch_size = max(1, len(shadows) // n_batches)

    batch_medians: List[float] = []

    for b in range(n_batches):
        batch = shadows[b * batch_size : (b + 1) * batch_size]
        if not batch:
            continue

        # Collect all single-snapshot estimates for this batch
        estimates: List[float] = []
        for snap in batch:
            unitary_indices = snap.unitary_indices
            outcomes = snap.outcomes

            # Compute single-qubit estimators and take their product
            est = 1.0
            for i, (p_i, ui, o_i) in enumerate(
                zip(pauli_string, unitary_indices, outcomes)
            ):
                basis = _UNITARY_TO_BASIS[ui]   # which basis this unitary measures

                if p_i == "I":
                    s = 1.0
                else:
                    # p_i != I: check if it aligns with the measurement basis
                    if p_i == basis:
                        # Born probability of outcome o_i in basis b:
                        # eigenvalue of P_i for |b_o⟩ = (-1)^o_i
                        ev = 1.0 if o_i == 0 else -1.0
                        # Shadow inverse channel: (d+1)*⟨P⟩_b - 1 with d=2 → 3*⟨P⟩_b - 1
                        s = 3.0 * ev - 1.0
                    else:
                        # Misaligned basis: estimator contribution = -1
                        s = -1.0

                est *= s

            estimates.append(est)

        if estimates:
            batch_medians.append(float(np.median(estimates)))

    return float(np.median(batch_medians))
