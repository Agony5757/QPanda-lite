"""Circuit adapter layer for converting QPanda-lite circuits to provider-native formats.

This module provides adapter classes for converting QPanda-lite Circuit objects
to native circuit formats used by different quantum computing platforms:
- OriginQ (pyqpanda)
- Quafu (pyquafu)
- IBM (qiskit)

Usage:
    from qpandalite.circuit_adapter import OriginQCircuitAdapter, QuafuCircuitAdapter, IBMCircuitAdapter
    from qpandalite.circuit_builder import Circuit

    # Create a QPanda-lite circuit
    circuit = Circuit()
    circuit.h(0)
    circuit.cnot(0, 1)
    circuit.measure(0, 1)

    # Convert to provider-native circuits
    originq_adapter = OriginQCircuitAdapter()
    pyqpanda_circuit = originq_adapter.adapt(circuit)

    quafu_adapter = QuafuCircuitAdapter()
    quafu_circuit = quafu_adapter.adapt(circuit)

    ibm_adapter = IBMCircuitAdapter()
    qiskit_circuit = ibm_adapter.adapt(circuit)
"""

from __future__ import annotations

__all__ = [
    "CircuitAdapter",
    "OriginQCircuitAdapter",
    "QuafuCircuitAdapter",
    "IBMCircuitAdapter",
]

import abc
from typing import TYPE_CHECKING, Any, List, TypeVar, Generic, Optional

if TYPE_CHECKING:
    from qpandalite.circuit_builder.qcircuit import Circuit

# Type variable for provider-native circuit types
T = TypeVar("T")


class CircuitAdapter(abc.ABC, Generic[T]):
    """Abstract base class for circuit adapters.

    Provides a unified interface for converting QPanda-lite Circuit objects
to provider-native circuit formats.
    """

    @abc.abstractmethod
    def adapt(self, circuit: "Circuit") -> T:
        """Convert a QPanda-lite Circuit to the provider's native circuit format.

        Args:
            circuit: QPanda-lite Circuit object.

        Returns:
            Provider-native circuit object.
        """
        ...

    def adapt_batch(self, circuits: List["Circuit"]) -> List[T]:
        """Convert multiple QPanda-lite Circuits to provider-native format.

        Args:
            circuits: List of QPanda-lite Circuit objects.

        Returns:
            List of provider-native circuit objects.
        """
        return [self.adapt(c) for c in circuits]

    @abc.abstractmethod
    def get_supported_gates(self) -> List[str]:
        """Return the list of gate names supported by this adapter.

        Returns:
            List of supported gate names (uppercase strings).
        """
        ...

    def _get_originir(self, circuit: "Circuit") -> str:
        """Extract OriginIR string from a QPanda-lite Circuit.

        Args:
            circuit: QPanda-lite Circuit object.

        Returns:
            OriginIR string representation of the circuit.
        """
        return circuit.originir


class OriginQCircuitAdapter(CircuitAdapter[Any]):
    """Adapter for converting QPanda-lite Circuit to pyqpanda (OriginQ) format.

    Uses pyqpanda3's intermediate compiler to convert OriginIR to QProg.
    """

    # Gate mapping from OriginIR names to pyqpanda supported gates
    SUPPORTED_GATES = [
        "H", "X", "Y", "Z", "S", "T", "SX",
        "RX", "RY", "RZ", "RPhi", "RPhi90", "RPhi180",
        "U1", "U2", "U3", "U4",
        "CNOT", "CZ", "SWAP", "ISWAP",
        "TOFFOLI", "CSWAP",
        "XX", "YY", "ZZ", "XY",
        "PHASE2Q", "UU15",
        "I", "BARRIER", "MEASURE",
    ]

    def __init__(self) -> None:
        self._pyqpanda3: Any = None
        self._convert_originir: Any = None

    def _ensure_imports(self) -> None:
        """Lazily import pyqpanda3 modules."""
        if self._pyqpanda3 is None or self._convert_originir is None:
            try:
                from pyqpanda3 import core as pyqpanda3_core
                from pyqpanda3.intermediate_compiler import (
                    convert_originir_string_to_qprog,
                )
                self._pyqpanda3 = pyqpanda3_core
                self._convert_originir = convert_originir_string_to_qprog
            except ImportError as e:
                raise RuntimeError(
                    "pyqpanda3 is required for OriginQCircuitAdapter. "
                    "Install it with: pip install pyqpanda3"
                ) from e

    def adapt(self, circuit: "Circuit") -> Any:
        """Convert QPanda-lite Circuit to pyqpanda QProg.

        Args:
            circuit: QPanda-lite Circuit object.

        Returns:
            pyqpanda3.core.QProg object.
        """
        self._ensure_imports()
        originir = self._get_originir(circuit)
        return self._convert_originir(originir)

    def get_supported_gates(self) -> List[str]:
        """Return the list of gate names supported by this adapter."""
        return self.SUPPORTED_GATES.copy()


