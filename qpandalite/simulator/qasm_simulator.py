__all__ = ["QASM_Simulator", "QASM_Noisy_Simulator"]
from typing import Dict, List, Tuple, TYPE_CHECKING
from qpandalite.qasm import OpenQASM2_BaseParser
import warnings

from .error_model import ErrorLoader
from .opcode_simulator import OpcodeSimulator
from .base_simulator import BaseNoisySimulator, BaseSimulator
import numpy as np
if TYPE_CHECKING:
    from .qpandalite_cpp import *

class QASM_Simulator(BaseSimulator):
    """OpenQASM 2.0 quantum program simulator.

    Simulator for OpenQASM 2.0 format quantum programs.

    Args:
        backend_type: Backend type ("statevector" or "densitymatrix").
        available_qubits: List of available qubit indices (optional).
        available_topology: List of available qubit pairs (optional).
        least_qubit_remapping: Whether to remap qubits to least-available indices (default False).
        **extra_kwargs: Additional arguments passed to BaseSimulator.
    """

    def __init__(self, backend_type = 'statevector',                                                  
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None,
                 least_qubit_remapping = False, # QASM_Simulator's default is False
                 **extra_kwargs):
        super().__init__(backend_type, available_qubits, available_topology, 
                         least_qubit_remapping = least_qubit_remapping, 
                         **extra_kwargs)
        self.parser = OpenQASM2_BaseParser()

    def _clear(self):
        """Reset the simulator state."""
        self.qubit_num = 0
        self.measure_qubit = []
        self.parser = OpenQASM2_BaseParser()
        self.opcode_simulator = OpcodeSimulator(self.backend_type)

class QASM_Noisy_Simulator(BaseNoisySimulator):
    """Noisy OpenQASM 2.0 quantum program simulator.

    Simulator for OpenQASM 2.0 format quantum programs with noise model support.

    Args:
        backend_type: Backend type ("statevector" or "densitymatrix").
        available_qubits: List of available qubit indices (optional).
        available_topology: List of available qubit pairs (optional).
        error_loader: ErrorLoader instance for gate error injection (optional).
        readout_error: Dict mapping qubit index to [p0, p1] readout error rates (optional).
    """

    def __init__(self, backend_type = 'statevector',                                                  
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None,
                 error_loader : ErrorLoader = None,
                 readout_error : Dict[int, List[float]]={}):
        super().__init__(backend_type, available_qubits, available_topology,
                         error_loader, readout_error)
        self.parser = OpenQASM2_BaseParser()

    def _clear(self):
        """Reset the simulator state."""
        self.qubit_num = 0
        self.measure_qubit = []
        self.parser = OpenQASM2_BaseParser()
        self.opcode_simulator = OpcodeSimulator(self.backend_type)
