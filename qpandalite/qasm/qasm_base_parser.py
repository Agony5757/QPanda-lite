from .qasm_line_parser import OpenQASM2_LineParser
from .exceptions import NotSupportedGateError, RegisterDefinitionError, RegisterNotFoundError
class OpenQASM2_BaseParser:    
    def __init__(self):
        self.qregs = list()
        self.cregs = list()        
        self.n_qubit = None
        self.n_cbit = None
        self.program_body = list()
        self.raw_qasm = None
        self.formatted_qasm = None

        # for qasm statement collection
        self.collected_qregs_str = list()
        self.collected_cregs_str = list()
        self.collected_measurements_str = list()
        self.program_body_str = list()

        # for measurement mapping
        self.measure_qubit = list()

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

        return ret_qasm, collected_qregs, collected_cregs, program_body, collected_measurements
                
    def _extract_qregs(self, lines):
        for line in lines:
            if line.startswith('qreg'):
                qreg_name, qreg_size = OpenQASM2_LineParser.handle_qreg(line)
    
    @staticmethod
    def _compute_id(regs, reg_name, reg_id):
        id = 0
        for reg_name, reg_size in regs:
            if reg_name == reg_name:
                return id + reg_id
            
            id += reg_size
            
        raise RegisterNotFoundError()
    
    def _get_qubit_id(self, qreg_name, qreg_id):
        try:
            qubit_id = OpenQASM2_BaseParser._compute_id(self.qregs, qreg_name, qreg_id)
            return qubit_id
        except RegisterNotFoundError:
            raise RegisterNotFoundError('Cannot find qreg {}, (defined = {})'.format(
                qreg_name, self.collected_qregs_str
            ))
        
    def _get_cbit_id(self, creg_name, creg_id):
        try:
            cbit_id = OpenQASM2_BaseParser._compute_id(self.cregs, creg_name, creg_id)
            return cbit_id
        except RegisterNotFoundError:
            raise RegisterNotFoundError('Cannot find creg {}, (defined = {})'.format(
                creg_name, self.collected_cregs_str
            ))
    
    @staticmethod
    def _check_regs(collected_regs, reg_handler):
        # check whether qregs have the same name
        names = set()
        regs = list()
        total_size = 0
        if len(collected_regs) == 0:
            raise RegisterDefinitionError("Register is empty")
        for reg_str in collected_regs:
            name, size = reg_handler(reg_str)
            if name in names:
                raise RegisterDefinitionError("Duplicate name")
            
            names.add(name)
            regs.append((name, size))
            total_size += size

        return total_size, regs
    
    def _process_measurements(self):
        for measurement in self.collected_measurements_str:
            qreg_name, qreg_id, creg_name, creg_id = OpenQASM2_LineParser.handle_measure(measurement)
            qid = self._get_qubit_id(qreg_name, qreg_id)
            cid = self._get_cbit_id(creg_name, creg_id)
            self.measure_qubit.append((qid, cid))

    def parse(self, raw_qasm):
        self.raw_qasm = raw_qasm

        # format, and check if QASM code is valid
        # also return the collected statements
        (self.formatted_qasm, 
         self.collected_qregs_str, 
         self.collected_cregs_str, 
         self.program_body, 
         self.collected_measurements_str) = self._format_and_check()
        
        # process the total number of qubit
        try:
            self.n_qubit, self.qregs = OpenQASM2_BaseParser._check_regs(self.collected_qregs_str, OpenQASM2_LineParser.handle_qreg)
        except RegisterDefinitionError as e:
            raise RegisterDefinitionError("QReg Definition Error.\n"
                                          f"Internal error: \n{str(e)}")
        
        # process the total number of cbit
        try:
            self.n_cbit, self.cregs = OpenQASM2_BaseParser._check_regs(self.collected_cregs_str, OpenQASM2_LineParser.handle_creg)
        except RegisterDefinitionError as e:
            raise RegisterDefinitionError("CReg Definition Error.\n"
                                          f"Internal error: \n{str(e)}")
        
        # process measurements
        self._process_measurements()

        # process program body
        for line in self.program_body:
            operation, qubits, cbits, parameters = OpenQASM2_LineParser.parse_line(line)
            if operation is None:
                continue
                
            if isinstance(qubits, list):
                qubit_ids = [self._get_qubit_id(qubit[0], qubit[1]) for qubit in qubits]
            else:
                qubit_ids = self._get_qubit_id(qubits[0], qubits[1])
                    

        
        
