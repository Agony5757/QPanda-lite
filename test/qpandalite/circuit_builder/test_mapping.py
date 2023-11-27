from qpandalite.circuit_builder import Circuit


c = Circuit()
c.h(0)
c.cnot(1, 0)
c.cnot(0, 2)
c.measure(0,1,2)
# c = c.remapping({0:45, 1:100, 2:100}) # ValueError: A physical qubit is assigned more than once.
# c = c.remapping({0:45, 1.0:3, 2:-1}) # TypeError: All keys and values in mapping must be non-negative integers.
print(c.circuit)