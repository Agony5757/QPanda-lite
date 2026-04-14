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

from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass, field
import itertools
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

        outcomes: Tuple of bits (0/1) sampled from the computational-basis
            distribution for each qubit. Bits are LSB-first — ``outcomes[i]``
            is qubit ``i``'s measurement.

        counts: Empirical outcome counts for this basis setting (integer
            keys are LSB-first qubit-bit-packed outcomes). Populated from
            all simulated shots; enables probability-scoring / exact-Born
            estimators in :func:`shadow_expectation` with much lower
            variance than the single-outcome HKP estimator.
    """

    unitary_indices: Tuple[int, ...]
    outcomes: Tuple[int, ...]
    counts: Dict[int, int] = field(default_factory=dict)

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

    # Stratified basis sampling: when n_shadow >= 3^n, cycle through every
    # basis combination an equal number of times (remainder drawn without
    # replacement). This keeps the estimator unbiased but zeroes out
    # basis-selection variance when n_shadow is a multiple of 3^n — crucial
    # for 3-qubit tests where random sampling's 3^n variance would dominate.
    n_bases = 3**n
    if n_shadow >= n_bases:
        all_combos = list(itertools.product(range(3), repeat=n))
        full_cycles = n_shadow // n_bases
        remainder = n_shadow % n_bases
        basis_sequence: List[Tuple[int, ...]] = list(all_combos) * full_cycles
        if remainder > 0:
            extra_idx = rng.choice(n_bases, size=remainder, replace=False)
            basis_sequence.extend(all_combos[i] for i in extra_idx)
        rng.shuffle(basis_sequence)
    else:
        basis_sequence = [
            tuple(rng.integers(0, 3, size=n).tolist()) for _ in range(n_shadow)
        ]

    snapshots: List[ShadowSnapshot] = []

    for unitary_indices in basis_sequence:
        unitary_indices = tuple(unitary_indices)

        tomo_qasm = _inject_random_basis(circuit, list(unitary_indices))

        counts = sim.simulate_shots(tomo_qasm, shots=shots)
        total = sum(counts.values())
        probs = {k: v / total for k, v in counts.items()}

        outcomes_int = int(
            rng.choice(
                list(probs.keys()), size=1, p=list(probs.values()), replace=True
            )[0]
        )

        # LSB-first: outcomes[i] = measurement of qubit i
        outcomes = tuple((outcomes_int >> i) & 1 for i in range(n))
        snapshots.append(
            ShadowSnapshot(unitary_indices, outcomes, dict(counts))
        )

    return snapshots


def shadow_expectation(
    shadows: List[ShadowSnapshot],
    pauli_string: str,
) -> float:
    """Estimate the expectation value of a Pauli string from classical-shadow snapshots.

    Computes the mean of single-snapshot HKP estimators. For a single
    observable the mean is optimal; median-of-means buys robustness only
    when estimating many Paulis with uniform tail-bound guarantees.

    For each snapshot the single-qubit estimator is (Huang-Kueng-Preskill,
    single-qubit Clifford shadow inverse channel ``M^{-1}(X) = 3X - I``):

        s_i = 1                   if Pauli_i = I
        s_i = 3 * (-1)^outcome_i  if Pauli_i ≠ I and aligned with measured basis
        s_i = 0                   if Pauli_i ≠ I and misaligned with measured basis

    The n-qubit estimator is the product :math:`\\hat{P}=\\prod_i s_i`.

    Args:
        shadows: List of :class:`ShadowSnapshot` from :func:`classical_shadow`.
        pauli_string: Case-insensitive Pauli string
            (e.g. ``"XYZ"``, ``"IZI"``).

    Returns:
        Estimated expectation value ``\<P>``.

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

    # # of non-identity Paulis: determines the HKP prefactor 3^m
    m = sum(1 for p in pauli_string if p != "I")
    prefactor = 3.0**m

    estimates: List[float] = []
    for snap in shadows:
        # Check alignment: every non-I Pauli must equal the measured basis.
        aligned = all(
            p_i == "I" or _UNITARY_TO_BASIS[ui] == p_i
            for p_i, ui in zip(pauli_string, snap.unitary_indices)
        )
        if not aligned:
            estimates.append(0.0)
            continue

        # Empirical Born expectation of the Pauli over all shots in this
        # basis. Using the full counts distribution (instead of a single
        # sampled outcome) removes per-basis shot noise entirely.
        counts = snap.counts if snap.counts else None
        if counts is None:
            # Backward-compat path: fall back to single stored outcome.
            pauli_eigenvalue = 1
            for i, p_i in enumerate(pauli_string):
                if p_i != "I" and snap.outcomes[i] == 1:
                    pauli_eigenvalue *= -1
            estimates.append(prefactor * pauli_eigenvalue)
            continue

        total = sum(counts.values())
        ev_sum = 0.0
        for outcome_int, count in counts.items():
            pauli_eigenvalue = 1
            for i, p_i in enumerate(pauli_string):
                if p_i == "I":
                    continue
                # LSB-first: bit i of outcome_int is qubit i's measurement
                if (outcome_int >> i) & 1:
                    pauli_eigenvalue = -pauli_eigenvalue
            ev_sum += count * pauli_eigenvalue
        born_ev = ev_sum / total
        estimates.append(prefactor * born_ev)

    return float(np.mean(estimates))
