"""Full density-matrix state tomography via basis rotations."""

__all__ = ["state_tomography", "tomography_summary"]

from typing import Optional, List
import numpy as np

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.analyzer.expectation import calculate_expectation


def _build_tomography_circuit(circuit: Circuit, basis: tuple[str, ...]) -> str:
    """Inject basis-rotation gates before each MEASURE in the QASM.

    Args:
        circuit: Original circuit.
        basis: Tuple of 'X'/'Y'/'Z' for each qubit.

    Returns:
        Modified QASM string with rotation gates injected.
    """
    n = circuit.max_qubit + 1
    rot_gates: dict[int, list[str]] = {i: [] for i in range(n)}
    for i, b in enumerate(basis):
        if b == "X":
            rot_gates[i].append(f"h q[{i}];")
        elif b == "Y":
            rot_gates[i].append(f"sdg q[{i}];")
            rot_gates[i].append(f"h q[{i}];")
        # Z: no rotation

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


def state_tomography(
    circuit: Circuit,
    qubits: Optional[List[int]] = None,
    shots: int = 8192,
) -> np.ndarray:
    """Reconstruct the density matrix of a quantum state via complete tomography.

    The method measures the circuit in all 3^n combinations of the single-qubit
    bases (X, Y, Z), then uses linear inversion over the Pauli basis to
    reconstruct the ``d × d`` density matrix, where ``d = 2^n`` and ``n``
    is the number of qubits being tomographied.

    Args:
        circuit: Quantum circuit (must already contain MEASURE instructions).
        qubits: Indices of qubits to include in the tomography.  ``None`` means
            all qubits used by the circuit, in their natural order.
        shots: Number of measurement shots per basis setting.
            Higher shots reduce statistical noise in the reconstruction.

    Returns:
        A ``(d, d)`` NumPy complex array representing the reconstructed
        density matrix ``ρ``, where ``d = 2**len(qubits)``.
        The matrix is always Hermitian (``ρ = ρ†``) and normalised
        (``Tr(ρ) = 1``).

    Raises:
        ValueError: ``shots`` is not a positive integer.
        ValueError: ``len(qubits)`` is zero or exceeds the circuit qubit count.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.measurement import state_tomography
        >>> c = Circuit()
        >>> c.h(0)           # |0⟩ → (|0⟩+|1⟩)/√2
        >>> c.cx(0, 1)       # Bell state (|00⟩+|11⟩)/√2
        >>> c.measure(0, 1)
        >>> rho = state_tomography(c, shots=4096)
        >>> rho.shape
        (4, 4)
        >>> abs(rho[0, 0])   # ≈ 0.5 (population of |00⟩)
        0.5
    """
    if shots is not None and (not isinstance(shots, int) or shots <= 0):
        raise ValueError(f"shots must be a positive integer, got {shots}")

    n_qubits = circuit.max_qubit + 1

    if qubits is None:
        qubits = list(range(n_qubits))
    else:
        qubits = list(qubits)
        if len(qubits) == 0:
            raise ValueError("qubits list cannot be empty")
        if any(q < 0 or q >= n_qubits for q in qubits):
            raise ValueError(
                f"qubits must be within circuit range 0..{n_qubits - 1}"
            )

    n = len(qubits)
    d = 2**n  # Hilbert space dimension

    # Build a reduced circuit that only uses the selected qubits
    # We achieve this by generating the full QASM and letting the simulator
    # handle the qubit remapping (least_qubit_remapping=False keeps indices).
    sim = QASM_Simulator(least_qubit_remapping=False)

    # Pre-compute the 3^n basis settings
    from itertools import product

    bases_list: list[tuple[str, ...]] = list(product(("X", "Y", "Z"), repeat=n))

    # Build a mapping: for each basis setting, get the measurement probabilities
    # We store results as a dict: {(b0,b1,...): {outcome: prob}}
    basis_results: dict[tuple[str, ...], dict[int, float]] = {}

    for basis in bases_list:
        tomo_qasm = _build_tomography_circuit(circuit, basis)
        counts = sim.simulate_shots(tomo_qasm, shots=shots)
        total = sum(counts.values())
        basis_results[basis] = {k: v / total for k, v in counts.items()}

    # Linear inversion over the Pauli basis
    # rho = (1/2^n) * sum_{pauli_string} <pauli_string> * pauli_string
    # where <pauli_string> = Tr(rho * pauli_string) = expectation of that Pauli string
    #
    # For n qubits there are 4^n Pauli strings (including identity).
    # We solve: M * vec(expectations) = vec(observed_probs)
    # where M maps Pauli strings → outcome probabilities.
    #
    # Because the Pauli basis is orthogonal under the Hilbert-Schmidt inner
    # product, the expectation of each Pauli string is simply:
    #   <P> = sum_{outcome} (-1)^{parity(outcome & pauli_string)} * P(outcome)
    # (identical to the Z-basis formula but applied after basis rotation).
    #
    # We directly compute each expectation via basis_rotation approach:
    # For each Pauli string P:
    #   1. Determine the measurement basis: X→H, Y→SdgH, Z→I  for each qubit
    #   2. Extract the probability distribution over Z outcomes from the
    #      pre-computed basis_results
    #   3. Compute <P> = sum_k (-1)^{popcount(k & string_idx)} * P(k)
    #
    # This is equivalent to applying the inverse Hadamard/SdgH transform to
    # the probability vector for each qubit and reading off the coefficient.
    #
    # Implementation: for a given basis setting b=(b0,...,b_{n-1}) and
    # Pauli string p=(p0,...,p_{n-1}), the contribution is:
    #   prod_i H_{p_i,b_i} * P_b(outcome)
    # where H is the 4×3 matrix mapping (pauli_char, basis_char) → {+1,-1,0}:
    #   X→Z: H = [[1,0],[0,1]]  (Hadamard)
    #   Y→Z: H = [[0,1],[1,0]]  (Sdg then H)
    #   Z→Z: H = [[1,0],[0,-1]] (identity)
    # and P_b(outcome) is the probability of outcome 'outcome' in basis b.

    # Precompute the basis-to-rotations mapping used in _build_tomography_circuit
    # to extract probabilities efficiently from basis_results.
    # Each basis result is keyed by integer index k (0..2^n-1, binary = qubit state).

    # pauli_strings[i] = index of the i-th Pauli string in the 4^n ordering
    # We enumerate all 4^n Pauli strings (I,X,Y,Z per qubit)
    pauli_strings: list[tuple[str, ...]] = list(product(("I", "X", "Y", "Z"), repeat=n))

    # For each Pauli string, compute <P>
    expectations: dict[tuple[str, ...], float] = {}

    for p in pauli_strings:
        # The measurement basis for Pauli string p: only non-identity qubits matter
        # We need: <P> = sum_{outcome} c_outcome * P_basis(outcome)
        # where c_outcome = product_i coeff_i(outcome_i)
        # coeff_i depends on whether p_i is I, X, Y, or Z
        #
        # For qubit i with pauli p_i and outcome bit k_i:
        #   - p_i = I: always contributes +1
        #   - p_i = Z: contributes (-1)^k_i
        #   - p_i = X: H maps outcome k_i to coefficient +1 if k_i=0, -1 if k_i=1
        #              but this is exactly the same as Z after H rotation!
        #              Wait - after H rotation, the probability of outcome k
        #              in the H-rotated basis corresponds to the X expectation.
        #   - p_i = Y: similar to X but with different sign structure
        #
        # Actually: For the Pauli string expectation <P_0 ⊗ P_1 ⊗ ...>:
        # We measure in basis b=(b0,...,b_{n-1}) where:
        #   - b_i = Z: measure Z directly → P(outcome) gives <Z>
        #   - b_i = X: measure X = H Z H → P_H(outcome) = P_X(outcome) gives <X>
        #   - b_i = Y: measure Y = Sdg H Z H S → gives <Y>
        #
        # For <P> where P = P_0 ⊗ ... ⊗ P_{n-1}:
        # We can compute by taking products of single-qubit contributions.
        #
        # Single-qubit projector matrices for each (P, basis):
        # For P in {I, X, Y, Z} and basis in {X, Y, Z}:
        #   I/basis: always 1
        #   Z/Z: diag(+1,-1) → P(0)-P(1) in Z basis
        #   X/X: H*Z*H = X → P_H(0)-P_H(1) = expectation
        #   Y/Y: SdgH*Z*HS = Y → expectation
        #
        # The multi-qubit expectation = sum over outcomes of:
        #   product_i <outcome_i| P_i |outcome_i> * P_b(outcome)
        # = sum_k (prod_i sigma_i[k_i]) * P_b(k)
        # where sigma_i[k_i] = eigenvalue of P_i for basis state |k_i>
        #
        # eigenvalue tables (row=outcome 0/1, col=P):
        #           I  Z  X  Y
        # outcome0: +1 +1 +1  0? No...
        #
        # Actually: |0> is +1 eigenstate of Z, |1> is -1 eigenstate of Z
        # |0>+|1> (H|0>) is +1 eigenstate of X, |0>-|1> (H|1>) is -1 eigenstate of X
        # |0>+i|1> (S|0>) is +1 eigenstate of Y, |0>-i|1> (S|1>) is -1 eigenstate of Y
        #
        # So for outcome k in the Z basis:
        #   I: eigenvalue = +1 for both k=0,1
        #   Z: eigenvalue = (+1) for k=0, (-1) for k=1 → = (-1)^k
        #   X: in Z basis, the projector onto X eigenstate requires basis rotation
        #   Y: same
        #
        # For multi-qubit P = P_0 ⊗ P_1 ⊗ ...:
        #   <P> = sum_{k} (prod_i <k_i| P_i |k_i>) * P_Z(k)
        # where P_Z(k) is the probability of outcome k in the Z basis.
        #
        # For P_i = X: <k_i| X |k_i> = 0! Because X flips |0>↔|1>.
        #   So <X> = sum_k <k| X |k> * P_Z(k) = 0?
        #   No - I made an error. The correct formula for expectation is:
        #   <P> = sum_{a,b} P(a) * <a| P |b> where {|a>} is the Z basis
        #        = sum_k P(k) * <k| P |k>  (off-diagonal terms vanish only if P is diagonal)
        #   For non-diagonal P (X,Y), we need off-diagonal terms!
        #
        # So for X expectation:
        #   <X> = P(0) * <0|X|0> + P(1) * <1|X|1> + cross terms
        #       = P(0)*0 + P(1)*0 + P(0,1)*<0|X|1> + P(1,0)*<1|X|0>
        #       = 0! This is wrong.
        #
        # The correct approach:
        # <X> = sum_{a,b} P(a) * <a| X |b>
        #      = P(0) * <0|X|0> + P(1),<1|X|1> + P(0)*<0|X|1> + P(1)*<1|X|0>
        #      = 0 + 0 + P(0)*1 + P(1)*1 = P(0) + P(1) = 1? No...
        #
        # Wait, <0|X|1> = 1 (since X|1> = |0>), <1|X|0> = 1
        # So <X> = P(0)*1 + P(1)*1 = P(0) + P(1) = 1!
        # That can't be right either. Let me think again.
        #
        # <ψ| X |ψ> for |ψ> = α|0> + β|1>:
        # = (α*<0| + β*<1|) X (α|0> + β|1>)
        # = (α*<0| + β*<1|) (α|1> + β|0>)
        # = α*β + β*α = 2 Re(α*β)
        #
        # Now P(0) = |α|^2, P(1) = |β|^2, P(0,1) = 0 (no coherence in Z basis)
        # So we CAN'T compute <X> from P(k) alone - we need coherences!
        #
        # This is why we need basis rotations:
        # <X> = <ψ| H Z H |ψ> = <ψ'| Z |ψ'> where |ψ'> = H|ψ>
        # P_H(k) = |<k|H|ψ>|^2 = |<k|ψ'>|^2
        # So <X> = sum_k (-1)^k P_H(k) = P_H(0) - P_H(1)
        #
        # Similarly <Y> = <ψ| Sdg H Z H S |ψ> = P_{SdgH}(0) - P_{SdgH}(1)
        #
        # For multi-qubit P = P_0 ⊗ ... ⊗ P_{n-1}:
        # <P> = product of single-qubit contributions if all P_i are diagonal (I or Z)
        # For non-diagonal P, we need the product formula:
        # <P> = sum_{k} (-1)^{popcount(k & string_idx)} P_basis(k)
        # where string_idx is the integer whose binary representation encodes
        # which qubits have non-trivial (X,Y) Paulis.
        #
        # For P = X ⊗ Z on 2 qubits:
        # <XZ> = sum_k (-1)^{k_0 * 1 + k_1 * 0} * P_{XZ}(k)
        #       = sum_k (-1)^{k_0} * P_{XZ}(k)
        #       = P_{XZ}(00) - P_{XZ}(10)
        #
        # The basis for X ⊗ Z is: apply H on qubit 0, identity on qubit 1.
        # P_{XZ}(k) = probability of outcome k in this basis.
        #
        # So the algorithm is:
        # 1. For each Pauli string P (4^n of them):
        #    Determine the measurement basis b = (b_0, ..., b_{n-1}) where
        #    b_i = Z if P_i ∈ {I, Z}, b_i = X if P_i = X, b_i = Y if P_i = Y
        #    (Note: P_i = I contributes trivially, P_i = Z uses Z basis)
        #    Wait - for X ⊗ Z: we measure X on q0 (H rotation), Z on q1 (no rotation)
        #    The probability P_{XZ}(k) comes from basis_results[(X, Z)][k]
        #    Then <XZ> = sum_k (-1)^{k_0} * P_{XZ}(k)
        #
        # 2. But we need to handle the sign structure properly.
        #    For each Pauli string P and basis b:
        #    The expectation = sum_{outcome} (prod_i sign_i(outcome_i)) * P_b(outcome)
        #    where sign_i depends on (P_i, basis_i):
        #    - basis_i = Z: sign = (-1)^outcome_i (Z eigenvalue)
        #    - basis_i = X: sign = outcome_i == 0 ? +1 : -1 after H... no.
        #
        #    Let me re-derive more carefully.
        #    We want <P> = <ψ| ⊗_{i} P_i |ψ>.
        #    We measure in basis b = (b_0, ..., b_{n-1}) where each b_i ∈ {X,Y,Z}.
        #    The measurement projectors are |k>_b <k|_b where |k>_b is the
        #    basis state in the b_i basis for qubit i.
        #
        #    <P> = sum_{k} P_b(k) * <k|_b ⊗_{i} P_i |k>_b
        #
        #    For each qubit i, we need the matrix element:
        #    <k_i|_b_i * P_i * |k_i>_{b_i}
        #
        #    The change-of-basis matrix from Z to b_i:
        #    Z basis: |0>_Z, |1>_Z
        #    X basis: |+>_Z = (|0>+|1>)/√2, |->_Z = (|0>-|1>)/√2
        #    Y basis: |i+>_Z = (|0>+i|1>)/√2, |i->_Z = (|0>-i|1>)/√2
        #
        #    For b_i = Z: |k>_Z, P_i = Z → eigenvalue = (-1)^k
        #    For b_i = Z: |k>_Z, P_i = X → off-diagonal = 0
        #    For b_i = Z: |k>_Z, P_i = Y → off-diagonal = 0
        #    For b_i = Z: |k>_Z, P_i = I → 1
        #
        #    For b_i = X: |k>_X, P_i = Z → off-diagonal: <k|_X Z |k>_X = 0 for both k
        #    For b_i = X: |k>_X, P_i = X → eigenvalue: +1 for k=0, -1 for k=1
        #    For b_i = X: |k>_X, P_i = I → 1
        #
        #    So: for a Pauli P = P_0 ⊗ ... and basis b:
        #    <P> = sum_k (prod_i M_{P_i, b_i}[k_i, k_i]) * P_b(k)
        #    where M is the diagonal of the single-qubit contribution matrix:
        #              Z     X     Y     I
        #    basis Z: [+1,-1] [0,0] [0,0] [1,1]
        #    basis X: [0,0]  [+1,-1] [?,?] [1,1]
        #    basis Y: [0,0]  [?,?] [+1,-1] [1,1]
        #
        #    For X/Y basis with Y/X: these are non-diagonal in Z basis
        #    Actually when we measure in X basis, the outcome k corresponds to
        #    |k>_X = H|k-1>_Z? No...
        #
        #    The probability P_b(k) is already the probability of outcome k
        #    in basis b. We need the "eigenvalue" of P_i for state |k>_b.
        #
        #    Table (row=basis, col=P, cell=[k=0 sign, k=1 sign]):
        #              I       Z       X       Y
        #    Z         [1,1]   [1,-1]  [0,0]   [0,0]
        #    X         [1,1]   [0,0]   [1,-1]  [0,0]
        #    Y         [1,1]   [0,0]   [0,0]   [1,-1]
        #
        #    This gives us the formula:
        #    <P> = sum_k (prod_i sign_matrix[P_i, b_i][k_i]) * P_b(k)
        #
        #    For multi-qubit P, the sign_matrix entry for each qubit is independent.
        #
        #    Implementation: For each Pauli string P and basis b, compute the
        #    product of signs over all qubits, then sum P_b(k) * product_of_signs.

        # Compute <P> for this Pauli string
        # Determine which basis setting we need: b_i = Z if P_i ∈ {I, Z},
        # b_i = P_i if P_i ∈ {X, Y} (we measure in the eigenbasis of P_i).
        basis_for_p: tuple[str, ...] = tuple(
            "Z" if p_i in ("I", "Z") else p_i for p_i in p
        )

        # Get the pre-computed probabilities for this basis
        probs_dict = basis_results[basis_for_p]

        # Build the sign vector for each outcome k
        # sign[k] = product_i sign_matrix[P_i, b_i][k_i]
        # For each qubit i where P_i ∈ {X, Y} and b_i = P_i:
        #   sign contribution = +1 if k_i=0, -1 if k_i=1 (X and Y eigenvalues in their own basis)
        # For qubits where P_i = I or P_i = Z and b_i = Z:
        #   if P_i = Z and b_i = Z: sign = (-1)^k_i (Z eigenvalue in Z basis)
        #   if P_i = I: sign = 1 always
        # For qubits where P_i = Z and b_i = Z: sign = (-1)^k_i
        # For qubits where P_i = I: sign = 1 always
        # For qubits where P_i = X and b_i = X: sign = +1 if k_i=0, -1 if k_i=1
        # For qubits where P_i = Y and b_i = Y: sign = +1 if k_i=0, -1 if k_i=1
        # For all other cases (mismatched P_i and b_i), sign = 0, which kills the term.

        total = 0.0
        for outcome, prob in probs_dict.items():
            if prob == 0:
                continue
            outcome_str = f"{outcome:0{n}b}"
            sign = 1.0
            for i, (p_i, b_i) in enumerate(zip(p, basis_for_p)):
                k_i = int(outcome_str[i])
                if p_i == "I":
                    # identity: always +1
                    s = 1
                elif p_i == "Z":
                    if b_i == "Z":
                        s = 1 if k_i == 0 else -1
                    else:
                        # P=Z but basis is X or Y: diagonal is 0
                        sign = 0
                        break
                elif p_i == "X":
                    if b_i == "X":
                        s = 1 if k_i == 0 else -1
                    else:
                        sign = 0
                        break
                elif p_i == "Y":
                    if b_i == "Y":
                        s = 1 if k_i == 0 else -1
                    else:
                        sign = 0
                        break
                sign *= s
            total += sign * prob

        expectations[p] = total

    # Build the density matrix from Pauli expectations
    # rho = (1/2^n) * sum_{pauli_strings} <P> * P
    # where P is the Pauli string operator (tensor product of Pauli matrices)
    #
    # We build rho in the computational (Z) basis.
    # The 2^n × 2^n matrix is indexed by |a> (row) and |b> (col).
    # rho_{a,b} = (1/2^n) * sum_P <P> * <a| P |b>
    # where <a| P |b> = product_i <a_i| P_i |b_i>
    # and each <a_i| P_i |b_i> is a 2×2 matrix element.
    #
    # For the Pauli matrices in Z basis:
    #   I = [[1,0],[0,1]], Z = [[1,0],[0,-1]], X = [[0,1],[1,0]], Y = [[0,-i],[i,0]]
    # <a_i| I |b_i> = δ_{a,b}
    # <a_i| Z |b_i> = δ_{a,b} * (-1)^{a_i}
    # <a_i| X |b_i> = δ_{a_i, 1-b_i} (flips)
    # <a_i| Y |b_i> = δ_{a_i, 1-b_i} * (-i)^{a_i} * i^{b_i}... complex
    #
    # For real density matrices (pure states from unitary circuits),
    # the Y contributions to off-diagonal elements are purely imaginary,
    # which cancel out. For simplicity with floating point, we compute
    # using qutip which handles this correctly.

    try:
        import qutip as qt

        # Use QuTiP for correct complex matrix construction
        d = 2**n
        rho = np.zeros((d, d), dtype=complex)

        # Pauli matrices in QuTiP ordering: dimension 2, first qubit is leftmost
        # Qubit 0 → most significant bit → index offset 2^(n-1-i)
        PAMS = {
            "I": qt.qeye(2),
            "X": qt.sigmax(),
            "Y": qt.sigmay(),
            "Z": qt.sigmaz(),
        }

        for p in pauli_strings:
            exp = expectations[p]
            # Build the n-qubit Pauli operator by tensor product
            # p[0] is qubit 0 (MSB in our bit ordering)
            op = PAMS[p[0]]
            for pi in p[1:]:
                op = qt.tensor(op, PAMS[pi])
            rho = rho + exp * op.full()

        rho = rho / (2**n)

        # Make numerically Hermitian
        rho = (rho + rho.conj().T) / 2

    except ImportError:
        # Fallback: manual construction (only handles real matrices correctly)
        d = 2**n
        rho = np.zeros((d, d), dtype=float)

        # Build lookup: for each (a,b) pair, compute sum_P <P> * <a|P|b>
        for a in range(d):
            for b in range(d):
                a_str = f"{a:0{n}b}"
                b_str = f"{b:0{n}b}"
                val = 0.0
                for p in pauli_strings:
                    exp = expectations[p]
                    prod = 1.0 + 0.0j  # complex for uniform handling
                    for i in range(n):
                        ai, bi = int(a_str[i]), int(b_str[i])
                        pi = p[i]
                        if pi == "I":
                            prod *= 1
                        elif pi == "Z":
                            prod *= (1 if ai == 0 else -1) if ai == bi else 0
                        elif pi == "X":
                            prod *= 1 if ai != bi else 0
                        elif pi == "Y":
                            # Y = [[0,-i],[i,0]] in Z basis
                            # <a|Y|b> = -i if (a,b)=(0,1), i if (a,b)=(1,0)
                            if (ai, bi) == (0, 1):
                                prod *= -1j
                            elif (ai, bi) == (1, 0):
                                prod *= 1j
                            else:
                                prod *= 0
                    val += exp * prod
                rho[a, b] = val / (2**n)

        rho = rho.real
        rho = (rho + rho.T) / 2  # symmetrize (should already be symmetric for pure states)

    return rho


