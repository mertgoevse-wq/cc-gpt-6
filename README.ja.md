# cc-gpt-6

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-65合格-brightgreen.svg)](tests/)

個人ツール：お使いの **ログイン済み ChatGPT セッション** を Chrome で使用し、Anthropic 互換のローカルプロキシを公開することで **Claude Code** を実行します。

> ⚠️ **自身のアカウントでのみ使用してください。** ChatGPT Web UI の自動化は OpenAI の利用規約に違反する可能性があります。これは個人研究用ツールです。

## 🌐 言語

- [English](README.md)
- [Deutsch](README.de.md)
- [中文](README.zh.md)
- [Español](README.es.md)
- [Français](README.fr.md)
- [日本語](README.ja.md) (このファイル)
- [한국어](README.ko.md)

---

## 仕組み

1. `cc-gpt-6 start` が Chrome の Cookie ストレージ (chatgpt.com、Windows では DPAPI) を読み取り、セッショントークンを自動抽出
2. `127.0.0.1:8787` でローカル FastAPI プロキシを起動、**Anthropic Messages API** 形式で ChatGPT バックエンドに転送
3. `claude` (Claude Code) を `ANTHROPIC_BASE_URL` をプロキシに向けて起動、Claude Code は Anthropic と通信していると認識
4. **GPT-6 / o3-mini / o1 / GPT-4o** の推論を Claude Code インターフェースで利用可能！

## ✨ 機能

- 🔐 **自動トークン抽出** - Chrome Cookies から (Windows DPAPI + AES-GCM)
- 🔄 **自動再接続・トークンリフレッシュ** - 401/403/期限切れ検出時に Cookies を自動再抽出
- 🧠 **推論努力制御** - low/medium/high (ChatGPT の reasoning_effort にマッピング)
- 🌍 **多言語対応** - 英語、ドイツ語、中国語、スペイン語、フランス語、日本語、韓国語
- ⚙️ **永続設定** - 言語、モデル、推論努力、ポートを `~/.config/cc-gpt-6/` に保存
- 🔌 **Anthropic API 互換** - Anthropic API 形式を期待するあらゆるツールで動作
- 📦 **モデル対応** - gpt-6, gpt-5.6, o3-mini, o1, gpt-4o

## 📋 必要条件

- **Python 3.12+**
- **Google Chrome** (https://chatgpt.com にログイン済み)
- **Claude Code** インストール済み (`claude` コマンドが PATH にあること)
- **Windows** (DPAPI Cookie 復号用) - Linux/macOS 対応予定

## 🚀 インストール

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/cc-gpt-6.git
cd cc-gpt-6

# 開発モードでインストール
pip install -e .

# または pipx で (CLI ツールには推奨)
pipx install -e .
```

## 🎯 使い方

### 初回実行 - インタラクティブセットアップ

```bash
cc-gpt-6 start
```

初回起動時、言語選択を求められます：
```
cc-gpt-6 へようこそ！

言語を選択 / Select your language / Wählen Sie Ihre Sprache:
  en: English *
  de: Deutsch
  zh: 中文
  es: Español
  fr: Français
  ja: 日本語
  ko: 한국어

Enter language code (e.g., en, de, zh): ja
```

### コマンド

| コマンド | 説明 |
|----------|------|
| `cc-gpt-6 start` | トークン抽出、プロキシ起動、Claude Code 起動 |
| `cc-gpt-6 start --no-claude` | プロキシのみ起動 (Claude Code 起動なし) |
| `cc-gpt-6 proxy` | プロキシサーバーのみ実行 |
| `cc-gpt-6 extract-token` | 抽出された ChatGPT セッショントークンを表示 |
| `cc-gpt-6 config` | インタラクティブ設定 |
| `cc-gpt-6 config --show` | 現在の設定を表示 |
| `cc-gpt-6 config --language ja` | 言語を日本語に設定 |
| `cc-gpt-6 config --model gpt-6` | デフォルトモデルを設定 |
| `cc-gpt-6 config --reasoning high` | 推論努力を設定 |
| `cc-gpt-6 config --port 9999` | プロキシポートを設定 |

### ワークフロー例

```bash
# 1. Chrome で ChatGPT にログイン済みであることを確認
# 2. cc-gpt-6 実行
cc-gpt-6 start

# 3. Claude Code 起動、お使いの ChatGPT セッションに接続！
#    これで GPT-6 / o3-mini / o1 推論を Claude Code で利用可能
```

### 手動プロキシ使用

```bash
# ターミナル 1: プロキシ起動
cc-gpt-6 proxy

# ターミナル 2: Anthropic 互換ツールで使用
export ANTHROPIC_BASE_URL=http://127.0.0.1:8787
export ANTHROPIC_API_KEY=cc-gpt-6-dummy
claude  # または他の Anthropic API クライアント
```

## ⚙️ 設定

設定は `~/.config/cc-gpt-6/config.json` に保存：

```json
{
  "language": "ja",
  "model": "o3-mini",
  "reasoning_effort": "high",
  "port": 8787,
  "auto_launch_claude": true
}
```

### 対応モデル

| モデル | 説明 |
|--------|------|
| `gpt-6` | GPT-6 (利用可能な場合) |
| `gpt-5.6` | GPT-5.6 (利用可能な場合) |
| `o3-mini` | o3-mini 推論モデル (デフォルト) |
| `o1` | o1 推論モデル |
| `gpt-4o` | GPT-4o |

### 推論努力レベル

| レベル | 説明 |
|--------|------|
| `low` | 高速、最小限の推論 |
| `medium` | バランスの取れた推論 |
| `high` | 深い推論 (デフォルト) |

## 🔧 トラブルシューティング

### "Chrome cookie database locked"
**すべての** Chrome ウィンドウを完全に閉じてから再試行。Chrome 実行中は Cookie データベースがロックされます。

### "No active ChatGPT session found"
1. Chrome を開く
2. https://chatgpt.com にアクセス
3. アカウントにログイン
4. `cc-gpt-6` を再実行

### "Claude Code not found"
Claude Code をインストール: https://claude.ai/code

### 使用中にトークンが期限切れ
プロキシには**自動再接続ガーディアン**があり、401/403/期限切れセッション検出時に Chrome から自動的に Cookies を再抽出。そのまま作業を継続！

## 🏗️ アーキテクチャ

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

## ⚠️ 免責事項

これは**個人研究ツール**です。責任を持って使用してください：
- 自身の ChatGPT アカウントでのみ使用
- OpenAI の利用規約を尊重
- ChatGPT が API を変更すると動作しなくなる可能性があります
- 保証やサポートは提供されません

## 📄 ライセンス

MIT ライセンス - 詳細は [LICENSE](LICENSE) を参照。

## 🤝 貢献

貢献を歓迎します！以下の手順で：
1. リポジトリをフォーク
2. 機能ブランチを作成
3. 新機能のテストを追加
4. すべてのテストが通ることを確認 (`pytest tests/ -v`)
5. PR を送信

---

**AI コーディングコミュニティのために ❤️ を込めて作成**