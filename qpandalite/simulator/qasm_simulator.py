from typing import List, Tuple, TYPE_CHECKING
from qpandalite.qasm import OpenQASM2_BaseParser
import warnings
from .opcode_simulator import OpcodeSimulator
from .base_simulator import BaseSimulator
import numpy as np
if TYPE_CHECKING:
    from .QPandaLitePy import *

class QASM_Simulator(BaseSimulator):
    def __init__(self, backend_type = 'statevector',                                                  
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None):
        super().__init__(backend_type, available_qubits, available_topology)
        self.parser = OpenQASM2_BaseParser()

    def _clear(self):
        self.qubit_num = 0
        self.measure_qubit = []
        self.parser = OpenQASM2_BaseParser()
        self.opcode_simulator = OpcodeSimulator(self.backend_type)

    def simulate_pmeasure(self, qasm):
        program_body, measure_qubit = self.simulate_preprocess(qasm)
        
        prob_list = self.opcode_simulator.simulate_opcodes_stateprob(
            self.qubit_num, program_body
        )

        return prob_list
    
    def simulate_density_matrix(self, qasm):
        program_body, measure_qubit = self.simulate_preprocess(qasm)

        density_matrix = self.opcode_simulator.simulate_opcodes_density_operator(
            self.qubit_num, program_body
        )

        return density_matrix

    def simulate_statevector(self, qasm):
        program_body, measure_qubit = self.simulate_preprocess(qasm)

        statevector = self.opcode_simulator.simulate_opcodes_statevector(
            self.qubit_num, program_body
        )

        return statevector
    
    
    @property
    def simulator(self):
        return self.opcode_simulator.simulator

    @property
    def state(self):
        return self.opcode_simulator.simulator.state