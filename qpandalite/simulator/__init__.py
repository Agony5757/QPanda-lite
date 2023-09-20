import warnings
from simulator import Simulator

try:
    from QPandaLitePy import *
except ImportError as e:
    warnings.warn('qpandalite is not install with QPandaLiteCpp.')
    # Note: Without compiling the QPandaLiteCpp, you can also use qpandalite.
    # Only the C++ simulator is disabled.
