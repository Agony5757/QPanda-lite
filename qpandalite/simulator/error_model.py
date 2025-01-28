# Error model

from typing import List

import numpy as np


class ErrorModel:
    def __init__(self):
        pass
    
    def generate_error_opcode(self, qubits):
        pass


class BitFlip(ErrorModel):
    def __init__(self, p):
        self.p = p
    
    def generate_error_opcode(self, qubits):
        if isinstance(qubits, int):
            qubits = [qubits]
        opcodes =[('BitFlip', qubit, self.p, None, None, None) for qubit in qubits]

        return opcodes
    
class PhaseFlip(ErrorModel):
    def __init__(self, p):
        self.p = p
    
    def generate_error_opcode(self, qubits):
        if isinstance(qubits, int):
            qubits = [qubits]
        opcodes =[('PhaseFlip', qubit, self.p, None, None, None) for qubit in qubits]

        return opcodes
    
class Depolarizing(ErrorModel):
    def __init__(self, p):
        self.p = p
    
    def generate_error_opcode(self, qubits):
        if isinstance(qubits, int):
            qubits = [qubits]
        opcodes =[('Depolarizing', qubit, self.p, None, None, None) for qubit in qubits]

        return opcodes
    
class TwoQubitDepolarizing(ErrorModel):
    def __init__(self, p):
        self.p = p
    
    def generate_error_opcode(self, qubits):
        if not isinstance(qubits, list) or len(qubits)!= 2:
            raise ValueError("TwoQubitDepolarizing error model requires two qubits")
        
        opcodes =[('TwoQubitDepolarizing', qubit, self.p, None, None, None) for qubit in qubits]

        return opcodes
    
class AmplitudeDamping(ErrorModel):
    def __init__(self, gamma):
        self.gamma = gamma
    
    def generate_error_opcode(self, qubits):
        if isinstance(qubits, int):
            qubits = [qubits]
        opcodes =[('AmplitudeDamping', qubit, self.gamma, None, None, None) for qubit in qubits]

        return opcodes
    
class PauliError1Q(ErrorModel):
    def __init__(self, p_x, p_y, p_z):
        self.p_x = p_x
        self.p_y = p_y
        self.p_z = p_z
    
    def generate_error_opcode(self, qubits):
        if isinstance(qubits, int):
            qubits = [qubits]
        opcodes =[('PauliError1Q', qubit, (self.p_x, self.p_y, self.p_z), None, None, None) for qubit in qubits]

        return opcodes
    
class PauliError2Q(ErrorModel):
    def __init__(self, ps: List[float]):
        self.ps = ps
    
    def generate_error_opcode(self, qubits):
        if not isinstance(qubits, list) or len(qubits)!= 2:
            raise ValueError("PauliError2Q error model requires two qubits")
        
        opcodes = [('PauliError2Q', qubit, self.ps, None, None, None) for qubit in qubits]

class Kraus1Q(ErrorModel):
    def __init__(self, kraus_ops: List[np.ndarray]):
        self.kraus_ops = kraus_ops

    def generate_error_opcode(self, qubits):
        if isinstance(qubits, int):
            qubits = [qubits]

        opcodes =[('Kraus1Q', qubit, self.kraus_ops, None, None, None) for qubit in qubits]
        return opcodes
