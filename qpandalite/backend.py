"""Unified backend management for quantum computing platforms.

This module provides a centralized Backend management system with:
- Abstract base class QuantumBackend defining a unified interface
- Factory pattern for backend instance creation/retrieval
- Caching mechanism for backend instances
- Integration with existing adapters (OriginQ, Quafu, IBM)

Usage:
    # Get or create a backend instance
    backend = get_backend('originq')
    
    # List all available backends
    available = list_backends()
    
    # Submit a circuit
    task_id = backend.submit(circuit, shots=1000)
    
    # Query task status
    result = backend.query(task_id)
"""

from __future__ import annotations

__all__ = [
    "QuantumBackend",
    "OriginQBackend",
    "QuafuBackend",
    "IBMBackend",
    "get_backend",
    "list_backends",
    "BACKENDS",
]

import abc
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Type

if TYPE_CHECKING:
    from qpandalite.circuit_builder.qcircuit import Circuit

from qpandalite.task.adapters import (
    OriginQAdapter,
    QuafuAdapter,
    QiskitAdapter,
    QuantumAdapter,
    TASK_STATUS_FAILED,
    TASK_STATUS_RUNNING,
    TASK_STATUS_SUCCESS,
)

# -----------------------------------------------------------------------------
# Cache Configuration
# -----------------------------------------------------------------------------

DEFAULT_CACHE_DIR = Path.home() / ".qpandalite" / "cache"
CACHE_FILE_SUFFIX = "_backend.json"


def _get_cache_file_path(platform: str, cache_dir: Path | None = None) -> Path:
    """Get the cache file path for a specific platform.
    
    Args:
        platform: The backend platform identifier.
        cache_dir: Optional custom cache directory. Uses default if None.
        
    Returns:
        Path to the cache file.
    """
    cache_path = cache_dir or DEFAULT_CACHE_DIR
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path / f"{platform}{CACHE_FILE_SUFFIX}"


# -----------------------------------------------------------------------------
# Abstract Base Backend
# -----------------------------------------------------------------------------