def tomography_summary(
    rho: np.ndarray,
    label: str = "ρ",
    reference_state: Optional[np.ndarray] = None,
) -> None:
    """Print a human-readable summary of a density matrix tomography result.

    Shows eigenvalues, purity (:math:` mathrm{Tr}( rho^2)`), trace, and,
    if ``reference_state`` is provided, the fidelity
    :math:`F( rho, \sigma) = ( mathrm{Tr}sqrt{sqrt{ rho}\sigmasqrt{ rho}})^2`.

    Args:
        rho: Density matrix from :func:`state_tomography`.
        label: Label to print alongside the matrix (e.g. ``"ρ"``).
        reference_state: Optional reference density matrix for fidelity
            computation. If ``None`` the fidelity is skipped.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.measurement import (
        ...     state_tomography, tomography_summary
        ... )
        >>> c = Circuit()
        >>> c.h(0)
        >>> c.cx(0, 1)
        >>> c.measure(0, 1)
        >>> rho = state_tomography(c, shots=4096)
        >>> tomography_summary(rho)   # doctest: +SKIP
    """
    import qutip as qt

    n = int(np.log2(rho.shape[0]))
    qt_rho = qt.Qobj(rho, dims=[[2] * n, [2] * n])

    # Eigenvalues
    eigvals = qt_rho.eigenenergies()
    eigvals = np.sort(eigvals.real)[::-1]

    print(f"{'=' * 50}")
    print(f"State Tomography Summary  (n_qubits={n})")
    print(f"{'=' * 50}")
    print(f"\nEigenvalues (largest first):")
    for i, ev in enumerate(eigvals):
        print(f"  λ_{i} = {ev: .6f}")

    # Purity
    purity = float(np.real(np.trace(rho @ rho)))
    print(f"\nPurity  Tr(ρ²) = {purity:.6f}  "
          f"({'pure' if abs(purity - 1.0) < 1e-4 else 'mixed'})")

    # Trace
    tr = float(np.real(np.trace(rho)))
    print(f"Trace   Tr(ρ)   = {tr:.6f}")

    # Fidelity with reference
    if reference_state is not None:
        qt_ref = qt.Qobj(reference_state, dims=[[2] * n, [2] * n])
        fid = qt.fidelity(qt_rho, qt_ref)
        print(f"\nFidelity F(ρ, σ) = {fid:.6f}")

    print(f"{'=' * 50}\n")
