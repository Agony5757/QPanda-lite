import warnings
from typing import TYPE_CHECKING
try:
    # qpandalite_cpp extension is implemented by C++
    from qpandalite_cpp import *
    if TYPE_CHECKING:
        from .qpandalite_cpp import *
except ImportError as e:
    # Note: Without compiling the QPandaLiteCpp, you can also use qpandalite.
    # Only the C++ simulator is disabled.
    warnings.warn('qpandalite is not install with QPandaLiteCpp.')

from .originir_simulator import OriginIR_Simulator, OriginIR_NoisySimulator