class QuafuCircuitAdapter(CircuitAdapter[Any]):
    """Adapter for converting QPanda-lite Circuit to pyquafu (Quafu) format.

    Translates OriginIR gate by gate to quafu.QuantumCircuit.
    """

    # Gate mapping from OriginIR to Quafu
    SUPPORTED_GATES = [
        "H", "X", "Y", "Z",
        "RX", "RY", "RZ",
        "CNOT", "CZ",
        "MEASURE",
        # Note: Quafu supports more gates, these are the most common ones
    ]

    def __init__(self) -> None:
        self._quafu: Any = None
        self._QuantumCircuit: Any = None

    def _ensure_imports(self) -> None:
        """Lazily import quafu modules."""
        if self._quafu is None:
            try:
                import quafu
                from quafu import QuantumCircuit
                self._quafu = quafu
                self._QuantumCircuit = QuantumCircuit
            except ImportError as e:
                raise RuntimeError(
                    "quafu is required for QuafuCircuitAdapter. "
                    "Install it with: pip install pyquafu"
                ) from e

    def adapt(self, circuit: "Circuit") -> Any:
        """Convert QPanda-lite Circuit to quafu QuantumCircuit.

        Args:
            circuit: QPanda-lite Circuit object.

        Returns:
            quafu.QuantumCircuit object.
        """
        self._ensure_imports()
        from qpandalite.originir.originir_line_parser import OriginIR_LineParser

        originir = self._get_originir(circuit)
        lines = originir.splitlines()
        qc: Any = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                (
                    operation,
                    qubit,
                    cbit,
                    parameter,
                    dagger_flag,
                    control_qubits,
                ) = OriginIR_LineParser.parse_line(line)
            except NotImplementedError:
                raise RuntimeError(
                    f"Unknown OriginIR operation in Quafu adapter: {line}"
                ) from None

            # Initialize circuit on QINIT
            if operation == "QINIT":
                num_qubits = int(qubit)
                qc = self._QuantumCircuit(num_qubits)
                continue

            if qc is None:
                raise RuntimeError("QINIT must appear before any gate operation.")

            # Skip CREG (handled implicitly)
            if operation == "CREG":
                continue

            # Apply gates
            qc = self._apply_gate(qc, operation, qubit, cbit, parameter, dagger_flag, control_qubits)

        if qc is None:
            raise RuntimeError("OriginIR string produced no circuit.")

        return qc

    def _apply_gate(
        self,
        qc: Any,
        operation: Optional[str],
        qubit: Any,
        cbit: Any,
        parameter: Any,
        dagger_flag: Optional[bool],
        control_qubits: Any,
    ) -> Any:
        """Apply a single gate to the Quafu QuantumCircuit.

        Args:
            qc: Quafu QuantumCircuit object.
            operation: Gate operation name.
            qubit: Target qubit(s).
            cbit: Classical bit for measurement.
            parameter: Gate parameter(s).
            dagger_flag: Whether the gate is daggered.
            control_qubits: Control qubits for controlled gates.

        Returns:
            Modified QuantumCircuit object.
        """
        if operation is None:
            return qc

        # Single-qubit gates
        if operation == "H":
            qc.h(int(qubit))
        elif operation == "X":
            qc.x(int(qubit))
        elif operation == "Y":
            qc.y(int(qubit))
        elif operation == "Z":
            qc.z(int(qubit))
        elif operation == "S":
            if dagger_flag:
                qc.sdg(int(qubit))
            else:
                qc.s(int(qubit))
        elif operation == "T":
            if dagger_flag:
                qc.tdg(int(qubit))
            else:
                qc.t(int(qubit))
        elif operation == "SX":
            if dagger_flag:
                qc.sxdg(int(qubit))
            else:
                qc.sx(int(qubit))

        # Single-qubit rotation gates
        elif operation == "RX":
            qc.rx(int(qubit), float(parameter))
        elif operation == "RY":
            qc.ry(int(qubit), float(parameter))
        elif operation == "RZ":
            qc.rz(int(qubit), float(parameter))

        # Two-qubit gates
        elif operation == "CNOT":
            qubits = qubit if isinstance(qubit, list) else [qubit]
            qc.cnot(int(qubits[0]), int(qubits[1]))
        elif operation == "CZ":
            qubits = qubit if isinstance(qubit, list) else [qubit]
            qc.cz(int(qubits[0]), int(qubits[1]))
        elif operation == "SWAP":
            qubits = qubit if isinstance(qubit, list) else [qubit]
            qc.swap(int(qubits[0]), int(qubits[1]))
        elif operation == "ISWAP":
            qubits = qubit if isinstance(qubit, list) else [qubit]
            qc.iswap(int(qubits[0]), int(qubits[1]))

        # Measurement
        elif operation == "MEASURE":
            # Quafu measure takes lists of qubits and cbits
            if cbit is not None:
                qc.measure([int(qubit)], [int(cbit)])
            else:
                qc.measure([int(qubit)])

        # Barrier
        elif operation == "BARRIER":
            if isinstance(qubit, list):
                qc.barrier(qubit)
            else:
                qc.barrier([qubit])

        # Ignore control structure markers
        elif operation in ("CONTROL", "ENDCONTROL", "DAGGER", "ENDDAGGER"):
            pass

        else:
            # For unsupported gates, raise a clear error
            raise NotImplementedError(
                f"Gate '{operation}' is not supported by QuafuCircuitAdapter. "
                f"Supported gates: {self.SUPPORTED_GATES}"
            )

        return qc

    def get_supported_gates(self) -> List[str]:
        """Return the list of gate names supported by this adapter."""
        return self.SUPPORTED_GATES.copy()


