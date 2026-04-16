"""QPanda-lite configuration management module.

This module provides centralized configuration management for quantum cloud platforms
including OriginQ (本源量子), Quafu (夸父), and IBM Quantum.

Configuration file location: ~/.qpandalite/qpandalite.yml

Example configuration structure:
    default:
      originq:
        token: xxx
        submit_url: xxx
        query_url: xxx
      quafu:
        token: xxx
      ibm:
        token: xxx
        proxy:
          http: http://proxy:8080
          https: https://proxy:8080
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

# Configuration file path
CONFIG_DIR = Path.home() / ".qpandalite"
CONFIG_FILE = CONFIG_DIR / "qpandalite.yml"

# Default configuration template
DEFAULT_CONFIG: dict[str, Any] = {
    "default": {
        "originq": {
            "token": "",
            "submit_url": "",
            "query_url": "",
            "available_qubits": [],
            "available_topology": [],
            "task_group_size": 200,
        },
        "quafu": {
            "token": "",
        },
        "ibm": {
            "token": "",
            "proxy": {
                "http": "",
                "https": "",
            },
        },
    }
}

# Supported platforms
SUPPORTED_PLATFORMS = ["originq", "quafu", "ibm"]

# Platform-specific required fields
PLATFORM_REQUIRED_FIELDS = {
    "originq": ["token", "submit_url", "query_url"],
    "quafu": ["token"],
    "ibm": ["token"],
}


class ConfigError(Exception):
    """Configuration-related error."""
    pass


class ConfigValidationError(ConfigError):
    """Configuration validation error."""
    pass


class PlatformNotFoundError(ConfigError):
    """Platform configuration not found error."""
    pass


class ProfileNotFoundError(ConfigError):
    """Profile not found error."""
    pass


def _ensure_config_dir() -> None:
    """Ensure configuration directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration file. If None, uses default path.

    Returns:
        Configuration dictionary.

    Raises:
        ConfigError: If configuration file cannot be read.
    """
    path = Path(config_path) if config_path else CONFIG_FILE

    if not path.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        if config is None:
            return DEFAULT_CONFIG.copy()
        return config
    except yaml.YAMLError as e:
        raise ConfigError(f"Failed to parse YAML configuration: {e}") from e
    except IOError as e:
        raise ConfigError(f"Failed to read configuration file: {e}") from e


def save_config(config: dict[str, Any], config_path: str | Path | None = None) -> None:
    """Save configuration to YAML file.

    Args:
        config: Configuration dictionary to save.
        config_path: Path to configuration file. If None, uses default path.

    Raises:
        ConfigError: If configuration file cannot be written.
    """
    path = Path(config_path) if config_path else CONFIG_FILE
    _ensure_config_dir()

    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                config,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
    except IOError as e:
        raise ConfigError(f"Failed to write configuration file: {e}") from e


def get_platform_config(
    platform_name: str,
    profile: str = "default",
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Get configuration for a specific platform.

    Args:
        platform_name: Name of the quantum cloud platform (originq, quafu, ibm).
        profile: Configuration profile name (default: "default").
        config_path: Path to configuration file. If None, uses default path.

    Returns:
        Platform configuration dictionary.

    Raises:
        PlatformNotFoundError: If platform is not supported.
        ProfileNotFoundError: If profile does not exist in configuration.
        ConfigError: If platform configuration is not found within profile.
    """
    if platform_name not in SUPPORTED_PLATFORMS:
        raise PlatformNotFoundError(
            f"Unsupported platform: {platform_name}. "
            f"Supported platforms: {', '.join(SUPPORTED_PLATFORMS)}"
        )

    config = load_config(config_path)

    if profile not in config:
        raise ProfileNotFoundError(
            f"Profile '{profile}' not found in configuration. "
            f"Available profiles: {', '.join(config.keys())}"
        )

    profile_config = config[profile]

    if platform_name not in profile_config:
        raise ConfigError(
            f"Platform '{platform_name}' not found in profile '{profile}'"
        )

    return profile_config[platform_name]


