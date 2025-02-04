'''Opcode simulator, a fundamental simulator for QPanda-lite.
It simulates from a basic opcode
'''
from typing import List, Optional, Tuple, TYPE_CHECKING, Union
from .qutip_sim_impl import DensityOperatorSimulatorQutip
import numpy as np
from QPandaLitePy import *
from qpandalite.circuit_builder.qcircuit import OpcodeType
if TYPE_CHECKING:
    from .QPandaLitePy import *


def backend_alias(backend_type):
    ''' Backend alias for different backends.
    Supported backends: statevector, density_matrix

    Note: Uppercase and lowercase are both supported.

    Supported aliases: ['statevector', 'state_vector',
    'density_matrix', 'density_operator', 'DensityMatrix', 'DensityOperator']
    '''
    statevector_alias = ['statevector', 'state_vector']
    density_operator_alias = ['density_matrix', 'density_operator',
                              'densitymatrix', 'densityoperator']
    density_operator_qutip_alias = ['density_matrix_qutip', 'density_operator_qutip']

    backend_type = backend_type.lower()
    if backend_type in statevector_alias:
        return 'statevector'
    elif backend_type in density_operator_alias:
        return 'density_operator'
    elif backend_type in density_operator_qutip_alias:
        return 'density_operator_qutip'
    else:
        raise ValueError(f'Unknown backend type: {backend_type}')


