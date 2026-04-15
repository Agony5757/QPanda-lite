"""QASM parser exceptions module.

This module defines custom exceptions for OpenQASM 2.0 parsing,
including errors for unsupported gates and register-related issues.

Key exports:
    NotSupportedGateError: Exception for unsupported quantum gates.
    RegisterNotFoundError: Exception for missing quantum/classical registers.
    RegisterOutOfRangeError: Exception for register index out of bounds.
    RegisterDefinitionError: Exception for invalid register definitions.
"""

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
