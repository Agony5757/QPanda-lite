'''Interface for quantum circuit simulator written in C++

Note:
    You can find implementation at QPandaLiteCpp/src/simulator.cpp. The python interface is implemented by pybind11, which can be found at QPandaLiteCpp/Pybinder/QPandaLitePy.cpp.

'''
from typing import Mapping, List, Optional
from typing_extensions import override
# from numpy.typing import ArrayLike

class Simulator:
    def __init__(self) -> None: 
        '''Create a simulator instance (implemented by C++).
        The simulator has two accessible variables: ``total_qubit'' and ``state''.
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

    def x(self, target_qn: int, control_qn: Optional[int] = None) -> None: 
        '''X gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...
    
    def sx(self, qn : int) -> None:
        '''SX gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...
    
    def y(self, qn : int) -> None:
        '''Y gate.

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

    def cz(self, q1 : int, q2 : int) -> None:
        '''CNOT gate.

        Args:
            q1 (int): The first qubit.
            q2 (int): The second qubit.
        '''
        ...

    def iswap(self, q1 : int, q2 : int) -> None:
        '''iSWAP gate.

        Args:
            q1 (int): The first qubit.
            q2 (int): The second qubit.
        '''
        ...

    def xy(self, q1 : int, q2 : int) -> None:
        '''XX+YY gate.

        Args:
            q1 (int): The first qubit.
            q2 (int): The second qubit.
        '''
        ...

    def cnot(self, controller : int, target : int) -> None:
        '''CNOT gate.

        Args:
            controller (int): The controller qubit.
            target (int): The target qubit.
        '''
        ...    

    def rx(self, qn : int, angle : float) -> None:
        '''Rx gate.

        Args:
            qn (int): Qubit.
            angle (float): The rotation angle.
        '''
        ...

    def ry(self, qn : int, angle : float) -> None:
        '''Ry gate.

        Args:
            qn (int): Qubit.
            angle (float): The rotation angle.
        '''
        ...

    def rz(self, qn : int, angle : float) -> None:
        '''Rz gate.

        Args:
            qn (int): Qubit.
            angle (float): The rotation angle.
        '''
        ...

    def rphi90(self, qn : int, phi : float) -> None:
        '''Rphi90 gate (pi/2 pulse).

        Args:
            qn (int): Qubit.
            phi (float): The phase angle.
        '''
        ...

    def rphi180(self, qn : int, phi : float) -> None:
        '''Rphi180 gate (pi pulse).

        Args:
            qn (int): Qubit.
            phi (float): The phase angle.
        '''
        ...

    def rphi(self, qn : int, phi : float, theta: float) -> None:
        '''Rphi gate.

        Args:
            qn (int): Qubit.
            phi (float): The phase angle.
            theta (float): The rotation angle.
        '''
        ...

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

    @override
    def pmeasure(self, measure_qubit: int) -> List[float]:
        '''Measure one qubit and get the prob list.

        Args:
            measure_qubit (List[int]): Measure qubits

        Returns:
            List[Float]: Probability of 0 and 1
        '''
        ...

    @override
    def pmeasure(self, measure_qubit : List[int]) -> List[float]:
        '''Measure many qubits and get the prob list.

        Args:
            measure_qubit (List[int]): Measure qubits

        Returns:
            List[Float]: Probability of 000... to 111...
        '''
        ...
    