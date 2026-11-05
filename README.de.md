# cc-gpt-6

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-65%20bestanden-brightgreen.svg)](tests/)

Persönliches Tool: Führt **Claude Code** mit Ihrer **eigenen eingeloggten ChatGPT-Sitzung** in Chrome aus, indem ein Anthropic-kompatibler lokaler Proxy bereitgestellt wird.

> ⚠️ **Nur mit dem eigenen Konto verwenden.** Die Automatisierung der ChatGPT-Web-UI kann gegen die Nutzungsbedingungen von OpenAI verstoßen. Dies ist ein persönliches Forschungstool.

## 🌐 Sprachen

- [English](README.md)
- [Deutsch](README.de.md) (diese Datei)
- [中文](README.zh.md)
- [Español](README.es.md)
- [Français](README.fr.md)
- [日本語](README.ja.md)
- [한국어](README.ko.md)

---

## Funktionsweise

1. `cc-gpt-6 start` liest Chromes Cookie-Speicher für chatgpt.com (DPAPI unter Windows) und extrahiert Ihren Sitzungstoken automatisch
2. Es startet einen lokalen FastAPI-Proxy auf `127.0.0.1:8787`, der die **Anthropic Messages API** spricht und an ChatGPTs Backend weiterleitet
3. Es startet `claude` (Claude Code) mit `ANTHROPIC_BASE_URL`, das auf den Proxy zeigt, sodass Claude Code glaubt, es spräche mit Anthropic
4. Sie erhalten **GPT-6 / o3-mini / o1 / GPT-4o** Reasoning über die Claude Code-Oberfläche!

## ✨ Funktionen

- 🔐 **Automatische Token-Extraktion** aus Chrome-Cookies (Windows DPAPI + AES-GCM)
- 🔄 **Auto-Reconnect & Token Refresh** - extrahiert Cookies bei 401/403/abgelaufen automatisch neu
- 🧠 **Reasoning-Aufwand steuerbar** - low/medium/high (abbildet auf ChatGPTs reasoning_effort)
- 🌍 **Mehrsprachig** - Englisch, Deutsch, Chinesisch, Spanisch, Französisch, Japanisch, Koreanisch
- ⚙️ **Persistente Konfiguration** - Sprache, Modell, Reasoning-Aufwand, Port in `~/.config/cc-gpt-6/`
- 🔌 **Anthropic API kompatibel** - funktioniert mit jedem Tool, das das Anthropic API-Format erwartet
- 📦 **Modellunterstützung** - gpt-6, gpt-5.6, o3-mini, o1, gpt-4o

## 📋 Voraussetzungen

