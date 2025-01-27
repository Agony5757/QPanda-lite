from .originir_simulator import OriginIR_Simulator
from .qasm_simulator import QASM_Simulator
from .base_simulator import BaseSimulator

def get_backend(program_type: str = "originir", backend_type: str = "statevector", **kwargs) -> BaseSimulator:
    if program_type == "originir":
        # resolve kwargs
        reverse_key = kwargs.get("reverse_key", False)
        return OriginIR_Simulator(reverse_key=reverse_key, backend_type=backend_type)

    elif program_type == "qasm":
        return QASM_Simulator(backend_type=backend_type)

    else:
        raise ValueError("Unsupported backend type: {}".format(program_type))