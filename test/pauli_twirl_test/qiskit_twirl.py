from qiskit import QuantumCircuit, execute, transpile
import numpy as np
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit_aer import AerSimulator
import re
import pyqpanda as pq
from step0_model import XY_circuit

TWIRL_GATES = {
    "cx": (
        (("id", "id"), ("id", "id")),
        (("id", "x"), ("id", "x")),
        (("id", "y"), ("z", "y")),
        (("id", "z"), ("z", "z")),
        (("x", "id"), ("x", "x")),
        (("x", "x"), ("x", "id")),
        (("x", "y"), ("y", "z")),
        (("x", "z"), ("y", "y")),
        (("y", "id"), ("y", "x")),
        (("y", "x"), ("y", "id")),
        (("y", "y"), ("x", "z")),
        (("y", "z"), ("x", "y")),
        (("z", "id"), ("z", "id")),
        (("z", "x"), ("z", "x")),
        (("z", "y"), ("id", "y")),
        (("z", "z"), ("id", "z")),
    ),
    "cz": (
        (("id", "id"), ("id", "id")),
        (("id", "x"), ("z", "x")),
        (("id", "y"), ("z", "y")),
        (("id", "z"), ("id", "z")),
        (("x", "id"), ("x", "z")),
        (("x", "x"), ("y", "y")),
        (("x", "y"), ("y", "x")),
        (("x", "z"), ("x", "id")),
        (("y", "id"), ("y", "z")),
        (("y", "x"), ("x", "y")),
        (("y", "y"), ("x", "x")),
        (("y", "z"), ("y", "id")),
        (("z", "id"), ("z", "id")),
        (("z", "x"), ("id", "x")),
        (("z", "y"), ("id", "y")),
        (("z", "z"), ("z", "z")),
    ),
}
four_pauli = ['id', 'x', 'y', 'z']


def generate_twirl(rand1, rand2, gate):
    pair = (rand1, rand2)
    for x, y in TWIRL_GATES[gate]:
        if x == pair:
            return y
    raise NotImplementedError


def generate_random_pauli_pair(gate='cz'):
    l1, l2 = np.random.choice(four_pauli, 2)
    r1, r2 = generate_twirl(l1, l2, gate)
    return l1, l2, r1, r2


def barrier_all(qubit_list):
    qasm = f'barrier '
    qubit_str = [f'q[{q}]' for q in qubit_list]
    qasm += ', '.join(qubit_str) + ';\n'
    return qasm


def twirl_circuit(qubit_set, cz_qubits, gate='cz'):
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
            ir += f'{pauli} q[{q}];\n'
        else:
            if q not in pauli_list:
                l1, l2, r1, r2 = generate_random_pauli_pair(gate)
                another_q = cz_pair[q]
                pauli_list[q] = l1
                pauli_list[another_q] = l2
                ir += f'{l1} q[{q}];\n'
                ir += f'{l2} q[{another_q}];\n'
                conj_list[q] = r1
                conj_list[another_q] = r2

    ir += barrier_all(qubit_list=qubit_set)

    for q, another_q in cz_pair.items():
        ir += f'{gate} q[{q}],q[{another_q}];\n'
    ir += barrier_all(qubit_list=qubit_set)

    for q, pauli in conj_list.items():
        ir += f'{pauli} q[{q}];\n'
    # ir += barrier_all(qubit_list=qubit_set)
    return ir


def readout_twirl(qubit_list):
    ir = ''
    flip = np.random.random(len(qubit_list)) < 0.5
    for i in range(len(qubit_list)):
        if flip[::-1][i]:
            ir += f'x q[{qubit_list[i]}];\n'
    for index, qubit in enumerate(qubit_list):
        ir += f'measure q[{qubit}] -> c[{index}];\n'
    return ir, flip


