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

    def make_measure(self):
        ret = ''
        for i, meas_qubit in enumerate(self.measure_list):
            ret += 'MEASURE q[{}], c[{}]\n'.format(meas_qubit, i)
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
        raise NotImplementedError('QASM support will be released in future.')

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
        """Analyze the stored circuit_str and update circuit_info."""
        
        # TODO: should be updated to using OriginIR_BaseParser.
        qinit_pattern = re.compile(r"QINIT (\d+)")
        gate_pattern = re.compile(r"(\w+) q\[(\d+)\](?:, q\[(\d+)\])?")
        measure_pattern = re.compile(r"MEASURE q\[(\d+)\], c\[(\d+)\]")

        for line in self.circuit_str.strip().split("\n"):
            # Match QINIT
            match = qinit_pattern.match(line)
            if match:
                self.circuit_info['qubits'] = int(match.group(1))
                continue

            # Match gates
            match = gate_pattern.match(line)
            if match:
                gate = match.group(1)
                self.circuit_info['gates'][gate] = self.circuit_info['gates'].get(gate, 0) + 1
                continue

            # Match MEASURE
            match = measure_pattern.match(line)
            if match:
                qubit = int(match.group(1))
                output = int(match.group(2))
                self.circuit_info['measurements'].append({'qubit': qubit, 'output': f'c[{output}]'})


if __name__ == '__main__':
    import qpandalite
    import qpandalite.simulator as sim
    c = Circuit()
    c.h(6)
    c.h(7)

    # Single control(Correct)
    # with c.control(0, 1, 2):
    #     c.x(4)
    
    # Single dagger(Correct)
    # with c.dagger():
    #     c.z(5)
    #     c.x(10)

    # Nested-dagger
    with c.dagger():
        c.z(2)
        with c.dagger():
            c.z(5)
            c.x(10)

    # Nested-control(Correct)
    # with c.control(0,1):
    #     c.x(2)
    #     with c.control(4,5):
    #         c.x(3)

    # Control-dagger-nested
    # with c.control(2):
    #     c.x(4)
    #     with c.dagger():
    #         c.z(5)
    #         c.x(10)
    #         with c.control(0,1):
    #             c.x(3)

    # Dagger-control-nested
    # with c.dagger():
    #     c.z(5)
    #     c.x(10)
    #     with c.control(0,1):
    #         c.x(3)
    
    c.h(8)
    c.h(9)
    c.measure(0,1,2,3,4)
    # c = c.remapping({0:45, 1:46, 2:52, 3:53})
    
    print(c.circuit)
    print(c.unwrap())
    # c.analyze_circuit()
    
    # qsim = sim.OriginIR_Simulator()

    # result = qsim.simulate(c.circuit)

    # print(result)
