from typing import Dict, List, Optional, Tuple, Union
from copy import deepcopy
# from qpandalite.originir import OriginIR_LineParser, OriginIR_BaseParser
import re

QubitType = Union[List[int], int]
CbitType = Union[List[int], int]
ParameterType = Optional[Union[List[float], float]]
OpcodeType = Tuple[str, QubitType, CbitType, ParameterType, set, bool]
class CircuitControlContext:
    """
    (test)Definition of quantum circuit (Circuit).

    Class `Circuit` acts as the OriginIR generator and analysis tool supported by
    `origin_line_parser` and `origin_base_parser`. Each function within the class
    provides the necessary components to construct quantum circuits. After parsing,
    each line is transferred to either the OriginIR_Simulator, OriginIR_Parser,
    OpenQASM2_Parser, or actual quantum machines for execution or further processing.
    """        
    def __init__(self, c, control_list):
        self.c = c
        self.control_list = control_list

    def _qubit_list(self):
        ret = ''
        for q in self.control_list:
            ret += f'q[{q}], '

        ret = ret[:-2]
        return ret
    
    def __enter__(self):
        ret = 'CONTROL ' + self._qubit_list() + '\n'
        self.c.circuit_str += ret        
        
    def __exit__(self, exc_type, exc_val, exc_tb):        
        ret = 'ENDCONTROL\n'
        self.c.circuit_str += ret

class CircuitDagContext:      
    def __init__(self, c):
        self.c = c

    def __enter__(self):
        ret = 'DAGGER\n'
        self.c.circuit_str += ret        
        
    def __exit__(self, exc_type, exc_val, exc_tb):        
        ret = 'ENDDAGGER\n'
        self.c.circuit_str += ret

def opcode_to_originir_line(opcode):                    
    (operation, qubit, cbit, parameter, dagger_flag, control_qubits_set) = opcode
    
    # operation qubits (,parameter?) (,cbits?) (dagger?) (control?)
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
            ret += ', '.join([str(p) for p in parameter])
        else:
            ret += str(parameter)
        ret += ')'
        
    if cbit: 
        ret += ', '
        ret += (f'c[{cbit}]' if cbit else '')
        
    if dagger_flag:
        ret += ' dagger'
    
    if control_qubits_set:        
        ret += ' controlled_by ('
        ret += ', '.join([f'q[{q}]' for q in control_qubits_set])
        ret += ')'

    # print(ret)

    return ret


