'''Result Adapter
'''

from copy import deepcopy
import numpy as np
from typing import Dict, Union, List

def convert_originq_result(key_value_result : Union[List[Dict[str,int]],
                                                    Dict[str, int]], 
                           style = 'keyvalue', 
                           prob_or_shots = 'prob',
                           reverse_key = False):
    '''OriginQ result general adapter. Return adapted format given by the arguments. 

    Args:
        key_value_result (Dict[str, int] or a list of Dict[str, int]): The raw result produced by machine.
        style (str): Accepts "keyvalue" or "list". Defaults to 'keyvalue'.
        prob_or_shots (str): Accepts "prob" or "shots". Defaults to 'prob'.
        reverse_key (bool, optional): Reverse the key (Change endian). Defaults to False.

    Raises:
        ValueError: style is not "keyvalue" or "list"
        ValueError: prob_or_shots is not "prob" or "shots"

    Returns:
        Dict/List: Adapted format given by arguments, or a list corresponding to the "List" input.
    '''

    if isinstance(key_value_result, list):
        return [convert_originq_result(result) for result in key_value_result]

    keys = deepcopy(key_value_result['key'])
    if reverse_key:
        for i in range(len(keys)):
            keys[i] = keys[i][::-1]
    values = deepcopy(key_value_result['value'])

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
        return kv2list(kv_result)
    else:
        raise ValueError('style only accepts "keyvalue" or "list".')

def shots2prob(measured_result : Dict[str, int], 
               total_shots = None):
    if not total_shots:
        total_shots = np.sum(list(measured_result.values()))

    return {k : measured_result[k] / total_shots for k in measured_result}

def kv2list(kv_result : dict):    
    for k in kv_result:
        qubit_num = len(k)
        break

    ret = [0] * (2 ** qubit_num)
    for k in kv_result:
        ret[int(k, 2)] = kv_result[k]

    return ret

if __name__ == '__main__':

    result = {'key': ['001','010','100'], 'value': [10, 20, 9970]}
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