class QuantumBackend(abc.ABC):
    """Abstract base class for quantum backend management.
    
    This class provides a unified interface for all quantum computing backends,
    wrapping the underlying adapters and providing caching capabilities.
    
    Attributes:
        name: The name of this backend instance.
        platform: The platform identifier (e.g., 'originq', 'quafu', 'ibm').
        adapter: The underlying quantum adapter instance.
        config: Backend-specific configuration dictionary.
    """
    
    # Class-level registry of backend instances
    _instances: ClassVar[dict[str, "QuantumBackend"]] = {}
    
    # Platform identifier (must be set by subclasses)
    platform: ClassVar[str] = ""
    
    # Adapter class (must be set by subclasses)
    _adapter_class: ClassVar[Type[QuantumAdapter]] = QuantumAdapter
    
    def __init__(
        self,
        name: str | None = None,
        config: dict[str, Any] | None = None,
        cache_dir: Path | str | None = None,
    ) -> None:
        """Initialize the backend.
        
        Args:
            name: Optional name for this backend instance. Uses platform name if None.
            config: Optional configuration dictionary.
            cache_dir: Optional custom cache directory path.
        """
        self.name = name or self.platform
        self.config = config or {}
        self._cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self._adapter: QuantumAdapter | None = None
        
    @property
    def adapter(self) -> QuantumAdapter:
        """Get or create the underlying adapter instance.
        
        Returns:
            The quantum adapter for this backend.
            
        Raises:
            RuntimeError: If the adapter cannot be initialized.
        """
        if self._adapter is None:
            self._adapter = self._create_adapter()
        return self._adapter
    
    @abc.abstractmethod
    def _create_adapter(self) -> QuantumAdapter:
        """Create and return the platform-specific adapter.
        
        Returns:
            A new adapter instance for this backend.
        """
        ...
    
    # -------------------------------------------------------------------------
    # Circuit Adapter
    # -------------------------------------------------------------------------
    
    def get_circuit_adapter(self) -> QuantumAdapter:
        """Get the circuit adapter for translating circuits.
        
        Returns:
            The quantum adapter that handles circuit translation.
        """
        return self.adapter
    
    def translate_circuit(self, originir: str) -> Any:
        """Translate an OriginIR circuit to the platform's native format.
        
        Args:
            originir: Circuit in OriginIR format.
            
        Returns:
            Provider-specific circuit object.
        """
        return self.adapter.translate_circuit(originir)
    
    # -------------------------------------------------------------------------
    # Task Submission
    # -------------------------------------------------------------------------
    
    def submit(self, circuit: Any, *, shots: int = 1000, **kwargs: Any) -> str:
        """Submit a circuit to the backend.
        
        Args:
            circuit: Provider-native circuit object or OriginIR string.
            shots: Number of measurement shots.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            Task ID assigned by the backend.
        """
        return self.adapter.submit(circuit, shots=shots, **kwargs)
    
    def submit_batch(
        self, circuits: list[Any], *, shots: int = 1000, **kwargs: Any
    ) -> str | list[str]:
        """Submit multiple circuits as a batch.
        
        Args:
            circuits: List of provider-native circuit objects or OriginIR strings.
            shots: Number of measurement shots.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            Task ID(s) assigned by the backend.
        """
        return self.adapter.submit_batch(circuits, shots=shots, **kwargs)
    
    # -------------------------------------------------------------------------
    # Task Query
    # -------------------------------------------------------------------------
    
    def query(self, task_id: str) -> dict[str, Any]:
        """Query a task's status and result.
        
        Args:
            task_id: Task identifier.
            
        Returns:
            Dict with keys:
                - 'status': 'success' | 'failed' | 'running'
                - 'result': Execution result (when status is 'success' or 'failed')
        """
        return self.adapter.query(task_id)
    
    def query_batch(self, task_ids: list[str]) -> dict[str, Any]:
        """Query multiple tasks' status and merge results.
        
        Args:
            task_ids: List of task identifiers.
            
        Returns:
            Dict with keys: 'status', 'result' (list of results).
        """
        return self.adapter.query_batch(task_ids)
    
    # -------------------------------------------------------------------------
    # Availability
    # -------------------------------------------------------------------------
    
    def is_available(self) -> bool:
        """Check if this backend is available.
        
        Returns:
            True if the backend is properly configured and ready to use.
        """
        try:
            return self.adapter.is_available()
        except Exception:
            return False
    
    # -------------------------------------------------------------------------
    # Cache Management
    # -------------------------------------------------------------------------
    
    def save_to_cache(self) -> None:
        """Save this backend instance configuration to cache."""
        cache_file = _get_cache_file_path(self.platform, self._cache_dir)
        cache_data = {
            "name": self.name,
            "platform": self.platform,
            "config": self.config,
        }
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            # Cache saving is non-critical, log but don't fail
            import warnings
            warnings.warn(f"Failed to save backend cache: {e}")
    
    @classmethod
    def load_from_cache(
        cls,
        cache_dir: Path | str | None = None,
    ) -> "QuantumBackend" | None:
        """Load a backend instance from cache.
        
        Args:
            cache_dir: Optional custom cache directory path.
            
        Returns:
            Loaded backend instance or None if cache doesn't exist or is invalid.
        """
        cache_path = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        cache_file = _get_cache_file_path(cls.platform, cache_path)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            
            # Verify platform matches
            if cache_data.get("platform") != cls.platform:
                return None
            
            instance = cls(
                name=cache_data.get("name"),
                config=cache_data.get("config", {}),
                cache_dir=cache_path,
            )
            return instance
        except (IOError, OSError, json.JSONDecodeError, KeyError):
            return None
    
    def clear_cache(self) -> None:
        """Clear the cache for this backend instance."""
        cache_file = _get_cache_file_path(self.platform, self._cache_dir)
        if cache_file.exists():
            try:
                cache_file.unlink()
            except (IOError, OSError):
                pass
    
    # -------------------------------------------------------------------------
    # Class Methods for Instance Management
    # -------------------------------------------------------------------------
    
    @classmethod
    def get_instance(
        cls,
        name: str | None = None,
        config: dict[str, Any] | None = None,
        use_cache: bool = True,
        cache_dir: Path | str | None = None,
    ) -> "QuantumBackend":
        """Get or create a backend instance (factory method).
        
        Args:
            name: Optional name for the instance.
            config: Optional configuration dictionary.
            use_cache: Whether to use/load cache. Defaults to True.
            cache_dir: Optional custom cache directory.
            
        Returns:
            A backend instance.
        """
        cache_key = f"{cls.platform}:{name or 'default'}"
        
        # Check in-memory cache first
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        
        # Try loading from disk cache if enabled
        if use_cache and config is None:
            cached = cls.load_from_cache(cache_dir)
            if cached is not None:
                cls._instances[cache_key] = cached
                return cached
        
        # Create new instance
        instance = cls(name=name, config=config, cache_dir=cache_dir)
        
        # Save to cache if enabled
        if use_cache:
            instance.save_to_cache()
        
        cls._instances[cache_key] = instance
        return instance
    
    @classmethod
    def list_available(cls) -> bool:
        """Check if this backend type is available.
        
        Returns:
            True if the backend can be instantiated and is configured.
        """
        try:
            instance = cls.get_instance(use_cache=False)
            return instance.is_available()
        except Exception:
            return False


