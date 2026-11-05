# cc-gpt-6

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-65%20aprobados-brightgreen.svg)](tests/)

Herramienta personal: ejecuta **Claude Code** contra tu **propia sesión de ChatGPT iniciada** en Chrome, exponiendo un proxy local compatible con Anthropic.

> ⚠️ **Úsalo solo con tu propia cuenta.** Automatizar la UI web de ChatGPT puede violar los Términos de Servicio de OpenAI. Esta es una herramienta de investigación personal.

## 🌐 Idiomas

- [English](README.md)
- [Deutsch](README.de.md)
- [中文](README.zh.md)
- [Español](README.es.md) (este archivo)
- [Français](README.fr.md)
- [日本語](README.ja.md)
- [한국어](README.ko.md)

---

## Cómo funciona

1. `cc-gpt-6 start` lee el almacenamiento de cookies de Chrome para chatgpt.com (DPAPI en Windows) y extrae tu token de sesión automáticamente
2. Inicia un proxy FastAPI local en `127.0.0.1:8787` que habla la **API de Mensajes de Anthropic** y reenvía al backend de ChatGPT
3. Lanza `claude` (Claude Code) con `ANTHROPIC_BASE_URL` apuntando al proxy, así Claude Code cree que habla con Anthropic
4. ¡Obtienes razonamiento **GPT-6 / o3-mini / o1 / GPT-4o** a través de la interfaz de Claude Code!

## ✨ Características

- 🔐 **Extracción automática de token** desde cookies de Chrome (Windows DPAPI + AES-GCM)
- 🔄 **Reconexión automática y refresco de token** - re-extrae cookies automáticamente en 401/403/expirado
- 🧠 **Control de esfuerzo de razonamiento** - low/medium/high (mapea a reasoning_effort de ChatGPT)
- 🌍 **Multilingüe** - Inglés, Alemán, Chino, Español, Francés, Japonés, Coreano
- ⚙️ **Configuración persistente** - idioma, modelo, esfuerzo de razonamiento, puerto guardados en `~/.config/cc-gpt-6/`
- 🔌 **Compatible con API de Anthropic** - funciona con cualquier herramienta que espere formato API de Anthropic
- 📦 **Soporte de modelos** - gpt-6, gpt-5.6, o3-mini, o1, gpt-4o

## 📋 Requisitos

- **Python 3.12+**
- **Google Chrome** (iniciado en https://chatgpt.com)
- **Claude Code** instalado (`claude` en PATH)
- **Windows** (para descifrado DPAPI de cookies) - Soporte Linux/macOS planeado

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/yourusername/cc-gpt-6.git
cd cc-gpt-6

# Instalar en modo desarrollo
pip install -e .

# O con pipx (recomendado para herramientas CLI)
pipx install -e .
```

## 🎯 Uso

### Primera ejecución - Configuración interactiva

```bash
cc-gpt-6 start
```

En la primera ejecución, se le pedirá que seleccione su idioma:
```
¡Bienvenido a cc-gpt-6!

Selecciona tu idioma / Select your language / Wählen Sie Ihre Sprache:
  en: English *
  de: Deutsch
  zh: 中文
  es: Español
  fr: Français
  ja: 日本語
  ko: 한국어

Enter language code (e.g., en, de, zh): es
```

### Comandos

| Comando | Descripción |
|---------|-------------|
| `cc-gpt-6 start` | Extraer token, iniciar proxy, lanzar Claude Code |
| `cc-gpt-6 start --no-claude` | Iniciar solo el proxy (no lanzar Claude Code) |
| `cc-gpt-6 proxy` | Ejecutar solo el servidor proxy |
| `cc-gpt-6 extract-token` | Mostrar el token de sesión de ChatGPT extraído |
| `cc-gpt-6 config` | Configuración interactiva |
| `cc-gpt-6 config --show` | Mostrar configuración actual |
| `cc-gpt-6 config --language es` | Establecer idioma a español |
| `cc-gpt-6 config --model gpt-6` | Establecer modelo predeterminado |
| `cc-gpt-6 config --reasoning high` | Establecer esfuerzo de razonamiento |
| `cc-gpt-6 config --port 9999` | Establecer puerto del proxy |

### Flujo de trabajo de ejemplo

```bash
# 1. Asegúrate de haber iniciado sesión en ChatGPT en Chrome
# 2. Ejecuta cc-gpt-6
cc-gpt-6 start

# 3. ¡Claude Code se inicia, conectado a tu sesión de ChatGPT!
#    Ahora puedes usar razonamiento GPT-6 / o3-mini / o1 a través de Claude Code
```

### Uso manual del proxy

```bash
# Terminal 1: Iniciar proxy
cc-gpt-6 proxy

# Terminal 2: Usar con cualquier herramienta compatible con Anthropic
export ANTHROPIC_BASE_URL=http://127.0.0.1:8787
export ANTHROPIC_API_KEY=cc-gpt-6-dummy
claude  # o cualquier otro cliente API de Anthropic
```

## ⚙️ Configuración

La configuración se guarda en `~/.config/cc-gpt-6/config.json`:

```json
{
  "language": "es",
  "model": "o3-mini",
  "reasoning_effort": "high",
  "port": 8787,
  "auto_launch_claude": true
}
```

### Modelos soportados

| Modelo | Descripción |
|--------|-------------|
| `gpt-6` | GPT-6 (si está disponible) |
| `gpt-5.6` | GPT-5.6 (si está disponible) |
| `o3-mini` | Modelo de razonamiento o3-mini (predeterminado) |
| `o1` | Modelo de razonamiento o1 |
| `gpt-4o` | GPT-4o |

### Niveles de esfuerzo de razonamiento

| Nivel | Descripción |
|-------|-------------|
| `low` | Rápido, razonamiento mínimo |
| `medium` | Razonamiento equilibrado |
| `high` | Razonamiento profundo (predeterminado) |

## 🔧 Solución de problemas

### "Chrome cookie database locked"
Cierra **todas** las ventanas de Chrome completamente e inténtalo de nuevo. Chrome bloquea la base de datos de cookies mientras se ejecuta.

### "No active ChatGPT session found"
1. Abre Chrome
2. Ve a https://chatgpt.com
3. Inicia sesión en tu cuenta
4. Ejecuta `cc-gpt-6` de nuevo

### "Claude Code not found"
Instala Claude Code: https://claude.ai/code

### El token expira durante el uso
El proxy tiene un **guardián de reconexión automática** que re-extrae automáticamente las cookies de Chrome cuando detecta sesiones 401/403/expiradas. ¡Solo continúa trabajando!

## 🏗️ Arquitectura

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

## ⚠️ Descargo de responsabilidad

Esta es una **herramienta de investigación personal**. Úsala responsablemente:
- Úsala solo con tu propia cuenta de ChatGPT
- Respeta los Términos de Servicio de OpenAI
- Esta herramienta puede dejar de funcionar si ChatGPT cambia su API
- Sin garantía ni soporte

## 📄 Licencia

Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## 🤝 Contribuir

¡Contribuciones bienvenidas! Por favor:
1. Haz fork del repositorio
2. Crea una rama de característica
3. Añade tests para nueva funcionalidad
4. Asegúrate que todos los tests pasen (`pytest tests/ -v`)
5. Envía un PR

---

**Hecho con ❤️ para la comunidad de codificación con IA**