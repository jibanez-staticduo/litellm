"""Isolated auth snapshots must never create a writer or contact OAuth."""

import ast
import base64
import hashlib
import json
import time
from pathlib import Path

import httpx
import pytest
from staticduo_litellm.compatibility.provider_upstream import (
    CHATGPT_OAUTH_UPSTREAM_AST_SHA256,
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


class RestoreUpstreamOAuthAST(ast.NodeTransformer):
    """Undo only the documented dependency hooks; retain every algorithm node."""

    def __init__(self):
        self.client_calls = 0
        self.interactive_checks = 0

    def visit_ClassDef(self, node):
        if node.name == "ChatGPTOAuthEngine":
            node.name = "Authenticator"
            helpers = {"_get_auth_http_client", "_can_start_interactive_auth"}
            expected = ast.parse("""
class Hooks:
    def _get_auth_http_client(self) -> HTTPHandler | httpx.Client:
        return get_httpx_client()
    def _can_start_interactive_auth(self) -> bool:
        return can_block_current_thread()
""").body[0]
            actual = [method for method in node.body if isinstance(method, ast.FunctionDef) and method.name in helpers]
            assert [ast.dump(method) for method in actual] == [ast.dump(method) for method in expected.body]
            node.body = [method for method in node.body if method not in actual]
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.name == "get_api_base":
            assert len(node.args.args) == 1 and node.args.args[0].arg == "default_base"
            assert [ast.dump(item) for item in node.decorator_list] == [
                ast.dump(ast.Name(id="staticmethod", ctx=ast.Load()))
            ]
            node.decorator_list = []
            node.args.args[0].arg = "self"
            node.args.args[0].annotation = None
            node.args.defaults = []
        return self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module == "litellm.llms.custom_httpx.http_handler":
            node.names = [name for name in node.names if name.name != "HTTPHandler"]
        return node

    def visit_Call(self, node):
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "self"
        ):
            if node.func.attr == "_get_auth_http_client":
                self.client_calls += 1
                node.func = ast.Name(id="get_httpx_client", ctx=ast.Load())
            elif node.func.attr == "_can_start_interactive_auth":
                self.interactive_checks += 1
                node.func = ast.Name(id="can_block_current_thread", ctx=ast.Load())
        return self.generic_visit(node)

    def visit_Name(self, node):
        if node.id == "default_base":
            node.id = "CHATGPT_API_BASE"
        return node


def test_upstream_oauth_engine_matches_pinned_source_and_rejects_drift():
    from litellm.llms.chatgpt import oauth_engine

    source = Path(oauth_engine.__file__).read_text()
    restorer = RestoreUpstreamOAuthAST()
    restored = restorer.visit(ast.parse(source))
    assert restorer.client_calls == 4
    assert restorer.interactive_checks == 1
    restored_digest = hashlib.sha256(ast.dump(restored, include_attributes=False).encode()).hexdigest()
    assert restored_digest == CHATGPT_OAUTH_UPSTREAM_AST_SHA256
    # Formatting does not change the upstream algorithm fingerprint.
    formatted_restorer = RestoreUpstreamOAuthAST()
    reformatted = formatted_restorer.visit(ast.parse(ast.unparse(ast.parse(source))))
    assert ast.dump(reformatted) == ast.dump(restored)
    mutated_restorer = RestoreUpstreamOAuthAST()
    changed = mutated_restorer.visit(ast.parse(source.replace('"refresh_token"', '"changed_refresh_token"')))
    assert hashlib.sha256(ast.dump(changed).encode()).hexdigest() != CHATGPT_OAUTH_UPSTREAM_AST_SHA256
    with pytest.raises(ProviderUpstreamDriftError):
        check_provider_upstream_source((source + "# upstream changed\n").encode())
