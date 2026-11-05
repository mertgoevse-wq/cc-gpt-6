# cc-gpt-6

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-65通过-brightgreen.svg)](tests/)

个人工具：通过暴露一个 Anthropic 兼容的本地代理，让 **Claude Code** 在您 **已登录的 ChatGPT 会话** 中运行。

> ⚠️ **仅限个人账号使用。** 自动化 ChatGPT Web UI 可能违反 OpenAI 服务条款。这是一个个人研究工具。

## 🌐 语言

- [English](README.md)
- [Deutsch](README.de.md)
- [中文](README.zh.md) (本文件)
- [Español](README.es.md)
- [Français](README.fr.md)
- [日本語](README.ja.md)
- [한국어](README.ko.md)

---

## 工作原理

1. `cc-gpt-6 start` 读取 Chrome 的 Cookie 存储 (chatgpt.com，Windows 上使用 DPAPI) 并自动提取您的会话令牌
2. 它在 `127.0.0.1:8787` 启动一个本地 FastAPI 代理，使用 **Anthropic Messages API** 格式并转发到 ChatGPT 后端
3. 它启动 `claude` (Claude Code)，将 `ANTHROPIC_BASE_URL` 指向代理，Claude Code 以为在与 Anthropic 通信
4. 您通过 Claude Code 界面获得 **GPT-6 / o3-mini / o1 / GPT-4o** 推理能力！

## ✨ 功能特性

- 🔐 **自动令牌提取** - 从 Chrome Cookies (Windows DPAPI + AES-GCM)
- 🔄 **自动重连与令牌刷新** - 检测到 401/403/过期时自动重新提取 Cookies
- 🧠 **推理力度控制** - low/medium/high (映射到 ChatGPT 的 reasoning_effort)
- 🌍 **多语言支持** - 英语、德语、中文、西班牙语、法语、日语、韩语
- ⚙️ **持久化配置** - 语言、模型、推理力度、端口保存在 `~/.config/cc-gpt-6/`
- 🔌 **Anthropic API 兼容** - 适用于任何期望 Anthropic API 格式的工具
- 📦 **模型支持** - gpt-6, gpt-5.6, o3-mini, o1, gpt-4o

## 📋 系统要求

- **Python 3.12+**
- **Google Chrome** (已登录 https://chatgpt.com)
- **Claude Code** 已安装 (`claude` 命令在 PATH 中)
- **Windows** (用于 DPAPI Cookie 解密) - Linux/macOS 支持计划中

## 🚀 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/cc-gpt-6.git
cd cc-gpt-6

# 开发模式安装
pip install -e .

# 或使用 pipx (推荐用于 CLI 工具)
pipx install -e .
```

## 🎯 使用方法

### 首次运行 - 交互式设置

```bash
cc-gpt-6 start
```

首次运行时，会提示您选择语言：
```
欢迎使用 cc-gpt-6！

选择语言 / Select your language / Wählen Sie Ihre Sprache:
  en: English *
  de: Deutsch
  zh: 中文
  es: Español
  fr: Français
  ja: 日本語
  ko: 한국어

Enter language code (e.g., en, de, zh): zh
```

### 命令

| 命令 | 说明 |
|------|------|
| `cc-gpt-6 start` | 提取令牌、启动代理、启动 Claude Code |
| `cc-gpt-6 start --no-claude` | 仅启动代理 (不启动 Claude Code) |
| `cc-gpt-6 proxy` | 仅运行代理服务器 |
| `cc-gpt-6 extract-token` | 显示提取的 ChatGPT 会话令牌 |
| `cc-gpt-6 config` | 交互式配置 |
| `cc-gpt-6 config --show` | 显示当前配置 |
| `cc-gpt-6 config --language zh` | 设置语言为中文 |
| `cc-gpt-6 config --model gpt-6` | 设置默认模型 |
| `cc-gpt-6 config --reasoning high` | 设置推理力度 |
| `cc-gpt-6 config --port 9999` | 设置代理端口 |

### 示例工作流

```bash
# 1. 确保在 Chrome 中已登录 ChatGPT
# 2. 运行 cc-gpt-6
cc-gpt-6 start

# 3. Claude Code 启动，连接到您的 ChatGPT 会话！
#    现在可以通过 Claude Code 使用 GPT-6 / o3-mini / o1 推理
```

### 手动代理使用

```bash
# 终端 1: 启动代理
cc-gpt-6 proxy

# 终端 2: 使用任何兼容 Anthropic API 的工具
export ANTHROPIC_BASE_URL=http://127.0.0.1:8787
export ANTHROPIC_API_KEY=cc-gpt-6-dummy
claude  # 或任何其他 Anthropic API 客户端
```

## ⚙️ 配置

配置存储在 `~/.config/cc-gpt-6/config.json`：

```json
{
  "language": "zh",
  "model": "o3-mini",
  "reasoning_effort": "high",
  "port": 8787,
  "auto_launch_claude": true
}
```

### 支持的模型

| 模型 | 说明 |
|------|------|
| `gpt-6` | GPT-6 (如可用) |
| `gpt-5.6` | GPT-5.6 (如可用) |
| `o3-mini` | o3-mini 推理模型 (默认) |
| `o1` | o1 推理模型 |
| `gpt-4o` | GPT-4o |

### 推理力度级别

| 级别 | 说明 |
|------|------|
| `low` | 快速，最少推理 |
| `medium` | 平衡推理 |
| `high` | 深度推理 (默认) |

## 🔧 故障排除

### "Chrome cookie database locked"
完全关闭**所有** Chrome 窗口后重试。Chrome 运行时会锁定 Cookie 数据库。

### "No active ChatGPT session found"
1. 打开 Chrome
2. 访问 https://chatgpt.com
3. 登录您的账号
4. 再次运行 `cc-gpt-6`

### "Claude Code not found"
安装 Claude Code: https://claude.ai/code

### 使用过程中令牌过期
代理具有**自动重连守护进程**，当检测到 401/403/过期会话时，会自动从 Chrome 重新提取 Cookies。继续工作即可！

## 🏗️ 架构

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

## ⚠️ 免责声明

这是一个**个人研究工具**。请负责任地使用：
- 仅配合您自己的 ChatGPT 账号使用
- 尊重 OpenAI 的服务条款
- 如果 ChatGPT 更改 API，此工具可能停止工作
- 不提供任何担保或支持

## 📄 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)。

## 🤝 贡献

欢迎贡献！请：
1. Fork 仓库
2. 创建功能分支
3. 为新功能添加测试
4. 确保所有测试通过 (`pytest tests/ -v`)
5. 提交 PR

---

**为 AI 编程社区用 ❤️ 制作**