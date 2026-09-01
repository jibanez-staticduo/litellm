import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from litellm.proxy._experimental.mcp_server.lazymcp_public_resource import (
    LazyMcpPublicResource,
    LazyMcpResourceError,
    build_lazymcp_challenge,
    build_lazymcp_metadata,
    is_lazymcp_resource_candidate,
    parse_lazymcp_resource,
    resource_from_transport_scope,
)


def _request(
    path: str = "/lazymcp",
    original_path: str | None = None,
    client: tuple[str, int] = ("127.0.0.1", 1234),
) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "scheme": "https",
        "path": path,
        "query_string": b"",
        "headers": [(b"host", b"gateway.example")],
        "client": client,
    }
    if original_path is not None:
        scope["_original_path"] = original_path
    return Request(scope)


def test_all_public_resource_shapes_build_exact_metadata_and_challenges(monkeypatch):
    monkeypatch.setenv("PROXY_BASE_URL", "https://gateway.example")
    for path, kind, identifier in (
        ("/lazymcp", "aggregate", None),
        ("/lazymcp/group-one", "scope", "group-one"),
        ("/toolset/tools_1/lazymcp", "toolset", "tools_1"),
    ):
        resource = parse_lazymcp_resource(_request(path), f"https://gateway.example{path}/")
        assert isinstance(resource, LazyMcpPublicResource)
        assert (resource.kind, resource.identifier) == (kind, identifier)
        assert resource.canonical_uri == f"https://gateway.example{path}"
        assert build_lazymcp_metadata(resource, "https://gateway.example/mcp") == {
            "resource": f"https://gateway.example{path}",
            "authorization_servers": ["https://gateway.example/mcp"],
        }
        assert build_lazymcp_challenge(resource, False) == (
            f'Bearer resource_metadata="https://gateway.example/.well-known/oauth-protected-resource{path}"'
        )
        assert 'error="invalid_token"' in build_lazymcp_challenge(resource, True)


def test_original_public_path_survives_internal_rewrite(monkeypatch):
    monkeypatch.setenv("PROXY_BASE_URL", "https://gateway.example")
    resource = resource_from_transport_scope(_request("/lazymcp", "/toolset/alpha/lazymcp").scope)
    assert isinstance(resource, LazyMcpPublicResource)
    assert resource.canonical_uri == "https://gateway.example/toolset/alpha/lazymcp"


def test_resource_parser_rejects_ambiguous_or_foreign_values(monkeypatch):
    monkeypatch.setenv("PROXY_BASE_URL", "https://gateway.example")
    request = _request()
    for candidate in (
        "https://evil.example/lazymcp",
        "https://gateway.example/mcp",
        "https://gateway.example/lazymcp/a/b",
        "https://gateway.example/lazymcp/%2f",
        "https://gateway.example/lazymcp/..",
        "https://gateway.example/lazymcp/name?query=1",
        "https://gateway.example/LazyMCP",
    ):
        assert isinstance(parse_lazymcp_resource(request, candidate), LazyMcpResourceError)


def test_candidate_classifier_detects_malformed_case_and_encoding():
    for candidate in (
        "https://gateway.example/LazyMCP",
        "https://gateway.example/toolset/name/LAZYMCP",
        "https://gateway.example/%6cazymcp",
    ):
        assert is_lazymcp_resource_candidate(_request(), candidate)


def test_candidate_classifier_preserves_legacy_mcp_resources_containing_lazymcp():
    for candidate in (
        "https://lazymcp.example/mcp",
        "https://gateway.example/mcp/lazymcp-server",
        "https://gateway.example/mcp/team/lazymcp",
        "https://gateway.example/mcp/server?label=lazymcp",
    ):
        assert not is_lazymcp_resource_candidate(_request(), candidate)


