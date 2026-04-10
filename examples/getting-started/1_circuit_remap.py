'''This is the demo for QPanda-lite

# 1. Build circuit and remap

## Concepts:
    
    Build Circuit: Before running the circuit, you must prepare a circuit input.
    Remap: Specify the qubit ID corresponding to the real chip, which is also known as 'qubit mapping'.

'''

import qpandalite
import math

def demo_1():    
    # Start from here.
    c = qpandalite.Circuit()

    # Define the gates with the simplest format.
    c.x(0)
    c.rx(1, math.pi)
    c.ry(2, math.pi / 2)
    c.cnot(2, 3)
    c.cz(1,2)

    # Measure the qubits you want.
    c.measure(0,1,2)

    # Print the original circuit    
    print(c.circuit)

    # Use this to create a remapping (this is NOT an inplace operation.)
    c = c.remapping({0 : 100, 1: 101, 2: 102, 3: 103})

    # Output as a str
    print(c.circuit)

    # The same with c.circuit
    print(c.originir)

if __name__ == '__main__':
    demo_1()

    # Output 1:
    # QINIT 4
    # CREG 3
    # X q[0]
    # RX q[1], (3.141592653589793)
    # RY q[2], (1.5707963267948966)
    # CNOT q[2], q[3]
    # CZ q[1], q[2]
    # MEASURE q[0], c[0]
    # MEASURE q[1], c[1]
    # MEASURE q[2], c[2]
    
    # Output 2:
    # QINIT 4
    # CREG 3
    # X q[100]
    # RX q[101], (3.141592653589793)
    # RY q[102], (1.5707963267948966)
    # CNOT q[102], q[103]        # Note that the qubit ID has been changed.
    # CZ q[101], q[102]
    # MEASURE q[100], c[0]
    # MEASURE q[101], c[1]
    # MEASURE q[102], c[2]