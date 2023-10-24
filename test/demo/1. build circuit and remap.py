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

    # Use this to create a remapping (this is NOT an inplace operation.)
    c = c.remapping({0 : 100, 1: 101, 2: 102, 3: 103})

    # Output as a str
    print(c.circuit)

    # The same with c.circuit
    print(c.originir)

if __name__ == '__main__':
    demo_1()