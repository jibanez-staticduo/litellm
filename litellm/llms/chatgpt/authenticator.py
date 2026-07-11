import base64
import json
import os
import re
import tempfile
import threading
import time
from typing import Any, Final

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows
    fcntl = None  # type: ignore[assignment]

try:
    import msvcrt
except ImportError:  # pragma: no cover - POSIX
    msvcrt = None  # type: ignore[assignment]

import httpx

from litellm._logging import verbose_logger
from litellm.llms.custom_httpx.http_handler import _get_httpx_client

from .common_utils import (
    CHATGPT_API_BASE,
    CHATGPT_AUTH_BASE,
    CHATGPT_CLIENT_ID,
    CHATGPT_DEVICE_CODE_URL,
    CHATGPT_DEVICE_TOKEN_URL,
    CHATGPT_DEVICE_VERIFY_URL,
    CHATGPT_OAUTH_TOKEN_URL,
    GetAccessTokenError,
    GetDeviceCodeError,
    InteractiveAuthError,
    RefreshAccessTokenError,
)

TOKEN_EXPIRY_SKEW_SECONDS = 60
DEVICE_CODE_TIMEOUT_SECONDS = 15 * 60
DEVICE_CODE_COOLDOWN_SECONDS = 5 * 60
DEVICE_CODE_POLL_SLEEP_SECONDS = 5
_SAFE_AUTH_PROFILE_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
_AUTH_LOCKS: Dict[str, threading.RLock] = {}
_AUTH_LOCKS_GUARD = threading.Lock()


def _lock_auth_file(lock_file: Any) -> None:
    if fcntl is not None:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        return
    if msvcrt is not None:
        lock_file.seek(0)
        if lock_file.read(1) == "":
            lock_file.write("0")
            lock_file.flush()
        lock_file.seek(0)
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        return
    raise RuntimeError("No supported cross-process file locking mechanism")