- **Python 3.12+**
- **Google Chrome** (eingeloggt bei https://chatgpt.com)
- **Claude Code** installiert (`claude` Befehl im PATH)
- **Windows** (für DPAPI Cookie-Entschlüsselung) - Linux/macOS Support geplant

## 🚀 Installation

```bash
# Repository klonen
git clone https://github.com/yourusername/cc-gpt-6.git
cd cc-gpt-6

# Im Entwicklungsmodus installieren
pip install -e .

# Oder mit pipx (empfohlen für CLI-Tools)
pipx install -e .
```

## 🎯 Verwendung

### Erster Start - Interaktives Setup

```bash
cc-gpt-6 start
```

Beim ersten Start werden Sie aufgefordert, Ihre Sprache zu wählen:
```
Willkommen bei cc-gpt-6!

Sprache auswählen / Select your language / 选择语言:
  en: English *
  de: Deutsch
  zh: 中文
  es: Español
  fr: Français
  ja: 日本語
  ko: 한국어

Enter language code (e.g., en, de, zh): de
```

### Befehle

| Befehl | Beschreibung |
|--------|--------------|
| `cc-gpt-6 start` | Token extrahieren, Proxy starten, Claude Code starten |
| `cc-gpt-6 start --no-claude` | Nur Proxy starten (kein Claude Code) |
| `cc-gpt-6 proxy` | Nur den Proxy-Server ausführen |
| `cc-gpt-6 extract-token` | Extrahierten ChatGPT-Sitzungstoken anzeigen |
| `cc-gpt-6 config` | Interaktive Konfiguration |
| `cc-gpt-6 config --show` | Aktuelle Konfiguration anzeigen |
| `cc-gpt-6 config --language de` | Sprache auf Deutsch setzen |
| `cc-gpt-6 config --model gpt-6` | Standard-Modell setzen |
| `cc-gpt-6 config --reasoning high` | Reasoning-Aufwand setzen |
| `cc-gpt-6 config --port 9999` | Proxy-Port setzen |

### Beispiel-Workflow

```bash
# 1. Sicherstellen, dass Sie in Chrome bei ChatGPT eingeloggt sind
# 2. cc-gpt-6 starten
cc-gpt-6 start

# 3. Claude Code startet, verbunden mit Ihrer ChatGPT-Sitzung!
#    Sie können jetzt GPT-6 / o3-mini / o1 Reasoning über Claude Code nutzen
```

### Manueller Proxy-Betrieb

```bash
# Terminal 1: Proxy starten
cc-gpt-6 proxy

# Terminal 2: Mit jedem Anthropic-kompatiblen Tool nutzen
export ANTHROPIC_BASE_URL=http://127.0.0.1:8787
export ANTHROPIC_API_KEY=cc-gpt-6-dummy
claude  # oder jedes andere Anthropic API Client
```

## ⚙️ Konfiguration

Die Konfiguration wird in `~/.config/cc-gpt-6/config.json` gespeichert:

```json
{
  "language": "de",
  "model": "o3-mini",
  "reasoning_effort": "high",
  "port": 8787,
  "auto_launch_claude": true
}
```

### Unterstützte Modelle

| Modell | Beschreibung |
|--------|--------------|
| `gpt-6` | GPT-6 (falls verfügbar) |
| `gpt-5.6` | GPT-5.6 (falls verfügbar) |
| `o3-mini` | o3-mini Reasoning-Modell (Standard) |
| `o1` | o1 Reasoning-Modell |
| `gpt-4o` | GPT-4o |

### Reasoning-Aufwand

| Stufe | Beschreibung |
|-------|--------------|
| `low` | Schnell, minimales Reasoning |
| `medium` | Ausgewogenes Reasoning |
| `high` | Tiefes Reasoning (Standard) |

## 🔧 Fehlerbehebung

### "Chrome cookie database locked"
Schließen Sie **alle** Chrome-Fenster vollständig und versuchen Sie es erneut. Chrome sperrt die Cookie-Datenbank während des Betriebs.

### "No active ChatGPT session found"
1. Chrome öffnen
2. Zu https://chatgpt.com gehen
3. In Ihr Konto einloggen
4. `cc-gpt-6` erneut ausführen

### "Claude Code not found"
Claude Code installieren: https://claude.ai/code

### Token läuft während der Nutzung ab
Der Proxy hat einen **Auto-Reconnect-Guardian**, der Cookies automatisch neu aus Chrome extrahiert, wenn er 401/403/abgelaufene Sitzungen erkennt. Einfach weitermachen!

## 🏗️ Architektur

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

## ⚠️ Haftungsausschluss

Dies ist ein **persönliches Forschungstool**. Verantwortungsvoll nutzen:
- Nur mit dem eigenen ChatGPT-Konto verwenden
- OpenAIs Nutzungsbedingungen respektieren
- Dieses Tool funktioniert möglicherweise nicht mehr, wenn ChatGPT ihre API ändert
- Keine Garantie oder Support

## 📄 Lizenz

MIT-Lizenz - siehe [LICENSE](LICENSE) für Details.

## 🤝 Beitragen

Beiträge willkommen! Bitte:
1. Repository forken
2. Feature-Branch erstellen
3. Tests für neue Funktionalität hinzufügen
4. Sicherstellen, dass alle Tests bestehen (`pytest tests/ -v`)
5. PR einreichen

---

**Mit ❤️ für die KI-Coding-Community erstellt**