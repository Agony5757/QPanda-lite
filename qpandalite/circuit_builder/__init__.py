from .basic_gates import SingleQubitRotation, Rx, Ry, Rz
from .qcircuit import Circuit, Fragment

'''Philosophy

Qubit is a wire

Gate links virtual wires
  -> (assign) Assigning qubits to Gate will make it link to different virtual wires

Circuit is a list of Gates

'''