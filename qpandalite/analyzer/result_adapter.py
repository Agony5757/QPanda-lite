'''Result Adapter
'''

__all__ = ["convert_originq_result", "convert_quafu_result", "shots2prob", "kv2list", "list2kv", "normalize_result", "QASMResultAdapter"]
from copy import deepcopy
import json
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
        quafu_result (List[Dict] or Dict): The raw result produced by Quafu.
            Each entry is a dict containing a ``res`` key with a JSON string
            of measurement counts (e.g. ``{"10": 2357, "00": 2628, ...}``).
        style (str): Accepts ``"keyvalue"`` or ``"list"``. Defaults to ``'keyvalue'``.
        prob_or_shots (str): Accepts ``"prob"`` or ``"shots"``. Defaults to ``'prob'``.
        key_style (str): Accepts ``"bin"`` (as str) or ``"dec"`` (as int). Defaults to ``'bin'``.
        reverse_key (bool, optional): Reverse the key (change endian). Defaults to True.
        qubit_num (int, optional): Override the number of qubits for key formatting.
            If not provided, it is guessed from the maximum key value.

    Raises:
        ValueError: If *style* is not ``"keyvalue"`` or ``"list"``.
        ValueError: If *prob_or_shots* is not ``"prob"`` or ``"shots"``.
        ValueError: If *key_style* is not ``"bin"`` or ``"dec"``.

    Returns:
        Dict/List: Adapted format given by arguments, or a list corresponding
        to the ``List`` input.
    '''
    if isinstance(quafu_result, list):
        return [convert_quafu_result(result,
                                      style=style,
                                      prob_or_shots=prob_or_shots,
                                      reverse_key=reverse_key,
                                      key_style=key_style,
                                      qubit_num=qubit_num) 
                                      for result in quafu_result]

    quafu_result_dict = json.loads(quafu_result["res"])
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

def list2kv(data: List[str]) -> Dict[str, int]:
    '''Convert a measurement result list to a key-value frequency dict.

    Args:
        data (List[str]): A list of measurement outcome strings,
            e.g. ``['00', '01', '10', '00', '11', '00']``.

    Returns:
        Dict[str, int]: Frequency dict where keys are outcome strings
        and values are occurrence counts. Returns ``{}`` for empty input.
    '''
    result: Dict[str, int] = {}
    for item in data:
        result[item] = result.get(item, 0) + 1
    return result


def normalize_result(data: Union[Dict[str, int], List[str]]) -> Dict[str, float]:
    '''Normalize measurement results to a probability distribution.

    Accepts either a frequency dict or a raw list of outcome strings.
    List input is first converted via :func:`list2kv`.
    Returns a dict whose values sum to 1.0.
    Returns ``{}`` for empty input.

    Args:
        data (Union[Dict[str, int], List[str]]): Measurement results as
            a frequency dict ``{'00': 3, '01': 1, ...}`` or a raw list
            ``['00', '01', '10', ...]``.

    Returns:
        Dict[str, float]: Probability distribution dict with values
        summing to 1.0.
    '''
    if isinstance(data, list):
        kv = list2kv(data)
    else:
        kv = data

    if not kv:
        return {}

    total = sum(kv.values())
    return {k: v / total for k, v in kv.items()}


def kv2list(kv_result : dict, guessed_qubit_num):
    ret = [0] * (2 ** guessed_qubit_num)
    # The key style of kv_result needs to be specified.
    for k in kv_result:
        ret[k] = kv_result[k]
        
    return ret

class QASMResultAdapter:
    """Adapter for QASM Simulator results, converting raw output to a
    standardized analysis-ready format.

    Takes a raw measurement counts dict from a QASM simulator and produces
    an :class:`AnalysisResult`-compatible object containing counts,
    probabilities, and metadata.

    The output can be passed directly to :mod:`qpandalite.analyzer.draw`
    visualization functions.

    Args:
        counts: Raw measurement counts, e.g. ``{"00": 512, "11": 488}``.
        shots: Total number of shots. If not provided, inferred from counts.
        metadata: Optional metadata dict (e.g. simulator type, circuit info).

    Attributes:
        counts (Dict[str, int]): Original measurement counts.
        probabilities (Dict[str, float]): Normalized probability distribution.
        shots (int): Total number of shots.
        metadata (dict): Simulation metadata.

    Example:
        >>> adapter = QASMResultAdapter(
        ...     counts={"00": 512, "11": 488},
        ...     metadata={"simulator": "qasm_simulator"},
        ... )
        >>> adapter.probabilities
        {'00': 0.512, '11': 0.488}
        >>> adapter.shots
        1000
    """

    def __init__(
        self,
        counts: Dict[str, int],
        shots: int = None,
        metadata: dict = None,
    ):
        self.counts: Dict[str, int] = dict(counts)
        self.shots: int = shots if shots is not None else sum(self.counts.values())
        self.metadata: dict = metadata if metadata is not None else {}
        self.metadata.setdefault("simulator", "qasm_simulator")
        self.metadata.setdefault("shots", self.shots)
        self.probabilities: Dict[str, float] = normalize_result(self.counts)

    def __repr__(self) -> str:
        return (
            f"QASMResultAdapter(shots={self.shots}, "
            f"outcomes={len(self.counts)}, "
            f"metadata={self.metadata})"
        )

    def to_dict(self) -> dict:
        """Convert to a plain dict for serialization.

        Returns:
            dict with keys ``counts``, ``probabilities``, ``shots``, ``metadata``.
        """
        return {
            "counts": self.counts,
            "probabilities": self.probabilities,
            "shots": self.shots,
            "metadata": self.metadata,
        }


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
    
