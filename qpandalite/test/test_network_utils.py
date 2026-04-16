"""Tests for network_utils module.

This module tests the proxy detection and connectivity checking utilities.
"""

from __future__ import annotations

import os
import unittest
from unittest.mock import MagicMock, patch

from qpandalite.network_utils import (
    check_proxy_connectivity,
    detect_system_proxy,
    get_ibm_proxy_from_config,
    test_ibm_connectivity,
)


class TestDetectSystemProxy(unittest.TestCase):
    """Tests for detect_system_proxy function."""

    def test_detect_no_proxy(self):
        """Test detection when no proxy is set."""
        # Clear all proxy env vars using mock
        with patch.dict(os.environ, {}, clear=False):
            for key in ["HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"]:
                os.environ.pop(key, None)

            result = detect_system_proxy()
            self.assertIsNone(result["http"])
            self.assertIsNone(result["https"])

    def test_detect_http_proxy_uppercase(self):
        """Test detection of HTTP_PROXY (uppercase)."""
        with patch.dict(os.environ, {"HTTP_PROXY": "http://proxy.example.com:8080"}, clear=False):
            # Ensure lowercase is not set
            os.environ.pop("http_proxy", None)

            result = detect_system_proxy()
            self.assertEqual(result["http"], "http://proxy.example.com:8080")
            self.assertIsNone(result["https"])

    def test_detect_http_proxy_lowercase(self):
        """Test detection of http_proxy (lowercase)."""
        with patch.dict(os.environ, {"http_proxy": "http://proxy.example.com:8080"}, clear=False):
            # Ensure uppercase is not set
            os.environ.pop("HTTP_PROXY", None)

            result = detect_system_proxy()
            self.assertEqual(result["http"], "http://proxy.example.com:8080")

    def test_detect_https_proxy(self):
        """Test detection of HTTPS_PROXY."""
        with patch.dict(os.environ, {"HTTPS_PROXY": "https://proxy.example.com:8080"}, clear=False):
            # Ensure lowercase is not set
            os.environ.pop("https_proxy", None)

            result = detect_system_proxy()
            self.assertEqual(result["https"], "https://proxy.example.com:8080")

    def test_detect_both_proxies(self):
        """Test detection of both HTTP and HTTPS proxies."""
        env_vars = {
            "HTTP_PROXY": "http://http-proxy.example.com:8080",
            "HTTPS_PROXY": "https://https-proxy.example.com:8443"
        }
        with patch.dict(os.environ, env_vars, clear=False):
            result = detect_system_proxy()
            self.assertEqual(result["http"], "http://http-proxy.example.com:8080")
            self.assertEqual(result["https"], "https://https-proxy.example.com:8443")

    def test_uppercase_takes_precedence(self):
        """Test that uppercase env vars take precedence over lowercase."""
        env_vars = {
            "HTTP_PROXY": "http://uppercase.example.com:8080",
            "http_proxy": "http://lowercase.example.com:9090"
        }
        with patch.dict(os.environ, env_vars, clear=False):
            result = detect_system_proxy()
            self.assertEqual(result["http"], "http://uppercase.example.com:8080")


class TestCheckProxyConnectivity(unittest.TestCase):
    """Tests for check_proxy_connectivity function."""

    @patch("socket.create_connection")
    def test_proxy_connectivity_success(self, mock_create_connection):
        """Test successful proxy connectivity check."""
        mock_socket = MagicMock()
        mock_create_connection.return_value = mock_socket

        result = check_proxy_connectivity("http://proxy.example.com:8080")

        self.assertTrue(result)
        mock_create_connection.assert_called_once()
        mock_socket.close.assert_called_once()

    @patch("socket.create_connection")
    def test_proxy_connectivity_failure(self, mock_create_connection):
        """Test failed proxy connectivity check."""
        mock_create_connection.side_effect = OSError("Connection refused")

        result = check_proxy_connectivity("http://proxy.example.com:8080")

        self.assertFalse(result)

    def test_proxy_connectivity_invalid_url(self):
        """Test connectivity check with invalid URL."""
        result = check_proxy_connectivity("not-a-valid-url")
        self.assertFalse(result)

    def test_proxy_connectivity_default_port(self):
        """Test connectivity check with URL without port."""
        with patch("socket.create_connection") as mock_create_connection:
            mock_socket = MagicMock()
            mock_create_connection.return_value = mock_socket

            result = check_proxy_connectivity("http://proxy.example.com")

            self.assertTrue(result)
            # Should use default port 80 for http
            call_args = mock_create_connection.call_args
            self.assertEqual(call_args[0][0][1], 80)


