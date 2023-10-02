import re

class OriginIR_Parser:    

    opname = r'([A-Za-z]+)'
    blank = r' *'
    qid = r'q *\[ *(\d+) *\]'
    cid = r'c *\[ *(\d+) *\]'
    comma = r','
    lbracket = r'\('
    rbracket = r'\)'
    parameter = r'(-?\d+(\.\d*)?([eE][-+]?\d+)?)'
    regexp_1q_str = '^' + opname + blank + qid + '$'
    regexp_2q_str = '^' + opname + blank + qid + blank + comma + blank + qid + '$'
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
    regexp_measure_str = ('^' + 
                        r'MEASURE' + blank + 
                        qid + blank + 
                        comma + blank + 
                        cid + 
                        '$')
    regexp_1q = re.compile(regexp_1q_str)
    regexp_2q = re.compile(regexp_2q_str)
    regexp_1q1p = re.compile(regexp_1q1p_str)
    regexp_1q2p = re.compile(regexp_1q2p_str)
    regexp_meas = re.compile(regexp_measure_str)

    def __init__(self):
        pass

    @staticmethod
    def handle_1q(line):
        matches = OriginIR_Parser.regexp_1q.match(line)
        operation = matches.group(1)
        q = matches.group(2)
        return operation, q

    @staticmethod
    def handle_2q(line):
        matches = OriginIR_Parser.regexp_2q.match(line)
        operation = matches.group(1)
        q1 = matches.group(2)
        q2 = matches.group(3)
        return operation, [q1, q2]

    @staticmethod
    def handle_1q1p(line):
        matches = OriginIR_Parser.regexp_1q1p.match(line)
        operation = matches.group(1)
        q = matches.group(2)
        parameter = float(matches.group(3))
        return operation, q, parameter

    @staticmethod
    def handle_1q2p(line):
        matches = OriginIR_Parser.regexp_1q2p.match(line)
        operation = matches.group(1)
        q = matches.group(2)
        parameter1 = float(matches.group(3))
        parameter2 = float(matches.group(6))
        return operation, q, [parameter1, parameter2]
    
    @staticmethod
    def handle_measure(line):
        matches = OriginIR_Parser.regexp_meas.match(line)
        q = matches.group(1)
        c = matches.group(2)
        return q, c

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
            elif line.startswith('X'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('Z'):
                operation, q = OriginIR_Parser.handle_1q(line)
            elif line.startswith('CZ'):
                operation, q = OriginIR_Parser.handle_2q(line)
            elif line.startswith('ISWAP'):
                operation, q = OriginIR_Parser.handle_2q(line)
            elif line.startswith('CNOT'):
                operation, q = OriginIR_Parser.handle_2q(line)
            elif line.startswith('RX'):
                operation, q, parameter = OriginIR_Parser.handle_1q1p(line)
            elif line.startswith('RY'):
                operation, q, parameter = OriginIR_Parser.handle_1q1p(line)
            elif line.startswith('RZ'):
                operation, q, parameter = OriginIR_Parser.handle_1q1p(line)
            elif line.startswith('Rphi'):
                operation, q, parameter = OriginIR_Parser.handle_1q2p(line)
            elif line.startswith('MEASURE'):
                operation = 'MEASURE'
                q, c = OriginIR_Parser.handle_measure(line)
            else:
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
    
    
    print(OriginIR_Parser.regexp_2q_str)
    matches = OriginIR_Parser.regexp_2q.match('CNOT q[ 45], q[46 ]')
    print(matches.group(0)) 
    print(matches.group(1)) # CNOT
    print(matches.group(2)) # 45
    print(matches.group(3)) # 46

    print(OriginIR_Parser.regexp_measure_str)
    matches = OriginIR_Parser.regexp_meas.match('MEASURE  q [ 45 ] ,  c[ 11 ]')
    print(matches.group(0))
    print(matches.group(1)) # 45
    print(matches.group(2)) # 11