class Circuit:
    """
    Definition of quantum circuit (Circuit).

    Class `Circuit` acts as the OriginIR generator and analysis tool supported by
    `origin_line_parser` and `origin_base_parser`. Each function within the class
    provides the necessary components to construct quantum circuits. After parsing,
    each line is transferred to either the OriginIR_Simulator, OriginIR_Parser,
    OpenQASM2_Parser, or actual quantum machines for execution or further processing.

    Attributes
    ----------
    used_qubit_list : list
        A list to keep track of the qubits used in the circuit.
    circuit_str : str
        The string representation of the circuit in OriginIR format.
    max_qubit : int
        The maximum index of qubits used in the circuit.
    measure_list : list
        A list of qubits that will be measured.
    circuit_info : dict
        A dictionary containing information about the circuit such as the number of qubits,
        the types and counts of gates used, and the measurement setup.
    
    """
    def __init__(self) -> None:
        self.used_qubit_list = []
        self.circuit_str = ''
        self.max_qubit = 0
        self.measure_list = []
        self.circuit_info = {
            'qubits': 0,
            'gates': {},
            'measurements': []
        }
        
    def make_header(self):
        ret = 'QINIT {}\n'.format(self.max_qubit + 1)
        ret += 'CREG {}\n'.format(len(self.measure_list))
        return ret
    
    def make_header_qasm(self):
        ret = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
        ret += 'qreg q[{}];\n'.format(self.max_qubit + 1)
        ret += 'creg c[{}];\n'.format(len(self.measure_list))
        return ret

    # def covert_1q1p_qasm(self, line):
    #     # Match 1-qubit operations with one parameter/ RX, RY, RZ
    #     operation, q, parameter = OriginIR_LineParser.handle_1q1p(line)

    #     return f"{operation.lower()}({parameter}) q[{q}]"

    # def covert_1q2p_qasm(self, line):
    #     from numpy import pi
    #     # Match 1-qubit operations with two parameters/ Rphi
    #     operation, q, parameter = OriginIR_LineParser.handle_1q2p(line)

    #     return f"u3({parameter[1]},{parameter[0]}-pi/2, -{parameter[0]}+pi/2) q[{q}]"

    def make_measure(self):
        ret = ''
        for i, meas_qubit in enumerate(self.measure_list):
            ret += 'MEASURE q[{}], c[{}]\n'.format(meas_qubit, i)
        return ret

    def make_measure_qasm(self):
        ret = ''
        for i, meas_qubit in enumerate(self.measure_list):
            ret += 'measure q[{}] -> c[{}];\n'.format(meas_qubit, i)
        return ret   
    
    # def make_operation_qasm(self):
    #     """
    #     Convert an OriginIR circuit description into an OpenQASM string.

    #     This function translates the supported OriginIR gates into their equivalent
    #     OpenQASM representations. Unsupported gates are either omitted or transformed
    #     into a supported sequence of OpenQASM operations.

    #     Supported OriginIR gates and their OpenQASM equivalents:

    #     - 'H': Hadamard gate
    #     - 'X': Pauli-X gate
    #     - 'SX': Sqrt-X gate (no direct support in OpenQASM)
    #     - 'Y': Pauli-Y gate
    #     - 'Z': Pauli-Z gate
    #     - 'CZ': Controlled-Z gate
    #     - 'ISWAP': iSWAP gate (no direct support in OpenQASM)
    #     - 'XY': XY gate (no direct support in OpenQASM)
    #     - 'CNOT': Controlled NOT gate
    #     - 'RX': Rotation around X-axis
    #     - 'RY': Rotation around Y-axis
    #     - 'RZ': Rotation around Z-axis
    #     - 'Rphi': Two-parameter single-qubit rotation (represented with u3 in OpenQASM)

    #     The conversion process ensures that:

    #     1. Any unsupported OriginIR operation is either mapped to a supported OpenQASM
    #        equivalent or is constructed from OpenQASM primitives.
    #        Example: The 'ISWAP' gate can be defined in OpenQASM using a sequence of
    #        simpler gates.

    #     2. Gates with the same name in both OriginIR and OpenQASM have identical effects.
    #        Any discrepancies, such as a phase factor difference in 'RZ', are corrected
    #        using OpenQASM's u3, u2, or u1 gates.

    #     Returns
    #     -------
    #     str
    #         The OpenQASM representation of the quantum circuit.

    #     Notes
    #     -----
    #     The SX, ISWAP, and XY gates are not natively supported in OpenQASM and require
    #     a decomposed implementation using native OpenQASM gates.

    #     Examples
    #     --------
    #     >>> originir_circuit = OriginIRCircuit()
    #     >>> print(originir_circuit.qasm)
    #     '...OpenQASM representation...'

    #     Raises
    #     ------
    #     NotImplementedError
    #         If the conversion functionality is not implemented, an error is raised.
    #     """
    #     modified_circ_str = self.circuit_str.replace('CNOT', 'cx')

    #     # Split the input string into individual lines
    #     lines = modified_circ_str.split('\n')

    #     # Create an empty list to store the transformed lines
    #     transformed_lines = []

    #     # Iterate over each line in the input
    #     for line in lines:
    #         # Check if the line isn't just whitespace or empty
    #         if line.strip():
    #             match_1q1p = OriginIR_LineParser.regexp_1q1p.match(line)
    #             match_1q2p = OriginIR_LineParser.regexp_1q2p.match(line)
    #             if match_1q1p:
    #                 line = self.covert_1q1p_qasm(line)
    #             if match_1q2p:
    #                 line = self.covert_1q2p_qasm(line)

    #             # Convert the line to lowercase and append a semicolon
    #             new_line = line.lower() + ';'

    #             # Add the transformed line to our list
    #             transformed_lines.append(new_line)
                
    #     # Join the transformed lines back into a single string
    #     ret = '\n'.join(transformed_lines)
    #     ret += "\n"

    #     return ret

    @property
    def circuit(self):
        header = self.make_header()
        measure = self.make_measure()
        return header + self.circuit_str + measure
    
    @property
    def originir(self):
        header = self.make_header()
        measure = self.make_measure()
        return header + self.circuit_str + measure
    
    # @property
    # def qasm(self):
    #     """
    #     Convert the OriginIR representation of the circuit into OpenQASM format.

    #     This property assembles the QASM representation by concatenating the headers,
    #     operations, and measurement sections. OpenQASM format has specific syntactical rules:
    #     statements are terminated with semicolons, whitespace is non-significant, the language
    #     is case-sensitive, and comments start with double forward slashes and end at the end of the line.
    #     For user-defined gates, the 'opaque' keyword should be used in QASM.

    #     Returns
    #     -------
    #     str
    #         The OpenQASM2 representation of the circuit.
        
    #     Notes
    #     -----
    #     Currently, this property only supports conversion to OpenQASM2. Future versions
    #     may include support for other versions or variants of QASM.

    #     Examples
    #     --------
    #     >>> circuit = QuantumCircuit()
    #     >>> print(circuit.qasm)
    #     '...OpenQASM2 representation...'

    #     Raises
    #     ------
    #     NotImplementedError
    #         If QASM support is not yet implemented, an error is raised.
    #     """
    #     return self.make_header_qasm() + self.make_operation_qasm() + self.make_measure_qasm()

    #     # raise NotImplementedError('QASM support will be released in future.')

    # @property
    # def depth(self):
    #     """
    #     Calculate the depth of the quantum circuit.

    #     The depth of a quantum circuit is defined as the maximum number of gates 
    #     on any single qubit path in the circuit. This is a measure of the circuit's 
    #     complexity and can be used to analyze the circuit's execution time on a quantum computer.

    #     Returns
    #     -------
    #     int
    #         The depth of the quantum circuit, which is the longest path of sequential 
    #         gate operations on a single qubit.

    #     Notes
    #     -----
    #     The measurement is not counted when calculating the depth of the circuit.
    #     """

        
    #     return self._depth()
        
    # def _depth(self):

    #     parser = OriginIR_BaseParser()
    #     parser.parse(self.originir)

    #     # Initialize the depth of each qubit to zero
    #     qubit_depths = {}

    #     # Process each operation using the OriginIR_base_parser
    #     for operation in parser.program_body:
    #         # Other options in the op_code will not affect the depth but the control
    #         op_name, qubits, _, _, _, control_qubits = operation
            
    #         # If the operation is on a single qubit, make it a list so that it could be processed
    #         # with control qubits
    #         if not isinstance(qubits, list):
    #             qubits = [qubits]
            
    #         # Determine the current maximum depth among the qubits involved
    #         current_max_depth = 0
    #         for q in qubits + list(control_qubits):
    #             # If q is found return the value associated with it, if not, return 0
    #             current_max_depth = max(current_max_depth, qubit_depths.get(q, 0))
            
    #         # Increment the depth of all involved qubits by 1
    #         for q in qubits + list(control_qubits):
    #             qubit_depths[q] = current_max_depth + 1

    #     # The depth of the circuit is the maximum depth across all qubits
    #     return max(qubit_depths.values())
    
    def record_qubit(self, *qubits):
        for qubit in qubits:
            if qubit not in self.used_qubit_list:
                self.used_qubit_list.append(qubit)
                self.max_qubit = max(self.max_qubit, qubit)

    def identity(self, qn) -> None:
        self.circuit_str += 'I q[{}]\n'.format(qn)
        self.record_qubit(qn)

    def h(self, qn) -> None:
        self.circuit_str += 'H q[{}]\n'.format(qn)
        self.record_qubit(qn)

    def x(self, qn) -> None:
        self.circuit_str += 'X q[{}]\n'.format(qn)    
        self.record_qubit(qn)

    def y(self, qn) -> None:
        self.circuit_str += 'Y q[{}]\n'.format(qn)
        self.record_qubit(qn)

    def z(self, qn) -> None:
        self.circuit_str += 'Z q[{}]\n'.format(qn)
        self.record_qubit(qn)

    def sx(self, qn) -> None:
        self.circuit_str += 'SX q[{}]\n'.format(qn)    
        self.record_qubit(qn)

    def s(self, qn) -> None:
        self.circuit_str += 'S q[{}]\n'.format(qn)    
        self.record_qubit(qn)

    def t(self, qn) -> None:
        self.circuit_str += 'T q[{}]\n'.format(qn)    
        self.record_qubit(qn)

    def rx(self, qn, theta) -> None:
        self.circuit_str += 'RX q[{}], ({})\n'.format(qn, theta)
        self.record_qubit(qn)

    def ry(self, qn, theta) -> None:
        self.circuit_str += 'RY q[{}], ({})\n'.format(qn, theta)
        self.record_qubit(qn)

    def rz(self, qn, theta) -> None:
        self.circuit_str += 'RZ q[{}], ({})\n'.format(qn, theta)
        self.record_qubit(qn)

    def rphi(self, qn, theta, phi) -> None:
        self.circuit_str += 'RPhi q[{}], ({}, {})\n'.format(qn, theta, phi)
        self.record_qubit(qn)

    def cnot(self, controller, target) -> None:
        self.circuit_str += 'CNOT q[{}], q[{}]\n'.format(controller, target)
        self.record_qubit(controller, target)

    def cx(self, controller, target) -> None:
        self.cnot(controller, target)

    def cz(self, q1, q2) -> None:
        self.circuit_str += 'CZ q[{}], q[{}]\n'.format(q1, q2)
        self.record_qubit(q1, q2)

    def iswap(self, q1, q2) -> None:
        self.circuit_str += 'ISWAP q[{}], q[{}]\n'.format(q1, q2)
        self.record_qubit(q1, q2)

    def u1(self, qn, lam) -> None:
        self.circuit_str += 'U1 q[{}], ({})\n'.format(qn, lam)
        self.record_qubit(qn)

    def u2(self, qn, phi, lam) -> None:
        self.circuit_str += 'U2 q[{}], ({}, {})\n'.format(qn, phi, lam)
        self.record_qubit(qn)

    def u3(self, qn, theta, phi, lam) -> None:
        self.circuit_str += 'U3 q[{}], ({}, {}, {})\n'.format(qn, theta, phi, lam)
        self.record_qubit(qn)
    
    def swap(self, q1, q2) -> None:
        self.circuit_str += 'SWAP q[{}], q[{}]\n'.format(q1, q2)
        self.record_qubit(q1, q2)

    def cswap(self, q1, q2, q3) -> None:
        self.circuit_str += 'CSWAP q[{}], q[{}], q[{}]\n'.format(q1, q2, q3)
        self.record_qubit(q1, q2, q3)

    def toffoli(self, q1, q2, q3) -> None:
        self.circuit_str += 'TOFFOLI q[{}], q[{}], q[{}]\n'.format(q1, q2, q3)
        self.record_qubit(q1, q2, q3)

    def xx(self, q1, q2, theta) -> None:
        self.circuit_str += 'XX q[{}], q[{}], ({})\n'.format(q1, q2, theta)
        self.record_qubit(q1, q2)

    def yy(self, q1, q2, theta) -> None:
        self.circuit_str += 'YY q[{}], q[{}], ({})\n'.format(q1, q2, theta)
        self.record_qubit(q1, q2)

    def zz(self, q1, q2, theta) -> None:
        self.circuit_str += 'ZZ q[{}], q[{}], ({})\n'.format(q1, q2, theta)
        self.record_qubit(q1, q2)

    def phase2q(self, q1, q2, theta1, theta2, thetazz) -> None:
        self.circuit_str += 'PHASE2Q q[{}], q[{}], ({}, {}, {})\n'.format(q1, q2, theta1, theta2, thetazz)
        self.record_qubit(q1, q2)

    def uu15(self, q1, q2, params: List[float]) -> None:
        # create param list
        params_str = ', '.join([str(param) for param in params])
        self.circuit_str += 'U15 q[{}], q[{}], ({})\n'.format(q1, q2, params_str)
        self.record_qubit(q1, q2)

    def barrier(self, *qubits) -> None:
        placeholders = ', '.join(['q[{}]'] * len(qubits))
        self.circuit_str += ('BARRIER ' + placeholders + '\n').format(*qubits)
        self.record_qubit(*qubits)

    def measure(self, *qubits):
        self.record_qubit(*qubits)
        self.measure_list = list(qubits)

    def control(self, *args):
        self.record_qubit(*args)
        if len(args) == 0:
            raise ValueError('Controller qubit must not be empty.')
        return CircuitControlContext(self, args)
    
    def set_control(self, *args):    
        self.record_qubit(*args)
        ret = 'CONTROL '
        for q in self.control_list:
            ret += f'q[{q}], '
        ret = ret[:-2] + '\n'
        self.circuit_str += ret

    def unset_control(self):
        ret = 'ENDCONTROL\n'
        self.circuit_str += ret

    def dagger(self):
        return CircuitDagContext(self)
    
    def set_dagger(self):
        self.circuit_str += 'DAGGER\n'

    def unset_dagger(self):
        self.circuit_str += 'ENDDAGGER\n'

    def remapping(self, mapping : Dict[int, int]):
        # Check that all keys and values in the mapping are integers and non-negative
        if not all(isinstance(k, int) and isinstance(v, int) and k >= 0 and v >= 0 for k, v in mapping.items()):
            raise TypeError('All keys and values in mapping must be non-negative integers.')

        # Check for duplicated physical qubits (same physical qubit assigned more than once)
        if len(set(mapping.values())) != len(mapping.values()):
            raise ValueError('A physical qubit is assigned more than once.')

        # check if mapping is full
        for qubit in self.used_qubit_list:
            if qubit not in mapping:
                raise ValueError('At lease one qubit is not appeared in mapping. '
                                 f'(qubit : {qubit})')
        
        # check if mapping has duplicated qubits
        unique_qubit_set = set()
        for qubit in mapping:
            if qubit in unique_qubit_set:
                raise ValueError('Qubit is used twice in the mapping. Given mapping : '
                                 f'({mapping})')
            
            unique_qubit_set.add(qubit)

        c = deepcopy(self)
        for old_qubit, new_qubit in mapping.items():
            c.circuit_str = c.circuit_str.replace(f'q[{old_qubit}]', f'q[_{old_qubit}]')

        for old_qubit, new_qubit in mapping.items():
            c.circuit_str = c.circuit_str.replace(f'q[_{old_qubit}]', f'q[{new_qubit}]')

        for i, old_qubit in enumerate(self.used_qubit_list):
            c.used_qubit_list[i] = mapping[old_qubit]

        for i, old_qubit in enumerate(self.measure_list):
            c.measure_list[i] = mapping[old_qubit]
            
        c.max_qubit = max(c.used_qubit_list)

        return c

    


    # def unwrap(self):
    #     """
    #     Process the given list of OriginIR operations and performs the 'unwrap' 
    #     operation to simplify control structures.

    #     Parameters
    #     ----------
    #     originir : list of str
    #         A list of strings representing OriginIR operations.

    #     Returns
    #     -------
    #     list of str
    #         A simplified list of OriginIR operations where control structures 
    #         have been unwrapped. For example, given the input:
            
    #         .. code-block:: none

    #             QINIT 2
    #             CREG 2
    #             H q[0]
    #             CONTROL q[0]
    #             X q[1]
    #             ENDCONTROL q[0]
            
    #         The return will be: ["H q[0]", "X q[1] controlled q[0]"].

    #     Notes
    #     -----
    #     The format for control structure strings is subject to change. The string 
    #     "X q[1] controlled q[0]" is currently a placeholder.

    #     Raises
    #     ------
    #     None
    #     """

    #     parser = OriginIR_BaseParser()
    #     parser.parse(self.originir)
    #     return parser.to_extended_originir()
        