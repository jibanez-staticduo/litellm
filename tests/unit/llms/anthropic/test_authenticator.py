import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue
from types import MappingProxyType
from typing import Final

import httpx
import pytest
from pydantic import BaseModel, ConfigDict

from litellm.llms.anthropic.authenticator import (
    ANTHROPIC_OAUTH_CLIENT_ID,
    ANTHROPIC_OAUTH_TOKEN_URL,
    AnthropicAuthenticator,
    AnthropicAuthError,
    AnthropicOAuthConfig,
)
from litellm.llms.anthropic.common_utils import AnthropicError

_NOW: Final = 2000.0
_REFRESH_BODY: Final = (
    '{"access_token":"sk-ant-oat01-fresh-access","refresh_token":"sk-ant-ort01-rotated-refresh",'
    '"expires_in":3600,"scope":"user:inference user:profile","token_type":"Bearer"}'
)


class _FixtureCredential(BaseModel):
    model_config = ConfigDict(frozen=True)

    access_token: str = "sk-ant-oat01-old-access"
    refresh_token: str | None = "sk-ant-ort01-old-refresh"
    expires_at: float = _NOW - 100
    scope: str = "user:inference user:profile"


class _FixtureRefreshRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    client_id: str
    grant_type: str
    refresh_token: str
    scope: str


def _config(directory: Path, profile: str = "default") -> AnthropicOAuthConfig:
    return AnthropicOAuthConfig(
        use_anthropic_oauth=True, anthropic_auth_profile=profile, anthropic_token_dir=str(directory)
    )


def _write(path: Path, credential: _FixtureCredential = _FixtureCredential()) -> None:
    path.write_text(credential.model_dump_json())


def _reject_network(request: httpx.Request) -> httpx.Response:
    pytest.fail("A valid or invalid offline profile must not trigger HTTP")


def _auth(directory: Path, profile: str = "default") -> AnthropicAuthenticator:
    return AnthropicAuthenticator(
        _config(directory, profile),
        http_client=httpx.Client(transport=httpx.MockTransport(_reject_network)),
        clock=lambda: _NOW,
    )


def test_valid_opaque_token_and_named_profile_remain_isolated(tmp_path: Path) -> None:
    _write(
        tmp_path / "auth.json", _FixtureCredential(access_token="sk-ant-oat01-default-access", expires_at=_NOW + 200)
    )
    _write(
        tmp_path / "account2.json",
        _FixtureCredential(access_token="sk-ant-oat01-account2-access", expires_at=_NOW + 200),
    )

    assert _auth(tmp_path).get_access_token() == "sk-ant-oat01-default-access"
    assert _auth(tmp_path, "account2").get_access_token() == "sk-ant-oat01-account2-access"


@pytest.mark.parametrize("profile", ("../outside", "/outside", "two/accounts", "..", "", "one\\account"))
def test_invalid_profile_cannot_read_outside_directory(tmp_path: Path, profile: str) -> None:
    with pytest.raises(AnthropicAuthError, match="inside its token directory"):
        _auth(tmp_path, profile).get_access_token()


def test_profile_symlink_outside_directory_is_rejected(tmp_path: Path) -> None:
    outside: Final = tmp_path / "outside"
    outside.mkdir()
    _write(outside / "credentials.json", _FixtureCredential(expires_at=_NOW + 200))
    directory: Final = tmp_path / "profiles"
    directory.mkdir()
    (directory / "auth.json").symlink_to(outside / "credentials.json")

    with pytest.raises(AnthropicAuthError, match="inside its token directory"):
        _auth(directory).get_access_token()


@pytest.mark.parametrize(
    "contents",
    (
        "not-json",
        '{"access_token":"sk-ant-oat01-private-access","refresh_token":"sk-ant-ort01-private-refresh"}',
        '{"access_token":"sk-ant-oat01-private-access","expires_at":"tomorrow","scope":"user:inference"}',
        '{"access_token":"sk-ant-oat01-private-access","expires_at":true,"scope":"user:inference"}',
        '{"access_token":"sk-ant-oat01-private-access","expires_at":NaN,"scope":"user:inference"}',
        '{"access_token":"sk-ant-oat01-private-access","expires_at":5000,"scope":[42,"user:inference"]}',
        '{"access_token":"bad token","expires_at":5000,"scope":"user:inference"}',
        '{"claudeAiOauth":{"accessToken":"sk-ant-oat01-private-access","expiresAt":5000000,"scopes":["user:inference"]}}',
    ),
)
def test_invalid_credentials_fail_without_exposing_secrets(tmp_path: Path, contents: str) -> None:
    (tmp_path / "auth.json").write_text(contents)

    with pytest.raises(AnthropicAuthError, match="invalid credentials") as caught:
        _auth(tmp_path).get_access_token()

    assert "sk-ant-oat01-private-access" not in str(caught.value)
    assert "sk-ant-ort01-private-refresh" not in str(caught.value)
    assert caught.value.__cause__ is None
    assert (tmp_path / "auth.json").read_text() == contents


