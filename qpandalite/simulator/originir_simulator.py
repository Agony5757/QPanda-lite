import random
from typing import List, Tuple, TYPE_CHECKING, Union
from qpandalite.originir.originir_base_parser import OriginIR_BaseParser
import warnings
from .opcode_simulator import OpcodeSimulator
from .base_simulator import BaseSimulator
from .error_model import *

if TYPE_CHECKING:
    from .QPandaLitePy import *

class OriginIR_Simulator(BaseSimulator):    
        
    def __init__(self, 
                 backend_type = 'statevector',                 
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None):
        '''OriginIR_Simulator is a quantum circuit simulation based on C++ which runs locally on your PC.
        

        Args:
            reverse_key (bool, optional): Whether to reverse the qubit index when performing measurements. Defaults to False.            
            backend_type (str, optional): The backend type. Defaults to 'statevector'. (optional = 'statevector', 'densitymatrix')
            available_qubits (List[int], optional): Available qubits (if need checking). Defaults to None.
            available_topology (list[Tuple[int, int]], optional): Available topology (if need checking). Defaults to None.
        '''
        super().__init__(backend_type, available_qubits, available_topology)
        self.parser = OriginIR_BaseParser()
        self.splitted_lines = None
    
    def _process_program_body(self):
        
        lines = self.parser.originir
        self.splitted_lines = lines.splitlines()

        processed_program_body = list()
        available_topology = self.available_topology
        program_body = self.parser.program_body

        for i, opcode in enumerate(program_body):            
            (operation, qubit, cbit, parameter, 
             dagger_flag, control_qubits_set) = opcode
                        
            if isinstance(qubit, list) and (available_topology):
                if len(qubit) > 2:                    
                    # i+2 because QINIT CREG are always excluded.
                    raise ValueError('Real chip does not support gate of 3-qubit or more. '
                                     'The dummy server does not support either. '
                                     'You should consider decomposite it. \n'
                                     f'Line {i + 2} ({self.splitted_lines[i + 2]}).')
                
                if ([int(qubit[0]), int(qubit[1])] not in available_topology) and \
                   ([int(qubit[1]), int(qubit[0])] not in available_topology):
                    # i+2 because QINIT CREG are always excluded.
                    raise ValueError('Unsupported topology.\n'
                                     f'Line {i + 2} ({self.splitted_lines[i + 2]}).')
            
            if qubit is not None:
                if isinstance(qubit, list):
                    mapped_qubit = [self.qubit_mapping[q] for q in qubit]
                else:
                    mapped_qubit = self.qubit_mapping[qubit]

            if operation == 'MEASURE':
                # In fact, I don't know the real implementation
                # This is a guessed implementation.
                self.measure_qubit.append((mapped_qubit, cbit))
            else:
                processed_program_body.append((operation, mapped_qubit, cbit, parameter, dagger_flag, control_qubits_set))
        
        return processed_program_body

    def _clear(self):
        super()._clear()
        self.parser = OriginIR_BaseParser()
        self.splitted_lines = None

    def simulate_pmeasure(self, originir):
        '''Simulate originir.
        Free mode: let available_qubits = None, then simulate any topology.
        Strict mode: input available_qubits and available_topology, then the originir is automatically checked.

        Args:
            originir (str): OriginIR.
        Returns:
            List[float]: The probability list of output from the ideal simulator
        '''
        processed_program_body, measure_qubit = self.simulate_preprocess(originir)
            
        prob_list = self.opcode_simulator.simulate_opcodes_pmeasure(
            self.qubit_num, processed_program_body, measure_qubit)
        
        return prob_list
    
    def simulate_statevector(self, originir):
        '''Simulate originir.
        Free mode: let available_qubits = None, then simulate any topology.
        Strict mode: input available_qubits and available_topology, then the originir is automatically checked.

        Args:
            originir (str): OriginIR.
        Returns:
            List[float]: The probability list of output from the ideal simulator
        '''        
        processed_program_body, measure_qubit = self.simulate_preprocess(originir)
            
        statevector = self.opcode_simulator.simulate_opcodes_statevector(
            self.qubit_num, processed_program_body)
        
        return statevector
    
    def simulate_density_matrix(self, originir):
        '''Simulate originir.
        Free mode: let available_qubits = None, then simulate any topology.
        Strict mode: input available_qubits and available_topology, then the originir is automatically checked.

        Args:
            originir (str): OriginIR.
        Returns:
            List[float]: The probability list of output from the ideal simulator
        '''        
        processed_program_body, measure_qubit = self.simulate_preprocess(originir)
            
        density_matrix = self.opcode_simulator.simulate_opcodes_density_operator(
            self.qubit_num, processed_program_body)
        
        return density_matrix
    
    def simulate_single_shot(self, originir):
        '''Simulate originir.
        Free mode: let available_qubits = None, then simulate any topology.
        Strict mode: input available_qubits and available_topology, then the originir is automatically checked.

        Args:
            originir (str): OriginIR.
        Returns:
            int: The sampled output from the ideal simulator
        '''        
        processed_program_body, measure_qubit = self.simulate_preprocess(originir)
        
        result = self.opcode_simulator.simulate_opcodes_shot(
            self.qubit_num, processed_program_body, measure_qubit)
        
        return result
    
    @property
    def simulator(self):
        return self.opcode_simulator.simulator

    @property
    def state(self):
        return self.opcode_simulator.simulator.state

