"""Tests for cc-gpt-6 proxy."""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cc_gpt_6.proxy import (
    app,
    configure,
    set_token,
    format_anthropic_messages,
    _normalize_model,
    SUPPORTED_MODELS,
    REASONING_LEVELS,
    CONFIG,
)


class TestProxy:
    """Test cases for proxy functions."""

    def setup_method(self):
        """Reset CONFIG before each test."""
        CONFIG.clear()
        CONFIG.update({
            "session_token": None,
            "access_token": None,
            "token_expiry": 0.0,
            "model": "o3-mini",
            "reasoning_effort": "high",
        })

    def test_configure(self):
        """Test configure function."""
        configure(
            session_token="test_session",
            access_token="test_access",
            model="gpt-6",
            reasoning_effort="medium"
        )
        assert CONFIG["session_token"] == "test_session"
        assert CONFIG["access_token"] == "test_access"
        assert CONFIG["model"] == "gpt-6"
        assert CONFIG["reasoning_effort"] == "medium"

    def test_configure_invalid_model(self):
        """Test configure with invalid model falls back to default."""
        configure(session_token="test", model="invalid-model")
        assert CONFIG["model"] == "o3-mini"

    def test_configure_invalid_reasoning(self):
        """Test configure with invalid reasoning falls back to default."""
        configure(session_token="test", reasoning_effort="invalid")
        assert CONFIG["reasoning_effort"] == "high"

    def test_set_token(self):
        """Test set_token function."""
        set_token("new_session_token")
        assert CONFIG["session_token"] == "new_session_token"
        assert CONFIG["access_token"] is None
        assert CONFIG["token_expiry"] == 0.0

    def test_format_anthropic_messages_simple(self):
        """Test formatting simple messages."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        result = format_anthropic_messages(None, messages)
        assert "<User>\nHello\n</User>" in result
        assert "<Assistant>\nHi there!\n</Assistant>" in result

    def test_format_anthropic_messages_with_system(self):
        """Test formatting with system prompt."""
        messages = [{"role": "user", "content": "Hello"}]
        result = format_anthropic_messages("You are a helpful assistant.", messages)
        assert "System Instructions:\nYou are a helpful assistant.\n" in result
        assert "<User>\nHello\n</User>" in result

    def test_format_anthropic_messages_content_blocks(self):
        """Test formatting with content blocks (tool use/result)."""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's the weather?"},
                    {"type": "tool_use", "name": "get_weather", "input": {"city": "Berlin"}},
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {"type": "tool_result", "content": "Sunny, 20°C"},
                ]
            },
        ]
        result = format_anthropic_messages(None, messages)
        assert "What's the weather?" in result
        assert "[Tool Call: get_weather(" in result
        assert "Berlin" in result
        assert "[Tool Result: Sunny, 20°C]" in result

    def test_normalize_model_exact(self):
        """Test model normalization with exact matches."""
        assert _normalize_model("gpt-6") == "gpt-6"
        assert _normalize_model("o3-mini") == "o3-mini"
        assert _normalize_model("gpt-4o") == "gpt-4o"

    def test_normalize_model_partial(self):
        """Test model normalization with partial matches."""
        assert _normalize_model("claude-3-5-sonnet") == "o3-mini"  # falls back
        assert _normalize_model("gpt-6-astra") == "gpt-6"
        assert _normalize_model("gpt6") == "gpt-6"
        assert _normalize_model("chatgpt-6") == "gpt-6"
        assert _normalize_model("gpt-5.6") == "gpt-5.6"
        assert _normalize_model("o1-preview") == "o1"
        assert _normalize_model("gpt4o") == "gpt-4o"

    def test_supported_models_list(self):
        """Test SUPPORTED_MODELS contains expected models."""
        assert "gpt-6" in SUPPORTED_MODELS
        assert "gpt-5.6" in SUPPORTED_MODELS
        assert "o3-mini" in SUPPORTED_MODELS
        assert "o1" in SUPPORTED_MODELS
        assert "gpt-4o" in SUPPORTED_MODELS

    def test_reasoning_levels(self):
        """Test REASONING_LEVELS."""
        assert REASONING_LEVELS == ["low", "medium", "high"]


class TestProxyAPI:
    """Test proxy API endpoints using TestClient."""

    def setup_method(self):
        """Reset CONFIG before each test."""
        CONFIG.clear()
        CONFIG.update({
            "session_token": "test_session_token",
            "access_token": "test_access_token",
            "token_expiry": 9999999999,  # far future
            "model": "o3-mini",
            "reasoning_effort": "high",
        })

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_list_models(self, client):
        """Test /v1/models endpoint."""
        response = client.get("/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        # Check for expected models
        model_ids = [m["id"] for m in data["data"]]
        assert "claude-3-5-sonnet-20241022" in model_ids
        assert "gpt-6" in model_ids
        assert "o3-mini" in model_ids

    def test_create_message_non_streaming(self, client):
        """Test /v1/messages non-streaming."""
        with patch("cc_gpt_6.proxy.get_valid_access_token", new_callable=AsyncMock) as mock_token:
            mock_token.return_value = "test_access_token"
            with patch("cc_gpt_6.proxy._do_chatgpt_request", new_callable=AsyncMock) as mock_request:
                # Mock successful response
                mock_request.return_value = (200, [
                    'data: {"message": {"content": {"parts": ["Hello! How can I help?"]}}}'
                ], True)

                response = client.post(
                    "/v1/messages",
                    json={
                        "model": "claude-3-5-sonnet-20241022",
                        "messages": [{"role": "user", "content": "Hello"}],
                        "stream": False
                    }
                )
                assert response.status_code == 200
                data = response.json()
                assert data["role"] == "assistant"
                assert "content" in data
                assert data["content"][0]["type"] == "text"

    def test_create_message_streaming(self, client):
        """Test /v1/messages streaming."""
        with patch("cc_gpt_6.proxy.get_valid_access_token", new_callable=AsyncMock) as mock_token:
            mock_token.return_value = "test_access_token"
            with patch("cc_gpt_6.proxy._do_chatgpt_request", new_callable=AsyncMock) as mock_request:
                mock_request.return_value = (200, [
                    'data: {"message": {"content": {"parts": ["Hello"]}}}',
                    'data: {"message": {"content": {"parts": ["Hello!"]}}}',
                    "data: [DONE]"
                ], True)

                response = client.post(
                    "/v1/messages",
                    json={
                        "model": "claude-3-5-sonnet-20241022",
                        "messages": [{"role": "user", "content": "Hello"}],
                        "stream": True
                    }
                )
                assert response.status_code == 200
                assert "text/event-stream" in response.headers.get("content-type", "")

    def test_create_message_no_token(self, client):
        """Test /v1/messages without token configured."""
        CONFIG["session_token"] = None
        CONFIG["access_token"] = None

        with patch("cc_gpt_6.proxy._reextract_session_token", new_callable=AsyncMock) as mock_extract:
            mock_extract.return_value = None

            response = client.post(
                "/v1/messages",
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "messages": [{"role": "user", "content": "Hello"}],
                }
            )
            assert response.status_code == 401
            data = response.json()
            assert "detail" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])