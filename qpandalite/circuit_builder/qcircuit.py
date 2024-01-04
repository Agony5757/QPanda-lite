from typing import Dict
from copy import deepcopy
from qpandalite.originir import OriginIR_Parser, OriginIR_BaseParser
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

    def covert_1q1p_qasm(self, line):
        # Match 1-qubit operations with one parameter/ RX, RY, RZ
        operation, q, parameter = OriginIR_Parser.handle_1q1p(line)

        return f"{operation.lower()}({parameter}) q[{q}]"

    def covert_1q2p_qasm(self, line):
        from numpy import pi
        # Match 1-qubit operations with two parameters/ Rphi
        operation, q, parameter = OriginIR_Parser.handle_1q2p(line)

        return f"u3({parameter[1]},{parameter[0]}-pi/2, -{parameter[0]}+pi/2) q[{q}]"

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
    
    def make_operation_qasm(self):
        """
        Convert an OriginIR circuit description into an OpenQASM string.

        This function translates the supported OriginIR gates into their equivalent
        OpenQASM representations. Unsupported gates are either omitted or transformed
        into a supported sequence of OpenQASM operations.

        Supported OriginIR gates and their OpenQASM equivalents:

        - 'H': Hadamard gate
        - 'X': Pauli-X gate
        - 'SX': Sqrt-X gate (no direct support in OpenQASM)
        - 'Y': Pauli-Y gate
        - 'Z': Pauli-Z gate
        - 'CZ': Controlled-Z gate
        - 'ISWAP': iSWAP gate (no direct support in OpenQASM)
        - 'XY': XY gate (no direct support in OpenQASM)
        - 'CNOT': Controlled NOT gate
        - 'RX': Rotation around X-axis
        - 'RY': Rotation around Y-axis
        - 'RZ': Rotation around Z-axis
        - 'Rphi': Two-parameter single-qubit rotation (represented with u3 in OpenQASM)

        The conversion process ensures that:

        1. Any unsupported OriginIR operation is either mapped to a supported OpenQASM
           equivalent or is constructed from OpenQASM primitives.
           Example: The 'ISWAP' gate can be defined in OpenQASM using a sequence of
           simpler gates.

        2. Gates with the same name in both OriginIR and OpenQASM have identical effects.
           Any discrepancies, such as a phase factor difference in 'RZ', are corrected
           using OpenQASM's u3, u2, or u1 gates.

        Returns
        -------
        str
            The OpenQASM representation of the quantum circuit.

        Notes
        -----
        The SX, ISWAP, and XY gates are not natively supported in OpenQASM and require
        a decomposed implementation using native OpenQASM gates.

        Examples
        --------
        >>> originir_circuit = OriginIRCircuit()
        >>> print(originir_circuit.qasm)
        '...OpenQASM representation...'

        Raises
        ------
        NotImplementedError
            If the conversion functionality is not implemented, an error is raised.
        """
        modified_circ_str = self.circuit_str.replace('CNOT', 'cx')

        # Split the input string into individual lines
        lines = modified_circ_str.split('\n')

        # Create an empty list to store the transformed lines
        transformed_lines = []

        # Iterate over each line in the input
        for line in lines:
            # Check if the line isn't just whitespace or empty
            if line.strip():
                match_1q1p = OriginIR_Parser.regexp_1q1p.match(line)
                match_1q2p = OriginIR_Parser.regexp_1q2p.match(line)
                if match_1q1p:
                    line = self.covert_1q1p_qasm(line)
                if match_1q2p:
                    line = self.covert_1q2p_qasm(line)

                # Convert the line to lowercase and append a semicolon
                new_line = line.lower() + ';'

                # Add the transformed line to our list
                transformed_lines.append(new_line)
                
        # Join the transformed lines back into a single string
        ret = '\n'.join(transformed_lines)
        ret += "\n"

        return ret

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
    
    @property
    def qasm(self):
        """
        Convert the OriginIR representation of the circuit into OpenQASM format.

        This property assembles the QASM representation by concatenating the headers,
        operations, and measurement sections. OpenQASM format has specific syntactical rules:
        statements are terminated with semicolons, whitespace is non-significant, the language
        is case-sensitive, and comments start with double forward slashes and end at the end of the line.
        For user-defined gates, the 'opaque' keyword should be used in QASM.

        Returns
        -------
        str
            The OpenQASM2 representation of the circuit.
        
        Notes
        -----
        Currently, this property only supports conversion to OpenQASM2. Future versions
        may include support for other versions or variants of QASM.

        Examples
        --------
        >>> circuit = QuantumCircuit()
        >>> print(circuit.qasm)
        '...OpenQASM2 representation...'

        Raises
        ------
        NotImplementedError
            If QASM support is not yet implemented, an error is raised.
        """
        return self.make_header_qasm() + self.make_operation_qasm() + self.make_measure_qasm()

        # raise NotImplementedError('QASM support will be released in future.')

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

        
        return self._depth()
        
    def _depth(self):

        parser = OriginIR_BaseParser()
        parser.parse(self.originir)

        # Initialize the depth of each qubit to zero
        qubit_depths = {}

        # Process each operation using the OriginIR_base_parser
        for operation in parser.program_body:
            # Other options in the op_code will not affect the depth but the control
            op_name, qubits, _, _, _, control_qubits = operation
            
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

    def cz(self, q1, q2) -> None:
        self.circuit_str += 'CZ q[{}], q[{}]\n'.format(q1, q2)
        self.record_qubit(q1, q2)

    def iswap(self, q1, q2) -> None:
        self.circuit_str += 'ISWAP q[{}], q[{}]\n'.format(q1, q2)
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

    def unwrap(self):
        """
        Process the given list of OriginIR operations and performs the 'unwrap' 
        operation to simplify control structures.

        Parameters
        ----------
        originir : list of str
            A list of strings representing OriginIR operations.

        Returns
        -------
        list of str
            A simplified list of OriginIR operations where control structures 
            have been unwrapped. For example, given the input:
            
            .. code-block:: none

                QINIT 2
                CREG 2
                H q[0]
                CONTROL q[0]
                X q[1]
                ENDCONTROL q[0]
            
            The return will be: ["H q[0]", "X q[1] controlled q[0]"].

        Notes
        -----
        The format for control structure strings is subject to change. The string 
        "X q[1] controlled q[0]" is currently a placeholder.

        Raises
        ------
        None
        """

        parser = OriginIR_BaseParser()
        parser.parse(self.originir)
        return parser.to_extended_originir()
        
    def analyze_circuit(self):
        """
        Analyzes the stored string representation of a quantum circuit and updates the circuit information.

        The updated 'circuit_info' dictionary contains:
        - 'qubits': The number of qubits used in the circuit.
        - 'gates': A dictionary with types of gates used and their counts.
        - 'measurements': Information about the measurement setup of the circuit.

        Parameters
        ----------
        circuit_str : str
            A string representation of the quantum circuit to be analyzed.

        Returns
        -------
        dict
            A dictionary containing information about the quantum circuit, including:
            - 'qubits': an integer representing the number of qubits.
            - 'gates': a dictionary where keys are gate types and values are counts.
            - 'measurements': a string or dictionary detailing the measurement setup.

        Raises
        ------
        None
        """
        parser = OriginIR_BaseParser()
        parser.parse(self.originir)
        # Now in the parser.program_body, there are lines in the form of 
        # (operation, qubits, cbit, parameter, dagger_flag, deepcopy(control_qubits_set)).

        self.circuit_info['qubits'] = parser.n_qubit
        # Just in case we have more ancillary_operations
        ancillary_operation = ['MEASURE']
        
        for single_command in parser.program_body:
            print(single_command)
            (operation, qubits, cbit, parameter, dagger_flag, control_qubits_set) = single_command

            # Match gates
            if operation not in ancillary_operation:
                if dagger_flag:
                    operation += "_dg"
                if control_qubits_set:
                    # Multiple-Control cases
                    operation = 'C' * len(control_qubits_set) + operation
                # This is to replace the Controlled-X to CNOT created by controls
                operation = operation.replace('CX', 'CNOT')
                self.circuit_info['gates'][operation] = self.circuit_info['gates'].get(operation, 0) + 1    
            # Match MEASURE
            elif operation == "MEASURE":
                qubit = int(qubits)
                output = int(cbit)
                self.circuit_info['measurements'].append({'qubit': qubit, 'output': f'c[{output}]'})
        
        print(self.circuit_info)
        # return parser.to_extended_originir()

