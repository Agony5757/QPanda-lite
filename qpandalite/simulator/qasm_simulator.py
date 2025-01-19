from typing import List, Tuple, TYPE_CHECKING
from qpandalite.qasm import OpenQASM2_BaseParser
import warnings
from .opcode_simulator import OpcodeSimulator

import numpy as np
if TYPE_CHECKING:
    from .QPandaLitePy import *

class QASM_Simulator:
    def __init__(self):
        self.qubit_num = 0
        self.measure_qubit = []
        self.parser = OpenQASM2_BaseParser()
        self.opcode_simulator = OpcodeSimulator()

    def _clear(self):    
        self.qubit_num = 0
        self.measure_qubit = []
        self.parser = OpenQASM2_BaseParser()
        self.opcode_simulator = OpcodeSimulator()

    def _simulate_preprocess(self, qasm):
        self._clear()
        self.parser.parse(qasm)

        # extract measurements
        measurements = self.parser.measure_qubit
        # currently we do not need to measure

        self.qubit_num = self.parser.n_qubit
        program_body = self.parser.program_body

        return program_body


    def simulate(self, qasm):
        program_body = self._simulate_preprocess(qasm)
        
        prob_list = self.opcode_simulator.simulate_opcodes_stateprob(
            self.qubit_num, program_body
        )

        return prob_list
    
    
    @property
    def simulator(self):
        return self.opcode_simulator.simulator

    @property
    def state(self):
        return self.opcode_simulator.simulator.state