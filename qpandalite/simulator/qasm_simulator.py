from typing import List, Tuple, TYPE_CHECKING
from qpandalite.qasm import OpenQASM2_BaseParser
import warnings
from .opcode_simulator import OpcodeSimulator
from .base_simulator import BaseSimulator
import numpy as np
if TYPE_CHECKING:
    from .QPandaLitePy import *

class QASM_Simulator(BaseSimulator):
    def __init__(self, backend_type = 'statevector'):
        self.qubit_num = 0
        self.measure_qubit = []
        self.parser = OpenQASM2_BaseParser()
        self.backend_type = backend_type
        self.opcode_simulator = OpcodeSimulator(self.backend_type)

    def _clear(self):
        self.qubit_num = 0
        self.measure_qubit = []
        self.parser = OpenQASM2_BaseParser()
        self.opcode_simulator = OpcodeSimulator(self.backend_type)

    def _simulate_preprocess(self, qasm):
        self._clear()
        self.parser.parse(qasm)

        # extract measurements
        measurements = self.parser.measure_qubit
        # currently we do not need to measure

        self.qubit_num = self.parser.n_qubit
        program_body = self.parser.program_body

        return program_body

    def simulate_pmeasure(self, qasm):
        program_body = self._simulate_preprocess(qasm)
        
        prob_list = self.opcode_simulator.simulate_opcodes_stateprob(
            self.qubit_num, program_body
        )

        return prob_list
    
    def simulate_density_matrix(self, qasm):
        program_body = self._simulate_preprocess(qasm)

        density_matrix = self.opcode_simulator.simulate_opcodes_density_operator(
            self.qubit_num, program_body
        )

        return density_matrix

    def simulate_statevector(self, qasm):
        program_body = self._simulate_preprocess(qasm)

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