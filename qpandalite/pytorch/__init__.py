"""
PyTorch integration for quantum machine learning.

This module provides tools for integrating quantum circuits with PyTorch:
- Parameter-shift rule gradient computation
- QuantumLayer nn.Module for hybrid quantum-classical models
- Batch execution utilities
"""

from .batch_executor import batch_execute, batch_execute_with_params
from .gradient import compute_all_gradients, parameter_shift_gradient
from .quantum_layer import QuantumLayer

__all__ = [
    "parameter_shift_gradient",
    "compute_all_gradients",
    "QuantumLayer",
    "batch_execute",
    "batch_execute_with_params",
]