# -----------------------------------------------------------------------------
# Concrete Backend Implementations
# -----------------------------------------------------------------------------

class OriginQBackend(QuantumBackend):
    """Backend for OriginQ Cloud (本源量子云).
    
    This backend connects to the OriginQ Cloud service for executing
    quantum circuits on OriginQ quantum computers and simulators.
    """
    
    platform = "originq"
    _adapter_class = OriginQAdapter
    
    def _create_adapter(self) -> OriginQAdapter:
        """Create an OriginQ adapter.
        
        Returns:
            A configured OriginQAdapter instance.
        """
        return OriginQAdapter()


class QuafuBackend(QuantumBackend):
    """Backend for BAQIS Quafu (ScQ) quantum cloud platform.
    
    This backend connects to the Quafu service for executing quantum
    circuits on superconducting quantum computers.
    """
    
    platform = "quafu"
    _adapter_class = QuafuAdapter
    
    # Valid chip IDs for Quafu
    VALID_CHIP_IDS = frozenset(
        {"ScQ-P10", "ScQ-P18", "ScQ-P136", "ScQ-P10C", "Dongling"}
    )
    
    def _create_adapter(self) -> QuafuAdapter:
        """Create a Quafu adapter.
        
        Returns:
            A configured QuafuAdapter instance.
        """
        return QuafuAdapter()
    
    def validate_chip_id(self, chip_id: str) -> bool:
        """Validate if the chip ID is valid for Quafu.
        
        Args:
            chip_id: The chip identifier to validate.
            
        Returns:
            True if the chip ID is valid.
        """
        return chip_id in self.VALID_CHIP_IDS


