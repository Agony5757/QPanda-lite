"""
QuantumLayer: PyTorch nn.Module for quantum circuits.

This module provides a PyTorch-compatible layer that wraps a parametric
quantum circuit, enabling gradient-based optimization via the parameter-shift
rule.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy as np

try:
    import torch
    import torch.nn as nn

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

    # Create placeholder classes for type hints
    class nn:  # type: ignore
        class Module:
            pass

    torch = None  # type: ignore

if TYPE_CHECKING:
    from qpandalite.circuit_builder import Circuit

__all__ = ["QuantumLayer"]


if TORCH_AVAILABLE:

    class _QuantumFunction(torch.autograd.Function):
        """Custom autograd function using parameter-shift rule."""

        @staticmethod
        def forward(ctx, params, circuit_template, expectation_fn, param_names, shift):
            ctx.save_for_backward(params)
            ctx.circuit_template = circuit_template
            ctx.expectation_fn = expectation_fn
            ctx.param_names = param_names
            ctx.shift = shift

            # Create bound circuit
            param_values = params.detach().numpy()
            bound_circuit = circuit_template.copy()

            for name, value in zip(param_names, param_values, strict=True):
                if name in bound_circuit._parameters:
                    bound_circuit._parameters[name].bind(float(value))

            result = expectation_fn(bound_circuit)
            return torch.tensor([result], dtype=params.dtype)

        @staticmethod
        def backward(ctx, grad_output):
            (params,) = ctx.saved_tensors
            circuit_template = ctx.circuit_template
            expectation_fn = ctx.expectation_fn
            param_names = ctx.param_names
            shift = ctx.shift

            param_values = params.detach().numpy()
            param_grads = []

            for i, _name in enumerate(param_names):
                # Plus shift
                plus_circuit = circuit_template.copy()
                for j, n in enumerate(param_names):
                    val = param_values[j] + (shift if j == i else 0.0)
                    if n in plus_circuit._parameters:
                        plus_circuit._parameters[n].bind(float(val))
                exp_plus = expectation_fn(plus_circuit)

                # Minus shift
                minus_circuit = circuit_template.copy()
                for j, n in enumerate(param_names):
                    val = param_values[j] - (shift if j == i else 0.0)
                    if n in minus_circuit._parameters:
                        minus_circuit._parameters[n].bind(float(val))
                exp_minus = expectation_fn(minus_circuit)

                grad = 0.5 * (exp_plus - exp_minus)
                param_grads.append(grad)

            grad_params = torch.tensor(param_grads, dtype=params.dtype) * grad_output
            return grad_params, None, None, None, None

    class QuantumLayer(nn.Module):
        """PyTorch layer wrapping a parametric quantum circuit.

        Supports automatic differentiation via the parameter-shift rule
        for gradient-based optimization.

        Args:
            circuit: Parametric Circuit or template with _parameters
            expectation_fn: Function computing expectation from a bound circuit
            n_outputs: Number of output values (default: 1)
            init_params: Initial parameter values (optional)
            shift: Shift value for parameter-shift rule (default: π/2)

        Example:
            >>> @circuit_def(name="vqe", qregs={"q": 2}, params=["theta"])
            ... def vqe_circuit(circ, q, theta):
            ...     circ.ry(q[0], theta[0])
            ...     circ.cnot(q[0], q[1])
            ...     return circ
            >>>
            >>> qlayer = QuantumLayer(
            ...     circuit=vqe_circuit.build_standalone(),
            ...     expectation_fn=lambda c: simulate_and_measure(c)
            ... )
            >>> optimizer = torch.optim.Adam(qlayer.parameters(), lr=0.01)
        """

        def __init__(
            self,
            circuit: Circuit,
            expectation_fn: Callable[[Circuit], float],
            n_outputs: int = 1,
            init_params: torch.Tensor | None = None,
            shift: float = np.pi / 2,
        ):
            super().__init__()
            self._circuit_template = circuit
            self._expectation_fn = expectation_fn
            self._n_outputs = n_outputs
            self._shift = shift

            # Get parameter info from circuit
            if hasattr(circuit, "_parameters"):
                self._param_names = list(circuit._parameters.keys())
                n_params = len(self._param_names)
            else:
                self._param_names = []
                n_params = 0

            # Initialize trainable parameters
            if init_params is not None:
                self.params = nn.Parameter(init_params.clone())
            else:
                self.params = nn.Parameter(torch.randn(n_params) * 0.1)

        def forward(self, x: torch.Tensor | None = None) -> torch.Tensor:
            """Execute the quantum circuit and return expectation values.

            Args:
                x: Optional input tensor (for data encoding circuits)

            Returns:
                Tensor of expectation values
            """
            return _QuantumFunction.apply(
                self.params,
                self._circuit_template,
                self._expectation_fn,
                self._param_names,
                self._shift,
            )

        def extra_repr(self) -> str:
            return f"n_params={len(self._param_names)}, n_outputs={self._n_outputs}"

else:
    # Placeholder when PyTorch is not available
    class QuantumLayer:  # type: ignore
        """Placeholder when PyTorch is not installed."""

        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is not installed. Install with: pip install qpandalite[pytorch]")
