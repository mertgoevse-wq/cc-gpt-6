"""Tests for cc-gpt-6 token extractor."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cc_gpt_6.token_extractor import (
    get_chrome_user_data_dir,
    get_chrome_cookie_db_path,
    dpapi_decrypt,
    aes_gcm_decrypt,
    get_chrome_aes_key,
    extract_chatgpt_cookies,
    extract_chatgpt_cookies_from_profile,
    extract_chatgpt_token,
)


class TestTokenExtractor:
    """Test cases for token extractor functions."""

    def test_get_chrome_user_data_dir(self):
        """Test getting Chrome user data directory."""
        with patch.dict(os.environ, {"LOCALAPPDATA": r"C:\Users\Test\AppData\Local"}):
            result = get_chrome_user_data_dir()
            expected = Path(r"C:\Users\Test\AppData\Local\Google\Chrome\User Data")
            assert result == expected

    def test_get_chrome_user_data_dir_missing_env(self):
        """Test error when LOCALAPPDATA is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="LOCALAPPDATA"):
                get_chrome_user_data_dir()

    def test_get_chrome_cookie_db_path_network(self):
        """Test cookie DB path for Chrome 110+ (Network/Cookies)."""
        with patch("cc_gpt_6.token_extractor.get_chrome_user_data_dir") as mock_dir:
            mock_dir.return_value = Path(r"C:\Chrome\User Data")
            with patch("pathlib.Path.exists", return_value=True):
                result = get_chrome_cookie_db_path()
                expected = Path(r"C:\Chrome\User Data\Default\Network\Cookies")
                assert result == expected

    def test_get_chrome_cookie_db_path_legacy(self):
        """Test cookie DB path for legacy Chrome (Cookies)."""
        with patch("cc_gpt_6.token_extractor.get_chrome_user_data_dir") as mock_dir:
            mock_dir.return_value = Path(r"C:\Chrome\User Data")
            # First path doesn't exist, second does
            with patch("pathlib.Path.exists", side_effect=[False, True]):
                result = get_chrome_cookie_db_path()
                expected = Path(r"C:\Chrome\User Data\Default\Cookies")
                assert result == expected

    @patch("cc_gpt_6.token_extractor.get_chrome_user_data_dir")
    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_get_chrome_aes_key(self, mock_exists, mock_read_text, mock_dir):
        """Test extracting Chrome AES key."""
        mock_dir.return_value = Path(r"C:\Chrome\User Data")
        mock_exists.return_value = True  # Local State file exists
        mock_read_text.return_value = '{"os_crypt": {"encrypted_key": "RGFQSQAAAAAAAA=="}}'
        with patch("base64.b64decode", return_value=b"DPAPI\x00\x00\x00\x00"):
            with patch("cc_gpt_6.token_extractor.dpapi_decrypt", return_value=b"test_key_32_bytes_long_1234567890"):
                key = get_chrome_aes_key()
                assert key == b"test_key_32_bytes_long_1234567890"

    @patch("cc_gpt_6.token_extractor.get_chrome_user_data_dir")
    def test_get_chrome_aes_key_missing_file(self, mock_dir):
        """Test error when Local State file is missing."""
        mock_dir.return_value = Path(r"C:\Chrome\User Data")
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Local State"):
                get_chrome_aes_key()

    @patch("cc_gpt_6.token_extractor.get_chrome_aes_key")
    @patch("cc_gpt_6.token_extractor.get_chrome_cookie_db_path")
    @patch("shutil.copy2")
    @patch("sqlite3.connect")
    @patch("tempfile.mkdtemp")
    @patch("shutil.rmtree")
    @patch("pathlib.Path.exists")
    def test_extract_chatgpt_cookies_v10(
        self, mock_exists, mock_rmtree, mock_mkdtemp, mock_connect, mock_copy2, mock_db_path, mock_aes_key
    ):
        """Test extracting v10 encrypted cookies."""
        mock_aes_key.return_value = b"x" * 32
        mock_db_path.return_value = Path(r"C:\Chrome\User Data\Default\Network\Cookies")
        mock_exists.return_value = True  # Path exists
        mock_mkdtemp.return_value = r"C:\Temp\cc_gpt_xyz"
        mock_copy2.return_value = None

        # Mock cursor with v10 encrypted cookie
        mock_cursor = MagicMock()
        # v10 prefix + 12-byte nonce + ciphertext+tag
        enc_val = b"v10" + b"x" * 12 + b"ciphertext_tag"
        mock_cursor.fetchall.return_value = [
            ("__Secure-next-auth.session-token", enc_val),
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        with patch("cc_gpt_6.token_extractor.aes_gcm_decrypt", return_value=b"test_token_value"):
            cookies = extract_chatgpt_cookies()

        assert "__Secure-next-auth.session-token" in cookies
        assert cookies["__Secure-next-auth.session-token"] == "test_token_value"

    @patch("cc_gpt_6.token_extractor.get_chrome_aes_key")
    @patch("cc_gpt_6.token_extractor.get_chrome_cookie_db_path")
    @patch("shutil.copy2")
    @patch("sqlite3.connect")
    @patch("tempfile.mkdtemp")
    @patch("shutil.rmtree")
    @patch("pathlib.Path.exists")
    def test_extract_chatgpt_cookies_dpapi(
        self, mock_exists, mock_rmtree, mock_mkdtemp, mock_connect, mock_copy2, mock_db_path, mock_aes_key
    ):
        """Test extracting DPAPI encrypted cookies (older format)."""
        mock_aes_key.return_value = b"x" * 32
        mock_db_path.return_value = Path(r"C:\Chrome\User Data\Default\Cookies")
        mock_exists.return_value = True  # Path exists
        mock_mkdtemp.return_value = r"C:\Temp\cc_gpt_xyz"
        mock_copy2.return_value = None

        mock_cursor = MagicMock()
        # DPAPI encrypted (no v10/v11 prefix)
        enc_val = b"dpapi_encrypted_data"
        mock_cursor.fetchall.return_value = [
            ("session-token", enc_val),
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        with patch("cc_gpt_6.token_extractor.dpapi_decrypt", return_value=b"dpapi_token_value"):
            cookies = extract_chatgpt_cookies()

        assert "session-token" in cookies
        assert cookies["session-token"] == "dpapi_token_value"

    @patch("cc_gpt_6.token_extractor.extract_chatgpt_cookies")
    def test_extract_chatgpt_token_from_env(self, mock_extract):
        """Test token extraction from environment variable."""
        with patch.dict(os.environ, {"CHATGPT_TOKEN": "env_token_123"}):
            token = extract_chatgpt_token()
            assert token == "env_token_123"
            mock_extract.assert_not_called()

    @patch("cc_gpt_6.token_extractor.extract_chatgpt_cookies_from_profile")
    def test_extract_chatgpt_token_from_cookies(self, mock_extract):
        """Test token extraction from cookies."""
        mock_extract.return_value = {
            "__Secure-next-auth.session-token": "cookie_token_456"
        }
        with patch.dict(os.environ, {}, clear=True):
            token = extract_chatgpt_token()
            assert token == "cookie_token_456"

    @patch("cc_gpt_6.token_extractor.extract_chatgpt_cookies_from_profile")
    def test_extract_chatgpt_token_split(self, mock_extract):
        """Test token extraction from split cookies."""
        mock_extract.return_value = {
            "__Secure-next-auth.session-token.0": "part1_",
            "__Secure-next-auth.session-token.1": "part2",
        }
        with patch.dict(os.environ, {}, clear=True):
            token = extract_chatgpt_token()
            assert token == "part1_part2"

    @patch("cc_gpt_6.token_extractor.extract_chatgpt_cookies_from_profile")
    def test_extract_chatgpt_token_no_cookies(self, mock_extract):
        """Test error when no cookies found."""
        mock_extract.return_value = {}
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="No ChatGPT/OpenAI cookies found"):
                extract_chatgpt_token()

    @patch("cc_gpt_6.token_extractor.extract_chatgpt_cookies_from_profile")
    def test_extract_chatgpt_token_no_session_token(self, mock_extract):
        """Test error when cookies exist but no session token."""
        mock_extract.return_value = {"some_other_cookie": "value"}
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="No active ChatGPT session token"):
                extract_chatgpt_token()


