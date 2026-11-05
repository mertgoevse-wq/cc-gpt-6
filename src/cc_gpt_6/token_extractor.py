"""Extract the ChatGPT session token from Chrome's cookie store (Windows DPAPI + AES-GCM)."""

import base64
import json
import os
import shutil
import sqlite3
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any


def get_chrome_user_data_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        raise RuntimeError("LOCALAPPDATA environment variable not set")
    return Path(local_app_data) / "Google" / "Chrome" / "User Data"


def get_chrome_cookie_db_path() -> Path:
    user_data = get_chrome_user_data_dir()
    # Chrome 110+ uses Network/Cookies
    cookie_path = user_data / "Default" / "Network" / "Cookies"
    if not cookie_path.exists():
        # Older Chrome versions
        cookie_path = user_data / "Default" / "Cookies"
    return cookie_path


def dpapi_decrypt(blob: bytes) -> bytes:
    import ctypes
    import ctypes.wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [
            ("cbData", ctypes.wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_char)),
        ]

    in_blob = DATA_BLOB(
        len(blob),
        ctypes.cast(ctypes.create_string_buffer(blob), ctypes.POINTER(ctypes.c_char)),
    )
    out_blob = DATA_BLOB()
    success = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)
    )
    if not success:
        raise RuntimeError("Windows DPAPI CryptUnprotectData failed to decrypt data")
    decrypted_bytes = ctypes.string_at(out_blob.pbData, out_blob.cbData)
    ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    return decrypted_bytes


def aes_gcm_decrypt(key: bytes, nonce: bytes, ciphertext_with_tag: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext_with_tag, None)


def get_chrome_app_bound_key() -> Optional[bytes]:
    """Get the app-bound encryption key using Chrome's IElevator COM service.

    This is needed for Chrome 127+ which uses App-Bound Encryption.
    Returns None if the service is not available or decryption fails.
    """
    try:
        import comtypes.client
        from comtypes import GUID, IUnknown, COMMETHOD, HRESULT, BSTR

        # IElevator interface definition
        class IElevator(IUnknown):
            _iid_ = GUID("{A8D4E1B2-3C4F-4E9B-9D8F-8E6B5D4C3A2B}")
            _methods_ = [
                COMMETHOD([], HRESULT, "DecryptData",
                          (["in"], BSTR, "encrypted_data"),
                          (["out", "retval"], BSTR, "decrypted_data")),
            ]

        # Try known CLSIDs for Chrome elevation service
        clsids_to_try = [
            "{3A6D0F51-1F1C-4E9B-9D8F-8E6B5D4C3A2B}",
            "{A8D4E1B2-3C4F-4E9B-9D8F-8E6B5D4C3A2B}",
        ]

        local_state_path = get_chrome_user_data_dir() / "Local State"
        if not local_state_path.exists():
            return None
        data = json.loads(local_state_path.read_text(encoding="utf-8"))
        if "os_crypt" not in data or "app_bound_encrypted_key" not in data["os_crypt"]:
            return None

        app_bound_b64 = data["os_crypt"]["app_bound_encrypted_key"]

        for clsid_str in clsids_to_try:
            try:
                clsid = GUID(clsid_str)
                elevator = comtypes.client.CreateObject(clsid, interface=IElevator)
                decrypted_bstr = elevator.DecryptData(app_bound_b64)
                if decrypted_bstr:
                    decrypted_bytes = base64.b64decode(decrypted_bstr)
                    if len(decrypted_bytes) == 32:
                        return decrypted_bytes
            except Exception:
                continue

        return None
    except ImportError:
        return None
    except Exception:
        return None


def is_app_bound_encryption_enabled() -> bool:
    """Check if Chrome is using App-Bound Encryption."""
    try:
        local_state_path = get_chrome_user_data_dir() / "Local State"
        if not local_state_path.exists():
            return False
        data = json.loads(local_state_path.read_text(encoding="utf-8"))
        os_crypt = data.get("os_crypt", {})
        return "app_bound_encrypted_key" in os_crypt and os_crypt.get("audit_enabled", False)
    except Exception:
        return False


