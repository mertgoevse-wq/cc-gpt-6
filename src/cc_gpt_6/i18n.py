"""Internationalization support for cc-gpt-6."""

from typing import Dict

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "de": "Deutsch",
    "zh": "中文",
    "es": "Español",
    "fr": "Français",
    "ja": "日本語",
    "ko": "한국어",
}

# Translation strings
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "welcome": "Welcome to cc-gpt-6!",
        "select_language": "Select your language / Wählen Sie Ihre Sprache / 选择语言:",
        "language_selected": "Language set to {lang}",
        "checking_chrome": "Checking Chrome for ChatGPT session...",
        "chrome_not_found": "Chrome not found or no active ChatGPT session.",
        "login_prompt": "Please log in to ChatGPT at https://chatgpt.com in Chrome first.",
        "token_extracted": "Session token extracted successfully!",
        "starting_proxy": "Starting proxy server on port {port}...",
        "proxy_started": "Proxy server started at http://127.0.0.1:{port}",
        "launching_claude": "Launching Claude Code...",
        "claude_not_found": "Claude Code not found. Please install it first: https://claude.ai/code",
        "error_token_extraction": "Failed to extract token: {error}",
        "error_chrome_locked": "Chrome is running and has the cookie database locked. Please close Chrome completely and try again.",
        "error_no_session": "No active ChatGPT session found. Please log in to https://chatgpt.com in Chrome.",
        "press_ctrl_c": "Press Ctrl+C to stop the proxy server.",
        "proxy_running": "Proxy is running. Configure Claude Code with:\n  ANTHROPIC_BASE_URL=http://127.0.0.1:{port}\n  ANTHROPIC_API_KEY=cc-gpt-6-dummy",
        "commands": {
            "start": "Extract token, start proxy, and launch Claude Code",
            "proxy": "Run only the proxy server",
            "extract_token": "Extract and print the ChatGPT session token",
            "config": "Configure settings (language, model, reasoning effort)",
        },
        "config_saved": "Configuration saved successfully!",
        "current_config": "Current configuration:",
        "config_language": "Language",
        "config_model": "Default Model",
        "config_reasoning": "Reasoning Effort",
        "config_port": "Proxy Port",
    },
    "de": {
        "welcome": "Willkommen bei cc-gpt-6!",
        "select_language": "Sprache auswählen / Select your language / 选择语言:",
        "language_selected": "Sprache auf {lang} gesetzt",
        "checking_chrome": "Prüfe Chrome auf ChatGPT-Sitzung...",
        "chrome_not_found": "Chrome nicht gefunden oder keine aktive ChatGPT-Sitzung.",
        "login_prompt": "Bitte melden Sie sich zuerst in Chrome bei https://chatgpt.com an.",
        "token_extracted": "Sitzungstoken erfolgreich extrahiert!",
        "starting_proxy": "Starte Proxy-Server auf Port {port}...",
        "proxy_started": "Proxy-Server gestartet unter http://127.0.0.1:{port}",
        "launching_claude": "Starte Claude Code...",
        "claude_not_found": "Claude Code nicht gefunden. Bitte zuerst installieren: https://claude.ai/code",
        "error_token_extraction": "Token-Extraktion fehlgeschlagen: {error}",
        "error_chrome_locked": "Chrome läuft und hat die Cookie-Datenbank gesperrt. Bitte Chrome vollständig schließen und erneut versuchen.",
        "error_no_session": "Keine aktive ChatGPT-Sitzung gefunden. Bitte bei https://chatgpt.com in Chrome anmelden.",
        "press_ctrl_c": "Drücken Sie Strg+C, um den Proxy-Server zu beenden.",
        "proxy_running": "Proxy läuft. Konfigurieren Sie Claude Code mit:\n  ANTHROPIC_BASE_URL=http://127.0.0.1:{port}\n  ANTHROPIC_API_KEY=cc-gpt-6-dummy",
        "commands": {
            "start": "Token extrahieren, Proxy starten und Claude Code starten",
            "proxy": "Nur den Proxy-Server starten",
            "extract_token": "ChatGPT-Sitzungstoken extrahieren und anzeigen",
            "config": "Einstellungen konfigurieren (Sprache, Modell, Reasoning-Aufwand)",
        },
        "config_saved": "Konfiguration erfolgreich gespeichert!",
        "current_config": "Aktuelle Konfiguration:",
        "config_language": "Sprache",
        "config_model": "Standard-Modell",
        "config_reasoning": "Reasoning-Aufwand",
        "config_port": "Proxy-Port",
    },
    "zh": {
        "welcome": "欢迎使用 cc-gpt-6！",
        "select_language": "选择语言 / Select your language / Wählen Sie Ihre Sprache:",
        "language_selected": "语言已设置为 {lang}",
        "checking_chrome": "正在检查 Chrome 的 ChatGPT 会话...",
        "chrome_not_found": "未找到 Chrome 或无活动的 ChatGPT 会话。",
        "login_prompt": "请先在 Chrome 中登录 https://chatgpt.com。",
        "token_extracted": "成功提取会话令牌！",
        "starting_proxy": "正在端口 {port} 启动代理服务器...",
        "proxy_started": "代理服务器已启动，地址：http://127.0.0.1:{port}",
        "launching_claude": "正在启动 Claude Code...",
        "claude_not_found": "未找到 Claude Code。请先安装：https://claude.ai/code",
        "error_token_extraction": "令牌提取失败：{error}",
        "error_chrome_locked": "Chrome 正在运行且锁定了 Cookie 数据库。请完全关闭 Chrome 后重试。",
        "error_no_session": "未找到活动的 ChatGPT 会话。请在 Chrome 中登录 https://chatgpt.com。",
        "press_ctrl_c": "按 Ctrl+C 停止代理服务器。",
        "proxy_running": "代理正在运行。使用以下配置 Claude Code：\n  ANTHROPIC_BASE_URL=http://127.0.0.1:{port}\n  ANTHROPIC_API_KEY=cc-gpt-6-dummy",
        "commands": {
            "start": "提取令牌、启动代理并启动 Claude Code",
            "proxy": "仅启动代理服务器",
            "extract_token": "提取并显示 ChatGPT 会话令牌",
            "config": "配置设置（语言、模型、推理力度）",
        },
        "config_saved": "配置已成功保存！",
        "current_config": "当前配置：",
        "config_language": "语言",
        "config_model": "默认模型",
        "config_reasoning": "推理力度",
        "config_port": "代理端口",
    },
    "es": {
        "welcome": "¡Bienvenido a cc-gpt-6!",
        "select_language": "Selecciona tu idioma / Select your language / Wählen Sie Ihre Sprache:",
        "language_selected": "Idioma establecido a {lang}",
        "checking_chrome": "Verificando Chrome para sesión de ChatGPT...",
        "chrome_not_found": "Chrome no encontrado o sin sesión activa de ChatGPT.",
        "login_prompt": "Por favor, inicia sesión en ChatGPT en https://chatgpt.com en Chrome primero.",
        "token_extracted": "¡Token de sesión extraído exitosamente!",
        "starting_proxy": "Iniciando servidor proxy en puerto {port}...",
        "proxy_started": "Servidor proxy iniciado en http://127.0.0.1:{port}",
        "launching_claude": "Iniciando Claude Code...",
        "claude_not_found": "Claude Code no encontrado. Instálalo primero: https://claude.ai/code",
        "error_token_extraction": "Error al extraer token: {error}",
        "error_chrome_locked": "Chrome se está ejecutando y tiene la base de datos de cookies bloqueada. Cierra Chrome completamente e inténtalo de nuevo.",
        "error_no_session": "No se encontró sesión activa de ChatGPT. Inicia sesión en https://chatgpt.com en Chrome.",
        "press_ctrl_c": "Presiona Ctrl+C para detener el servidor proxy.",
        "proxy_running": "Proxy en ejecución. Configura Claude Code con:\n  ANTHROPIC_BASE_URL=http://127.0.0.1:{port}\n  ANTHROPIC_API_KEY=cc-gpt-6-dummy",
        "commands": {
            "start": "Extraer token, iniciar proxy y lanzar Claude Code",
            "proxy": "Ejecutar solo el servidor proxy",
            "extract_token": "Extraer y mostrar el token de sesión de ChatGPT",
            "config": "Configurar ajustes (idioma, modelo, esfuerzo de razonamiento)",
        },
        "config_saved": "¡Configuración guardada exitosamente!",
        "current_config": "Configuración actual:",
        "config_language": "Idioma",
        "config_model": "Modelo por defecto",
        "config_reasoning": "Esfuerzo de razonamiento",
        "config_port": "Puerto del proxy",
    },
    "fr": {
        "welcome": "Bienvenue dans cc-gpt-6 !",
        "select_language": "Sélectionnez votre langue / Select your language / Wählen Sie Ihre Sprache:",
        "language_selected": "Langue définie sur {lang}",
        "checking_chrome": "Vérification de Chrome pour la session ChatGPT...",
        "chrome_not_found": "Chrome non trouvé ou aucune session ChatGPT active.",
        "login_prompt": "Veuillez vous connecter à ChatGPT sur https://chatgpt.com dans Chrome d'abord.",
        "token_extracted": "Jeton de session extrait avec succès !",
        "starting_proxy": "Démarrage du serveur proxy sur le port {port}...",
        "proxy_started": "Serveur proxy démarré sur http://127.0.0.1:{port}",
        "launching_claude": "Lancement de Claude Code...",
        "claude_not_found": "Claude Code introuvable. Veuillez l'installer d'abord : https://claude.ai/code",
        "error_token_extraction": "Échec de l'extraction du jeton : {error}",
        "error_chrome_locked": "Chrome s'exécute et verrouille la base de données des cookies. Fermez complètement Chrome et réessayez.",
        "error_no_session": "Aucune session ChatGPT active trouvée. Connectez-vous à https://chatgpt.com dans Chrome.",
        "press_ctrl_c": "Appuyez sur Ctrl+C pour arrêter le serveur proxy.",
        "proxy_running": "Proxy en cours d'exécution. Configurez Claude Code avec :\n  ANTHROPIC_BASE_URL=http://127.0.0.1:{port}\n  ANTHROPIC_API_KEY=cc-gpt-6-dummy",
        "commands": {
            "start": "Extraire le token, démarrer le proxy et lancer Claude Code",
            "proxy": "Exécuter uniquement le serveur proxy",
            "extract_token": "Extraire et afficher le jeton de session ChatGPT",
            "config": "Configurer les paramètres (langue, modèle, effort de raisonnement)",
        },
        "config_saved": "Configuration enregistrée avec succès !",
        "current_config": "Configuration actuelle :",
        "config_language": "Langue",
        "config_model": "Modèle par défaut",
        "config_reasoning": "Effort de raisonnement",
        "config_port": "Port du proxy",
    },
    "ja": {
        "welcome": "cc-gpt-6 へようこそ！",
        "select_language": "言語を選択 / Select your language / Wählen Sie Ihre Sprache:",
        "language_selected": "言語を {lang} に設定しました",
        "checking_chrome": "Chrome の ChatGPT セッションを確認中...",
        "chrome_not_found": "Chrome が見つからないか、アクティブな ChatGPT セッションがありません。",
        "login_prompt": "まず Chrome で https://chatgpt.com にログインしてください。",
        "token_extracted": "セッショントークンを正常に抽出しました！",
        "starting_proxy": "ポート {port} でプロキシサーバーを起動中...",
        "proxy_started": "プロキシサーバーが起動しました: http://127.0.0.1:{port}",
        "launching_claude": "Claude Code を起動中...",
        "claude_not_found": "Claude Code が見つかりません。まずインストールしてください: https://claude.ai/code",
        "error_token_extraction": "トークンの抽出に失敗しました: {error}",
        "error_chrome_locked": "Chrome が実行中で Cookie データベースがロックされています。Chrome を完全に終了してから再試行してください。",
        "error_no_session": "アクティブな ChatGPT セッションが見つかりません。Chrome で https://chatgpt.com にログインしてください。",
        "press_ctrl_c": "Ctrl+C を押してプロキシサーバーを停止してください。",
        "proxy_running": "プロキシが実行中です。Claude Code を以下で設定してください：\n  ANTHROPIC_BASE_URL=http://127.0.0.1:{port}\n  ANTHROPIC_API_KEY=cc-gpt-6-dummy",
        "commands": {
            "start": "トークンを抽出、プロキシを起動、Claude Code を起動",
            "proxy": "プロキシサーバーのみを実行",
            "extract_token": "ChatGPT セッショントークンを抽出して表示",
            "config": "設定を構成（言語、モデル、推論の努力）",
        },
        "config_saved": "設定が正常に保存されました！",
        "current_config": "現在の設定：",
        "config_language": "言語",
        "config_model": "デフォルトモデル",
        "config_reasoning": "推論の努力",
        "config_port": "プロキシポート",
    },
    "ko": {
        "welcome": "cc-gpt-6에 오신 것을 환영합니다!",
        "select_language": "언어 선택 / Select your language / Wählen Sie Ihre Sprache:",
        "language_selected": "언어가 {lang}로 설정되었습니다",
        "checking_chrome": "ChatGPT 세션을 위해 Chrome 확인 중...",
        "chrome_not_found": "Chrome을 찾을 수 없거나 활성 ChatGPT 세션이 없습니다.",
        "login_prompt": "먼저 Chrome에서 https://chatgpt.com에 로그인하세요.",
        "token_extracted": "세션 토큰이 성공적으로 추출되었습니다!",
        "starting_proxy": "포트 {port}에서 프록시 서버 시작 중...",
        "proxy_started": "프록시 서버가 시작되었습니다: http://127.0.0.1:{port}",
        "launching_claude": "Claude Code 시작 중...",
        "claude_not_found": "Claude Code를 찾을 수 없습니다. 먼저 설치하세요: https://claude.ai/code",
        "error_token_extraction": "토큰 추출 실패: {error}",
        "error_chrome_locked": "Chrome이 실행 중이며 쿠키 데이터베이스가 잠겨 있습니다. Chrome을 완전히 종료하고 다시 시도하세요.",
        "error_no_session": "활성 ChatGPT 세션을 찾을 수 없습니다. Chrome에서 https://chatgpt.com에 로그인하세요.",
        "press_ctrl_c": "Ctrl+C를 눌러 프록시 서버를 중지하세요.",
        "proxy_running": "프록시가 실행 중입니다. Claude Code를 다음으로 구성하세요:\n  ANTHROPIC_BASE_URL=http://127.0.0.1:{port}\n  ANTHROPIC_API_KEY=cc-gpt-6-dummy",
        "commands": {
            "start": "토큰 추출, 프록시 시작, Claude Code 실행",
            "proxy": "프록시 서버만 실행",
            "extract_token": "ChatGPT 세션 토큰 추출 및 표시",
            "config": "설정 구성 (언어, 모델, 추론 노력)",
        },
        "config_saved": "설정이 성공적으로 저장되었습니다!",
        "current_config": "현재 설정:",
        "config_language": "언어",
        "config_model": "기본 모델",
        "config_reasoning": "추론 노력",
        "config_port": "프록시 포트",
    },
}