class Authenticator:
    def __init__(self, litellm_params: Optional[object] = None) -> None:
        self.token_dir = self._resolve_token_dir(litellm_params)
        self.auth_file = self._resolve_auth_file(litellm_params)
        self._ensure_token_dir()

    def _resolve_token_dir(self, litellm_params: Optional[object]) -> str:
        configured_token_dir = self._get_litellm_param(litellm_params, "chatgpt_token_dir")
        if configured_token_dir:
            return os.path.expanduser(str(configured_token_dir))
        return os.getenv(
            "CHATGPT_TOKEN_DIR",
            os.path.expanduser("~/.config/litellm/chatgpt"),
        )

    def _resolve_auth_file(self, litellm_params: Optional[object]) -> str:
        configured_auth_file = self._get_litellm_param(litellm_params, "chatgpt_auth_file")
        if configured_auth_file:
            auth_file = os.path.expanduser(str(configured_auth_file))
            if os.path.isabs(auth_file):
                return auth_file
            return os.path.join(self.token_dir, auth_file)

        auth_profile = self._get_litellm_param(litellm_params, "chatgpt_auth_profile")
        if auth_profile is not None:
            profile_name = self._validate_auth_profile(auth_profile)
            return os.path.join(self.token_dir, f"{profile_name}.json")

        return os.path.join(self.token_dir, os.getenv("CHATGPT_AUTH_FILE", "auth.json"))

    def _validate_auth_profile(self, auth_profile: object) -> str:
        profile_name = str(auth_profile).strip()
        if (
            not profile_name
            or profile_name in {".", ".."}
            or os.path.isabs(profile_name)
            or os.path.sep in profile_name
            or (os.path.altsep is not None and os.path.altsep in profile_name)
            or ".." in profile_name
            or _SAFE_AUTH_PROFILE_PATTERN.fullmatch(profile_name) is None
        ):
            raise ValueError(
                "chatgpt_auth_profile must be a logical profile name containing only letters, numbers, '_' or '-'"
            )
        profile_path = os.path.abspath(os.path.join(self.token_dir, f"{profile_name}.json"))
        token_root = os.path.abspath(self.token_dir)
        if os.path.commonpath((token_root, profile_path)) != token_root:
            raise ValueError("chatgpt_auth_profile must resolve inside chatgpt_token_dir")
        return profile_name

    def _get_litellm_param(self, litellm_params: Optional[object], key: str) -> Optional[object]:
        if litellm_params is None:
            return None
        getter = getattr(litellm_params, "get", None)
        if callable(getter):
            return getter(key)
        return getattr(litellm_params, key, None)

    def get_api_base(self) -> str:
        return os.getenv("CHATGPT_API_BASE") or os.getenv("OPENAI_CHATGPT_API_BASE") or CHATGPT_API_BASE

    def get_access_token(self) -> str:
        with _AUTH_LOCKS_GUARD:
            auth_lock = _AUTH_LOCKS.setdefault(os.path.realpath(self.auth_file), threading.RLock())
        with auth_lock:
            with open(f"{self.auth_file}.lock", "a+") as lock_file:
                os.chmod(lock_file.name, 0o600)
                _lock_auth_file(lock_file)
                return self._get_access_token_locked()

    def _get_access_token_locked(self) -> str:
        auth_data = self._read_auth_file()
        if auth_data:
            access_token: Final = auth_data.get("access_token")
            if access_token and not self._is_token_expired(auth_data, access_token):
                return access_token
            refresh_token: Final = auth_data.get("refresh_token")
            if refresh_token:
                try:
                    refreshed: Final = self._refresh_tokens(refresh_token)
                    return refreshed["access_token"]
                except RefreshAccessTokenError as exc:
                    verbose_logger.warning("ChatGPT refresh token failed, re-login required: %s", exc)

        cooldown_remaining: Final = self._get_device_code_cooldown_remaining(auth_data)
        if cooldown_remaining > 0:
            token: Final = self._wait_for_access_token(cooldown_remaining)
            if token:
                return token

        try:
            tokens = self._login_device_code()
        except (GetDeviceCodeError, GetAccessTokenError) as exc:
            raise InteractiveAuthError(message="Interactive ChatGPT authentication failed", status_code=401) from exc
        return tokens["access_token"]

    def get_account_id(self) -> Optional[str]:
        with _AUTH_LOCKS_GUARD:
            auth_lock = _AUTH_LOCKS.setdefault(os.path.realpath(self.auth_file), threading.RLock())
        with auth_lock:
            with open(f"{self.auth_file}.lock", "a+") as lock_file:
                os.chmod(lock_file.name, 0o600)
                _lock_auth_file(lock_file)
                auth_data = self._read_auth_file()
                if not auth_data:
                    return None
                account_id = auth_data.get("account_id")
                if account_id:
                    return account_id
                derived = self._extract_account_id(auth_data.get("id_token") or auth_data.get("access_token"))
                if derived:
                    latest_auth_data = self._read_auth_file() or auth_data
                    self._write_auth_file({**latest_auth_data, "account_id": derived})
                return derived

    def _ensure_token_dir(self) -> None:
        auth_file_dir = os.path.dirname(self.auth_file)
        if auth_file_dir and not os.path.exists(auth_file_dir):
            os.makedirs(auth_file_dir, mode=0o700, exist_ok=True)
            os.chmod(auth_file_dir, 0o700)

    def _read_auth_file(self) -> dict[str, Any] | None:
        try:
            with open(self.auth_file, "r") as f:
                return json.load(f)
        except OSError:
            return None
        except json.JSONDecodeError as exc:
            verbose_logger.warning("Invalid ChatGPT auth file: %s", exc)
            return None

    def _write_auth_file(self, data: Dict[str, Any]) -> None:
        temporary_path: Optional[str] = None
        try:
            auth_file_dir = os.path.dirname(self.auth_file) or "."
            file_descriptor, temporary_path = tempfile.mkstemp(prefix=".chatgpt-auth-", dir=auth_file_dir)
            if hasattr(os, "fchmod"):
                os.fchmod(file_descriptor, 0o600)
            else:  # pragma: no cover - Windows
                os.chmod(temporary_path, 0o600)
            with os.fdopen(file_descriptor, "w") as f:
                json.dump(data, f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary_path, self.auth_file)
            directory_flag = getattr(os, "O_DIRECTORY", None)
            if directory_flag is not None:
                directory_fd = os.open(auth_file_dir, directory_flag)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            temporary_path = None
        except IOError as exc:
            verbose_logger.error("Failed to write ChatGPT auth file: %s", exc)
        finally:
            if temporary_path is not None:
                try:
                    os.unlink(temporary_path)
                except OSError:
                    pass

    def _is_token_expired(self, auth_data: dict[str, Any], access_token: str) -> bool:
        expires_at = auth_data.get("expires_at")
        if expires_at is None:
            expires_at = self._get_expires_at(access_token)
            if expires_at:
                auth_data["expires_at"] = expires_at
                self._write_auth_file(auth_data)
        if expires_at is None:
            return True
        return time.time() >= float(expires_at) - TOKEN_EXPIRY_SKEW_SECONDS

    def _get_expires_at(self, token: str) -> int | None:
        claims: Final = self._decode_jwt_claims(token)
        exp: Final = claims.get("exp")
        if isinstance(exp, (int, float)):
            return int(exp)
        return None

    def _decode_jwt_claims(self, token: str) -> dict[str, Any]:
        try:
            parts: Final = token.split(".")
            if len(parts) < 2:
                return {}
            payload_b64 = parts[1]
            payload_b64 += "=" * (-len(payload_b64) % 4)
            payload_bytes: Final = base64.urlsafe_b64decode(payload_b64)
            return json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            return {}

    def _extract_account_id(self, token: str | None) -> str | None:
        if not token:
            return None
        claims: Final = self._decode_jwt_claims(token)
        auth_claims: Final = claims.get("https://api.openai.com/auth")
        if isinstance(auth_claims, dict):
            account_id: Final = auth_claims.get("chatgpt_account_id")
            if isinstance(account_id, str) and account_id:
                return account_id
        return None

    def _login_device_code(self) -> dict[str, str]:
        cooldown_remaining: Final = self._get_device_code_cooldown_remaining(self._read_auth_file())
        if cooldown_remaining > 0:
            token: Final = self._wait_for_access_token(cooldown_remaining)
            if token:
                return {"access_token": token}

        device_code: Final = self._request_device_code()
        self._record_device_code_request()
        print(  # noqa: T201
            "Sign in with ChatGPT using device code:\n"
            f"1) Visit {CHATGPT_DEVICE_VERIFY_URL}\n"
            f"2) Enter code: {device_code['user_code']}\n"
            "Device codes are a common phishing target. Never share this code.",
            flush=True,
        )
        auth_code: Final = self._poll_for_authorization_code(device_code)
        tokens: Final = self._exchange_code_for_tokens(auth_code)
        auth_data: Final = self._build_auth_record(tokens)
        self._write_auth_file(auth_data)
        return tokens

    def _request_device_code(self) -> dict[str, str]:
        try:
            client: Final = _get_httpx_client()
            resp: Final = client.post(
                CHATGPT_DEVICE_CODE_URL,
                json={"client_id": CHATGPT_CLIENT_ID},
            )
            resp.raise_for_status()
            data: Final = resp.json()
        except httpx.HTTPStatusError as exc:
            raise GetDeviceCodeError(
                message=f"Failed to request device code: {exc}",
                status_code=exc.response.status_code,
            )
        except Exception as exc:
            raise GetDeviceCodeError(
                message=f"Failed to request device code: {exc}",
                status_code=400,
            )

        device_auth_id: Final = data.get("device_auth_id")
        user_code: Final = data.get("user_code") or data.get("usercode")
        interval: Final = data.get("interval")
        if not device_auth_id or not user_code:
            raise GetDeviceCodeError(
                message=f"Device code response missing fields: {data}",
                status_code=400,
            )
        return {
            "device_auth_id": device_auth_id,
            "user_code": user_code,
            "interval": str(interval or "5"),
        }

    def _poll_for_authorization_code(self, device_code: dict[str, str]) -> dict[str, str]:
        client: Final = _get_httpx_client()
        interval: Final = int(device_code.get("interval", "5"))
        start_time: Final = time.time()
        while time.time() - start_time < DEVICE_CODE_TIMEOUT_SECONDS:
            try:
                resp = client.post(
                    CHATGPT_DEVICE_TOKEN_URL,
                    json={
                        "device_auth_id": device_code["device_auth_id"],
                        "user_code": device_code["user_code"],
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if all(
                        key in data
                        for key in (
                            "authorization_code",
                            "code_challenge",
                            "code_verifier",
                        )
                    ):
                        return data
                if resp.status_code in (403, 404):
                    time.sleep(max(interval, DEVICE_CODE_POLL_SLEEP_SECONDS))
                    continue
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code if exc.response else None
                if status_code in (403, 404):
                    time.sleep(max(interval, DEVICE_CODE_POLL_SLEEP_SECONDS))
                    continue
                raise GetAccessTokenError(
                    message=f"Polling failed: {exc}",
                    status_code=exc.response.status_code,
                )
            except Exception as exc:
                raise GetAccessTokenError(
                    message=f"Polling failed: {exc}",
                    status_code=400,
                )
            time.sleep(max(interval, DEVICE_CODE_POLL_SLEEP_SECONDS))

        raise GetAccessTokenError(
            message="Timed out waiting for device authorization",
            status_code=408,
        )

    def _exchange_code_for_tokens(self, code_data: dict[str, str]) -> dict[str, str]:
        try:
            client: Final = _get_httpx_client()
            redirect_uri: Final = f"{CHATGPT_AUTH_BASE}/deviceauth/callback"
            body: Final = (
                "grant_type=authorization_code"
                f"&code={code_data['authorization_code']}"
                f"&redirect_uri={redirect_uri}"
                f"&client_id={CHATGPT_CLIENT_ID}"
                f"&code_verifier={code_data['code_verifier']}"
            )
            resp: Final = client.post(
                CHATGPT_OAUTH_TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                content=body,
            )
            resp.raise_for_status()
            data: Final = resp.json()
        except httpx.HTTPStatusError as exc:
            raise GetAccessTokenError(
                message=f"Token exchange failed: {exc}",
                status_code=exc.response.status_code,
            )
        except Exception as exc:
            raise GetAccessTokenError(
                message=f"Token exchange failed: {exc}",
                status_code=400,
            )

        if not all(key in data for key in ("access_token", "refresh_token", "id_token")):
            raise GetAccessTokenError(
                message=f"Token exchange response missing fields: {data}",
                status_code=400,
            )
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "id_token": data["id_token"],
        }

    def _refresh_tokens(self, refresh_token: str) -> dict[str, str]:
        try:
            client: Final = _get_httpx_client()
            resp: Final = client.post(
                CHATGPT_OAUTH_TOKEN_URL,
                json={
                    "client_id": CHATGPT_CLIENT_ID,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "scope": "openid profile email",
                },
            )
            resp.raise_for_status()
            data: Final = resp.json()
        except httpx.HTTPStatusError as exc:
            raise RefreshAccessTokenError(
                message=f"Refresh token failed: {exc}",
                status_code=exc.response.status_code,
            )
        except Exception as exc:
            raise RefreshAccessTokenError(
                message=f"Refresh token failed: {exc}",
                status_code=400,
            )

        access_token: Final = data.get("access_token")
        id_token: Final = data.get("id_token")
        if not access_token or not id_token:
            raise RefreshAccessTokenError(
                message=f"Refresh response missing fields: {data}",
                status_code=400,
            )

        refreshed: Final = {
            "access_token": access_token,
            "refresh_token": data.get("refresh_token", refresh_token),
            "id_token": id_token,
        }
        auth_data: Final = self._build_auth_record(refreshed)
        self._write_auth_file(auth_data)
        return refreshed

    def _build_auth_record(self, tokens: dict[str, str]) -> dict[str, Any]:
        access_token: Final = tokens.get("access_token")
        id_token: Final = tokens.get("id_token")
        expires_at: Final = self._get_expires_at(access_token) if access_token else None
        account_id: Final = self._extract_account_id(id_token or access_token)
        return {
            "access_token": access_token,
            "refresh_token": tokens.get("refresh_token"),
            "id_token": id_token,
            "expires_at": expires_at,
            "account_id": account_id,
        }

    def _get_device_code_cooldown_remaining(self, auth_data: dict[str, Any] | None) -> float:
        if not auth_data:
            return 0.0
        requested_at = auth_data.get("device_code_requested_at")
        if not isinstance(requested_at, (int, float, str)):
            return 0.0
        try:
            requested_at = float(requested_at)
        except (TypeError, ValueError):
            return 0.0
        elapsed: Final = time.time() - requested_at
        remaining: Final = DEVICE_CODE_COOLDOWN_SECONDS - elapsed
        return max(0.0, remaining)

    def _record_device_code_request(self) -> None:
        auth_data: Final = self._read_auth_file() or {}
        auth_data["device_code_requested_at"] = time.time()
        self._write_auth_file(auth_data)

    def _wait_for_access_token(self, timeout_seconds: float) -> str | None:
        deadline: Final = time.time() + timeout_seconds
        while time.time() < deadline:
            auth_data = self._read_auth_file()
            if auth_data:
                access_token = auth_data.get("access_token")
                if access_token and not self._is_token_expired(auth_data, access_token):
                    return access_token
            sleep_for = min(DEVICE_CODE_POLL_SLEEP_SECONDS, max(0.0, deadline - time.time()))
            if sleep_for <= 0:
                break
            time.sleep(sleep_for)
        return None
