from typing import Dict, List, Tuple, TYPE_CHECKING
from qpandalite.qasm import OpenQASM2_BaseParser
import warnings

from .error_model import ErrorLoader
from .opcode_simulator import OpcodeSimulator
from .base_simulator import BaseNoisySimulator, BaseSimulator
import numpy as np
if TYPE_CHECKING:
    from .QPandaLitePy import *

class QASM_Simulator(BaseSimulator):
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
        self.qubit_num = 0
        self.measure_qubit = []
        self.parser = OpenQASM2_BaseParser()
        self.opcode_simulator = OpcodeSimulator(self.backend_type)

class QASM_Noisy_Simulator(BaseNoisySimulator):
    def __init__(self, backend_type = 'statevector',                                                  
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None,
                 error_loader : ErrorLoader = None,
                 readout_error : Dict[int, List[float]]={}):
        super().__init__(backend_type, available_qubits, available_topology,
                         error_loader, readout_error)
        self.parser = OpenQASM2_BaseParser()

    def _clear(self):
        self.qubit_num = 0
        self.measure_qubit = []
        self.parser = OpenQASM2_BaseParser()
        self.opcode_simulator = OpcodeSimulator(self.backend_type)