def validate_config(
    config: dict[str, Any] | None = None,
    config_path: str | Path | None = None,
) -> list[str]:
    """Validate configuration structure and required fields.

    Args:
        config: Configuration dictionary to validate. If None, loads from file.
        config_path: Path to configuration file. Used if config is None.

    Returns:
        List of validation error messages. Empty list if valid.
    """
    errors: list[str] = []

    try:
        cfg = config if config is not None else load_config(config_path)
    except ConfigError as e:
        return [str(e)]

    if not isinstance(cfg, dict):
        return ["Configuration must be a dictionary"]

    if not cfg:
        return ["Configuration is empty"]

    for profile_name, profile_config in cfg.items():
        if not isinstance(profile_config, dict):
            errors.append(f"Profile '{profile_name}' must be a dictionary")
            continue

        for platform_name in SUPPORTED_PLATFORMS:
            if platform_name not in profile_config:
                continue

            platform_config = profile_config[platform_name]

            if not isinstance(platform_config, dict):
                errors.append(
                    f"Platform '{platform_name}' in profile '{profile_name}' "
                    "must be a dictionary"
                )
                continue

            # Check required fields
            required_fields = PLATFORM_REQUIRED_FIELDS.get(platform_name, [])
            for field in required_fields:
                if field not in platform_config:
                    errors.append(
                        f"Missing required field '{field}' for platform "
                        f"'{platform_name}' in profile '{profile_name}'"
                    )

            # Validate proxy configuration for IBM
            if platform_name == "ibm" and "proxy" in platform_config:
                proxy = platform_config["proxy"]
                if not isinstance(proxy, dict):
                    errors.append(
                        f"Proxy configuration for IBM in profile '{profile_name}' "
                        "must be a dictionary"
                    )
                else:
                    for proxy_type in ["http", "https"]:
                        if proxy_type in proxy and not isinstance(proxy[proxy_type], str):
                            errors.append(
                                f"Proxy '{proxy_type}' for IBM in profile "
                                f"'{profile_name}' must be a string"
                            )

    return errors


def create_default_config(config_path: str | Path | None = None) -> None:
    """Create default configuration file if it doesn't exist.

    Args:
        config_path: Path to configuration file. If None, uses default path.
    """
    path = Path(config_path) if config_path else CONFIG_FILE

    if path.exists():
        return

    _ensure_config_dir()
    save_config(DEFAULT_CONFIG, path)


def update_platform_config(
    platform_name: str,
    platform_config: dict[str, Any],
    profile: str = "default",
    config_path: str | Path | None = None,
) -> None:
    """Update configuration for a specific platform.

    Args:
        platform_name: Name of the quantum cloud platform.
        platform_config: Platform configuration dictionary.
        profile: Configuration profile name (default: "default").
        config_path: Path to configuration file. If None, uses default path.

    Raises:
        PlatformNotFoundError: If platform is not supported.
    """
    if platform_name not in SUPPORTED_PLATFORMS:
        raise PlatformNotFoundError(
            f"Unsupported platform: {platform_name}. "
            f"Supported platforms: {', '.join(SUPPORTED_PLATFORMS)}"
        )

    config = load_config(config_path)

    if profile not in config:
        config[profile] = {}

    config[profile][platform_name] = platform_config
    save_config(config, config_path)


def get_active_profile(config_path: str | Path | None = None) -> str:
    """Get the active profile from configuration.

    First checks QPANDALITE_PROFILE environment variable,
    then falls back to 'default'.

    Args:
        config_path: Path to configuration file. If None, uses default path.

    Returns:
        Active profile name.
    """
    env_profile = os.environ.get("QPANDALITE_PROFILE")
    if env_profile:
        return env_profile

    config = load_config(config_path)
    if "active_profile" in config:
        return config["active_profile"]

    return "default"


def set_active_profile(
    profile: str,
    config_path: str | Path | None = None,
) -> None:
    """Set the active profile in configuration.

    Args:
        profile: Profile name to set as active.
        config_path: Path to configuration file. If None, uses default path.

    Raises:
        ProfileNotFoundError: If profile does not exist in configuration.
    """
    config = load_config(config_path)

    if profile not in config:
        raise ProfileNotFoundError(
            f"Profile '{profile}' not found in configuration. "
            f"Available profiles: {', '.join(k for k in config.keys() if k != 'active_profile')}"
        )

    config["active_profile"] = profile
    save_config(config, config_path)


# Convenience functions for specific platforms

def get_originq_config(profile: str = "default") -> dict[str, Any]:
    """Get OriginQ (本源量子) configuration.

    Args:
        profile: Configuration profile name (default: "default").

    Returns:
        OriginQ configuration dictionary.
    """
    return get_platform_config("originq", profile)


def get_quafu_config(profile: str = "default") -> dict[str, Any]:
    """Get Quafu (夸父) configuration.

    Args:
        profile: Configuration profile name (default: "default").

    Returns:
        Quafu configuration dictionary.
    """
    return get_platform_config("quafu", profile)


def get_ibm_config(profile: str = "default") -> dict[str, Any]:
    """Get IBM Quantum configuration.

    Args:
        profile: Configuration profile name (default: "default").

    Returns:
        IBM Quantum configuration dictionary.
    """
    return get_platform_config("ibm", profile)
