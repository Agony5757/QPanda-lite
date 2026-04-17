# Test suite for qpandalite

from .core.test_general import run_test_general
from .cloud.test_demos import run_test_demos
from .simulator.test_simulator import run_test_simulator
from .core.test_originir_parser import run_test_originir_parser
from .core.test_qasm_parser import run_test_qasm_parser
from .cloud.test_result_adapter import run_test_result_adapter
from .benchmark.test_QASMBench import run_test_qasm
from .simulator.test_random_QASM import (
    run_test_random_qasm_statevector,
    run_test_random_qasm_density_operator,
    run_test_random_qasm_density_operator_qutip,
    run_test_random_qasm_density_operator_compare_with_qutip)
from .simulator.test_random_OriginIR import run_test_random_originir_density_operator
from .simulator.test_random_QASM_measure import run_test_random_qasm_compare_shots
from ._utils import qpandalite_test

def run_test():
    run_test_general()
    run_test_demos()
    run_test_simulator()
    run_test_originir_parser()
    run_test_qasm_parser()
    run_test_result_adapter()
    run_test_qasm()
    run_test_random_qasm_statevector()
    run_test_random_qasm_density_operator()
    run_test_random_qasm_density_operator_qutip()
    run_test_random_qasm_density_operator_compare_with_qutip()
    run_test_random_originir_density_operator()
    run_test_random_qasm_compare_shots()

    print('All tests passed~!!!')