@pytest.mark.parametrize("scope", ("user:profile", "user:inference-extra", ""))
def test_inference_scope_is_required(tmp_path: Path, scope: str) -> None:
    _write(tmp_path / "auth.json", _FixtureCredential(expires_at=_NOW + 200, scope=scope))

    with pytest.raises(AnthropicAuthError, match="require user:inference"):
        _auth(tmp_path).get_access_token()


@pytest.mark.parametrize("token", ("sk-ant-api03-private", "sk-ant-ort01-private", "Bearer sk-ant-oat01-private"))
def test_api_keys_and_refresh_tokens_are_never_used_for_inference(tmp_path: Path, token: str) -> None:
    _write(tmp_path / "auth.json", _FixtureCredential(access_token=token, expires_at=_NOW + 200))

    with pytest.raises(AnthropicAuthError, match="invalid credentials"):
        _auth(tmp_path).get_access_token()


def test_missing_profile_fails_without_interactive_login(tmp_path: Path) -> None:
    with pytest.raises(AnthropicAuthError, match="import credentials explicitly"):
        _auth(tmp_path).get_access_token()

    assert not (tmp_path / "auth.json").exists()


def test_disabled_authentication_does_not_read_credentials(tmp_path: Path) -> None:
    authenticator: Final = AnthropicAuthenticator(AnthropicOAuthConfig(anthropic_token_dir=str(tmp_path)))

    with pytest.raises(AnthropicAuthError, match="not enabled"):
        authenticator.get_access_token()

    assert not tuple(tmp_path.iterdir())


@pytest.mark.parametrize("share_instance", (False, True))
def test_concurrent_instances_refresh_once_and_persist_rotated_pair(tmp_path: Path, share_instance: bool) -> None:
    directory: Final = tmp_path / "profiles"
    directory.mkdir()
    alias: Final = tmp_path / "alias"
    alias.symlink_to(directory, target_is_directory=True)
    _write(directory / "auth.json")
    requests: Final[Queue[httpx.Request]] = Queue()

    def refresh(request: httpx.Request) -> httpx.Response:
        requests.put(request)
        return httpx.Response(200, content=_REFRESH_BODY)

    client: Final = httpx.Client(transport=httpx.MockTransport(refresh))
    barrier: Final = threading.Barrier(8)
    distinct_authenticators: Final = tuple(
        AnthropicAuthenticator(_config(directory if index % 2 == 0 else alias), http_client=client, clock=lambda: _NOW)
        for index in range(8)
    )
    authenticators: Final = (distinct_authenticators[0],) * 8 if share_instance else distinct_authenticators

    def obtain(authenticator: AnthropicAuthenticator) -> str:
        barrier.wait()
        return authenticator.get_access_token()

    with ThreadPoolExecutor(max_workers=8) as executor:
        results: Final = tuple(executor.map(obtain, authenticators))

    assert results == ("sk-ant-oat01-fresh-access",) * len(authenticators)
    assert requests.qsize() == 1
    request: Final = requests.get_nowait()
    payload: Final = _FixtureRefreshRequest.model_validate_json(request.content)
    assert str(request.url) == ANTHROPIC_OAUTH_TOKEN_URL
    assert payload.client_id == ANTHROPIC_OAUTH_CLIENT_ID
    assert payload.grant_type == "refresh_token"
    assert payload.refresh_token == "sk-ant-ort01-old-refresh"
    assert "user:inference" in payload.scope.split()
    stored: Final = _FixtureCredential.model_validate_json((directory / "auth.json").read_bytes())
    assert stored.access_token == "sk-ant-oat01-fresh-access"
    assert stored.refresh_token == "sk-ant-ort01-rotated-refresh"
    assert stored.expires_at == _NOW + 3600
    assert os.stat(directory / "auth.json").st_mode & 0o777 == 0o600
    assert os.stat(directory / "auth.json.lock").st_mode & 0o777 == 0o600
    assert not tuple(directory.glob(".anthropic-auth-*"))


