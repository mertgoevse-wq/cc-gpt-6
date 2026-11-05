# cc-gpt-6

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-65%20réussis-brightgreen.svg)](tests/)

Outil personnel : exécute **Claude Code** avec votre **propre session ChatGPT connectée** dans Chrome, en exposant un proxy local compatible avec l'API Anthropic.

> ⚠️ **À utiliser uniquement avec votre propre compte.** L'automatisation de l'interface web de ChatGPT peut violer les Conditions d'Utilisation d'OpenAI. Ceci est un outil de recherche personnel.

## 🌐 Langues

- [English](README.md)
- [Deutsch](README.de.md)
- [中文](README.zh.md)
- [Español](README.es.md)
- [Français](README.fr.md) (ce fichier)
- [日本語](README.ja.md)
- [한국어](README.ko.md)

---

## Fonctionnement

1. `cc-gpt-6 start` lit le stockage de cookies de Chrome pour chatgpt.com (DPAPI sur Windows) et extrait automatiquement votre jeton de session
2. Il démarre un proxy FastAPI local sur `127.0.0.1:8787` qui parle l'**API Messages d'Anthropic** et transmet au backend de ChatGPT
3. Il lance `claude` (Claude Code) avec `ANTHROPIC_BASE_URL` pointant vers le proxy, donc Claude Code pense qu'il parle à Anthropic
4. Vous obtenez le raisonnement **GPT-6 / o3-mini / o1 / GPT-4o** via l'interface de Claude Code !

## ✨ Fonctionnalités

- 🔐 **Extraction automatique du jeton** depuis les cookies Chrome (Windows DPAPI + AES-GCM)
- 🔄 **Reconnexion auto et rafraîchissement du jeton** - ré-extrait les cookies automatiquement sur 401/403/expiré
- 🧠 **Contrôle de l'effort de raisonnement** - low/medium/high (correspond à reasoning_effort de ChatGPT)
- 🌍 **Multilingue** - Anglais, Allemand, Chinois, Espagnol, Français, Japonais, Coréen
- ⚙️ **Configuration persistante** - langue, modèle, effort de raisonnement, port sauvés dans `~/.config/cc-gpt-6/`
- 🔌 **Compatible API Anthropic** - fonctionne avec tout outil attendant le format API d'Anthropic
- 📦 **Support des modèles** - gpt-6, gpt-5.6, o3-mini, o1, gpt-4o

## 📋 Prérequis

- **Python 3.12+**
- **Google Chrome** (connecté à https://chatgpt.com)
- **Claude Code** installé (`claude` dans PATH)
- **Windows** (pour le déchiffrement DPAPI des cookies) - Support Linux/macOS prévu

## 🚀 Installation

```bash
# Cloner le dépôt
git clone https://github.com/yourusername/cc-gpt-6.git
cd cc-gpt-6

# Installer en mode développement
pip install -e .

# Ou avec pipx (recommandé pour les outils CLI)
pipx install -e .
```

## 🎯 Utilisation

### Première exécution - Configuration interactive

```bash
cc-gpt-6 start
```

Au premier lancement, on vous demandera de choisir votre langue :
```
Bienvenue dans cc-gpt-6 !

Sélectionnez votre langue / Select your language / Wählen Sie Ihre Sprache:
  en: English *
  de: Deutsch
  zh: 中文
  es: Español
  fr: Français
  ja: 日本語
  ko: 한국어

Enter language code (e.g., en, de, zh): fr
```

### Commandes

| Commande | Description |
|----------|-------------|
| `cc-gpt-6 start` | Extraire le jeton, démarrer le proxy, lancer Claude Code |
| `cc-gpt-6 start --no-claude` | Démarrer seulement le proxy (ne pas lancer Claude Code) |
| `cc-gpt-6 proxy` | Exécuter seulement le serveur proxy |
| `cc-gpt-6 extract-token` | Afficher le jeton de session ChatGPT extrait |
| `cc-gpt-6 config` | Configuration interactive |
| `cc-gpt-6 config --show` | Afficher la configuration actuelle |
| `cc-gpt-6 config --language fr` | Définir la langue sur français |
| `cc-gpt-6 config --model gpt-6` | Définir le modèle par défaut |
| `cc-gpt-6 config --reasoning high` | Définir l'effort de raisonnement |
| `cc-gpt-6 config --port 9999` | Définir le port du proxy |

### Exemple de flux de travail

```bash
# 1. Assurez-vous d'être connecté à ChatGPT dans Chrome
# 2. Lancez cc-gpt-6
cc-gpt-6 start

# 3. Claude Code démarre, connecté à votre session ChatGPT !
#    Vous pouvez maintenant utiliser le raisonnement GPT-6 / o3-mini / o1 via Claude Code
```

### Utilisation manuelle du proxy

```bash
# Terminal 1: Démarrer le proxy
cc-gpt-6 proxy

# Terminal 2: Utiliser avec n'importe quel outil compatible Anthropic
export ANTHROPIC_BASE_URL=http://127.0.0.1:8787
export ANTHROPIC_API_KEY=cc-gpt-6-dummy
claude  # ou tout autre client API Anthropic
```

## ⚙️ Configuration

La configuration est stockée dans `~/.config/cc-gpt-6/config.json` :

```json
{
  "language": "fr",
  "model": "o3-mini",
  "reasoning_effort": "high",
  "port": 8787,
  "auto_launch_claude": true
}
```

### Modèles supportés

| Modèle | Description |
|--------|-------------|
| `gpt-6` | GPT-6 (si disponible) |
| `gpt-5.6` | GPT-5.6 (si disponible) |
| `o3-mini` | Modèle de raisonnement o3-mini (défaut) |
| `o1` | Modèle de raisonnement o1 |
| `gpt-4o` | GPT-4o |

### Niveaux d'effort de raisonnement

| Niveau | Description |
|--------|-------------|
| `low` | Rapide, raisonnement minimal |
| `medium` | Raisonnement équilibré |
| `high` | Raisonnement profond (défaut) |

## 🔧 Dépannage

### "Chrome cookie database locked"
Fermez **toutes** les fenêtres Chrome complètement et réessayez. Chrome verrouille la base de données de cookies pendant son exécution.

### "No active ChatGPT session found"
1. Ouvrez Chrome
2. Allez sur https://chatgpt.com
3. Connectez-vous à votre compte
4. Relancez `cc-gpt-6`

### "Claude Code not found"
Installez Claude Code : https://claude.ai/code

### Le jeton expire pendant l'utilisation
Le proxy a un **gardien de reconnexion auto** qui ré-extrait automatiquement les cookies de Chrome quand il détecte des sessions 401/403/expirées. Continuez simplement à travailler !

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

## ⚠️ Avertissement

Ceci est un **outil de recherche personnel**. Utilisez-le responsablement :
- Utilisez uniquement avec votre propre compte ChatGPT
- Respectez les Conditions d'Utilisation d'OpenAI
- Cet outil peut cesser de fonctionner si ChatGPT change son API
- Aucune garantie ni support fourni

## 📄 Licence

Licence MIT - voir [LICENSE](LICENSE) pour les détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! Merci de :
1. Fork le dépôt
2. Créer une branche de fonctionnalité
3. Ajouter des tests pour les nouvelles fonctionnalités
4. Vérifier que tous les tests passent (`pytest tests/ -v`)
5. Soumettre une PR

---

**Fait avec ❤️ pour la communauté du codage IA**