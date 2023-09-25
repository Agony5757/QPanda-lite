'''Expectation
'''

from typing import List, Dict, Union, Optional
import numpy as np

def shots2prob(measured_result : dict, total_shots = None):
    if not total_shots:
        total_shots = np.sum(list(measured_result.values()))

    return {k : measured_result[k] / total_shots for k in measured_result}

def _calculate_expectation_dict(
    measured_result : Dict[str, float], 
    h : str, 
    nqubit : int):
    
    exp = 0
    for result in measured_result:
        if len(result) != nqubit:
            raise ValueError('The Hamiltonian must have the same size with the measured result')
        
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
        raise ValueError('The Hamiltonian must have the same size with the measured result')

    for j, p in enumerate(measured_result):                
        for i in range(nqubit):
            if (h[i] == 'Z' or h[i] == 'z') and ((j >> i) & 1):
                p *= -1
        exp += p     

    return exp

def calculate_expectation(
    measured_result : Union[Dict[str, float], List[float]], 
    hamiltonian : Union[List[str], str]
):
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