def test_slash_containing_legacy_mcp_resource_is_not_a_lazymcp_resource(monkeypatch):
    monkeypatch.setenv("PROXY_BASE_URL", "https://gateway.example")
    candidate = "https://gateway.example/mcp/team/lazymcp"
    assert not is_lazymcp_resource_candidate(_request(), candidate)
    assert isinstance(parse_lazymcp_resource(_request(), candidate), LazyMcpResourceError)


def test_classifier_is_relative_to_configured_trusted_root(monkeypatch):
    monkeypatch.setenv("PROXY_BASE_URL", "https://gateway.example/mcp")
    request = _request(path="/mcp/LazyMCP")
    candidate = "https://gateway.example/mcp/LazyMCP"
    assert is_lazymcp_resource_candidate(request, candidate)
    assert isinstance(parse_lazymcp_resource(request, candidate), LazyMcpResourceError)


def test_invalid_nonempty_proxy_base_never_falls_back_to_request_host(monkeypatch):
    monkeypatch.setenv("PROXY_BASE_URL", "not-a-valid-url")
    request = _request(client=("203.0.113.5", 1234))
    assert isinstance(parse_lazymcp_resource(request, "https://gateway.example/lazymcp"), LazyMcpResourceError)


def test_trusted_base_requires_https_or_loopback_http(monkeypatch):
    monkeypatch.setenv("PROXY_BASE_URL", "http://gateway.example")
    assert isinstance(parse_lazymcp_resource(_request(), "http://gateway.example/lazymcp"), LazyMcpResourceError)

    monkeypatch.setenv("PROXY_BASE_URL", "http://127.0.0.1:4000")
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "path": "/lazymcp",
            "query_string": b"",
            "headers": [(b"host", b"127.0.0.1:4000")],
            "client": ("127.0.0.1", 1234),
        }
    )
    assert isinstance(parse_lazymcp_resource(request, "http://127.0.0.1:4000/lazymcp"), LazyMcpPublicResource)


@pytest.mark.parametrize("scheme", ("http", "https"))
def test_remote_peer_cannot_claim_loopback_authority(monkeypatch, scheme):
    monkeypatch.delenv("PROXY_BASE_URL", raising=False)
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": scheme,
            "path": "/lazymcp",
            "query_string": b"",
            "headers": [(b"host", b"localhost")],
            "client": ("203.0.113.5", 1234),
        }
    )
    assert isinstance(parse_lazymcp_resource(request, f"{scheme}://localhost/lazymcp"), LazyMcpResourceError)


def test_untrusted_host_and_forwarded_headers_cannot_select_authority(monkeypatch):
    from litellm.proxy.auth.ip_address_utils import IPAddressUtils

    monkeypatch.delenv("PROXY_BASE_URL", raising=False)
    monkeypatch.setattr(IPAddressUtils, "is_request_from_trusted_proxy", lambda request: False)
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "https",
            "path": "/lazymcp",
            "query_string": b"",
            "headers": [
                (b"host", b"attacker.example"),
                (b"x-forwarded-host", b"public.example"),
                (b"x-forwarded-proto", b"https"),
            ],
            "client": ("203.0.113.5", 1234),
        }
    )
    assert isinstance(parse_lazymcp_resource(request, "https://attacker.example/lazymcp"), LazyMcpResourceError)


def test_trusted_proxy_external_base_and_root_path(monkeypatch):
    from litellm.proxy.auth.ip_address_utils import IPAddressUtils

    monkeypatch.delenv("PROXY_BASE_URL", raising=False)
    monkeypatch.setenv("SERVER_ROOT_PATH", "/proxy")
    monkeypatch.setattr(IPAddressUtils, "is_request_from_trusted_proxy", lambda request: True)
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "root_path": "/proxy",
            "path": "/proxy/lazymcp/team-a",
            "query_string": b"",
            "headers": [
                (b"host", b"internal:4000"),
                (b"x-forwarded-host", b"gateway.example"),
                (b"x-forwarded-proto", b"https"),
            ],
            "client": ("10.0.0.1", 1234),
        }
    )
    resource = parse_lazymcp_resource(request, "https://gateway.example/proxy/lazymcp/team-a")
    assert isinstance(resource, LazyMcpPublicResource)
    assert resource.metadata_path == "/.well-known/oauth-protected-resource/proxy/lazymcp/team-a"


