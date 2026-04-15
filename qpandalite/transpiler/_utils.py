
"""Compilation exception classes for the transpiler module.

This module defines custom exceptions for quantum circuit compilation
and IR conversion failures.
"""

__all__ = ["CompilationFailedException", "IRConversionFailedException"]
class CompilationFailedException(RuntimeError):
    """Raised when quantum circuit compilation fails."""
    pass

class IRConversionFailedException(RuntimeError):
    """Raised when IR conversion between formats fails."""
    pass