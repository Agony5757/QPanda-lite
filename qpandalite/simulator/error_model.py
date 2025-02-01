# Error model

from typing import Dict, List, Tuple
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

        opcodes = [('BitFlip', qubit, None, self.p, None, None) for qubit in qubits]
        return opcodes
    
class PhaseFlip(ErrorModel):
    def __init__(self, p):
        self.p = p
    
    def generate_error_opcode(self, qubits):
        if isinstance(qubits, int):
            qubits = [qubits]

        opcodes =[('PhaseFlip', qubit, None, self.p, None, None) for qubit in qubits]
        return opcodes
    
class Depolarizing(ErrorModel):
    def __init__(self, p):
        self.p = p
    
    def generate_error_opcode(self, qubits):
        if isinstance(qubits, int):
            qubits = [qubits]

        opcodes =[('Depolarizing', qubit, None, self.p, None, None) for qubit in qubits]
        return opcodes
    
class TwoQubitDepolarizing(ErrorModel):
    def __init__(self, p):
        self.p = p
    
    def generate_error_opcode(self, qubits):
        if not isinstance(qubits, list) or len(qubits)!= 2:
            raise ValueError("TwoQubitDepolarizing error model requires two qubits")
        
        opcodes =[('TwoQubitDepolarizing', qubit, None, self.p, None, None) for qubit in qubits]
        return opcodes
    
class AmplitudeDamping(ErrorModel):
    def __init__(self, gamma):
        self.gamma = gamma
    
    def generate_error_opcode(self, qubits):
        if isinstance(qubits, int):
            qubits = [qubits]

        opcodes =[('AmplitudeDamping', qubit, None, self.gamma, None, None) for qubit in qubits]
        return opcodes
    
class PauliError1Q(ErrorModel):
    def __init__(self, p_x, p_y, p_z):
        self.p_x = p_x
        self.p_y = p_y
        self.p_z = p_z
    
    def generate_error_opcode(self, qubits):
        if isinstance(qubits, int):
            qubits = [qubits]

        opcodes =[('PauliError1Q', qubit, None, (self.p_x, self.p_y, self.p_z), None, None) for qubit in qubits]
        return opcodes
    
class PauliError2Q(ErrorModel):
    def __init__(self, ps: List[float]):
        self.ps = ps
    
    def generate_error_opcode(self, qubits):
        if not isinstance(qubits, list) or len(qubits)!= 2:
            raise ValueError("PauliError2Q error model requires two qubits")
        
        opcodes = [('PauliError2Q', qubit, None, self.ps, None, None) for qubit in qubits]
        return opcodes

class Kraus1Q(ErrorModel):
    def __init__(self, kraus_ops: List[List[complex]]):
        self.kraus_ops = kraus_ops

    def generate_error_opcode(self, qubits):
        if isinstance(qubits, int):
            qubits = [qubits]

        opcodes =[('Kraus1Q', qubit, None, self.kraus_ops, None, None) for qubit in qubits]
        return opcodes


class ErrorLoader:
    '''
    This class is used to load the opcodes into the simulator.'
    '''
    def __init__(self):
        self.opcodes = []

    def insert_error(self, opcode):
        pass

    def insert_opcode(self, opcode):
        # extract opcode
        self.opcodes.append(opcode)
        self.insert_error(opcode)

    def process_opcodes(self, opcodes):
        for opcode in opcodes:
            self.insert_opcode(opcode)


class ErrorLoader_GenericError(ErrorLoader):
    '''
    This class is used to load the opcodes into the simulator with generic noise.'
    '''
    def __init__(self, generic_error : List[ErrorModel]):
        super().__init__()
        self.generic_error = generic_error if generic_error else []
        
    def insert_error(self, opcode):
        # extract opcode
        _, qubits, _, _, _, _ = opcode
        
        for noise_model in self.generic_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)
        

class ErrorLoader_GateTypeError(ErrorLoader_GenericError):
    '''
    This class is used to load the opcodes into the simulator with gate dependent noise.'
    '''
    def __init__(self, generic_error : List[ErrorModel], gatetype_error : Dict[str, List[ErrorModel]]):
        super().__init__(generic_error)
        
        self.gatetype_error = gatetype_error if gatetype_error else {}

        
    def insert_error(self, opcode):
        # extract opcode
        gate, qubits, _, _, _, _ = opcode

        for noise_model in self.generic_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)

        gate_error = self.gatetype_error.get(gate, [])
        for noise_model in gate_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)

class ErrorLoader_GateSpecificError(ErrorLoader_GateTypeError):
    '''
    This class is used to load the opcodes into the simulator with gate specific noise.
    '''
    def __init__(self, generic_error : List[ErrorModel], gatetype_error : Dict[str, List[ErrorModel]], 
                 gate_specific_error : Dict[Tuple[str, Tuple[int, int]], List[ErrorModel]]):
        super().__init__(generic_error, gatetype_error)
        self.gate_specific_error = gate_specific_error if gate_specific_error else {}
        
    def insert_error(self, opcode):
        # extract opcode
        gate, qubits, _, _, _, _ = opcode

        super().insert_error(opcode)
        # special case for CZ gate, the qubits need to be sorted
        if gate == 'CZ':
            qubits = [min(qubits[0], qubits[1]), max(qubits[0], qubits[1])]
        
        if isinstance(qubits, list):
            qubits = tuple(qubits)

        key = (gate, qubits)

        gate_specific_error = self.gate_specific_error.get(key, [])
        for noise_model in gate_specific_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)

