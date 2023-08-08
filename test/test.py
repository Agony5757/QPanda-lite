from qpandalite import Circuit, Rx, BigGate
import math
c = Circuit(n_qubit = 5)
c.rx(3, angle=1.0)
c.rx(2, math.pi)
print(c)

c1 = c.assign(q3 = 2, q2 = 3)
print(c)
print(c1)

c.append(c1)

def Toffoli():
    c = BigGate(n_qubit = 3, name = 'Toffoli')
    c.rx(1, 0.1)
    c.rx(2, 0.2)
    c.rx(0, 0.3)
    return c

c.append(Toffoli().assign([4,2,1]))
c.append(Toffoli().assign(q0 = 4, q1 = 2, q2 = 3))

print(c)
print(Toffoli())