class TestConfig:
    """Tests for configuration management."""

    def test_load_config_defaults(self):
        """Test loading default configuration."""
        from cc_gpt_6.config import load_config, DEFAULT_CONFIG
        with patch("pathlib.Path.exists", return_value=False):
            config = load_config()
            assert config == DEFAULT_CONFIG

    def test_validate_language(self):
        """Test language validation."""
        from cc_gpt_6.config import validate_language
        assert validate_language("en") is True
        assert validate_language("de") is True
        assert validate_language("zh") is True
        assert validate_language("invalid") is False

    def test_validate_model(self):
        """Test model validation."""
        from cc_gpt_6.config import validate_model
        assert validate_model("o3-mini") is True
        assert validate_model("gpt-6") is True
        assert validate_model("gpt-4o") is True
        assert validate_model("invalid-model") is False

    def test_validate_reasoning_effort(self):
        """Test reasoning effort validation."""
        from cc_gpt_6.config import validate_reasoning_effort
        assert validate_reasoning_effort("low") is True
        assert validate_reasoning_effort("medium") is True
        assert validate_reasoning_effort("high") is True
        assert validate_reasoning_effort("invalid") is False

    def test_validate_port(self):
        """Test port validation."""
        from cc_gpt_6.config import validate_port
        assert validate_port(8787) is True
        assert validate_port(1) is True
        assert validate_port(65535) is True
        assert validate_port(0) is False
        assert validate_port(65536) is False
        assert validate_port(-1) is False


class TestI18n:
    """Tests for internationalization."""

    def test_set_language(self):
        """Test setting language."""
        from cc_gpt_6.i18n import set_language, get_language, DEFAULT_LANG
        assert set_language("de") is True
        assert get_language() == "de"
        assert set_language("invalid") is False
        assert get_language() == "de"  # unchanged
        # Reset
        set_language(DEFAULT_LANG)

    def test_get_lang_name(self):
        """Test getting language display name."""
        from cc_gpt_6.i18n import get_lang_name
        assert get_lang_name("en") == "English"
        assert get_lang_name("de") == "Deutsch"
        assert get_lang_name("zh") == "中文"
        assert get_lang_name("invalid") == "invalid"

    def test_t_translation(self):
        """Test translation function."""
        from cc_gpt_6.i18n import set_language, t
        set_language("en")
        assert t("welcome") == "Welcome to cc-gpt-6!"
        set_language("de")
        assert t("welcome") == "Willkommen bei cc-gpt-6!"
        set_language("zh")
        assert t("welcome") == "欢迎使用 cc-gpt-6！"
        # Reset
        set_language("en")

    def test_t_formatting(self):
        """Test translation with formatting."""
        from cc_gpt_6.i18n import set_language, t
        set_language("en")
        result = t("language_selected", lang="Deutsch")
        assert result == "Language set to Deutsch"
        set_language("de")
        result = t("language_selected", lang="English")
        assert result == "Sprache auf English gesetzt"
        set_language("en")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])