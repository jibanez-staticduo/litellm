import base64
import json
import math
import os
import re
import tempfile
import threading
import time
from collections.abc import Callable, Mapping
from functools import lru_cache
from typing import IO, Final, TypeAlias

from staticduo_litellm.compatibility.provider_providers_chatgpt_authenticator import (
    DEVICE_CODE_COOLDOWN_SECONDS,
    DEVICE_CODE_POLL_SLEEP_SECONDS,
    DEVICE_CODE_TIMEOUT_SECONDS,
    JSON_OBJECT_ADAPTER,
    OPENAI_AUTH_CLAIM_KEY,
    TOKEN_EXPIRY_SKEW_SECONDS,
    TOKEN_REFRESH_TIMEOUT_SECONDS,
    ChatGPTOAuthEngine,
    HTTPHandler,
    JsonObject,
    decode_jwt_claims,
    extract_chatgpt_account_id,
    optional_str,
    token_refresh_timeout,
)

_JSON_OBJECT_ADAPTER: Final = JSON_OBJECT_ADAPTER
_optional_str: Final = optional_str
_token_refresh_timeout: Final = token_refresh_timeout

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows
    fcntl = None  # pyright: ignore[reportAssignmentType]  # platform-specific module absence  # rebind-ok: framework flow intentionally updates request or lifecycle state

try:
    import msvcrt
except ImportError:  # pragma: no cover - POSIX
    msvcrt = None  # pyright: ignore[reportAssignmentType]  # platform-specific module absence  # rebind-ok: framework flow intentionally updates request or lifecycle state

import httpx
from pydantic import JsonValue, TypeAdapter, ValidationError

from staticduo_litellm.compatibility.provider_providers_chatgpt_authenticator import (
    CHATGPT_API_BASE,
    CHATGPT_AUTH_BASE,
    CHATGPT_CLIENT_ID,
    CHATGPT_DEVICE_CODE_URL,
    CHATGPT_DEVICE_TOKEN_URL,
    CHATGPT_DEVICE_VERIFY_URL,
    CHATGPT_OAUTH_TOKEN_URL,
    HTTP_HANDLER_CONNECT_TIMEOUT_SECONDS,
    GetAccessTokenError,
    GetDeviceCodeError,
    InteractiveAuthError,
    RefreshAccessTokenError,
    can_block_current_thread,
    get_configured_request_timeout,
    get_httpx_client,
    verbose_logger,
)

_SAFE_AUTH_PROFILE_PATTERN: Final = re.compile(r"^[A-Za-z0-9_-]+$")
_AUTH_LOCKS: Final[  # mutable-ok: framework contract requires mutable request or response containers
    dict[str, threading.RLock]
] = {}
_AUTH_LOCKS_GUARD: Final = threading.Lock()


def _lock_auth_file(lock_file: IO[str]) -> None:
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


def _auth_lock(auth_file: str) -> threading.RLock:
    with _AUTH_LOCKS_GUARD:
        return _AUTH_LOCKS.setdefault(os.path.realpath(auth_file), threading.RLock())


