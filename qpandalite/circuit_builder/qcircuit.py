from __future__ import annotations

from copy import deepcopy

from .opcode import (
    make_header_originir,
    make_header_qasm,
    make_measure_originir,
    make_measure_qasm,
    opcode_to_line_originir,
    opcode_to_line_qasm,
)

# Opcode: (op_name, qubits, cbits, params, dagger, control_qubits)
QubitSpec = int | list[int]
CbitSpec = int | list[int] | None
ParamSpec = float | list[float] | tuple[float, ...] | None
OpCode = tuple[str, QubitSpec, CbitSpec, ParamSpec, bool, QubitSpec]

__all__ = ["Circuit", "OpcodeType"]

# Backward-compatible type alias
OpcodeType = OpCode


class CircuitControlContext:
    """Context manager for controlled gate blocks."""

    c: Circuit
    control_list: tuple[int, ...]

    def __init__(self, c: Circuit, control_list: tuple[int, ...]) -> None:
        self.c = c
        self.control_list = control_list

    def _qubit_list(self) -> str:
        ret = ""
        for q in self.control_list:
            ret += f"q[{q}], "
        return ret[:-2]

    def __enter__(self) -> None:
        ret = "CONTROL " + self._qubit_list() + "\n"
        self.c.circuit_str += ret

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.c.circuit_str += "ENDCONTROL\n"


class CircuitDagContext:
    """Context manager for dagger (adjoint) gate blocks."""

    c: Circuit

    def __init__(self, c: Circuit) -> None:
        self.c = c

    def __enter__(self) -> None:
        self.c.circuit_str += "DAGGER\n"

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        self.c.circuit_str += "ENDDAGGER\n"


