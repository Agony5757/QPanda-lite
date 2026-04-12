
__all__ = ["NotSupportedGateError", "RegisterNotFoundError", "RegisterOutOfRangeError", "RegisterDefinitionError"]
class NotSupportedGateError(Exception):
    """Raised when an unsupported gate is encountered in OpenQASM 2."""
    pass

class RegisterNotFoundError(Exception):
    """Raised when a quantum or classical register is not found."""
    pass

class RegisterOutOfRangeError(Exception):
    """Raised when a register index exceeds its defined size."""
    pass

class RegisterDefinitionError(Exception):
    """Raised when a register definition is invalid (e.g., duplicate name, empty)."""
    pass