class TestGetIbmProxyFromConfig(unittest.TestCase):
    """Tests for get_ibm_proxy_from_config function."""

    def test_no_proxy_config(self):
        """Test with no proxy configuration."""
        config = {"token": "test_token"}
        result = get_ibm_proxy_from_config(config)
        self.assertIsNone(result)

    def test_empty_proxy_config(self):
        """Test with empty proxy configuration."""
        config = {"token": "test_token", "proxy": {}}
        result = get_ibm_proxy_from_config(config)
        self.assertIsNone(result)

    def test_http_proxy_only(self):
        """Test with only HTTP proxy configured."""
        config = {
            "token": "test_token",
            "proxy": {"http": "http://proxy.example.com:8080"}
        }
        result = get_ibm_proxy_from_config(config)
        self.assertEqual(result, {"http": "http://proxy.example.com:8080"})

    def test_https_proxy_only(self):
        """Test with only HTTPS proxy configured."""
        config = {
            "token": "test_token",
            "proxy": {"https": "https://proxy.example.com:8443"}
        }
        result = get_ibm_proxy_from_config(config)
        self.assertEqual(result, {"https": "https://proxy.example.com:8443"})

    def test_both_proxies(self):
        """Test with both HTTP and HTTPS proxies configured."""
        config = {
            "token": "test_token",
            "proxy": {
                "http": "http://http-proxy.example.com:8080",
                "https": "https://https-proxy.example.com:8443"
            }
        }
        result = get_ibm_proxy_from_config(config)
        self.assertEqual(result, {
            "http": "http://http-proxy.example.com:8080",
            "https": "https://https-proxy.example.com:8443"
        })

    def test_empty_proxy_values(self):
        """Test with empty proxy values."""
        config = {
            "token": "test_token",
            "proxy": {
                "http": "",
                "https": ""
            }
        }
        result = get_ibm_proxy_from_config(config)
        self.assertIsNone(result)


class TestTestIbmConnectivity(unittest.TestCase):
    """Tests for test_ibm_connectivity function."""

    def setUp(self):
        """Save original environment variables."""
        self.original_token = os.environ.get("IBM_TOKEN")

    def tearDown(self):
        """Restore original environment variables."""
        if self.original_token is None:
            os.environ.pop("IBM_TOKEN", None)
        else:
            os.environ["IBM_TOKEN"] = self.original_token

    def test_no_token_provided_and_no_env_var(self):
        """Test when no token is provided and no env var is set."""
        os.environ.pop("IBM_TOKEN", None)

        result = test_ibm_connectivity()

        self.assertFalse(result["success"])
        self.assertIn("token not provided", result["message"])
        self.assertIsNone(result["response_time_ms"])

    def test_uses_env_var_token(self):
        """Test that IBM_TOKEN env var is used when token not provided."""
        os.environ["IBM_TOKEN"] = "env_token_123"

        # Mock the actual HTTP request to avoid network calls
        with patch("urllib.request.OpenerDirector.open") as mock_open:
            mock_response = MagicMock()
            mock_response.getcode.return_value = 200
            mock_open.return_value.__enter__ = MagicMock(return_value=mock_response)
            mock_open.return_value.__exit__ = MagicMock(return_value=False)

            result = test_ibm_connectivity()

            # Should attempt to connect (actual result depends on mock)
            self.assertIsNotNone(result)

    def test_with_explicit_proxy(self):
        """Test with explicit proxy configuration."""
        proxy = {"https": "http://proxy.example.com:8080"}

        result = test_ibm_connectivity(
            token="test_token",
            proxy=proxy
        )

        # Verify proxy is recorded in result
        self.assertEqual(result["proxy_used"], proxy)

    def test_with_string_proxy(self):
        """Test with string proxy configuration."""
        with patch("urllib.request.OpenerDirector.open") as mock_open:
            mock_response = MagicMock()
            mock_response.getcode.return_value = 200
            mock_open.return_value.__enter__ = MagicMock(return_value=mock_response)
            mock_open.return_value.__exit__ = MagicMock(return_value=False)

            result = test_ibm_connectivity(
                token="test_token",
                proxy="http://proxy.example.com:8080"
            )

            # String proxy should be converted to dict
            self.assertIsNotNone(result["proxy_used"])

    def test_connectivity_failure(self):
        """Test handling of connection failure."""
        with patch("urllib.request.OpenerDirector.open") as mock_open:
            mock_open.side_effect = Exception("Connection refused")

            result = test_ibm_connectivity(token="test_token")

            self.assertFalse(result["success"])
            self.assertIn("Connection failed", result["message"])
            self.assertIsNotNone(result["response_time_ms"])


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple functions."""

    def test_system_proxy_to_ibm_connectivity(self):
        """Test full flow from system proxy detection to IBM connectivity."""
        with patch.dict(os.environ, {
            "HTTPS_PROXY": "http://proxy.example.com:8080",
            "IBM_TOKEN": "test_token"
        }):
            # Detect system proxy
            proxies = detect_system_proxy()
            self.assertEqual(proxies["https"], "http://proxy.example.com:8080")

            # Test IBM connectivity with detected proxy
            with patch("urllib.request.OpenerDirector.open") as mock_open:
                mock_response = MagicMock()
                mock_response.getcode.return_value = 200
                mock_open.return_value.__enter__ = MagicMock(return_value=mock_response)
                mock_open.return_value.__exit__ = MagicMock(return_value=False)

                result = test_ibm_connectivity(proxy=proxies)
                self.assertTrue(result["success"])


if __name__ == "__main__":
    unittest.main()