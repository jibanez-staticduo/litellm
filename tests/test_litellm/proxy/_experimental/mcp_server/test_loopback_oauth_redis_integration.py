import asyncio
import os
import time
from typing import Final
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import HTTPException
from redis.asyncio import Redis

from litellm.proxy._experimental.mcp_server.loopback_oauth import (
    _RATE_PREFIX,
    LOOPBACK_RESOURCE,
    LOOPBACK_SERVER_ID,
    LoopbackOAuthCompletionRequest,
    LoopbackOAuthStartResponse,
    _active_key,
    _safe_server_key,
    _transaction_active_key,
    _transaction_key,
    complete_loopback_oauth,
    mark_loopback_oauth_ready,
    start_loopback_oauth,
)
from litellm.types.mcp import MCPAuth, MCPTransport
from litellm.types.mcp_server.mcp_server_manager import MCPServer

os.environ.setdefault("LITELLM_SALT_KEY", "test-loopback-oauth-redis-salt-32-bytes")


class FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> object:
        return {"access_token": "fake-access-token", "expires_in": 3600}


class FakeIssuer:
    def __init__(self) -> None:
        self.requests: Final[list[dict[str, str]]] = []

    async def post(self, url: str, *, headers: dict[str, str], data: dict[str, str]) -> FakeResponse:
        del url, headers
        self.requests.append(data)
        return FakeResponse()


def server(server_id: str = LOOPBACK_SERVER_ID) -> MCPServer:
    return MCPServer(
        server_id=server_id,
        name="Lovable",
        alias="lovable",
        url=LOOPBACK_RESOURCE,
        transport=MCPTransport.http,
        auth_type=MCPAuth.oauth2,
        oauth2_flow="authorization_code",
        issuer="https://lovable.dev/oauth",
        authorization_url="https://lovable.dev/oauth/authorize",
        token_url="https://lovable.dev/oauth/token",
        registration_url="https://lovable.dev/oauth/register",
        client_id="6d465f583e1e4ce5801b1616f735670c",
        scopes=["offline", "projects:read", "projects:write", "projects:create", "workspaces:read", "workspaces:write"],
        upstream_resource=LOOPBACK_RESOURCE,
    )


async def transaction_from_start(redis: Redis) -> tuple[str, LoopbackOAuthStartResponse]:
    result: Final = await start_loopback_oauth(redis=redis, server=server(), user_id="alice")
    state: Final = parse_qs(urlparse(result.authorization_url).query)["state"][0]
    return state, result


def _redis() -> Redis:
    port: Final = int(os.environ["LITELLM_LOOPBACK_TEST_REDIS_PORT"])
    return Redis(host="127.0.0.1", port=port, decode_responses=True)


@pytest.fixture
def real_redis():
    redis: Final = _redis()
    yield redis


@pytest.mark.asyncio
async def test_real_redis_transaction_ttl_atomic_consume_and_active_release(real_redis: Redis) -> None:
    await real_redis.ping()
    await real_redis.flushdb()
    state, started = await transaction_from_start(real_redis)
    await mark_loopback_oauth_ready(redis=real_redis, transaction_id=started.transaction_id)
    transaction_key: Final = _transaction_key(state)
    active_reference_key: Final = _transaction_active_key(state)
    assert 0 < await real_redis.ttl(transaction_key) <= 300
    assert 0 < await real_redis.ttl(active_reference_key) <= 300
    assert await real_redis.zcard(_active_key("alice", LOOPBACK_SERVER_ID)) == 1

    issuer: Final = FakeIssuer()
    stored: Final[list[tuple[object, ...]]] = []

    async def get_server(server_id: str):
        return server(server_id)

    async def store(*args: object) -> None:
        stored.append(args)

    async def invalidate(user_id: str, server_id: str) -> None:
        del user_id, server_id

    payload: Final = LoopbackOAuthCompletionRequest(state=state, code="fake-code")
    results: Final = await asyncio.gather(
        *(
            complete_loopback_oauth(
                redis=real_redis,
                http_client=issuer,
                payload=payload,
                get_server=get_server,
                store_credential=store,
                invalidate_cache=invalidate,
            )
            for _ in range(2)
        ),
        return_exceptions=True,
    )

    assert sum(not isinstance(result, Exception) for result in results) == 1, repr(results)
    assert any(isinstance(result, HTTPException) and result.status_code == 400 for result in results)
    assert await real_redis.exists(transaction_key, active_reference_key) == 0
    assert await real_redis.zcard(_active_key("alice", LOOPBACK_SERVER_ID)) == 0
    assert len(issuer.requests) == 1
    assert len(stored) == 1
    await real_redis.aclose()


@pytest.mark.asyncio
async def test_real_redis_rate_window_and_expiry_score_cleanup(real_redis: Redis) -> None:
    await real_redis.ping()
    await real_redis.flushdb()
    await asyncio.gather(*(transaction_from_start(real_redis) for _ in range(3)))
    rate_key: Final = f"{_RATE_PREFIX}:start:{_safe_server_key('alice', LOOPBACK_SERVER_ID)}"
    assert 0 < await real_redis.ttl(rate_key) <= 60
    with pytest.raises(HTTPException) as blocked:
        await start_loopback_oauth(redis=real_redis, server=server(), user_id="alice")
    assert blocked.value.status_code == 429

    active_key: Final = _active_key("alice", LOOPBACK_SERVER_ID)
    members: Final = await real_redis.zrange(active_key, 0, -1)
    await real_redis.zadd(active_key, {member: time.time() - 1 for member in members})

    result: Final = await start_loopback_oauth(redis=real_redis, server=server(), user_id="alice")
    assert result.expires_in == 300
    assert await real_redis.zcard(active_key) == 1
    assert parse_qs(urlparse(result.authorization_url).query)["resource"] == [LOOPBACK_RESOURCE]
    await real_redis.delete(rate_key)
    reset: Final = await start_loopback_oauth(redis=real_redis, server=server(), user_id="alice")
    assert reset.expires_in == 300
    assert await real_redis.get(rate_key) == "1"
    await real_redis.aclose()
