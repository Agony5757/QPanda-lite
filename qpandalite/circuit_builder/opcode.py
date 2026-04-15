"""
This file is used to convert the opcode to various quantum code formats.
"""

from typing import List, Optional, Tuple, Union
from .translate_qasm2_oir import OriginIR_QASM2_dict, get_QASM2_from_opcode, decompose_mcx_qasm_text

__all__ = [
    'make_header_originir',
    'make_header_qasm',
    'make_measure_originir',
    'make_measure_qasm',
    'opcode_to_line_originir',
    'opcode_to_line_qasm',
    'OpcodeType',
    'QubitType',
    'CbitType',
    'ParameterType',
]

QubitType = Union[List[int], int]
CbitType = Union[List[int], int]
ParameterType = Optional[Union[List[float], float]]
OpcodeType = Tuple[str, QubitType, CbitType, ParameterType, set, bool]


def make_header_originir(qubit_num: int, cbit_num: int) -> str:
    '''
    Generate the header of OriginIR code for the given qubit and cbit number.

    Args:
        qubit_num (int): The number of qubits in the circuit.
        cbit_num (int): The number of classical bits in the circuit.

    Returns:
        str: The header of OriginIR code.
    '''
    ret = 'QINIT {}\n'.format(qubit_num)
    ret += 'CREG {}\n'.format(cbit_num)
    return ret


def opcode_to_line_originir(opcode : OpcodeType) -> str:            
    '''
    Convert the given opcode to OriginIR line format.

    opcode is a tuple with the following format:
    (operation, qubit, cbit, parameter, dagger_flag, control_qubits_set) where:
        operation (str): The name of the operation.
        qubit (QubitType): The qubit(s) the operation is applied to.
        cbit (CbitType): The classical bit(s) the operation stores the result in.
        parameter (ParameterType): The parameter(s) of the operation.
        dagger_flag (bool): Whether the operation is daggered.
        control_qubits_set (set): The set of control qubits.

    QubitType = Union[List[int], int]
    CbitType = Union[List[int], int]
    ParameterType = Optional[Union[List[float], float]] 
    
    and

    OpcodeType = Tuple[str, QubitType, CbitType, ParameterType, set, bool]

    Args:
        opcode (OpcodeType): The given opcode to be converted.

    Returns:
        str: The converted OriginIR line format.
    '''
    (operation, qubit, cbit, parameter, dagger_flag, control_qubits_set) = opcode
    
    # operation qubits (,parameter?) (,cbits?) (dagger?) (control?)
    if not operation:
        raise RuntimeError('Unexpected error. Operation is empty.')
    ret = ''
    
    ret += operation
    
    if isinstance(qubit, list):
        ret += ' '
        ret += ', '.join([f'q[{q}]' for q in qubit])
    else:
        ret += f' q[{qubit}]'

    if parameter is not None and (not hasattr(parameter, '__len__') or len(parameter) > 0):
        ret += ', ('
        if hasattr(parameter, '__iter__') and not isinstance(parameter, str):
            ret += ', '.join([str(p) for p in parameter])
        else:
            ret += str(parameter)
        ret += ')'
        
    if cbit: 
        ret += ', '
        ret += (f'c[{cbit}]' if cbit else '')
        
    if dagger_flag:
        ret += ' dagger'
    
    if control_qubits_set:        
        ret += ' controlled_by ('
        ret += ', '.join([f'q[{q}]' for q in control_qubits_set])
        ret += ')'

    # print(ret)

    return ret


def make_measure_originir(measure_list : List[int]):
    '''
    Generate the measure statement of OriginIR code for the given measure list.

    Args:
        measure_list (List[int]): The list of qubits to be measured.

    Returns:
        str: The measure statement of OriginIR code.
    '''

    ret = ''
    for i, meas_qubit in enumerate(measure_list):
        ret += 'MEASURE q[{}], c[{}]\n'.format(meas_qubit, i)
    return ret


def make_header_qasm(qubit_num: int, cbit_num: int) -> str:
    '''
    Generate the header of QASM code for the given qubit and cbit number.

    Args:
        qubit_num (int): The number of qubits in the circuit.
        cbit_num (int): The number of classical bits in the circuit.

    Returns:
        str: The header of QASM code.
    '''
    
    ret = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
    ret += 'qreg q[{}];\n'.format(qubit_num)
    ret += 'creg c[{}];\n'.format(cbit_num)
    return ret


def opcode_to_line_qasm(opcode: OpcodeType, qubit_num: Optional[int] = None) -> str:
    '''
    Convert the given opcode to QASM line format.

    For gates with ≥ 4 control qubits on an X gate, a multi-line Toffoli-ladder
    decomposition is returned.  The *qubit_num* argument must be supplied in that
    case so workspace qubits can be located; otherwise a NotImplementedError is
    raised.

    Args:
        opcode (OpcodeType): The given opcode to be converted.
        qubit_num (Optional[int]): Total number of qubits in the circuit (needed
            for MCX decomposition with ≥ 4 controls).

    Returns:
        str: The converted QASM line format (potentially multi-line for MCX
        decompositions).
    '''

    operation, qubit, cbit, parameter = get_QASM2_from_opcode(opcode)

    # Sentinel returned by get_QASM2_from_opcode for n≥4 control MCX.
    if operation == '_MCX_DECOMP_':
        controls_list, target = qubit  # type: ignore[misc]
        if qubit_num is None:
            raise NotImplementedError(
                "MCX with ≥4 controls cannot be decomposed without knowing the "
                "circuit's qubit count. Pass qubit_num to opcode_to_line_qasm."
            )
        return decompose_mcx_qasm_text(controls_list, target, qubit_num)

    # operation qubits (,parameter?) (,cbits?) (dagger?) (control?)
    if not operation:
        raise RuntimeError('Unexpected error. Operation is empty.')
    ret = ''

    ret += operation

    if parameter is not None:
        if isinstance(parameter, list):
            parameter_str = ', '.join([str(p) for p in parameter])
        else:
            parameter_str = str(parameter)

        ret += f'({parameter_str})'

    if isinstance(qubit, list):
        ret += ' '
        ret += ', '.join([f'q[{q}]' for q in qubit])
    else:
        ret += f' q[{qubit}]'

    if cbit:
        raise NotImplementedError('qpandalite does not support cbit in QASM code.')

    ret += ';'

    return ret


def make_measure_qasm(measure_list : List[int]) -> str:
    '''
    Generate the measure statement of QASM code for the given measure list.

    Args:
        measure_list (List[int]): The list of qubits to be measured.

    Returns:
        str: The measure statement of QASM code.
    '''
    
    ret = ''
    for i, meas_qubit in enumerate(measure_list):
        ret += 'measure q[{}] -> c[{}];\n'.format(meas_qubit, i)
    return ret   