import re

class OriginIR_Parser:    

    opname = r'([A-Za-z][A-Za-z\d]*)'
    blank = r' *'
    qid = r'q *\[ *(\d+) *\]'
    cid = r'c *\[ *(\d+) *\]'
    comma = r','
    lbracket = r'\('
    rbracket = r'\)'
    parameter = r'([-+]?\d+(\.\d*)?([eE][-+]?\d+)?)'
    regexp_1q_str = '^' + opname + blank + qid + '$'
    regexp_2q_str = ('^' + 
                     opname + blank + 
                     qid + blank + 
                     comma + blank + 
                     qid + 
                     '$')
    regexp_3q_str = ('^' + 
                     opname + blank + 
                     qid + blank + 
                     comma + blank +  
                     qid + blank + 
                     comma + blank + 
                     qid + 
                     '$')
    regexp_1q1p_str = ('^' + 
                        opname + blank + 
                        qid + blank +  
                        comma + blank + 
                        lbracket + blank + 
                        parameter + blank + 
                        rbracket + 
                        '$')    
    regexp_1q2p_str = ('^' + 
                        opname + blank + 
                        qid + blank +  
                        comma + blank + 
                        lbracket + blank + 
                        parameter + blank + 
                        comma + blank + 
                        parameter + blank + 
                        rbracket +
                        '$')    
    regexp_1q3p_str = ('^' + 
                        opname + blank + 
                        qid + blank +  
                        comma + blank + 
                        lbracket + blank + 
                        parameter + blank + 
                        comma + blank + 
                        parameter + blank + 
                        comma + blank + 
                        parameter + blank + 
                        rbracket +
                        '$')    
    regexp_1q4p_str = ('^' + 
                        opname + blank + 
                        qid + blank +  
                        comma + blank + 
                        lbracket + blank + 
                        parameter + blank + 
                        comma + blank + 
                        parameter + blank + 
                        comma + blank + 
                        parameter + blank + 
                        comma + blank + 
                        parameter + blank + 
                        rbracket +
                        '$')    
    regexp_2q1p_str = ('^' + 
                        opname + blank + 
                        qid + blank +  
                        comma + blank + 
                        qid + blank +  
                        comma + blank + 
                        lbracket + blank + 
                        parameter + blank + 
                        rbracket +
                        '$')    
    regexp_measure_str = ('^' + 
                        r'MEASURE' + blank + 
                        qid + blank + 
                        comma + blank + 
                        cid + 
                        '$')
    regexp_barrier_str = (r'^BARRIER' +
                          f'(({blank}{qid}{blank}{comma})*{blank}{qid}{blank})' + 
                          '$')    
    regexp_control_str = (r'^(CONTROL|ENDCONTROL)' +
                          f'(({blank}{qid}{blank}{comma})*{blank}{qid}{blank})' + 
                          '$')
    
    regexp_1q = re.compile(regexp_1q_str)
    regexp_2q = re.compile(regexp_2q_str)
    regexp_3q = re.compile(regexp_3q_str)
    regexp_1q1p = re.compile(regexp_1q1p_str)
    regexp_1q2p = re.compile(regexp_1q2p_str)
    regexp_1q3p = re.compile(regexp_1q3p_str)
    regexp_1q4p = re.compile(regexp_1q4p_str)
    regexp_2q1p = re.compile(regexp_2q1p_str)
    regexp_meas = re.compile(regexp_measure_str)
    regexp_barrier = re.compile(regexp_barrier_str)
    regexp_control = re.compile(regexp_control_str)
    regexp_qid = re.compile(qid)

    def __init__(self):
        pass

    @staticmethod
    def handle_1q(line):
        matches = OriginIR_Parser.regexp_1q.match(line)
        operation = matches.group(1)
        q = int(matches.group(2))
        return operation, q

    @staticmethod
    def handle_2q(line):
        matches = OriginIR_Parser.regexp_2q.match(line)
        operation = matches.group(1)
        q1 = int(matches.group(2))
        q2 = int(matches.group(3))
        return operation, [q1, q2]
    
    @staticmethod
    def handle_3q(line):
        matches = OriginIR_Parser.regexp_2q.match(line)
        operation = matches.group(1)
        q1 = int(matches.group(2))
        q2 = int(matches.group(3))
        q3 = int(matches.group(4))
        return operation, [q1, q2, q3]

    @staticmethod
    def handle_1q1p(line):
        matches = OriginIR_Parser.regexp_1q1p.match(line)
        operation = matches.group(1)
        q = int(matches.group(2))
        parameter = float(matches.group(3))
        return operation, q, parameter

    @staticmethod
    def handle_1q2p(line):
        matches = OriginIR_Parser.regexp_1q2p.match(line)
        operation = matches.group(1)
        q = int(matches.group(2))
        parameter1 = float(matches.group(3))
        parameter2 = float(matches.group(6))
        return operation, q, [parameter1, parameter2]
    
    @staticmethod
    def handle_1q3p(line):
        matches = OriginIR_Parser.regexp_1q2p.match(line)
        operation = matches.group(1)
        q = int(matches.group(2))
        parameter1 = float(matches.group(3))
        parameter2 = float(matches.group(6))
        parameter3 = float(matches.group(9))
        return operation, q, [parameter1, parameter2, parameter3]
    
    @staticmethod
    def handle_1q4p(line):
        matches = OriginIR_Parser.regexp_1q2p.match(line)
        operation = matches.group(1)
        q = int(matches.group(2))
        parameter1 = float(matches.group(3))
        parameter2 = float(matches.group(6))
        parameter3 = float(matches.group(9))
        parameter4 = float(matches.group(12))
        return operation, q, [parameter1, parameter2, parameter3, parameter4]
    
    @staticmethod
    def handle_2q1p(line):
        matches = OriginIR_Parser.regexp_2q1p.match(line)
        operation = matches.group(1)
        q1 = int(matches.group(2))
        q2 = int(matches.group(3))
        parameter1 = float(matches.group(4))
        return operation, [q1, q2], parameter1
    
    @staticmethod
    def handle_measure(line):
        matches = OriginIR_Parser.regexp_meas.match(line)
        q = int(matches.group(1))
        c = int(matches.group(2))
        return q, c
    
    @staticmethod
    def handle_barrier(line):
        matches = OriginIR_Parser.regexp_barrier.match(line)
        # Extract individual qubit patterns
        qubits = OriginIR_Parser.regexp_qid.findall(line)
        # Extract only the numeric part of each qubit pattern
        qubit_indices = [int(q) for q in qubits]
        return "BARRIER", qubit_indices
    
    @staticmethod
    def handle_control(line):
        """
        Parse a line to extract control qubits information and the type of control operation.

        This function analyzes a given line of text to identify and extract information about
        control qubits and determine whether the line represents the beginning of a control operation
        (CONTROL) or the end of a control operation (ENDCONTROL) in OriginIR language.

        Parameters
        ----------
        line : str
            The line of text to be parsed for control qubit information.

        Returns
        -------
        tuple of (str, list)
            A tuple where the first element is a string indicating the control operation type
            ("CONTROL" or "ENDCONTROL") and the second element is a list of integers representing
            the parsed control qubits.

        Notes
        -----
        The function relies on the `regexp_control` regular expression to match the CONTROL or
        ENDCONTROL patterns in OriginIR language. This regular expression should be predefined
        and properly constructed to capture the necessary information from the line.
        """
        matches = OriginIR_Parser.regexp_control.match(line)        
        # Extracting the operation type and multiple control qubits
        operation_type = matches.group(1)
        qubits = OriginIR_Parser.regexp_qid.findall(matches.group(2))
        controls = [int(ctrl) for ctrl in qubits]
        return operation_type, controls
    
    @staticmethod
    def handle_dagger(line):
        """
        Parse a line to identify DAGGER or ENDDAGGER commands in OriginIR.

        This function checks a line of text to determine if it contains a command
        related to the start or end of a DAGGER operation block in the OriginIR language.

        Parameters
        ----------
        line : str
            The line of text to be parsed.

        Returns
        -------
        str or None
            Returns "DAGGER" if the line is a DAGGER command, "ENDDAGGER" if it's an ENDDAGGER command,
            or None if neither command is present.

        Notes
        -----
        The DAGGER command in OriginIR denotes the start of a block where the operations are to be
        applied in reverse order with conjugate transposition (dagger operation). The ENDDAGGER command
        signifies the end of such a block.
        """
        if "ENDDAGGER" in line:
            return "ENDDAGGER"
        elif "DAGGER" in line:
            return "DAGGER"
        else:
            return None
    
    @staticmethod
    def parse_line(line):
        try:
            q = None
            c = None
            operation = None
            parameter = None
            if not line:
                pass 
            elif line.startswith('QINIT'):
                q = int(line.strip().split()[1])
                operation = 'QINIT'
            elif line.startswith('CREG'):
                c = int(line.strip().split()[1])
                operation = 'CREG'
            elif line.startswith('H'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('SX'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('X1'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('Y1'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('Z1'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('X'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('Y'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('Z'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('T'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('S'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('CZ'):
                operation, q = OriginIR_Parser.handle_2q(line)
            elif line.startswith('ISWAP'):
                operation, q = OriginIR_Parser.handle_2q(line)
            elif line.startswith('I'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('XY'):
                operation, q = OriginIR_Parser.handle_2q1p(line)
            elif line.startswith('CNOT'):
                operation, q = OriginIR_Parser.handle_2q(line)
            elif line.startswith('TOFFOLI'):
                operation, q = OriginIR_Parser.handle_3q(line)
            elif line.startswith('RX'):
                operation, q, parameter = OriginIR_Parser.handle_1q1p(line)
            elif line.startswith('RY'):
                operation, q, parameter = OriginIR_Parser.handle_1q1p(line)
            elif line.startswith('RZ'):
                operation, q, parameter = OriginIR_Parser.handle_1q1p(line)
            elif line.startswith('RPhi'):
                operation, q, parameter = OriginIR_Parser.handle_1q2p(line)
            elif line.startswith('BARRIER'):
                operation = 'BARRIER'
                operation, q = OriginIR_Parser.handle_barrier(line)
            elif line.startswith('MEASURE'):
                operation = 'MEASURE'
                q, c = OriginIR_Parser.handle_measure(line)
            elif line.startswith('CONTROL'):
                operation, q = OriginIR_Parser.handle_control(line)
            elif line.startswith('ENDCONTROL'):
                operation = 'ENDCONTROL'
            elif line.startswith('DAGGER'):
                operation = OriginIR_Parser.handle_dagger(line)
            elif line.startswith('ENDDAGGER'):
                operation = OriginIR_Parser.handle_dagger(line)
            else:
                print("something wrong")
                raise NotImplementedError(f'A invalid line: {line}.')      
            
            return operation, q, c, parameter
        except AttributeError as e:
            raise RuntimeError(f'Error when parsing the line: {line}')
    
if __name__ == '__main__':
    
    print(OriginIR_Parser.regexp_1q_str)
    matches = OriginIR_Parser.regexp_1q.match('H  q [ 45 ]')
    print(matches.group(0))
    print(matches.group(1)) # H
    print(matches.group(2)) # 45
    
    print(OriginIR_Parser.regexp_1q1p_str)
    matches = OriginIR_Parser.regexp_1q1p.match('RX  q [ 45 ] , ( 1.1e+3)')
    print(matches.group(0))
    print(matches.group(1)) # RX
    print(matches.group(2)) # 45
    print(matches.group(3)) # 1.1e+3
    print(matches.group(4)) # 
    print(matches.group(5)) # 

    print(OriginIR_Parser.regexp_1q2p_str)
    matches = OriginIR_Parser.regexp_1q2p.match('Rphi q[ 45 ], ( -1.1 , 1.2e-5)')
    print(matches.group(0))
    print(matches.group(1)) # Rphi
    print(matches.group(2)) # 45
    print(matches.group(3)) # -1.1
    print(matches.group(4)) # 
    print(matches.group(5)) # 
    print(matches.group(6)) # 1.2e-5
    print(matches.group(7)) #
    print(matches.group(8)) #

    print(OriginIR_Parser.regexp_1q3p_str)
    matches = OriginIR_Parser.regexp_1q3p.match('U3 q[ 45 ], ( -1.1 , 1.2e-5 , 0.11)')
    print(matches.group(0))
    print(matches.group(1)) # U3
    print(matches.group(2)) # 45
    print(matches.group(3)) # -1.1
    print(matches.group(4)) # 
    print(matches.group(5)) # 
    print(matches.group(6)) # 1.2e-5
    print(matches.group(7)) #
    print(matches.group(8)) #
    print(matches.group(9)) # 0.11
    print(matches.group(10)) #
    print(matches.group(11)) #

    print(OriginIR_Parser.regexp_1q4p_str)
    matches = OriginIR_Parser.regexp_1q4p.match('U4 q[ 45 ], ( -1.1 , 1.2e-5, 0 , 0.11)')
    print(matches.group(0))
    print(matches.group(1)) # U4
    print(matches.group(2)) # 45
    print(matches.group(3)) # -1.1
    print(matches.group(4)) # 
    print(matches.group(5)) # 
    print(matches.group(6)) # 1.2e-5
    print(matches.group(7)) #
    print(matches.group(8)) #
    print(matches.group(9)) # 0
    print(matches.group(10)) #
    print(matches.group(11)) #
    print(matches.group(12)) # 0.11
    print(matches.group(13)) #
    print(matches.group(14)) #
        
    print(OriginIR_Parser.regexp_2q_str)
    matches = OriginIR_Parser.regexp_2q.match('CNOT q[ 45], q[46 ]')
    print(matches.group(0)) 
    print(matches.group(1)) # CNOT
    print(matches.group(2)) # 45
    print(matches.group(3)) # 46
        
    print(OriginIR_Parser.regexp_3q_str)
    matches = OriginIR_Parser.regexp_3q.match('TOFFOLI q[ 45], q[46 ], q [ 42 ]')
    print(matches.group(0)) 
    print(matches.group(1)) # TOFFOLI
    print(matches.group(2)) # 45
    print(matches.group(3)) # 46
    print(matches.group(4)) # 42
    
    print(OriginIR_Parser.regexp_2q1p_str)
    matches = OriginIR_Parser.regexp_2q1p.match('XY q[ 45], q[46 ], ( -1.1 )')
    print(matches.group(0)) 
    print(matches.group(1)) # XY
    print(matches.group(2)) # 45
    print(matches.group(3)) # 46
    print(matches.group(4)) # -1.1

    print(OriginIR_Parser.regexp_measure_str)
    matches = OriginIR_Parser.regexp_meas.match('MEASURE  q [ 45 ] ,  c[ 11 ]')
    print(matches.group(0))
    print(matches.group(1)) # 45
    print(matches.group(2)) # 11
    
    print(OriginIR_Parser.regexp_control_str)
    matches = OriginIR_Parser.regexp_control.match('CONTROL   q [ 45] , q[ 46]  ,  q [  999 ]')
    print(matches.group(0))
    print(matches.group(1)) # CONTROL
    print(matches.group(2)) #    q [ 45] , q[ 46]  ,  q [  999 ]
    all_matches = OriginIR_Parser.regexp_qid.findall(matches.group(2))
    print(all_matches) # ['45', '46', '999']