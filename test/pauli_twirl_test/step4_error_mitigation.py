import numpy as np
from qiskit import QuantumCircuit
from qiskit_twirl import *


def change_pauli_into_xz(pauli):
    ax = []
    az = []
    for index, p in enumerate(pauli):
        if p == 'X':
            ax.append(1)
            az.append(0)
        if p == 'Y':
            ax.append(1)
            az.append(1)
        if p == 'Z':
            ax.append(0)
            az.append(1)
        if p == 'I':
            ax.append(0)
            az.append(0)
    return np.array(ax), np.array(az)


def calculate_commutant(pauli_a, pauli_b):
    ax, az = change_pauli_into_xz(pauli_a)
    bx, bz = change_pauli_into_xz(pauli_b)
    return np.sum(ax*bz+az*bx) % 2


def get_probability_map(qubit_number, noise_parameter_map):
    all_pauli = [''.join(i) for i in product('IXYZ', repeat=qubit_number)]
    probability_map = {}
    for pauli_b in all_pauli:
        c = 0
        for pauli_a, f in noise_parameter_map.items():
            c += (-1) ** calculate_commutant(pauli_a, pauli_b) / f
        c = c / 2**qubit_number
        probability_map[pauli_b] = c

    gamma = sum([abs(i) for i in probability_map.values()])
    sign = 1
    for key, value in probability_map.items():
        probability_map[key] = abs(value) / gamma
        sign *= np.sign(value)
    return probability_map, sign, gamma


def random_pauli(probability_map):
    intervals = []
    s = 0
    for key, value in probability_map.items():
        intervals.append([s, s+value, key])
        s += value
    r = np.random.random()
    for i in intervals:
        if i[0] <= r <= i[1]:
            return i[2]


def mitigate_two_qubit_gate(qubit_set, cz_qubits, probability_map, gate='cz'):
    ir_before = twirl_circuit(qubit_set, cz_qubits, gate)
    pauli = random_pauli(probability_map)
    ir = ''
    for index, qubit in enumerate(qubit_set):
        ir += f'{pauli[index]} q[{qubit}];\n'
    ir = ir + ir_before
    return ir


def mitigation_circuit(qasm, qubit_map, noise):
    qubit_number = QuantumCircuit.from_qasm_str(qasm).num_qubits
    if qubit_map is None:
        qubit_map = list(range(qubit_number))
    qasm = mapping_qubits(qasm, qubit_map)
    qc = QuantumCircuit.from_qasm_str(qasm)
    # qubit_set = list(range(qc.num_qubits))
    qubit_set = qubit_map
    layers = circuit_to_benchmark_layers(qc)
    twirled_qasm = '\n'.join(layers[0][:4])+'\n'
    total_gamma = 1
    total_sign = 1
    for layer in layers:
        gates = layer[4:]
        pattern = []
        new_gates = gates.copy()
        for gate in gates:
            if gate.startswith('c') and not gate.startswith('creg'):
                two_qubit_gate, q1, q2 = get_2q_gate_qubits_from_qasm(gate)
                pattern.append([int(q1), int(q2)])
            if gate.startswith('measure'):
                new_gates.remove(gate)
        if pattern:
            p_map, sign, gamma = get_probability_map(len(qubit_map), noise)
            total_sign *= sign
            total_gamma *= gamma
            new_qasm = mitigate_two_qubit_gate(qubit_set, pattern, probability_map=p_map, gate=two_qubit_gate)
            twirled_qasm += new_qasm
        else:
            twirled_qasm += '\n'.join(new_gates) + '\n'
    measure_qasm, flip_list = readout_twirl(qubit_set)
    twirled_qasm += measure_qasm

    twirled_delete_id = []
    for line in twirled_qasm.split('\n'):
        # if not line.startswith('id'):
        if not 'id' in line:
            twirled_delete_id.append(line)
    twirled_qasm = '\n'.join(twirled_delete_id)
    return twirled_qasm, flip_list


if __name__ == '__main__':
    from itertools import product

    s = [''.join(i) for i in list(product('IXYZ', repeat=3))]
    y = np.random.random(64)
    y = y / np.sum(y)
    d = dict(zip(s, y))
    print(random_pauli(d))