class IBMBackend(QuantumBackend):
    """Backend for IBM Quantum via Qiskit.

    This backend connects to IBM Quantum services for executing quantum
    circuits on IBM quantum computers and simulators.

    Proxy Configuration:
        Proxies can be configured in multiple ways (in priority order):
        1. Explicit config dict passed to constructor
        2. Environment variables (HTTP_PROXY, HTTPS_PROXY)
        3. qpandalite.yml configuration file

    Example:
        >>> # Using config file
        >>> backend = get_backend('ibm')
        >>> # Check proxy availability
        >>> backend.check_proxy()
        True
        >>> # Test IBM connectivity
        >>> result = backend.test_connectivity()
        >>> print(result['success'])
        True
    """

    platform = "ibm"
    _adapter_class = QiskitAdapter

    def __init__(
        self,
        name: str | None = None,
        config: dict[str, Any] | None = None,
        cache_dir: Path | str | None = None,
    ) -> None:
        """Initialize the IBM backend.

        Args:
            name: Optional name for this backend instance.
            config: Optional configuration dictionary. Can include:
                - token: IBM Quantum API token
                - proxy: Dict with 'http' and/or 'https' keys
            cache_dir: Optional custom cache directory path.
        """
        super().__init__(name=name, config=config, cache_dir=cache_dir)
        self._proxy_config: dict[str, str] | None = None
        self._api_token: str | None = None
        self._load_ibm_config()

    def _load_ibm_config(self) -> None:
        """Load IBM configuration including proxy settings.

        Loads from (in priority order):
        1. Explicit config dict passed to constructor
        2. Environment variables (HTTP_PROXY, HTTPS_PROXY)
        3. qpandalite.yml configuration file
        """
        from qpandalite.config import get_ibm_config
        from qpandalite.network_utils import (
            detect_system_proxy,
            get_ibm_proxy_from_config,
        )

        # Start with config file settings
        try:
            file_config = get_ibm_config()
            self._api_token = file_config.get("token")
            self._proxy_config = get_ibm_proxy_from_config(file_config)
        except Exception:
            file_config = {}

        # Override with explicit config if provided
        if self.config:
            if "token" in self.config:
                self._api_token = self.config["token"]
            if "proxy" in self.config:
                proxy = self.config["proxy"]
                if isinstance(proxy, dict):
                    self._proxy_config = {
                        k: v for k, v in proxy.items()
                        if k in ("http", "https") and v
                    }
                elif isinstance(proxy, str):
                    self._proxy_config = {"http": proxy, "https": proxy}

        # Environment variables take highest priority
        env_proxies = detect_system_proxy()
        if env_proxies.get("http"):
            if self._proxy_config is None:
                self._proxy_config = {}
            self._proxy_config["http"] = env_proxies["http"]
        if env_proxies.get("https"):
            if self._proxy_config is None:
                self._proxy_config = {}
            self._proxy_config["https"] = env_proxies["https"]

    def _create_adapter(self) -> QiskitAdapter:
        """Create an IBM Qiskit adapter.

        Returns:
            A configured QiskitAdapter instance.
        """
        # Pass proxy configuration to adapter if available
        if self._proxy_config:
            return QiskitAdapter(proxy=self._proxy_config)
        return QiskitAdapter()

    def check_proxy(self) -> bool:
        """Check if the configured proxy is available.

        Returns:
            True if proxy is configured and reachable, False otherwise.

        Note:
            If no proxy is configured, returns True (direct connection).
        """
        from qpandalite.network_utils import check_proxy_connectivity

        if not self._proxy_config:
            return True  # No proxy configured, direct connection

        # Check HTTPS proxy first (preferred for IBM Quantum)
        https_proxy = self._proxy_config.get("https")
        if https_proxy:
            return check_proxy_connectivity(https_proxy)

        # Fall back to HTTP proxy
        http_proxy = self._proxy_config.get("http")
        if http_proxy:
            return check_proxy_connectivity(http_proxy)

        return False

    def test_connectivity(self) -> dict[str, Any]:
        """Test connectivity to IBM Quantum services.

        Returns:
            dict with connectivity test results:
            {
                'success': bool,
                'message': str,
                'proxy_used': dict | None,
                'response_time_ms': float | None,
            }
        """
        from qpandalite.network_utils import test_ibm_connectivity

        return test_ibm_connectivity(
            token=self._api_token,
            proxy=self._proxy_config,
        )

    def get_proxy_config(self) -> dict[str, str] | None:
        """Get the current proxy configuration.

        Returns:
            Dict with 'http' and/or 'https' proxy URLs, or None if not configured.
        """
        return self._proxy_config.copy() if self._proxy_config else None


# -----------------------------------------------------------------------------
# Backend Registry
# -----------------------------------------------------------------------------

BACKENDS: dict[str, Type[QuantumBackend]] = {
    "originq": OriginQBackend,
    "quafu": QuafuBackend,
    "ibm": IBMBackend,
}


