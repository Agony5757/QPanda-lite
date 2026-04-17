"""Tests for qpandalite.config module."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from qpandalite import config
from qpandalite.config import (
    DEFAULT_CONFIG,
    ConfigError,
    ConfigValidationError,
    PlatformNotFoundError,
    ProfileNotFoundError,
    create_default_config,
    get_active_profile,
    get_ibm_config,
    get_originq_config,
    get_platform_config,
    get_quafu_config,
    load_config,
    save_config,
    set_active_profile,
    update_platform_config,
    validate_config,
)


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_default_when_file_not_exists(self, tmp_path: Path) -> None:
        """Test that default config is returned when file doesn't exist."""
        non_existent = tmp_path / "non_existent.yml"
        result = load_config(non_existent)
        assert result == DEFAULT_CONFIG

    def test_load_existing_config(self, tmp_path: Path) -> None:
        """Test loading an existing configuration file."""
        config_file = tmp_path / "test_config.yml"
        test_config = {
            "default": {
                "originq": {"token": "test_token"},
            }
        }
        save_config(test_config, config_file)
        result = load_config(config_file)
        assert result == test_config

    def test_load_empty_file_returns_default(self, tmp_path: Path) -> None:
        """Test that empty file returns default config."""
        config_file = tmp_path / "empty.yml"
        config_file.write_text("")
        result = load_config(config_file)
        assert result == DEFAULT_CONFIG

    def test_load_invalid_yaml_raises_error(self, tmp_path: Path) -> None:
        """Test that invalid YAML raises ConfigError."""
        config_file = tmp_path / "invalid.yml"
        config_file.write_text("invalid: yaml: [")
        with pytest.raises(ConfigError):
            load_config(config_file)


class TestSaveConfig:
    """Tests for save_config function."""

    def test_save_config_creates_file(self, tmp_path: Path) -> None:
        """Test that save_config creates the configuration file."""
        config_file = tmp_path / "config.yml"
        test_config = {"default": {"originq": {"token": "test"}}}
        save_config(test_config, config_file)
        assert config_file.exists()

    def test_save_config_creates_directory(self, tmp_path: Path) -> None:
        """Test that save_config creates parent directories."""
        config_file = tmp_path / "nested" / "dir" / "config.yml"
        test_config = {"default": {"originq": {"token": "test"}}}
        save_config(test_config, config_file)
        assert config_file.exists()

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        """Test that saved config can be loaded back correctly."""
        config_file = tmp_path / "config.yml"
        test_config = {
            "default": {
                "originq": {"token": "originq_token", "submit_url": "http://submit"},
                "quafu": {"token": "quafu_token"},
                "ibm": {"token": "ibm_token", "proxy": {"http": "http://proxy"}},
            },
            "prod": {
                "originq": {"token": "prod_token"},
            },
        }
        save_config(test_config, config_file)
        loaded = load_config(config_file)
        assert loaded == test_config


class TestGetPlatformConfig:
    """Tests for get_platform_config function."""

    def test_get_originq_config(self, tmp_path: Path) -> None:
        """Test getting OriginQ configuration."""
        config_file = tmp_path / "config.yml"
        test_config = {
            "default": {
                "originq": {
                    "token": "originq_token",
                    "submit_url": "http://submit",
                    "query_url": "http://query",
                },
            }
        }
        save_config(test_config, config_file)
        result = get_platform_config("originq", config_path=config_file)
        assert result["token"] == "originq_token"
        assert result["submit_url"] == "http://submit"

    def test_get_quafu_config(self, tmp_path: Path) -> None:
        """Test getting Quafu configuration."""
        config_file = tmp_path / "config.yml"
        test_config = {"default": {"quafu": {"token": "quafu_token"}}}
        save_config(test_config, config_file)
        result = get_platform_config("quafu", config_path=config_file)
        assert result["token"] == "quafu_token"

    def test_get_ibm_config_with_proxy(self, tmp_path: Path) -> None:
        """Test getting IBM configuration with proxy."""
        config_file = tmp_path / "config.yml"
        test_config = {
            "default": {
                "ibm": {
                    "token": "ibm_token",
                    "proxy": {"http": "http://proxy:8080", "https": "https://proxy:8080"},
                },
            }
        }
        save_config(test_config, config_file)
        result = get_platform_config("ibm", config_path=config_file)
        assert result["token"] == "ibm_token"
        assert result["proxy"]["http"] == "http://proxy:8080"

    def test_get_config_with_different_profile(self, tmp_path: Path) -> None:
        """Test getting configuration with different profile."""
        config_file = tmp_path / "config.yml"
        test_config = {
            "default": {"originq": {"token": "default_token"}},
            "prod": {"originq": {"token": "prod_token"}},
        }
        save_config(test_config, config_file)
        result = get_platform_config("originq", profile="prod", config_path=config_file)
        assert result["token"] == "prod_token"

    def test_get_config_unsupported_platform_raises(self, tmp_path: Path) -> None:
        """Test that unsupported platform raises PlatformNotFoundError."""
        config_file = tmp_path / "config.yml"
        save_config(DEFAULT_CONFIG, config_file)
        with pytest.raises(PlatformNotFoundError):
            get_platform_config("unsupported", config_path=config_file)

    def test_get_config_missing_profile_raises(self, tmp_path: Path) -> None:
        """Test that missing profile raises ProfileNotFoundError."""
        config_file = tmp_path / "config.yml"
        save_config(DEFAULT_CONFIG, config_file)
        with pytest.raises(ProfileNotFoundError):
            get_platform_config("originq", profile="nonexistent", config_path=config_file)

    def test_get_config_missing_platform_raises(self, tmp_path: Path) -> None:
        """Test that missing platform in profile raises ConfigError."""
        config_file = tmp_path / "config.yml"
        test_config = {"default": {}}  # No platforms configured
        save_config(test_config, config_file)
        with pytest.raises(ConfigError):
            get_platform_config("originq", config_path=config_file)


