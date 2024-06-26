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

def convert_quafu_result(quafu_result : List[Union[Dict[str, Dict[str, int]], Dict[str, int], Dict[str, str]]],
                           style = 'keyvalue',
                           prob_or_shots = 'prob',
                           reverse_key = True,
                           key_style = 'bin',
                           qubit_num = None):
    '''Quafu result general adapter. Return adapted format given by the arguments.

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
    if isinstance(quafu_result, list):
        return [convert_quafu_result(result,
                                       style=style,
                                       prob_or_shots=prob_or_shots,
                                       reverse_key=reverse_key,
                                       key_style=key_style,
                                       qubit_num=qubit_num) 
                                       for result in quafu_result]

    quafu_result_dict = eval(quafu_result["res"])
    keys = list(quafu_result_dict.keys())
    keys = deepcopy([int(key, base=2) for key in keys])

    values = deepcopy(list(quafu_result_dict.values()))

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
        return [kv_result]
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

    # quafu_result =  [{'input_q2c': None, 'measure': '{0: 0, 1: 1}', 'openqasm': 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[130];\ncreg c[2];\nh q[2];\nh q[3];\nbarrier q[2],q[3];\nmeasure q[2] -> c[0];\nmeasure q[3] -> c[1];\n', 'raw': '{"10": 2357, "00": 2628, "11": 2520, "01": 2495}', 'res': '{"10": 2357, "00": 2628, "11": 2520, "01": 2495}', 'status': 2, 'task_id': '4A08323012C269F9', 'task_name': 'test1-0'}]
    quafu_result = [{'input_q2c': None, 'measure': '{0: 0, 1: 1}', 'openqasm': 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[130];\ncreg c[2];\nry(1.7882381976938504) q[3];\nry(1.2144518702039844) q[2];\ncx q[3],q[2];\nbarrier q[2],q[3];\nmeasure q[3] -> c[0];\nmeasure q[2] -> c[1];\n', 'raw': '{"10": 2075, "00": 2717, "11": 3884, "01": 1324}', 'res': '{"10": 2075, "00": 2717, "11": 3884, "01": 1324}', 'status': 2, 'task_id': '4A207CE005C923DC', 'task_name': '0_find_best_initial_theta-0'}, {'input_q2c': None, 'measure': '{0: 0, 1: 1}', 'openqasm': 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[130];\ncreg c[2];\nry(1.2625578959744033) q[2];\nry(1.5277845308363243) q[3];\ncx q[2],q[3];\nbarrier q[2],q[3];\nmeasure q[2] -> c[0];\nmeasure q[3] -> c[1];\n', 'raw': '{"00": 3310, "01": 3127, "10": 1610, "11": 1953}', 'res': '{"00": 3310, "01": 3127, "10": 1610, "11": 1953}', 'status': 2, 'task_id': '4A207CE0199C1372', 'task_name': '0_find_best_initial_theta-1'}, {'input_q2c': None, 'measure': '{0: 0, 1: 1}', 'openqasm': 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[130];\ncreg c[2];\nry(5.762547309276938) q[2];\nry(5.338250023590393) q[3];\ncx q[2],q[3];\nbarrier q[2],q[3];\nmeasure q[2] -> c[0];\nmeasure q[3] -> c[1];\n', 'raw': '{"01": 2037, "00": 6985, "11": 692, "10": 286}', 'res': '{"01": 2037, "00": 6985, "11": 692, "10": 286}', 'status': 2, 'task_id': '4A207CE025DDFC2A', 'task_name': '0_find_best_initial_theta-2'}, {'input_q2c': None, 'measure': '{0: 0, 1: 1}', 'openqasm': 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[130];\ncreg c[2];\nry(1.228936999472893) q[3];\nry(1.6563349539117342) q[2];\ncx q[3],q[2];\nbarrier q[2],q[3];\nmeasure q[3] -> c[0];\nmeasure q[2] -> c[1];\n', 'raw': '{"00": 3232, "10": 1807, "11": 1606, "01": 3355}', 'res': '{"00": 3232, "10": 1807, "11": 1606, "01": 3355}', 'status': 2, 'task_id': '4A207CE032321CE3', 'task_name': '0_find_best_initial_theta-3'}, {'input_q2c': None, 'measure': '{0: 0, 1: 1}', 'openqasm': 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[130];\ncreg c[2];\nry(0.9552400455227436) q[3];\nry(3.635679885833879) q[2];\ncx q[3],q[2];\nbarrier q[2],q[3];\nmeasure q[3] -> c[0];\nmeasure q[2] -> c[1];\n', 'raw': '{"01": 6259, "00": 1177, "10": 2153, "11": 411}', 'res': '{"01": 6259, "00": 1177, "10": 2153, "11": 411}', 'status': 2, 'task_id': '4A207CF0030B6B43', 'task_name': '0_find_best_initial_theta-4'}]
    print("quafu_result: \n", quafu_result)
    print(convert_quafu_result(quafu_result, style = 'list', prob_or_shots = 'prob', reverse_key = True, qubit_num = 2))

    print(convert_quafu_result(quafu_result, 
                                 style='keyvalue', 
                                 prob_or_shots='prob', 
                                 reverse_key=True))
    
    print(convert_quafu_result(quafu_result, 
                                 style='list', 
                                 prob_or_shots='prob', 
                                 reverse_key=True))
    
    print(convert_quafu_result(quafu_result, 
                                 style='keyvalue', 
                                 prob_or_shots='shots', 
                                 reverse_key=True))
    
    print(convert_quafu_result(quafu_result, 
                                 style='list', 
                                 prob_or_shots='shots', 
                                 reverse_key=True))
    
    print(convert_quafu_result(quafu_result, 
                                 style='keyvalue', 
                                 prob_or_shots='prob', 
                                 reverse_key=False))
    
    print(convert_quafu_result(quafu_result, 
                                 style='list', 
                                 prob_or_shots='prob', 
                                 reverse_key=False))
    
    print(convert_quafu_result(quafu_result, 
                                 style='keyvalue', 
                                 prob_or_shots='shots', 
                                 reverse_key=False))
    
    print(convert_quafu_result(quafu_result, 
                                 style='list', 
                                 prob_or_shots='shots', 
                                 reverse_key=False))
