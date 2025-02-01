import re
import math
from qpandalite.circuit_builder.qcircuit import Circuit
from math import pi

class OpenQASM2_LineParser:
    
    identifier = r'([A-Za-z_][A-Za-z_\d]*)'
    blank = r' *'    
    comma = r','
    index = r'\[ *(\d+) *\]'
    any_parameters = r'\(([^()]+)\)'

    regexp_qreg_str = ('^' +
                        'qreg' + blank + 
                        identifier + blank + 
                        index + blank + 
                        '$')
    
    regexp_creg_str = ('^' +
                        'creg' + blank + 
                        identifier + blank + 
                        index + blank + 
                        '$')
    
    qreg_str = (identifier + blank +  # qreg name
                index + blank)  # qubit index

    regexp_1q_str = ('^' +
                      identifier + blank +  # op name
                      qreg_str +
                      '$')
    
    regexp_2q_str = ('^' +
                      identifier + blank +  # op name
                      qreg_str + comma + blank + qreg_str + 
                      '$')
    
    regexp_3q_str = ('^' +
                      identifier + blank +  # op name
                      qreg_str + comma + blank + 
                      qreg_str + comma + blank + 
                      qreg_str + 
                      '$')
    
    regexp_4q_str = ('^' +
                      identifier + blank +  # op name
                      qreg_str + comma + blank + 
                      qreg_str + comma + blank + 
                      qreg_str + comma + blank + 
                      qreg_str + 
                      '$')
    
    regexp_1qnp_str = ('^' +
                      identifier + blank +  # op name
                      any_parameters + blank +  # parameter
                      qreg_str +
                      '$')
    
    regexp_2qnp_str = ('^' +
                      identifier + blank +  # op name
                      any_parameters + blank +  # parameter
                      qreg_str + comma + blank + qreg_str + 
                      '$')
        
    regexp_3qnp_str = ('^' +
                      identifier + blank +  # op name
                      any_parameters + blank +  # parameter
                      qreg_str + comma + blank + qreg_str + comma + blank + qreg_str + 
                      '$')
    
    regexp_measure_str = ('^' +
                      'measure' + blank +  
                      qreg_str + '->' + blank +  qreg_str + 
                      '$')

    regexp_qreg = re.compile(regexp_qreg_str)
    regexp_creg = re.compile(regexp_creg_str)
    regexp_1q = re.compile(regexp_1q_str)
    regexp_2q = re.compile(regexp_2q_str)
    regexp_3q = re.compile(regexp_3q_str)
    regexp_4q = re.compile(regexp_4q_str)
    regexp_1qnp = re.compile(regexp_1qnp_str)
    regexp_2qnp = re.compile(regexp_2qnp_str)
    regexp_3qnp = re.compile(regexp_3qnp_str)
    regexp_measure = re.compile(regexp_measure_str)
    
    def __init__(self):
        pass
    
    @staticmethod
    def handle_qreg(line):
        matches = OpenQASM2_LineParser.regexp_qreg.match(line)
        qreg_name = matches.group(1)
        qreg_size = int(matches.group(2))
        return qreg_name, qreg_size
        
    @staticmethod
    def handle_creg(line):
        matches = OpenQASM2_LineParser.regexp_creg.match(line)
        creg_name = matches.group(1)
        creg_size = int(matches.group(2))
        return creg_name, creg_size

    @staticmethod
    def handle_parameters(parameters_str):
        parameters_str = parameters_str.strip()
        parameter_str_list = parameters_str.split(',')
        parameters = []
        for parameter_str in parameter_str_list:
            parameters.append(eval(parameter_str.strip()))

        return parameters

    @staticmethod
    def handle_1q(line):
        matches = OpenQASM2_LineParser.regexp_1q.match(line)
        op_name = matches.group(1)
        qreg_name = matches.group(2)
        qubit_index = int(matches.group(3))
        return op_name, qreg_name, qubit_index

    @staticmethod
    def handle_2q(line):
        matches = OpenQASM2_LineParser.regexp_2q.match(line)
        op_name = matches.group(1)
        qreg_name1 = matches.group(2)
        qubit_index1 = int(matches.group(3))
        qreg_name2 = matches.group(4)
        qubit_index2 = int(matches.group(5))
        return op_name, qreg_name1, qubit_index1, qreg_name2, qubit_index2
    
    @staticmethod
    def handle_3q(line):
        matches = OpenQASM2_LineParser.regexp_3q.match(line)
        op_name = matches.group(1)
        qreg_name1 = matches.group(2)
        qubit_index1 = int(matches.group(3))
        qreg_name2 = matches.group(4)
        qubit_index2 = int(matches.group(5))
        qreg_name3 = matches.group(6)
        qubit_index3 = int(matches.group(7))
        return (op_name, 
                qreg_name1, qubit_index1, 
                qreg_name2, qubit_index2, 
                qreg_name3, qubit_index3)

    @staticmethod
    def handle_4q(line):
        matches = OpenQASM2_LineParser.regexp_4q.match(line)
        op_name = matches.group(1)
        qreg_name1 = matches.group(2)
        qubit_index1 = int(matches.group(3))
        qreg_name2 = matches.group(4)
        qubit_index2 = int(matches.group(5))
        qreg_name3 = matches.group(6)
        qubit_index3 = int(matches.group(7))
        qreg_name4 = matches.group(8)
        qubit_index4 = int(matches.group(9))
        return (op_name, 
                qreg_name1, qubit_index1, 
                qreg_name2, qubit_index2, 
                qreg_name3, qubit_index3, 
                qreg_name4, qubit_index4)
    
    @staticmethod
    def handle_1qnp(line, n_parameters):
        matches = OpenQASM2_LineParser.regexp_1qnp.match(line)
        op_name = matches.group(1)
        parameters = OpenQASM2_LineParser.handle_parameters(matches.group(2))
        qreg_name = matches.group(3)
        qubit_index = int(matches.group(4))
        if len(parameters) != n_parameters:
            raise ValueError(f'The number of parameters for {op_name} '
                             f'should be {n_parameters}, '
                             f'but got {len(parameters)}.')
        
        return op_name, parameters, qreg_name, qubit_index
    
    @staticmethod
    def handle_2qnp(line, n_parameters):
        matches = OpenQASM2_LineParser.regexp_2qnp.match(line)
        op_name = matches.group(1)
        parameters = OpenQASM2_LineParser.handle_parameters(matches.group(2))
        qreg_name1 = matches.group(3)
        qubit_index1 = int(matches.group(4))
        qreg_name2 = matches.group(5)
        qubit_index2 = int(matches.group(6))
        if len(parameters) != n_parameters:
            raise ValueError(f'The number of parameters for {op_name} '
                             f'should be {n_parameters}, '
                             f'but got {len(parameters)}.')
        
        return op_name, parameters, qreg_name1, qubit_index1, qreg_name2, qubit_index2

    @staticmethod
    def handle_3qnp(line, n_parameters):
        matches = OpenQASM2_LineParser.regexp_3qnp.match(line)
        op_name = matches.group(1)
        parameters = OpenQASM2_LineParser.handle_parameters(matches.group(2))
        qreg_name1 = matches.group(3)
        qubit_index1 = int(matches.group(4))
        qreg_name2 = matches.group(5)
        qubit_index2 = int(matches.group(6))
        qreg_name3 = matches.group(7)
        qubit_index3 = int(matches.group(8))
        if len(parameters) != n_parameters:
            raise ValueError(f'The number of parameters for {op_name} '
                             f'should be {n_parameters}, '
                             f'but got {len(parameters)}.')
        
        return (op_name, 
                parameters, 
                qreg_name1, qubit_index1, 
                qreg_name2, qubit_index2, 
                qreg_name3, qubit_index3)
    
    @staticmethod
    def handle_1q1p(line):
        return OpenQASM2_LineParser.handle_1qnp(line, 1)

    @staticmethod
    def handle_1q2p(line):
        return OpenQASM2_LineParser.handle_1qnp(line, 2)

    @staticmethod
    def handle_1q3p(line):
        return OpenQASM2_LineParser.handle_1qnp(line, 3)

    @staticmethod
    def handle_1q4p(line):
        return OpenQASM2_LineParser.handle_1qnp(line, 4)

    @staticmethod
    def handle_2q1p(line):
        return OpenQASM2_LineParser.handle_2qnp(line, 1)

    @staticmethod
    def handle_2q2p(line):
        return OpenQASM2_LineParser.handle_2qnp(line, 2)

    @staticmethod
    def handle_2q3p(line):
        return OpenQASM2_LineParser.handle_2qnp(line, 3)

    @staticmethod
    def handle_2q4p(line):
        return OpenQASM2_LineParser.handle_2qnp(line, 4)
    
    @staticmethod
    def handle_3q1p(line):
        return OpenQASM2_LineParser.handle_3qnp(line, 1)

    @staticmethod
    def handle_3q2p(line):
        return OpenQASM2_LineParser.handle_3qnp(line, 2)

    @staticmethod
    def handle_3q3p(line):
        return OpenQASM2_LineParser.handle_3qnp(line, 3)

    @staticmethod
    def handle_3q4p(line):
        return OpenQASM2_LineParser.handle_3qnp(line, 4)

    @staticmethod
    def handle_measure(line):
        matches = OpenQASM2_LineParser.regexp_measure.match(line)
        qreg_name = matches.group(1)
        qubit_index = int(matches.group(2))
        creg_name = matches.group(3)
        creg_index = int(matches.group(4))
        return qreg_name, qubit_index, creg_name, creg_index

    @staticmethod
    def parse_line(line):
        try:            
            q = None
            c = None
            operation = None
            parameter = None

            # remove comments and whitespace
            if not line:
                return q, c, operation, parameter
            if line.startswith('//'):
                return q, c, operation, parameter

            # extract operation
            # there are two cases:
            # 1. operation with no parameter (split by space)
            # 2. operation with parameter (split by '(')
            if '(' in line:
                operation = line.split('(')[0].strip()
            else:
                operation = line.split()[0].strip()



            if operation == 'qreg':
                qreg_name, qreg_size = OpenQASM2_LineParser.handle_qreg(line)
                q = (qreg_name, qreg_size)
            elif operation == 'creg':
                creg_name, creg_size = OpenQASM2_LineParser.handle_creg(line)
                c = (creg_name, creg_size)
            # 1-qubit gates            
            elif operation == '//':
                pass
            elif operation == 'id' or \
                 operation == 'h' or \
                 operation == 'x' or \
                 operation == 'y' or \
                 operation == 'z' or \
                 operation == 's' or \
                 operation == 'sdg' or \
                 operation == 'sx' or \
                 operation == 'sxdg' or \
                 operation == 't' or \
                 operation == 'tdg':
                operation, qreg_name, qubit_index = OpenQASM2_LineParser.handle_1q(line)
                q = (qreg_name, qubit_index)
            # 2-qubit gates
            elif operation == 'cx' or \
                 operation == 'cy' or \
                 operation == 'cz' or \
                 operation == 'swap' or \
                 operation == 'ch':
                operation, qreg_name1, qubit_index1, qreg_name2, qubit_index2 = OpenQASM2_LineParser.handle_2q(line)
                q = [(qreg_name1, qubit_index1), (qreg_name2, qubit_index2)]
            # 3-qubit gates
            elif operation == 'ccx' or \
                 operation == 'cswap':
                operation, qreg_name1, qubit_index1, qreg_name2, qubit_index2, qreg_name3, qubit_index3 = OpenQASM2_LineParser.handle_3q(line)
                q = [(qreg_name1, qubit_index1), (qreg_name2, qubit_index2), (qreg_name3, qubit_index3)]
            # 4-qubit gates
            elif operation == 'c3x':
                operation, qreg_name1, qubit_index1, qreg_name2, qubit_index2, qreg_name3, qubit_index3, qreg_name4, qubit_index4 = OpenQASM2_LineParser.handle_4q(line)
                q = [(qreg_name1, qubit_index1), 
                     (qreg_name2, qubit_index2), 
                     (qreg_name3, qubit_index3), 
                     (qreg_name4, qubit_index4)]
            # 1-qubit 1-parameter gates
            elif operation == 'rx' or \
                 operation == 'ry' or \
                 operation == 'rz' or \
                 operation == 'u1':
                operation, parameter, qreg_name, qubit_index = OpenQASM2_LineParser.handle_1q1p(line)
                q = (qreg_name, qubit_index)            
            # 1-qubit 2-parameter gates
            elif operation == 'u2':
                operation, parameter, qreg_name, qubit_index = OpenQASM2_LineParser.handle_1q2p(line)
                q = (qreg_name, qubit_index)
            elif operation == 'u0':
                raise NotImplementedError(f'This line of OpenQASM 2 has not been supported yet: {line}.')
            # 1-qubit 3-parameter gates
            elif operation == 'u3' or \
                 operation == 'u':
                operation, parameter, qreg_name, qubit_index = OpenQASM2_LineParser.handle_1q3p(line)
                q = (qreg_name, qubit_index)
            # 2-qubit 1-parameter gates
            elif operation == 'rxx' or \
                 operation == 'ryy' or \
                 operation == 'rzz' or \
                 operation == 'cu1' or \
                 operation == 'crx' or \
                 operation == 'cry' or \
                 operation == 'crz':
                operation, parameter, qreg_name1, qubit_index1, qreg_name2, qubit_index2 = OpenQASM2_LineParser.handle_2q1p(line)
                q = [(qreg_name1, qubit_index1), (qreg_name2, qubit_index2)]
            # 2-qubit 3-parameter gates
            elif operation == 'cu3':
                operation, parameter, qreg_name1, qubit_index1, qreg_name2, qubit_index2 = OpenQASM2_LineParser.handle_2q3p(line)
                q = [(qreg_name1, qubit_index1), (qreg_name2, qubit_index2)]                
            elif operation == 'barrier':
                pass
            elif operation == 'measure':
                qreg_name, qubit_index, creg_name, creg_index = OpenQASM2_LineParser.handle_measure(line)
                operation ='measure'
                q = (qreg_name, qubit_index)
                c = (creg_name, creg_index)
            else:
                raise NotImplementedError(f'This line of OpenQASM 2 has not been supported yet: {line}.')      
            
            return operation, q, c, parameter
        except AttributeError as e:
            raise RuntimeError(f'Error when parsing the line: {line}')

    @staticmethod
    def build_from_qasm_str(qasm_str):
        """
        The function coverts OpenQASM string into OriginIR circuit. It will create the
        quantum circuit object given the qasm_str.

        In the initilization phase, we need to notice that OriginIR-based quantum circuit
        doe not need to specify how many qregs and cregs used. 
        
        Parameters:
        - qasm_str: The quantum circuit of intersts in the OpenQASM format.

        Returns:
        - origin_qcirc: The quantum circuit of intersts in the OriginIR format. 
        """
        # Create an empty Circuit object
        origincircuit = Circuit()
        # parser = OpenQASM2_Parser()

        lines_to_remove = ["OPENQASM 2.0;", "include \"qelib1.inc\";"]

        # Split the QASM string into lines and parse each line
        for line in qasm_str.split("\n"):
            if line not in lines_to_remove:
                OpenQASM2_LineParser.parse_line(line, origincircuit)

        return origincircuit
    
