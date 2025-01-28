# opcode loader for qpandalite simulator

from typing import List
from .error_model import (ErrorModel, BitFlip, PhaseFlip, AmplitudeDamping,
                          Depolarizing, TwoQubitDepolarizing,
                          PauliError1Q, PauliError2Q,
                          Kraus1Q)

class OpcodeLoader:
    '''
    This class is used to load the opcodes into the simulator.'
    '''
    def __init__(self):
        self.opcodes = []

    def load_opcode(self, opcode):
        self.opcodes.append(opcode)


class OpcodeLoader_GenericError(OpcodeLoader):
    '''
    This class is used to load the opcodes into the simulator with generic noise.'
    '''
    def __init__(self, generic_error : List[ErrorModel]):
        super().__init__()
        self.generic_error = generic_error
        
    def insert_error(self, opcode):
        # extract opcode
        _, qubits, _, _, _, _ = opcode

        for noise_model in self.generic_error:
            noise_opcodes = noise_model.generate_error_opcode(qubits)
            self.opcodes.extend(noise_opcodes)
        
    def load_opcode(self, opcode):
        super().load_opcode(opcode)
        if self.generic_error:
            self.insert_error(opcode)

class OpcodeLoader_GateDependentError(OpcodeLoader_GenericError):
    '''
    This class is used to load the opcodes into the simulator with gate dependent noise.'
    '''
    def __init__(self, generic_error : List[ErrorModel], gate_error : List[str, ErrorModel]):
        super().__init__(generic_error)
        self.gate_error = gate_error
        self.gate_noise = gate_noise

