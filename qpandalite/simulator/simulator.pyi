'''Interface for quantum circuit simulator written in C++
'''
from typing import Mapping, List
from typing_extensions import override
# from numpy.typing import ArrayLike

class Simulator:
    def __init__(self) -> None: 
        '''Create a simulator instance (implemented by C++).
        The simulator has two accessible variables: total_qubit and state.
        total_qubit is initialized with init_n_qubit method.
        state represents the quantum state, which can be modified by calling the gate method.
        '''
        ...

    @property
    def state(self) -> List[complex]:
        '''The quantum state

        Returns:
            List[complex]: The representation of the quantum state.
        '''
        ...

    @property
    def total_qubit(self) -> int:
        '''The number of qubit.

        Returns:
            int: The number of qubit of the simulator.
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

    def x(self, qn : int) -> None:
        '''X gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...

    def z(self, qn : int) -> None:
        '''Z gate.

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

    def cnot(self, controller : int, target : int) -> None:
        '''CNOT gate.

        Args:
            controller (int): The controller qubit.
            target (int): The target qubit.
        '''
        ...       

    def cz(self, q1 : int, q2 : int) -> None:
        '''CNOT gate.

        Args:
            q1 (int): The first qubit.
            q2 (int): The second qubit.
        '''
    
    @override
    def get_prob(self, measure_qubit : int, measure_state : int ) -> float:
        '''Measure

        Args:
            measure_qubit (int): The measured qubit.
            measure_state (int): The state of the measured qubit (either 0 or 1).

        Returns:
            float: The probability of the matching qubit & state.
        '''
        ...
    
    @override
    def get_prob(self, measure_qubits_and_states : Mapping[int,int] ) -> float:
        '''Measure

        Args:
            measure_qubits_and_states (Mapping[int,int]): A mapping for measured qubits and corresponding states (either 0 or 1).

        Returns:
            float: The probability of all qubits & states are matched.
        '''
        ...

    