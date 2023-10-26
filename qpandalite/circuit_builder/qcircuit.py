'''
Definition of quantum circuit (Circuit)

Author: Agony5757
'''

from typing import Dict
from copy import deepcopy
from qpandalite.originir import OriginIR_Parser, OriginIR_BaseParser
import re

class CircuitControlContext:        
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
        c.circuit_str += ret        
        
    def __exit__(self, exc_type, exc_val, exc_tb):        
        ret = 'ENDCONTROL ' + self._qubit_list() + '\n'
        c.circuit_str += ret

class CircuitDagContext:      
    def __init__(self, c):
        self.c = c

    def __enter__(self):
        ret = 'DAGGER\n'
        c.circuit_str += ret        
        
    def __exit__(self, exc_type, exc_val, exc_tb):        
        ret = 'ENDDAGGER\n'
        c.circuit_str += ret

class Circuit:
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
        The function coverts OriginIR circuit into OpenQASM string.

        Returns:
        The OpenQASM version of the quantum circuit.

        
        OriginIR supports gates:
            'H':    operation, q = OriginIR_Parser.handle_1q(line)
            'X':    operation, q = OriginIR_Parser.handle_1q(line)
            'SX':   operation, q = OriginIR_Parser.handle_1q(line) - no support in qcircuit.py
            'Y':    operation, q = OriginIR_Parser.handle_1q(line)
            'Z':    operation, q = OriginIR_Parser.handle_1q(line)
            'CZ':   operation, q = OriginIR_Parser.handle_2q(line)
            'ISWAP':operation, q = OriginIR_Parser.handle_2q(line) - no support in qcircuit.py
            'XY':   operation, q = OriginIR_Parser.handle_2q(line) - no support in qcircuit.py
            'CNOT': operation, q = OriginIR_Parser.handle_2q(line)
            'RX':   operation, q, parameter = OriginIR_Parser.handle_1q1p(line)
            'RY':   operation, q, parameter = OriginIR_Parser.handle_1q1p(line)
            'RZ':   operation, q, parameter = OriginIR_Parser.handle_1q1p(line)
            'Rphi': operation, q, parameter = OriginIR_Parser.handle_1q2p(line)
        
        OpenQASM2 supports gates:
            gate h a { u2(0,pi) a; }
            gate x a { u3(pi,0,pi) a; }
            SX(NOT SUPPORTED)
            gate y a { u3(pi,pi/2,pi/2) a; }
            gate z a { u1(pi) a; }
            ---   CZ (    SUPPORTED)---
            ---iSWAP (NOT SUPPORTED)---
            ---   XY (NOT SUPPORTED)---
            gate cx c,t { CX c,t; }
            gate rx(theta) a { u3(theta,-pi/2,pi/2) a; }
            gate ry(theta) a { u3(theta,0,0) a; }
            gate rz(phi) a { u1(phi) a; }
            gate u3(theta,phi,lambda) q { U(theta,phi,lambda) q; } roughly equals to Rphi 

        
            // 2-parameter 1-pulse single qubit gate
            gate u2(phi,lambda) q { U(pi/2,phi,lambda) q; }
            // 1-parameter 0-pulse single qubit gate
            gate u1(lambda) q { U(0,0,lambda) q; }
            // idle gate (identity)
            gate id a { U(0,0,0) a; }            
            // Clifford gate: sqrt(Z) phase gate
            gate s a { u1(pi/2) a; }
            // Clifford gate: conjugate of sqrt(Z)
            gate sdg a { u1(-pi/2) a; }
            // C3 gate: sqrt(S) phase gate
            gate t a { u1(pi/4) a; }
            // C3 gate: conjugate of sqrt(S)
            gate tdg a { u1(-pi/4) a; }

        From OriginIR to OpenQASM2, we need to make sure that：
        
        1. The operation that is not in the OpenQASM need to be specified, 
        for example, gate iswap q0,q1 { s q0; s q1; h q0; cx q0,q1; cx q1,q0; h q1; }

        2. The operation from both OpenQASM and OriginIR that has the same name will have the same behavior,
        especially the rotation-theta. If not, some modification could be done with the help of u3, u2, u1.

            2.1 RX, RY are the same, and RZ has a phase factor difference.
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
                # print(new_line)
        # Join the transformed lines back into a single string
        ret = '\n'.join(transformed_lines)
        # modified_circ_str = self.covert_1q1p_qasm(modified_circ_str)
        # ret= '\n'.join([line.lower() + ';' for line in modified_circ_str.split('\n') if line.strip()])
        ret += "\n"
        # print(self.circuit_str)
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
        Convert the OriginIR representation into OpenQASM.
        
        Statements are separated by semicolons. 
        Whitespace is ignored. 
        The language is case sensitive. 
        Comments begin with a pair of forward slashes and end with a new line.

        For self-defined gate, one should use opaque to define

        Return:
            The OpenQASM2 representation of our circuit.
        """
        return self.make_header_qasm() + self.make_operation_qasm() + self.make_measure_qasm()

        # raise NotImplementedError('QASM support will be released in future.')

    def record_qubit(self, *qubits):
        for qubit in qubits:
            if qubit not in self.used_qubit_list:
                self.used_qubit_list.append(qubit)
                self.max_qubit = max(self.max_qubit, qubit)

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

    def rphi(self, qn, phi, theta) -> None:
        self.circuit_str += 'Rphi q[{}], ({}, {})\n'.format(qn, phi, theta)
        self.record_qubit(qn)

    def cnot(self, controller, target) -> None:
        self.circuit_str += 'CNOT q[{}], q[{}]\n'.format(controller, target)
        self.record_qubit(controller, target)

    def cz(self, q1, q2) -> None:
        self.circuit_str += 'CZ q[{}], q[{}]\n'.format(q1, q2)
        self.record_qubit(q1, q2)

    def measure(self, *qubits):
        self.record_qubit(*qubits)
        self.measure_list = list(qubits)

    def control(self, *args):
        c.record_qubit(*args)
        if len(args) == 0:
            raise ValueError('Controller qubit must not be empty.')
        return CircuitControlContext(self, args)
    
    def set_control(self, *args):    
        c.record_qubit(*args)    
        ret = 'CONTROL '
        for q in self.control_list:
            ret += f'q[{q}], '
        ret = ret[:-2] + '\n'
        c.circuit_str += ret

    def unset_control(self, *args):
        ret = 'ENDCONTROL '
        for q in self.control_list:
            ret += f'q[{q}], '
        ret = ret[:-2] + '\n'
        c.circuit_str += ret

    def dagger(self):
        return CircuitDagContext(self)
    
    def set_dagger(self):
        c.circuit_str += 'DAGGER\n'

    def unset_dagger(self):
        c.circuit_str += 'ENDDAGGER\n'

    def remapping(self, mapping : Dict[int, int]):
        # check if mapping is full
        for qubit in self.used_qubit_list:
            if qubit not in mapping:
                raise ValueError('At lease one qubit is not appeared in mapping. '
                                 f'(qubit : {qubit})')
            
        c = deepcopy(self)
        for old_qubit, new_qubit in mapping.items():
            c.circuit_str = c.circuit_str.replace(f'q[{old_qubit}]', f'q[{new_qubit}]')

        for i, old_qubit in enumerate(self.used_qubit_list):
            c.used_qubit_list[i] = mapping[old_qubit]

        for i, old_qubit in enumerate(self.measure_list):
            c.measure_list[i] = mapping[old_qubit]
            
        c.max_qubit = max(c.used_qubit_list)

        return c

    def unwrap(self):
        """
        This method is designed to process the given 'originir' and perform the 'unwrap' operation.

        Returns:
            unwrapped originir (list): List of OriginIR operations. 
            For example, the input will be,
            QINIT 2
            CREG 2
            H q[0]
            CONTROL q[0]
            X q[1]
            ENDCONTROL q[0]
            The return will be ["H q[0]", "X q[1] controlled q[0]"].

            NOTE: The control version string is still undecided., the string "X q[1] controlled q[0]" is temporary.
        Raises:
            None
        """

        parser = OriginIR_BaseParser()
        parser.parse(self.originir)
        return parser.to_extended_originir()

        ## !!!NOTE: The following are old codes. It will be permanently changed to the current version.

        # actual_used_operations = []
        # control_qubits_set = set()  # Using a set to manage nested/multiple CONTROL qubits uniquely
        # dagger_stack = []  # Stack to manage nested DAGGER operations
        # dagger_count = 0

        # lines = self.circuit_str.splitlines()
        # for i, line in enumerate(lines):
        #     # print(line)
        #     operation, qubits, cbit, parameter = OriginIR_Parser.parse_line(line.strip())
        #     # print(operation, qubits, cbit, parameter)
        #     if operation == "CONTROL":
        #         # Add all control qubits to the set
        #         control_qubits_set.update(qubits)

        #     elif operation == "ENDCONTROL":
        #         # Discard the mentioned qubits from the set
        #         for qubit in qubits:
        #             control_qubits_set.discard(qubit)

        #     elif operation == "DAGGER":
        #         # Add a new list to the stack to collect operations inside this DAGGER block
        #         dagger_stack.append([])
        #         dagger_count += 1

        #     elif operation == "ENDDAGGER":
        #         # Pop the latest list of operations from the dagger stack and reverse them
        #         if dagger_stack:
        #             reversed_ops = dagger_stack.pop()
        #             actual_used_operations.extend(reversed_ops[::-1])
        #         dagger_count -= 1
            
        #     else:
        #         # This is in-between CONTROL & DAGGER, use this "else" to process strings
        #         operation_line = line.strip()
        #         # print(operation_line)
        #         # First to check whether the operation has the control qubit(s).
        #         if control_qubits_set:
        #             operation_line += " controlled"
        #             # Sorting qubits before appending to ensure the order
        #             for control_qubit in sorted(control_qubits_set, reverse=True):
        #                 operation_line += f" {control_qubit}"
                
        #         if dagger_stack and (dagger_count % 2 == 1):
        #             operation_line += " dagger"
        #             dagger_stack[-1].append(operation_line)  # Add to the latest DAGGER block
        #         else:
        #             actual_used_operations.append(operation_line)

        # # Handle remaining operations within the DAGGER blocks (if any)
        # while dagger_stack:
        #     reversed_ops = dagger_stack.pop()
        #     actual_used_operations.extend(reversed_ops[::-1])

        # return actual_used_operations
        
    def analyze_circuit(self):
        """
        Analyze the stored circuit_str and update circuit_info
        """
        parser = OriginIR_BaseParser()
        parser.parse(self.originir)
        
        self.circuit_info['qubits'] = parser.n_qubit
        # Now in the parser.program_body, there are lines in the form of 
        # (operation, qubits, cbit, parameter, dagger_flag, deepcopy(control_qubits_set)).

        # qinit_pattern = re.compile(r"QINIT (\d+)")
        # gate_pattern = re.compile(r"(\w+) q\[(\d+)\](?:, q\[(\d+)\])?")
        # measure_pattern = re.compile(r"MEASURE q\[(\d+)\], c\[(\d+)\]")
        print(self.circuit_info['qubits'])
        for single_command in parser.program_body:
            (operation, qubits, cbit, parameter, dagger_flag, control_qubits_set) = single_command
            # # Match QINIT
            # match = qinit_pattern.match(line)
            # if match:
            #     self.circuit_info['qubits'] = int(match.group(1))
            #     continue

            # # Match gates
            # match = gate_pattern.match(line)
            # if match:
            #     gate = match.group(1)
            #     self.circuit_info['gates'][gate] = self.circuit_info['gates'].get(gate, 0) + 1
            #     continue

            # Match MEASURE
            
            if operation == "MEASURE":
                qubit = int(qubits)
                output = int(cbit)
                self.circuit_info['measurements'].append({'qubit': qubit, 'output': f'c[{output}]'})
        
        print(self.circuit_info)
        # return parser.to_extended_originir()

# def transform_line(line, circuit):
#     # Match the cx operation
#     match_cx = re.match(r'cx q\[(\d+)\],q\[(\d+)\];', line)
#     if match_cx:
#         qubit1, qubit2 = map(int, match_cx.groups())
#         circuit.cnot(qubit1, qubit2)
    
#     # Match other operations, for example, h gate
#     match_h = re.match(r'h q\[(\d+)\];', line)
#     if match_h:
#         qubit = int(match_h.group(1))
#         circuit.h(qubit)
    
#     # Handling measure operation
#     match_measure = re.match(r'measure q\[(\d+)\] -> c\[\d+\];', line)
#     if match_measure:
#         qubit = int(match_measure.group(1))
#         circuit.measure_list.append(qubit)
        # return None 


if __name__ == '__main__':
    import qpandalite
    import qpandalite.simulator as sim
    from qiskit import QuantumCircuit
    import numpy as np
    import math

    from qpandalite.qasm_origin import OpenQASM2_Parser
    # # The quantum circuit in qiskit
    # circ = QuantumCircuit(3)
    
    # circ.h(0)
    # circ.rx(0.4, 0)
    # circ.x(0)
    # circ.ry(3*math.pi/4, 1)
    # circ.y(0)
    # circ.rz(math.pi/3, 1)
    # circ.z(0)
    # circ.cz(0, 1)
    # circ.cx(0, 2) 

    # # circ.sx(0)
    # # circ.iswap(0, 1)
    # # circ.cz(0, 2)
    # # circ.ccx(0, 1, 2)
    # # Create a Quantum Circuit
    # meas = QuantumCircuit(3, 3)
    # meas.measure(range(3), range(3))
    # circ = meas.compose(circ, range(3), front=True)
    # qasm_string = circ.qasm()
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
        c.x(2)
        with c.control(4,5):
            c.x(3)

    # Control-dagger-nested
    with c.control(2):
        c.x(4)
        with c.dagger():
            c.z(5)
            c.x(10)
            with c.control(0,1):
                c.x(3)

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
    
    # print(c.circuit)
    # print(c.unwrap())
    c.analyze_circuit()
    
    # qsim = sim.OriginIR_Simulator()

    # result = qsim.simulate(c.circuit)

    # print(result)