class OpcodeSimulator:   
    def __init__(self, backend_type = 'statevector'):
        '''OpcodeSimulator is a quantum circuit simulation based on C++ which runs locally on your PC.
        
        Args:
            backend_type (str): The backend type for simulation. Supported backends: statevector, density_matrix. Default: 'statevector'.

        Note: Uppercase and lowercase are both supported.

        Supported aliases for backend_type:
         statevector: ['statevector', 'state_vector']
         density_matrix: ['density_matrix', 'density_operator', 'densitymatrix', 'densityoperator']
         density_matrix_qutip: ['density_matrix_qutip', 'density_operator_qutip']

         density_matrix_qutip is a backend based on Qutip library, which is used to compare with
         the density matrix simulator in QPanda-lite.
        '''
        backend_type = backend_alias(backend_type)        
        if backend_type =='statevector':
            self.SimulatorType = StatevectorSimulator
            self.simulator_typestr = 'statevector'
        elif backend_type == 'density_operator':
            self.SimulatorType = DensityOperatorSimulator
            self.simulator_typestr = 'density_operator'
        elif backend_type == 'density_operator_qutip':
            self.SimulatorType = DensityOperatorSimulatorQutip
            self.simulator_typestr = 'density_operator'
        else:
            raise ValueError(f'Unknown backend type: {backend_type}')
        
        self.simulator = self.SimulatorType()

    def _clear(self):
        self.simulator = self.SimulatorType()

    def _simulate_common_gate(self, operation, qubit, cbit, parameter, is_dagger, control_qubits_set):
        if operation == 'RX':
            self.simulator.rx(qubit, parameter, control_qubits_set, is_dagger)
        elif operation == 'RY':
            self.simulator.ry(qubit, parameter, control_qubits_set, is_dagger)
        elif operation == 'RZ':
            self.simulator.rz(qubit, parameter, control_qubits_set, is_dagger)
        elif operation == 'U1':
            self.simulator.u1(qubit, parameter, control_qubits_set, is_dagger)
        elif operation == 'U2':
            self.simulator.u2(qubit, parameter[0], parameter[1], control_qubits_set, is_dagger)
        elif operation == 'H':
            self.simulator.hadamard(qubit, control_qubits_set, is_dagger)
        elif operation == 'X':
            self.simulator.x(qubit, control_qubits_set, is_dagger)
        elif operation == 'SX':
            self.simulator.sx(qubit, control_qubits_set, is_dagger)
        elif operation == 'Y':
            self.simulator.y(qubit, control_qubits_set, is_dagger)
        elif operation == 'Z':
            self.simulator.z(qubit, control_qubits_set, is_dagger)
        elif operation == 'S':
            self.simulator.s(qubit, control_qubits_set, is_dagger)
        elif operation == 'T':
            self.simulator.t(qubit, control_qubits_set, is_dagger)
        elif operation == 'CZ':
            self.simulator.cz(qubit[0], 
                            qubit[1], control_qubits_set, is_dagger)
        elif operation == 'SWAP':
            self.simulator.swap(qubit[0], 
                                qubit[1], control_qubits_set, is_dagger)
        elif operation == 'ISWAP':
            self.simulator.iswap(qubit[0], 
                                qubit[1], control_qubits_set, is_dagger)
        elif operation == 'TOFFOLI':
            self.simulator.toffoli(qubit[0], 
                                qubit[1], 
                                qubit[2], control_qubits_set, is_dagger)
        elif operation == 'CSWAP':
            self.simulator.cswap(qubit[0], 
                                qubit[1], 
                                qubit[2], control_qubits_set, is_dagger)
        elif operation == 'XY':
            self.simulator.xy(qubit[0], qubit[1], 
                              parameter, control_qubits_set, is_dagger)
        elif operation == 'CNOT':
            self.simulator.cnot(qubit[0], 
                                qubit[1], control_qubits_set, is_dagger)  
        elif operation == 'RPhi':
            self.simulator.rphi(qubit, parameter[0], parameter[1], control_qubits_set, is_dagger)
        elif operation == 'RPhi90':
            self.simulator.rphi90(qubit, parameter, control_qubits_set, is_dagger)
        elif operation == 'RPhi180':
            self.simulator.rphi180(qubit, parameter, control_qubits_set, is_dagger) 
        elif operation == 'U3':
            self.simulator.u3(qubit, parameter[0], parameter[1], parameter[2], 
                              control_qubits_set, is_dagger) 
        elif operation == 'XX':
            self.simulator.xx(qubit[0],
                              qubit[1],
                              parameter, control_qubits_set, is_dagger) 
        elif operation == 'YY':
            self.simulator.yy(qubit[0],
                              qubit[1],
                              parameter, control_qubits_set, is_dagger) 
        elif operation == 'ZZ':
            self.simulator.zz(qubit[0],
                              qubit[1],
                              parameter, control_qubits_set, is_dagger)
        elif operation == 'UU15':
            self.simulator.uu15(qubit[0],
                                qubit[1],
                                parameter, control_qubits_set, True)
        elif operation == 'PHASE2Q':
            self.simulator.phase2q(qubit[0], qubit[1],
                parameter[0], parameter[1], parameter[2], 
                control_qubits_set, is_dagger)
        elif operation == 'PauliError1Q':
            # parameter[0]: probability of X error
            # parameter[1]: probability of Y error
            # parameter[2]: probability of Z error
            self.simulator.pauli_error_1q(qubit, parameter[0], parameter[1], parameter[2])
        elif operation == 'Depolarizing':
            # parameter: depolarizing probability
            self.simulator.depolarizing(qubit, parameter)
        elif operation == 'BitFlip':
            # parameter: bit flip probability
            self.simulator.bitflip(qubit, parameter)
        elif operation == 'PhaseFlip':
            # parameter: phase flip probability
            self.simulator.phaseflip(qubit, parameter)
        elif operation == 'AmplitudeDamping':
            # parameter: phase flip probability
            self.simulator.amplitude_damping(qubit, parameter)
        elif operation == 'PauliError2Q':
            # parameter: List[float]
            self.simulator.pauli_error_2q(qubit[0], qubit[1], parameter)
        elif operation == 'TwoQubitDepolarizing':
            # parameter: depolarizing probability
            self.simulator.twoqubit_depolarizing(qubit[0], qubit[1], parameter)
        elif operation == 'Kraus1Q':
            # parameter: List[List[complex]]
            if not isinstance(parameter, list):
                raise ValueError('Kraus1Q parameter should be a list of U22 matrices.')
            
            def build_u22(arr):
                # the cases include the following:
                # 1. a 2x2 np.ndarray
                # 2. a 4 elements np.ndarray[complex]
                # 3. a 2x2 List[List[complex]]
                # 4. a 4-element List[complex]
                # Final target is to transform into case (4), a 4-element List[complex]
                if isinstance(arr, np.ndarray):
                    if arr.shape == (2, 2):
                        return [arr[0][0], arr[0][1], arr[1][0], arr[1][1]]
                    elif arr.shape == (4,):
                        return arr.tolist()
                    else:
                        raise ValueError('Kraus1Q parameter should be a 2x2 or 4-element list or numpy array.')
                elif isinstance(arr, list):
                    if len(arr) == 4:
                        return arr
                    elif len(arr) == 2 and len(arr[0]) == 2 and len(arr[1]) == 2:   
                        return [arr[0][0], arr[0][1], arr[1][0], arr[1][1]]
                    else:
                        raise ValueError('Kraus1Q parameter should be a 2x2 or 4-element list or numpy array.')
                else:
                    raise ValueError('Kraus1Q parameter should be a 2x2 or 4-element list or numpy array.')
                
            parameters_ = [build_u22(arr) for arr in parameter]
            self.simulator.kraus1q(qubit, parameters_)
        elif operation == 'AmplitudeDamping':
            # parameter: gamma
            self.simulator.amplitude_damping(qubit, parameter)
        elif operation == 'I':
            pass
        elif operation == None:
            pass
        elif operation == 'QINIT':
            pass
        elif operation == 'CREG':
            pass
        elif operation == 'BARRIER':
            pass
        else:
            raise RuntimeError('Unknown Opcode operation. '
                                f'Operation: {operation}.'
                                f'Full opcode: {(operation, qubit, cbit, parameter, control_qubits_set, is_dagger)}')

    def simulate_gate(self, operation, qubit, cbit, parameter, is_dagger, control_qubits_set):
        # convert from set to list (to adapt to C++ input)
        if control_qubits_set:
            control_qubits_set = list(control_qubits_set)
        else:
            control_qubits_set = list()

        self._simulate_common_gate(operation, qubit, cbit, parameter, is_dagger, control_qubits_set)    

    def simulate_opcodes_pmeasure(self, n_qubit, program_body, measure_qubits):
        self.simulator.init_n_qubit(n_qubit)
        for opcode in program_body:
            operation, qubit, cbit, parameter, is_dagger, control_qubits_set = opcode
            self.simulate_gate(operation, qubit, cbit, parameter, is_dagger, control_qubits_set)
        
        prob_list = self.simulator.pmeasure(measure_qubits)
        return prob_list
    
    def simulate_opcodes_statevector(self, n_qubit, program_body):
        if self.simulator_typestr == 'density_matrix':
            raise ValueError('Density matrix is not supported for statevector simulation.')

        self.simulator.init_n_qubit(n_qubit)
        for opcode in program_body:
            operation, qubit, cbit, parameter, is_dagger, control_qubits_set = opcode
            self.simulate_gate(operation, qubit, cbit, parameter, is_dagger, control_qubits_set)
        
        statevector = self.simulator.state
        return statevector
    
    def simulate_opcodes_stateprob(self, n_qubit, program_body):
        if self.simulator_typestr == 'statevector':      
            statevector = self.simulate_opcodes_statevector(n_qubit, program_body)
            statevector = np.array(statevector)
            return np.abs(statevector) ** 2
        
        if self.simulator_typestr == 'density_operator':
            self.simulator.init_n_qubit(n_qubit)
            for opcode in program_body:
                operation, qubit, cbit, parameter, is_dagger, control_qubits_set = opcode
                self.simulate_gate(operation, qubit, cbit, parameter, is_dagger, control_qubits_set)

            return self.simulator.stateprob()
        
        raise ValueError('Unknown simulator type.')
    
    def simulate_opcodes_density_operator(self, n_qubit, program_body):
        if self.simulator_typestr == 'density_operator':
            self.simulator.init_n_qubit(n_qubit)
            for opcode in program_body:
                operation, qubit, cbit, parameter, is_dagger, control_qubits_set = opcode
                self.simulate_gate(operation, qubit, cbit, parameter, is_dagger, control_qubits_set)

            state = self.simulator.state            
            state = np.array(state)
            
            # reshape to 2^n x 2^n matrix
            density_matrix = np.reshape(state, (2 ** n_qubit, 2 ** n_qubit), order='F')
            
            return density_matrix
        
        if self.simulator_typestr =='statevector':
            statevector = self.simulate_opcodes_statevector(n_qubit, program_body)
            statevector = np.array(statevector)
            density_matrix = np.outer(statevector, np.conj(statevector))
            return density_matrix
        
        raise ValueError('Unknown simulator type.')
    
    def simulate_opcodes_shot(self, n_qubit, program_body : List[OpcodeType], measure_qubits):
        if self.simulator_typestr == 'density_operator':
            raise NotImplementedError('Density matrix is not supported for shot simulation.')
        
        self.simulator.init_n_qubit(n_qubit)
        for opcode in program_body:
            operation, qubit, cbit, parameter, is_dagger, control_qubits_set = opcode
            self.simulate_gate(operation, qubit, cbit, parameter, is_dagger, control_qubits_set)
        
        return self.simulator.measure_single_shot(measure_qubits)