from qpandalite import OriginIR_BaseParser, OpenQASM2_BaseParser
from ._utils import IRConversionFailedException

def convert_oir_to_qasm(originir_str: str) -> str:
    """
    Convert OriginIR to OpenQASM2.
    """
    try:
        originir_parser = OriginIR_BaseParser()
        originir_parser.parse(originir_str)
        return originir_parser.to_qasm()
    except Exception as e:
        raise IRConversionFailedException(f"Failed to convert OriginIR to OpenQASM2: {e}")

def convert_qasm_to_oir(qasm_str: str) -> str:
    """
    Convert OpenQASM2 to OriginIR.
    """
    try:
        qasm_parser = OpenQASM2_BaseParser()
        qasm_parser.parse(qasm_str)
        return qasm_parser.to_originir()
    except Exception as e:
        raise IRConversionFailedException(f"Failed to convert OpenQASM2 to OriginIR: {e}")