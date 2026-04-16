"""Network utilities for proxy detection and connectivity testing.

This module provides functions for:
- Detecting system proxy settings
- Testing proxy connectivity
- Testing IBM Quantum connectivity with or without proxy
"""

from __future__ import annotations

__all__ = [
    "check_proxy_connectivity",
    "detect_system_proxy",
    "test_ibm_connectivity",
]

import os
import socket
from typing import Any
from urllib.parse import urlparse


def detect_system_proxy() -> dict[str, str | None]:
    """Detect system proxy settings from environment variables.

    Checks for both uppercase and lowercase environment variable names:
    - HTTP_PROXY / http_proxy
    - HTTPS_PROXY / https_proxy

    Returns:
        dict with keys 'http' and 'https', values are proxy URLs or None.

    Example:
        >>> proxies = detect_system_proxy()
        >>> print(proxies)
        {'http': 'http://proxy.example.com:8080', 'https': None}
    """
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

    return {
        "http": http_proxy,
        "https": https_proxy,
    }


def _parse_proxy_url(proxy_url: str) -> tuple[str, int] | None:
    """Parse proxy URL and extract host and port.

    Args:
        proxy_url: Proxy URL (e.g., 'http://proxy.example.com:8080')

    Returns:
        Tuple of (host, port) or None if parsing fails.
    """
    try:
        parsed = urlparse(proxy_url)
        host = parsed.hostname
        port = parsed.port

        if host is None:
            return None

        # Default ports for http and https
        if port is None:
            if parsed.scheme == "https":
                port = 443
            else:
                port = 80

        return (host, port)
    except Exception:
        return None


def check_proxy_connectivity(
    proxy_url: str,
    test_url: str = "https://www.googleapis.com",
    timeout: float = 10.0,
) -> bool:
    """Check if a proxy is reachable and can connect to a test URL.

    Args:
        proxy_url: The proxy URL to test (e.g., 'http://proxy.example.com:8080').
        test_url: URL to test connectivity through the proxy (default: Google APIs).
        timeout: Connection timeout in seconds (default: 10.0).

    Returns:
        True if the proxy is reachable, False otherwise.

    Note:
        This function performs a basic TCP connection check to the proxy
        host and port. It does not perform an actual HTTP CONNECT request
        or verify that the proxy can reach the test URL.

    Example:
        >>> is_available = check_proxy_connectivity(
        ...     "http://proxy.example.com:8080"
        ... )
        >>> print(f"Proxy available: {is_available}")
    """
    proxy_info = _parse_proxy_url(proxy_url)
    if proxy_info is None:
        return False

    host, port = proxy_info

    try:
        # Attempt TCP connection to the proxy
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except (socket.timeout, socket.error, OSError):
        return False


def _build_proxies_dict(
    proxy: dict[str, str] | str | None,
) -> dict[str, str] | None:
    """Build a proxies dictionary for requests library.

    Args:
        proxy: Can be:
            - None (uses system proxy)
            - A proxy URL string
            - A dict with 'http' and/or 'https' keys

    Returns:
        Dict suitable for requests library or None.
    """
    if proxy is None:
        # Use system proxy
        system_proxies = detect_system_proxy()
        proxies = {}
        if system_proxies.get("http"):
            proxies["http"] = system_proxies["http"]
        if system_proxies.get("https"):
            proxies["https"] = system_proxies["https"]
        return proxies if proxies else None

    if isinstance(proxy, str):
        return {"http": proxy, "https": proxy}

    if isinstance(proxy, dict):
        proxies = {}
        if proxy.get("http"):
            proxies["http"] = proxy["http"]
        if proxy.get("https"):
            proxies["https"] = proxy["https"]
        return proxies if proxies else None

    return None


def test_ibm_connectivity(
    token: str | None = None,
    proxy: dict[str, str] | str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Test connectivity to IBM Quantum services.

    Args:
        token: IBM Quantum API token. If None, tries to load from environment.
        proxy: Proxy configuration. Can be:
            - None: uses system proxy settings
            - str: proxy URL (used for both http and https)
            - dict: with 'http' and/or 'https' keys
        timeout: Request timeout in seconds (default: 30.0).

    Returns:
        dict with connectivity test results:
        {
            'success': bool,
            'message': str,
            'proxy_used': dict | str | None,
            'response_time_ms': float | None,
        }

    Example:
        >>> result = test_ibm_connectivity(
        ...     token="my_api_token",
        ...     proxy={"https": "http://proxy.example.com:8080"}
        ... )
        >>> print(result["success"])
    """
    import time

    # Get token if not provided
    if token is None:
        token = os.getenv("IBM_TOKEN")
        if token is None:
            return {
                "success": False,
                "message": "IBM token not provided and IBM_TOKEN env var not set",
                "proxy_used": proxy,
                "response_time_ms": None,
            }

    # Build proxy configuration
    proxies = _build_proxies_dict(proxy)

    # IBM Quantum API endpoint for authentication test
    # Using IBM Quantum's jobs endpoint for a lightweight check
    ibm_api_url = "https://auth.quantum-computing.ibm.com/api/version"

    start_time = time.time()

    try:
        import urllib.request

        # Build request
        request = urllib.request.Request(
            ibm_api_url,
            headers={"Authorization": f"Bearer {token}"},
            method="GET",
        )

        # Build proxy handler
        proxy_handler = None
        if proxies:
            proxy_handler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(proxy_handler)
        else:
            opener = urllib.request.build_opener()

        # Perform request
        with opener.open(request, timeout=timeout) as response:
            response_time = (time.time() - start_time) * 1000
            status_code = response.getcode()

            if 200 <= status_code < 300:
                return {
                    "success": True,
                    "message": f"Successfully connected to IBM Quantum (status: {status_code})",
                    "proxy_used": proxies or proxy,
                    "response_time_ms": round(response_time, 2),
                }
            else:
                return {
                    "success": False,
                    "message": f"Unexpected status code: {status_code}",
                    "proxy_used": proxies or proxy,
                    "response_time_ms": round(response_time, 2),
                }

    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}",
            "proxy_used": proxies or proxy,
            "response_time_ms": round(response_time, 2),
        }


def get_ibm_proxy_from_config(config: dict[str, Any] | None = None) -> dict[str, str] | None:
    """Extract IBM proxy configuration from qpandalite config.

    Args:
        config: IBM configuration dict. If None, loads from qpandalite config.

    Returns:
        Dict with 'http' and/or 'https' proxy URLs, or None if no proxy configured.

    Example:
        >>> from qpandalite.config import get_ibm_config
        >>> config = get_ibm_config()
        >>> proxy = get_ibm_proxy_from_config(config)
    """
    if config is None:
        from qpandalite.config import get_ibm_config
        config = get_ibm_config()

    proxy_config = config.get("proxy")
    if not proxy_config:
        return None

    proxies = {}
    if proxy_config.get("http"):
        proxies["http"] = proxy_config["http"]
    if proxy_config.get("https"):
        proxies["https"] = proxy_config["https"]

    return proxies if proxies else None