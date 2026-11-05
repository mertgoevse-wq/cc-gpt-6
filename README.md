# cc-gpt-6

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-65%20passing-brightgreen.svg)](tests/)

Personal tool: runs **Claude Code** against your **own logged-in ChatGPT session** in Chrome, by exposing an Anthropic-compatible local proxy.

> ⚠️ **Use only with your own account.** Automating the ChatGPT web UI may violate OpenAI's Terms of Service. This is a personal research tool.

## 🌐 Languages / 语言 / Sprachen / Idiomas / Langues / 言語 / 언어

- [English](README.md) (this file)
- [Deutsch](README.de.md)
- [中文](README.zh.md)
- [Español](README.es.md)
- [Français](README.fr.md)
- [日本語](README.ja.md)
- [한국어](README.ko.md)

---

## How it works

1. `cc-gpt-6 start` reads Chrome's cookie store for chatgpt.com (DPAPI on Windows) and extracts your session token automatically
2. It starts a local FastAPI proxy on `127.0.0.1:8787` that speaks the **Anthropic Messages API** and forwards to ChatGPT's backend
3. It launches `claude` (Claude Code) with `ANTHROPIC_BASE_URL` pointing at the proxy, so Claude Code thinks it talks to Anthropic
4. You get **GPT-6 / o3-mini / o1 / GPT-4o** reasoning through the Claude Code interface!

## ✨ Features

- 🔐 **Auto token extraction** from Chrome cookies (Windows DPAPI + AES-GCM)
- 🔄 **Auto-reconnect & token refresh** - automatically re-extracts cookies on 401/403/expired
- 🧠 **Reasoning effort control** - low/medium/high (maps to ChatGPT's reasoning_effort)
- 🌍 **Multilingual** - English, German, Chinese, Spanish, French, Japanese, Korean
- ⚙️ **Persistent config** - language, model, reasoning effort, port saved in `~/.config/cc-gpt-6/`
- 🔌 **Anthropic API compatible** - works with any tool expecting Anthropic API format
- 📦 **Model support** - gpt-6, gpt-5.6, o3-mini, o1, gpt-4o

## 📋 Requirements

- **Python 3.12+**
- **Google Chrome** (logged into https://chatgpt.com)
- **Claude Code** installed (`claude` command in PATH)
- **Windows** (for DPAPI cookie decryption) - Linux/macOS support planned

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cc-gpt-6.git
cd cc-gpt-6

# Install in development mode
pip install -e .

# Or install with pipx (recommended for CLI tools)
pipx install -e .
```

## 🎯 Usage

### First run - Interactive setup

```bash
cc-gpt-6 start
```

On first run, you'll be prompted to select your language:
```
Welcome to cc-gpt-6!

Select your language / Wählen Sie Ihre Sprache / 选择语言:
  en: English *
  de: Deutsch
  zh: 中文
  es: Español
  fr: Français
  ja: 日本語
  ko: 한국어

Enter language code (e.g., en, de, zh): de
```

### Commands

| Command | Description |
|---------|-------------|
| `cc-gpt-6 start` | Extract token, start proxy, launch Claude Code |
| `cc-gpt-6 start --no-claude` | Start proxy only (don't launch Claude Code) |
| `cc-gpt-6 proxy` | Run only the proxy server |
| `cc-gpt-6 extract-token` | Print the extracted ChatGPT session token |
| `cc-gpt-6 config` | Interactive configuration |
| `cc-gpt-6 config --show` | Show current configuration |
| `cc-gpt-6 config --language de` | Set language to German |
| `cc-gpt-6 config --model gpt-6` | Set default model |
| `cc-gpt-6 config --reasoning high` | Set reasoning effort |
| `cc-gpt-6 config --port 9999` | Set proxy port |

### Example workflow

```bash
# 1. Make sure you're logged into ChatGPT in Chrome
# 2. Run cc-gpt-6
cc-gpt-6 start

# 3. Claude Code launches, connected to your ChatGPT session!
#    You can now use GPT-6 / o3-mini / o1 reasoning through Claude Code
```

### Manual proxy usage

```bash
# Terminal 1: Start proxy
cc-gpt-6 proxy

# Terminal 2: Use with any Anthropic-compatible tool
export ANTHROPIC_BASE_URL=http://127.0.0.1:8787
export ANTHROPIC_API_KEY=cc-gpt-6-dummy
claude  # or any other Anthropic API client
```

## ⚙️ Configuration

Configuration is stored in `~/.config/cc-gpt-6/config.json`:

```json
{
  "language": "en",
  "model": "o3-mini",
  "reasoning_effort": "high",
  "port": 8787,
  "auto_launch_claude": true
}
```

### Supported Models

| Model | Description |
|-------|-------------|
| `gpt-6` | GPT-6 (if available) |
| `gpt-5.6` | GPT-5.6 (if available) |
| `o3-mini` | o3-mini reasoning model (default) |
| `o1` | o1 reasoning model |
| `gpt-4o` | GPT-4o |

### Reasoning Effort Levels

| Level | Description |
|-------|-------------|
| `low` | Fast, minimal reasoning |
| `medium` | Balanced reasoning |
| `high` | Deep reasoning (default) |

## 🔧 Troubleshooting

### "Chrome cookie database locked"
Close **all** Chrome windows completely and try again. Chrome locks the cookie database while running.

### "No active ChatGPT session found"
1. Open Chrome
2. Go to https://chatgpt.com
3. Log in to your account
4. Run `cc-gpt-6` again

### "Claude Code not found"
Install Claude Code: https://claude.ai/code

### Token expires during use
The proxy has an **auto-reconnect guardian** that automatically re-extracts cookies from Chrome when it detects 401/403/expired sessions. Just continue working!

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Claude     │────▶│  cc-gpt-6    │────▶│  ChatGPT        │
│  Code       │     │  Proxy       │     │  Backend API    │
│  (Anthropic │     │  :8787       │     │  (conversation) │
│   API)      │     │              │     │                 │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Chrome      │
                    │  Cookies     │
                    │  (DPAPI)     │
                    └──────────────┘
```

## ⚠️ Disclaimer

This is a **personal research tool**. Use responsibly:
- Only use with your own ChatGPT account
- Respect OpenAI's Terms of Service
- This tool may stop working if ChatGPT changes their API
- No warranty or support provided

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass (`pytest tests/ -v`)
5. Submit a PR

---

**Made with ❤️ for the AI coding community**