class IBMCircuitAdapter(CircuitAdapter[Any]):
    """Adapter for converting QPanda-lite Circuit to qiskit (IBM) format.

    Converts Circuit -> OriginIR -> QASM -> Qiskit QuantumCircuit.
    """

    # QASM 2.0 standard gates supported by qiskit
    SUPPORTED_GATES = [
        "H", "X", "Y", "Z", "S", "T", "SX",
        "RX", "RY", "RZ",
        "U1", "U2", "U3",
        "CNOT", "CX", "CZ", "SWAP", "ISWAP",
        "TOFFOLI", "CCX", "CSWAP", "Fredkin",
        "MEASURE", "BARRIER",
        "I", "ID",
    ]

    def __init__(self) -> None:
        self._qiskit: Any = None

    def _ensure_imports(self) -> None:
        """Lazily import qiskit modules."""
        if self._qiskit is None:
            try:
                import qiskit
                self._qiskit = qiskit
            except ImportError as e:
                raise RuntimeError(
                    "qiskit is required for IBMCircuitAdapter. "
                    "Install it with: pip install qiskit"
                ) from e

    def adapt(self, circuit: "Circuit") -> Any:
        """Convert QPanda-lite Circuit to qiskit QuantumCircuit.

        The conversion path is:
        QPanda-lite Circuit -> OriginIR -> QASM -> Qiskit QuantumCircuit

        Args:
            circuit: QPanda-lite Circuit object.

        Returns:
            qiskit.QuantumCircuit object.
        """
        self._ensure_imports()

        # Get QASM representation (via OriginIR -> QASM conversion)
        qasm_str = circuit.qasm

        # Parse QASM to Qiskit QuantumCircuit
        return self._qiskit.QuantumCircuit.from_qasm_str(qasm_str)

    def adapt_with_transpilation(
        self,
        circuit: "Circuit",
        backend: Any = None,
        optimization_level: int = 1,
        **kwargs: Any,
    ) -> Any:
        """Convert and transpile the circuit for a specific backend.

        Args:
            circuit: QPanda-lite Circuit object.
            backend: Qiskit backend to transpile for.
            optimization_level: Transpiler optimization level (0-3).
            **kwargs: Additional arguments for qiskit.compiler.transpile.

        Returns:
            Transpiled qiskit.QuantumCircuit object.
        """
        self._ensure_imports()
        qiskit_circuit = self.adapt(circuit)

        if backend is not None:
            return self._qiskit.compiler.transpile(
                qiskit_circuit, backend=backend, optimization_level=optimization_level, **kwargs
            )

        return qiskit_circuit

    def get_supported_gates(self) -> List[str]:
        """Return the list of gate names supported by this adapter."""
        return self.SUPPORTED_GATES.copy()
