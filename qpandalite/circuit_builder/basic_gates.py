'''
Basic gates.

Author: Agony5757
'''
from copy import deepcopy

class Gate:
    def __init__(self):
        pass

    def __repr__(self) -> str:
        pass

    def is_parametric(self) -> bool:
        pass

    def involved_qubits(self) -> list:
        pass

    def assign_by_map(self, qubit_map):
        pass

class SingleQubitRotation(Gate):
    def __init__(self, qubit, angle = 0):
        if isinstance(angle, str):
            self.parametric_angle = True
        elif isinstance(angle, float):
            self.parametric_angle = False
        elif isinstance(angle, int):
            self.parametric_angle = False
        else:
            raise RuntimeError(f'Cannot handle input (angle = {angle})')

        if isinstance(qubit, str):
            self.parametric_qubit = True
        elif isinstance(qubit, int):
            self.parametric_qubit = False
        else:
            raise RuntimeError(f'Cannot handle input (qubit = {qubit})')

        self.qubit = qubit
        self.angle = angle
        self.gate_type = '[Abstract]SingleQubitRotation'

    def is_parametric_angle(self) -> bool:
        return self.parametric_angle
    
    def is_parametric_qubit(self) -> bool:
        return self.parametric_qubit

    def is_parametric(self) -> bool:
        return self.is_parametric_angle() or self.is_parametric_qubit()

    def __repr__(self) -> str:        
        return "{}({}) q[{}]".format(self.gate_type, self.angle, self.qubit)

    def involved_qubits(self) -> list:
        return [self.qubit]
    
    def assign_by_map(self, qubit_map):
        obj = deepcopy(self)
        if self.qubit not in qubit_map:     
            raise RuntimeError('Assign failed. Involved qubit: {}, qubit_map: {}'.format(self.qubit, qubit_map))
        obj.qubit = qubit_map[self.qubit]
        return obj

class Rx(SingleQubitRotation):
    def __init__(self, qubit, angle = 0.0):
        super().__init__(qubit, angle)
        self.gate_type = 'Rx'

class Ry(SingleQubitRotation):
    def __init__(self, qubit, angle = 0):
        super().__init__(self, qubit, angle)
        self.gate_type = 'Ry'

class Rz(SingleQubitRotation):
    def __init__(self, qubit, angle = 0):
        super().__init__(self, qubit, angle)
        self.gate_type = 'Rz'

