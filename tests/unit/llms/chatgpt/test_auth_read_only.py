"""Isolated auth snapshots must never create a writer or contact OAuth."""

import base64
import json
import re
import time
from pathlib import Path

import httpx
import pytest
from staticduo_litellm.compatibility.provider_upstream import (
    ProviderUpstreamDriftError,
    check_provider_upstream_source,
)

from litellm.llms.anthropic.authenticator import AnthropicAuthenticator, AnthropicAuthError, AnthropicOAuthConfig
from litellm.llms.chatgpt.authenticator import Authenticator
from litellm.llms.chatgpt.common_utils import GetAccessTokenError


def no_http_client():
    pytest.fail("Read-only auth must reject before acquiring an HTTP client")


def jwt(claims):
    return "header." + base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=") + ".signature"


@pytest.fixture(autouse=True)
def read_only(monkeypatch):
    monkeypatch.setenv("STATICDUO_AUTH_READ_ONLY", "true")


def chatgpt_auth(path):
    return Authenticator({"chatgpt_token_dir": str(path)}, http_client_factory=no_http_client)


@pytest.mark.parametrize("derived", [False, True])
def test_chatgpt_valid_snapshot_has_no_auth_writes_or_locks(tmp_path, derived):
    claims = {"exp": int(time.time()) + 3600, "https://api.openai.com/auth": {"chatgpt_account_id": "server-owner"}}
    record = (
        {"access_token": jwt(claims)}
        if derived
        else {"access_token": "test-access", "expires_at": time.time() + 3600, "account_id": "server-owner"}
    )
    path = tmp_path / "auth.json"
    path.write_text(json.dumps(record))
    path.chmod(0o444)
    before = (path.read_bytes(), path.stat().st_mtime_ns, path.stat().st_mode)
    auth = chatgpt_auth(tmp_path)
    assert auth.get_access_token() == record["access_token"]
    assert auth.get_account_id() == "server-owner"
    assert list(tmp_path.iterdir()) == [path]
    assert (path.read_bytes(), path.stat().st_mtime_ns, path.stat().st_mode) == before


@pytest.mark.parametrize("expiry", [1, None, float("nan"), float("inf"), True, "99999999999"])
def test_chatgpt_expired_or_invalid_snapshot_rejects_before_http_or_lock(tmp_path, expiry):
    path = tmp_path / "auth.json"
    path.write_text(json.dumps({"access_token": "test-access", "refresh_token": "test-refresh", "expires_at": expiry}))
    before = path.read_bytes()
    auth = chatgpt_auth(tmp_path)
    for read in (auth.get_access_token, auth.get_account_id):
        with pytest.raises(GetAccessTokenError, match="missing, invalid or expired"):
            read()
    assert list(tmp_path.iterdir()) == [path]
    assert path.read_bytes() == before


def test_chatgpt_missing_snapshot_does_not_create_directory_or_login(tmp_path):
    directory = tmp_path / "missing-profile"
    auth = chatgpt_auth(directory)
    with pytest.raises(GetAccessTokenError):
        auth.get_access_token()
    assert not directory.exists()
    with pytest.raises(GetAccessTokenError, match="read-only"):
        auth._login_device_code()
    with pytest.raises(GetAccessTokenError, match="read-only"):
        auth._write_auth_file({"access_token": "new"})
    assert not directory.exists()


def test_client_parameter_cannot_disable_read_only(tmp_path):
    auth = Authenticator(
        {"chatgpt_token_dir": str(tmp_path), "STATICDUO_AUTH_READ_ONLY": False}, http_client_factory=no_http_client
    )
    with pytest.raises(GetAccessTokenError):
        auth.get_access_token()
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("expiry", [time.time() + 3600, 1])
def test_anthropic_managed_snapshot_without_writer(tmp_path, expiry):
    path = tmp_path / "auth.json"
    path.write_text(
        json.dumps(
            {
                "access_token": "sk-ant-oat01-snapshot",
                "refresh_token": "test-refresh",
                "expires_at": expiry,
                "scope": "user:inference",
            }
        )
    )
    before = path.read_bytes()
    client = httpx.Client(transport=httpx.MockTransport(lambda request: pytest.fail("Read-only OAuth network")))
    config = AnthropicOAuthConfig(use_anthropic_oauth=True, anthropic_token_dir=str(tmp_path))
    auth = AnthropicAuthenticator(config, http_client=client)
    if expiry == 1:
        with pytest.raises(AnthropicAuthError, match="expired"):
            auth.get_access_token()
    else:
        assert auth.get_access_token() == "sk-ant-oat01-snapshot"
    with pytest.raises(AnthropicAuthError, match="read-only"):
        auth.import_credentials(path)
    client.close()
    assert list(tmp_path.iterdir()) == [path]
    assert path.read_bytes() == before


def test_anthropic_missing_snapshot_does_not_create_directory(tmp_path):
    directory = tmp_path / "missing-profile"
    auth = AnthropicAuthenticator(AnthropicOAuthConfig(use_anthropic_oauth=True, anthropic_token_dir=str(directory)))
    with pytest.raises(AnthropicAuthError, match="missing"):
        auth.get_access_token()
    assert not directory.exists()


def test_upstream_oauth_engine_matches_pinned_source_and_rejects_drift():
    from litellm.llms.chatgpt import oauth_engine

    source = Path(oauth_engine.__file__).read_text()
    source = re.sub(r"  # (?:mutable-ok|noqa: BLE001|pyright: ignore).*", "", source)
    source = source.replace("# noqa: T201  # device login must display user instructions", "# noqa: T201")
    upstream = source.replace("class ChatGPTOAuthEngine:", "class Authenticator:")
    upstream = upstream.replace(
        "    def _get_auth_http_client(self) -> HTTPHandler | httpx.Client:\n        return get_httpx_client()\n\n", ""
    )
    upstream = upstream.replace("client: Final = self._get_auth_http_client()", "client: Final = get_httpx_client()")
    upstream = upstream.replace(
        "    def _can_start_interactive_auth(self) -> bool:\n        return can_block_current_thread()\n\n", ""
    )
    upstream = upstream.replace("if not self._can_start_interactive_auth():", "if not can_block_current_thread():")
    upstream = upstream.replace(
        "http_handler import HTTPHandler, get_httpx_client", "http_handler import get_httpx_client"
    )
    upstream = upstream.replace(
        "http_handler import (\n    HTTPHandler,\n    get_httpx_client,\n)",
        "http_handler import get_httpx_client",
    )
    upstream = upstream.replace(
        "    @staticmethod\n    def get_api_base(default_base: str = CHATGPT_API_BASE) -> str:",
        "    def get_api_base(self) -> str:",
    ).replace("or default_base\n", "or CHATGPT_API_BASE\n")
    check_provider_upstream_source(upstream.encode())
    with pytest.raises(ProviderUpstreamDriftError):
        check_provider_upstream_source((upstream + "# upstream changed\n").encode())