if __name__ == '__main__':
    import qpandalite
    import qpandalite.simulator as sim
    from qiskit import QuantumCircuit, transpile
    from qiskit.circuit.library import TdgGate, RXGate
    import numpy as np
    import math
    from qiskit import BasicAer
    from qpandalite.qasm_origin import OpenQASM2_Parser
    # The quantum circuit in qiskit
    circ = QuantumCircuit(3)
    
    # circ.h(0)
    # circ.rx(-0.4, 0)
    # circ.x(0)
    # circ.ry(0.4, 0)
    # circ.y(0)
    # circ.rz(math.pi/3, 1).inverse()
    # circ.z(0)
    # circ.cz(0, 1)
    # circ.cx(0, 2) 
    # circ.tdg(0)
    t = TdgGate().inverse()
    rxdg = RXGate(-0.4).inverse()
    circ.append(t, [0])
    circ.append(rxdg, [0])
    circ.tdg(0).inverse()
    # circ.sx(0).inverse()
    # circ.iswap(0, 1).inverse()
    # circ.cz(0, 2)
    # circ.ccx(0, 1, 2)
    backend = BasicAer.get_backend('unitary_simulator')
    job = backend.run(transpile(circ, backend))
    # print(job.result().get_unitary(circ, decimals=3))
    # Create a Quantum Circuit
    # meas = QuantumCircuit(3, 3)
    # meas.measure(range(3), range(3))
    # circ = meas.compose(circ, range(3), front=True)
    qasm_string = circ.qasm()
    # print("---Circuit created using Qiskit(QASM)---")
    # print(qasm_string)
    # # Create a Circuit instance from the QASM string
    # circuit_origin = OpenQASM2_Parser.build_from_qasm_str(qasm_string)
    # print("---OriginIR Circuit coverted from QASM---")
    # print(circuit_origin.circuit)

    # origin_qc = QuantumCircuit.from_qasm_str(circuit_origin.qasm)
    # print("---Back?---")
    # print(origin_qc.qasm())
    # qsim = sim.OriginIR_Simulator()

    # result = qsim.simulate(circuit_origin.circuit)

    # print(result)
    # print(circuit.circuit_str)
    # print(circuit.used_qubit_list)
    # print(circuit.max_qubit)

    c = Circuit()
    c.h(0)
    c.cnot(1, 0)
    c.cnot(0, 2)  
    # Single control(Correct)
    with c.control(0, 1, 2):
        c.x(4)
    
    # Single dagger(Correct)
    with c.dagger():
        c.z(5)
        c.x(10)

    # Nested-dagger
    with c.dagger():
        c.z(2)
        with c.dagger():
            c.z(5)
            c.x(10)

    # Nested-control(Correct)
    with c.control(0,1):
        c.x(2) # controlled by 0,1
        with c.control(4,5):
            c.x(3) # controlled by 0,1,4,5

    # Control-dagger-nested
    with c.control(2):
        c.x(4) # controlled by 2
        with c.dagger():
            c.z(5) # dagger, controlled by 2
            c.x(10) # dagger, controlled by 2
            with c.control(0,1):
                c.x(3) # dagger, controlled by 0,1,2

    # Dagger-control-nested
    with c.dagger():
        c.z(5)
        c.x(10)
        with c.control(0,1):
            c.x(3)
    
    c.h(8)
    c.h(9)
    c.measure(0,1,2)
    # c = c.remapping({0:45, 1:46, 2:52, 3:53})
    # c = c.remapping({0:45, 1:46, 2:52, 3:53})
    print('---- Original Circuit ----')
    print(c.circuit)
    print()
    print('---- Converted Circuit ----')
    print(c.unwrap())
    # c.analyze_circuit()
    
    # qsim = sim.OriginIR_Simulator()

    # result = qsim.simulate(c.circuit)

    # print(result)



    # c = Circuit()
    # c.h(0)
    # c.cnot(1, 0)
    # c.cnot(0, 2)
    # c.measure(0,1,2)
    # c = c.remapping({0:45, 1:46})