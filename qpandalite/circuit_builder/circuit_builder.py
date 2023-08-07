import warnings

class QCircuit:
    '''
    A template of circuit object. By assigning the qubit, we can create a concrete insertable circuit.    
    The qubit/cbit in the gate template is represented by {q1}/{q2}/{q3}... instead of q1/q2/q3.
    It allows users to format the gate template and assign it to the circuit.

    Example:

    toffoli = GateTemplate(n_qubit = 3)
        (... some definitions)
    toffoli_123   = toffoli.assign(q1 = 1, q2 = 2, q3 = 3) # to assign the corresponding qubits, returning a 'Gate'
    toffoli_214   = toffoli.assign(q1 = 2, q2 = 1, q3 = 4) # to assign the corresponding qubits, returning a 'Gate'
    toffoli_fix_1 = toffoli.assign(q1 = 1) # to assign partially, returning another 'GateTemplate'

    c = Circuit()
    c.gate(toffoli_123)                             # good
    c.gate(toffoli)                                 # bad, because it is not fully converted to a gate
    c.gate(toffoli_fix_1.format(q2 = 2, q3 = 3))    # good
    '''

    def __init__(self, n_qubit = 1, n_cbit = 0):
        self.n_qubit = n_qubit
        self.n_cbit = n_cbit

    def __repr__(self) -> str:
        pass

    def assign(self, **kwargs):
        pass


class QProg:
    '''
    An abstract representation of a quantum circuit.
    Attributes:
        - n_qubit : number of qubits
        - n_cbit : number of cbits
        - gate_list (Python list) : a list of gates
    '''

    def __init__(self, n_qubit = 1, n_cbit = 0):
        '''
        Constructing an empty circuit.
        Args:
            n_qubit : number of qubits
            n_cbit : number of cbits
        '''
        self.n_qubit = n_qubit
        self.n_cbit = n_cbit
        self.gate_list = []
        self.has_measure = False
        if (not n_qubit) and (not n_cbit):
            warnings.warn('A completely empty circuit instance is created. (n_qubit = n_cbit = 0)')

    def __repr__(self) -> str:
        return ('{} qubits\n'
                '{} cbits\n'
                '{} gates\n'
                ).format(self.n_qubit, self.n_cbit, len(self.gate_list))
    
    def append(self, gate):
        self.gate_list.append(gate)

    def dagger(self):
        if self.has_measure:
            raise RuntimeError('Cannot inverse a classical-involved circuit.')
        

    def to_originir(self) -> str:
        '''
        Convert to originir
        '''
        pass
        