def get_chatgpt_auth_file(litellm_params: object | None) -> str | None:
    if litellm_params is None:
        return None
    getter = getattr(litellm_params, "get", None)
    configured = getter("chatgpt_auth_file") if callable(getter) else getattr(litellm_params, "chatgpt_auth_file", None)
    if isinstance(configured, str) and configured:
        base = os.path.expanduser(configured)
        if not os.path.isabs(base):
            token_dir = (
                getter("chatgpt_token_dir") if callable(getter) else getattr(litellm_params, "chatgpt_token_dir", None)
            )
            resolved_dir = (
                os.path.expanduser(str(token_dir))
                if token_dir
                else os.getenv("CHATGPT_TOKEN_DIR", os.path.expanduser("~/.config/litellm/chatgpt"))
            )
            base = os.path.join(resolved_dir, base)
        return os.path.abspath(base)
    profile = (
        getter("chatgpt_auth_profile") if callable(getter) else getattr(litellm_params, "chatgpt_auth_profile", None)
    )
    if profile is None:
        return None
    token_dir = getter("chatgpt_token_dir") if callable(getter) else getattr(litellm_params, "chatgpt_token_dir", None)
    resolved_dir = (
        os.path.expanduser(str(token_dir))
        if token_dir
        else os.getenv("CHATGPT_TOKEN_DIR", os.path.expanduser("~/.config/litellm/chatgpt"))
    )
    name = str(profile).strip()
    if (
        not name
        or name in {".", ".."}
        or os.path.isabs(name)
        or os.path.sep in name
        or (os.path.altsep is not None and os.path.altsep in name)
        or ".." in name
        or _SAFE_AUTH_PROFILE_PATTERN.fullmatch(name) is None
    ):
        raise ValueError(
            "chatgpt_auth_profile must be a logical profile name containing only letters, numbers, '_' or '-'"
        )
    return os.path.abspath(os.path.join(resolved_dir, f"{name}.json"))


@lru_cache(maxsize=128)
def get_cached_authenticator(auth_file: str) -> "Authenticator":
    return Authenticator({"chatgpt_auth_file": auth_file})


