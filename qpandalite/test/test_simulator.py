import qpandalite
from qpandalite.simulator import (StatevectorSimulator)
from qpandalite.qasm import OpenQASM2_LineParser
from qpandalite.circuit_builder import Circuit
from qpandalite.simulator import seed
from qpandalite.simulator import OriginIR_Simulator, OriginIR_NoisySimulator

import time

from qpandalite.test._utils import qpandalite_test
from qpandalite.simulator.error_model import *


def test_noisy_simulator():    
    circuit = Circuit()
    circuit.x(0)
    circuit.h(1)
    circuit.cx(0, 1)
    circuit.h(2)
    circuit.cx(1, 2)
    circuit.h(3)
    circuit.cx(2, 3)
    circuit.h(4)
    circuit.cx(3, 4)
    circuit.h(5)
    circuit.cx(4, 5)

    shots = 1024
    measure_qubit = [0, 1, 2, 3, 4, 5]
    circuit.measure(*measure_qubit)

    current_time_seed = int(time.time())
    # Use the current time as a seed
    seed(current_time_seed)
    
    generic_noise_description = [Depolarizing(0.01)]
    
    gatetype_description = {
        "X": [Depolarizing(0.03)],
        "HADAMARD": [Depolarizing(0.02), AmplitudeDamping(0.01)],
        "ISWAP": [Depolarizing(0.02)]
    }

    gate_specified_noise_description = {
        ("CNOT", (1,2)): [Depolarizing(0.01), Depolarizing(0.02)],
        ("CZ", (1,2)): [Depolarizing(0.03)],
        ("X", 1): [Depolarizing(0.03)],
        ("Y", 1): [Depolarizing(0.03)],
        ("Z", 1): [Depolarizing(0.03)],
        ("ISWAP", (1,2)): [Depolarizing(0.03)],
        ("HADAMARD", 1): [Depolarizing(0.03)],
        ("RX", 1): [Depolarizing(0.03)],
    }        
    # Define the measurement errors
    readout_error = {0:(0.01, 0.01), 
                         1:(0.02, 0.02),
                         2:(0.03, 0.03),
                         3:(0.02, 0.02),
                         4:(0.01, 0.01),
                         5:(0.03, 0.03)}

    error_loader = ErrorLoader_GateSpecificError(
        generic_noise_description,
        gatetype_description,
        gate_specified_noise_description
    )

    print(error_loader)
    
    # Create an instance of the NoisySimulator
    simulator = OriginIR_NoisySimulator(
        backend_type='statevector',
        error_loader=error_loader,
        readout_error=readout_error
    )

    measurement_results = simulator.simulate_shots(circuit.originir, shots=shots)

    print(measurement_results)


def test_noisy_simulator_2():    
    circuit = Circuit()
    circuit.x(0)
    circuit.x(1)
    circuit.x(2)
    circuit.x(3)
    circuit.x(4)
    circuit.x(5)

    shots = 1024
    measure_qubit = [0, 1, 2, 3, 4, 5]
    circuit.measure(*measure_qubit)

    current_time_seed = int(time.time())
    # Use the current time as a seed
    seed(current_time_seed)
    
    generic_noise_description = [Depolarizing(0.01)]
    
    gatetype_description = {
        "X": [Depolarizing(0.03)],
        "HADAMARD": [Depolarizing(0.02), AmplitudeDamping(0.01)],
        "ISWAP": [Depolarizing(0.02)]
    }

    gate_specified_noise_description = {
        ("CNOT", (1,2)): [Depolarizing(0.01), Depolarizing(0.02)],
        ("CZ", (1,2)): [Depolarizing(0.03)],
        ("X", 1): [Depolarizing(0.03)],
        ("Y", 1): [Depolarizing(0.03)],
        ("Z", 1): [Depolarizing(0.03)],
        ("ISWAP", (1,2)): [Depolarizing(0.03)],
        ("HADAMARD", 1): [Depolarizing(0.03)],
        ("RX", 1): [Depolarizing(0.03)],
    }        
    # Define the measurement errors
    readout_error = {0:(0.01, 0.01), 
                    1:(0.02, 0.02),
                    2:(0.03, 0.03),
                    3:(0.02, 0.02),
                    4:(0.01, 0.01),
                    5:(0.03, 0.03)}

    error_loader = ErrorLoader_GateSpecificError(
        generic_noise_description,
        gatetype_description,
        gate_specified_noise_description
    )

    print(error_loader)
    
    # Create an instance of the NoisySimulator
    simulator = OriginIR_NoisySimulator(
        backend_type='density_matrix',
        error_loader=error_loader,
        readout_error=readout_error
    )

    measurement_results = simulator.simulate_pmeasure(circuit.originir)

    print(measurement_results)

@qpandalite_test('Test Simulator')
def run_test_simulator():
    test_noisy_simulator()
    test_noisy_simulator_2()

if __name__ == '__main__':
    run_test_simulator()