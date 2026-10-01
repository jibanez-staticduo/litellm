import os
import re
import tempfile
import threading
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Annotated, Final, Literal, NoReturn, TypeAlias, assert_never

import httpx
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, SecretStr, ValidationError

from .common_utils import AnthropicError, is_anthropic_oauth_key

ANTHROPIC_OAUTH_TOKEN_URL: Final = "https://platform.claude.com/v1/oauth/token"
ANTHROPIC_OAUTH_CLIENT_ID: Final = "9d1c250a-e61b-44d9-88ed-5944d1962f5e"
TOKEN_EXPIRY_SKEW_SECONDS: Final = 60
_PROFILE_PATTERN: Final = re.compile(r"^[A-Za-z0-9_-]+$")
_PositiveSeconds: TypeAlias = Annotated[float, Field(strict=True, gt=0, allow_inf_nan=False)]
_Token: TypeAlias = Annotated[SecretStr, Field(min_length=1)]
_ScopeList: TypeAlias = Annotated[tuple[str, ...], Field(strict=False)]


class AnthropicOAuthConfig(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, hide_input_in_errors=True)

    use_anthropic_oauth: bool = False
    anthropic_auth_profile: str = "default"
    anthropic_token_dir: str | None = None


class AnthropicAuthError(AnthropicError):
    pass


class _Credential(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, hide_input_in_errors=True)

    access_token: _Token = Field(repr=False)
    refresh_token: _Token | None = Field(default=None, repr=False)
    expires_at: _PositiveSeconds = Field(
        validation_alias=AliasChoices("expires_at", "expires_at_s", "expires_at_seconds")
    )
    scope: str | _ScopeList = Field(validation_alias=AliasChoices("scope", "scopes"))


class _NativeCredential(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, hide_input_in_errors=True)

    accessToken: _Token = Field(repr=False)
    refreshToken: _Token | None = Field(default=None, repr=False)
    expiresAt: _PositiveSeconds
    scopes: tuple[str, ...] = Field(strict=False)


class _NativeImport(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, hide_input_in_errors=True)

    claudeAiOauth: _NativeCredential


class _RefreshResponse(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, hide_input_in_errors=True)

    access_token: _Token = Field(repr=False)
    refresh_token: _Token | None = Field(default=None, repr=False)
    expires_in: _PositiveSeconds
    scope: str | _ScopeList | None = None
    token_type: Literal["Bearer", "bearer"] = "Bearer"


class _PersistedCredential(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, hide_input_in_errors=True)

    access_token: str = Field(repr=False)
    refresh_token: str | None = Field(repr=False)
    expires_at: float
    scope: str


class _RefreshRequest(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, hide_input_in_errors=True)

    client_id: str = ANTHROPIC_OAUTH_CLIENT_ID
    grant_type: Literal["refresh_token"] = "refresh_token"
    refresh_token: str = Field(repr=False)
    scope: str


@dataclass(frozen=True, slots=True)
class _AuthFailure:
    kind: Literal["disabled", "profile", "missing", "invalid", "scope", "refresh", "storage"]


def _raise_public(failure: _AuthFailure) -> NoReturn:
    match failure.kind:
        case "disabled":
            raise AnthropicAuthError(401, "Central Anthropic OAuth is not enabled") from None
        case "profile":
            raise AnthropicAuthError(401, "Anthropic OAuth profile must resolve inside its token directory") from None
        case "missing":
            raise AnthropicAuthError(401, "Anthropic OAuth profile is missing; import credentials explicitly") from None
        case "invalid":
            raise AnthropicAuthError(401, "Anthropic OAuth profile contains invalid credentials") from None
        case "scope":
            raise AnthropicAuthError(401, "Anthropic OAuth credentials require user:inference scope") from None
        case "refresh":
            raise AnthropicAuthError(401, "Anthropic OAuth refresh failed; authorize the profile again") from None
        case "storage":
            raise AnthropicError(503, "Anthropic OAuth credential storage is unavailable") from None
    assert_never(failure.kind)


def _scopes(credential: _Credential) -> tuple[str, ...]:
    return tuple(credential.scope.split()) if isinstance(credential.scope, str) else credential.scope


def _validate_credential(credential: _Credential) -> _Credential | _AuthFailure:
    tokens: Final = (credential.access_token, credential.refresh_token)
    if any(token is not None and any(char.isspace() for char in token.get_secret_value()) for token in tokens):
        return _AuthFailure("invalid")
    if not is_anthropic_oauth_key(credential.access_token.get_secret_value()):
        return _AuthFailure("invalid")
    if "user:inference" not in _scopes(credential):
        return _AuthFailure("scope")
    return credential


def _read_credential(source: Path, *, native_import: bool = False) -> _Credential | _AuthFailure:
    try:
        descriptor: Final = os.open(source, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "rb") as handle:
            contents: Final = handle.read()
    except FileNotFoundError:
        return _AuthFailure("missing")
    except OSError:
        return _AuthFailure("storage")
    try:
        if native_import:
            native: Final = _NativeImport.model_validate_json(contents).claudeAiOauth
            credential: Final = _Credential(
                access_token=native.accessToken,
                refresh_token=native.refreshToken,
                expires_at=native.expiresAt / 1000,
                scope=native.scopes,
            )
            return _validate_credential(credential)
        return _validate_credential(_Credential.model_validate_json(contents))
    except ValidationError:
        return _AuthFailure("invalid")


