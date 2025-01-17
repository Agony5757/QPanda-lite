import qpandalite
from qpandalite.simulator import (Simulator, 
                                  NoisySimulator,
                                  NoisySimulator_GateDependent, 
                                  NoisySimulator_GateSpecificError)
from qpandalite.qasm_origin import OpenQASM2_Parser
from qpandalite.circuit_builder import Circuit
from qpandalite.simulator import seed
from qpandalite.test._utils import qpandalite_test

import time

@qpandalite_test('Simulator')
def run_test_simulator():
    test_noisy_simulator()

def test_noisy_simulator():

    measure_qubits = [0, 1]
    shots = 1024

    current_time_seed = int(time.time())
    # Use the current time as a seed
    seed(current_time_seed)
    
    noise_description = {
        "depolarizing": 0.01
    }
    
    gate_noise_description = {
        "X": {"depolarizing": 0.03},
        "HADAMARD": {"depolarizing": 0.02},
        "ISWAP": {"depolarizing": 0.02}
    }
        
    # Define the measurement errors
    measurement_error = [(0.01, 0.01), (0.02, 0.02)]
    
    # Create an instance of the NoisySimulator
    simulator = NoisySimulator(2,noise_description, measurement_error)

    measurement_results = simulator.measure_shots(measure_qubits=measure_qubits, shots=shots)
