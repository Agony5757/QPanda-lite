import re

class OriginIR_Parser:    
    regexp_1q = re.compile(r'^([A-Za-z]+) *q\[(\d+)\]$')
    regexp_2q = re.compile(r'^([A-Za-z]+) *q\[(\d+)\], *q\[(\d+)\]$')
    regexp_1q1p = re.compile(r'^([A-Za-z]+) *q\[(\d+)\], *\((-?\d+(\.\d*)?)\)$')
    regexp_1q2p = re.compile(r'^([A-Za-z]+) *q\[(\d+)\], *\((-?\d+(\.\d*)?), *(-?\d+(\.\d*)?)\)$')
    regexp_meas = re.compile(r'^MEASURE q\[(\d+)\], *c\[(\d+)\]$')

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
        parameter2 = float(matches.group(5))
        return operation, q, [parameter1, parameter2]
    
    @staticmethod
    def handle_measure(line):
        matches = OriginIR_Parser.regexp_meas.match(line)
        q = matches.group(1)
        c = matches.group(2)
        return q, c

    @staticmethod
    def parse_line(line):
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
    
if __name__ == '__main__':
    matches = OriginIR_Parser.regexp_1q2p.match('Rphi q[45], (-1.1,1.2)')
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))
    print(matches.group(5))