def _write_credential(target: Path, credential: _Credential) -> _AuthFailure | None:
    try:
        descriptor, temporary_name = tempfile.mkstemp(prefix=".anthropic-auth-", dir=target.parent)
    except OSError:
        return _AuthFailure("storage")
    temporary_path: Final = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w") as handle:
            os.fchmod(handle.fileno(), 0o600)
            serialized: Final = _PersistedCredential(
                access_token=credential.access_token.get_secret_value(),
                refresh_token=(
                    credential.refresh_token.get_secret_value() if credential.refresh_token is not None else None
                ),
                expires_at=credential.expires_at,
                scope=" ".join(_scopes(credential)),
            )
            handle.write(serialized.model_dump_json())
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, target)
        directory_descriptor: Final = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except OSError:
        return _AuthFailure("storage")
    else:
        return None
    finally:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass


class AnthropicAuthenticator:
    def __init__(
        self,
        config: AnthropicOAuthConfig,
        http_client: httpx.Client | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._config = config
        self._http_client = http_client
        self._clock = clock
        self._thread_lock = threading.RLock()
        self._token_dir = (
            Path(
                config.anthropic_token_dir
                or os.environ.get("ANTHROPIC_OAUTH_TOKEN_DIR")
                or "~/.config/litellm/anthropic"
            )
            .expanduser()
            .resolve()
        )

    def _profile_path(self) -> Path | _AuthFailure:
        profile: Final = self._config.anthropic_auth_profile
        if _PROFILE_PATTERN.fullmatch(profile) is None:
            return _AuthFailure("profile")
        filename: Final = "auth.json" if profile == "default" else f"{profile}.json"
        path: Final = (self._token_dir / filename).resolve()
        if path.parent != self._token_dir:
            return _AuthFailure("profile")
        return path

    @contextmanager
    def _profile_lock(self, path: Path) -> Generator[None]:
        import fcntl

        with self._thread_lock:
            self._token_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
            descriptor: Final = os.open(f"{path}.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            with os.fdopen(descriptor, "a+") as lock_file:
                os.fchmod(lock_file.fileno(), 0o600)
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def get_access_token(self) -> str:
        if not self._config.use_anthropic_oauth:
            _raise_public(_AuthFailure("disabled"))
        path: Final = self._profile_path()
        if isinstance(path, _AuthFailure):
            _raise_public(path)
        try:
            with self._profile_lock(path):
                result: Final = self._get_access_token_locked(path)
        except (OSError, ImportError):
            _raise_public(_AuthFailure("storage"))
        if isinstance(result, _AuthFailure):
            _raise_public(result)
        return result

    def _get_access_token_locked(self, path: Path) -> str | _AuthFailure:
        credential: Final = _read_credential(path)
        if isinstance(credential, _AuthFailure):
            return credential
        if self._clock() < credential.expires_at - TOKEN_EXPIRY_SKEW_SECONDS:
            return credential.access_token.get_secret_value()
        refreshed: Final = self._refresh(credential)
        if isinstance(refreshed, _AuthFailure):
            return refreshed
        persisted: Final = _write_credential(path, refreshed)
        return persisted if persisted is not None else refreshed.access_token.get_secret_value()

    def _refresh(self, credential: _Credential) -> _Credential | _AuthFailure:
        if credential.refresh_token is None:
            return _AuthFailure("refresh")
        if self._http_client is not None:
            return self._refresh_using_client(credential, self._http_client)
        with httpx.Client() as client:
            return self._refresh_using_client(credential, client)

    def _refresh_using_client(self, credential: _Credential, client: httpx.Client) -> _Credential | _AuthFailure:
        if credential.refresh_token is None:
            return _AuthFailure("refresh")
        payload: Final = _RefreshRequest(
            refresh_token=credential.refresh_token.get_secret_value(), scope=" ".join(_scopes(credential))
        )
        try:
            response: Final = client.post(
                ANTHROPIC_OAUTH_TOKEN_URL,
                content=payload.model_dump_json(),
                headers=MappingProxyType({"Content-Type": "application/json"}),
                timeout=30,
                follow_redirects=False,
            )
            if response.status_code != 200:
                return _AuthFailure("refresh")
            refreshed: Final = _RefreshResponse.model_validate_json(response.content)
        except (httpx.HTTPError, ValidationError):
            return _AuthFailure("refresh")
        return _validate_credential(
            _Credential(
                access_token=refreshed.access_token,
                refresh_token=refreshed.refresh_token or credential.refresh_token,
                expires_at=self._clock() + refreshed.expires_in,
                scope=refreshed.scope if refreshed.scope is not None else credential.scope,
            )
        )

    def import_credentials(self, source_path: str | Path) -> None:
        path: Final = self._profile_path()
        if isinstance(path, _AuthFailure):
            _raise_public(path)
        source: Final = Path(source_path).expanduser()
        legacy: Final = _read_credential(source)
        credential: Final = (
            _read_credential(source, native_import=True)
            if isinstance(legacy, _AuthFailure) and legacy.kind == "invalid"
            else legacy
        )
        if isinstance(credential, _AuthFailure):
            _raise_public(credential)
        try:
            with self._profile_lock(path):
                persisted: Final = _write_credential(path, credential)
        except (OSError, ImportError):
            _raise_public(_AuthFailure("storage"))
        if persisted is not None:
            _raise_public(persisted)
