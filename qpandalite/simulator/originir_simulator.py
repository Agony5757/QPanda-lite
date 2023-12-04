from typing import List, Tuple, TYPE_CHECKING
from qpandalite.originir.originir_base_parser import OriginIR_BaseParser
import warnings

from QPandaLitePy import *

if TYPE_CHECKING:
    from .QPandaLitePy import *

class OriginIR_Simulator:    
    def __init__(self, reverse_key = False):
        '''OriginIR_Simulator is a quantum circuit simulation based on C++ which runs locally on your PC.

        Args:
            reverse_key (bool, optional): _description_. Defaults to False.
        '''
        self.qubit_num = 0
        self.simulator = None
        self.measure_qubit = []
        self.qubit_mapping = dict()
        self.reverse_key = reverse_key
        self.parser = OriginIR_BaseParser()
        
    def _clear(self):
        self.qubit_num = 0
        self.measure_qubit = []
        self.qubit_mapping = dict()
        self._make_simulator()

    def _make_simulator(self):        
        self.simulator = Simulator()

    def simulate_gate(self, operation, qubit, cbit, parameter, is_dagger):
        if operation == 'RX':
            self.simulator.rx(self.qubit_mapping[int(qubit)], parameter, is_dagger)
        elif operation == 'RY':
            self.simulator.ry(self.qubit_mapping[int(qubit)], parameter, is_dagger)
        elif operation == 'RZ':
            self.simulator.rz(self.qubit_mapping[int(qubit)], parameter, is_dagger)
        elif operation == 'H':
            self.simulator.hadamard(self.qubit_mapping[int(qubit)], is_dagger)
        elif operation == 'X':
            self.simulator.x(self.qubit_mapping[int(qubit)], is_dagger)
        elif operation == 'SX':
            self.simulator.sx(self.qubit_mapping[int(qubit)], is_dagger)
        elif operation == 'Y':
            self.simulator.y(self.qubit_mapping[int(qubit)], is_dagger)
        elif operation == 'Z':
            self.simulator.z(self.qubit_mapping[int(qubit)], is_dagger)
        elif operation == 'CZ':
            self.simulator.cz(self.qubit_mapping[int(qubit[0])], 
                              self.qubit_mapping[int(qubit[1])], is_dagger)
        elif operation == 'ISWAP':
            self.simulator.iswap(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])], is_dagger)
        elif operation == 'XY':
            self.simulator.xy(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])], is_dagger)
        elif operation == 'CNOT':
            self.simulator.cnot(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])], is_dagger)
        elif operation == 'RPhi':
            self.simulator.rphi(self.qubit_mapping[int(qubit)], 
                                parameter[0], parameter[1], is_dagger)  
        elif operation == 'MEASURE':
            # In fact, I don't know the real implementation
            # This is a guessed implementation.
            self.measure_qubit.append((self.qubit_mapping[int(qubit)], int(cbit)))
        elif operation == None:
            pass
        elif operation == 'QINIT':
            pass
        elif operation == 'CREG':
            pass
        elif operation == 'BARRIER':
            pass
        else:
            raise RuntimeError('Unknown OriginIR operation. '
                               f'Operation: {operation}.')

    def _add_used_qubit(self, qubit):
        if qubit in self.qubit_mapping:
            return
        
        n = len(self.qubit_mapping)
        self.qubit_mapping[qubit] = n

    def extract_actual_used_qubits(self, program_body):
        for (operation, qubit, cbit, parameter, 
             dagger_flag, control_qubits_set) in program_body:
                        
            if isinstance(qubit, list):
                for q in qubit:
                    self._add_used_qubit(int(q))
            else:
                self._add_used_qubit(int(qubit))

    def check_topology(self, available_qubits : List[int] = None):        
        used_qubits = list(self.qubit_mapping.keys())
        
        # check qubits
        for used_qubit in used_qubits:
            if used_qubit not in available_qubits:                
                raise ValueError('A invalid qubit is used. '
                                 f'Available qubits: {available_qubits}\n'
                                 f'Used: {used_qubit}.')

    def simulate(self, 
                 originir, 
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None):
        '''Simulate originir.
        Free mode: let available_qubits = None, then simulate any topology.
        Strict mode: input available_qubits and available_topology, then the originir is automatically checked.

        Args:
            originir (str): OriginIR.
            available_qubits (List[int], optional): Available qubits (if need checking). Defaults to None.
            available_topology (list[Tuple[int, int]], optional): Available topology (if need checking). Defaults to None.

        Returns:
            _type_: _description_
        '''
        # extract the actual used qubit, and build qubit mapping
        # like q45 -> 0, q46 -> 1, etc..
        self._clear()
        self.parser.parse(originir)
        self.extract_actual_used_qubits(self.parser.program_body)

        if available_qubits:
            self.check_topology(available_qubits)

        self.simulator.init_n_qubit(len(self.qubit_mapping))
        
        lines = self.parser.originir
        splitted_lines = lines.splitlines()
        
        for i, opcode in enumerate(self.parser.program_body):            
            (operation, qubit, cbit, parameter, 
             dagger_flag, control_qubits_set) = opcode
            if isinstance(qubit, list) and (available_topology):
                if len(qubit) > 2:                    
                    # i+2 because QINIT CREG are always excluded.
                    raise ValueError('Real chip does not support gate of 3-qubit or more. '
                                     'The dummy server does not support either. '
                                     'You should consider decomposite it. \n'
                                     f'Line {i + 2} ({splitted_lines[i + 2]}).')
                
                if ([int(qubit[0]), int(qubit[1])] not in available_topology) and \
                   ([int(qubit[1]), int(qubit[0])] not in available_topology):
                    # i+2 because QINIT CREG are always excluded.
                    raise ValueError('Unsupported topology.\n'
                                     f'Line {i + 2} ({splitted_lines[i + 2]}).')
                    
            self.simulate_gate(operation, qubit, cbit, parameter, dagger_flag)
        
        self.qubit_num = len(self.qubit_mapping)
        measure_qubit_cbit = sorted(self.measure_qubit, key = lambda k : k[1], reverse=self.reverse_key)
        measure_qubit = []
        for qubit in measure_qubit_cbit:
            measure_qubit.append(qubit[0])
        prob_list = self.simulator.pmeasure(measure_qubit)
        return prob_list
    
    @property
    def state(self):
        return self.simulator.state


