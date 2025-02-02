# generic simulator class for qpanda-lite

import random
from typing import Dict, List
import numpy as np

from .error_model import ErrorLoader
from .opcode_simulator import OpcodeSimulator
from qpandalite.circuit_builder.qcircuit import OpcodeType


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

    def _handle_kwargs(self, kwargs : dict):
        # Least qubit remapping is to map the qubits to the least available qubits.
        # This can be useful when we only use a part of the qubits in the chip.
        # By default, we use this feature.
        # If you want to disable it, set least_qubit_remapping=False.
        self.least_qubit_remapping = kwargs.pop('least_qubit_remapping', True)

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

    def _extract_actual_used_qubits(self):        
        # extract from program
        program_body = self.parser.program_body
        for (operation, qubit, cbit, parameter, dagger_flag, control_qubits_set) in program_body:                        
            if isinstance(qubit, list):
                for q in qubit:
                    self._add_used_qubit(int(q))
            else:
                self._add_used_qubit(int(qubit))

        # extract from measure
        measure_qubits = self.parser.measure_qubits
        for qubit, cbit in measure_qubits:
            self._add_used_qubit(qubit)

        if not self.least_qubit_remapping:
            self.qubit_num = max(self.qubit_mapping.keys()) + 1
            self.qubit_mapping = {q : q for q in range(self.qubit_num)}
        else:
            self.qubit_num = max(self.qubit_mapping.values()) + 1
    
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
        
        # self.qubit_num = len(self.qubit_mapping)
        measure_qubit_cbit = sorted(measure_qubit, key = lambda k : k[1], reverse=False)
        measure_qubit = []
        for qubit in measure_qubit_cbit:
            measure_qubit.append(qubit[0])

        return processed_program_body, measure_qubit
    
    def simulate_pmeasure(self, quantum_code):
        program_body, measure_qubit = self.simulate_preprocess(quantum_code)
        
        prob_list = self.opcode_simulator.simulate_opcodes_pmeasure(
            self.qubit_num, program_body, measure_qubit
        )

        return prob_list

    def simulate_statevector(self, quantum_code):
        program_body, measure_qubit = self.simulate_preprocess(quantum_code)

        statevector = self.opcode_simulator.simulate_opcodes_statevector(
            self.qubit_num, program_body
        )

        return statevector
    
    def simulate_stateprob(self, quantum_code):
        program_body, measure_qubit = self.simulate_preprocess(quantum_code)

        stateprob = self.opcode_simulator.simulate_opcodes_stateprob(
            self.qubit_num, program_body
        )

        return stateprob

    def simulate_density_matrix(self, quantum_code):
        program_body, measure_qubit = self.simulate_preprocess(quantum_code)

        density_matrix = self.opcode_simulator.simulate_opcodes_density_operator(
            self.qubit_num, program_body
        )

        return density_matrix
    
    def simulate_single_shot(self, quantum_code):
        processed_program_body, measure_qubit = self.simulate_preprocess(quantum_code)
        
        result = self.opcode_simulator.simulate_opcodes_shot(
            self.qubit_num, processed_program_body, measure_qubit)
        
        return result
    
    def simulate_shots(self, quantum_code, shots):
        processed_program_body, measure_qubit = self.simulate_preprocess(quantum_code)

        # results = {}
        # for _ in range(shots):
        #     result = self.opcode_simulator.simulate_opcodes_shot(
        #         self.qubit_num, processed_program_body, measure_qubit)
            
        #     results[result] = results.get(result, 0) + 1

        # get pmeasured result
        pmeasured_result = self.simulate_pmeasure(quantum_code)
        cum_weights = []
        cumulative = 0
        for prob in pmeasured_result:
            cumulative += prob
            cum_weights.append(cumulative)
        
        result = {}
        # sample shots times from pmeasured result
        for _ in range(shots):
            shot_result = random.choices(range(len(pmeasured_result)), cum_weights=cum_weights, k=1)[0]
            result[shot_result] = result.get(shot_result, 0) + 1

        return result
        
    @property
    def simulator(self):
        return self.opcode_simulator.simulator

    @property
    def state(self):
        return self.opcode_simulator.simulator.state
    
