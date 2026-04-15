"""Quantum error models for noisy simulation.

This module defines various quantum noise models that can be applied to
circuit simulations, including bit-flip, phase-flip, depolarizing, amplitude
damping, and Kraus operator errors.

Key exports:
    - ErrorModel: Base class for all error models.
    - BitFlip: Bit-flip (X) error model.
    - PhaseFlip: Phase-flip (Z) error model.
    - Depolarizing: Single-qubit depolarizing channel.
    - TwoQubitDepolarizing: Two-qubit depolarizing channel.
    - AmplitudeDamping: Amplitude damping (T1) error model.
    - PauliError1Q: Single-qubit Pauli error model.
    - PauliError2Q: Two-qubit Pauli error model.
    - Kraus1Q: Single-qubit Kraus operator error model.
    - ErrorLoader: Base error loader interface.
    - ErrorLoader_GenericError: Generic error loader.
    - ErrorLoader_GateTypeError: Gate-type specific error loader.
    - ErrorLoader_GateSpecificError: Gate-specific error loader.
"""

from __future__ import annotations

__all__ = [
    "ErrorModel",
    "BitFlip",
    "PhaseFlip",
    "Depolarizing",
    "TwoQubitDepolarizing",
    "AmplitudeDamping",
    "PauliError1Q",
    "PauliError2Q",
    "Kraus1Q",
    "ErrorLoader",
    "ErrorLoader_GenericError",
    "ErrorLoader_GateTypeError",
    "ErrorLoader_GateSpecificError",
]

from typing import Any

# Opcode type: (gate_name, qubits, params, prob, None, None)
OpCode = tuple[str, int | list[int], Any, float | tuple[float, float, float] | list[complex] | None, None, None]


class ErrorModel:
    """Base class for quantum error models."""

    def __init__(self) -> None: ...

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        """Generate error opcodes for the given qubits.

        Args:
            qubits: Qubit or list of qubits to apply error to.

        Returns:
            List of error opcodes.
        """
        ...


class BitFlip(ErrorModel):
    """Bit-flip error model.

    Args:
        p: Bit-flip probability.
    """
    p: float

    def __init__(self, p: float) -> None:
        self.p = p

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        """Generate BitFlip error opcodes for the given qubits.

        Args:
            qubits: Qubit or list of qubits to apply error to.

        Returns:
            List of error opcodes.
        """
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("BitFlip", q, None, self.p, None, None) for q in qubits]


class PhaseFlip(ErrorModel):
    """Phase-flip (Z) error model.

    Args:
        p: Phase-flip probability.
    """
    p: float

    def __init__(self, p: float) -> None:
        self.p = p

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        """Generate PhaseFlip error opcodes for the given qubits.

        Args:
            qubits: Qubit or list of qubits to apply error to.

        Returns:
            List of error opcodes.
        """
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("PhaseFlip", q, None, self.p, None, None) for q in qubits]


class Depolarizing(ErrorModel):
    """Depolarizing error model for single qubits.

    Args:
        p: Depolarizing probability.
    """
    p: float

    def __init__(self, p: float) -> None:
        self.p = p

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        """Generate Depolarizing error opcodes for the given qubits.

        Args:
            qubits: Qubit or list of qubits to apply error to.

        Returns:
            List of error opcodes.
        """
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("Depolarizing", q, None, self.p, None, None) for q in qubits]


class TwoQubitDepolarizing(ErrorModel):
    """Two-qubit depolarizing error model.

    Args:
        p: Depolarizing probability.
    """
    p: float

    def __init__(self, p: float) -> None:
        self.p = p

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        """Generate TwoQubitDepolarizing error opcodes for the given qubit pair.

        Args:
            qubits: List of exactly two qubits.

        Returns:
            List of error opcodes.

        Raises:
            ValueError: If not exactly two qubits are provided.
        """
        if not isinstance(qubits, list) or len(qubits) != 2:
            raise ValueError("TwoQubitDepolarizing error model requires two qubits")
        return [("TwoQubitDepolarizing", q, None, self.p, None, None) for q in qubits]


class AmplitudeDamping(ErrorModel):
    """Amplitude damping error model.

    Args:
        gamma: Damping rate (0 to 1).
    """
    gamma: float

    def __init__(self, gamma: float) -> None:
        self.gamma = gamma

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        """Generate AmplitudeDamping error opcodes for the given qubits.

        Args:
            qubits: Qubit or list of qubits to apply error to.

        Returns:
            List of error opcodes.
        """
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("AmplitudeDamping", q, None, self.gamma, None, None) for q in qubits]


class PauliError1Q(ErrorModel):
    """Single-qubit Pauli error model with independent X, Y, Z probabilities.

    Args:
        p_x: Probability of X error.
        p_y: Probability of Y error.
        p_z: Probability of Z error.
    """
    p_x: float
    p_y: float
    p_z: float

    def __init__(self, p_x: float, p_y: float, p_z: float) -> None:
        self.p_x = p_x
        self.p_y = p_y
        self.p_z = p_z

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        """Generate PauliError1Q opcodes for the given qubits.

        Args:
            qubits: Qubit or list of qubits to apply error to.

        Returns:
            List of error opcodes.
        """
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("PauliError1Q", q, None, (self.p_x, self.p_y, self.p_z), None, None) for q in qubits]


