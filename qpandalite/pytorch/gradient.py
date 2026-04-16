"""
Parameter-shift rule gradient computation for quantum circuits.

The parameter-shift rule allows exact gradient computation for parametric
quantum gates without finite differences. For gates with generator G:

    ∂⟨G(θ)⟩/∂θ = (⟨G(θ + π/2)⟩ - ⟨G(θ - π/2)⟩) / 2

This module provides functions to compute gradients for all parameters
in a parametric circuit.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from qpandalite.circuit_builder import Circuit

__all__ = ["parameter_shift_gradient", "compute_all_gradients"]


def parameter_shift_gradient(
    circuit: Circuit,
    param_name: str,
    expectation_fn: Callable[[Circuit], float],
    shift: float = np.pi / 2,
) -> float:
    """Compute gradient using the parameter-shift rule.

    For a parametric gate G(θ), the gradient of an expectation value is:

        ∂⟨G(θ)⟩/∂θ = 0.5 * (⟨G(θ + π/2)⟩ - ⟨G(θ - π/2)⟩)

    Args:
        circuit: Parametric circuit with the parameter
        param_name: Name of the parameter to differentiate
        expectation_fn: Function that computes expectation value from a circuit
        shift: Shift value (default π/2 for standard Pauli rotation gates)

    Returns:
        Gradient value

    Example:
        >>> def expectation(c):
        ...     # Simulate and compute <Z0>
        ...     sim.simulate(c.originir)
        ...     return sim.expectation([("Z", [0])])
        >>> grad = parameter_shift_gradient(circuit, "theta", expectation)
    """
    # Get base parameter value
    if not hasattr(circuit, "_parameters") or param_name not in circuit._parameters:
        raise ValueError(f"Parameter '{param_name}' not found in circuit")

    param = circuit._parameters[param_name]
    base_value = param._bound_value if param.is_bound() else 0.0

    # Plus shift circuit
    plus_circuit = circuit.copy()
    plus_circuit._parameters[param_name].bind(base_value + shift)

    # Minus shift circuit
    minus_circuit = circuit.copy()
    minus_circuit._parameters[param_name].bind(base_value - shift)

    # Compute expectations
    exp_plus = expectation_fn(plus_circuit)
    exp_minus = expectation_fn(minus_circuit)

    return 0.5 * (exp_plus - exp_minus)


def compute_all_gradients(
    circuit: Circuit,
    expectation_fn: Callable[[Circuit], float],
    shift: float = np.pi / 2,
) -> dict[str, float]:
    """Compute gradients for all parameters in a circuit.

    Uses the parameter-shift rule for each parameter independently.

    Args:
        circuit: Parametric circuit
        expectation_fn: Function that computes expectation value from a circuit
        shift: Shift value for parameter-shift rule

    Returns:
        Dictionary mapping parameter names to gradient values

    Example:
        >>> grads = compute_all_gradients(circuit, expectation)
        >>> print(grads)  # {'theta': 0.5, 'phi': -0.3}
    """
    gradients = {}

    if not hasattr(circuit, "_parameters"):
        return gradients

    for param_name in circuit._parameters:
        gradients[param_name] = parameter_shift_gradient(circuit, param_name, expectation_fn, shift)

    return gradients
