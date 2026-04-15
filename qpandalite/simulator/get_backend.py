"""Simulator backend factory for QPanda-lite.

This module provides a factory function to obtain appropriate simulator
instances based on the quantum program type (OriginIR or QASM).

Key exports:
    - get_backend: Factory function to create simulator backends.
"""

__all__ = ["get_backend"]
from .originir_simulator import OriginIR_Simulator
from .qasm_simulator import QASM_Simulator
from .base_simulator import BaseSimulator

def get_backend(program_type: str = "originir", backend_type: str = "statevector", **kwargs) -> BaseSimulator:
    """Get a simulator backend for the specified program type.

    Args:
        program_type: Type of quantum program ("originir" or "qasm").
        backend_type: Backend simulation type ("statevector" or "density_matrix").
        **kwargs: Additional arguments passed to the simulator constructor.

    Returns:
        A BaseSimulator instance for the given program type.

    Raises:
        ValueError: If program_type is not supported.
    """
    if program_type == "originir":
        return OriginIR_Simulator(backend_type=backend_type)

    elif program_type == "qasm":
        return QASM_Simulator(backend_type=backend_type)

    else:
        raise ValueError("Unsupported backend type: {}".format(program_type))