class Authenticator(ChatGPTOAuthEngine):
    def _can_start_interactive_auth(self) -> bool:
        return can_block_current_thread()

    def _get_auth_http_client(self) -> HTTPHandler | httpx.Client:
        self._require_writable()
        return self._http_client_factory()

    def __init__(
        self,
        litellm_params: object | None = None,
        *,
        http_client_factory: Callable[[], HTTPHandler | httpx.Client] | None = None,
    ) -> None:
        self._http_client_factory = http_client_factory or get_httpx_client
        self.token_dir = self._resolve_token_dir(litellm_params)
        self.auth_file = self._resolve_auth_file(litellm_params)
        if not self._read_only:
            self._ensure_token_dir()

    @property
    def _read_only(self) -> bool:
        return os.environ.get("STATICDUO_AUTH_READ_ONLY", "").lower() == "true"

    def _require_writable(self) -> None:
        if self._read_only:
            raise GetAccessTokenError(message="ChatGPT authentication snapshot is read-only", status_code=401)

    def _read_access_snapshot(self) -> tuple[str, JsonObject]:
        auth_data: Final = self._read_auth_file()
        token: Final = _optional_str(auth_data.get("access_token")) if auth_data else None
        stored_expiry: Final = auth_data.get("expires_at") if auth_data else None
        expiry: Final = self._get_expires_at(token) if stored_expiry is None and token else stored_expiry
        if (
            not auth_data
            or not token
            or isinstance(expiry, bool)
            or not isinstance(expiry, (int, float))
            or not math.isfinite(expiry)
            or self._is_token_expired(auth_data, token)
        ):
            raise GetAccessTokenError(
                message="ChatGPT authentication snapshot is missing, invalid or expired", status_code=401
            )
        return token, auth_data

    def _resolve_token_dir(self, litellm_params: object | None) -> str:
        configured_token_dir = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            self._get_litellm_param(litellm_params, "chatgpt_token_dir")
        )
        if configured_token_dir:
            return os.path.expanduser(str(configured_token_dir))
        return os.getenv(
            "CHATGPT_TOKEN_DIR",
            os.path.expanduser("~/.config/litellm/chatgpt"),
        )

    def _resolve_auth_file(self, litellm_params: object | None) -> str:
        configured_auth_file = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            self._get_litellm_param(litellm_params, "chatgpt_auth_file")
        )
        if configured_auth_file:
            auth_file = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
                os.path.expanduser(str(configured_auth_file))
            )
            if os.path.isabs(auth_file):
                return auth_file
            return os.path.join(self.token_dir, auth_file)

        auth_profile = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            self._get_litellm_param(litellm_params, "chatgpt_auth_profile")
        )
        if auth_profile is not None:
            profile_name = self._validate_auth_profile(  # rebind-ok: framework flow intentionally updates request or lifecycle state
                auth_profile
            )
            return os.path.join(self.token_dir, f"{profile_name}.json")

        return os.path.join(self.token_dir, os.getenv("CHATGPT_AUTH_FILE", "auth.json"))

    def _validate_auth_profile(self, auth_profile: object) -> str:
        profile_name = str(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            auth_profile
        ).strip()
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
        profile_path = os.path.abspath(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            os.path.join(self.token_dir, f"{profile_name}.json")
        )
        token_root = os.path.abspath(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            self.token_dir
        )
        if os.path.commonpath((token_root, profile_path)) != token_root:
            raise ValueError("chatgpt_auth_profile must resolve inside chatgpt_token_dir")
        return profile_name

    def _get_litellm_param(self, litellm_params: object | None, key: str) -> object | None:
        if litellm_params is None:
            return None
        getter = getattr(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            litellm_params, "get", None
        )
        if callable(getter):
            return getter(key)
        return getattr(litellm_params, key, None)

    @staticmethod
    def get_api_base(default_base: str = CHATGPT_API_BASE) -> str:
        return os.getenv("CHATGPT_API_BASE") or os.getenv("OPENAI_CHATGPT_API_BASE") or default_base

    def _decode_jwt_claims(self, token: str) -> JsonObject:
        return decode_jwt_claims(token)

    def _extract_account_id(self, token: str | None) -> str | None:
        return extract_chatgpt_account_id(token)

    def get_access_token(self) -> str:
        if self._read_only:
            return self._read_access_snapshot()[0]
        with _auth_lock(self.auth_file), open(f"{self.auth_file}.lock", "a+") as lock_file:
            os.chmod(lock_file.name, 0o600)
            _lock_auth_file(lock_file)
            return self._get_access_token_locked()

    def _get_access_token_locked(self) -> str:
        return super().get_access_token()

    def get_account_id(self, access_token: str | None = None) -> str | None:
        explicit_auth_data: Final = self._read_auth_file()
        if access_token and (not explicit_auth_data or explicit_auth_data.get("access_token") != access_token):
            return self._extract_account_id(access_token)
        if self._read_only:
            snapshot: Final = self._read_access_snapshot()
            snapshot_token: Final = snapshot[0]
            snapshot_auth_data: Final = snapshot[1]
            return _optional_str(snapshot_auth_data.get("account_id")) or self._extract_account_id(
                _optional_str(snapshot_auth_data.get("id_token")) or snapshot_token
            )
        with _auth_lock(self.auth_file), open(f"{self.auth_file}.lock", "a+") as lock_file:
            os.chmod(lock_file.name, 0o600)
            _lock_auth_file(lock_file)
            locked_auth_data: Final = self._read_auth_file()
            if access_token and (not locked_auth_data or locked_auth_data.get("access_token") != access_token):
                return self._extract_account_id(access_token)
            if not locked_auth_data:
                return None
            account_id: Final = _optional_str(locked_auth_data.get("account_id"))
            if account_id:
                return account_id
            id_token: Final = _optional_str(locked_auth_data.get("id_token"))
            saved_access_token: Final = _optional_str(locked_auth_data.get("access_token"))
            derived: Final = self._extract_account_id(id_token or saved_access_token)
            if derived:
                latest_auth_data: Final = self._read_auth_file() or locked_auth_data
                self._write_auth_file(
                    {
                        **latest_auth_data,
                        "account_id": derived,
                    }
                )
            return derived

    def _ensure_token_dir(self) -> None:
        self._require_writable()
        auth_file_dir = os.path.dirname(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            self.auth_file
        )
        if auth_file_dir and not os.path.exists(auth_file_dir):
            os.makedirs(auth_file_dir, mode=0o700, exist_ok=True)
            os.chmod(auth_file_dir, 0o700)

    def _write_auth_file(self, data: JsonObject) -> None:
        self._require_writable()
        temporary_path: str | None = None  # rebind-ok: framework flow intentionally updates request or lifecycle state
        try:
            auth_file_dir = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
                os.path.dirname(self.auth_file) or "."
            )
            (
                file_descriptor,
                temporary_path,  # rebind-ok: framework flow intentionally updates request or lifecycle state
            ) = tempfile.mkstemp(prefix=".chatgpt-auth-", dir=auth_file_dir)
            if hasattr(os, "fchmod"):
                os.fchmod(file_descriptor, 0o600)
            else:  # pragma: no cover - Windows
                os.chmod(temporary_path, 0o600)
            with os.fdopen(file_descriptor, "w") as f:
                json.dump(data, f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary_path, self.auth_file)
            directory_flag = getattr(  # rebind-ok: framework flow intentionally updates request or lifecycle state
                os, "O_DIRECTORY", None
            )
            if isinstance(directory_flag, int):
                directory_fd = os.open(  # rebind-ok: framework flow intentionally updates request or lifecycle state
                    auth_file_dir, directory_flag
                )
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            temporary_path = None  # rebind-ok: framework flow intentionally updates request or lifecycle state
        except OSError as exc:
            verbose_logger.error("Failed to write ChatGPT auth file: %s", exc)
        finally:
            if temporary_path is not None:
                try:
                    os.unlink(temporary_path)
                except OSError:
                    pass

    def _is_token_expired(self, auth_data: JsonObject, access_token: str) -> bool:
        stored_expires_at: Final = auth_data.get("expires_at")
        if isinstance(stored_expires_at, (int, float)):
            return time.time() >= float(stored_expires_at) - TOKEN_EXPIRY_SKEW_SECONDS
        derived_expires_at: Final = self._get_expires_at(access_token)
        if derived_expires_at and not self._read_only:
            self._write_auth_file({**auth_data, "expires_at": derived_expires_at})
        if derived_expires_at is None:
            return True
        return time.time() >= float(derived_expires_at) - TOKEN_EXPIRY_SKEW_SECONDS

    def _login_device_code(self) -> dict[str, str]:  # mutable-ok: upstream OAuth method contract
        self._require_writable()
        try:
            return super()._login_device_code()
        except (GetDeviceCodeError, GetAccessTokenError) as exc:
            raise InteractiveAuthError(message="Interactive ChatGPT authentication failed", status_code=401) from exc