def test_all_discovery_aliases_return_equivalent_generic_metadata(monkeypatch):
    from litellm.proxy._experimental.mcp_server.discoverable_endpoints import router

    monkeypatch.setenv("PROXY_BASE_URL", "https://gateway.example")
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app, base_url="https://gateway.example")
    for inserted, appended, resource in (
        (
            "/.well-known/oauth-protected-resource/lazymcp",
            "/lazymcp/.well-known/oauth-protected-resource",
            "https://gateway.example/lazymcp",
        ),
        (
            "/.well-known/oauth-protected-resource/lazymcp/unknown-scope",
            "/lazymcp/unknown-scope/.well-known/oauth-protected-resource",
            "https://gateway.example/lazymcp/unknown-scope",
        ),
        (
            "/.well-known/oauth-protected-resource/toolset/unknown-tools/lazymcp",
            "/toolset/unknown-tools/lazymcp/.well-known/oauth-protected-resource",
            "https://gateway.example/toolset/unknown-tools/lazymcp",
        ),
    ):
        inserted_response = client.get(inserted)
        appended_response = client.get(appended)
        assert inserted_response.status_code == appended_response.status_code == 200
        assert inserted_response.headers["content-type"].startswith("application/json")
        assert inserted_response.json() == appended_response.json() == {
            "resource": resource,
            "authorization_servers": ["https://gateway.example/mcp"],
        }


def test_discovery_fails_closed_for_untrusted_docker_peer_without_public_base(monkeypatch):
    from litellm.proxy._experimental.mcp_server.discoverable_endpoints import router

    monkeypatch.delenv("PROXY_BASE_URL", raising=False)
    app = FastAPI()
    app.include_router(router)
    client = TestClient(
        app,
        base_url="http://gateway.internal",
        client=("172.18.0.2", 49152),
    )
    for path in (
        "/.well-known/oauth-protected-resource/lazymcp",
        "/lazymcp/.well-known/oauth-protected-resource",
        "/.well-known/oauth-protected-resource/lazymcp/team-a",
        "/lazymcp/team-a/.well-known/oauth-protected-resource",
        "/.well-known/oauth-protected-resource/toolset/tools-a/lazymcp",
        "/toolset/tools-a/lazymcp/.well-known/oauth-protected-resource",
    ):
        response = client.get(path)
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}


def test_discovery_succeeds_for_docker_peer_with_reserved_https_public_base(monkeypatch):
    from litellm.proxy._experimental.mcp_server.discoverable_endpoints import router

    monkeypatch.setenv("PROXY_BASE_URL", "https://candidate.invalid")
    app = FastAPI()
    app.include_router(router)
    client = TestClient(
        app,
        base_url="http://gateway.internal",
        client=("172.18.0.2", 49152),
    )
    for path, resource in (
        ("/.well-known/oauth-protected-resource/lazymcp", "https://candidate.invalid/lazymcp"),
        ("/lazymcp/.well-known/oauth-protected-resource", "https://candidate.invalid/lazymcp"),
        (
            "/.well-known/oauth-protected-resource/lazymcp/team-a",
            "https://candidate.invalid/lazymcp/team-a",
        ),
        (
            "/lazymcp/team-a/.well-known/oauth-protected-resource",
            "https://candidate.invalid/lazymcp/team-a",
        ),
        (
            "/.well-known/oauth-protected-resource/toolset/tools-a/lazymcp",
            "https://candidate.invalid/toolset/tools-a/lazymcp",
        ),
        (
            "/toolset/tools-a/lazymcp/.well-known/oauth-protected-resource",
            "https://candidate.invalid/toolset/tools-a/lazymcp",
        ),
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json() == {
            "resource": resource,
            "authorization_servers": ["https://candidate.invalid/mcp"],
        }
