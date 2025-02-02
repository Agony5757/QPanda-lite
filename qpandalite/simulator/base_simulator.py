# generic simulator class for qpanda-lite

from typing import Dict, List, Optional, Tuple, Union
from .opcode_simulator import OpcodeSimulator

QubitType = Union[List[int], int]
CbitType = Union[List[int], int]
ParameterType = Optional[Union[List[float], float]]
OpcodeType = Tuple[str, QubitType, CbitType, ParameterType, bool, set]

class TopologyError(Exception):
    pass

class BaseSimulator:
    # This class describes some common behaviors of simulators.
    # It is not designed to be used directly.
    # Instead, it should be subclassed by specific simulators.

    def __init__(self, backend_type = 'statevector',                                  
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None,
                 **extra_kwargs):
        
        self.qubit_num = 0
        self.available_qubits = available_qubits
        self.available_topology = available_topology
        self.program_body : List[OpcodeType] = list()
        self.qubit_mapping : Dict[int, int] = dict()
        self.backend_type = backend_type
        self.opcode_simulator = OpcodeSimulator(self.backend_type)
        self.parser = None  # Note: parser must be set by subclass.
        self._handle_kwargs(extra_kwargs)

    def _handle_kwargs(self, kwargs):
        pass

    def _clear(self):        
        self.qubit_num = 0
        self.measure_qubit = []
        self.qubit_mapping = dict()
        self.opcode_simulator = OpcodeSimulator(self.backend_type)  

    def _add_used_qubit(self, qubit):
        if qubit in self.qubit_mapping:
            return
        
        n = len(self.qubit_mapping)
        self.qubit_mapping[qubit] = n

    def _extract_actual_used_qubits(self, program_body):
        for (operation, qubit, cbit, parameter, dagger_flag, control_qubits_set) in program_body:                        
            if isinstance(qubit, list):
                for q in qubit:
                    self._add_used_qubit(int(q))
            else:
                self._add_used_qubit(int(qubit))
    
    def _check_available_qubits(self):        
        used_qubits = list(self.qubit_mapping.keys())
        
        # check qubits
        for used_qubit in used_qubits:
            if used_qubit not in self.available_qubits:                
                raise TopologyError('A invalid qubit is used. '
                                 f'Available qubits: {self.available_qubits}\n'
                                 f'Used: {used_qubit}.')
    
    def _check_topology(self, qubit):
        if len(qubit) > 2:                    
            # i+2 because QINIT CREG are always excluded.
            raise TopologyError('Real chip does not support gate of 3-qubit or more. '
                                'The dummy server does not support either. '
                                'You should consider decomposite it.')
        
        if ([int(qubit[0]), int(qubit[1])] not in self.available_topology) and \
            ([int(qubit[1]), int(qubit[0])] not in self.available_topology):
            # i+2 because QINIT CREG are always excluded.
            raise TopologyError('Unsupported topology.')
    
    def _process_program_body(self) -> List[OpcodeType]:
        processed_program_body = list()
        program_body = self.parser.program_body

        for i, opcode in enumerate(program_body):            
            (operation, qubit, cbit, parameter, 
             dagger_flag, control_qubits_set) = opcode
            
            if self.available_topology and isinstance(qubit, list):
                try:
                    self._check_topology(qubit)         
                except TopologyError as e:
                    raise ValueError(f'Error in line {i+1}: \n'
                                     f'Opcode: {opcode}\n'
                                     f'Errorinfo: {e}')
            
            if qubit is not None:
                if isinstance(qubit, list):
                    mapped_qubit = [self.qubit_mapping[q] for q in qubit]
                else:
                    mapped_qubit = self.qubit_mapping[qubit]

            processed_program_body.append((operation, mapped_qubit, cbit, parameter, dagger_flag, control_qubits_set))
        
        return processed_program_body
    
    def _process_measure(self):
        # perform qubit mapping and check if cbit has duplicates
        processed_measure_qubits = []
        used_cbit = set()
        measure_qubits = self.parser.measure_qubits

        for qubit, cbit in measure_qubits:
            mapped_qubit = self.qubit_mapping[qubit]
            if cbit in used_cbit:
                raise ValueError('Duplicate cbit in measure instruction.')
            
            used_cbit.add(cbit)
            processed_measure_qubits.append((mapped_qubit, cbit))

        return processed_measure_qubits

    def simulate_preprocess(self, originir):
        # extract the actual used qubit, and build qubit mapping
        # like q45 -> 0, q46 -> 1, etc..
        self._clear()
        self.parser.parse(originir)

        # update self.qubit_mapping
        self._extract_actual_used_qubits()

        if self.available_qubits or self.available_topology:
            self._check_available_qubits()
        
        processed_program_body = self._process_program_body()
        measure_qubit = self._process_measure()
        
        self.qubit_num = len(self.qubit_mapping)
        measure_qubit_cbit = sorted(measure_qubit, key = lambda k : k[1], reverse=False)
        measure_qubit = []
        for qubit in measure_qubit_cbit:
            measure_qubit.append(qubit[0])

        return processed_program_body, measure_qubit

    def simulate_pmeasure(self, *args, **kwargs):
        raise NotImplementedError('This method should be implemented by subclass.')

    def simulate_statevector(self, *args, **kwargs):
        raise NotImplementedError('This method should be implemented by subclass.')

    def simulate_density_matrix(self, *args, **kwargs):
        raise NotImplementedError('This method should be implemented by subclass.')

    def simulate_single_shot(self, *args, **kwargs):
        raise NotImplementedError('This method should be implemented by subclass.')
    
    def simulate_shots(self, *args, **kwargs):
        raise NotImplementedError('This method should be implemented by subclass.')