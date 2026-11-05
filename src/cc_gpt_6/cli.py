"""CLI entry point for cc-gpt-6."""

import argparse
import os
import subprocess
import sys
import threading
import time

from .config import (
    DEFAULT_CONFIG,
    get_config_value,
    load_config,
    reset_config,
    save_config,
    set_config_value,
    validate_language,
    validate_model,
    validate_port,
    validate_reasoning_effort,
)
from .i18n import (
    DEFAULT_LANG,
    SUPPORTED_LANGUAGES,
    get_lang_name,
    list_languages,
    set_language,
    t,
    t_cmd,
)
from .token_extractor import extract_chatgpt_token
from . import proxy


def _safe_print(text: str, file=None) -> None:
    """Print text safely handling encoding issues on Windows."""
    try:
        print(text, file=file)
    except UnicodeEncodeError:
        # Fallback: replace non-encodable characters
        safe_text = text.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
        print(safe_text, file=file)


def print_welcome() -> None:
    """Print welcome message in current language."""
    _safe_print(f"\n{t('welcome')}\n")


def select_language_interactive() -> str:
    """Interactive language selection."""
    _safe_print(t("select_language"))
    _safe_print(list_languages())
    _safe_print("")

    while True:
        choice = input("Enter language code (e.g., en, de, zh): ").strip().lower()
        if validate_language(choice):
            return choice
        _safe_print(f"Invalid language code. Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}")


def run_first_time_setup() -> str:
    """Run first-time setup: language selection."""
    config = load_config()

    # Check if config file exists (user has run setup before)
    from .config import CONFIG_FILE
    if CONFIG_FILE.exists():
        # Config exists, use the language from config
        lang = config.get("language", DEFAULT_LANG)
        set_language(lang)
        return lang

    # First run - ask for language
    print_welcome()
    lang = select_language_interactive()
    set_language(lang)
    set_config_value("language", lang)
    _safe_print(f"\n{t('language_selected', lang=get_lang_name(lang))}\n")
    return lang


