"""
Tests for Configuration module
Part of Integrity Validation Matrix: Configuration Settings
"""

import pytest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfigDefaults:
    """Tests for default configuration values."""

    def test_defaults_values(self):
        from wFabricSecurity.fabric_security.config.defaults import Defaults

        assert Defaults.FABRIC_CHANNEL == "mychannel"
        assert Defaults.FABRIC_CHAINCODE == "tasks"
        assert Defaults.RATE_LIMIT_REQUESTS_PER_SECOND == 100

    def test_defaults_retry(self):
        from wFabricSecurity.fabric_security.config.defaults import Defaults

        assert Defaults.RETRY_MAX_ATTEMPTS == 3
        assert Defaults.RETRY_BACKOFF_FACTOR == 1.5
        assert Defaults.RETRY_INITIAL_DELAY == 0.5


class TestConfigSettings:
    """Tests for Settings class."""

    def test_settings_default_init(self):
        from wFabricSecurity import Settings

        settings = Settings()
        assert settings.fabric_channel == "mychannel"
        assert settings.rate_limit_requests_per_second == 100

    def test_settings_from_env(self):
        from wFabricSecurity import Settings

        os.environ["FABRIC_CHANNEL"] = "test-channel"
        os.environ["FABRIC_RATE_LIMIT_RPS"] = "200"
        settings = Settings.from_env()
        assert settings.fabric_channel == "test-channel"
        assert settings.rate_limit_requests_per_second == 200
        del os.environ["FABRIC_CHANNEL"]
        del os.environ["FABRIC_RATE_LIMIT_RPS"]

    def test_settings_to_yaml(self):
        from wFabricSecurity import Settings

        settings = Settings()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_file = f.name
        try:
            settings.to_yaml(temp_file)
            assert os.path.exists(temp_file)
        finally:
            os.unlink(temp_file)

    def test_settings_from_yaml_not_found(self):
        from wFabricSecurity import Settings

        settings = Settings.from_yaml("/nonexistent/path.yaml")
        assert settings.fabric_channel == "mychannel"

    def test_settings_from_yaml_file(self):
        from wFabricSecurity import Settings

        yaml_content = """local_data_dir: /custom/path
fabric_channel: custom_channel
rate_limit_rps: 200
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        try:
            settings = Settings.from_yaml(temp_file)
            assert settings.local_data_dir == "/custom/path"
            assert settings.fabric_channel == "custom_channel"
            assert settings.rate_limit_requests_per_second == 200
        finally:
            os.unlink(temp_file)

    def test_settings_singleton(self):
        from wFabricSecurity.fabric_security.config.settings import get_settings

        settings = get_settings()
        assert settings is not None

    def test_settings_extra_chaincodes(self):
        from wFabricSecurity import Settings

        settings = Settings(extra_chaincodes=["cc1", "cc2"])
        assert len(settings.extra_chaincodes) == 2
        assert "cc1" in settings.extra_chaincodes
