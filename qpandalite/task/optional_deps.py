"""Optional dependency management with clear error messages.

This module provides utilities for handling optional dependencies across
different quantum cloud platforms. When a dependency is not installed,
users receive clear instructions on how to install it.

Usage:
    # Check if dependency is available
    from qpandalite.task.optional_deps import QUAFU_AVAILABLE
    if QUAFU_AVAILABLE:
        from qpandalite.task.adapters.quafu_adapter import QuafuAdapter

    # Require dependency with error message
    from qpandalite.task.optional_deps import require
    quafu = require("quafu", "quafu")  # Raises MissingDependencyError if not installed
"""

from __future__ import annotations

__all__ = [
    "MissingDependencyError",
    "require",
    "check_quafu",
    "check_qiskit",
    "check_pyqpanda3",
    "check_simulation",
    "QUAFU_AVAILABLE",
    "QISKIT_AVAILABLE",
    "PYQPANDA3_AVAILABLE",
    "SIMULATION_AVAILABLE",
]


class MissingDependencyError(ImportError):
    """Raised when an optional dependency is not installed.

    Provides a clear error message indicating which package is missing
    and how to install it using pip extras.

    Attributes:
        package: The name of the missing package.
        extra: The pip extras name to install the package.
    """

    def __init__(self, package: str, extra: str) -> None:
        self.package = package
        self.extra = extra
        msg = (
            f"Package '{package}' is required for this feature. "
            f"Install it with: pip install qpandalite[{extra}]"
        )
        super().__init__(msg)


def require(name: str, extra: str):
    """Import an optional module with a clear error message if missing.

    Args:
        name: The module name to import (e.g., 'quafu', 'qiskit').
        extra: The pip extras name for installation (e.g., 'quafu', 'qiskit').

    Returns:
        The imported module.

    Raises:
        MissingDependencyError: If the module cannot be imported.

    Example:
        >>> quafu = require("quafu", "quafu")
        >>> # If quafu is not installed:
        >>> # MissingDependencyError: Package 'quafu' is required...
    """
    try:
        return __import__(name)
    except ImportError as e:
        raise MissingDependencyError(name, extra) from e


def check_quafu() -> bool:
    """Check if the quafu package is available.

    Returns:
        True if quafu can be imported, False otherwise.
    """
    try:
        import quafu  # noqa: F401
        return True
    except ImportError:
        return False


def check_qiskit() -> bool:
    """Check if the qiskit and qiskit_ibm_provider packages are available.

    Returns:
        True if both packages can be imported, False otherwise.
    """
    try:
        import qiskit  # noqa: F401
        import qiskit_ibm_provider  # noqa: F401
        return True
    except ImportError:
        return False


def check_pyqpanda3() -> bool:
    """Check if the pyqpanda3 package is available.

    Returns:
        True if pyqpanda3 can be imported, False otherwise.
    """
    try:
        import pyqpanda3  # noqa: F401
        return True
    except ImportError:
        return False


def check_simulation() -> bool:
    """Check if simulation dependencies (qutip) are available.

    Returns:
        True if qutip can be imported, False otherwise.
    """
    try:
        import qutip  # noqa: F401
        return True
    except ImportError:
        return False


# Pre-computed availability flags (evaluated at module load time)
QUAFU_AVAILABLE = check_quafu()
QISKIT_AVAILABLE = check_qiskit()
PYQPANDA3_AVAILABLE = check_pyqpanda3()
SIMULATION_AVAILABLE = check_simulation()