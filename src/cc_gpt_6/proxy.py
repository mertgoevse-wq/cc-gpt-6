"""Anthropic-compatible proxy that translates Claude Code calls to ChatGPT's conversation API.

Supports:
- /v1/messages (Anthropic Messages API format)
- /v1/models
- Streaming and non-streaming responses
- Mapping system and conversation messages
- Reasoning effort parameter (low/medium/high)
- Session token to Access Token exchange
- Auto-Reconnect & Token Refresh Guardian (re-extracts cookies on 401/403/expired)
"""

import json
import logging
import os
import sys
import time
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

logger = logging.getLogger("cc_gpt_6.proxy")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

app = FastAPI(title="cc-gpt-6 Anthropic Proxy", version="0.2.0")

CHATGPT_BASE = "https://chatgpt.com"
DEFAULT_MODEL = "o3-mini"
DEFAULT_REASONING_EFFORT = "high"

SUPPORTED_MODELS = ["gpt-6", "gpt-5.6", "o3-mini", "o1", "gpt-4o"]
REASONING_LEVELS = ["low", "medium", "high"]

CONFIG: Dict[str, Any] = {
    "session_token": None,
    "access_token": None,
    "token_expiry": 0.0,
    "model": DEFAULT_MODEL,
    "reasoning_effort": DEFAULT_REASONING_EFFORT,
}


def _try_import_extractor():
    try:
        from .token_extractor import extract_chatgpt_token
        return extract_chatgpt_token
    except Exception:
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from token_extractor import extract_chatgpt_token  # type: ignore
            return extract_chatgpt_token
        except Exception:
            return None


def set_token(session_token: str) -> None:
    """Set the session token (called from CLI)."""
    CONFIG["session_token"] = session_token
    CONFIG["access_token"] = None
    CONFIG["token_expiry"] = 0.0


def configure(
    session_token: str,
    access_token: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
) -> None:
    CONFIG["session_token"] = session_token
    CONFIG["access_token"] = access_token
    CONFIG["model"] = model if model in SUPPORTED_MODELS else DEFAULT_MODEL
    CONFIG["reasoning_effort"] = reasoning_effort if reasoning_effort in REASONING_LEVELS else DEFAULT_REASONING_EFFORT


def _is_session_expired(status_code: int, body_text: str) -> bool:
    if status_code in (401, 403):
        return True
    low = (body_text or "").lower()
    return any(k in low for k in ("session expired", "unauthorized", "invalid session", "token expired", "login required"))


async def _reextract_session_token() -> Optional[str]:
    """Re-extract session token from browser (auto-reconnect guardian)."""
    extractor = _try_import_extractor()
    if extractor is None:
        return None
    try:
        token = extractor()
        if token:
            CONFIG["session_token"] = token
            CONFIG["access_token"] = None
            CONFIG["token_expiry"] = 0.0
            logger.info("Auto-reconnect: re-extracted session token from browser")
            return token
    except Exception as exc:
        logger.warning(f"Auto-reconnect: failed to re-extract token: {exc}")
    return None


