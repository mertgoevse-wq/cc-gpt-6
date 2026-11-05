"""Tests for cc-gpt-6 CLI."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cc_gpt_6.cli import (
    cmd_extract_token,
    cmd_proxy,
    cmd_start,
    cmd_config,
    run_first_time_setup,
    run_interactive_config,
)
from cc_gpt_6.config import load_config, save_config, DEFAULT_CONFIG


class TestCLI:
    """Test cases for CLI commands."""

    def setup_method(self):
        """Reset config before each test."""
        # Use a temp config file
        import cc_gpt_6.config as config_module
        config_module.CONFIG_FILE = Path(tempfile.mkdtemp()) / "config.json"
        config_module.CONFIG_DIR = config_module.CONFIG_FILE.parent
        save_config(DEFAULT_CONFIG.copy())

    def test_cmd_extract_token_success(self):
        """Test extract-token command success."""
        with patch("cc_gpt_6.cli.extract_chatgpt_token", return_value="test_token"):
            # Capture stdout
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                result = cmd_extract_token(MagicMock())
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
            assert result == 0
            assert "test_token" in output

    def test_cmd_extract_token_file_not_found(self):
        """Test extract-token with Chrome not found/locked."""
        with patch("cc_gpt_6.cli.extract_chatgpt_token", side_effect=FileNotFoundError("locked")):
            import io
            import sys
            old_stderr = sys.stderr
            sys.stderr = io.StringIO()
            try:
                result = cmd_extract_token(MagicMock())
                output = sys.stderr.getvalue()
            finally:
                sys.stderr = old_stderr
            assert result == 1
            assert "locked" in output.lower() or "chrome" in output.lower()

    def test_cmd_config_show(self):
        """Test config --show."""
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            args = MagicMock()
            args.show = True
            args.reset = False
            args.language = None
            args.model = None
            args.reasoning = None
            args.port = None
            result = cmd_config(args)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        assert result == 0
        assert "Language" in output or "Sprache" in output

    def test_cmd_config_reset(self):
        """Test config --reset."""
        # First modify config
        save_config({"language": "de", "model": "gpt-6"})
        args = MagicMock()
        args.show = False
        args.reset = True
        args.language = None
        args.model = None
        args.reasoning = None
        args.port = None
        result = cmd_config(args)
        assert result == 0
        config = load_config()
        assert config["language"] == DEFAULT_CONFIG["language"]
        assert config["model"] == DEFAULT_CONFIG["model"]

    def test_cmd_config_set_language(self):
        """Test config --language."""
        args = MagicMock()
        args.show = False
        args.reset = False
        args.language = "de"
        args.model = None
        args.reasoning = None
        args.port = None
        result = cmd_config(args)
        assert result == 0
        config = load_config()
        assert config["language"] == "de"

    def test_cmd_config_invalid_language(self):
        """Test config with invalid language."""
        args = MagicMock()
        args.show = False
        args.reset = False
        args.language = "invalid_lang"
        args.model = None
        args.reasoning = None
        args.port = None
        result = cmd_config(args)
        assert result == 1

    def test_cmd_config_set_model(self):
        """Test config --model."""
        args = MagicMock()
        args.show = False
        args.reset = False
        args.language = None
        args.model = "gpt-6"
        args.reasoning = None
        args.port = None
        result = cmd_config(args)
        assert result == 0
        config = load_config()
        assert config["model"] == "gpt-6"

    def test_cmd_config_invalid_model(self):
        """Test config with invalid model."""
        args = MagicMock()
        args.show = False
        args.reset = False
        args.language = None
        args.model = "invalid-model"
        args.reasoning = None
        args.port = None
        result = cmd_config(args)
        assert result == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])