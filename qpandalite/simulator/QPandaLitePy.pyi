'''Interface for quantum circuit simulator written in C++

Note:
    You can find implementation at QPandaLiteCpp/src/simulator.cpp. The python interface is implemented by pybind11, which can be found at QPandaLiteCpp/Pybinder/QPandaLitePy.cpp.

'''
from typing import Dict, Mapping, List, Optional, Tuple
from typing_extensions import override

# from numpy.typing import ArrayLike

def seed(seed_: int) -> None: ...
def rand() -> float: ...

def seed(seed_: int) -> None: ...
def rand() -> float: ...

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

    def hadamard(self, qn : int, control : List[int], is_dagger : bool = False) -> None:
        '''Hadamard gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...

    def x(self, qn: int, control : List[int], is_dagger : bool = False) -> None: 
        '''X gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...
    
    def sx(self, qn : int, control : List[int], is_dagger : bool = False) -> None:
        '''SX gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...
    
    def y(self, qn : int, control : List[int], is_dagger : bool = False) -> None:
        '''Y gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...

    def z(self, qn : int, control : List[int], is_dagger : bool = False) -> None:
        '''Z gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...

    def u22(self, qn : int, control : List[int], unitary : List[complex]) -> None:
        '''Any 2*2 unitary.

        Args:
            qn (int): The gate qubit.
            unitary (List[complex]): A list with 4 complex elements, representing u00, u01, u10, u11 respectively.
        '''
        ...   

    def cz(self, q1 : int, q2 : int, control : List[int], is_dagger : bool = False) -> None:
        '''CZ gate.

        Args:
            q1 (int): The first qubit.
            q2 (int): The second qubit.
        '''
        ...

    def iswap(self, q1 : int, q2 : int, control : List[int], is_dagger : bool = False) -> None:
        '''iSWAP gate.

        Args:
            q1 (int): The first qubit.
            q2 (int): The second qubit.
        '''
        ...

    def xy(self, q1 : int, q2 : int, theta: float, control : List[int], is_dagger : bool = False) -> None:
        '''XX+YY gate.

        Args:
            q1 (int): The first qubit.
            q2 (int): The second qubit.
        '''
        ...

    def cnot(self, controller : int, target : int, control : List[int], is_dagger : bool = False) -> None:
        '''CNOT gate.

        Args:
            controller (int): The controller qubit.
            target (int): The target qubit.
        '''
        ...    

    def rx(self, qn : int, angle : float, control : List[int], is_dagger : bool = False) -> None:
        '''Rx gate.

        Args:
            qn (int): Qubit.
            angle (float): The rotation angle.
        '''
        ...

    def ry(self, qn : int, angle : float, control : List[int], is_dagger : bool = False) -> None:
        '''Ry gate.

        Args:
            qn (int): Qubit.
            angle (float): The rotation angle.
        '''
        ...

    def rz(self, qn : int, angle : float, control : List[int], is_dagger : bool = False) -> None:
        '''Rz gate.

        Args:
            qn (int): Qubit.
            angle (float): The rotation angle.
        '''
        ...

    def rphi90(self, qn : int, phi : float, control : List[int], is_dagger : bool = False) -> None:
        '''Rphi90 gate (pi/2 pulse).

        Args:
            qn (int): Qubit.
            phi (float): The phase angle.
        '''
        ...

    def rphi180(self, qn : int, phi : float, control : List[int], is_dagger : bool = False) -> None:
        '''Rphi180 gate (pi pulse).

        Args:
            qn (int): Qubit.
            phi (float): The phase angle.
        '''
        ...

    def rphi(self, qn : int, phi : float, theta: float, control : List[int], is_dagger : bool = False) -> None:
        '''Rphi gate.

        Args:
            qn (int): Qubit.
            phi (float): The phase angle.
            theta (float): The rotation angle.
        '''
        ...

    @override
    def get_prob(self, measure_qubit : int, measure_state : int) -> float:
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
    
class NoiseType:
    Depolarizing: int
    Damping: int
    BitFlip: int
    PhaseFlip: int
    TwoQubitDepolarizing : int

class SupportOperationType:
    HADAMARD : int
    IDENTITY : int
    U22 : int
    X : int
    Y : int
    Z : int
    SX : int
    CZ : int
    ISWAP : int
    XY : int
    CNOT : int
    RX : int
    RY : int
    RZ : int
    RPHI90 : int
    RPHI180 : int
    RPHI : int
    TOFFOLI : int
    CSWAP : int

class NoisySimulator:    
    noise: Dict[str, float]
    measurement_error_matrices: List[Tuple[float, float]]

    def __init__(self,
                n_qubit: int, 
                noise_description: Optional[Dict[str, float]] = None, 
                measurement_error: Optional[List[Tuple[float, float]]] = None):
        """
        Create a simulator instance (implemented by C++).
        The simulator has three accessible variables: `total_qubit`, `noise`, and `gate_dependent_noise`.
        `total_qubit` is the number of qubits for the simulation.
        `noise` is a dictionary mapping global noise types to their probabilities.
        `gate_dependent_noise` is a dictionary mapping gate names to dictionaries of noise types and probabilities.
        `measurement_error_matrices` represents the measurement error for the simulator.
        
        :param n_qubit: The number of qubits for the simulation.
        :param noise_description: A dictionary mapping global noise types to their probabilities.
        :param gate_noise_description: A dictionary mapping gate names to dictionaries of noise types and probabilities.
        :param measurement_error: A list of tuples representing measurement error matrices.
        """
        # self.simulator_instance = qpandalite.NoisySimulator(
        #     n_qubit, noise_description, gate_noise_description, measurement_error
        # )
        ...

    @property
    def total_qubit(self) -> int:
        '''The number of qubit.

        Returns:
            int: The number of qubit of the simulator.
        '''
        ...
    
    def load_opcode(self, opstr: str,                # Operation name as a string
                    qubits: List[int],              # List of qubits
                    parameters: List[float],         # List of parameters
                    dagger: bool,                   # Dagger flag
                    global_controller: List[int]) -> None:  # List of control qubits

        """
        Loads an opcode into the simulator.       
        """
        ...

    def insert_error(self, qubits: List[int]) -> None: 
        '''insert_error based on the noise_description

        Args:
            qubits List[int]: The list of gate qubit.
        '''
        ...

    def hadamard(self, qn : int, control : List[int], is_dagger : bool = False) -> None:
        '''Hadamard gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...

    def x(self, qn: int, control : List[int], is_dagger : bool = False) -> None: 
        '''X gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...
    
    def sx(self, qn : int, control : List[int], is_dagger : bool = False) -> None:
        '''SX gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...
    
    def y(self, qn : int, control : List[int], is_dagger : bool = False) -> None:
        '''Y gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...

    def z(self, qn : int, control : List[int], is_dagger : bool = False) -> None:
        '''Z gate.

        Args:
            qn (int): The gate qubit.
        '''
        ...
    
    def cz(self, qn1 : int, qn2 : int, control : List[int], is_dagger : bool = False) -> None:
        '''CZ gate.

        Args:
            qn1 (int): The gate qubit.
            qn2 (int): The gate qubit.
        '''
        ...

    def iswap(self, q1 : int, q2 : int, control : List[int], is_dagger : bool = False) -> None:
        '''iSWAP gate.

        Args:
            q1 (int): The first qubit.
            q2 (int): The second qubit.
        '''
        ...

    
    def xy(self, q1 : int, q2 : int, theta: float, control : List[int], is_dagger : bool = False) -> None:
        '''XX+YY gate.

        Args:
            q1 (int): The first qubit.
            q2 (int): The second qubit.
        '''
        ...
    
    def cnot(self, controller : int, target : int, control : List[int], is_dagger : bool = False) -> None:
        '''CNOT gate.

        Args:
            controller (int): The controller qubit.
            target (int): The target qubit.
        '''
        ...  
    
    def swap(self, q1 : int, q2 : int, control : List[int], is_dagger : bool = False) -> None:
        '''CNOT gate.

        Args:
            controller (int): The controller qubit.
            target (int): The target qubit.
        '''
        ...  

    def rx(self, qn : int, angle : float, control : List[int], is_dagger : bool = False) -> None:
        '''Rx gate.

        Args:
            qn (int): Qubit.
            angle (float): The rotation angle.
        '''
        ...

    def ry(self, qn : int, angle : float, control : List[int], is_dagger : bool = False) -> None:
        '''Ry gate.

        Args:
            qn (int): Qubit.
            angle (float): The rotation angle.
        '''
        ...

    def rz(self, qn : int, angle : float, control : List[int], is_dagger : bool = False) -> None:
        '''Rz gate.

        Args:
            qn (int): Qubit.
            angle (float): The rotation angle.
        '''
        ...
    
    def rphi90(self, qn : int, phi : float, control : List[int], is_dagger : bool = False) -> None:
        '''Rphi90 gate (pi/2 pulse).

        Args:
            qn (int): Qubit.
            phi (float): The phase angle.
        '''
        ...

    def rphi180(self, qn : int, phi : float, control : List[int], is_dagger : bool = False) -> None:
        '''Rphi180 gate (pi pulse).

        Args:
            qn (int): Qubit.
            phi (float): The phase angle.
        '''
        ...

    def rphi(self, qn : int, phi : float, theta: float, control : List[int], is_dagger : bool = False) -> None:
        '''Rphi gate.

        Args:
            qn (int): Qubit.
            phi (float): The phase angle.
            theta (float): The rotation angle.
        '''
        ...
    
    def toffoli(self, qn1 : int, qn2 : int, target : int, control : List[int], is_dagger : bool = False) -> None:
        '''Toffoli gate.

        Args:
            qn1 (int): The controller qubit1.
            qn2 (int): The controller qubit2.
            target (int): The target qubit.
        '''
        ... 
    
    def cswap(self, controller : int, target1 : int, target2 : int, control : List[int], is_dagger : bool = False) -> None:
        '''CSWAP gate.

        Args:
            controller (int): The controller qubit.
            target1 (int): The target qubit1.
            target2 (int): The target qubit2.
        '''
        ... 

    def cnot(self, controller : int, target : int, control : List[int], control : List[int], is_dagger : bool = False) -> None:
        '''CNOT gate.

        Args:
            controller (int): The controller qubit.
            target (int): The target qubit.
        '''
        ... 


    def measure_shots(self, measure_qubits: List[int], shots: int) -> Dict[int, int]:
        """
        Simulate a quantum measurement multiple times and tally the results.
        
        Args:
            measure_qubits (List[int]): The list of measured qubits.
            shots (int): The number of times the quantum measurement is simulated.
        
        Returns:
            Dict[int, int]: A dictionary where keys represent unique measurement results 
            (as integers) and values represent the frequency of each result.
        """
        ...        

    def measure_shots(self, shots: int) -> Dict[int, int]:
        """
        Simulate a quantum measurement multiple times and tally the results.
        The measure qubits are set empty, so all qubits are measured.
        
        Args:
            shots (int): The number of times the quantum measurement is simulated.
        
        Returns:
            Dict[int, int]: A dictionary where keys represent unique measurement results 
            (as integers) and values represent the frequency of each result.
        """
        ...
        
class NoisySimulator_GateDependent(NoisySimulator):
    
    gate_dependent_noise: Dict[str, Dict[str, float]]
    
    def __init__(self,
        n_qubit: int, 
        noise_description: Optional[Dict[str, float]] = None, 
        gate_noise_description: Optional[Dict[str, Dict[str, float]]] = None, 
        measurement_error: Optional[List[Tuple[float, float]]] = None):
        ...

GateError1q_t = Dict[Tuple[SupportOperationType, int], Dict[NoiseType, float]]
GateError2q_t = Dict[Tuple[SupportOperationType, int], Dict[NoiseType, float]]
class NoisySimulator_GateErrorSpecific(NoisySimulator):
    
    gate_error1q: Dict[str, Dict[str, float]]
    
    def __init__(self,
        n_qubit: int, 
        noise_description: Optional[Dict[str, float]] = None, 
        gate_noise_description: Optional[Dict[str, Dict[str, float]]] = None, 
        measurement_error: Optional[List[Tuple[float, float]]] = None):
        ...