async def get_valid_access_token(force_refresh: bool = False) -> str:
    """Ensure we have a valid bearer access token from ChatGPT session."""
    if not force_refresh and CONFIG["access_token"] and time.time() < CONFIG["token_expiry"]:
        return CONFIG["access_token"]

    session_token = CONFIG.get("session_token")
    if not session_token:
        # Try to extract from browser automatically
        await _reextract_session_token()
        session_token = CONFIG.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="No session token configured in cc-gpt-6 proxy")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        ),
        "Cookie": f"__Secure-next-auth.session-token={session_token}",
        "Accept": "*/*",
    }

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(f"{CHATGPT_BASE}/api/auth/session", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("accessToken")
                if token:
                    CONFIG["access_token"] = token
                    CONFIG["token_expiry"] = time.time() + 3500
                    logger.info("Successfully refreshed ChatGPT access token via /api/auth/session")
                    return token
    except Exception as exc:
        logger.warning(f"Failed to refresh via /api/auth/session: {exc}")

    # Fallback: use session token directly as bearer
    CONFIG["access_token"] = session_token
    CONFIG["token_expiry"] = time.time() + 3600
    return session_token


def format_anthropic_messages(system_prompt: Optional[str], messages: List[Dict[str, Any]]) -> str:
    """Format Anthropic multi-turn messages into unified conversation text."""
    parts = []
    if system_prompt:
        parts.append(f"System Instructions:\n{system_prompt}\n")

    for msg in messages:
        role = msg.get("role", "user").capitalize()
        content = msg.get("content", "")
        if isinstance(content, list):
            text_blocks = []
            for b in content:
                if isinstance(b, dict):
                    if b.get("type") == "text":
                        text_blocks.append(b.get("text", ""))
                    elif b.get("type") == "tool_use":
                        text_blocks.append(f"[Tool Call: {b.get('name')}({json.dumps(b.get('input', {}))})]")
                    elif b.get("type") == "tool_result":
                        text_blocks.append(f"[Tool Result: {b.get('content', '')}]")
                elif isinstance(b, str):
                    text_blocks.append(b)
            content_str = "\n".join(text_blocks)
        else:
            content_str = str(content)

        parts.append(f"<{role}>\n{content_str}\n</{role}>")

    return "\n\n".join(parts)


@app.get("/v1/models")
async def list_models():
    """List available models in Anthropic-compatible format."""
    return {
        "data": [
            {"id": "claude-3-5-sonnet-20241022", "object": "model"},
            {"id": "claude-3-7-sonnet-20250219", "object": "model"},
            {"id": "gpt-6", "object": "model"},
            {"id": "gpt-5.6", "object": "model"},
            {"id": "o3-mini", "object": "model"},
            {"id": "o1", "object": "model"},
            {"id": "gpt-4o", "object": "model"},
        ],
        "object": "list",
    }


def _normalize_model(model: str) -> str:
    m = (model or "").lower()
    for cand in SUPPORTED_MODELS:
        if cand in m:
            return cand
    if "gpt-6" in m or "gpt6" in m or "chatgpt-6" in m:
        return "gpt-6"
    if "gpt-5.6" in m or "gpt5.6" in m:
        return "gpt-5.6"
    if "o1" in m:
        return "o1"
    if "gpt-4o" in m or "gpt4o" in m:
        return "gpt-4o"
    return "o3-mini"


async def _do_chatgpt_request(payload, req_headers):
    """Perform the conversation request; returns (status_code, lines_or_text, is_stream)."""
    async with httpx.AsyncClient(timeout=180.0) as client:
        async with client.stream("POST", f"{CHATGPT_BASE}/backend-api/conversation", headers=req_headers, json=payload) as resp:
            status = resp.status_code
            if status != 200:
                err_body = await resp.aread()
                return status, err_body.decode("utf-8", errors="replace"), False
            lines = []
            async for line in resp.aiter_lines():
                lines.append(line)
            return status, lines, True


@app.post("/v1/messages")
async def create_message(request: Request):
    """Handle Anthropic /v1/messages POST endpoint."""
    body = await request.json()
    raw_model = body.get("model", CONFIG["model"])
    model = _normalize_model(raw_model)
    system = body.get("system")
    messages = body.get("messages", [])
    stream = body.get("stream", False)

    prompt_text = format_anthropic_messages(system, messages)

    # Reasoning effort from request or config
    reasoning_effort = body.get("reasoning_effort", CONFIG.get("reasoning_effort", DEFAULT_REASONING_EFFORT))
    if reasoning_effort not in REASONING_LEVELS:
        reasoning_effort = CONFIG.get("reasoning_effort", DEFAULT_REASONING_EFFORT)

    msg_id = f"msg_{uuid.uuid4().hex[:24]}"

    async def fetch_with_guardian():
        """Returns (status, data, token) with auto-reconnect on 401/403/expired."""
        nonlocal_token = None
        for attempt in range(2):
            token = await get_valid_access_token(force_refresh=(attempt > 0))
            req_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
                ),
                "Origin": CHATGPT_BASE,
                "Referer": f"{CHATGPT_BASE}/",
                "Accept": "text/event-stream",
            }
            payload = {
                "action": "next",
                "messages": [
                    {
                        "id": str(uuid.uuid4()),
                        "author": {"role": "user"},
                        "content": {"content_type": "text", "parts": [prompt_text]},
                    }
                ],
                "parent_message_id": str(uuid.uuid4()),
                "model": model,
                "reasoning_effort": reasoning_effort,
                "timezone_offset_min": -60,
                "suggestions": [],
                "history_and_training_disabled": False,
                "conversation_mode": {"kind": "primary_assistant"},
                "force_paragen": False,
                "force_rate_limit": False,
            }
            status, data, ok = await _do_chatgpt_request(payload, req_headers)
            body_text = data if isinstance(data, str) else ""
            if _is_session_expired(status, body_text):
                logger.warning(f"Session expired / auth error (HTTP {status}); triggering auto-reconnect")
                await _reextract_session_token()
                # force refresh token next attempt
                CONFIG["access_token"] = None
                CONFIG["token_expiry"] = 0.0
                if attempt == 0:
                    continue
            return status, data, ok, req_headers, payload
        return status, data, ok, req_headers, payload

    if stream:
        async def event_generator() -> AsyncGenerator[str, None]:
            yield f"event: message_start\ndata: {json.dumps({'type': 'message_start', 'message': {'id': msg_id, 'type': 'message', 'role': 'assistant', 'content': [], 'model': model, 'stop_reason': None, 'stop_sequence': None, 'usage': {'input_tokens': len(prompt_text)//4, 'output_tokens': 1}}})}\n\n"
            yield f"event: content_block_start\ndata: {json.dumps({'type': 'content_block_start', 'index': 0, 'content_block': {'type': 'text', 'text': ''}})}\n\n"

            accumulated_text = ""
            status, data, ok, req_headers, payload = await fetch_with_guardian()

            if isinstance(data, str):
                # error body
                err_msg = f"ChatGPT API returned HTTP {status}: {data}"
                yield f"event: content_block_delta\ndata: {json.dumps({'type': 'content_block_delta', 'index': 0, 'delta': {'type': 'text_delta', 'text': err_msg}})}\n\n"
                accumulated_text += err_msg
            else:
                for line in data:
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        event_obj = json.loads(data_str)
                        message_obj = event_obj.get("message")
                        if message_obj:
                            parts = message_obj.get("content", {}).get("parts", [])
                            if parts and isinstance(parts[0], str):
                                new_full_text = parts[0]
                                if len(new_full_text) > len(accumulated_text):
                                    delta_chunk = new_full_text[len(accumulated_text):]
                                    accumulated_text = new_full_text
                                    yield f"event: content_block_delta\ndata: {json.dumps({'type': 'content_block_delta', 'index': 0, 'delta': {'type': 'text_delta', 'text': delta_chunk}})}\n\n"
                    except Exception:
                        continue

            yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': 0})}\n\n"
            yield f"event: message_delta\ndata: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': 'end_turn', 'stop_sequence': None}, 'usage': {'output_tokens': len(accumulated_text)//4}})}\n\n"
            yield f"event: message_stop\ndata: {json.dumps({'type': 'message_stop'})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    # Non-streaming response
    accumulated_text = ""
    status, data, ok, req_headers, payload = await fetch_with_guardian()
    if isinstance(data, str):
        accumulated_text = f"ChatGPT API returned HTTP {status}: {data}"
    else:
        for line in data:
            if not line or not line.startswith("data: "):
                continue
            data_str = line[6:].strip()
            if data_str == "[DONE]":
                break
            try:
                event_obj = json.loads(data_str)
                message_obj = event_obj.get("message")
                if message_obj:
                    parts = message_obj.get("content", {}).get("parts", [])
                    if parts and isinstance(parts[0], str):
                        accumulated_text = parts[0]
            except Exception:
                continue

    return JSONResponse(
        {
            "id": msg_id,
            "type": "message",
            "role": "assistant",
            "model": model,
            "content": [{"type": "text", "text": accumulated_text}],
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": len(prompt_text) // 4,
                "output_tokens": len(accumulated_text) // 4,
            },
        }
    )