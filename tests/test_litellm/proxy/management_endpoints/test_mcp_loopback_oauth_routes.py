import json
import os
from typing import Final
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from litellm.proxy._experimental.mcp_server.loopback_oauth import LOOPBACK_REDIRECT_URI
from litellm.proxy._types import LitellmUserRoles, UserAPIKeyAuth
from litellm.proxy.auth.user_api_key_auth import user_api_key_auth
from litellm.proxy.common_utils.encrypt_decrypt_utils import decrypt_value_helper
from litellm.proxy.management_endpoints import mcp_management_endpoints as endpoints
from tests.test_litellm.proxy._experimental.mcp_server.test_loopback_oauth import FakeIssuer, FakeRedis, server

os.environ.setdefault("LITELLM_SALT_KEY", "test-loopback-oauth-route-salt-32-bytes")


def _app(user_id: str = "route-user") -> FastAPI:
    app: Final = FastAPI()
    app.include_router(endpoints.router)
    app.dependency_overrides[user_api_key_auth] = lambda: UserAPIKeyAuth(
        user_id=user_id,
        user_role=LitellmUserRoles.INTERNAL_USER,
        api_key="test-admission-key",
    )
    return app


def _prisma() -> MagicMock:
    prisma: Final = MagicMock()
    prisma.db.litellm_mcpusercredentials.find_unique = AsyncMock(return_value=None)
    prisma.db.litellm_mcpusercredentials.upsert = AsyncMock()
    return prisma


def _install_route_dependencies(monkeypatch: pytest.MonkeyPatch):
    redis: Final = FakeRedis()
    issuer: Final = FakeIssuer()
    prisma: Final = _prisma()
    lovable: Final = server()
    invalidation: Final = AsyncMock()
    monkeypatch.setenv("LITELLM_LOOPBACK_OAUTH_RELAY_SECRET", "route-service-secret-with-at-least-32-bytes")
    monkeypatch.setattr(endpoints, "get_prisma_client_or_throw", lambda message: prisma)
    monkeypatch.setattr(endpoints, "get_loopback_oauth_redis", lambda: redis)
    monkeypatch.setattr(endpoints, "get_loopback_oauth_http_client", lambda: issuer)
    monkeypatch.setattr(endpoints, "_authorize_and_fetch_mcp_server", AsyncMock(return_value=MagicMock()))
    monkeypatch.setattr(endpoints.global_mcp_server_manager, "get_mcp_server_by_id", lambda server_id: lovable)
    monkeypatch.setattr(endpoints.global_mcp_server_manager, "get_registry", lambda: {lovable.server_id: lovable})
    monkeypatch.setattr(endpoints.global_mcp_server_manager, "invalidate_user_oauth_token_cache", invalidation)
    return redis, issuer, prisma, invalidation


def test_http_start_and_completion_auth_persist_encrypted_user_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, issuer, prisma, invalidation = _install_route_dependencies(monkeypatch)
    client: Final = TestClient(_app())

    server_id: Final = "74d40886-9a8d-44da-941a-4c490bb7c8da"
    start: Final = client.post(f"/v1/mcp/server/{server_id}/loopback-oauth/start")
    assert start.status_code == 200
    authorization_url: Final = start.json()["authorization_url"]
    query: Final = parse_qs(urlparse(authorization_url).query)
    assert query["redirect_uri"] == [LOOPBACK_REDIRECT_URI]
    assert query["code_challenge_method"] == ["S256"]
    ready: Final = client.post(
        "/v1/mcp/loopback-oauth/ready",
        headers={"Authorization": "Bearer route-service-secret-with-at-least-32-bytes"},
        json={"transaction_id": start.json()["transaction_id"]},
    )
    assert ready.json() == {"status": "ready"}

    completion: Final = client.post(
        "/v1/mcp/loopback-oauth/complete",
        headers={"Authorization": "Bearer route-service-secret-with-at-least-32-bytes"},
        json={"state": query["state"][0], "code": "route-fake-code"},
    )
    assert completion.status_code == 200
    assert completion.json() == {"outcome": "connected"}
    assert len(issuer.requests) == 1
    upsert: Final = prisma.db.litellm_mcpusercredentials.upsert.call_args.kwargs["data"]
    encrypted: Final = upsert["create"]["credential_b64"]
    assert "fake-access-token" not in encrypted
    decrypted: Final = decrypt_value_helper(value=encrypted, key="credential_b64")
    assert json.loads(decrypted)["access_token"] == "fake-access-token"
    invalidation.assert_awaited_once_with("route-user", server_id)


