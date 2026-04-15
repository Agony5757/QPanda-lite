"""QuTiP-backed density matrix simulator implementation.

This module provides a density-matrix quantum simulator implementation using
QuTiP, supporting unitary operations, Kraus channels, and measurement for
noisy quantum simulation.

Key exports:
    - DensityOperatorSimulatorQutip: Density-matrix simulator backed by QuTiP.
"""

from __future__ import annotations

from itertools import product

import numpy as np
from qutip import Qobj, basis, ket2dm, qeye, sigmax, sigmay, sigmaz, tensor
from qutip_qip.operations import (
    cnot,
    expand_operator,
    phasegate,
    rx,
    ry,
    rz,
    snot,
    sqrtnot,
    swap,
    toffoli,
)


def _validate_kraus_ops(kraus_ops: list[Qobj], nqubit: int) -> None:
    """Validate Kraus operators satisfy the Kraus representation condition."""
    ndim = 2**nqubit
    for K in kraus_ops:
        if not isinstance(K, Qobj):
            raise TypeError("Kraus operators must be Qobj instances.")
        if K.type != "oper":
            raise TypeError("Kraus operators must be operators.")
        if K.shape != (ndim, ndim):
            raise ValueError(f"Kraus operators must be square matrices with dimensions ({ndim}, {ndim}).")
    sum_kraus = sum(kraus_op.dag() * kraus_op for kraus_op in kraus_ops)
    eye = qeye(ndim)
    if not np.allclose(sum_kraus.full(), eye.full()):
        raise ValueError("Kraus operators must satisfy the Kraus representation condition.")


