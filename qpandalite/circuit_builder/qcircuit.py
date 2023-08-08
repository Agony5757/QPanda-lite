'''
Definition of quantum circuit (Circuit)

Author: Agony5757
'''

import warnings
from .basic_gates import *

def _check_qubit_overflow(qubits, n):    
    '''
    Check if any qubit in qubits (list) is overflow.
    
    Args:
        qubits : list
        n : int
    Return:
        True (if ok)
        or False (if overflow)
    '''
    for qubit in qubits:
        if qubit >= n:
            return False
        
    return True

def _check_qubit_key(qubit_key: str):
    '''
    check if qubit_key match ''q+any integer'' format (q1, q2, etc.) 
    Return:
        int : if the qubit_key is available, return this qubit
        or None : if not match this style.
    '''
    if not qubit_key.startswith('q'):
        return None
    
    try:
        q = int(qubit_key[1:])
        return q
    except:
        return None

class Circuit:
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

    def __init__(self, n_qubit = None, name = None):
        self.n_qubit = n_qubit
        self.gate_list = []
        if not name:
            self.name = hex(id(self))
        else:
            self.name = name

    def _to_string(self) -> str:       
        ret = '' 
        if self.n_qubit is None:
            ret += '# n_qubit : Unlimited\n'
        else:
            ret += '# n_qubit : {}\n'.format(self.n_qubit)
        
        for gate in self.gate_list:
            ret += '{};\n'.format(gate)
        return ret

    def __repr__(self) -> str:
        ret = '---{:^25s}---\n'.format(f'Circuit {self.name}')
        ret += self._to_string()
        return ret

    def assign_by_map(self, qubit_map):
        ret = Circuit()

        for gate in self.gate_list:
            assigned_gate = gate.assign_by_map(qubit_map)
            ret._append_gate(assigned_gate)
        
        return ret

    def _parse_qubit_map_from_kwargs(self, **kwargs):
        '''
        Implementation of assign (kwargs case).
        '''        
        keys = kwargs.keys()
        qubit_map = dict()
        for key in keys:
            if key == 'n_qubit': continue
            q = _check_qubit_key(key)
            if q is None:
                # do not match q+integer style
                raise RuntimeError('Input must be q+integer=integer style (e.g. q1=1, etc.). User input: {}'.format(key))
            
            assigned_q = kwargs[key]
            if not isinstance(assigned_q, int):
                raise RuntimeError('Input must be q+integer=integer style (e.g. q1=1, etc.). User input: {}, assigned_q: {}'.format(key, assigned_q))
            
            qubit_map[q] = assigned_q

        return qubit_map
    
    def _parse_qubit_map_from_list(self, *args):
        if len(args) == 0:
            raise RuntimeError('Fatal!!! Unexpected error.')
        if isinstance(args[0], list):
            qubit_list = args[0]
        else:
            qubit_list = args
        qubit_map = dict()
        for i, qubit in enumerate(qubit_list):
            qubit_map[i] = qubit
        
        return qubit_map

    def assign(self, *args, **kwargs):        
        if self.n_qubit is None:
            # unlimited circuit, it may not be assignable.
            raise RuntimeError('Cannot assign an unlimited circuit.')
        if len(args) > 0:
            # _assign_list mode
            qubit_map = self._parse_qubit_map_from_list(*args)
        else:
            # _assign_kwargs mode
            qubit_map = self._parse_qubit_map_from_kwargs(**kwargs)

        ret = self.assign_by_map(qubit_map)
        if 'n_qubit' in kwargs:
            n_qubit = kwargs['n_qubit']
            if n_qubit < self.n_qubit:
                raise RuntimeError('Cannot shrink circuit size (self.n_qubit > n_qubit(input) {} > {})'.format(self.n_qubit, n_qubit))
            ret.n_qubit = n_qubit
        else:
            # use the unlimited mode as default
            ret.n_qubit = self.n_qubit

        return ret
            
    def _append_gate(self, gate_object : Gate):
        '''
        add gate to the quantum circuit.
        '''
        if self.n_qubit is None:
            # unlimited mode
            self.gate_list.append(gate_object) 
            return  

        # check overflow
        qubits = gate_object.involved_qubits()
        if not _check_qubit_overflow(qubits, self.n_qubit):
            raise RuntimeError('All qubits must be within the range'
                            '(involved_qubits: {}, n_qubits: {})'
                            .format(qubits, self.n_qubit))  
              
        self.gate_list.append(gate_object)

    def _append_circuit(self, new_circuit):
        '''
        Connect two circuits.

        Note: 
            When the append circuit is another object, it modifies self without affecting new_circuit.
            When the append circuit is self, it appends a copy of self.
        '''
        if id(new_circuit) == id(self):
            # check if self-appending
            new_circuit = deepcopy(new_circuit)

        # set to the maximum number
        if self.n_qubit is None or new_circuit.n_qubit is None:
            self.n_qubit = None
        else:
            self.n_qubit = max(self.n_qubit, new_circuit.n_qubit)
        
        for gate in new_circuit.gate_list:
            self.gate_list.append(gate)

    def append(self, object):
        '''
        Append an object (Gate/Circuit)
        '''
        if isinstance(object, BigGate):
            self._append_gate(object)
        elif isinstance(object, Circuit):
            self._append_circuit(object)
        elif isinstance(object, Gate):
            self._append_gate(object)
        else:
            raise NotImplementedError

    def rx(self, qubit, angle):
        self._append_gate(Rx(qubit, angle))
        return self

class BigGate(Circuit) : 
    def __init__(self, n_qubit = None, name = None):
        if not name:
            raise RuntimeError('You must name a BigGate')
        super().__init__(n_qubit, name)

        # Here, n_qubit only specifies the qubit range in definition
        # It does not affect the assigned_qubits

        # start from an abstract definition
        self.is_abstract = True
        self.assigned_qubits = []
    
    def __repr__(self):
        if self.is_abstract:
            ret = '---{:^25s}---\n'.format(f'BigGate {self.name} (Definition)')
            ret += self._to_string()
        else:
            ret = f'{self.name} q{self.assigned_qubits}'
        return ret
     
    def assign_by_map(self, qubit_map):
        ret = BigGate(n_qubit = None, name = self.name)

        for gate in self.gate_list:
            assigned_gate = gate.assign_by_map(qubit_map)
            ret._append_gate(assigned_gate)
        
        return ret   
    
    def involved_qubits(self) -> list:
        return self.assigned_qubits

    def assign(self, *args, **kwargs):
        ret = super().assign(*args, **kwargs)
        ret.n_qubit = self.n_qubit
        ret.is_abstract = False

        if len(args) > 0:
            # list mode
            qubit_map = self._parse_qubit_map_from_list(*args)
        else:
            # kwargs mode
            qubit_map = self._parse_qubit_map_from_kwargs(**kwargs)
        
        for i in range(ret.n_qubit):
            if i in qubit_map:
                ret.assigned_qubits.append(qubit_map[i])
            else:
                raise RuntimeWarning('The assign-map does not cover all qubits.')
                ret.append(None)
        
        return ret
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
        