def cmd_extract_token(args) -> int:
    """Extract and print the ChatGPT session token."""
    try:
        token = extract_chatgpt_token()
        _safe_print(token)
        return 0
    except FileNotFoundError as e:
        _safe_print(t("error_chrome_locked"), file=sys.stderr)
        _safe_print(f"Detail: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        if "locked" in str(e).lower() or "permission" in str(e).lower():
            _safe_print(t("error_chrome_locked"), file=sys.stderr)
        else:
            _safe_print(t("error_no_session"), file=sys.stderr)
        _safe_print(f"Detail: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        _safe_print(t("error_token_extraction", error=e), file=sys.stderr)
        return 1


def cmd_proxy(args) -> int:
    """Run only the proxy server."""
    port = args.port or get_config_value("port", DEFAULT_CONFIG["port"])

    # Get token
    token = os.environ.get("CHATGPT_TOKEN")
    if not token:
        try:
            _safe_print(t("checking_chrome"), file=sys.stderr)
            token = extract_chatgpt_token()
            _safe_print(t("token_extracted"), file=sys.stderr)
        except Exception as e:
            _safe_print(t("error_token_extraction", error=e), file=sys.stderr)
            return 1

    proxy.set_token(token)

    # Apply config
    model = get_config_value("model", DEFAULT_CONFIG["model"])
    reasoning = get_config_value("reasoning_effort", DEFAULT_CONFIG["reasoning_effort"])
    proxy.configure(session_token=token, model=model, reasoning_effort=reasoning)

    _safe_print(t("starting_proxy", port=port), file=sys.stderr)

    import uvicorn
    try:
        uvicorn.run(proxy.app, host="127.0.0.1", port=port)
    except KeyboardInterrupt:
        _safe_print("\n" + t("press_ctrl_c"), file=sys.stderr)
    return 0


def cmd_start(args) -> int:
    """Extract token, start proxy, and launch Claude Code."""
    port = args.port or get_config_value("port", DEFAULT_CONFIG["port"])

    # Get token
    token = os.environ.get("CHATGPT_TOKEN")
    if not token:
        try:
            _safe_print(t("checking_chrome"), file=sys.stderr)
            token = extract_chatgpt_token()
            _safe_print(t("token_extracted"), file=sys.stderr)
        except FileNotFoundError as e:
            _safe_print(t("error_chrome_locked"), file=sys.stderr)
            _safe_print(f"Detail: {e}", file=sys.stderr)
            return 1
        except RuntimeError as e:
            if "locked" in str(e).lower() or "permission" in str(e).lower():
                _safe_print(t("error_chrome_locked"), file=sys.stderr)
            else:
                _safe_print(t("error_no_session"), file=sys.stderr)
            _safe_print(f"Detail: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            _safe_print(t("error_token_extraction", error=e), file=sys.stderr)
            return 1

    proxy.set_token(token)

    # Apply config
    model = get_config_value("model", DEFAULT_CONFIG["model"])
    reasoning = get_config_value("reasoning_effort", DEFAULT_CONFIG["reasoning_effort"])
    proxy.configure(session_token=token, model=model, reasoning_effort=reasoning)

    # Start proxy in background
    _safe_print(t("starting_proxy", port=port), file=sys.stderr)

    def run_proxy():
        import uvicorn
        uvicorn.run(proxy.app, host="127.0.0.1", port=port, log_level="warning")

    proxy_thread = threading.Thread(target=run_proxy, daemon=True)
    proxy_thread.start()

    # Wait for proxy to start
    time.sleep(1.5)

    _safe_print(t("proxy_started", port=port), file=sys.stderr)
    _safe_print(t("proxy_running", port=port), file=sys.stderr)

    # Launch Claude Code if requested
    if args.no_claude or not get_config_value("auto_launch_claude", DEFAULT_CONFIG["auto_launch_claude"]):
        _safe_print(t("press_ctrl_c"), file=sys.stderr)
        try:
            proxy_thread.join()
        except KeyboardInterrupt:
            pass
        return 0

    _safe_print(t("launching_claude"), file=sys.stderr)
    env = dict(os.environ)
    env["ANTHROPIC_BASE_URL"] = f"http://127.0.0.1:{port}"
    env["ANTHROPIC_API_KEY"] = "cc-gpt-6-dummy"

    try:
        subprocess.run(["claude"], env=env, check=True)
    except FileNotFoundError:
        _safe_print(t("claude_not_found"), file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        _safe_print(f"Claude Code exited with code {e.returncode}", file=sys.stderr)
        return e.returncode
    except KeyboardInterrupt:
        pass

    return 0


def cmd_config(args) -> int:
    """Configure settings."""
    config = load_config()

    if args.show:
        _safe_print(t("current_config"))
        _safe_print(f"  {t('config_language')}: {get_lang_name(config.get('language', DEFAULT_LANG))}")
        _safe_print(f"  {t('config_model')}: {config.get('model', DEFAULT_CONFIG['model'])}")
        _safe_print(f"  {t('config_reasoning')}: {config.get('reasoning_effort', DEFAULT_CONFIG['reasoning_effort'])}")
        _safe_print(f"  {t('config_port')}: {config.get('port', DEFAULT_CONFIG['port'])}")
        return 0

    if args.reset:
        reset_config()
        _safe_print(t("config_saved"))
        return 0

    if args.language:
        if not validate_language(args.language):
            _safe_print(f"Invalid language. Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}", file=sys.stderr)
            return 1
        set_config_value("language", args.language)
        set_language(args.language)
        _safe_print(t("config_saved"))
        return 0

    if args.model:
        if not validate_model(args.model):
            from .proxy import SUPPORTED_MODELS
            _safe_print(f"Invalid model. Supported: {', '.join(SUPPORTED_MODELS)}", file=sys.stderr)
            return 1
        set_config_value("model", args.model)
        _safe_print(t("config_saved"))
        return 0

    if args.reasoning:
        if not validate_reasoning_effort(args.reasoning):
            from .proxy import REASONING_LEVELS
            _safe_print(f"Invalid reasoning effort. Supported: {', '.join(REASONING_LEVELS)}", file=sys.stderr)
            return 1
        set_config_value("reasoning_effort", args.reasoning)
        _safe_print(t("config_saved"))
        return 0

    if args.port:
        if not validate_port(args.port):
            _safe_print("Invalid port. Must be 1-65535.", file=sys.stderr)
            return 1
        set_config_value("port", args.port)
        _safe_print(t("config_saved"))
        return 0

    # If no specific config option given, run interactive config
    return run_interactive_config()


def run_interactive_config() -> int:
    """Run interactive configuration."""
    config = load_config()

    _safe_print(t("current_config"))
    _safe_print(f"  1. {t('config_language')}: {get_lang_name(config.get('language', DEFAULT_LANG))}")
    _safe_print(f"  2. {t('config_model')}: {config.get('model', DEFAULT_CONFIG['model'])}")
    _safe_print(f"  3. {t('config_reasoning')}: {config.get('reasoning_effort', DEFAULT_CONFIG['reasoning_effort'])}")
    _safe_print(f"  4. {t('config_port')}: {config.get('port', DEFAULT_CONFIG['port'])}")
    _safe_print("")
    _safe_print("Enter number to change, or 'q' to quit:")

    while True:
        choice = input("> ").strip().lower()
        if choice == 'q':
            break

        if choice == '1':
            _safe_print(t("select_language"))
            _safe_print(list_languages())
            lang = input("Language code: ").strip().lower()
            if validate_language(lang):
                set_config_value("language", lang)
                set_language(lang)
                _safe_print(t("config_saved"))
            else:
                _safe_print("Invalid language code.")

        elif choice == '2':
            from .proxy import SUPPORTED_MODELS
            _safe_print(f"Supported models: {', '.join(SUPPORTED_MODELS)}")
            model = input("Model: ").strip()
            if validate_model(model):
                set_config_value("model", model)
                _safe_print(t("config_saved"))
            else:
                _safe_print("Invalid model.")

        elif choice == '3':
            from .proxy import REASONING_LEVELS
            _safe_print(f"Supported levels: {', '.join(REASONING_LEVELS)}")
            reasoning = input("Reasoning effort: ").strip().lower()
            if validate_reasoning_effort(reasoning):
                set_config_value("reasoning_effort", reasoning)
                _safe_print(t("config_saved"))
            else:
                _safe_print("Invalid reasoning effort.")

        elif choice == '4':
            try:
                port = int(input("Port: ").strip())
                if validate_port(port):
                    set_config_value("port", port)
                    _safe_print(t("config_saved"))
                else:
                    _safe_print("Invalid port. Must be 1-65535.")
            except ValueError:
                _safe_print("Invalid port number.")

        else:
            _safe_print("Invalid choice. Enter 1-4 or 'q'.")

    return 0


def main() -> int:
    # Run first-time setup (language selection)
    run_first_time_setup()

    parser = argparse.ArgumentParser(
        prog="cc-gpt-6",
        description="Anthropic-compatible proxy over a logged-in ChatGPT session"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # extract-token
    sub.add_parser("extract-token", help=t_cmd("extract_token"))

    # proxy
    sp = sub.add_parser("proxy", help=t_cmd("proxy"))
    sp.add_argument("--port", type=int, help="Proxy port")

    # start
    sp = sub.add_parser("start", help=t_cmd("start"))
    sp.add_argument("--port", type=int, help="Proxy port")
    sp.add_argument("--no-claude", action="store_true", help="Don't launch Claude Code, just run proxy")

    # config
    sp = sub.add_parser("config", help=t_cmd("config"))
    sp.add_argument("--show", action="store_true", help="Show current configuration")
    sp.add_argument("--reset", action="store_true", help="Reset to defaults")
    sp.add_argument("--language", help="Set language (en, de, zh, es, fr, ja, ko)")
    sp.add_argument("--model", help="Set default model")
    sp.add_argument("--reasoning", help="Set reasoning effort (low, medium, high)")
    sp.add_argument("--port", type=int, help="Set proxy port")

    args = parser.parse_args()

    # Dispatch
    if args.cmd == "extract-token":
        return cmd_extract_token(args)
    elif args.cmd == "proxy":
        return cmd_proxy(args)
    elif args.cmd == "start":
        return cmd_start(args)
    elif args.cmd == "config":
        return cmd_config(args)

    return 1


if __name__ == "__main__":
    sys.exit(main())