class OriginIR_NoisySimulator(OriginIR_Simulator):
    def __init__(self, 
                 backend_type = 'statevector',                 
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None,
                 error_loader : ErrorLoader = None,
                 readout_error : Dict[int, List[float]]={}):
        super().__init__(backend_type, available_qubits, available_topology)        
        self.readout_error = readout_error
        self.error_loader = error_loader 

    def simulate_preprocess(self, originir, available_qubits = None, available_topology = None):
        processed_program_body, measure_qubit = super().simulate_preprocess(originir, available_qubits, available_topology)
        if self.error_loader:
            # replace the original program_body with the error-injected program_body
            self.error_loader.process_opcodes(processed_program_body)
            processed_program_body = self.error_loader.opcodes

        return processed_program_body, measure_qubit

    def simulate_pmeasure(self, originir):
        if self.opcode_simulator.simulator_typestr == 'density_operator':
            processed_program_body, measure_qubit = self._simulate_preprocess(
                originir, self.available_qubits, self.available_topology
            )
                
            prob_list = self.opcode_simulator.simulate_opcodes_pmeasure(
                self.qubit_num, processed_program_body, measure_qubit)
        
            if self.readout_error:
                return self._add_readout_error_pmeasure(prob_list, measure_qubit)
            else:
                return prob_list
            
        else:
            raise ValueError('simulate_pmeasure is only available for density_operator type OpcodeSimulator backend.')

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
        processed_program_body, measure_qubit = self._simulate_preprocess(
            originir, self.available_qubits, self.available_topology
        )

        result = self.opcode_simulator.simulate_opcodes_shot(
            self.qubit_num, processed_program_body, measure_qubit)
        
        if self.readout_error:
            result = self._add_readout_error_single_shot(result, measure_qubit)
        return result

    def simulate_shots(self, originir, shots):
        '''Simulate originir with error model.
        Free mode: let available_qubits = None, then simulate any topology.
        Strict mode: input available_qubits and available_topology, then the originir is automatically checked.

        Args:
            originir (str): OriginIR.
            shots (int): number of shots
        Returns:
            Dict[int, int]: Probability list produced by the noisy simulator.
        '''
        processed_program_body, measure_qubit = self._simulate_preprocess(
            originir, self.available_qubits, self.available_topology
        )

        results = {}
        for _ in range(shots):
            result = self.opcode_simulator.simulate_opcodes_shot(
                self.qubit_num, processed_program_body, measure_qubit)
            
            if self.readout_error:
                result = self._add_readout_error_single_shot(result, measure_qubit)
            
            results[result] = results.get(result, 0) + 1

        return results


# class OriginIR_NoisySimulator(OriginIR_Simulator):
#     def __init__(self, noise_description, gate_noise_description={}, 
#                  readout_error=[], reverse_key=False):
        
#         # Initialize noise-related attributes
#         self.noise_description = noise_description
#         self.gate_noise_description = gate_noise_description
#         self.readout_error = readout_error
#         # Initialize the superclass with the reverse_key parameter
#         super().__init__(reverse_key=reverse_key)

#     def _make_simulator(self):
#         # Overriding the parent class's _make_simulator method
#         # to create an instance of NoisySimulator instead of Simulator
#         self.simulator = NoisySimulator(self.qubit_num, 
#                                         self.noise_description, 
#                                         self.gate_noise_description,
#                                         self.readout_error)