# -----------------------------------------------------------------------------
# Public API Functions
# -----------------------------------------------------------------------------

def get_backend(
    name: str,
    *,
    config: dict[str, Any] | None = None,
    use_cache: bool = True,
    cache_dir: Path | str | None = None,
) -> QuantumBackend:
    """Get or create a backend instance by name.
    
    This is the main factory function for obtaining backend instances.
    It uses the BACKENDS registry to look up the appropriate backend class
    and returns a configured instance.
    
    Args:
        name: The platform name ('originq', 'quafu', or 'ibm').
        config: Optional configuration dictionary for the backend.
        use_cache: Whether to use cache. Defaults to True.
        cache_dir: Optional custom cache directory path.
        
    Returns:
        A configured QuantumBackend instance.
        
    Raises:
        ValueError: If the backend name is not recognized.
        RuntimeError: If the backend cannot be initialized.
        
    Example:
        >>> backend = get_backend('originq')
        >>> task_id = backend.submit(circuit, shots=1000)
    """
    if name not in BACKENDS:
        available = ", ".join(BACKENDS.keys())
        raise ValueError(
            f"Unknown backend '{name}'. Available backends: {available}"
        )
    
    backend_class = BACKENDS[name]
    return backend_class.get_instance(
        name=None,
        config=config,
        use_cache=use_cache,
        cache_dir=cache_dir,
    )


def list_backends() -> dict[str, dict[str, Any]]:
    """List all available backends and their status.
    
    Returns:
        A dictionary mapping backend names to their information:
        {
            'originq': {'available': True, 'platform': 'originq'},
            'quafu': {'available': False, 'platform': 'quafu'},
            ...
        }
        
    Example:
        >>> backends = list_backends()
        >>> for name, info in backends.items():
        ...     print(f"{name}: {'available' if info['available'] else 'unavailable'}")
    """
    result = {}
    for name, backend_class in BACKENDS.items():
        result[name] = {
            "platform": name,
            "available": backend_class.list_available(),
            "class": backend_class.__name__,
        }
    return result


def register_backend(
    name: str,
    backend_class: Type[QuantumBackend],
    allow_override: bool = False,
) -> None:
    """Register a custom backend class.
    
    Args:
        name: The platform name to register.
        backend_class: The backend class to register.
        allow_override: Whether to allow overriding existing registrations.
        
    Raises:
        ValueError: If the name is already registered and override is False.
        
    Example:
        >>> class MyBackend(QuantumBackend):
        ...     platform = "my_platform"
        ...     def _create_adapter(self):
        ...         return MyAdapter()
        ...
        >>> register_backend("my_platform", MyBackend)
    """
    if name in BACKENDS and not allow_override:
        raise ValueError(
            f"Backend '{name}' is already registered. "
            "Use allow_override=True to replace it."
        )
    
    # Validate the backend class
    if not issubclass(backend_class, QuantumBackend):
        raise TypeError(
            f"Backend class must be a subclass of QuantumBackend, "
            f"got {type(backend_class)}"
        )
    
    if not backend_class.platform:
        raise ValueError(
            f"Backend class {backend_class.__name__} must define a platform attribute"
        )
    
    BACKENDS[name] = backend_class


def unregister_backend(name: str) -> None:
    """Unregister a backend.
    
    Args:
        name: The platform name to unregister.
        
    Raises:
        ValueError: If the backend is not registered.
    """
    if name not in BACKENDS:
        raise ValueError(f"Backend '{name}' is not registered")
    
    del BACKENDS[name]


def clear_backend_cache(cache_dir: Path | str | None = None) -> None:
    """Clear all backend caches.
    
    Args:
        cache_dir: Optional custom cache directory. Uses default if None.
    """
    cache_path = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
    
    if not cache_path.exists():
        return
    
    for cache_file in cache_path.glob(f"*{CACHE_FILE_SUFFIX}"):
        try:
            cache_file.unlink()
        except (IOError, OSError):
            pass
