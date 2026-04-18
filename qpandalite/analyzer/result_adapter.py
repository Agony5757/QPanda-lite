'''Result Adapter

Utility functions for converting and normalizing quantum measurement results.
'''

__all__ = ["shots2prob", "kv2list", "list2kv", "normalize_result", "QASMResultAdapter"]

from copy import deepcopy
import numpy as np
from typing import Dict, List, Optional, Union


def shots2prob(measured_result : Dict[str, int],
               total_shots = None):
    """Convert a shot-counts dict to a probability distribution.

    Args:
        measured_result (Dict[str, int]): Measurement counts, e.g. ``{'00': 512, '11': 488}``.
        total_shots (int, optional): Total number of shots. If not provided,
            it is inferred by summing the values of *measured_result*.

    Returns:
        Dict[str, float]: Probability dict where each count is divided by *total_shots*.
    """
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
    """Convert a key-value result dict to a flat list indexed by integer keys.

    The list has length ``2 ** guessed_qubit_num`` and is indexed by the
    integer representation of the measurement outcome.

    Args:
        kv_result (dict): Key-value result dict, e.g. ``{0: 0.1, 3: 0.9}``.
            Keys must be integers.
        guessed_qubit_num (int): Number of qubits, used to determine the
            output list length (``2 ** guessed_qubit_num``).

    Returns:
        list: Flat list where ``ret[k]`` holds the value for outcome ``k``.
    """
    ret = [0] * (2 ** guessed_qubit_num)
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
        shots: Optional[int] = None,
        metadata: Optional[dict] = None,
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