#     def simulate_gate(self, operation, qubit, cbit, parameter, control_qubits_set, is_dagger):
#         # print(operation, qubit, cbit, parameter, is_dagger)
#         if operation == 'RX':
#             self.simulator.rx(self.qubit_mapping[int(qubit)], parameter, control_qubits_set, is_dagger)
#         elif operation == 'RY':
#             self.simulator.ry(self.qubit_mapping[int(qubit)], parameter, control_qubits_set, is_dagger)
#         elif operation == 'RZ':
#             self.simulator.rz(self.qubit_mapping[int(qubit)], parameter, control_qubits_set, is_dagger)
#         elif operation == 'H':
#             self.simulator.hadamard(self.qubit_mapping[int(qubit)], control_qubits_set, is_dagger)
#         elif operation == 'X':
#             self.simulator.x(self.qubit_mapping[int(qubit)], control_qubits_set, is_dagger)
#         elif operation == 'SX':
#             self.simulator.sx(self.qubit_mapping[int(qubit)], control_qubits_set, is_dagger)
#         elif operation == 'Y':
#             self.simulator.y(self.qubit_mapping[int(qubit)], control_qubits_set, is_dagger)
#         elif operation == 'Z':
#             self.simulator.z(self.qubit_mapping[int(qubit)], control_qubits_set, is_dagger)
#         elif operation == 'CZ':
#             self.simulator.cz(self.qubit_mapping[int(qubit[0])], 
#                               self.qubit_mapping[int(qubit[1])], control_qubits_set, is_dagger)
#         elif operation == 'ISWAP':
#             self.simulator.iswap(self.qubit_mapping[int(qubit[0])], 
#                                 self.qubit_mapping[int(qubit[1])], control_qubits_set, is_dagger)
#         elif operation == 'XY':
#             self.simulator.xy(self.qubit_mapping[int(qubit[0])], 
#                                 self.qubit_mapping[int(qubit[1])], control_qubits_set, is_dagger)
#         elif operation == 'CNOT':
#             self.simulator.cnot(self.qubit_mapping[int(qubit[0])], 
#                                 self.qubit_mapping[int(qubit[1])], control_qubits_set, is_dagger)
#         elif operation == 'RPhi':
#             self.simulator.rphi(self.qubit_mapping[int(qubit)], 
#                                 parameter[0], parameter[1], control_qubits_set, is_dagger)  
#         elif operation == 'MEASURE':
#             # In fact, I don't know the real implementation
#             # This is a guessed implementation.
#             self.measure_qubit.append((self.qubit_mapping[int(qubit)], int(cbit)))
#             # pass
#         elif operation == None:
#             pass
#         elif operation == 'QINIT':
#             pass
#         elif operation == 'CREG':
#             pass
#         elif operation == 'BARRIER':
#             pass
#         else:
#             raise RuntimeError('Unknown OriginIR operation. '
#                                f'Operation: {operation}.')

#     def simulate_pmeasure(self, 
#                  originir, 
#                  shots = 1000,
#                  available_qubits : List[int] = None, 
#                  available_topology : List[List[int]] = None):
#         '''Simulate originir.
#         Free mode: let available_qubits = None, then simulate any topology.
#         Strict mode: input available_qubits and available_topology, then the originir is automatically checked.

#         Args:
#             originir (str): OriginIR.
#             available_qubits (List[int], optional): Available qubits (if need checking). Defaults to None.
#             available_topology (list[Tuple[int, int]], optional): Available topology (if need checking). Defaults to None.

#         Returns:
#             _type_: _description_
#         '''
#         # extract the actual used qubit, and build qubit mapping
#         # like q45 -> 0, q46 -> 1, etc..
#         self._clear()
#         self.parser.parse(originir)
#         self.extract_actual_used_qubits(self.parser.program_body)
#         self.simulator = NoisySimulator(len(self.qubit_mapping), self.noise_description, self.gate_noise_description)

#         if available_qubits:
#             self.check_topology(available_qubits)
        
#         lines = self.parser.originir
#         splitted_lines = lines.splitlines()
        
#         for i, opcode in enumerate(self.parser.program_body):            
#             (operation, qubit, cbit, parameter, 
#              dagger_flag, control_qubits_set) = opcode
#             if isinstance(qubit, list) and (available_topology):
#                 if len(qubit) > 2:                    
#                     # i+2 because QINIT CREG are always excluded.
#                     raise ValueError('Real chip does not support gate of 3-qubit or more. '
#                                      'The dummy server does not support either. '
#                                      'You should consider decomposite it. \n'
#                                      f'Line {i + 2} ({splitted_lines[i + 2]}).')
                
#                 if ([int(qubit[0]), int(qubit[1])] not in available_topology) and \
#                    ([int(qubit[1]), int(qubit[0])] not in available_topology):
#                     # i+2 because QINIT CREG are always excluded.
#                     raise ValueError('Unsupported topology.\n'
#                                      f'Line {i + 2} ({splitted_lines[i + 2]}).')
                    
#             self.simulate_gate(operation, qubit, cbit, parameter, dagger_flag)
        
#         self.qubit_num = len(self.qubit_mapping)
#         measure_qubit_cbit = sorted(self.measure_qubit, key = lambda k : k[1], reverse=self.reverse_key)
#         measure_qubit = []
#         for qubit in measure_qubit_cbit:
#             measure_qubit.append(qubit[0])
#         prob_list = self.simulator.measure_shots(measure_qubit, shots)
#         return prob_list
    
#     def measure_shots(self, shots):
#         '''Call this to actually perform simulation

#         Args:
#             shots (int): number of shots

#         Returns:
#             List[float]: Probability list produced by the noisy simulator.
#         '''
#         return self.simulator.measure_shots(shots)

#     @property
#     def state(self):
#         return self.simulator.state

