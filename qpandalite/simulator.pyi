'''Interface for quantum circuit simulator written in C++
'''
from typing import Mapping, List
# from numpy.typing import ArrayLike

class Simulator:
    def __init__(self) -> None: 
        '''Create a simulator instance (implemented by C++).
        The simulator has two accessible variables: total_qubit and state.
        total_qubit is initialized with init_n_qubit method.
        state represents the quantum state, which can be modified by calling the gate method.
        '''
        ...

    def init_n_qubit(self, n : int) -> None:
        '''Initialize a |0...0> state of n qubits.

        Args:
            n (int): The number of qubits.
        '''
        ...

    def hadamard(self, qn : int) -> None:
        '''Hadamard gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...

    def u22(self, qn : int, unitary : List[complex]) -> None:
        '''Any 2*2 unitary.

        Args:
            qn (int): The gate qubit.
            unitary (List[complex]): A list with 4 complex elements, representing u00, u01, u10, u11 respectively.
        '''
        ...

    

    