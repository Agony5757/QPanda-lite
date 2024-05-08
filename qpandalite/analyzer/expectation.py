'''Expectation
'''

from typing import List, Dict, Union, Optional
import numpy as np

def _calculate_expectation_dict(
    measured_result : Dict[str, float], 
    h : str, 
    nqubit : int):
    
    exp = 0
    for result in measured_result:
        if len(result) != nqubit:
            raise ValueError('The Hamiltonian must have the same size with the measured result.')
        
        p = measured_result[result]
        for i in range(nqubit):
            if (h[i] == 'Z' or h[i] == 'z') and (result[i] == '1'):
                p *= -1  
        exp += p     

    return exp

def _calculate_expectation_list(
    measured_result : List[float], 
    h : str, 
    nqubit : int):
    
    exp = 0
    if len(measured_result) != 2 ** nqubit:
        raise ValueError('The Hamiltonian must have the same size with the measured result.')

    for j, p in enumerate(measured_result):                
        for i in range(nqubit):
            if (h[i] == 'Z' or h[i] == 'z') and ((j >> (nqubit - i - 1)) & 1):
                p *= -1
        exp += p     

    return exp

def calculate_expectation(
    measured_result : Union[Dict[str, float], List[float]], 
    hamiltonian : Union[List[str], str]
):
    '''Calculate expectation from measured results.

    Args:
        measured_result (Union[Dict[str, float], List[float]]): The result in keyvalue or list format
        hamiltonian (Union[List[str], str]): A Hamiltonian string (only containing Z or I) with matched size. Or a list of Hamiltonian

    Raises:
        ValueError: Invalid arguments.

    Returns:
        float or List[float]: The expectation(s) corresponding to given Hamiltonian(s)
    '''
    if isinstance(hamiltonian, list):
        return [calculate_expectation(measured_result, h) for h in hamiltonian]
    
    if not isinstance(hamiltonian, str):
        raise ValueError('The Hamiltonian input must be a str (only containing Z or I or z or i).')

    for h in hamiltonian:
        if h != 'Z' and h != 'z' and h != 'I' and h != 'i':
            raise ValueError('The Hamiltonian input must be a str (only containing Z or I or z or i).')
        
    nqubit = len(hamiltonian)

    if isinstance(measured_result, dict):
        return _calculate_expectation_dict(measured_result, hamiltonian, nqubit)
    elif isinstance(measured_result, list):
        return _calculate_expectation_list(measured_result, hamiltonian, nqubit)
    else:
        raise ValueError('measured_result must be a Dict or a List.')

if __name__ == '__main__':
    from result_adapter import convert_originq_result

    result = {'key': ['001','010','100'], 'value': [10, 20, 9970]}
    kvresult = convert_originq_result(result, 
                                    style='keyvalue', 
                                    prob_or_shots='prob', 
                                    reverse_key=False,
                                    qubit_num=3)
    
    print(calculate_expectation(kvresult, ['IIZ', 'IZI', 'ZII', 'ZZZ']))
    
    listresult = convert_originq_result(result, 
                                    style='list', 
                                    prob_or_shots='prob', 
                                    reverse_key=False,
                                    qubit_num=3)

    print(calculate_expectation(listresult, ['IIZ', 'IZI', 'ZII', 'ZZZ']))