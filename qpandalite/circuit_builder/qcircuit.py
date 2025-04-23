from typing import Dict, List, Optional, Tuple, Union
from copy import deepcopy
from .opcode import (make_header_originir, make_header_qasm, 
                     make_measure_originir, make_measure_qasm, 
                     opcode_to_line_originir, opcode_to_line_qasm,
                     OpcodeType, )
import re

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
    """

    def __init__(self) -> None:
        self.used_qubit_list = []
        self.max_qubit = 0
        self.qubit_num = 0
        self.cbit_num = 0
        self.measure_list = []
        self.opcode_list = []
    
    def _make_originir_circuit(self) -> str:
        '''
        Generate the circuit in OriginIR format.
        '''
        header = make_header_originir(self.qubit_num, self.cbit_num)
        circuit_str = '\n'.join([opcode_to_line_originir(op) for op in self.opcode_list])
        measure = make_measure_originir(self.measure_list)
        return header + circuit_str + '\n' + measure
    
    def _make_qasm_circuit(self):
        '''
        Generate the circuit in OpenQASM format.
        '''
        header = make_header_qasm(self.qubit_num, self.cbit_num)
        circuit_str = '\n'.join([opcode_to_line_qasm(op) for op in self.opcode_list])
        measure = make_measure_qasm(self.measure_list)
        return header + circuit_str + '\n' + measure
    
    @property
    def circuit(self):
        '''
        Generate the circuit in OriginIR format.
        '''
        return self._make_originir_circuit()
    
    @property
    def originir(self):
        '''
        Generate the circuit in OriginIR format.
        '''
        return self._make_originir_circuit()
    
    @property
    def qasm(self):
        '''
        Generate the circuit in OpenQASM format.
        '''
        return self._make_qasm_circuit()
    
    
    def record_qubit(self, qubits):
        '''Record the qubits used in the circuit.
        '''
        for qubit in qubits:
            if qubit not in self.used_qubit_list:
                self.used_qubit_list.append(qubit)
                self.max_qubit = max(self.max_qubit, qubit)
        
        self.qubit_num = self.max_qubit + 1


    def add_gate(self, operation: str,
                       qubits: Union[int, List[int]], 
                       cbits: Optional[Union[int, List[int]]] = None, 
                       params: Optional[Union[float, List[float]]] = None, 
                       dagger: bool = False, 
                       control_qubits: Optional[Union[int, List[int]]] = None) -> None:
        """
        Add a gate to the circuit.

        This method adds a gate to the circuit with the specified operationname, qubits,
        parameters, and classical bits. The gate can be controlled by the specified
        control qubits.

        Parameters
        ----------
        name : str
            The name of the gate.
        qubits : int or list of int
            The qubits the gate acts on.
        params : float or list of float, optional
            The parameters of the gate.
        cbits : int or list of int, optional
            The classical bits the gate stores the result in.
        dagger : bool, optional
            Whether to add the dagger of the gate.
        control_qubits : int or list of int, optional
            The qubits to control the gate.

        Raises
        ------
        ValueError
            If the qubits are not valid or the control qubits are not valid.
        """
        
        opcode = (operation, qubits, cbits, params, dagger, control_qubits)
        self.opcode_list.append(opcode)
        self.record_qubit(qubits if isinstance(qubits, list) else [qubits])
    
    @property
    def depth(self):
        """
        Calculate the depth of the quantum circuit.

        The depth of a quantum circuit is defined as the maximum number of gates 
        on any single qubit path in the circuit. This is a measure of the circuit's 
        complexity and can be used to analyze the circuit's execution time on a quantum computer.

        Returns
        -------
        int
            The depth of the quantum circuit, which is the longest path of sequential 
            gate operations on a single qubit.

        Notes
        -----
        The measurement is not counted when calculating the depth of the circuit.
        """

        # Initialize the depth of each qubit to zero
        qubit_depths = {}

        # Process each operation using the OriginIR_base_parser
        for opcode in self.opcode_list:
            # Other options in the op_code will not affect the depth but the control
            op_name, qubits, _, _, _, control_qubits = opcode
            
            if op_name == 'I' or op_name == 'BARRIER':
                # do not count identity or barrier gates
                continue

            # If the operation is on a single qubit, make it a list so that it could be processed
            # with control qubits
            if not isinstance(qubits, list):
                qubits = [qubits]
            
            # Determine the current maximum depth among the qubits involved
            current_max_depth = 0
            for q in qubits + list(control_qubits):
                # If q is found return the value associated with it, if not, return 0
                current_max_depth = max(current_max_depth, qubit_depths.get(q, 0))
            
            # Increment the depth of all involved qubits by 1
            for q in qubits + list(control_qubits):
                qubit_depths[q] = current_max_depth + 1

        # The depth of the circuit is the maximum depth across all qubits
        return max(qubit_depths.values())

    def identity(self, qn) -> None:
        self.add_gate('I', qn)        

    def h(self, qn) -> None:
        self.add_gate('H', qn)
        
    def x(self, qn) -> None:
        self.add_gate('X', qn)

    def y(self, qn) -> None:
        self.add_gate('Y', qn)

    def z(self, qn) -> None:
        self.add_gate('Z', qn)

    def sx(self, qn) -> None:
        self.add_gate('SX', qn)

    def sxdg(self, qn) -> None:
        self.add_gate('SX', qn, dagger=True)

    def s(self, qn) -> None:
        self.add_gate('S', qn)

    def sdg(self, qn) -> None:
        self.add_gate('S', qn, dagger=True)
  
    def t(self, qn) -> None:
        self.add_gate('T', qn)

    def tdg(self, qn) -> None:
        self.add_gate('T', qn, dagger=True)

    def rx(self, qn, theta) -> None:
        self.add_gate('RX', qn, params=theta)

    def ry(self, qn, theta) -> None:
        self.add_gate('RY', qn, params=theta)

    def rz(self, qn, theta) -> None:
        self.add_gate('RZ', qn, params=theta)

    def rphi(self, qn, theta, phi) -> None:
        self.add_gate('RPhi', qn, params=[theta, phi])

    def cnot(self, controller, target) -> None:
        self.add_gate('CNOT', [controller, target])

    def cx(self, controller, target) -> None:
        self.cnot(controller, target)

    def cz(self, q1, q2) -> None:
        self.add_gate('CZ', [q1, q2])

    def iswap(self, q1, q2) -> None:
        self.add_gate('ISWAP', [q1, q2])

    def u1(self, qn, lam) -> None:
        self.add_gate('U1', qn, params=lam)

    def u2(self, qn, phi, lam) -> None:
        self.add_gate('U2', qn, params=[phi, lam])

    def u3(self, qn, theta, phi, lam) -> None:
        self.add_gate('U3', qn, params=[theta, phi, lam])

    def swap(self, q1, q2) -> None:
        self.add_gate('SWAP', [q1, q2])

    def cswap(self, q1, q2, q3) -> None:
        self.add_gate('CSWAP', [q1, q2, q3])

    def toffoli(self, q1, q2, q3) -> None:
        self.add_gate('TOFFOLI', [q1, q2, q3])

    def xx(self, q1, q2, theta) -> None:
        self.add_gate('XX', [q1, q2], params=theta)

    def yy(self, q1, q2, theta) -> None:
        self.add_gate('YY', [q1, q2], params=theta)

    def zz(self, q1, q2, theta) -> None:
        self.add_gate('ZZ', [q1, q2], params=theta)

    def phase2q(self, q1, q2, theta1, theta2, thetazz) -> None:
        self.add_gate('PHASE2Q', [q1, q2], params=[theta1, theta2, thetazz])

    def uu15(self, q1, q2, params: List[float]) -> None:
        self.add_gate('UU15', [q1, q2], params=params)

    def barrier(self, *qubits) -> None:
        self.add_gate('BARRIER', list(qubits))

    def measure(self, *qubits):
        self.record_qubit(qubits)
        if self.measure_list is None:
            self.measure_list = list()
            
        self.measure_list.extend(list(qubits))
        self.cbit_num = len(self.measure_list)

    def control(self, *args):
        self.record_qubit(args)
        if len(args) == 0:
            raise ValueError('Controller qubit must not be empty.')
        return CircuitControlContext(self, args)
    
    def set_control(self, *args):    
        self.record_qubit(args)
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
        
        def remap_opcode(opcode, mapping):
            op_name, qubits, cbits, params, dagger, control_qubits = opcode
            new_qubits = [mapping[q] for q in qubits] if isinstance(qubits, list) else mapping[qubits]

            if control_qubits is not None:
                new_control_qubits = [mapping[q] for q in control_qubits] if isinstance(control_qubits, list) else mapping[control_qubits]
            else:
                new_control_qubits = None

            return (op_name, new_qubits, cbits, params, dagger, new_control_qubits)

        c.opcode_list = [remap_opcode(op, mapping) for op in self.opcode_list]

        for i, old_qubit in enumerate(self.used_qubit_list):
            c.used_qubit_list[i] = mapping[old_qubit]

        for i, old_qubit in enumerate(self.measure_list):
            c.measure_list[i] = mapping[old_qubit]
        
        # update the circuit information
        c.max_qubit = max(c.used_qubit_list)
        c.qubit_num = c.max_qubit + 1
        c.cbit_num = len(c.measure_list)

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
        