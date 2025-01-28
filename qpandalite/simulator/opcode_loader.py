# opcode loader for qpandalite simulator

class OpcodeLoader:
    '''
    This class is used to load the opcodes into the simulator.'
    '''
    def __init__(self):
        self.opcodes = []

    def load_opcode(self, opcode):
        self.opcodes.append(opcode)


class OpcodeLoader_GenericNoise(OpcodeLoader):
    '''
    This class is used to load the opcodes into the simulator with generic noise.'
    '''
    def __init__(self, noise_model):
        super().__init__()
        self.noise_model = noise_model
        
    def insert_error(self, opcode):
        # extract opcode
        operation, qubits, _, _, _, _ = opcode


    def load_opcode(self, opcode):
        if self.noise_model: