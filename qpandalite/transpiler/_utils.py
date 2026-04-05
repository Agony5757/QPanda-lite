
__all__ = ["CompilationFailedException", "IRConversionFailedException"]
class CompilationFailedException(RuntimeError):
    pass

class IRConversionFailedException(RuntimeError):
    pass