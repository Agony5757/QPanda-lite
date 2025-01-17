from .qasm_line_parser import QASM_LineParser

class OpenQASM2_BaseParser:    
    def __init__(self):
        self.n_qubit = None
        self.n_cbit = None        
        self.program_body = list()
        self.raw_originir = None