class TestValidateConfig:
    """Tests for validate_config function."""

    def test_validate_valid_config(self) -> None:
        """Test validating a valid configuration."""
        valid_config = {
            "default": {
                "originq": {"token": "t", "submit_url": "s", "query_url": "q"},
                "quafu": {"token": "t"},
                "ibm": {"token": "t"},
            }
        }
        errors = validate_config(valid_config)
        assert errors == []

    def test_validate_empty_config(self) -> None:
        """Test validating empty configuration."""
        errors = validate_config({})
        assert len(errors) == 1
        assert "empty" in errors[0].lower()

    def test_validate_non_dict_config(self) -> None:
        """Test validating non-dictionary configuration."""
        errors = validate_config("not a dict")
        assert len(errors) == 1
        assert "dictionary" in errors[0].lower()

    def test_validate_missing_required_fields(self) -> None:
        """Test validating configuration with missing required fields."""
        invalid_config = {
            "default": {
                "originq": {"token": "t"},  # Missing submit_url and query_url
            }
        }
        errors = validate_config(invalid_config)
        assert len(errors) == 2
        assert any("submit_url" in e for e in errors)
        assert any("query_url" in e for e in errors)

    def test_validate_invalid_proxy_config(self) -> None:
        """Test validating IBM configuration with invalid proxy."""
        invalid_config = {
            "default": {
                "ibm": {"token": "t", "proxy": "not a dict"},
            }
        }
        errors = validate_config(invalid_config)
        assert len(errors) == 1
        assert "proxy" in errors[0].lower()

    def test_validate_profile_not_dict(self) -> None:
        """Test validating configuration where profile is not a dict."""
        invalid_config = {"default": "not a dict"}
        errors = validate_config(invalid_config)
        assert len(errors) == 1
        assert "dictionary" in errors[0].lower()


class TestCreateDefaultConfig:
    """Tests for create_default_config function."""

    def test_create_default_config(self, tmp_path: Path) -> None:
        """Test creating default configuration file."""
        config_file = tmp_path / "config.yml"
        create_default_config(config_file)
        assert config_file.exists()
        loaded = load_config(config_file)
        assert loaded == DEFAULT_CONFIG

    def test_create_default_config_does_not_overwrite(self, tmp_path: Path) -> None:
        """Test that create_default_config doesn't overwrite existing file."""
        config_file = tmp_path / "config.yml"
        custom_config = {"custom": {"key": "value"}}
        save_config(custom_config, config_file)
        create_default_config(config_file)
        loaded = load_config(config_file)
        assert loaded == custom_config


class TestUpdatePlatformConfig:
    """Tests for update_platform_config function."""

    def test_update_existing_platform(self, tmp_path: Path) -> None:
        """Test updating an existing platform configuration."""
        config_file = tmp_path / "config.yml"
        create_default_config(config_file)

        new_config = {"token": "new_token", "submit_url": "http://new"}
        update_platform_config("originq", new_config, config_path=config_file)

        result = get_platform_config("originq", config_path=config_file)
        assert result["token"] == "new_token"
        assert result["submit_url"] == "http://new"

    def test_update_create_new_profile(self, tmp_path: Path) -> None:
        """Test update creates new profile if it doesn't exist."""
        config_file = tmp_path / "config.yml"
        create_default_config(config_file)

        new_config = {"token": "test_token"}
        update_platform_config("quafu", new_config, profile="test", config_path=config_file)

        result = get_platform_config("quafu", profile="test", config_path=config_file)
        assert result["token"] == "test_token"

    def test_update_unsupported_platform_raises(self, tmp_path: Path) -> None:
        """Test that updating unsupported platform raises PlatformNotFoundError."""
        config_file = tmp_path / "config.yml"
        create_default_config(config_file)
        with pytest.raises(PlatformNotFoundError):
            update_platform_config("unsupported", {}, config_path=config_file)