def get_chrome_aes_key() -> bytes:
    local_state_path = get_chrome_user_data_dir() / "Local State"
    if not local_state_path.exists():
        raise FileNotFoundError(f"Chrome Local State file not found at: {local_state_path}")
    data = json.loads(local_state_path.read_text(encoding="utf-8"))

    # First try app-bound key (Chrome 127+)
    if "os_crypt" in data and "app_bound_encrypted_key" in data["os_crypt"]:
        app_bound_key = get_chrome_app_bound_key()
        if app_bound_key:
            return app_bound_key

    # Fall back to old encrypted_key
    encrypted_key_b64 = data["os_crypt"]["encrypted_key"]
    encrypted_key = base64.b64decode(encrypted_key_b64)
    if not encrypted_key.startswith(b"DPAPI"):
        raise ValueError("Invalid encrypted key format (expected DPAPI prefix)")
    return dpapi_decrypt(encrypted_key[5:])


def extract_chatgpt_cookies() -> Dict[str, str]:
    db_path = get_chrome_cookie_db_path()
    if not db_path.exists():
        raise FileNotFoundError(f"Chrome cookie database not found at: {db_path}")

    master_key = get_chrome_aes_key()
    cookies_found: Dict[str, str] = {}

    temp_dir = tempfile.mkdtemp(prefix="cc_gpt_")
    temp_db = Path(temp_dir) / "Cookies.sqlite"

    # Chrome locks the cookie database - retry with short delays
    max_retries = 5
    for attempt in range(max_retries):
        try:
            shutil.copy2(db_path, temp_db)
            break
        except PermissionError:
            if attempt == max_retries - 1:
                raise RuntimeError(
                    "Could not copy Chrome cookie database. "
                    "Please close Chrome completely and try again."
                )
            time.sleep(0.5)

    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()

    query = (
        "SELECT name, encrypted_value FROM cookies "
        "WHERE host_key LIKE '%chatgpt.com%' OR host_key LIKE '%openai.com%'"
    )
    cursor.execute(query)

    try:
        for name, enc_val in cursor.fetchall():
            if not enc_val:
                continue
            decrypted_str = ""
            try:
                # Handle v10, v11, v20, etc. - all use AES-GCM with 12-byte nonce after version prefix
                if enc_val.startswith(b"v") and len(enc_val) > 15 and enc_val[1:3].isdigit():
                    # Version prefix (v10, v11, v20, etc.) + 12-byte nonce + ciphertext+tag
                    version_end = 3
                    # Check if it's v10, v11, v20 (two digits) or v9 (one digit)
                    if len(enc_val) > 4 and enc_val[3:4].isdigit():
                        version_end = 4
                    nonce = enc_val[version_end:version_end + 12]
                    ct_with_tag = enc_val[version_end + 12:]
                    decrypted_bytes = aes_gcm_decrypt(master_key, nonce, ct_with_tag)
                    decrypted_str = decrypted_bytes.decode("utf-8", errors="replace")
                else:
                    decrypted_bytes = dpapi_decrypt(enc_val)
                    decrypted_str = decrypted_bytes.decode("utf-8", errors="replace")
            except Exception:
                continue

            if decrypted_str:
                cookies_found[name] = decrypted_str
    finally:
        conn.close()
        shutil.rmtree(temp_dir, ignore_errors=True)

    return cookies_found