class OriginIR_NoisySimulator(OriginIR_Simulator):
    def __init__(self, noise_description, gate_noise_description={}, reverse_key=False):
        # Initialize noise-related attributes
        self.noise_description = noise_description
        self.gate_noise_description = gate_noise_description
        # Initialize the superclass with the reverse_key parameter
        super().__init__(reverse_key=reverse_key)

    def _make_simulator(self):
        # Overriding the parent class's _make_simulator method
        # to create an instance of NoisySimulator instead of Simulator
        self.simulator = NoisySimulator(self.qubit_num, self.noise_description, self.gate_noise_description)

    def simulate_gate(self, operation, qubit, cbit, parameter, is_dagger):
        # print(operation, qubit, cbit, parameter, is_dagger)
        if operation == 'RX':
            self.simulator.rx(self.qubit_mapping[int(qubit)], parameter, is_dagger)
        elif operation == 'RY':
            self.simulator.ry(self.qubit_mapping[int(qubit)], parameter, is_dagger)
        elif operation == 'RZ':
            self.simulator.rz(self.qubit_mapping[int(qubit)], parameter, is_dagger)
        elif operation == 'H':
            self.simulator.hadamard(self.qubit_mapping[int(qubit)], is_dagger)
        elif operation == 'X':
            self.simulator.x(self.qubit_mapping[int(qubit)], is_dagger)
        elif operation == 'SX':
            self.simulator.sx(self.qubit_mapping[int(qubit)], is_dagger)
        elif operation == 'Y':
            self.simulator.y(self.qubit_mapping[int(qubit)], is_dagger)
        elif operation == 'Z':
            self.simulator.z(self.qubit_mapping[int(qubit)], is_dagger)
        elif operation == 'CZ':
            self.simulator.cz(self.qubit_mapping[int(qubit[0])], 
                              self.qubit_mapping[int(qubit[1])], is_dagger)
        elif operation == 'ISWAP':
            self.simulator.iswap(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])], is_dagger)
        elif operation == 'XY':
            self.simulator.xy(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])], is_dagger)
        elif operation == 'CNOT':
            self.simulator.cnot(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])], is_dagger)
        elif operation == 'RPhi':
            self.simulator.rphi(self.qubit_mapping[int(qubit)], 
                                parameter[0], parameter[1], is_dagger)  
        elif operation == 'MEASURE':
            # In fact, I don't know the real implementation
            # This is a guessed implementation.
            self.measure_qubit.append((self.qubit_mapping[int(qubit)], int(cbit)))
            # pass
        elif operation == None:
            pass
        elif operation == 'QINIT':
            pass
        elif operation == 'CREG':
            pass
        elif operation == 'BARRIER':
            pass
        else:
            raise RuntimeError('Unknown OriginIR operation. '
                               f'Operation: {operation}.')

    def simulate(self, 
                 originir, 
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None):
        '''Simulate originir.
        Free mode: let available_qubits = None, then simulate any topology.
        Strict mode: input available_qubits and available_topology, then the originir is automatically checked.

        Args:
            originir (str): OriginIR.
            available_qubits (List[int], optional): Available qubits (if need checking). Defaults to None.
            available_topology (list[Tuple[int, int]], optional): Available topology (if need checking). Defaults to None.

        Returns:
            _type_: _description_
        '''
        # extract the actual used qubit, and build qubit mapping
        # like q45 -> 0, q46 -> 1, etc..
        self._clear()
        self.parser.parse(originir)
        self.extract_actual_used_qubits(self.parser.program_body)
        self.simulator = NoisySimulator(len(self.qubit_mapping), self.noise_description, self.gate_noise_description)

        if available_qubits:
            self.check_topology(available_qubits)
        
        lines = self.parser.originir
        splitted_lines = lines.splitlines()
        
        for i, opcode in enumerate(self.parser.program_body):            
            (operation, qubit, cbit, parameter, 
             dagger_flag, control_qubits_set) = opcode
            if isinstance(qubit, list) and (available_topology):
                if len(qubit) > 2:                    
                    # i+2 because QINIT CREG are always excluded.
                    raise ValueError('Real chip does not support gate of 3-qubit or more. '
                                     'The dummy server does not support either. '
                                     'You should consider decomposite it. \n'
                                     f'Line {i + 2} ({splitted_lines[i + 2]}).')
                
                if ([int(qubit[0]), int(qubit[1])] not in available_topology) and \
                   ([int(qubit[1]), int(qubit[0])] not in available_topology):
                    # i+2 because QINIT CREG are always excluded.
                    raise ValueError('Unsupported topology.\n'
                                     f'Line {i + 2} ({splitted_lines[i + 2]}).')
                    
            self.simulate_gate(operation, qubit, cbit, parameter, dagger_flag)
        
        self.qubit_num = len(self.qubit_mapping)
        # measure_qubit_cbit = sorted(self.measure_qubit, key = lambda k : k[1], reverse=self.reverse_key)
        # measure_qubit = []
        # for qubit in measure_qubit_cbit:
        #     measure_qubit.append(qubit[0])
        # prob_list = self.simulator.measure_shots(1024)
        # return prob_list
    
    @property
    def state(self):
        return self.simulator.state