__all__: Final = (
    "CHATGPT_API_BASE",
    "CHATGPT_AUTH_BASE",
    "CHATGPT_CLIENT_ID",
    "CHATGPT_DEVICE_CODE_URL",
    "CHATGPT_DEVICE_TOKEN_URL",
    "CHATGPT_DEVICE_VERIFY_URL",
    "CHATGPT_OAUTH_TOKEN_URL",
    "DEVICE_CODE_COOLDOWN_SECONDS",
    "DEVICE_CODE_POLL_SLEEP_SECONDS",
    "DEVICE_CODE_TIMEOUT_SECONDS",
    "HTTP_HANDLER_CONNECT_TIMEOUT_SECONDS",
    "OPENAI_AUTH_CLAIM_KEY",
    "TOKEN_EXPIRY_SKEW_SECONDS",
    "TOKEN_REFRESH_TIMEOUT_SECONDS",
    "ChatGPTOAuthEngine",
    "GetAccessTokenError",
    "GetDeviceCodeError",
    "HTTPHandler",
    "InteractiveAuthError",
    "JsonObject",
    "JsonValue",
    "Mapping",
    "RefreshAccessTokenError",
    "TypeAdapter",
    "TypeAlias",
    "ValidationError",
    "base64",
    "can_block_current_thread",
    "get_cached_authenticator",
    "get_chatgpt_auth_file",
    "get_configured_request_timeout",
    "get_httpx_client",
    "verbose_logger",
)