# Default language
DEFAULT_LANG = "en"

# Current language (set at runtime)
_current_lang = DEFAULT_LANG


def set_language(lang: str) -> bool:
    """Set the current language. Returns True if successful."""
    global _current_lang
    if lang in SUPPORTED_LANGUAGES:
        _current_lang = lang
        return True
    return False


def get_language() -> str:
    """Get the current language code."""
    return _current_lang


def get_lang_name(lang: str) -> str:
    """Get the display name for a language code."""
    return SUPPORTED_LANGUAGES.get(lang, lang)


def t(key: str, **kwargs) -> str:
    """Translate a key with optional formatting."""
    lang_dict = TRANSLATIONS.get(_current_lang, TRANSLATIONS[DEFAULT_LANG])
    template = lang_dict.get(key, TRANSLATIONS[DEFAULT_LANG].get(key, key))
    try:
        return template.format(**kwargs)
    except (KeyError, ValueError):
        return template


def t_cmd(key: str) -> str:
    """Translate a command description."""
    lang_dict = TRANSLATIONS.get(_current_lang, TRANSLATIONS[DEFAULT_LANG])
    return lang_dict.get("commands", {}).get(key, key)


def list_languages() -> str:
    """Return a formatted string of available languages."""
    lines = []
    for code, name in SUPPORTED_LANGUAGES.items():
        marker = " *" if code == _current_lang else ""
        lines.append(f"  {code}: {name}{marker}")
    return "\n".join(lines)