"""
Named circuit definitions for reusable quantum subroutines.

This module provides:
- @circuit_def: Decorator to create named circuit definitions
- NamedCircuit: Reusable circuit definition with signature

Named circuits can be applied to parent circuits with qubit mapping
and parameter binding, similar to QASM3 gate definitions.

Example usage:
    @circuit_def(name="bell_pair", qregs={"q": 2})
    def bell_pair(circ, q):
        circ.h(q[0])
        circ.cnot(q[0], q[1])
        return circ

    # Apply to parent circuit
    c = Circuit(qregs={"data": 4})
    bell_pair(c, qreg_mapping={"q": [c.get_qreg("data")[0], c.get_qreg("data")[1]]})
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from .qcircuit import Circuit

if TYPE_CHECKING:
    from .qubit import QReg, QRegSlice, Qubit

__all__ = ["circuit_def", "NamedCircuit"]


class NamedCircuit:
    """Reusable circuit definition with named qregs and parameters.

    A NamedCircuit is a template for a quantum subroutine that can be
    instantiated multiple times with different qubit mappings and
    parameter values.

    Attributes:
        name: Circuit definition name
        qregs: Dictionary mapping qreg names to sizes
        params: List of parameter names
        builder: Function that builds the circuit body

    Example:
        >>> @circuit_def(name="u3", qregs={"q": 1}, params=["theta", "phi", "lam"])
        ... def u3_gate(circ, q, theta, phi, lam):
        ...     circ.rz(q[0], phi)
        ...     circ.ry(q[0], theta)
        ...     circ.rz(q[0], lam)
        ...     return circ
        ...
        >>> u3_gate.num_qubits  # 1
        >>> u3_gate.num_parameters  # 3
    """

    def __init__(
        self,
        name: str,
        qregs: dict[str, int] | list[str] | None = None,
        params: list[str] | None = None,
        builder: Callable | None = None,
    ) -> None:
        """Initialize a NamedCircuit.

        Args:
            name: Circuit definition name
            qregs: Qubit register specification (dict or list of names with size 1)
            params: Parameter names
            builder: Function that builds the circuit body
        """
        self._name = name

        # Normalize qregs to dict
        if qregs is None:
            self._qregs: dict[str, int] = {}
        elif isinstance(qregs, dict):
            self._qregs = qregs
        elif isinstance(qregs, list):
            # Each name gets size 1
            self._qregs = dict.fromkeys(qregs, 1)
        else:
            self._qregs = {}

        self._params = params or []
        self._builder = builder

    @property
    def name(self) -> str:
        return self._name

    @property
    def qregs(self) -> dict[str, int]:
        return self._qregs

    @property
    def params(self) -> list[str]:
        return self._params

    @property
    def num_qubits(self) -> int:
        """Total number of qubits used by this circuit."""
        return sum(self._qregs.values())

    @property
    def num_parameters(self) -> int:
        """Number of parameters."""
        return len(self._params)

    def __call__(
        self,
        circuit: Circuit,
        qreg_mapping: dict[str, QReg | QRegSlice | Qubit | list[int] | list[Qubit]] | None = None,
        param_values: dict[str, float] | list[float] | None = None,
    ) -> Circuit:
        """Apply this circuit definition to a parent circuit.

        Args:
            circuit: Parent circuit to add gates to
            qreg_mapping: Map this circuit's qreg names to parent qubits
                - QReg: Use entire register
                - QRegSlice: Use slice of register
                - Qubit: Use single qubit
                - List[int]: Explicit qubit indices
                - List[Qubit]: List of Qubit objects
            param_values: Concrete values for parameters
                - dict: Mapping parameter names to values
                - list: Values in order of params list

        Returns:
            The modified parent circuit
        """
        if self._builder is None:
            raise ValueError(f"NamedCircuit '{self._name}' has no builder function")

        # Normalize qreg_mapping
        if qreg_mapping is None:
            qreg_mapping = {}

        # Resolve qreg mappings to concrete qubit references
        resolved_mapping: dict[str, list[int]] = {}
        for qreg_name, target in qreg_mapping.items():
            if isinstance(target, int):
                resolved_mapping[qreg_name] = [target]
            elif hasattr(target, "__iter__") and not isinstance(target, str):
                # QReg, QRegSlice, or list
                resolved = circuit._resolve_qubit(target)
                if isinstance(resolved, list):
                    resolved_mapping[qreg_name] = resolved
                else:
                    resolved_mapping[qreg_name] = [resolved]
            else:
                # Single Qubit
                resolved = circuit._resolve_qubit(target)
                resolved_mapping[qreg_name] = [resolved]

        # Normalize param_values
        if param_values is None:
            param_dict: dict[str, float] = {}
        elif isinstance(param_values, dict):
            param_dict = param_values
        else:
            # List - map to params in order
            if len(param_values) != len(self._params):
                raise ValueError(f"Expected {len(self._params)} parameters, got {len(param_values)}")
            param_dict = dict(zip(self._params, param_values, strict=True))

        # Create qreg proxies for the builder function
        from .qubit import QReg as QRegClass

        qreg_proxies: dict[str, QRegClass] = {}
        for qreg_name, indices in resolved_mapping.items():
            # Create a temporary QReg that maps to the resolved indices
            size = self._qregs.get(qreg_name, len(indices))
            # Create proxy with base_index=0, then manually set qubit resolution
            proxy = QRegClass(name=qreg_name, size=size, base_index=indices[0] if indices else 0)
            # Override the __getitem__ behavior by storing indices
            proxy._resolved_indices = indices  # type: ignore[attr-defined]
            qreg_proxies[qreg_name] = proxy

        # Create a wrapper circuit that maps qubits
        class QregProxyWrapper:
            """Wrapper that provides qreg access with resolved indices."""

            def __init__(self, indices: list[int]):
                self._indices = indices

            def __getitem__(self, key: int) -> int:
                return self._indices[key]

            def __len__(self) -> int:
                return len(self._indices)

        # Build argument list for builder
        # First arg is circuit, then qregs in order of qregs keys, then params
        builder_args = [circuit]

        # Add qreg proxies
        for qreg_name in self._qregs:
            if qreg_name in resolved_mapping:
                indices = resolved_mapping[qreg_name]
                proxy = QregProxyWrapper(indices)
                builder_args.append(proxy)
            else:
                raise ValueError(f"Missing qreg mapping for '{qreg_name}'")

        # Add parameter values
        for param_name in self._params:
            if param_name in param_dict:
                builder_args.append(param_dict[param_name])
            else:
                # Pass None for unbound parameters (may cause issues downstream)
                builder_args.append(None)

        # Call the builder
        self._builder(*builder_args)

        return circuit

    def build_standalone(
        self,
        param_values: dict[str, float] | list[float] | None = None,
    ) -> Circuit:
        """Build a standalone Circuit with this definition.

        Creates a new Circuit with qregs matching this definition's signature.

        Args:
            param_values: Optional parameter values

        Returns:
            A new Circuit instance
        """
        c = Circuit(qregs=self._qregs)
        # Apply this definition to the new circuit with default mapping
        # Use integer indices instead of QReg objects to avoid resolution issues
        qreg_mapping = {}
        offset = 0
        for name, size in self._qregs.items():
            qreg_mapping[name] = list(range(offset, offset + size))
            offset += size
        return self(c, qreg_mapping=qreg_mapping, param_values=param_values)

    def to_originir_def(self) -> str:
        """Export as OriginIR DEF block.

        Note: This is a placeholder. Full DEF export requires
        symbolic parameter support in OriginIR format.
        """
        lines = []
        # Header: DEF name(qreg_list) (param_list)
        qreg_str = ", ".join(f"q[{i}]" for i in range(self.num_qubits))
        if self._params:
            param_str = ", ".join(self._params)
            lines.append(f"DEF {self._name}({qreg_str}) ({param_str})")
        else:
            lines.append(f"DEF {self._name}({qreg_str})")

        # Build body circuit - use qreg_mapping with integer indices
        if self._builder:
            qreg_mapping = {}
            offset = 0
            for name, size in self._qregs.items():
                qreg_mapping[name] = list(range(offset, offset + size))
                offset += size

            c = Circuit(qregs=self._qregs)
            self(c, qreg_mapping=qreg_mapping)

            for line in c.originir.split("\n"):
                if line.startswith("QINIT") or line.startswith("CREG") or line.startswith("MEASURE"):
                    continue
                if line.strip():
                    lines.append(line)

        lines.append("ENDDEF")
        return "\n".join(lines)

    def __repr__(self) -> str:
        qregs_str = ", ".join(f"{k}:{v}" for k, v in self._qregs.items())
        params_str = ", ".join(self._params)
        return f"NamedCircuit({self._name!r}, qregs={{{qregs_str}}}, params=[{params_str}])"


def circuit_def(
    name: str,
    qregs: dict[str, int] | list[str] | None = None,
    params: list[str] | None = None,
) -> Callable:
    """Decorator to create a NamedCircuit definition.

    Args:
        name: Circuit definition name
        qregs: Qubit register specification
            - dict: {name: size} pairs
            - list: Names (each with size 1)
        params: Parameter names

    Returns:
        Decorator that wraps a function into a NamedCircuit

    Example:
        >>> @circuit_def(name="bell_pair", qregs={"q": 2})
        ... def bell_pair(circ, q):
        ...     circ.h(q[0])
        ...     circ.cnot(q[0], q[1])
        ...     return circ
        ...
        >>> c = Circuit(2)
        >>> bell_pair(c, qreg_mapping={"q": [0, 1]})
    """

    def decorator(func: Callable) -> NamedCircuit:
        return NamedCircuit(
            name=name,
            qregs=qregs,
            params=params,
            builder=func,
        )

    return decorator
