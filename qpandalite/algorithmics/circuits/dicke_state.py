"""Dicke state preparation circuit using the SCUC algorithm."""

__all__ = ["dicke_state_circuit"]

from typing import List, Optional
import math

from qpandalite.circuit_builder import Circuit

def dicke_state_circuit(circuit: Circuit, k: int, qubits: list = None):
    """
    Generate Dicke state |D^n_k> exactly.
    """
    if qubits is None:
        qubits = list(range(circuit.qubit_num))

    n = len(qubits)
    if k < 1 or k > n:
        raise ValueError(f"k must satisfy 1 <= k <= n (got k={k}, n={n})")

    # Step 1: 初始化【最后 k 个】量子比特为 |1>
    for i in range(n - k, n):
        circuit.x(qubits[i])

    # Step 2: 使用 SCS (Single Combination Step) 降维网络构建
    # 外层循环1：把 n 逐步降维到 k+1
    for current_n in range(n, k, -1):
        _scs_layer(circuit, current_n, k, qubits)
        
    # 外层循环2：把 k 逐步降维到 2
    for current_k in range(k, 1, -1):
        _scs_layer(circuit, current_k, current_k - 1, qubits)


def _scs_layer(circuit, m: int, l: int, qubits: list):
    """
    应用一层单组合步 (Single Combination Step)
    m: 当前处理的块大小
    l: 当前块内最大的激发数 (1 的数量)
    """
    # 1. 基础情况 (k=1时的行为) -> 1个控制位
    theta = math.acos(math.sqrt(1 / m))
    tgt = qubits[m - 2]
    ctrl = qubits[m - 1]

    circuit.cx(tgt, ctrl)
    _cry(circuit, ctrl, tgt, 2 * theta)
    circuit.cx(tgt, ctrl)

    # 2. 复杂情况 (k>=2时的行为) -> 2个控制位
    for i in range(2, l + 1):
        theta = math.acos(math.sqrt(i / m))
        tgt = qubits[m - 1 - i]
        ctrl1 = qubits[m - 1]
        ctrl2 = qubits[m - i]

        circuit.cx(tgt, ctrl1)
        _ccry(circuit, ctrl1, ctrl2, tgt, 2 * theta)
        circuit.cx(tgt, ctrl1)


def _cry(circuit, ctrl, tgt, angle):
    """标准的 Controlled-Ry 门分解"""
    circuit.ry(tgt, angle / 2)
    circuit.cx(ctrl, tgt)
    circuit.ry(tgt, -angle / 2)
    circuit.cx(ctrl, tgt)

def _ccry(circuit, ctrl1, ctrl2, tgt, angle):
    """标准的 Doubly-Controlled-Ry (CCRy) 门分解"""
    _cry(circuit, ctrl2, tgt, angle / 2)
    circuit.cx(ctrl1, ctrl2)
    _cry(circuit, ctrl2, tgt, -angle / 2)
    circuit.cx(ctrl1, ctrl2)
    _cry(circuit, ctrl1, tgt, angle / 2)