class Circuit:
    """Quantum circuit builder that generates OriginIR and OpenQASM output.

    Attributes
    ----------
    used_qubit_list : list[int]
        Qubits referenced in the circuit.
    circuit_str : str
        Raw string builder used by context managers.
    max_qubit : int
        Highest qubit index used.
    qubit_num : int
        Total number of qubits.
    cbit_num : int
        Total number of classical bits.
    measure_list : list[int]
        Qubits scheduled for measurement.
    opcode_list : list[OpCode]
        Internal list of gate opcodes.
    """

    used_qubit_list: list[int]
    circuit_str: str
    max_qubit: int
    qubit_num: int
    cbit_num: int
    measure_list: list[int]
    opcode_list: list[OpCode]

    def __init__(self) -> None:
        self.used_qubit_list = []
        self.max_qubit = 0
        self.qubit_num = 0
        self.cbit_num = 0
        self.measure_list = []
        self.opcode_list = []
        self.circuit_str = ""

    def copy(self) -> "Circuit":
        """Return a deep copy of this circuit."""
        new_circuit = Circuit()
        new_circuit.used_qubit_list = self.used_qubit_list.copy()
        new_circuit.max_qubit = self.max_qubit
        new_circuit.qubit_num = self.qubit_num
        new_circuit.cbit_num = self.cbit_num
        new_circuit.measure_list = self.measure_list.copy()
        new_circuit.opcode_list = self.opcode_list.copy()
        new_circuit.circuit_str = self.circuit_str
        return new_circuit

    def _make_originir_circuit(self) -> str:
        header = make_header_originir(self.qubit_num, self.cbit_num)
        circuit_str = "\n".join([opcode_to_line_originir(op) for op in self.opcode_list])
        measure = make_measure_originir(self.measure_list)
        return header + circuit_str + "\n" + measure

    def _make_qasm_circuit(self) -> str:
        header = make_header_qasm(self.qubit_num, self.cbit_num)
        circuit_str = "\n".join([opcode_to_line_qasm(op) for op in self.opcode_list])
        measure = make_measure_qasm(self.measure_list)
        return header + circuit_str + "\n" + measure

    @property
    def circuit(self) -> str:
        """Generate the circuit in OriginIR format."""
        return self._make_originir_circuit()

    @property
    def originir(self) -> str:
        """Generate the circuit in OriginIR format."""
        return self._make_originir_circuit()

    @property
    def qasm(self) -> str:
        """Generate the circuit in OpenQASM format."""
        return self._make_qasm_circuit()

    def record_qubit(self, qubits: int | list[int]) -> None:
        """Record the qubits used in the circuit."""
        for qubit in qubits if isinstance(qubits, list) else [qubits]:
            if qubit not in self.used_qubit_list:
                self.used_qubit_list.append(qubit)
                self.max_qubit = max(self.max_qubit, qubit)
        self.qubit_num = self.max_qubit + 1

    def add_gate(
        self,
        operation: str,
        qubits: QubitSpec,
        cbits: CbitSpec = None,
        params: ParamSpec = None,
        dagger: bool = False,
        control_qubits: QubitSpec = None,
    ) -> None:
        """Add a gate to the circuit."""
        opcode: OpCode = (operation, qubits, cbits, params, dagger, control_qubits)  # type: ignore[assignment]
        self.opcode_list.append(opcode)
        self.record_qubit(qubits if isinstance(qubits, list) else [qubits])

    @property
    def depth(self) -> int:
        """Calculate the depth of the quantum circuit."""
        qubit_depths: dict[int, int] = {}

        for opcode in self.opcode_list:
            op_name, qubits, _, _, _, control_qubits = opcode

            if op_name in ("I", "BARRIER"):
                continue

            if not isinstance(qubits, list):
                qubits = [qubits]

            all_qubits = qubits + list(control_qubits) if control_qubits else qubits

            current_max_depth = 0
            for q in all_qubits:
                current_max_depth = max(current_max_depth, qubit_depths.get(q, 0))

            for q in all_qubits:
                qubit_depths[q] = current_max_depth + 1

        return max(qubit_depths.values())

    # ─────────────────── Single-qubit gates (no parameters) ───────────────────

    def identity(self, qn: int) -> None:
        """Apply the identity (no-op) gate to qubit."""
        self.add_gate("I", qn)

    def h(self, qn: int) -> None:
        """Apply single-qubit Hadamard gate to qubit."""
        self.add_gate("H", qn)

    def x(self, qn: int) -> None:
        """Apply Pauli-X (NOT) gate to qubit."""
        self.add_gate("X", qn)

    def y(self, qn: int) -> None:
        """Apply Pauli-Y gate to qubit."""
        self.add_gate("Y", qn)

    def z(self, qn: int) -> None:
        """Apply Pauli-Z gate to qubit."""
        self.add_gate("Z", qn)

    def sx(self, qn: int) -> None:
        """Apply square-root-of-X (SX) gate to qubit."""
        self.add_gate("SX", qn)

    def sxdg(self, qn: int) -> None:
        """Apply conjugate-transpose of SX gate to qubit."""
        self.add_gate("SX", qn, dagger=True)

    def s(self, qn: int) -> None:
        """Apply S (phase) gate to qubit."""
        self.add_gate("S", qn)

    def sdg(self, qn: int) -> None:
        """Apply S-dagger (inverse phase) gate to qubit."""
        self.add_gate("S", qn, dagger=True)

    def t(self, qn: int) -> None:
        """Apply T gate to qubit."""
        self.add_gate("T", qn)

    def tdg(self, qn: int) -> None:
        """Apply T-dagger (inverse T) gate to qubit."""
        self.add_gate("T", qn, dagger=True)

    # ─────────────────── Single-qubit parametric gates ───────────────────

    def rx(self, qn: int, theta: float) -> None:
        """Apply RX rotation gate.

        Args:
            qn: Target qubit index.
            theta: Rotation angle in radians.
        """
        self.add_gate("RX", qn, params=theta)

    def ry(self, qn: int, theta: float) -> None:
        """Apply RY rotation gate.

        Args:
            qn: Target qubit index.
            theta: Rotation angle in radians.
        """
        self.add_gate("RY", qn, params=theta)

    def rz(self, qn: int, theta: float) -> None:
        """Apply RZ rotation gate.

        Args:
            qn: Target qubit index.
            theta: Rotation angle in radians.
        """
        self.add_gate("RZ", qn, params=theta)

    def rphi(self, qn: int, theta: float, phi: float) -> None:
        """Apply RPhi rotation gate.

        Args:
            qn: Target qubit index.
            theta: Polar rotation angle in radians.
            phi: Azimuthal angle in radians.
        """
        self.add_gate("RPhi", qn, params=[theta, phi])

    # ─────────────────── Two-qubit gates ───────────────────

    def cnot(self, controller: int, target: int) -> None:
        """Apply CNOT (controlled-X) gate.

        Args:
            controller: Control qubit index.
            target: Target qubit index.
        """
        self.add_gate("CNOT", [controller, target])

    def cx(self, controller: int, target: int) -> None:
        """Apply CX gate (alias for CNOT).

        Args:
            controller: Control qubit index.
            target: Target qubit index.
        """
        self.cnot(controller, target)

    def cz(self, q1: int, q2: int) -> None:
        """Apply controlled-Z gate to two qubits."""
        self.add_gate("CZ", [q1, q2])

    def iswap(self, q1: int, q2: int) -> None:
        """Apply iSWAP gate to two qubits."""
        self.add_gate("ISWAP", [q1, q2])

    def swap(self, q1: int, q2: int) -> None:
        """Apply SWAP gate to two qubits."""
        self.add_gate("SWAP", [q1, q2])

    # ─────────────────── Three-qubit gates ───────────────────

    def cswap(self, q1: int, q2: int, q3: int) -> None:
        """Apply CSWAP (Fredkin) gate to three qubits."""
        self.add_gate("CSWAP", [q1, q2, q3])

    def toffoli(self, q1: int, q2: int, q3: int) -> None:
        """Apply Toffoli (CCNOT) gate to three qubits."""
        self.add_gate("TOFFOLI", [q1, q2, q3])

    # ─────────────────── Parametric gates ───────────────────

    def u1(self, qn: int, lam: float) -> None:
        """Apply U1 single-parameter unitary gate.

        Args:
            qn: Target qubit index.
            lam: Phase angle lambda in radians.
        """
        self.add_gate("U1", qn, params=lam)

    def u2(self, qn: int, phi: float, lam: float) -> None:
        """Apply U2 two-parameter unitary gate.

        Args:
            qn: Target qubit index.
            phi: Phi angle in radians.
            lam: Lambda angle in radians.
        """
        self.add_gate("U2", qn, params=[phi, lam])

    def u3(self, qn: int, theta: float, phi: float, lam: float) -> None:
        """Apply U3 three-parameter unitary gate.

        Args:
            qn: Target qubit index.
            theta: Theta angle in radians.
            phi: Phi angle in radians.
            lam: Lambda angle in radians.
        """
        self.add_gate("U3", qn, params=[theta, phi, lam])

    def xx(self, q1: int, q2: int, theta: float) -> None:
        """Apply XX Ising interaction gate.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            theta: Interaction angle in radians.
        """
        self.add_gate("XX", [q1, q2], params=theta)

    def yy(self, q1: int, q2: int, theta: float) -> None:
        """Apply YY Ising interaction gate.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            theta: Interaction angle in radians.
        """
        self.add_gate("YY", [q1, q2], params=theta)

    def zz(self, q1: int, q2: int, theta: float) -> None:
        """Apply ZZ Ising interaction gate.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            theta: Interaction angle in radians.
        """
        self.add_gate("ZZ", [q1, q2], params=theta)

    def phase2q(self, q1: int, q2: int, theta1: float, theta2: float, thetazz: float) -> None:
        """Apply two-qubit phase gate with local and ZZ terms.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            theta1: Local phase angle for q1 in radians.
            theta2: Local phase angle for q2 in radians.
            thetazz: ZZ interaction angle in radians.
        """
        self.add_gate("PHASE2Q", [q1, q2], params=[theta1, theta2, thetazz])

    def uu15(self, q1: int, q2: int, params: list[float]) -> None:
        """Apply general two-qubit UU15 gate with 15 parameters.

        Args:
            q1: First qubit index.
            q2: Second qubit index.
            params: List of 15 rotation parameters in radians.
        """
        self.add_gate("UU15", [q1, q2], params=params)

    def barrier(self, *qubits: int) -> None:
        """Insert a barrier across the specified qubits.

        Args:
            *qubits: Qubit indices to include in the barrier.
        """
        self.add_gate("BARRIER", list(qubits))

    # ─────────────────── Measurement ───────────────────

    def measure(self, *qubits: int) -> None:
        """Schedule qubits for measurement.

        Appends the given qubits to the measurement list.  Multiple calls
        accumulate measurements; classical bit indices are assigned in the
        order qubits are added.

        Args:
            *qubits: One or more qubit indices to measure.
        """
        self.record_qubit(list(qubits))
        if self.measure_list is None:
            self.measure_list = []
        self.measure_list.extend(list(qubits))
        self.cbit_num = len(self.measure_list)

    # ─────────────────── Control / Dagger context managers ───────────────────

    def control(self, *args: int) -> CircuitControlContext:
        """Return a context manager that wraps gates in a CONTROL block.

        All gates added inside the ``with`` block will be executed only
        when all specified control qubits are in state ``|1>``.

        Args:
            *args: One or more control qubit indices.

        Returns:
            A :class:`CircuitControlContext` context manager.

        Raises:
            ValueError: No control qubits were supplied.
        """
        self.record_qubit(list(args))
        if len(args) == 0:
            raise ValueError("Controller qubit must not be empty.")
        return CircuitControlContext(self, args)

    def set_control(self, *args: int) -> None:
        """Manually open a CONTROL block (low-level API; prefer :meth:`control`).

        Args:
            *args: Control qubit indices.
        """
        self.record_qubit(list(args))
        ret = "CONTROL "
        for q in args:
            ret += f"q[{q}], "
        self.circuit_str += ret[:-2] + "\n"

    def unset_control(self) -> None:
        """Manually close a CONTROL block (low-level API; prefer :meth:`control`)."""
        self.circuit_str += "ENDCONTROL\n"

    def dagger(self) -> CircuitDagContext:
        """Return a context manager that wraps gates in a DAGGER block.

        All gates added inside the ``with`` block will be conjugate-transposed
        (adjoint).

        Returns:
            A :class:`CircuitDagContext` context manager.
        """
        return CircuitDagContext(self)

    def set_dagger(self) -> None:
        """Manually open a DAGGER block (low-level API; prefer :meth:`dagger`)."""
        self.circuit_str += "DAGGER\n"

    def unset_dagger(self) -> None:
        """Manually close a DAGGER block (low-level API; prefer :meth:`dagger`)."""
        self.circuit_str += "ENDDAGGER\n"

    # ─────────────────── Remapping ───────────────────

    def remapping(self, mapping: dict[int, int]) -> Circuit:
        """Create a new circuit with qubits remapped according to *mapping*."""
        if not all(isinstance(k, int) and isinstance(v, int) and k >= 0 and v >= 0 for k, v in mapping.items()):
            raise TypeError("All keys and values in mapping must be non-negative integers.")

        if len(set(mapping.values())) != len(mapping.values()):
            raise ValueError("A physical qubit is assigned more than once.")

        for qubit in self.used_qubit_list:
            if qubit not in mapping:
                raise ValueError(f"At least one qubit is not appeared in mapping. (qubit : {qubit})")

        unique_qubit_set: set[int] = set()
        for qubit in mapping:
            if qubit in unique_qubit_set:
                raise ValueError(f"Qubit is used twice in the mapping. Given mapping : ({mapping})")
            unique_qubit_set.add(qubit)

        c = deepcopy(self)

        def remap_opcode(opcode: OpCode, mp: dict[int, int]) -> OpCode:
            op_name, qubits, cbits, params, dagger, control_qubits = opcode
            new_qubits = [mp[q] for q in qubits] if isinstance(qubits, list) else mp[qubits]

            if control_qubits is not None:
                new_control_qubits = (
                    [mp[q] for q in control_qubits] if isinstance(control_qubits, list) else mp[control_qubits]
                )
            else:
                new_control_qubits = None

            return (op_name, new_qubits, cbits, params, dagger, new_control_qubits)

        c.opcode_list = [remap_opcode(op, mapping) for op in self.opcode_list]

        for i, old_qubit in enumerate(self.used_qubit_list):
            c.used_qubit_list[i] = mapping[old_qubit]

        for i, old_qubit in enumerate(self.measure_list):
            c.measure_list[i] = mapping[old_qubit]

        c.max_qubit = max(c.used_qubit_list)
        c.qubit_num = c.max_qubit + 1
        c.cbit_num = len(c.measure_list)

        return c