class PauliError2Q(ErrorModel):
    """Two-qubit Pauli error model with 15 independent probabilities.

    Args:
        ps: List of 15 Pauli error probabilities.
    """
    ps: list[float]

    def __init__(self, ps: list[float]) -> None:
        self.ps = ps

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        """Generate PauliError2Q opcodes for the given qubit pair.

        Args:
            qubits: List of exactly two qubits.

        Returns:
            List of error opcodes.

        Raises:
            ValueError: If not exactly two qubits are provided.
        """
        if not isinstance(qubits, list) or len(qubits) != 2:
            raise ValueError("PauliError2Q error model requires two qubits")
        return [("PauliError2Q", q, None, self.ps, None, None) for q in qubits]


class Kraus1Q(ErrorModel):
    """Single-qubit Kraus operator error model.

    Args:
        kraus_ops: List of Kraus operators (2x2 matrices).
    """
    kraus_ops: list[list[complex]]

    def __init__(self, kraus_ops: list[list[complex]]) -> None:
        self.kraus_ops = kraus_ops

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        """Generate Kraus1Q error opcodes for the given qubits.

        Args:
            qubits: Qubit or list of qubits to apply error to.

        Returns:
            List of error opcodes.
        """
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("Kraus1Q", q, None, self.kraus_ops, None, None) for q in qubits]


class ErrorLoader:
    """Load opcodes into the simulator with noise models.

    Base class that inserts error opcodes into the program.
    """

    opcodes: list[OpCode]

    def __init__(self) -> None:
        self.opcodes = []

    def insert_error(self, opcode: OpCode) -> None:
        """Insert error opcodes for the given opcode. Override in subclasses."""
        ...

    def insert_opcode(self, opcode: OpCode) -> None:
        """Append the original opcode and insert associated errors."""
        self.opcodes.append(opcode)
        self.insert_error(opcode)

    def process_opcodes(self, opcodes: list[OpCode]) -> None:
        """Process a list of opcodes, inserting errors for each."""
        for opcode in opcodes:
            self.insert_opcode(opcode)


class ErrorLoader_GenericError(ErrorLoader):
    """Load opcodes with generic (gate-independent) noise.

    Applies the same set of error models to every gate.
    """

    generic_error: list[ErrorModel]

    def __init__(self, generic_error: list[ErrorModel]) -> None:
        super().__init__()
        self.generic_error = generic_error if generic_error else []

    def insert_error(self, opcode: OpCode) -> None:
        """Insert generic errors for the given opcode."""
        _, qubits, _, _, _, _ = opcode
        for noise_model in self.generic_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)


class ErrorLoader_GateTypeError(ErrorLoader_GenericError):
    """Load opcodes with gate-dependent noise.

    Supports both generic errors (applied to all gates) and per-gate-type
    errors (applied only to specific gate types).
    """

    gatetype_error: dict[str, list[ErrorModel]]

    def __init__(
        self,
        generic_error: list[ErrorModel],
        gatetype_error: dict[str, list[ErrorModel]],
    ) -> None:
        super().__init__(generic_error)
        self.gatetype_error = gatetype_error if gatetype_error else {}

    def insert_error(self, opcode: OpCode) -> None:
        """Insert generic and gate-type-specific errors for the given opcode."""
        gate, qubits, _, _, _, _ = opcode
        for noise_model in self.generic_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)
        gate_error = self.gatetype_error.get(gate, [])
        for noise_model in gate_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)


class ErrorLoader_GateSpecificError(ErrorLoader_GateTypeError):
    """Load opcodes with gate-specific noise (including per qubit-pair).

    Supports generic errors, per-gate-type errors, and per-gate-instance
    errors (keyed by gate name and specific qubit(s)).
    """

    gate_specific_error: dict[tuple[str, tuple[int, int]], list[ErrorModel]]

    def __init__(
        self,
        generic_error: list[ErrorModel],
        gatetype_error: dict[str, list[ErrorModel]],
        gate_specific_error: dict[tuple[str, tuple[int, int]], list[ErrorModel]],
    ) -> None:
        super().__init__(generic_error, gatetype_error)
        self.gate_specific_error = gate_specific_error if gate_specific_error else {}

    def insert_error(self, opcode: OpCode) -> None:
        """Insert generic, gate-type, and gate-specific errors for the given opcode."""
        gate, qubits, _, _, _, _ = opcode
        super().insert_error(opcode)
        if gate == "CZ":
            qubits = [min(qubits[0], qubits[1]), max(qubits[0], qubits[1])]
        if isinstance(qubits, list):
            qubits = tuple(qubits)
        key = (gate, qubits)
        gate_specific_error = self.gate_specific_error.get(key, [])
        for noise_model in gate_specific_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)