class DensityOperatorSimulatorQutip:
    """Density-matrix simulator backed by QuTiP."""

    n_qubits: int
    density_matrix: Qobj | None

    def __init__(self) -> None:
        self.n_qubits = 0
        self.density_matrix = None

    def init_n_qubit(self, n: int) -> None:
        """Initialize the simulator with n qubits in the ``|0...0>`` state."""
        self.n_qubits = n
        zero_state = tensor([basis(2, 0) for _ in range(n)])
        self.density_matrix = ket2dm(zero_state)

    def _expand_operator(self, operator: Qobj, targets: list[int]) -> Qobj:
        return expand_operator(operator, self.n_qubits, [self.n_qubits - 1 - i for i in targets])

    def _construct_control_op(self, control_qubits: list[int], U_expanded: Qobj) -> Qobj:
        """Apply control structure to U_expanded."""
        if not control_qubits:
            return U_expanded
        control_qubits = [self.n_qubits - 1 - i for i in control_qubits]
        identity = tensor([qeye(2)] * self.n_qubits)
        proj = tensor([qeye(2)] * self.n_qubits)
        for q in control_qubits:
            op_list = [qeye(2) if i != q else basis(2, 1).proj() for i in range(self.n_qubits)]
            proj_q = tensor(op_list)
            proj = proj * proj_q
        return proj * U_expanded + (identity - proj)

    def _apply_unitary(
        self,
        U: Qobj,
        qubits: list[int],
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply a unitary gate to the density matrix."""
        if control_qubits_set is None:
            control_qubits_set = []
        U_base = U.dag() if is_dagger else U
        U_expanded = self._expand_operator(U_base, qubits)
        control_op = self._construct_control_op(control_qubits_set, U_expanded)
        self.density_matrix = control_op * self.density_matrix * control_op.dag()  # type: ignore[operator]

    def _apply_kraus(self, kraus_ops: list[Qobj], targets: list[int]) -> None:
        """Apply Kraus operators to the density matrix."""
        expanded_ops = [self._expand_operator(K, targets) for K in kraus_ops]
        new_rho = sum(K * self.density_matrix * K.dag() for K in expanded_ops)  # type: ignore[operator]
        self.density_matrix = new_rho  # type: ignore[assignment]

    # ─────────────────── Single-qubit gates ───────────────────

    def rx(
        self,
        qubit: int,
        theta: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the RX gate.

        Args:
            qubit: Target qubit index.
            theta: Rotation angle in radians.
            control_qubits_set: Control qubits for controlled rotation.
            is_dagger: Whether to apply the dagger version.
        """
        U = rx(theta)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def ry(
        self,
        qubit: int,
        theta: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the RY gate.

        Args:
            qubit: Target qubit index.
            theta: Rotation angle in radians.
            control_qubits_set: Control qubits for controlled rotation.
            is_dagger: Whether to apply the dagger version.
        """
        U = ry(theta)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def rz(
        self,
        qubit: int,
        theta: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the RZ gate.

        Args:
            qubit: Target qubit index.
            theta: Rotation angle in radians.
            control_qubits_set: Control qubits for controlled rotation.
            is_dagger: Whether to apply the dagger version.
        """
        U = rz(theta)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def x(
        self,
        qubit: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the X (NOT) gate.

        Args:
            qubit: Target qubit index.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = sigmax()
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def y(
        self,
        qubit: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the Y gate.

        Args:
            qubit: Target qubit index.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = sigmay()
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def z(
        self,
        qubit: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the Z gate.

        Args:
            qubit: Target qubit index.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = sigmaz()
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def hadamard(
        self,
        qubit: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the Hadamard gate.

        Args:
            qubit: Target qubit index.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = snot()
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def sx(
        self,
        qubit: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the SX (square-root of X) gate.

        Args:
            qubit: Target qubit index.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = sqrtnot()
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def s(
        self,
        qubit: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the S gate (phase gate, π/2).

        Args:
            qubit: Target qubit index.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = phasegate(np.pi / 2)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def t(
        self,
        qubit: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the T gate (π/4 phase gate).

        Args:
            qubit: Target qubit index.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = phasegate(np.pi / 4)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    # ─────────────────── Two-qubit gates ───────────────────

    def cnot(
        self,
        control_qubit: int,
        target_qubit: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the CNOT (controlled-NOT) gate.

        Args:
            control_qubit: Control qubit index.
            target_qubit: Target qubit index.
            control_qubits_set: Additional control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = cnot(2, 0, 1)
        self._apply_unitary(U, [control_qubit, target_qubit], control_qubits_set, is_dagger)

    def cz(
        self,
        qubit1: int,
        qubit2: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the CZ (controlled-Z) gate.

        Args:
            qubit1: First qubit index.
            qubit2: Second qubit index.
            control_qubits_set: Additional control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = Qobj([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]], dims=[[2, 2], [2, 2]])
        self._apply_unitary(U, [qubit1, qubit2], control_qubits_set, is_dagger)

    def swap(
        self,
        qubit1: int,
        qubit2: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the SWAP gate.

        Args:
            qubit1: First qubit index.
            qubit2: Second qubit index.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = swap()
        self._apply_unitary(U, [qubit1, qubit2], control_qubits_set, is_dagger)

    def toffoli(
        self,
        c1: int,
        c2: int,
        target: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the Toffoli (CCNOT) gate.

        Args:
            c1: First control qubit index.
            c2: Second control qubit index.
            target: Target qubit index.
            control_qubits_set: Additional control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = toffoli()
        self._apply_unitary(U, [c1, c2, target], control_qubits_set, is_dagger)

    def iswap(
        self,
        q1: int,
        q2: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the iSWAP gate.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        matrix = Qobj(
            [[1, 0, 0, 0], [0, 0, 1j, 0], [0, 1j, 0, 0], [0, 0, 0, 1]],
            dims=[[2, 2], [2, 2]],
        )
        self._apply_unitary(matrix, [q1, q2], control_qubits_set, is_dagger)

    def cswap(
        self,
        control_qubit: int,
        q1: int,
        q2: int,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the CSWAP (Fredkin) gate.

        Args:
            control_qubit: Control qubit index.
            q1: First target qubit index.
            q2: Second target qubit index.
            control_qubits_set: Additional control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        total_control = list(control_qubits_set) + [control_qubit] if control_qubits_set else [control_qubit]
        swap_op = swap()
        self._apply_unitary(swap_op, [q1, q2], total_control, is_dagger)

    # ─────────────────── Parametric gates ───────────────────

    def u1(
        self,
        qubit: int,
        theta: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the U1 gate.

        Args:
            qubit: Target qubit index.
            theta: Phase angle in radians.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = phasegate(theta)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def u2(
        self,
        qubit: int,
        phi: float,
        lam: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the U2 gate.

        Args:
            qubit: Target qubit index.
            phi: First phase angle in radians.
            lam: Second phase angle in radians.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        sqrt2 = np.sqrt(2)
        matrix = np.array(
            [
                [1 / sqrt2, -np.exp(1j * lam) / sqrt2],
                [np.exp(1j * phi) / sqrt2, np.exp(1j * (phi + lam)) / sqrt2],
            ],
            dtype=complex,
        )
        U = Qobj(matrix)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def u3(
        self,
        qubit: int,
        theta: float,
        phi: float,
        lam: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the U3 gate.

        Args:
            qubit: Target qubit index.
            theta: Polar angle in radians.
            phi: First phase angle in radians.
            lam: Second phase angle in radians.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        matrix = np.array(
            [
                [np.cos(theta / 2), -np.exp(1j * lam) * np.sin(theta / 2)],
                [np.exp(1j * phi) * np.sin(theta / 2), np.exp(1j * (phi + lam)) * np.cos(theta / 2)],
            ],
            dtype=complex,
        )
        U = Qobj(matrix)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def xy(
        self,
        q1: int,
        q2: int,
        theta: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the XY interaction gate.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            theta: Interaction angle in radians.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        H = (tensor(sigmax(), sigmax()) + tensor(sigmay(), sigmay())) * (-1j * theta / 4)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def rphi(
        self,
        qubit: int,
        theta: float,
        phi: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the RPhi gate (rotation around axis in XY plane).

        Args:
            qubit: Target qubit index.
            theta: Polar angle in radians.
            phi: Azimuthal angle in radians.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        U = rz(phi) * rx(theta) * rz(-phi)
        self._apply_unitary(U, [qubit], control_qubits_set, is_dagger)

    def rphi90(
        self,
        qubit: int,
        phi: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the RPhi90 gate (π/2 rotation around axis in XY plane).

        Args:
            qubit: Target qubit index.
            phi: Azimuthal angle in radians.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        self.rphi(qubit, np.pi / 2, phi, control_qubits_set, is_dagger)

    def rphi180(
        self,
        qubit: int,
        phi: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the RPhi180 gate (π rotation around axis in XY plane).

        Args:
            qubit: Target qubit index.
            phi: Azimuthal angle in radians.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        self.rphi(qubit, np.pi, phi, control_qubits_set, is_dagger)

    def xx(
        self,
        q1: int,
        q2: int,
        theta: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the XX interaction gate.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            theta: Interaction angle in radians.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        H = tensor(sigmax(), sigmax()) * (-1j * theta / 2)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def yy(
        self,
        q1: int,
        q2: int,
        theta: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the YY interaction gate.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            theta: Interaction angle in radians.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        H = tensor(sigmay(), sigmay()) * (-1j * theta / 2)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def zz(
        self,
        q1: int,
        q2: int,
        theta: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Apply the ZZ interaction gate.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            theta: Interaction angle in radians.
            control_qubits_set: Control qubits.
            is_dagger: Whether to apply the dagger version.
        """
        H = tensor(sigmaz(), sigmaz()) * (-1j * theta / 2)
        U = H.expm()
        self._apply_unitary(U, [q1, q2], control_qubits_set, is_dagger)

    def phaseflip(self, qubit: int, prob: float) -> None:
        """Apply phase-flip (Z) noise.

        Args:
            qubit: Target qubit index.
            prob: Phase-flip probability.
        """
        K0 = np.sqrt(1 - prob) * Qobj([[1, 0], [0, 1]])
        K1 = np.sqrt(prob) * Qobj([[1, 0], [0, -1]])
        self._apply_kraus([K0, K1], [qubit])

    # ─────────────────── Two-qubit parametric gates ───────────────────

    def uu15(
        self,
        q1: int,
        q2: int,
        params: list[float],
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """U15 gate using KAK decomposition.

        Args:
            q1: qubit 1 index
            q2: qubit 2 index
            params: list of 15 parameters
            control_qubits_set: list of control qubits
            is_dagger: whether to apply daggered gate
        """
        if not is_dagger:
            self.u3(q1, *params[0:3], control_qubits_set, False)
            self.u3(q2, *params[3:6], control_qubits_set, False)
            self.xx(q1, q2, params[6], control_qubits_set, False)
            self.yy(q1, q2, params[7], control_qubits_set, False)
            self.zz(q1, q2, params[8], control_qubits_set, False)
            self.u3(q1, *params[9:12], control_qubits_set, False)
            self.u3(q2, *params[12:15], control_qubits_set, False)
        else:
            self.u3(q1, *params[9:12], control_qubits_set, True)
            self.u3(q2, *params[12:15], control_qubits_set, True)
            self.zz(q1, q2, params[8], control_qubits_set, True)
            self.yy(q1, q2, params[7], control_qubits_set, True)
            self.xx(q1, q2, params[6], control_qubits_set, True)
            self.u3(q2, *params[3:6], control_qubits_set, True)
            self.u3(q1, *params[0:3], control_qubits_set, True)

    def phase2q(
        self,
        q1: int,
        q2: int,
        theta1: float,
        theta2: float,
        theta3: float,
        control_qubits_set: list[int] | None = None,
        is_dagger: bool = False,
    ) -> None:
        """Phase2Q gate: u1(q1, theta1), u1(q2, theta2), zz(q1, q2, theta3)."""
        if not is_dagger:
            self.u1(q1, theta1, control_qubits_set, False)
            self.u1(q2, theta2, control_qubits_set, False)
            self.zz(q1, q2, theta3, control_qubits_set, False)
        else:
            self.zz(q1, q2, theta3, control_qubits_set, True)
            self.u1(q2, theta2, control_qubits_set, True)
            self.u1(q1, theta1, control_qubits_set, True)

    # ─────────────────── Noise models ───────────────────

    def pauli_error_1q(self, qubit: int, px: float, py: float, pz: float) -> None:
        """Apply single-qubit Pauli error.

        Args:
            qubit: Target qubit index.
            px: Probability of X error.
            py: Probability of Y error.
            pz: Probability of Z error.
        """
        p0 = max(1 - px - py - pz, 0)
        K0 = np.sqrt(p0) * qeye(2)
        K1 = np.sqrt(px) * sigmax()
        K2 = np.sqrt(py) * sigmay()
        K3 = np.sqrt(pz) * sigmaz()
        self._apply_kraus([K0, K1, K2, K3], [qubit])

    def depolarizing(self, qubit: int, p: float) -> None:
        """Apply depolarizing noise to a single qubit.

        Args:
            qubit: Target qubit index.
            p: Depolarizing probability.
        """
        K0 = np.sqrt(1 - p) * qeye(2)
        K1 = np.sqrt(p / 3) * sigmax()
        K2 = np.sqrt(p / 3) * sigmay()
        K3 = np.sqrt(p / 3) * sigmaz()
        self._apply_kraus([K0, K1, K2, K3], [qubit])

    def bitflip(self, qubit: int, p: float) -> None:
        """Apply bit-flip (X) noise.

        Args:
            qubit: Target qubit index.
            p: Bit-flip probability.
        """
        K0 = np.sqrt(1 - p) * qeye(2)
        K1 = np.sqrt(p) * sigmax()
        self._apply_kraus([K0, K1], [qubit])

    def kraus1q(self, qubit: int, parameters: list[list[float]]) -> None:
        """Apply single-qubit Kraus noise.

        Args:
            qubit: Target qubit index.
            parameters: List of Kraus operator matrix elements (flattened 2x2).
        """
        kraus_ops = [Qobj(np.array(k).reshape(2, 2)) for k in parameters]
        self._apply_kraus(kraus_ops, [qubit])

    def amplitude_damping(self, qubit: int, gamma: float) -> None:
        """Apply amplitude damping noise.

        Args:
            qubit: Target qubit index.
            gamma: Damping rate (0 to 1).
        """
        K0 = Qobj([[1, 0], [0, np.sqrt(1 - gamma)]])
        K1 = Qobj([[0, np.sqrt(gamma)], [0, 0]])
        self._apply_kraus([K0, K1], [qubit])

    def kraus2q(self, q1: int, q2: int, parameters: list[list[float]]) -> None:
        """Apply two-qubit Kraus noise.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            parameters: List of Kraus operator matrix elements (flattened 4x4).
        """
        kraus_ops = [Qobj(np.array(k).reshape(4, 4)) for k in parameters]
        self._apply_kraus(kraus_ops, [q1, q2])

    def pauli_error_2q(self, q1: int, q2: int, parameters: list[float] | tuple[float, ...]) -> None:
        """Two-qubit Pauli error with 15 independent probabilities.

        Args:
            q1: qubit 1 index
            q2: qubit 2 index
            parameters: list of 15 probabilities
        """
        parameters = list(parameters)
        if sum(parameters) > 1:
            raise ValueError("Probabilities must be less than or equal to 1.")
        ii = [1 - sum(parameters)]
        all_params = ii + parameters
        all_params = [np.sqrt(p) for p in all_params]
        (ii, xi, yi, zi, ix, xx, yx, zx, iy, xy, yy, zy, iz, xz, yz, zz) = tuple(all_params)  # type: ignore[assignment]

        Eii = ii * tensor(qeye(2), qeye(2))
        Eix = ix * tensor(sigmax(), qeye(2))
        Eiy = iy * tensor(sigmay(), qeye(2))
        Eiz = iz * tensor(sigmaz(), qeye(2))
        Exi = xi * tensor(qeye(2), sigmax())
        Exx = xx * tensor(sigmax(), sigmax())
        Exy = xy * tensor(sigmay(), sigmax())
        Exz = xz * tensor(sigmaz(), sigmax())
        Eyi = yi * tensor(qeye(2), sigmay())
        Eyx = yx * tensor(sigmax(), sigmay())
        Eyy = yy * tensor(sigmay(), sigmay())
        Eyz = yz * tensor(sigmaz(), sigmay())
        Ezi = zi * tensor(qeye(2), sigmaz())
        Ezx = zx * tensor(sigmax(), sigmaz())
        Ezy = zy * tensor(sigmay(), sigmaz())
        Ezz = zz * tensor(sigmaz(), sigmaz())

        kraus = [
            Eii,
            Exi,
            Eyi,
            Ezi,
            Eix,
            Exx,
            Eyx,
            Ezx,
            Eiy,
            Exy,
            Eyy,
            Ezy,
            Eiz,
            Exz,
            Eyz,
            Ezz,
        ]
        _validate_kraus_ops(kraus, 2)
        self._apply_kraus(kraus, [q1, q2])

    def twoqubit_depolarizing(self, q1: int, q2: int, p: float) -> None:
        """Apply two-qubit depolarizing noise.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            p: Depolarizing probability.
        """
        self.pauli_error_2q(q1, q2, [p / 15] * 15)

    # ─────────────────── Measurement ───────────────────

    def pmeasure(self, measure_qubits: list[int]) -> list[float]:
        """Compute measurement probabilities for the given qubits."""
        prob_list = [0.0] * (2 ** len(measure_qubits))
        for bits in product([0, 1], repeat=len(measure_qubits)):
            proj_list = []
            for q in range(self.n_qubits):
                if q in measure_qubits:
                    idx = measure_qubits.index(q)
                    proj = basis(2, bits[idx]).proj()
                else:
                    proj = qeye(2)
                proj_list.append(proj)
            projector = tensor(proj_list)
            prob = (self.density_matrix * projector).tr().real  # type: ignore[operator]
            bit_idx = int("".join(map(str, bits)), 2)
            prob_list[bit_idx] = prob
        return prob_list

    def stateprob(self) -> np.ndarray:
        """Return the diagonal of the density matrix (state probabilities)."""
        return self.density_matrix.diag().real  # type: ignore[return-value]

    @property
    def state(self) -> np.ndarray:
        """Return the density matrix as a NumPy array."""
        return self.density_matrix.full()  # type: ignore[return-value]


if __name__ == "__main__":
    sim = DensityOperatorSimulatorQutip()
    sim.init_n_qubit(3)
    sim.x(0)
    sim.cnot(0, 1)
    sim.toffoli(0, 1, 2)
    print(sim.density_matrix)
    print(sim.pmeasure([0, 1]))
    print(sim.stateprob())