def test_http_completion_relay_auth_precedes_redis_prisma_and_exchange(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LITELLM_LOOPBACK_OAUTH_RELAY_SECRET", "route-service-secret-with-at-least-32-bytes")
    monkeypatch.setattr(
        endpoints,
        "get_prisma_client_or_throw",
        lambda message: pytest.fail(f"prisma reached before relay auth: {message}"),
    )
    monkeypatch.setattr(endpoints, "get_loopback_oauth_redis", lambda: pytest.fail("redis reached before relay auth"))
    response: Final = TestClient(_app()).post(
        "/v1/mcp/loopback-oauth/complete",
        headers={"Authorization": "Bearer wrong-service-secret-with-at-least-32-bytes"},
        json={"state": "x" * 43, "code": "fake-code"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": {"error": "Unauthorized"}}


def test_http_completion_rejects_identity_fields_and_duplicate_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    _, issuer, prisma, _ = _install_route_dependencies(monkeypatch)
    lovable: Final = server()
    duplicate: Final = server().model_copy(update={"alias": "duplicate-lovable"})
    monkeypatch.setattr(
        endpoints.global_mcp_server_manager,
        "get_registry",
        lambda: {lovable.server_id: lovable, duplicate.server_id: duplicate},
    )
    client: Final = TestClient(_app())
    start: Final = client.post("/v1/mcp/server/74d40886-9a8d-44da-941a-4c490bb7c8da/loopback-oauth/start")
    assert start.status_code == 400

    malformed: Final = client.post(
        "/v1/mcp/loopback-oauth/complete",
        headers={"Authorization": "Bearer route-service-secret-with-at-least-32-bytes"},
        json={"state": "x" * 43, "code": "fake-code", "user_id": "mallory", "server_id": "other"},
    )
    assert malformed.status_code == 422
    assert issuer.requests == []
    prisma.db.litellm_mcpusercredentials.upsert.assert_not_awaited()


def test_health_is_principal_relative_for_user_oauth(monkeypatch: pytest.MonkeyPatch) -> None:
    lovable: Final = server()
    monkeypatch.setattr(endpoints, "_get_user_mcp_management_mode", lambda: "view_all")
    monkeypatch.setattr(
        endpoints.global_mcp_server_manager,
        "get_all_mcp_servers_with_health_unfiltered",
        AsyncMock(return_value=[MagicMock(server_id=lovable.server_id, status="unknown")]),
    )
    monkeypatch.setattr(endpoints.global_mcp_server_manager, "get_mcp_server_by_id", lambda server_id: lovable)
    has_token: Final = AsyncMock(side_effect=[True, False])
    monkeypatch.setattr(endpoints.global_mcp_server_manager, "has_user_oauth_token", has_token)
    monkeypatch.setattr(
        endpoints.global_mcp_server_manager,
        "_get_tools_from_server",
        AsyncMock(return_value=[]),
    )
    client: Final = TestClient(_app())

    connected: Final = client.get(f"/v1/mcp/server/health?server_ids={lovable.server_id}")
    auth_required: Final = client.get(f"/v1/mcp/server/health?server_ids={lovable.server_id}")

    assert connected.json() == [{"server_id": lovable.server_id, "status": "healthy"}]
    assert auth_required.json() == [{"server_id": lovable.server_id, "status": "auth_required"}]


def test_http_status_denies_other_user_and_server(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_route_dependencies(monkeypatch)
    server_id: Final = "74d40886-9a8d-44da-941a-4c490bb7c8da"
    owner: Final = TestClient(_app("owner"))
    started: Final = owner.post(f"/v1/mcp/server/{server_id}/loopback-oauth/start").json()

    other_user: Final = TestClient(_app("other")).get(
        f"/v1/mcp/server/{server_id}/loopback-oauth/status/{started['transaction_id']}"
    )
    other_server: Final = owner.get(f"/v1/mcp/server/other-server/loopback-oauth/status/{started['transaction_id']}")

    assert other_user.status_code == 404
    assert other_server.status_code == 404
