import numpy as np
from qpandalite.task.quafu import Translation_OriginIR_to_QuafuCircuit as tqf
TWIRL_GATES = {
    "CNOT": (
        (("I", "I"), ("I", "I")),
        (("I", "X"), ("I", "X")),
        (("I", "Y"), ("Z", "Y")),
        (("I", "Z"), ("Z", "Z")),
        (("X", "I"), ("X", "X")),
        (("X", "X"), ("X", "I")),
        (("X", "Y"), ("Y", "Z")),
        (("X", "Z"), ("Y", "Y")),
        (("Y", "I"), ("Y", "X")),
        (("Y", "X"), ("Y", "I")),
        (("Y", "Y"), ("X", "Z")),
        (("Y", "Z"), ("X", "Y")),
        (("Z", "I"), ("Z", "I")),
        (("Z", "X"), ("Z", "X")),
        (("Z", "Y"), ("I", "Y")),
        (("Z", "Z"), ("I", "Z")),
    ),
    "CZ": (
        (("I", "I"), ("I", "I")),
        (("I", "X"), ("Z", "X")),
        (("I", "Y"), ("Z", "Y")),
        (("I", "Z"), ("I", "Z")),
        (("X", "I"), ("X", "Z")),
        (("X", "X"), ("Y", "Y")),
        (("X", "Y"), ("Y", "X")),
        (("X", "Z"), ("X", "I")),
        (("Y", "I"), ("Y", "Z")),
        (("Y", "X"), ("X", "Y")),
        (("Y", "Y"), ("X", "X")),
        (("Y", "Z"), ("Y", "I")),
        (("Z", "I"), ("Z", "I")),
        (("Z", "X"), ("I", "X")),
        (("Z", "Y"), ("I", "Y")),
        (("Z", "Z"), ("Z", "Z")),
    ),
}

four_pauli = ['I', 'X', 'Y', 'Z']


def generate_twirl(rand1, rand2, gate):
    pair = (rand1, rand2)
    for x, y in TWIRL_GATES[gate]:
        if x == pair:
            return y
    raise NotImplementedError


def generate_random_pauli_pair(gate='CZ'):
    l1, l2 = np.random.choice(four_pauli, 2)
    r1, r2 = generate_twirl(l1, l2, gate)
    return l1, l2, r1, r2


def barrier_all(qubit_list):
    originir = f'BARRIER '
    qubit_str = [f'q[{q}]' for q in qubit_list]
    originir += ','.join(qubit_str) + '\n'
    return originir


def transfer_to_quafu_gates(pauli, qubit):
    if pauli == 'X':
        return f'RX q[{qubit}],(3.1415926)\n'
    if pauli == 'Y':
        return f'RY q[{qubit}],(3.1415926)\n'
    if pauli == 'Z':
        return f'RY q[{qubit}],(3.1415926)\n'
    if pauli == 'I':
        return ''


def twirl_circuit(qubit_set, cz_qubits, gate='CZ'):
    ir = ''
    idle_qubit_set = qubit_set.copy()
    cz_pair = dict(cz_qubits)

    # 不作用CZ的qubit
    for pair in cz_qubits:
        if pair[0] in idle_qubit_set:
            idle_qubit_set.remove(pair[0])
        if pair[1] in idle_qubit_set:
            idle_qubit_set.remove(pair[1])

    pauli_list = {}
    conj_list = {}
    for q in qubit_set:
        if q in idle_qubit_set:
            pauli = np.random.choice(four_pauli[1:])
            pauli_list[q] = pauli
            conj_list[q] = pauli
            ir += f'{pauli} q[{q}]\n'
        else:
            if q not in pauli_list:
                l1, l2, r1, r2 = generate_random_pauli_pair(gate)
                another_q = cz_pair[q]
                pauli_list[q] = l1
                pauli_list[another_q] = l2
                ir += f'{l1} q[{q}]\n'
                ir += f'{l2} q[{q}]\n'
                conj_list[q] = r1
                conj_list[another_q] = r2

    ir += barrier_all(qubit_list=qubit_set)

    for q, another_q in cz_pair.items():
        ir += f'{gate} q[{q}],q[{another_q}]\n'
    ir += barrier_all(qubit_list=qubit_set)

    for q, pauli in conj_list.items():
        ir += f'{pauli} q[{q}]\n'
    ir += barrier_all(qubit_list=qubit_set)
    return ir


def readout_twirl(qubit_list):
    ir = ''
    flip = np.random.random(len(qubit_list)) < 0.5
    for qubit, f in enumerate(qubit_list, flip):
        if f:
            ir += f'X q[{qubit}]\n'
    for qubit in qubit_list:
        ir += f'MEASURE q[{qubit}],c[{qubit}]\n'
    return ir, flip


def get_layer_information():
    pass


def twirl_ir(origin_ir, patterns):
    new_ir = origin_ir
    for line in origin_ir:
        if line.startwith('C') and not line.startwith('CREG'):
            gate, q = tqf().regexp_2q(line)
            twirl_gate_ir = twirl_circuit(q)
    pass


cz_pattern = [[0, 1], [2, 3], [1, 2]]
ir = twirl_circuit([0,1,2,3,4,5], cz_pattern)