def extract_chatgpt_cookies_from_profile(profile_name: str) -> Dict[str, str]:
    """Extract cookies from a specific Chrome profile."""
    user_data = get_chrome_user_data_dir()
    # Chrome 110+ uses Network/Cookies
    cookie_path = user_data / profile_name / "Network" / "Cookies"
    if not cookie_path.exists():
        # Older Chrome versions
        cookie_path = user_data / profile_name / "Cookies"

    if not cookie_path.exists():
        return {}

    master_key = get_chrome_aes_key()
    cookies_found: Dict[str, str] = {}

    temp_dir = tempfile.mkdtemp(prefix="cc_gpt_")
    temp_db = Path(temp_dir) / "Cookies.sqlite"

    max_retries = 5
    for attempt in range(max_retries):
        try:
            shutil.copy2(cookie_path, temp_db)
            break
        except PermissionError:
            if attempt == max_retries - 1:
                raise RuntimeError(
                    f"Could not copy Chrome cookie database for profile '{profile_name}'. "
                    "Please close Chrome completely and try again."
                )
            time.sleep(0.5)

    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()

    query = (
        "SELECT name, encrypted_value FROM cookies "
        "WHERE host_key LIKE '%chatgpt.com%' OR host_key LIKE '%openai.com%'"
    )
    cursor.execute(query)

    try:
        for name, enc_val in cursor.fetchall():
            if not enc_val:
                continue
            decrypted_str = ""
            try:
                # Handle v10, v11, v20, etc. - all use AES-GCM with 12-byte nonce after version prefix
                if enc_val.startswith(b"v") and len(enc_val) > 15 and enc_val[1:3].isdigit():
                    # Version prefix (v10, v11, v20, etc.) + 12-byte nonce + ciphertext+tag
                    version_end = 3
                    # Check if it's v10, v11, v20 (two digits) or v9 (one digit)
                    if len(enc_val) > 4 and enc_val[3:4].isdigit():
                        version_end = 4
                    nonce = enc_val[version_end:version_end + 12]
                    ct_with_tag = enc_val[version_end + 12:]
                    decrypted_bytes = aes_gcm_decrypt(master_key, nonce, ct_with_tag)
                    decrypted_str = decrypted_bytes.decode("utf-8", errors="replace")
                else:
                    decrypted_bytes = dpapi_decrypt(enc_val)
                    decrypted_str = decrypted_bytes.decode("utf-8", errors="replace")
            except Exception:
                continue

            if decrypted_str:
                cookies_found[name] = decrypted_str
    finally:
        conn.close()
        shutil.rmtree(temp_dir, ignore_errors=True)

    return cookies_found


def extract_chatgpt_token() -> str:
    # Check environment variables first
    env_token = os.environ.get("CHATGPT_SESSION_TOKEN") or os.environ.get("CHATGPT_TOKEN")
    if env_token:
        return env_token.strip()

    # Try multiple Chrome profiles
    profiles_to_try = ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4", "Profile 5"]
    all_cookies: Dict[str, str] = {}

    for profile in profiles_to_try:
        try:
            cookies = extract_chatgpt_cookies_from_profile(profile)
            if cookies:
                all_cookies.update(cookies)
        except (FileNotFoundError, RuntimeError):
            continue

    if not all_cookies:
        raise RuntimeError(
            "No ChatGPT/OpenAI cookies found in any Chrome profile. "
            "Please open Chrome, log in to https://chatgpt.com, and try again."
        )

    # Handle split token first (some Chrome versions split the token into .0 and .1)
    if "__Secure-next-auth.session-token.0" in all_cookies and "__Secure-next-auth.session-token.1" in all_cookies:
        return all_cookies["__Secure-next-auth.session-token.0"] + all_cookies["__Secure-next-auth.session-token.1"]

    # Extended token candidates - ChatGPT uses various cookie names
    token_candidates = [
        "__Secure-next-auth.session-token",
        "session-token",
        "access_token",
        "next-auth.session-token",
        "cf_clearance",  # Sometimes used
    ]

    for key in token_candidates:
        if key in all_cookies and all_cookies[key]:
            return all_cookies[key]

    raise RuntimeError(
        "No active ChatGPT session token found in Chrome cookies. "
        "Please log in to https://chatgpt.com in Chrome and try again. "
        f"Found cookies: {list(all_cookies.keys())}"
    )