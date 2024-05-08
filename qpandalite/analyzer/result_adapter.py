'''Result Adapter
'''

from copy import deepcopy
import math
import numpy as np
from typing import Dict, Union, List

def convert_originq_result(key_value_result : Union[List[Dict[str,int]],
                                                    Dict[str, int]], 
                           style = 'keyvalue', 
                           prob_or_shots = 'prob',
                           reverse_key = True, 
                           key_style = 'bin',
                           qubit_num = None):
    '''OriginQ result general adapter. Return adapted format given by the arguments. 

    Args:
        key_value_result (Dict[str, int] or a list of Dict[str, int]): The raw result produced by machine.
        style (str): Accepts "keyvalue" or "list". Defaults to 'keyvalue'.
        prob_or_shots (str): Accepts "prob" or "shots". Defaults to 'prob'.
        key_style (str): Accepts "bin" (as str) or "dec" (as int). Defaults to 'bin'.
        reverse_key (bool, optional): Reverse the key (Change endian). Defaults to True.

    Raises:
        ValueError: style is not "keyvalue" or "list"
        ValueError: prob_or_shots is not "prob" or "shots"

    Returns:
        Dict/List: Adapted format given by arguments, or a list corresponding to the "List" input.
    '''

    if isinstance(key_value_result, list):
        return [convert_originq_result(result,
                                       style=style,
                                       prob_or_shots=prob_or_shots,
                                       reverse_key=reverse_key,
                                       key_style=key_style,
                                       qubit_num=qubit_num) 
                                       for result in key_value_result]

    keys = deepcopy(key_value_result['key'])
    # for results which contain binary keys    
    keys = [int(key, base=16) for key in keys]
    
    values = deepcopy(key_value_result['value'])

    max_key = max(keys)
    if qubit_num:
        guessed_qubit_num = qubit_num
    else:
        guessed_qubit_num = len(bin(max_key)) - 2

    if style == 'list':
        key_style = 'dec'

    if reverse_key:        
        if key_style == 'bin':
            keys = [np.binary_repr(key, guessed_qubit_num)[::-1] for key in keys]
        elif key_style == 'dec':
            keys = [int(np.binary_repr(key, guessed_qubit_num)[::-1], 2) for key in keys]
        else:
            raise ValueError('key_style must be either bin or dec')
    else:
        if key_style == 'bin':
            keys = [np.binary_repr(key, guessed_qubit_num) for key in keys]
        elif key_style == 'dec':
            # default is decimal
            pass
        else:
            raise ValueError('key_style must be either bin or dec')

    if prob_or_shots == 'prob':
        total_shots = np.sum(values)
        kv_result = {k:v/total_shots for k,v in zip(keys, values)}
    elif prob_or_shots == 'shots':
        kv_result = {k:v for k,v in zip(keys, values)}
    else:
        raise ValueError('prob_or_shots only accepts "prob" or "shots".')

    if style == 'keyvalue':
        return kv_result
    elif style == 'list':
        return kv2list(kv_result, guessed_qubit_num)
    else:
        raise ValueError('style only accepts "keyvalue" or "list".')

def shots2prob(measured_result : Dict[str, int], 
               total_shots = None):
    if not total_shots:
        total_shots = np.sum(list(measured_result.values()))

    return {k : measured_result[k] / total_shots for k in measured_result}

def kv2list(kv_result : dict, guessed_qubit_num):
    ret = [0] * (2 ** guessed_qubit_num)
    # The key style of kv_result needs to be specified.
    for k in kv_result:
        ret[k] = kv_result[k]
        
    return ret

if __name__ == '__main__':

    result = {'key': ['0x1','0x2','0x7'], 'value': [10, 20, 9970]}
    print(convert_originq_result(result, 
                                 style='keyvalue', 
                                 prob_or_shots='prob', 
                                 reverse_key=True))
    
    print(convert_originq_result(result, 
                                 style='list', 
                                 prob_or_shots='prob', 
                                 reverse_key=True))
    
    print(convert_originq_result(result, 
                                 style='keyvalue', 
                                 prob_or_shots='shots', 
                                 reverse_key=True))
    
    print(convert_originq_result(result, 
                                 style='list', 
                                 prob_or_shots='shots', 
                                 reverse_key=True))
    
    print(convert_originq_result(result, 
                                 style='keyvalue', 
                                 prob_or_shots='prob', 
                                 reverse_key=False))
    
    print(convert_originq_result(result, 
                                 style='list', 
                                 prob_or_shots='prob', 
                                 reverse_key=False))
    
    print(convert_originq_result(result, 
                                 style='keyvalue', 
                                 prob_or_shots='shots', 
                                 reverse_key=False))
    
    print(convert_originq_result(result, 
                                 style='list', 
                                 prob_or_shots='shots', 
                                 reverse_key=False))
    
