import numpy as np
import math

from qpandalite.simulator import StatevectorSimulator, NoisySimulator
from qpandalite.qasm import OpenQASM2_LineParser
from qpandalite.circuit_builder import Circuit

global_shots = 10000

def circuit(mx, theta):

    # Define the noise descriptions
    noise_description = {
        "damping": 0.01,
        "depolarizing": 0.00
    }

    # Define the gate noise descriptions
    gate_noise_description = {
        "CZ": {"depolarizing": 0.00},
        "RY": {"depolarizing": 0.00}
    }

    # Define the measurement errors
    measurement_error = [(0.01, 0.01), (0.02, 0.02)]

    c = NoisySimulator(2, noise_description, gate_noise_description, measurement_error)
    c.ry(0, np.arccos(mx[0]))
    c.ry(1, np.arccos(mx[1]))
    c.cz(0, 1)
    c.ry(0, theta[0])
    c.ry(1, theta[1])
    # c.measure(0, 1)

    # Number of measurement shots
    shots = global_shots

    # Measure the state multiple times
    measurement_results = c.measure_shots(shots)
    
    return measurement_results

THETA = np.array([-0.25521154,0.26327053])
def NoisyGenerator(theta=THETA, Init=[-0.5, 0], n_iter=25):
    state = Init
    RES = []
    for i in range(n_iter):
        circ = circuit(state, theta)
        # print(circ)
        prob = circ
        state = [(prob[0]+prob[2]-prob[1]-prob[3])/global_shots,
                    (prob[0]+prob[1]-prob[2]-prob[3])/global_shots]
        RES.append(state)
    
    RES = np.array(RES)
    return RES

import matplotlib.pyplot as plt

def plot_compare2(mx_ideal, mx_experiment, filename=None):
    '''
    # 1.无噪声量子线路生成的结果pred_qdm与有噪声结果pred_err(真实芯片)之间的比较;
    # 2....
    '''
    s0 = 4
    marker = '^'
    _dpi = 200
    fig, ax = plt.subplots(dpi=_dpi)
    fig.set_size_inches(6, 4)
    
    Len = 25
    ylim = 1
    title = ' Theoretical and experimental results '
    t_list = np.array([0.08*t for t in range(1,51,1)])
    
    ax.plot(t_list[0:Len], mx_ideal[:,0], color ='darkorange', label='m-Theoretical')
    ax.plot(t_list[0:Len], mx_ideal[:,1], color = 'steelblue', label='x-Theoretical')
    
    ax.plot(t_list[0:Len], mx_experiment[:,0], color ='red', linestyle='--', lw=1,
            marker=marker, fillstyle='none', markersize=s0, label='m-Experimental (with EM)')
    
    ax.plot(t_list[0:Len], mx_experiment[:,1], color = 'blue', linestyle='--',lw=1,
            marker=marker, fillstyle='none', markersize=s0, label='x-Experimental (with EM)')


    ax.set_xlabel(r'$t\Delta$',fontsize=16)
    #ax.set_ylabel(r'x_t\&m_t',fontsize=16)
    #plt.xlim(780,800)
    
    
    #ax.set_title(title, fontsize=16)
    ax.set_ylim(-ylim,ylim)
    #ax.set_xlim(0,2.1)
    #ax.set_xticks([0, 0.4, 0.8, 1.2, 1.6, 2.0])
    #ax.set_yticks([-0.6,-0.3,0.0,0.3,0.6])
    ax.tick_params(axis='both', which='major', labelsize=14)
    
    # ax.legend(loc=2,bbox_to_anchor=(0.0,1.),borderaxespad=0.,ncols=2,fontsize=10)
    ax.legend(loc=2,borderaxespad=0.,ncols=2,fontsize=10)
    if filename is not None:
        plt.savefig(filename, dpi=400, bbox_inches = 'tight', format="svg")
        plt.close()
    else:plt.show()
    return None

def Generator(theta=THETA, Init=[-0.5, 0], n_iter=25):
    RES = []
    m, x = Init[0], Init[1]
    for i in range(n_iter):
        m_p = m*np.cos(theta[0]) - x*np.sqrt(1-m**2)*np.sin(theta[0])
        x_p = x*np.cos(theta[1]) - m*np.sqrt(1-x**2)*np.sin(theta[1])
        RES.append([m_p, x_p])
        m, x = m_p, x_p
    RES = np.array(RES)

    return RES

RES0 = Generator()
RES1 = NoisyGenerator()

plot_compare2(RES0, RES1)