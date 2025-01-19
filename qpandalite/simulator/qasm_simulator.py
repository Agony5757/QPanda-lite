from typing import List, Tuple, TYPE_CHECKING
from qpandalite.qasm import OpenQASM2_BaseParser
import warnings
from .opcode_simulator import OpcodeSimulator

import numpy as np
if TYPE_CHECKING:
    from .QPandaLitePy import *

class QASM_Simulator:
    def __init__(self):
        pass