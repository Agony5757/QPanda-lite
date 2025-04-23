from qpandalite.originir.originir_base_parser import OriginIR_BaseParser
import qpandalite.simulator as qsim
import numpy as np

from qpandalite.circuit_builder.random_originir import random_originir
from qpandalite.simulator.originir_simulator import OriginIR_Simulator
from qpandalite.circuit_builder import Circuit
from qpandalite.test._utils import qpandalite_test, NotMatchError

@qpandalite_test('Test OriginIR Parser')
def run_test_originir_parser():
    # Generate random OriginIR circuit, and parse it
    n_qubits = 5
    n_gates = 50
    n_test = 50
    for i in range(n_test):
        oir_1 = random_originir(n_qubits, n_gates, allow_control=False, allow_dagger=False)
        parser = OriginIR_BaseParser()
        parser.parse(oir_1)
        circuit_obj : Circuit = parser.to_circuit()
        oir_2 = circuit_obj.originir

        # simulate oir_1 and oir_2
        sim = OriginIR_Simulator(backend_type='statevector')
        state_1 = sim.simulate_statevector(oir_1)
        state_2 = sim.simulate_statevector(oir_2)

        # compare the results
        if not np.allclose(state_1, state_2):
            raise NotMatchError(
            '---------------\n'
            f'OriginIR 1:\n{oir_1}\n'
            '---------------\n'
            f'OriginIR 2:\n{oir_2}\n'
            '---------------\n'
            'Result not match!\n'
            f'Reference = {state_1}\n'
            f'My Result = {state_2}\n'
        )
        print(f'Test {i+1} passed.')


if __name__ == '__main__':
    run_test_originir_parser()