@pytest.mark.parametrize(
    ("status", "body"),
    (
        (400, '{"error_description":"sk-ant-ort01-private-refresh"}'),
        (302, ""),
        (200, '{"access_token":"sk-ant-oat01-private-access","expires_in":-1}'),
        (200, '{"access_token":"sk-ant-oat01-private-access","expires_in":3600,"scope":"user:profile"}'),
        (200, '{"access_token":"sk-ant-api03-private","expires_in":3600,"scope":"user:inference"}'),
        (200, '{"access_token":"sk-ant-ort01-private","expires_in":3600,"scope":"user:inference"}'),
    ),
)
def test_refresh_failure_preserves_profile_and_sanitizes_error(tmp_path: Path, status: int, body: str) -> None:
    _write(tmp_path / "auth.json")
    original: Final = (tmp_path / "auth.json").read_bytes()

    def refresh(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, content=body, headers=MappingProxyType({"Location": "https://example.com"}))

    authenticator: Final = AnthropicAuthenticator(
        _config(tmp_path), http_client=httpx.Client(transport=httpx.MockTransport(refresh)), clock=lambda: _NOW
    )

    with pytest.raises(AnthropicAuthError) as caught:
        authenticator.get_access_token()

    assert "sk-ant-oat01-private-access" not in str(caught.value)
    assert "sk-ant-ort01-private-refresh" not in str(caught.value)
    assert (tmp_path / "auth.json").read_bytes() == original


