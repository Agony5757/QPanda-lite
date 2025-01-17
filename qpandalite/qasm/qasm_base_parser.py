from .qasm_line_parser import OpenQASM2_LineParser
from .exceptions import NotSupportedGateError
class OpenQASM2_BaseParser:    
    def __init__(self):
        self.qregs = list()
        self.cregs = list()        
        self.program_body = list()
        self.raw_qasm = None
        self.formatted_qasm = None

    def _format_and_check(self):
        '''Format the original qasm code and check if it is valid.
           Currently, this is a simple parser, so that "gate" defines are not
           supported, and 'if' statements are not supported.
           A canonical format of qasm code is like:
           OPENQASM 2.0;
           include "qelib1.inc";

           qreg q[n];
           <other qreg definitions>
           creg c[m];
           <other creg definitions>
           <program_body>
           
           These rules will be applied in the formatted qasm code.
           1. OPENQASM 2.0 and include "qelib1.inc" will be removed.
           2. qreg definitions are collected together; so as creg definitions.
           3. program body is line-wise, separated by semicolons
           4. measurements must be at the end of the program body.
           5. barriers will be ignored.
        '''
        if self.raw_qasm is None:
            raise ValueError("No raw qasm code provided.")
        
        # check if there is "gate" definitions
        if 'gate' in self.raw_qasm and '{' in self.raw_qasm:
            raise NotSupportedGateError("Gate definitions are not supported yet.")
        
        # check if there is "if" statements
        if 'if' in self.raw_qasm:
            raise NotSupportedGateError("If statements are not supported yet.")
        
        collected_qregs = list()
        collected_cregs = list()
        collected_measurements = list()
        program_body = list()

        # split all codes by semicolons
        codes = self.raw_qasm.split(';')
        for code in codes:
            # strip leading and trailing whitespaces
            code = code.strip()
            # remove comments and OPENQASM/include statements
            if code.startswith('//'):
                continue
            elif code == '':
                continue
            elif code.startswith('include'):
                continue
            elif code.startswith('OPENQASM'):
                continue
            elif code.startswith('barrier'):
                continue
            
            # handle qreg and creg definitions
            elif code.startswith('qreg'):
                collected_qregs.append(code)
            elif code.startswith('creg'):
                collected_cregs.append(code)
            elif code.startswith('measure'):
                collected_measurements.append(code)
            else:
                program_body.append(code)
            
        ret_qasm = ('{};\n'
                    '{};\n'
                    '{};\n'
                    '{};'.format(
                        ';\n'.join(collected_qregs),
                        ';\n'.join(collected_cregs),
                        ';\n'.join(program_body),
                        ';\n'.join(collected_measurements)
                    ))
        
        return ret_qasm
                
    def _extract_qregs(self, lines):
        for line in lines:
            if line.startswith('qreg'):
                qreg_name, qreg_size = OpenQASM2_LineParser.handle_qreg(line)
                

    def parse(self, raw_qasm):
        self.raw_qasm = raw_qasm
        self.formatted_qasm = self._format_and_check()