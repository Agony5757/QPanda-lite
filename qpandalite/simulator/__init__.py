try:
    from QPandaLitePy import *
except ImportError as e:
    raise ImportError('qpandalite is not install with QPandaLiteCpp.')
    # Note: Without compiling the QPandaLiteCpp, you can also use qpandalite.
    # Only the C++ simulator is disabled.