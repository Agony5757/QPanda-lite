from qpandalite.originir.parser import OriginIR_Parser

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

    def simulate_gate(self, operation, qubit, cbit, parameter):
        if operation == 'RX':
            self.simulator.rx(self.qubit_mapping[int(qubit)], parameter)
        elif operation == 'RY':
            self.simulator.ry(self.qubit_mapping[int(qubit)], parameter)
        elif operation == 'RZ':
            self.simulator.rz(self.qubit_mapping[int(qubit)], parameter)
        elif operation == 'H':
            self.simulator.hadamard(self.qubit_mapping[int(qubit)])
        elif operation == 'X':
            self.simulator.x(self.qubit_mapping[int(qubit)])
        elif operation == 'SX':
            self.simulator.sx(self.qubit_mapping[int(qubit)])
        elif operation == 'Y':
            self.simulator.y(self.qubit_mapping[int(qubit)])
        elif operation == 'Z':
            self.simulator.z(self.qubit_mapping[int(qubit)])
        elif operation == 'CZ':
            self.simulator.cz(self.qubit_mapping[int(qubit[0])], 
                              self.qubit_mapping[int(qubit[1])])
        elif operation == 'ISWAP':
            self.simulator.iswap(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])])
        elif operation == 'XY':
            self.simulator.xy(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])])
        elif operation == 'CNOT':
            self.simulator.cnot(self.qubit_mapping[int(qubit[0])], 
                                self.qubit_mapping[int(qubit[1])])
        elif operation == 'Rphi':
            self.simulator.rphi(self.qubit_mapping[int(qubit)], 
                                parameter[0], parameter[1])  
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

    def simulate(self, originir):
        # extract the actual used qubit, and build qubit mapping
        # like q45 -> 0, q46 -> 1, etc..
        self._clear()
        self.extract_actual_used_qubits(originir)
        self.simulator.init_n_qubit(len(self.qubit_mapping))

        lines = originir.splitlines()
        for line in lines:            
            operation, qubit, cbit, parameter = OriginIR_Parser.parse_line(line.strip())
            self.simulate_gate(operation, qubit, cbit, parameter)
        
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