if __name__ == '__main__':

    print('----------qreg test------------')
    matches = OpenQASM2_LineParser.regexp_qreg.match('qreg q [ 12 ]')
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))

    print('----------creg test------------')
    matches = OpenQASM2_LineParser.regexp_creg.match('creg c [ 12 ]')
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))

    print('----------op 1q test-----------')
    matches = OpenQASM2_LineParser.regexp_1q.match('h q[0]')
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))

    print('----------op 2q test-----------')
    matches = OpenQASM2_LineParser.regexp_2q.match('cx q[0],q[12]')
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))
    print(matches.group(5))

    print('----------op 3q test-----------')
    matches = OpenQASM2_LineParser.regexp_3q.match('ccx q[0],q[12],q[11]')
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))
    print(matches.group(5))
    print(matches.group(6))
    print(matches.group(7))

    print('----------op 1q1p test---------')
    matches = OpenQASM2_LineParser.regexp_1qnp.match('ry (-0.5*pi) q[0]')
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))
    
    results = OpenQASM2_LineParser.handle_1q1p('ry (-0.5*pi) q[0]')
    print(results)

    print('----------op 1q2p test---------')
    matches = OpenQASM2_LineParser.regexp_1qnp.match('u2 (-0.5*pi, 11) q[0]')
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))
    
    results = OpenQASM2_LineParser.handle_1q2p('u2 (-0.5*pi, 11) q[0]')
    print(results)

    print('----------op 1q3p test---------')
    matches = OpenQASM2_LineParser.regexp_1qnp.match('u3 (-0.5*pi, 11, 888.1111) q[0]')
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))
    
    results = OpenQASM2_LineParser.handle_1q3p('u3 (-0.5*pi, 11, 888.1111) q[0]')
    print(results)

    print('----------op 2q1p test---------')
    matches = OpenQASM2_LineParser.regexp_2qnp.match('rxx (-0.5*pi) q[0], q[108]')
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))
    
    results = OpenQASM2_LineParser.handle_2q1p('rxx (-0.5*pi) q[0], q[108]')
    print(results)
    
    results = OpenQASM2_LineParser.handle_2q1p('rzz(0.8342297582553907) q[2],q[0] ')
    print(results)

    print('----------measure test---------')
    matches = OpenQASM2_LineParser.regexp_measure.match('measure q[0] -> c[18]')
    print(matches.group(0))
    print(matches.group(1))
    print(matches.group(2))
    print(matches.group(3))
    print(matches.group(4))
    