from .originir_line_parser import OriginIR_Parser

class OriginIR_BaseParser:    
    def __init__(self):
        pass

    def parse(self, originir_str):
        self.originir = originir_str