class BaseNoisySimulator(BaseSimulator):

    def __init__(self, 
                 backend_type = 'statevector',                 
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None,
                 error_loader : ErrorLoader = None,
                 readout_error : Dict[int, List[float]]={}):
        super().__init__(backend_type, available_qubits, available_topology)        
        self.readout_error = readout_error
        self.error_loader = error_loader 

    def _add_readout_error_pmeasure(self, prob_list, measure_qubit):
        # add measurement error to the result from simulate_pmeasure

        processed_measure_error_list = []
        for i, qubit in enumerate(measure_qubit):
            if qubit in self.readout_error:
                error_rate01 = self.readout_error[qubit][0]
                error_rate10 = self.readout_error[qubit][1]
                error_rate = np.array([[1-error_rate01, error_rate10], [error_rate01, 1-error_rate10]])
                processed_measure_error_list.append((i, error_rate))
        
        def _apply_matrix_to_prob_list(prob_list, qn, error_rate, measure_qubit_length):
            # apply the error_rate to the i-th qubit
            step = 2 ** qn
            for i in range(0, 2 ** measure_qubit_length, 2 * step):
                for j in range(i, i + step):
                    # 提取子空间
                    subspace = np.array([prob_list[j], prob_list[j + step]])
                    # 应用矩阵
                    new_subspace = np.dot(error_rate, subspace)
                    # 更新状态向量
                    prob_list[j], prob_list[j + step] = new_subspace[0], new_subspace[1]

            return prob_list
        
        # perform measurement error like a quantum gate simulation
        for i, error_rate in processed_measure_error_list:
            prob_list =_apply_matrix_to_prob_list(prob_list, i, error_rate, len(measure_qubit))

        return prob_list


    def _add_readout_error_single_shot(self, result, measure_qubit):
        # add measurement error to the result
        
        # to binary and reverse
        measure_length = len(measure_qubit)
        result_binary = bin(result)[2:].zfill(measure_length)[::-1]

        result_binary_list = [bit for bit in result_binary]
        # decide each measurement qubit has error or not
        r = random.random()
        for i in range(measure_length):
            measure_qubit_index = measure_qubit[i]
            measure_to = result_binary_list[i]
            error_rate01 = self.readout_error.get(measure_qubit_index, [0, 0])
            if measure_to == '0':
                rate = error_rate01[0]
            elif measure_to == '1':
                rate = error_rate01[1]
            else:
                raise ValueError(f'Unexpected measurement result {measure_to} (neither 0 nor 1).')
            if r < rate:
                result_binary_list[i] = '1' if measure_to == '0' else '0'

        # to decimal (first flip the list, then join the bits)
        result = int(''.join(result_binary_list[::-1]), 2)

        return result
    

    def simulate_preprocess(self, originir):
        processed_program_body, measure_qubit = super().simulate_preprocess(originir)
        if self.error_loader:
            # replace the original program_body with the error-injected program_body
            self.error_loader.process_opcodes(processed_program_body)
            processed_program_body = self.error_loader.opcodes

        return processed_program_body, measure_qubit
        

    def simulate_statevector(self, originir):
        raise NotImplementedError('Noisy simulator does not support statevector.')
    

    def simulate_density_matrix(self, originir):
        if self.opcode_simulator.simulator_typestr == 'density_operator':
            density_matrix = super().simulate_density_matrix(originir)
            if self.readout_error:
                raise NotImplementedError('density_matrix simulation does not support measurement error yet.')
                return self._add_readout_error_density_matrix(density_matrix)
            else:
                return density_matrix
        else:
            raise ValueError('simulate_density_matrix is only available for density_operator type OpcodeSimulator backend.')
    
    
    def simulate_pmeasure(self, originir):
        if self.opcode_simulator.simulator_typestr == 'density_operator':
            processed_program_body, measure_qubit = self.simulate_preprocess(originir)
                
            prob_list = self.opcode_simulator.simulate_opcodes_pmeasure(
                self.qubit_num, processed_program_body, measure_qubit)
        
            if self.readout_error:
                return self._add_readout_error_pmeasure(prob_list, measure_qubit)
            else:
                return prob_list
            
        else:
            raise ValueError('simulate_pmeasure is only available for density_operator type OpcodeSimulator backend.')


    def simulate_single_shot(self, originir):
        '''Simulate originir with error model.
        Free mode: let available_qubits = None, then simulate any topology.
        Strict mode: input available_qubits and available_topology, then the originir is automatically checked.

        Args:
            originir (str): OriginIR.
        Returns:
            int: The sampled output from the ideal simulator

        Note: Measurement protocol.

        For measurement qubits, the result is returned in decimal form. Suppose the measure_qubit is [q0, q1, q2], and result is b0, b1, b2, then the decimal form is:

        result = b2b1b0
        '''
        processed_program_body, measure_qubit = self.simulate_preprocess(originir)

        result = self.opcode_simulator.simulate_opcodes_shot(
            self.qubit_num, processed_program_body, measure_qubit)
        
        if self.readout_error:
            result = self._add_readout_error_single_shot(result, measure_qubit)
        return result
    
    def simulate_shots(self, quantum_code, shots):
        processed_program_body, measure_qubit = self.simulate_preprocess(quantum_code)

        results = {}
        for _ in range(shots):
            result = self.opcode_simulator.simulate_opcodes_shot(
                self.qubit_num, processed_program_body, measure_qubit)
            
            if self.readout_error:
                result = self._add_readout_error_single_shot(result, measure_qubit)
            
            results[result] = results.get(result, 0) + 1

        return results