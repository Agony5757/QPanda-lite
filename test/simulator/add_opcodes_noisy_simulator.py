from qpandalite.simulator import NoisySimulator
from qpandalite.qasm_origin import OpenQASM2_Parser
import numpy as np
import qpandalite.simulator as qsim
from qpandalite.circuit_builder import Circuit
from qpandalite.originir import OriginIR_Parser, OriginIR_BaseParser

c = Circuit()

# c.h(0)
c.x(0)
# c.h(1)
c.z(1)
# c.iswap(0, 1)
c.rx(0, np.pi/8)
c.ry(0, np.pi/4)
c.rz(0, np.pi/2)
# c.rphi90(1, np.pi/8)
# c.rphi180(1, np.pi/4)
# c.rphi(1, np.pi/2, np.pi/4)
parser = OriginIR_BaseParser()
parser.parse(c.originir)


print(parser.program_body)

# Define the noise descriptions
noise_description = {
    "damping": 0.01
}

# Define the gate noise descriptions
gate_noise_description = {
    "X": {"depolarizing": 0.03},
    "HADAMARD": {"depolarizing": 0.02}
}

# Define the measurement errors
measurement_error = [(0.01, 0.01), (0.02, 0.02)]

# Create an instance of the NoisySimulator
simulator = NoisySimulator(2,noise_description, gate_noise_description)

for code in parser.program_body:
     # Deconstruct the opcode into individual components
    operation, qubit, cbit, parameter, dagger_flag, control_qubits_set = code
    
    # Convert control qubits set to list if not None
    control_qubits_list = list(control_qubits_set) if control_qubits_set else []
    
    # Convert parameter to a list if not None, else to an empty list
    parameters_list = [parameter] if parameter else []

    # Call the load_opcode method on the simulator for each opcode
    simulator.load_opcode(operation, [qubit], parameters_list, dagger_flag, control_qubits_list)


# Number of measurement shots
shots = 1024

# Measure the state multiple times
measurement_results = simulator.measure_shots(shots)
print(measurement_results)