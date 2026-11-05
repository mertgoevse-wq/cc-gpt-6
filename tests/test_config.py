"""Tests for cc-gpt-6 configuration."""

import json
import tempfile
from pathlib import Path

import pytest

# Use a temp config directory
import cc_gpt_6.config as config_module


@pytest.fixture(autouse=True)
def temp_config_dir():
    """Create a temporary config directory for each test."""
    temp_dir = Path(tempfile.mkdtemp())
    config_module.CONFIG_DIR = temp_dir
    config_module.CONFIG_FILE = temp_dir / "config.json"
    yield
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestConfig:
    """Test configuration management."""

    def test_load_config_defaults(self):
        """Test loading default config when no file exists."""
        config = config_module.load_config()
        assert config == config_module.DEFAULT_CONFIG

    def test_load_config_from_file(self):
        """Test loading config from file."""
        custom_config = {
            "language": "de",
            "model": "gpt-6",
            "reasoning_effort": "medium",
            "port": 9999,
        }
        config_module.save_config(custom_config)
        loaded = config_module.load_config()
        assert loaded["language"] == "de"
        assert loaded["model"] == "gpt-6"
        assert loaded["reasoning_effort"] == "medium"
        assert loaded["port"] == 9999

    def test_load_config_merges_with_defaults(self):
        """Test that file config merges with defaults."""
        # Only save partial config
        config_module.save_config({"language": "fr"})
        loaded = config_module.load_config()
        assert loaded["language"] == "fr"
        # Other values should be defaults
        assert loaded["model"] == config_module.DEFAULT_CONFIG["model"]
        assert loaded["port"] == config_module.DEFAULT_CONFIG["port"]

    def test_save_config(self):
        """Test saving config."""
        config = {"language": "es", "port": 8080}
        config_module.save_config(config)
        loaded = config_module.load_config()
        assert loaded["language"] == "es"
        assert loaded["port"] == 8080

    def test_get_config_value(self):
        """Test getting single config value."""
        config_module.save_config({"language": "ja"})
        assert config_module.get_config_value("language") == "ja"
        assert config_module.get_config_value("nonexistent", "default") == "default"

    def test_set_config_value(self):
        """Test setting single config value."""
        config_module.set_config_value("language", "ko")
        assert config_module.get_config_value("language") == "ko"

    def test_reset_config(self):
        """Test resetting config to defaults."""
        config_module.save_config({"language": "de", "model": "gpt-6"})
        config_module.reset_config()
        loaded = config_module.load_config()
        assert loaded == config_module.DEFAULT_CONFIG

    def test_validate_language(self):
        """Test language validation."""
        from cc_gpt_6.i18n import SUPPORTED_LANGUAGES
        for lang in SUPPORTED_LANGUAGES:
            assert config_module.validate_language(lang) is True
        assert config_module.validate_language("invalid") is False

    def test_validate_model(self):
        """Test model validation."""
        from cc_gpt_6.proxy import SUPPORTED_MODELS
        for model in SUPPORTED_MODELS:
            assert config_module.validate_model(model) is True
        assert config_module.validate_model("invalid-model") is False

    def test_validate_reasoning_effort(self):
        """Test reasoning effort validation."""
        from cc_gpt_6.proxy import REASONING_LEVELS
        for effort in REASONING_LEVELS:
            assert config_module.validate_reasoning_effort(effort) is True
        assert config_module.validate_reasoning_effort("invalid") is False

    def test_validate_port(self):
        """Test port validation."""
        assert config_module.validate_port(8787) is True
        assert config_module.validate_port(1) is True
        assert config_module.validate_port(65535) is True
        assert config_module.validate_port(0) is False
        assert config_module.validate_port(65536) is False
        assert config_module.validate_port(-1) is False