def circuit_to_benchmark_layers(qc):
    layers = []
    qc = qc
    dag = circuit_to_dag(qc)
    for layer in dag.layers():
        layer_as_circuit = dag_to_circuit(layer['graph'])
        layer_qasm = layer_as_circuit.qasm().strip().split('\n')
        layers.append(layer_qasm)
        # layer_qasm =
        # inst_list = [inst for inst in layer_as_circuit if not inst.ismeas()]
        # while inst_list:
        #     circ = qc.copy_empty()
        #     layer_qubits = set()
        #     for inst in inst_list.copy():
        #         if not layer_qubits.intersection(inst.support()):
        #             circ.add_instruction(inst)
        #             inst_list.remove(inst)
        #         if inst.weight() == 2:
        #             layer_qubits = layer_qubits.union(inst.support())
        #     layers.append(circ)
    return layers


def get_2q_gate_qubits_from_qasm(line):
    regexp_2q = re.compile(r'^([a-z]+) *q\[(\d+)\],*q\[(\d+)\];$')
    matches = regexp_2q.match(line)
    operator = matches.group(1)
    q1 = matches.group(2)
    q2 = matches.group(3)
    return operator, q1, q2


def twirl_layers_circuits(qasm, qubit_map=None):
    qubit_number = QuantumCircuit.from_qasm_str(qasm).num_qubits
    if qubit_map is None:
        qubit_map = list(range(qubit_number))
    qasm = mapping_qubits(qasm, qubit_map)
    qc = QuantumCircuit.from_qasm_str(qasm)
    # qubit_set = list(range(qc.num_qubits))
    qubit_set = qubit_map
    layers = circuit_to_benchmark_layers(qc)
    twirled_qasm = '\n'.join(layers[0][:4])+'\n'
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
            new_qasm = twirl_circuit(qubit_set, pattern, two_qubit_gate)
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


def flip_result(result, flip, reverse=False):
    if reverse:
        flip = flip[::-1]
    new_result_flip = {}
    for key, value in result.items():
        new_key = ''
        for i, r in enumerate(key):
            if flip[i]:
                new_key += str(1 - int(r))
            else:
                new_key += r
        new_result_flip[new_key] = value
    return new_result_flip


def mapping_qubits(qasm, coupling_map):
    prog = QuantumCircuit.from_qasm_str(qasm)
    new_prog = transpile(prog, initial_layout=coupling_map, optimization_level=1, basis_gates=['rx','ry','rz','cz'])
    return new_prog.qasm()


if __name__ == '__main__':

    num = 4
    layer = 2
    model = XY_circuit(num, layer)
    result = []
    twirl_result = []
    simulator = AerSimulator()
    target = '1' + '0'*(num-1)
    for time in np.linspace(0, np.pi*2, 10):
        prog = model.ising_simulation_time(np.pi, time)
        job = execute(prog, simulator)
        counts = job.result().get_counts()
        if target in counts:
            result.append(counts[target])
        else:
            result.append(0)

        twirl_qasm, flip = twirl_layers_circuits(prog.qasm(), qubit_map=[25,26,27,28])
        twirl_prog = QuantumCircuit.from_qasm_str(twirl_qasm)
        new_job = execute(twirl_prog, simulator)
        new_counts = new_job.result().get_counts()
        new_counts_flip = flip_result(new_counts, flip)
        if target in new_counts_flip:
            twirl_result.append(new_counts_flip[target])
        else:
            twirl_result.append(0)

    print(result)
    print(twirl_result)
    print(twirl_qasm)
    # new_qasm = mapping_qubits(twirl_qasm, coupling_map=[0,1,4,5])
    # print(new_qasm)

    # ising_qc = ising_simulation_time(num, J, 3, np.pi, np.pi)
    # new_qasm, flip_list = twirl_layers_circuits(ising_qc.qasm())
    #
    # qc = ising_simulation_time(4, J, 2, np.pi, np.pi)
    # new_qasm, flip_list = twirl_layers_circuits(qc)



