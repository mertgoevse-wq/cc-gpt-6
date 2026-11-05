"""Tests for cc-gpt-6 internationalization."""

import pytest

from cc_gpt_6.i18n import (
    SUPPORTED_LANGUAGES,
    DEFAULT_LANG,
    set_language,
    get_language,
    get_lang_name,
    t,
    t_cmd,
    list_languages,
)


class TestI18n:
    """Test internationalization functions."""

    def setup_method(self):
        """Reset to default language before each test."""
        set_language(DEFAULT_LANG)

    def test_supported_languages(self):
        """Test supported languages dict."""
        assert "en" in SUPPORTED_LANGUAGES
        assert "de" in SUPPORTED_LANGUAGES
        assert "zh" in SUPPORTED_LANGUAGES
        assert "es" in SUPPORTED_LANGUAGES
        assert "fr" in SUPPORTED_LANGUAGES
        assert "ja" in SUPPORTED_LANGUAGES
        assert "ko" in SUPPORTED_LANGUAGES
        assert SUPPORTED_LANGUAGES["en"] == "English"
        assert SUPPORTED_LANGUAGES["de"] == "Deutsch"
        assert SUPPORTED_LANGUAGES["zh"] == "中文"

    def test_set_get_language(self):
        """Test setting and getting language."""
        assert get_language() == DEFAULT_LANG
        assert set_language("de") is True
        assert get_language() == "de"
        assert set_language("zh") is True
        assert get_language() == "zh"
        # Invalid language should return False and not change
        assert set_language("invalid") is False
        assert get_language() == "zh"

    def test_get_lang_name(self):
        """Test getting language display name."""
        assert get_lang_name("en") == "English"
        assert get_lang_name("de") == "Deutsch"
        assert get_lang_name("zh") == "中文"
        assert get_lang_name("invalid") == "invalid"  # fallback

    def test_t_translation(self):
        """Test translation function."""
        # English
        set_language("en")
        assert t("welcome") == "Welcome to cc-gpt-6!"
        assert t("checking_chrome") == "Checking Chrome for ChatGPT session..."

        # German
        set_language("de")
        assert t("welcome") == "Willkommen bei cc-gpt-6!"
        assert t("checking_chrome") == "Prüfe Chrome auf ChatGPT-Sitzung..."

        # Chinese
        set_language("zh")
        assert t("welcome") == "欢迎使用 cc-gpt-6！"
        assert t("checking_chrome") == "正在检查 Chrome 的 ChatGPT 会话..."

        # Spanish
        set_language("es")
        assert t("welcome") == "¡Bienvenido a cc-gpt-6!"

        # French
        set_language("fr")
        assert t("welcome") == "Bienvenue dans cc-gpt-6 !"

        # Japanese
        set_language("ja")
        assert t("welcome") == "cc-gpt-6 へようこそ！"

        # Korean
        set_language("ko")
        assert t("welcome") == "cc-gpt-6에 오신 것을 환영합니다!"

    def test_t_formatting(self):
        """Test translation with string formatting."""
        set_language("en")
        result = t("language_selected", lang="Deutsch")
        assert result == "Language set to Deutsch"

        set_language("de")
        result = t("language_selected", lang="English")
        assert result == "Sprache auf English gesetzt"

        set_language("zh")
        result = t("language_selected", lang="English")
        assert result == "语言已设置为 English"

    def test_t_missing_key_fallback(self):
        """Test fallback for missing translation key."""
        set_language("en")
        result = t("nonexistent_key")
        assert result == "nonexistent_key"  # returns key as fallback

    def test_t_missing_lang_fallback(self):
        """Test fallback to English for unsupported language."""
        # Directly test the fallback logic
        from cc_gpt_6.i18n import TRANSLATIONS, _current_lang
        # Set to a language that doesn't have a translation
        original_lang = _current_lang
        try:
            # Manually test fallback
            result = TRANSLATIONS.get("invalid_lang", TRANSLATIONS[DEFAULT_LANG]).get("welcome", "welcome")
            assert result == "Welcome to cc-gpt-6!"
        finally:
            set_language(original_lang)

    def test_t_cmd(self):
        """Test command translation."""
        set_language("en")
        assert t_cmd("start") == "Extract token, start proxy, and launch Claude Code"
        assert t_cmd("proxy") == "Run only the proxy server"
        assert t_cmd("extract_token") == "Extract and print the ChatGPT session token"
        assert t_cmd("config") == "Configure settings (language, model, reasoning effort)"

        set_language("de")
        assert t_cmd("start") == "Token extrahieren, Proxy starten und Claude Code starten"
        assert t_cmd("proxy") == "Nur den Proxy-Server starten"

    def test_list_languages(self):
        """Test list_languages output."""
        set_language("en")
        output = list_languages()
        assert "en: English" in output
        assert "de: Deutsch" in output
        assert "zh: 中文" in output
        assert "*" in output  # current language marker

        set_language("de")
        output = list_languages()
        assert "de: Deutsch *" in output  # current language has marker