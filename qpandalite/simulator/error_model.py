# Error model

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
    def __init__(self) -> None: ...

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]: ...


class BitFlip(ErrorModel):
    p: float

    def __init__(self, p: float) -> None:
        self.p = p

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("BitFlip", q, None, self.p, None, None) for q in qubits]


class PhaseFlip(ErrorModel):
    p: float

    def __init__(self, p: float) -> None:
        self.p = p

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("PhaseFlip", q, None, self.p, None, None) for q in qubits]


class Depolarizing(ErrorModel):
    p: float

    def __init__(self, p: float) -> None:
        self.p = p

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("Depolarizing", q, None, self.p, None, None) for q in qubits]


class TwoQubitDepolarizing(ErrorModel):
    p: float

    def __init__(self, p: float) -> None:
        self.p = p

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        if not isinstance(qubits, list) or len(qubits) != 2:
            raise ValueError("TwoQubitDepolarizing error model requires two qubits")
        return [("TwoQubitDepolarizing", q, None, self.p, None, None) for q in qubits]


class AmplitudeDamping(ErrorModel):
    gamma: float

    def __init__(self, gamma: float) -> None:
        self.gamma = gamma

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("AmplitudeDamping", q, None, self.gamma, None, None) for q in qubits]


class PauliError1Q(ErrorModel):
    p_x: float
    p_y: float
    p_z: float

    def __init__(self, p_x: float, p_y: float, p_z: float) -> None:
        self.p_x = p_x
        self.p_y = p_y
        self.p_z = p_z

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("PauliError1Q", q, None, (self.p_x, self.p_y, self.p_z), None, None) for q in qubits]


class PauliError2Q(ErrorModel):
    ps: list[float]

    def __init__(self, ps: list[float]) -> None:
        self.ps = ps

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        if not isinstance(qubits, list) or len(qubits) != 2:
            raise ValueError("PauliError2Q error model requires two qubits")
        return [("PauliError2Q", q, None, self.ps, None, None) for q in qubits]


class Kraus1Q(ErrorModel):
    kraus_ops: list[list[complex]]

    def __init__(self, kraus_ops: list[list[complex]]) -> None:
        self.kraus_ops = kraus_ops

    def generate_error_opcode(self, qubits: int | list[int]) -> list[OpCode]:
        if isinstance(qubits, int):
            qubits = [qubits]
        return [("Kraus1Q", q, None, self.kraus_ops, None, None) for q in qubits]


class ErrorLoader:
    """Load opcodes into the simulator with noise models."""

    opcodes: list[OpCode]

    def __init__(self) -> None:
        self.opcodes = []

    def insert_error(self, opcode: OpCode) -> None: ...

    def insert_opcode(self, opcode: OpCode) -> None:
        self.opcodes.append(opcode)
        self.insert_error(opcode)

    def process_opcodes(self, opcodes: list[OpCode]) -> None:
        for opcode in opcodes:
            self.insert_opcode(opcode)


class ErrorLoader_GenericError(ErrorLoader):
    """Load opcodes with generic (gate-independent) noise."""

    generic_error: list[ErrorModel]

    def __init__(self, generic_error: list[ErrorModel]) -> None:
        super().__init__()
        self.generic_error = generic_error if generic_error else []

    def insert_error(self, opcode: OpCode) -> None:
        _, qubits, _, _, _, _ = opcode
        for noise_model in self.generic_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)


class ErrorLoader_GateTypeError(ErrorLoader_GenericError):
    """Load opcodes with gate-dependent noise."""

    gatetype_error: dict[str, list[ErrorModel]]

    def __init__(
        self,
        generic_error: list[ErrorModel],
        gatetype_error: dict[str, list[ErrorModel]],
    ) -> None:
        super().__init__(generic_error)
        self.gatetype_error = gatetype_error if gatetype_error else {}

    def insert_error(self, opcode: OpCode) -> None:
        gate, qubits, _, _, _, _ = opcode
        for noise_model in self.generic_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)
        gate_error = self.gatetype_error.get(gate, [])
        for noise_model in gate_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)


class ErrorLoader_GateSpecificError(ErrorLoader_GateTypeError):
    """Load opcodes with gate-specific noise (including per qubit-pair)."""

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
