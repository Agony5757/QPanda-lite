from qpandalite.qasm import OpenQASM2_BaseParser
import qpandalite.simulator as qsim
import numpy as np

from qpandalite.circuit_builder.random_qasm import random_qasm, available_qasm_gates
from qpandalite.simulator.originir_simulator import OriginIR_Simulator
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.circuit_builder import Circuit
from qpandalite.test._utils import qpandalite_test, NotMatchError

@qpandalite_test('Test QASM Parser')
def run_test_qasm_parser():
    # Generate random OriginIR circuit, and parse it
    n_qubits = 5
    n_gates = 50
    n_test = 50
    for i in range(n_test):
        qasm_1 = random_qasm(n_qubits, n_gates, measurements=True)
        parser = OpenQASM2_BaseParser()
        parser.parse(qasm_1)
        circuit_obj : Circuit = parser.to_circuit()
        oir_1 = circuit_obj.originir

        # simulate oir_1 and oir_2
        sim_oir = OriginIR_Simulator(backend_type='statevector')
        sim_qasm = QASM_Simulator(backend_type='statevector')
        
        state_1 = sim_oir.simulate_pmeasure(oir_1)
        state_2 = sim_qasm.simulate_pmeasure(qasm_1)

        # compare the results
        if not np.allclose(state_1, state_2):
            for i in range(len(state_1)):
                print(f'{i} (binary = {bin(i)}): {state_1[i]} vs {state_2[i]}')

            raise NotMatchError(
            '---------------\n'
            f'OriginIR =\n {oir_1}\n'
            f'QASM =\n {qasm_1}\n'
            '---------------\n'
            'Result not match!\n'
            f'Reference = {state_1}\n'
            f'My Result = {state_2}\n'
        )
        print(f'Test {i+1} passed.')


if __name__ == '__main__':
    run_test_qasm_parser()