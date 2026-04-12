
__all__ = ["CompilationFailedException", "IRConversionFailedException"]
class CompilationFailedException(RuntimeError):
    """Raised when quantum circuit compilation fails."""
    pass

class IRConversionFailedException(RuntimeError):
    """Raised when IR conversion between formats fails."""
    pass