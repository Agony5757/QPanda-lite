'''
Basic gates.

Author: Agony5757
'''

class Gate:
    def __init__(self):
        pass

    def __repr__(self) -> str:
        pass

class SingleQubitRotation(Gate):
    def __init__(self, qubit, angle = 0):
        if isinstance(angle, str):
            self.parametric_angle = True
        elif isinstance(angle, float):
            self.parametric_angle = False
        else:
            raise RuntimeError('Cannot handle input')

        if isinstance(angle, str):
            self.parametric_qubit = True
        elif isinstance(angle, float):
            self.parametric_qubit = False
        else:
            raise RuntimeError('Cannot handle input')

        self.qubit = qubit
        self.angle = angle

    def is_parametric_angle(self):
        return self.parametric_angle
    
    def is_parametric_qubit(self):
        return self.parametric_qubit

class Rx(SingleQubitRotation):
    def __init__(self, qubit, angle = 0):
        super().__init__(self, qubit, angle)
        self.gate_type = 'Rx'

class Ry(SingleQubitRotation):
    def __init__(self, qubit, angle = 0):
        super().__init__(self, qubit, angle)
        self.gate_type = 'Ry'

class Rz(SingleQubitRotation):
    def __init__(self, qubit, angle = 0):
        super().__init__(self, qubit, angle)
        self.gate_type = 'Rz'
