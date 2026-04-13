"""Thermal state preparation circuit."""

__all__ = ["thermal_state_circuit"]

from typing import List, Optional
import math

from qpandalite.circuit_builder import Circuit


def thermal_state_circuit(
    circuit: Circuit,
    beta: float,
    qubits: Optional[List[int]] = None,
) -> None:
    r"""Prepare a thermal state via single-qubit rotations.

    For the transverse-field-free Hamiltonian :math:`H = \sum_i Z_i`, the
    thermal (Gibbs) state at inverse temperature :math:`\beta` factorises
    into a product of single-qubit states.  Each qubit is prepared in

    .. math::

        \sqrt{p_0}\,|0\rangle + \sqrt{p_1}\,|1\rangle

    where

    .. math::

        p_0 = \frac{e^{\beta}}{e^{\beta}+e^{-\beta}}, \qquad
        p_1 = 1 - p_0.

    This is achieved by applying :math:`R_y(\theta)` with
    :math:`\theta = 2\arccos(\sqrt{p_0})` to every qubit independently.

    This is a lightweight, circuit-only counterpart of
    ``state_preparation.thermal_state`` for the default Hamiltonian case.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        beta: Inverse temperature (:math:`\beta > 0`).  Larger values
            bias the state towards :math:`|0\rangle`.
        qubits: Qubit indices to use.  ``None`` means all qubits of
            *circuit* (``list(range(circuit.qubit_num))``).

    Raises:
        ValueError: *beta* is negative.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import thermal_state_circuit
        >>> c = Circuit(3)
        >>> thermal_state_circuit(c, beta=1.0)
    """
    if beta < 0:
        raise ValueError(f"beta must be non-negative, got {beta}")

    if qubits is None:
        qubits = list(range(circuit.qubit_num))

    # Compute rotation angle: theta = 2 * arccos(sqrt(p0))
    # p0 = e^beta / (e^beta + e^{-beta})
    exp_beta = math.exp(beta)
    exp_neg_beta = math.exp(-beta)
    p0 = exp_beta / (exp_beta + exp_neg_beta)
    theta = 2.0 * math.acos(math.sqrt(p0))

    for q in qubits:
        circuit.ry(q, theta)
