import numpy as np
import pyqpanda as pq
import os


def CNOT(q1, q2):
    cir = pq.QCircuit()
    cir << pq.H(q2) << pq.CZ(q1, q2) << pq.H(q2)
    return cir


def xxyy(q1, q2, J, dt):
    '''
    generate exp(-i*angle*(s_x s_x+s_y s_y))
    :param q1: the first qubit
    :param q2: the second qubit
    :param angle: angle
    :return: iSWAP(q1, q2, angle)
    '''
    xycir = pq.QCircuit()
    angle = J * dt / 2
    xycir << pq.RX(q1, np.pi / 2) << pq.RX(q2, np.pi / 2) << CNOT(q1, q2) << pq.RX(q1, angle) << pq.RZ(q2, angle) \
        << CNOT(q1, q2) << pq.RX(q1, -np.pi / 2) << pq.RX(q2, -np.pi / 2)
    return xycir


def xy_layer(qlist, J, dt, parallel_patterns):
    cir = pq.QCircuit()
    num = len(qlist)
    for pattern in parallel_patterns:
        for cz in pattern:
            if cz[0] >= num or cz[1] >= num:
                continue
            cir << xxyy(qlist[cz[0]], qlist[cz[1]], J[cz[0]], dt)
        # cir << pq.BARRIER(qlist)
    return cir


def ising_simulation_time(num, J, n, t, theta=np.pi/2, noise=0, save='', parallel_pattern=None):
    """

    :param num: qubit number
    :param J: coupling strength
    :param n: trotter steps
    :param t: evolution time
    :param theta: initial state RX(theta)|0>, default by pi/2, |10...0>
    :param noise: 0 means use CPUQVM, other float use depolarizing noise simulator
    :param save: if '', then only simulate. if give a string, then make a dictionary and save the origin ir files.
    :return:
    result: measurement result
    """
    if parallel_pattern is None:
        parallel_pattern = [[[0, 1], [2, 3]], [[1, 2], [4, 5]],
                            [[3, 4]], [[5, 6]]]
    if noise == 0:
        qvm = pq.CPUQVM()
        qvm.init_qvm()
    else:
        qvm = pq.NoiseQVM()
        qvm.init_qvm()
        qvm.set_noise_model(pq.NoiseModel.DEPOLARIZING_KRAUS_OPERATOR, pq.GateType.CNOT_GATE, noise)

    q = qvm.qAlloc_many(num)
    c = qvm.cAlloc_many(num)
    prog = pq.QProg()
    prog << pq.RX(q[0], theta)
    for i in range(n):
        prog << xy_layer(q, J, t/n, parallel_patterns=parallel_pattern)
    bit_flip = np.random.random(n) < 0.5
    for i in range(n):
        if bit_flip[i]:
            prog << pq.X(q[i])
    prog << pq.measure_all(q, c)
    # new_prog = pq.transform_to_base_qgate(prog, qvm)
    # new_prog = pq.virtual_z_transform(new_prog, qvm, b_del_rz_gate=True)
    ir = pq.convert_qprog_to_originir(prog, qvm)
    result = qvm.run_with_configuration(prog, c, 100)
    new_result = {}
    for key, value in result.items():
        new_key = []
        for i in range(n):
            if bit_flip:
                new_key.append(str(1-int(key[i])))
            else:
                new_key.append(key[i])
        new_result[new_key] = value
    return ir, new_result


def simple_rx_model(n, theta):
    qvm = pq.CPUQVM()
    qvm.init_qvm()
    q = qvm.qAlloc_many(2)
    c = qvm.cAlloc_many(2)
    prog = pq.QProg()
    for i in range(n):
        prog << pq.RY(q[0], theta/n) << pq.CNOT(q[0], q[1])
    prog << pq.measure_all(q, c)
    # prog << pq.RX(q, theta) << pq.measure_all(q, c)
    ir = pq.convert_qprog_to_originir(prog, qvm)
    result = qvm.run_with_configuration(prog, c, 1000)

    return ir, result


if __name__ == '__main__':
    n = 4
    layer = 2
    t = np.pi
    theta = np.pi
    J = np.array([np.sqrt(i * (n - i)) for i in range(1, n)])
    r = ising_simulation_time(n, J, layer, t, theta=theta, noise=0, save='test')
    pass
