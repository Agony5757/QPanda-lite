from copy import deepcopy


if __name__ == '__main__':
    from originir_line_parser import OriginIR_Parser
else:
    from .originir_line_parser import OriginIR_Parser

def opcode_to_line(opcode):                    
    (operation, qubit, cbit, parameter, dagger_flag, control_qubits_set) = opcode
    
    # operation qubits (,parameter?) (,cbits?) (control?) (dagger?)
    if not operation:
        raise RuntimeError('Unexpected error. Operation is empty.')
    ret = ''
    
    ret += operation
    
    if isinstance(qubit, list):
        ret += ' '
        ret += ', '.join([f'q[{q}]' for q in qubit])
    else:
        ret += f' q[{qubit}]'

    if parameter:
        ret += ', ('
        if isinstance(parameter, list):
            ret += ', '.join(str(parameter))
        else:
            ret += str(parameter)
        ret += ')'
        
    if cbit: 
        ret += ', '
        ret += (f'c[{cbit}]' if cbit else '')
        
    if dagger_flag:
        ret += ' '
        ret += 'dagger'
    
    if control_qubits_set:        
        ret += ' controlled_by ('
        ret += ', '.join([f'q[{q}]' for q in control_qubits_set])
        ret += ')'

    return ret    

class OriginIR_BaseParser:    
    def __init__(self):
        self.n_qubit = None
        self.n_cbit = None        
        self.program_body = list()
        self.raw_originir = None

    def _extract_qinit_statement(self, lines):
        for i, line in enumerate(lines):
            operation, q, c, parameter = OriginIR_Parser.parse_line(line.strip())
            if operation is None:
                continue
            if operation != 'QINIT':
                raise ValueError('OriginIR input does not have correct QINIT statement.')
            
            self.n_qubit = q

            # skip this line
            return i + 1
    
    def _extract_creg_statement(self, lines, start_lineno):
        for i in range(start_lineno, len(lines)):
            operation, q, c, parameter = OriginIR_Parser.parse_line(lines[i].strip())
            
            if operation is None:
                continue
            if operation != 'CREG':
                raise ValueError('OriginIR input does not have correct CREG statement.')
            
            self.n_cbit = c

            # skip this line
            return i + 1

    def parse(self, originir_str):
        self.raw_originir = originir_str

        # Split into lines, and use strip() to skip the blank lines   
        lines = originir_str.strip().splitlines()

        if not lines:
            raise ValueError('Parse error. Input is empty.')
        
        # Extract the QINIT statement and CBIT statement
        # Note: always return current line number (current_lineno)
        # Will raise ValueError when the statement does not follow the grammar.
        current_lineno = self._extract_qinit_statement(lines)
        current_lineno = self._extract_creg_statement(lines, current_lineno)
        
        control_qubits_set = set()
        control_stack = list()
        dagger_count = 0
        dagger_stack = list()

        for lineno in range(current_lineno, len(lines)): 
            # handle the line
            line = lines[lineno]
            operation, qubits, cbit, parameter = OriginIR_Parser.parse_line(line.strip())
            if operation is None:
                continue
            
            # check if the operational qubit and cbit are within range
            if isinstance(qubits, list):
                for qubit in qubits:
                    if qubit >= self.n_qubit:
                        raise ValueError(f'Parse error at line {lineno}: {line}\n'
                                        f'Qubit exceeds the maximum (QINIT {self.n_qubit}).')                    
            elif qubits:
                if qubits >= self.n_qubit:
                    raise ValueError(f'Parse error at line {lineno}: {line}\n'
                                    f'Qubit exceeds the maximum (QINIT {self.n_qubit}).')
            else:
                # Dagger statement does not contain qubit parameter
                pass

            if cbit and cbit >= self.n_cbit:
                raise ValueError(f'Parse error at line {lineno}: {line}\n'
                                 f'Cbit exceeds the maximum (CBIT {self.n_cbit}).')
            
            # Handle the control statement
            if operation == "CONTROL":
                # Add all control qubits to the set
                control_stack.append(qubits)
                control_qubits_set.update(qubits)

            elif operation == "ENDCONTROL":
                qubits = control_stack.pop()
                for qubit in qubits:
                    control_qubits_set.discard(qubit)

            # Handle the dagger statement
            elif operation == "DAGGER":
                # Add a new list to the stack to collect operations inside this DAGGER block
                dagger_stack.append([])
                dagger_count += 1

            elif operation == "ENDDAGGER":
                # Pop the latest list of operations from the dagger stack and reverse them
                if dagger_stack:
                    reversed_ops = dagger_stack.pop()

                    # case 1: dagger_stack is empty, insert reversed operations
                    if not dagger_stack:
                        self.program_body.extend(reversed_ops[::-1])

                    # case 2: dagger_stack is not empty, insert reversed operations to top
                    else:
                        dagger_stack[-1].extend(reversed_ops[::-1])
                else:
                    raise ValueError(f'Parse error at line {lineno}: {line}\n'
                                      'Encounter ENDDAGGER operation before any DAGGER.')
                dagger_count -= 1

            else:

                # Check if the measurement was "controlled" or "daggered"
                if operation == 'MEASURE':
                    if control_qubits_set:
                        raise ValueError(f'Parse error at line {lineno}: {line}\n'
                                         'MEASURE operation is inside a CONTROL block.')
                    
                    if dagger_stack:
                        raise ValueError(f'Parse error at line {lineno}: {line}\n'
                                         'MEASURE operation is inside a DAGGER block.')

                # For common statements
                if dagger_count % 2:
                    dagger_flag = True
                else:
                    dagger_flag = False

                if dagger_stack:
                    # insert to the top of the dagger stack
                    dagger_stack[-1].append((operation, 
                                              qubits, 
                                              cbit, 
                                              parameter, 
                                              dagger_flag, 
                                              deepcopy(control_qubits_set)))
                else:
                    self.program_body.append((operation, 
                                              qubits, 
                                              cbit, 
                                              parameter, 
                                              dagger_flag, 
                                              deepcopy(control_qubits_set)))
                    
        # Finally, check if all dagger and control operations are closed
        if control_qubits_set:
            raise ValueError('Parse error at end.\n'
                             'The CONTROL operation is not closed at the end of the OriginIR.')
        if dagger_stack:
            raise ValueError('Parse error at end.\n'
                             'The DAGGER operation is not closed at the end of the OriginIR.')
        

    def to_extended_originir(self):
        ret = f'QINIT {self.n_qubit}\n'
        ret += f'CREG {self.n_cbit}\n'
        ret += '\n'.join([opcode_to_line(opcode) for opcode in self.program_body])
        return ret
    
    @property
    def originir(self):
        return self.to_extended_originir()

    def __str__(self):
        return self.to_extended_originir()


if __name__ == '__main__':
    originir = '''
    QINIT 11
    CREG 5
    H q[6]
    H q[7]
    DAGGER
    Z q[2]
    DAGGER
    Z q[5]
    X q[10]
    ENDDAGGER
    ENDDAGGER
    DAGGER
    Z q[5]
    X q[10]
    CONTROL q[0], q[1]
    X q[3]
    ENDCONTROL q[0], q[1]
    ENDDAGGER
    H q[8]
    H q[9]
    MEASURE q[0], c[0]
    MEASURE q[1], c[1]
    MEASURE q[2], c[2]
    MEASURE q[3], c[3]
    MEASURE q[4], c[4]
    '''

    parser = OriginIR_BaseParser()
    parser.parse(originir)

    print(parser.program_body)
    print(parser.to_extended_originir())
    print(parser.raw_originir)
    print(parser.originir)