from qiskit import QuantumCircuit, execute
from qiskit_aer import AerSimulator
from my_task import *
from qiskit_twirl import twirl_layers_circuits, mapping_qubits
from step0_model import XY_circuit
import numpy as np
import json


def different_initial_state(qubit_num, layers, evolve_time=np.pi, circuit_number=100, mapping=None):
    if mapping is None:
        mapping = list(range(qubit_num))
    before_twirl_circuits = []
    twirl_circuits = []
    theory_result = []
    model = XY_circuit(qubit_num, layers)
    for initial_theta in np.linspace(0, np.pi * 2, circuit_number):
        prog = model.ising_simulation_time(initial_theta, evolve_time)
        before_twirl_prog = prog.qasm()
        # before_twirl_prog = mapping_qubits(before_twirl_prog, mapping)
        single_twirl_circuit = []
        for i in range(50):
            twirl_qasm, flip = twirl_layers_circuits(before_twirl_prog, mapping)
            # twirl_qasm = mapping_qubits(twirl_qasm, mapping)
            single_twirl_circuit.append((twirl_qasm, flip))
        before_twirl_circuits.append(before_twirl_prog)
        twirl_circuits.append(single_twirl_circuit)
        theory_result.append(np.sin(initial_theta / 2) ** 2)
    return before_twirl_circuits, twirl_circuits, theory_result


def different_evolve_time(qubit_num, layers, initial_theta=np.pi, circuit_number=100, mapping=None):
    before_twirl_circuits = []
    twirl_circuits = []
    flip_list = []
    theory_result = []
    model = XY_circuit(qubit_num, layers)
    for evolve_time in np.linspace(0, np.pi * 2, circuit_number):
        prog = model.ising_simulation_time(initial_theta, evolve_time)
        before_twirl_prog = prog.qasm()
        twirl_qasm, flip = twirl_layers_circuits(before_twirl_prog, mapping)
        before_twirl_circuits.append(before_twirl_prog)
        twirl_circuits.append(twirl_qasm)
        flip_list.append(flip)
        theory_result.append(np.sin(initial_theta / 2) ** (2 * qubit_num))
    return before_twirl_circuits, twirl_circuits, flip_list, theory_result


if __name__ == '__main__':
    num = 4
    layer = 2
    before_twirl_circuits, twirl_circuits, theory_result = \
        different_initial_state(num, layer, circuit_number=50, mapping=[31, 30, 42, 43])
    savepath = Path.cwd() / 'quafu_online_info_verify'
    provider = login('quafu')
    simulator = AerSimulator()
    result_dict = {}
    for index, circuit in enumerate(before_twirl_circuits):
        taskid, taskname = submit_single_circuit_quafu(circuit,
                                                       task_name=f'quafu no twirl-{index}',
                                                       shots=4000,
                                                       chip_id='ScQ-P136',
                                                       auto_mapping=False,
                                                       savepath=savepath,
                                                       user=provider)
        print(taskid, taskname)
        # prog = QuantumCircuit.from_qasm_str(circuit)
        # job = execute(prog, simulator)
        # result = job.result().get_counts()
        # print(sorted(result.items(), key=lambda i:i[1], reverse=True))
    for index, circuit_list in enumerate(twirl_circuits[:25]):
        # twirl_result[index] = {}
        for twirl_index, circuit in enumerate(circuit_list):
            taskid, taskname = submit_single_circuit_quafu(circuit[0],
                                                           task_name=f'quafu circuit-{index}, twirl-{twirl_index}',
                                                           shots=256,
                                                           chip_id='ScQ-P136',
                                                           savepath=savepath,
                                                           auto_mapping=False,
                                                           user=provider)
            print(taskname, taskid)
            # prog = QuantumCircuit.from_qasm_str(circuit[0])
            # job = execute(prog, simulator)
            # result = job.result().get_counts()
            # print(sorted(result.items(), key=lambda i: i[1], reverse=True))

    for index, circuit_list in enumerate(twirl_circuits[25:]):
        # twirl_result[index] = {}
        for twirl_index, circuit in enumerate(circuit_list):
            taskid, taskname = submit_single_circuit_quafu(circuit[0],
                                                           task_name=f'quafu circuit-{index+25}, twirl-{twirl_index}',
                                                           shots=256,
                                                           chip_id='ScQ-P136',
                                                           savepath=savepath,
                                                           auto_mapping=False,
                                                           user=provider)
            print(taskname, taskid)

    flip_result = {}
    for circuit_index, all_circuit in enumerate(twirl_circuits):
        flip_dict = {}
        for index, circuit in enumerate(all_circuit):
            flip_dict["twirl {}".format(index)] = circuit[1].tolist()
        flip_result["circuit {}".format(circuit_index)] = flip_dict.copy()

    with open(savepath / 'flip result.txt', 'w') as f:
        json.dump(flip_result, f)

