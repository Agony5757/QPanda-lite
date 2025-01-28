import qpandalite
from qpandalite.simulator import (StatevectorSimulator)
from qpandalite.qasm import OpenQASM2_LineParser
from qpandalite.circuit_builder import Circuit
from qpandalite.simulator import seed

import time

from qpandalite.test._utils import qpandalite_test
from qpandalite.simulator.error_model import *

def test_noisy_simulator():
    measure_qubits = [0, 1]
    shots = 1024

    current_time_seed = int(time.time())
    # Use the current time as a seed
    seed(current_time_seed)
    
    generic_noise_description = {
        "depolarizing": 0.01
    }
    
    gatetype_description = {
        "X": [Depolarizing(0.03)],
        "HADAMARD": [Depolarizing(0.02), AmplitudeDamping(0.01)],
        "ISWAP": [Depolarizing(0.02)]
    }

    gate_specified_noise_description = {
        ("CNOT", [1,2]): [Depolarizing(0.01), Depolarizing(0.02)],
        ("CZ", [1,2]): [Depolarizing(0.03)],
        ("X", [1]): [Depolarizing(0.03)],
        ("Y", [1]): [Depolarizing(0.03)],
        ("Z", [1]): [Depolarizing(0.03)],
        ("ISWAP", [1,2]): [Depolarizing(0.03)],
        ("HADAMARD", [1]): [Depolarizing(0.03)],
        ("RX", [1]): [Depolarizing(0.03)],
    }        
    # Define the measurement errors
    measurement_error = [(0.01, 0.01), (0.02, 0.02)]
    
    # Create an instance of the NoisySimulator
    # simulator = NoisySimulator(2, noise_description, measurement_error)

    # measurement_results = simulator.measure_shots(measure_qubits=measure_qubits, shots=shots)


@qpandalite_test('Test Simulator')
def run_test_simulator():
    test_noisy_simulator()