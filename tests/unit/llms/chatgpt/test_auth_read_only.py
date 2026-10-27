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


def test_read_only_client_token_account_id_does_not_require_saved_snapshot(tmp_path):
    token = jwt({"https://api.openai.com/auth": {"chatgpt_account_id": "client-account"}})
    directory = tmp_path / "missing-profile"
    auth = chatgpt_auth(directory)

    assert auth.get_account_id(token) == "client-account"
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
    def __init__(self):
        self.client_calls = 0
        self.interactive_checks = 0

    def visit_ClassDef(self, node):
        if node.name == "ChatGPTOAuthEngine":
            node.name = "Authenticator"
            node.body = [
                method
                for method in node.body
                if not (
                    isinstance(method, ast.FunctionDef)
                    and method.name in {"_get_auth_http_client", "_can_start_interactive_auth"}
                )
            ]
        return self.generic_visit(node)

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


def test_upstream_oauth_algorithm_fingerprint_and_drift_guard():
    from litellm.llms.chatgpt import oauth_engine

    source = Path(oauth_engine.__file__).read_text()
    restorer = RestoreUpstreamOAuthAST()
    restored = restorer.visit(ast.parse(source))
    assert restorer.client_calls == 4
    assert restorer.interactive_checks == 1
    engine_class = next(node for node in restored.body if isinstance(node, ast.ClassDef) and node.name == "Authenticator")
    methods = {
        "_ensure_token_dir",
        "_get_device_code_cooldown_remaining",
        "_is_token_expired",
        "_login_device_code",
        "_read_auth_file",
        "_record_device_code_request",
        "_wait_for_access_token",
        "_request_device_code",
        "_poll_for_authorization_code",
        "_exchange_code_for_tokens",
        "get_access_token",
    }
    algorithm = ast.Module(
        body=sorted(
            (node for node in engine_class.body if isinstance(node, ast.FunctionDef) and node.name in methods),
            key=lambda node: node.name,
        ),
        type_ignores=[],
    )
    digest = hashlib.sha256(ast.dump(algorithm, include_attributes=False).encode()).hexdigest()
    assert digest == CHATGPT_OAUTH_UPSTREAM_AST_SHA256
    mutated = ast.parse(source.replace('"refresh_token"', '"changed_refresh_token"', 1))
    mutated_tree = RestoreUpstreamOAuthAST().visit(mutated)
    mutated_class = next(
        node for node in mutated_tree.body if isinstance(node, ast.ClassDef) and node.name == "Authenticator"
    )
    mutated_algorithm = ast.Module(
        body=sorted(
            (node for node in mutated_class.body if isinstance(node, ast.FunctionDef) and node.name in methods),
            key=lambda node: node.name,
        ),
        type_ignores=[],
    )
    assert hashlib.sha256(ast.dump(mutated_algorithm, include_attributes=False).encode()).hexdigest() != digest
    with pytest.raises(ProviderUpstreamDriftError):
        check_provider_upstream_source((source + "# changed\n").encode())