class TestActiveProfile:
    """Tests for get_active_profile and set_active_profile functions."""

    def test_get_active_profile_default(self, tmp_path: Path) -> None:
        """Test getting default active profile."""
        config_file = tmp_path / "config.yml"
        create_default_config(config_file)
        result = get_active_profile(config_file)
        assert result == "default"

    def test_get_active_profile_from_env(self, tmp_path: Path) -> None:
        """Test getting active profile from environment variable."""
        config_file = tmp_path / "config.yml"
        create_default_config(config_file)
        with mock.patch.dict(os.environ, {"QPANDALITE_PROFILE": "prod"}):
            result = get_active_profile(config_file)
            assert result == "prod"

    def test_get_active_profile_from_config(self, tmp_path: Path) -> None:
        """Test getting active profile from configuration file."""
        config_file = tmp_path / "config.yml"
        config = {"active_profile": "staging", "default": {}}
        save_config(config, config_file)
        result = get_active_profile(config_file)
        assert result == "staging"

    def test_env_overrides_config(self, tmp_path: Path) -> None:
        """Test that environment variable overrides config file."""
        config_file = tmp_path / "config.yml"
        config = {"active_profile": "staging", "default": {}}
        save_config(config, config_file)
        with mock.patch.dict(os.environ, {"QPANDALITE_PROFILE": "prod"}):
            result = get_active_profile(config_file)
            assert result == "prod"

    def test_set_active_profile(self, tmp_path: Path) -> None:
        """Test setting active profile."""
        config_file = tmp_path / "config.yml"
        config = {"default": {}, "prod": {}}
        save_config(config, config_file)
        set_active_profile("prod", config_file)
        result = get_active_profile(config_file)
        assert result == "prod"

    def test_set_active_profile_invalid_raises(self, tmp_path: Path) -> None:
        """Test that setting non-existent active profile raises error."""
        config_file = tmp_path / "config.yml"
        create_default_config(config_file)
        with pytest.raises(ProfileNotFoundError):
            set_active_profile("nonexistent", config_file)


class TestConvenienceFunctions:
    """Tests for convenience functions (get_originq_config, etc.)."""

    def test_get_originq_config(self, tmp_path: Path) -> None:
        """Test get_originq_config convenience function."""
        config_file = tmp_path / "config.yml"
        test_config = {"default": {"originq": {"token": "test_token"}}}
        save_config(test_config, config_file)

        with mock.patch.object(config, "CONFIG_FILE", config_file):
            result = get_originq_config()
            assert result["token"] == "test_token"

    def test_get_quafu_config(self, tmp_path: Path) -> None:
        """Test get_quafu_config convenience function."""
        config_file = tmp_path / "config.yml"
        test_config = {"default": {"quafu": {"token": "test_token"}}}
        save_config(test_config, config_file)

        with mock.patch.object(config, "CONFIG_FILE", config_file):
            result = get_quafu_config()
            assert result["token"] == "test_token"

    def test_get_ibm_config(self, tmp_path: Path) -> None:
        """Test get_ibm_config convenience function."""
        config_file = tmp_path / "config.yml"
        test_config = {"default": {"ibm": {"token": "test_token"}}}
        save_config(test_config, config_file)

        with mock.patch.object(config, "CONFIG_FILE", config_file):
            result = get_ibm_config()
            assert result["token"] == "test_token"


class TestDefaultConfig:
    """Tests for DEFAULT_CONFIG constant."""

    def test_default_config_structure(self) -> None:
        """Test that DEFAULT_CONFIG has expected structure."""
        assert "default" in DEFAULT_CONFIG
        assert "originq" in DEFAULT_CONFIG["default"]
        assert "quafu" in DEFAULT_CONFIG["default"]
        assert "ibm" in DEFAULT_CONFIG["default"]

    def test_originq_default_fields(self) -> None:
        """Test OriginQ default configuration fields."""
        originq = DEFAULT_CONFIG["default"]["originq"]
        assert "token" in originq
        assert "submit_url" in originq
        assert "query_url" in originq
        assert "available_qubits" in originq
        assert "available_topology" in originq
        assert "task_group_size" in originq
        assert originq["task_group_size"] == 200

    def test_quafu_default_fields(self) -> None:
        """Test Quafu default configuration fields."""
        quafu = DEFAULT_CONFIG["default"]["quafu"]
        assert "token" in quafu

    def test_ibm_default_fields(self) -> None:
        """Test IBM default configuration fields."""
        ibm = DEFAULT_CONFIG["default"]["ibm"]
        assert "token" in ibm
        assert "proxy" in ibm
        assert "http" in ibm["proxy"]
        assert "https" in ibm["proxy"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
