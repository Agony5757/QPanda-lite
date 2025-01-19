from .test_general import run_test_general
from .test_demos import run_test_demos
from .test_simulator import run_test_simulator
from .test_originir_parser import run_test_originir_parser
from .test_result_adapter import run_test_result_adapter
from .test_QASMBench import run_test_qasm

def run_test():
    run_test_general()
    run_test_demos()
    run_test_simulator()
    run_test_originir_parser()
    run_test_result_adapter()
    run_test_qasm()