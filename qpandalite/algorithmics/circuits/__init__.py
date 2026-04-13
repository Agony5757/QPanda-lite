"""Circuits module — reusable quantum circuit building blocks."""

__all__ = [
    "qft_circuit",
    "deutsch_jozsa_circuit",
    "deutsch_jozsa_oracle",
    "thermal_state_circuit",
    "dicke_state_circuit",
    "grover_oracle",
    "grover_diffusion",
    "vqd_circuit",
    "vqd_overlap_circuit",
    "amplitude_estimation_circuit",
    "amplitude_estimation_result",
    "grover_operator",
    "ghz_state",
    "w_state",
    "cluster_state",
]

from .qft import qft_circuit
from .deutsch_jozsa import deutsch_jozsa_circuit, deutsch_jozsa_oracle
from .thermal_state import thermal_state_circuit
from .dicke_state import dicke_state_circuit
from .grover_oracle import grover_oracle, grover_diffusion
from .vqd import vqd_circuit, vqd_overlap_circuit
from .amplitude_estimation import amplitude_estimation_circuit, amplitude_estimation_result, grover_operator
from .entangled_states import ghz_state, w_state, cluster_state
