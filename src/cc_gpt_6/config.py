"""Configuration management for cc-gpt-6."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .i18n import DEFAULT_LANG, SUPPORTED_LANGUAGES


CONFIG_DIR = Path.home() / ".config" / "cc-gpt-6"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "language": DEFAULT_LANG,
    "model": "o3-mini",
    "reasoning_effort": "high",
    "port": 8787,
    "auto_launch_claude": True,
}


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load configuration from file, merging with defaults."""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            # Merge with defaults (user config takes precedence)
            config = DEFAULT_CONFIG.copy()
            config.update(user_config)
            return config
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except OSError as e:
        raise RuntimeError(f"Failed to save config: {e}")


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a single configuration value."""
    config = load_config()
    return config.get(key, default)


def set_config_value(key: str, value: Any) -> None:
    """Set a single configuration value."""
    config = load_config()
    config[key] = value
    save_config(config)


def reset_config() -> None:
    """Reset configuration to defaults."""
    save_config(DEFAULT_CONFIG.copy())


def validate_language(lang: str) -> bool:
    """Validate a language code."""
    return lang in SUPPORTED_LANGUAGES


def validate_model(model: str) -> bool:
    """Validate a model name."""
    from .proxy import SUPPORTED_MODELS
    return model in SUPPORTED_MODELS


def validate_reasoning_effort(effort: str) -> bool:
    """Validate a reasoning effort level."""
    from .proxy import REASONING_LEVELS
    return effort in REASONING_LEVELS


def validate_port(port: int) -> bool:
    """Validate a port number."""
    return 1 <= port <= 65535