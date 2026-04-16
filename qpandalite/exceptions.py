"""Custom exceptions for QPanda-lite.

This module defines all custom exceptions used throughout the QPanda-lite
package, providing clear error types for different failure scenarios.
"""

from __future__ import annotations

__all__ = [
    # Base exception
    "QPandaLiteError",
    # Authentication errors
    "AuthenticationError",
    # Credit/Quota errors
    "InsufficientCreditsError",
    "QuotaExceededError",
    # Network errors
    "NetworkError",
    # Task errors
    "TaskFailedError",
    "TaskTimeoutError",
    "TaskNotFoundError",
    # Backend errors
    "BackendError",
    "BackendNotAvailableError",
    "BackendNotFoundError",
    # Circuit errors
    "CircuitError",
    "CircuitTranslationError",
    "UnsupportedGateError",
]


class QPandaLiteError(Exception):
    """Base exception for all QPanda-lite errors."""
    
    def __init__(self, message: str, *, details: dict | None = None) -> None:
        """Initialize the error.
        
        Args:
            message: Human-readable error message.
            details: Optional dictionary with additional error details.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (details: {self.details})"
        return self.message


# -----------------------------------------------------------------------------
# Authentication Errors
# -----------------------------------------------------------------------------

class AuthenticationError(QPandaLiteError):
    """Raised when authentication fails (invalid token, expired credentials, etc.).
    
    This error indicates that the provided API token or credentials are invalid,
    expired, or do not have the required permissions.
    """
    pass


# -----------------------------------------------------------------------------
# Credit and Quota Errors
# -----------------------------------------------------------------------------

class InsufficientCreditsError(QPandaLiteError):
    """Raised when the account has insufficient credits to run a task.
    
    This error indicates that the user's account balance is too low to
    execute the requested quantum computation.
    """
    pass


class QuotaExceededError(QPandaLiteError):
    """Raised when the user has exceeded their usage quota.
    
    This error indicates that the user has reached their daily, monthly,
    or total usage limit for the quantum computing service.
    """
    pass


# -----------------------------------------------------------------------------
# Network Errors
# -----------------------------------------------------------------------------

class NetworkError(QPandaLiteError):
    """Raised when a network operation fails.
    
    This error covers connection failures, timeouts, DNS errors,
    and other network-related issues when communicating with
    quantum computing backends.
    """
    
    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
        status_code: int | None = None,
        details: dict | None = None,
    ) -> None:
        """Initialize the network error.
        
        Args:
            message: Human-readable error message.
            url: The URL that was being accessed when the error occurred.
            status_code: HTTP status code if applicable.
            details: Optional dictionary with additional error details.
        """
        super().__init__(message, details=details)
        self.url = url
        self.status_code = status_code


# -----------------------------------------------------------------------------
# Task Errors
# -----------------------------------------------------------------------------

class TaskFailedError(QPandaLiteError):
    """Raised when a quantum task fails on the backend.
    
    This error indicates that the task was submitted successfully but
    failed during execution on the quantum computer or simulator.
    """
    
    def __init__(
        self,
        message: str,
        *,
        task_id: str | None = None,
        backend: str | None = None,
        error_code: str | None = None,
        details: dict | None = None,
    ) -> None:
        """Initialize the task failed error.
        
        Args:
            message: Human-readable error message.
            task_id: The ID of the failed task.
            backend: The backend where the task failed.
            error_code: Backend-specific error code if available.
            details: Optional dictionary with additional error details.
        """
        super().__init__(message, details=details)
        self.task_id = task_id
        self.backend = backend
        self.error_code = error_code


class TaskTimeoutError(QPandaLiteError):
    """Raised when waiting for a task result exceeds the timeout.
    
    This error indicates that the task did not complete within the
    specified timeout period. The task may still be running.
    """
    
    def __init__(
        self,
        message: str,
        *,
        task_id: str | None = None,
        timeout: float | None = None,
        details: dict | None = None,
    ) -> None:
        """Initialize the timeout error.
        
        Args:
            message: Human-readable error message.
            task_id: The ID of the task that timed out.
            timeout: The timeout value in seconds.
            details: Optional dictionary with additional error details.
        """
        super().__init__(message, details=details)
        self.task_id = task_id
        self.timeout = timeout


class TaskNotFoundError(QPandaLiteError):
    """Raised when a task cannot be found.
    
    This error indicates that the specified task ID does not exist
    or the user does not have permission to access it.
    """
    
    def __init__(
        self,
        message: str,
        *,
        task_id: str | None = None,
        details: dict | None = None,
    ) -> None:
        """Initialize the task not found error.
        
        Args:
            message: Human-readable error message.
            task_id: The ID of the task that was not found.
            details: Optional dictionary with additional error details.
        """
        super().__init__(message, details=details)
        self.task_id = task_id


# -----------------------------------------------------------------------------
# Backend Errors
# -----------------------------------------------------------------------------

class BackendError(QPandaLiteError):
    """Raised when a backend operation fails.
    
    This is the base class for all backend-related errors.
    """
    pass


class BackendNotAvailableError(BackendError):
    """Raised when a backend is not available.
    
    This error indicates that the backend is offline, not configured,
    or cannot be accessed due to missing dependencies.
    """
    pass


class BackendNotFoundError(BackendError):
    """Raised when a requested backend is not found.
    
    This error indicates that the specified backend name is not
    registered in the backend registry.
    """
    pass


# -----------------------------------------------------------------------------
# Circuit Errors
# -----------------------------------------------------------------------------

class CircuitError(QPandaLiteError):
    """Raised when a circuit operation fails.
    
    This is the base class for all circuit-related errors.
    """
    pass


class CircuitTranslationError(CircuitError):
    """Raised when circuit translation fails.
    
    This error indicates that a circuit could not be converted
    from OriginIR to the target backend's native format.
    """
    
    def __init__(
        self,
        message: str,
        *,
        source_format: str | None = None,
        target_format: str | None = None,
        details: dict | None = None,
    ) -> None:
        """Initialize the translation error.
        
        Args:
            message: Human-readable error message.
            source_format: The source circuit format.
            target_format: The target circuit format.
            details: Optional dictionary with additional error details.
        """
        super().__init__(message, details=details)
        self.source_format = source_format
        self.target_format = target_format


class UnsupportedGateError(CircuitError):
    """Raised when a circuit contains an unsupported gate.
    
    This error indicates that the target backend does not support
    one or more gates present in the circuit.
    """
    
    def __init__(
        self,
        message: str,
        *,
        gate_name: str | None = None,
        backend: str | None = None,
        details: dict | None = None,
    ) -> None:
        """Initialize the unsupported gate error.
        
        Args:
            message: Human-readable error message.
            gate_name: The name of the unsupported gate.
            backend: The backend that does not support this gate.
            details: Optional dictionary with additional error details.
        """
        super().__init__(message, details=details)
        self.gate_name = gate_name
        self.backend = backend
