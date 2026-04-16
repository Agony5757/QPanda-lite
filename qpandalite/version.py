"""QPanda-lite version information.

This module provides the package version, automatically managed by setuptools_scm.
"""

try:
    from importlib.metadata import version, PackageNotFoundError
    __version__ = version("qpandalite")
except PackageNotFoundError:
    # Package not installed (e.g., running from source without install)
    try:
        from qpandalite._version import __version__
    except ImportError:
        __version__ = "0.0.0+unknown"
