from qpandalite import Circuit, Rx, Fragment
import math
c = Circuit('hello')
c.rx(3, angle=1.0)
c.rx(2, math.pi)
print(c)

c1 = c.assign(q3 = 2, q2 = 3)
print(c)
print(c1)

c.append(c1)
print(c)

def Toffoli():
    c = Fragment(name = 'Toffoli')
    c.rx(1, 0.1)
    c.rx(2, 0.2)
    c.rx(0, 0.3)
    return c


def Toffoli_2():
    c = Circuit(name = 'Toffoli2')
    c.expand = False
    c.rx(1, 0.1)
    c.rx(2, 0.2)
    c.rx(0, 0.3)
    return c

def Toffoli_3():
    c = Circuit(name = 'Toffoli3')
    c.rx(1, 0.1)
    c.rx(2, 0.2)
    c.rx(0, 0.3)
    return c

c.append(Toffoli().assign([4,1,2]))
c.append(Toffoli().assign(q0 = 4, q1 = 2, q2 = 3))
c.append(Toffoli_2())
c.append(Toffoli_3())

print(c)
print(Toffoli())