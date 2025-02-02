import random
from typing import List, Tuple, TYPE_CHECKING, Union
from qpandalite.originir.originir_base_parser import OriginIR_BaseParser
import warnings
from .opcode_simulator import OpcodeSimulator
from .base_simulator import BaseNoisySimulator, BaseSimulator
from .error_model import *

if TYPE_CHECKING:
    from .QPandaLitePy import *

class OriginIR_Simulator(BaseSimulator):    
        
    def __init__(self, 
                 backend_type = 'statevector',                 
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None,
                 **extra_kwargs):
        '''OriginIR_Simulator is a quantum circuit simulation based on C++ which runs locally on your PC.
        

        Args:
            reverse_key (bool, optional): Whether to reverse the qubit index when performing measurements. Defaults to False.            
            backend_type (str, optional): The backend type. Defaults to 'statevector'. (optional = 'statevector', 'densitymatrix')
            available_qubits (List[int], optional): Available qubits (if need checking). Defaults to None.
            available_topology (list[Tuple[int, int]], optional): Available topology (if need checking). Defaults to None.
        '''
        super().__init__(backend_type, available_qubits, available_topology, **extra_kwargs)
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

    

class OriginIR_NoisySimulator(BaseNoisySimulator):    
    def __init__(self, 
                 backend_type = 'statevector',                     
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None,
                 error_loader : ErrorLoader = None,
                 readout_error : Dict[int, List[float]]={}):
        '''OriginIR_Simulator is a quantum circuit simulation based on C++ which runs locally on your PC.
        

        Args:
            reverse_key (bool, optional): Whether to reverse the qubit index when performing measurements. Defaults to False.            
            backend_type (str, optional): The backend type. Defaults to 'statevector'. (optional = 'statevector', 'densitymatrix')
            available_qubits (List[int], optional): Available qubits (if need checking). Defaults to None.
            available_topology (list[Tuple[int, int]], optional): Available topology (if need checking). Defaults to None.
        '''
        super().__init__(backend_type, available_qubits, available_topology,
                         error_loader, readout_error)
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
