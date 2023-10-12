from typing import List, Tuple
from qpandalite.originir.originir_line_parser import OriginIR_Parser

try:
    from qpandalite.simulator import Simulator
except ImportError as e:
    # warning has been emitted in __init__.py
    pass


class OriginIR_Simulator:    
    def __init__(self, reverse_key = False):
        self.qubit_num = 0
        self.simulator = Simulator()
        self.measure_qubit = []
        self.qubit_mapping = dict()
        self.reverse_key = reverse_key

    def _clear(self):
        self.qubit_num = 0
        self.simulator = Simulator()
        self.measure_qubit = []
        self.qubit_mapping = dict()

    def simulate_gate(self, operation, qubit, cbit, parameter,is_dagger):
        if operation == 'RX':
            self.simulator.rx(self.qubit_mapping[int(qubit)], parameter,is_dagger)
        elif operation == 'RY':
            self.simulator.ry(self.qubit_mapping[int(qubit)], parameter,is_dagger)
        elif operation == 'RZ':
            self.simulator.rz(self.qubit_mapping[int(qubit)], parameter,is_dagger)
        elif operation == 'H':
            self.simulator.hadamard(self.qubit_mapping[int(qubit)],is_dagger)
        elif operation == 'X':
            self.simulator.x(self.qubit_mapping[int(qubit)],is_dagger)
        elif operation == 'SX':
            self.simulator.sx(self.qubit_mapping[int(qubit)],is_dagger)
        elif operation == 'Y':
            self.simulator.y(self.qubit_mapping[int(qubit)],is_dagger)
        elif operation == 'Z':
            self.simulator.z(self.qubit_mapping[int(qubit)],is_dagger)
        elif operation == 'CZ':
            self.simulator.cz(self.qubit_mapping[int(qubit[0])], 
                              self.qubit_mapping[int(qubit[1])],is_dagger)
        elif operation == 'ISWAP':
            self.simulator.iswap(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])],is_dagger)
        elif operation == 'XY':
            self.simulator.xy(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])],is_dagger)
        elif operation == 'CNOT':
            self.simulator.cnot(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])],is_dagger)
        elif operation == 'RPhi':
            self.simulator.rphi(self.qubit_mapping[int(qubit)], 
                                parameter[0], parameter[1],is_dagger)  
        elif operation == 'MEASURE':
            # In fact, I don't know the real implementation
            # This is a guessed implementation.
            self.measure_qubit.append((self.qubit_mapping[int(qubit)], int(cbit)))
        elif operation == None:
            pass
        elif operation == 'QINIT':
            pass
        elif operation == 'CREG':
            pass
        elif operation == 'BARRIER':
            pass
        else:
            raise RuntimeError('Unknown OriginIR operation. '
                               f'Operation: {operation}.')

    def _add_used_qubit(self, qubit):
        if qubit in self.qubit_mapping:
            return
        
        n = len(self.qubit_mapping)
        self.qubit_mapping[qubit] = n

    def extract_actual_used_qubits(self, originir):
        lines = originir.splitlines()
        for line in lines:
            operation, qubit, cbit, parameter = OriginIR_Parser.parse_line(line.strip())
            
            if not operation: continue
            if operation == 'QINIT': continue
            if not qubit: continue
            
            if isinstance(qubit, list):
                for q in qubit:
                    self._add_used_qubit(int(q))
            else:
                self._add_used_qubit(int(qubit))

    def check_topology(self, available_qubits : List[int] = None):
        
        used_qubits = list(self.qubit_mapping.keys())
        
        # check qubits
        for used_qubit in used_qubits:
            if used_qubit not in available_qubits:                
                raise ValueError('A invalid qubit is used. '
                                 f'Available qubits: {available_qubits}\n'
                                 f'Used: {used_qubit}.')

    def simulate(self, 
                 originir, 
                 available_qubits : List[int] = None, 
                 available_topology : List[List[int]] = None):
        '''Simulate originir.
        Free mode: let available_qubits = None, then simulate any topology.
        Strict mode: input available_qubits and available_topology, then the originir is automatically checked.

        Args:
            originir (str): OriginIR.
            available_qubits (List[int], optional): Available qubits (if need checking). Defaults to None.
            available_topology (list[Tuple[int, int]], optional): Available topology (if need checking). Defaults to None.

        Returns:
            _type_: _description_
        '''
        # extract the actual used qubit, and build qubit mapping
        # like q45 -> 0, q46 -> 1, etc..
        self._clear()
        self.extract_actual_used_qubits(originir)

        if available_qubits is not None:
            self.check_topology(available_qubits)

        self.simulator.init_n_qubit(len(self.qubit_mapping))

        lines = originir.splitlines()
        dagger_flag = False
        for i, line in enumerate(lines):
            if line.strip() == 'DAGGER':
                dagger_flag = True
                end_line = ''
                cnt = i+1
                while end_line != 'ENDDAGGER':
                    end_line = lines[cnt]
                    cnt += 1
                lines[i+1:cnt-1] = lines[i+1:cnt-1][::-1]
                continue
            elif line.strip() == 'ENDDAGGER':
                dagger_flag = False
                continue
            operation, qubit, cbit, parameter = OriginIR_Parser.parse_line(line.strip())
            if isinstance(qubit, list) and (available_topology is not None):
                if len(qubit) > 2: raise ValueError('Real chip does not support 3-qubit gate or more. '
                                                    'The dummy server does not support either. '
                                                    'You should consider decomposite it.')
                if ([int(qubit[0]), int(qubit[1])] not in available_topology) and \
                   ([int(qubit[1]), int(qubit[0])] not in available_topology):
                    raise ValueError(f'Unsupported topology in line {i} ({line}).')

            self.simulate_gate(operation, qubit, cbit, parameter,is_dagger=dagger_flag)
        
        self.qubit_num = len(self.qubit_mapping)
        measure_qubit_cbit = sorted(self.measure_qubit, key = lambda k : k[1], reverse=self.reverse_key)
        measure_qubit = []
        for qubit in measure_qubit_cbit:
            measure_qubit.append(qubit[0])
        prob_list = self.simulator.pmeasure(measure_qubit)
        return prob_list
    
    @property
    def state(self):
        return self.simulator.state