def test_refresh_transport_failure_is_sanitized(tmp_path: Path) -> None:
    _write(tmp_path / "auth.json")

    def refresh(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sk-ant-ort01-private-refresh", request=request)

    authenticator: Final = AnthropicAuthenticator(
        _config(tmp_path), http_client=httpx.Client(transport=httpx.MockTransport(refresh)), clock=lambda: _NOW
    )

    with pytest.raises(AnthropicAuthError, match="refresh failed") as caught:
        authenticator.get_access_token()

    assert "sk-ant-ort01-private-refresh" not in str(caught.value)
    assert caught.value.__cause__ is None


def test_failed_persistence_never_returns_unstored_rotated_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write(tmp_path / "auth.json")
    original: Final = (tmp_path / "auth.json").read_bytes()

    def refresh(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=_REFRESH_BODY)

    def reject_replace(source: Path, target: Path) -> None:
        raise OSError("sk-ant-ort01-private-refresh")

    monkeypatch.setattr(os, "replace", reject_replace)
    authenticator: Final = AnthropicAuthenticator(
        _config(tmp_path), http_client=httpx.Client(transport=httpx.MockTransport(refresh)), clock=lambda: _NOW
    )

    with pytest.raises(AnthropicError, match="storage is unavailable") as caught:
        authenticator.get_access_token()

    assert caught.value.status_code == 503
    assert (tmp_path / "auth.json").read_bytes() == original
    assert not tuple(tmp_path.glob(".anthropic-auth-*"))


def test_explicit_native_import_converts_milliseconds_and_does_not_modify_source(tmp_path: Path) -> None:
    source: Final = tmp_path / "explicit-source.json"
    source.write_text(
        '{"claudeAiOauth":{"accessToken":"sk-ant-oat01-native-access","refreshToken":"sk-ant-ort01-native-refresh",'
        '"expiresAt":5000000,"scopes":["user:inference","user:profile"]}}'
    )
    original: Final = source.read_bytes()
    profiles: Final = tmp_path / "profiles"
    authenticator: Final = _auth(profiles, "account2")

    authenticator.import_credentials(source)

    assert authenticator.get_access_token() == "sk-ant-oat01-native-access"
    stored: Final = _FixtureCredential.model_validate_json((profiles / "account2.json").read_bytes())
    assert stored.expires_at == 5000
    assert stored.refresh_token == "sk-ant-ort01-native-refresh"
    assert source.read_bytes() == original
    assert not (profiles / "auth.json").exists()


def test_explicit_legacy_import_accepts_seconds_alias(tmp_path: Path) -> None:
    source: Final = tmp_path / "source.json"
    source.write_text('{"access_token":"sk-ant-oat01-legacy-access","expires_at_s":5000,"scopes":["user:inference"]}')
    authenticator: Final = _auth(tmp_path / "profiles")

    authenticator.import_credentials(source)

    assert authenticator.get_access_token() == "sk-ant-oat01-legacy-access"


def test_token_directory_environment_is_used(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_OAUTH_TOKEN_DIR", str(tmp_path))
    _write(tmp_path / "auth.json", _FixtureCredential(expires_at=_NOW + 200))
    authenticator: Final = AnthropicAuthenticator(
        AnthropicOAuthConfig(use_anthropic_oauth=True),
        http_client=httpx.Client(transport=httpx.MockTransport(_reject_network)),
        clock=lambda: _NOW,
    )

    assert authenticator.get_access_token() == "sk-ant-oat01-old-access"


def test_authenticator_rereads_profile_after_external_rotation(tmp_path: Path) -> None:
    _write(tmp_path / "auth.json", _FixtureCredential(expires_at=_NOW + 200))
    authenticator: Final = _auth(tmp_path)
    assert authenticator.get_access_token() == "sk-ant-oat01-old-access"

    _write(
        tmp_path / "auth.json", _FixtureCredential(access_token="sk-ant-oat01-external-access", expires_at=_NOW + 200)
    )

    assert authenticator.get_access_token() == "sk-ant-oat01-external-access"


@pytest.mark.parametrize("expired", (False, True))
def test_native_profile_is_read_only_and_never_refreshes(tmp_path: Path, expired: bool) -> None:
    directory: Final = tmp_path / "work"
    directory.mkdir()
    path: Final = directory / ".credentials.json"
    expiration: Final = (_NOW - 100 if expired else _NOW + 200) * 1000
    path.write_text(
        json.dumps(
            {
                "extra": "preserved",
                "claudeAiOauth": {
                    "accessToken": "sk-ant-oat01-native-access",
                    "expiresAt": expiration,
                    "scopes": ["user:inference"],
                    "subscriptionType": "max",
                },
            }
        )
    )
    original: Final = path.read_bytes()
    authenticator: Final = AnthropicAuthenticator(
        AnthropicOAuthConfig(
            use_anthropic_oauth=True,
            anthropic_auth_profile="work",
            anthropic_token_dir=str(tmp_path),
            anthropic_credential_mode="claude_code",
        ),
        http_client=httpx.Client(transport=httpx.MockTransport(_reject_network)),
        clock=lambda: _NOW,
    )
    if expired:
        with pytest.raises(AnthropicAuthError, match=r"Claude Code.*expired"):
            authenticator.get_access_token()
    else:
        assert authenticator.get_access_token() == "sk-ant-oat01-native-access"
    assert path.read_bytes() == original
    assert tuple(directory.iterdir()) == (path,)
    with pytest.raises(AnthropicAuthError, match="read-only"):
        authenticator.import_credentials(path)


@pytest.mark.parametrize("symlink_target", ("profile", "credential"))
def test_native_profile_never_reads_external_symlink(tmp_path: Path, symlink_target: str) -> None:
    root: Final = tmp_path / "profiles"
    root.mkdir()
    outside: Final = tmp_path / "outside"
    outside.mkdir()
    secret: Final = outside / ".credentials.json"
    secret.write_text(
        json.dumps(
            {
                "claudeAiOauth": {
                    "accessToken": "sk-ant-oat01-external-token",
                    "expiresAt": 99999999999999,
                    "scopes": ["user:inference"],
                }
            }
        )
    )
    profile: Final = root / "work"
    if symlink_target == "profile":
        profile.symlink_to(outside, target_is_directory=True)
    else:
        profile.mkdir()
        (profile / ".credentials.json").symlink_to(secret)
    authenticator: Final = AnthropicAuthenticator(
        AnthropicOAuthConfig(
            use_anthropic_oauth=True,
            anthropic_auth_profile="work",
            anthropic_token_dir=str(root),
            anthropic_credential_mode="claude_code",
        ),
        clock=lambda: _NOW,
    )
    with pytest.raises(AnthropicError) as caught:
        authenticator.get_access_token()
    assert "external-token" not in str(caught.value)
    assert secret.read_text().startswith('{"claudeAiOauth":')
