'''Opcode simulator, a fundamental simulator for QPanda-lite.
It simulates from a basic opcode
'''
from QPandaLitePy import *
from typing import List, Tuple, TYPE_CHECKING

import numpy as np
if TYPE_CHECKING:
    from .QPandaLitePy import *

class OpcodeSimulator:   
    def __init__(self):
        '''OpcodeSimulator is a quantum circuit simulation based on C++ which runs locally on your PC.

        Args:
            reverse_key (bool, optional): _description_. Defaults to False.
        '''
        self.qubit_num = None
        self.measure_qubit = None
        self.program_body = None
        self.simulator = Simulator()
        
    def _clear(self):
        self.simulator = Simulator()  

    def _simulate_common_gate(self, operation, qubit, cbit, parameter, control_qubits_set, is_dagger):
        if operation == 'RX':
            self.simulator.rx(qubit, parameter, control_qubits_set, is_dagger)
        elif operation == 'RY':
            self.simulator.ry(qubit, parameter, control_qubits_set, is_dagger)
        elif operation == 'RZ':
            self.simulator.rz(qubit, parameter, control_qubits_set, is_dagger)
        elif operation == 'U1':
            self.simulator.u1(qubit, parameter, control_qubits_set, is_dagger)
        elif operation == 'H':
            self.simulator.hadamard(qubit, control_qubits_set, is_dagger)
        elif operation == 'X':
            self.simulator.x(qubit, control_qubits_set, is_dagger)
        elif operation == 'SX':
            self.simulator.sx(qubit, control_qubits_set, is_dagger)
        elif operation == 'Y':
            self.simulator.y(qubit, control_qubits_set, is_dagger)
        elif operation == 'Z':
            self.simulator.z(qubit, control_qubits_set, is_dagger)
        elif operation == 'S':
            self.simulator.s(qubit, control_qubits_set, is_dagger)
        elif operation == 'T':
            self.simulator.t(qubit, control_qubits_set, is_dagger)
        elif operation == 'CZ':
            self.simulator.cz(qubit[0], 
                            qubit[1], control_qubits_set, is_dagger)
        elif operation == 'SWAP':
            self.simulator.swap(qubit[0], 
                                qubit[1], control_qubits_set, is_dagger)
        elif operation == 'ISWAP':
            self.simulator.iswap(qubit[0], 
                                qubit[1], control_qubits_set, is_dagger)
        elif operation == 'TOFFOLI':
            self.simulator.toffoli(qubit[0], 
                                qubit[1], 
                                qubit[2], control_qubits_set, is_dagger)
        elif operation == 'CSWAP':
            self.simulator.cswap(qubit[0], 
                                qubit[1], 
                                qubit[2], control_qubits_set, is_dagger)
        elif operation == 'XY':
            self.simulator.xy(qubit[0], 
                                qubit[1], control_qubits_set, is_dagger)
        elif operation == 'CNOT':
            self.simulator.cnot(qubit[0], 
                                qubit[1], control_qubits_set, is_dagger)
        elif operation == 'RPhi':
            self.simulator.rphi(qubit, 
                                parameter[0], parameter[1], control_qubits_set, is_dagger)  
        elif operation == 'RPhi90':
            self.simulator.rphi90(qubit, 
                                parameter[0], parameter[1], control_qubits_set, is_dagger)  
        elif operation == 'RPhi180':
            self.simulator.rphi180(qubit, 
                                parameter[0], parameter[1], control_qubits_set, is_dagger) 
        elif operation == 'U3':
            self.simulator.u3(qubit, 
                                parameter[0], parameter[1], parameter[2], control_qubits_set, is_dagger) 
        elif operation == 'XX':
            self.simulator.xx(qubit[0],
                              qubit[1],
                              parameter, control_qubits_set, is_dagger) 
        elif operation == 'YY':
            self.simulator.yy(qubit[0],
                              qubit[1],
                              parameter, control_qubits_set, is_dagger) 
        elif operation == 'ZZ':
            self.simulator.zz(qubit[0],
                              qubit[1],
                              parameter, control_qubits_set, is_dagger)
        elif operation == 'UU15':
            self.simulator.uu15(qubit[0],
                                qubit[1],
                                parameter, control_qubits_set, is_dagger)
        elif operation == 'PHASE2Q':
            self.simulator.phase2q(qubit[0], qubit[1],
                parameter[0], parameter[1], parameter[2], 
                control_qubits_set, is_dagger)
        elif operation == 'I':
            pass
        elif operation == None:
            pass
        elif operation == 'QINIT':
            pass
        elif operation == 'CREG':
            pass
        elif operation == 'BARRIER':
            pass
        else:
            raise RuntimeError('Unknown Opcode operation. '
                                f'Operation: {operation}.'
                                f'Full opcode: {(operation, qubit, cbit, parameter, control_qubits_set, is_dagger)}')

    def simulate_gate(self, operation, qubit, cbit, parameter, is_dagger, control_qubits_set):
        # convert from set to list (to adapt to C++ input)
        if control_qubits_set:
            control_qubits_set = list(control_qubits_set)
        else:
            control_qubits_set = list()

        self._simulate_common_gate(operation, qubit, cbit, parameter, control_qubits_set, is_dagger)    

    def simulate_opcodes_pmeasure(self, n_qubit, program_body, measure_qubits):
        self.simulator.init_n_qubit(n_qubit)
        for opcode in program_body:
            operation, qubit, cbit, parameter, control_qubits_set, is_dagger = opcode
            self.simulate_gate(operation, qubit, cbit, parameter, control_qubits_set, is_dagger)
        
        prob_list = self.simulator.pmeasure(measure_qubits)
        return prob_list
    
    def simulate_opcodes_statevector(self, n_qubit, program_body):
        self.simulator.init_n_qubit(n_qubit)
        for opcode in program_body:
            operation, qubit, cbit, parameter, control_qubits_set, is_dagger = opcode
            self.simulate_gate(operation, qubit, cbit, parameter, control_qubits_set, is_dagger)
        
        statevector = self.simulator.state
        return statevector
    
    def simulate_opcodes_stateprob(self, n_qubit, program_body):
        statevector = self.simulate_opcodes_statevector(n_qubit, program_body)
        statevector = np.array(statevector)
        return np.abs(statevector) ** 2
        

