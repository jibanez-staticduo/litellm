import asyncio
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Final
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from litellm.proxy._experimental.mcp_server.loopback_oauth import (
    _CONSUME_SCRIPT,
    _RATE_SCRIPT,
    _START_SCRIPT,
    _STATUS_GET_SCRIPT,
    _STATUS_TRANSITION_SCRIPT,
    LOOPBACK_AUTHORIZATION_URL,
    LOOPBACK_PUBLIC_CLIENT_ID,
    LOOPBACK_REDIRECT_URI,
    LOOPBACK_RESOURCE,
    LOOPBACK_SCOPES,
    LOOPBACK_TOKEN_URL,
    LoopbackOAuthCompletionRequest,
    LoopbackOAuthTransaction,
    _decode_transaction,
    _transaction_key,
    authenticate_loopback_oauth_relay,
    complete_loopback_oauth,
    mark_loopback_oauth_ready,
    start_loopback_oauth,
)
from litellm.types.mcp import MCPAuth, MCPTransport
from litellm.types.mcp_server.mcp_server_manager import MCPServer

os.environ.setdefault("LITELLM_SALT_KEY", "test-loopback-oauth-salt-key-32-bytes")


class FakeRedis:
    def __init__(self) -> None:
        self.values: Final[dict[str, str]] = {}
        self.active: Final[dict[str, set[str]]] = {}
        self.rates: Final[dict[str, int]] = {}
        self.lock: Final = asyncio.Lock()

    async def eval(self, script: str, numkeys: int, *args: object) -> object:
        del numkeys
        async with self.lock:
            if script == _RATE_SCRIPT:
                key: Final = str(args[0])
                self.rates[key] = self.rates.get(key, 0) + 1
                return self.rates[key]
            if script == _START_SCRIPT:
                transaction_key, transaction_active_key, active_key, status_key, status_phase_key = (
                    str(args[0]),
                    str(args[1]),
                    str(args[2]),
                    str(args[3]),
                    str(args[4]),
                )
                encrypted, limit, state_hash = str(args[6]), int(args[8]), str(args[9])
                active: Final = self.active.setdefault(active_key, set())
                if len(active) >= limit:
                    return 0
                self.values[transaction_key] = encrypted
                self.values[transaction_active_key] = active_key
                self.values[status_key] = str(args[10])
                self.values[status_phase_key] = "pending"
                active.add(state_hash)
                return 1
            if script == _CONSUME_SCRIPT:
                transaction_key, transaction_active_key, state_hash = str(args[0]), str(args[1]), str(args[2])
                value: Final = self.values.pop(transaction_key, False)
                active_key: Final = self.values.pop(transaction_active_key, None)
                if active_key is not None:
                    self.active[active_key].discard(state_hash)
                return value
            if script == _STATUS_GET_SCRIPT:
                return self.values.get(str(args[0]), False)
            if script == _STATUS_TRANSITION_SCRIPT:
                key, phase_key = str(args[0]), str(args[1])
                if self.values.get(phase_key) != str(args[2]):
                    return 0
                self.values[key] = str(args[3])
                self.values[phase_key] = str(args[4])
                return 1
            raise AssertionError("unexpected script")


class PausedReadinessRedis(FakeRedis):
    def __init__(self) -> None:
        super().__init__()
        self.readiness_entered: Final = asyncio.Event()
        self.release_readiness: Final = asyncio.Event()

    async def eval(self, script: str, numkeys: int, *args: object) -> object:
        if script == _STATUS_TRANSITION_SCRIPT and not self.readiness_entered.is_set():
            self.readiness_entered.set()
            await self.release_readiness.wait()
        return await super().eval(script, numkeys, *args)


class FakeResponse:
    def __init__(self, body: object, failure: bool = False) -> None:
        self.body: Final = body
        self.failure: Final = failure

    def raise_for_status(self) -> None:
        if self.failure:
            raise RuntimeError("synthetic issuer failure")

    def json(self) -> object:
        return self.body


class FakeIssuer:
    def __init__(self, response: FakeResponse | None = None) -> None:
        self.response: Final = response or FakeResponse(
            {
                "access_token": "fake-access-token",
                "refresh_token": "fake-refresh-token",
                "expires_in": 3600,
                "scope": " ".join(LOOPBACK_SCOPES),
                "token_type": "Bearer",
            }
        )
        self.requests: Final[list[tuple[str, dict[str, str], dict[str, str]]]] = []

    async def post(self, url: str, *, headers: dict[str, str], data: dict[str, str]) -> FakeResponse:
        self.requests.append((url, headers, data))
        return self.response


class TransportFailureIssuer:
    async def post(self, url: str, *, headers: dict[str, str], data: dict[str, str]) -> FakeResponse:
        del url, headers, data
        raise OSError("synthetic DNS failure containing fake-code")


def server(server_id: str = "74d40886-9a8d-44da-941a-4c490bb7c8da") -> MCPServer:
    return MCPServer(
        server_id=server_id,
        name="Lovable",
        alias="lovable",
        url=LOOPBACK_RESOURCE,
        transport=MCPTransport.http,
        auth_type=MCPAuth.oauth2,
        oauth2_flow="authorization_code",
        issuer="https://lovable.dev/oauth",
        authorization_url=LOOPBACK_AUTHORIZATION_URL,
        token_url=LOOPBACK_TOKEN_URL,
        registration_url="https://lovable.dev/oauth/register",
        client_id=LOOPBACK_PUBLIC_CLIENT_ID,
        scopes=list(LOOPBACK_SCOPES),
        upstream_resource=LOOPBACK_RESOURCE,
    )


async def transaction_from_start(redis: FakeRedis, user_id: str = "alice") -> tuple[str, LoopbackOAuthTransaction]:
    result: Final = await start_loopback_oauth(redis=redis, server=server(), user_id=user_id)
    state: Final = parse_qs(urlparse(result.authorization_url).query)["state"][0]
    encrypted: Final = redis.values[_transaction_key(state)]
    await mark_loopback_oauth_ready(redis=redis, transaction_id=result.transaction_id)
    return state, _decode_transaction(encrypted)


async def complete(
    redis: FakeRedis,
    state: str,
    issuer: FakeIssuer,
    stored: list[tuple[object, ...]],
    invalidated: list[tuple[str, str]],
    get_server: Callable[[str], Awaitable[MCPServer | None]] | None = None,
):
    async def default_get_server(server_id: str) -> MCPServer | None:
        return server(server_id)

    async def store_credential(*args: object) -> None:
        stored.append(args)

    async def invalidate(user_id: str, server_id: str) -> None:
        invalidated.append((user_id, server_id))

    return await complete_loopback_oauth(
        redis=redis,
        http_client=issuer,
        payload=LoopbackOAuthCompletionRequest(state=state, code="fake-code"),
        get_server=get_server or default_get_server,
        store_credential=store_credential,
        invalidate_cache=invalidate,
    )


@pytest.mark.asyncio
async def test_success_uses_exact_redirect_pkce_and_user_binding(caplog: pytest.LogCaptureFixture) -> None:
    redis: Final = FakeRedis()
    state, transaction = await transaction_from_start(redis)
    issuer: Final = FakeIssuer()
    stored: Final[list[tuple[object, ...]]] = []
    invalidated: Final[list[tuple[str, str]]] = []
    caplog.set_level(logging.INFO)

    result: Final = await complete(redis, state, issuer, stored, invalidated)

    assert result.outcome == "connected"
    assert issuer.requests[0][0] == LOOPBACK_TOKEN_URL
    assert issuer.requests[0][2] == {
        "grant_type": "authorization_code",
        "code": "fake-code",
        "client_id": LOOPBACK_PUBLIC_CLIENT_ID,
        "redirect_uri": LOOPBACK_REDIRECT_URI,
        "code_verifier": transaction.code_verifier,
        "resource": LOOPBACK_RESOURCE,
    }
    assert stored == [
        (
            "alice",
            "74d40886-9a8d-44da-941a-4c490bb7c8da",
            "fake-access-token",
            "fake-refresh-token",
            3600,
            list(LOOPBACK_SCOPES),
        )
    ]
    assert invalidated == [("alice", "74d40886-9a8d-44da-941a-4c490bb7c8da")]
    assert all(
        value not in caplog.text for value in (state, transaction.code_verifier, "fake-code", "fake-access-token")
    )


@pytest.mark.asyncio
async def test_replay_and_concurrent_completion_have_exactly_one_winner() -> None:
    redis: Final = FakeRedis()
    state, _ = await transaction_from_start(redis)
    issuer: Final = FakeIssuer()
    stored: Final[list[tuple[object, ...]]] = []
    invalidated: Final[list[tuple[str, str]]] = []

    results: Final = await asyncio.gather(
        complete(redis, state, issuer, stored, invalidated),
        complete(redis, state, issuer, stored, invalidated),
        return_exceptions=True,
    )

    assert sum(not isinstance(result, Exception) for result in results) == 1
    assert len(issuer.requests) == 1
    assert len(stored) == 1


@pytest.mark.asyncio
async def test_delayed_duplicate_readiness_cannot_overwrite_connected() -> None:
    redis: Final = PausedReadinessRedis()
    start: Final = await start_loopback_oauth(redis=redis, server=server(), user_id="alice")
    delayed: Final = asyncio.create_task(mark_loopback_oauth_ready(redis=redis, transaction_id=start.transaction_id))
    await redis.readiness_entered.wait()
    redis.release_readiness.set()
    await delayed
    state: Final = parse_qs(urlparse(start.authorization_url).query)["state"][0]
    await complete(redis, state, FakeIssuer(), [], [])

    with pytest.raises(HTTPException) as duplicate:
        await mark_loopback_oauth_ready(redis=redis, transaction_id=start.transaction_id)

    assert duplicate.value.status_code == 409
    from litellm.proxy._experimental.mcp_server.loopback_oauth import get_loopback_oauth_status

    status_result: Final = await get_loopback_oauth_status(
        redis=redis,
        transaction_id=start.transaction_id,
        user_id="alice",
        server_id=server().server_id,
    )
    assert status_result.status == "connected"


@pytest.mark.asyncio
async def test_expired_or_missing_state_fails_before_exchange() -> None:
    redis: Final = FakeRedis()
    issuer: Final = FakeIssuer()

    with pytest.raises(HTTPException) as exc:
        await complete(redis, "x" * 43, issuer, [], [])

    assert exc.value.status_code == 400
    assert issuer.requests == []


@pytest.mark.asyncio
async def test_expired_transaction_fails_before_exchange(monkeypatch: pytest.MonkeyPatch) -> None:
    redis: Final = FakeRedis()
    state, transaction = await transaction_from_start(redis)
    issuer: Final = FakeIssuer()
    monkeypatch.setattr(
        "litellm.proxy._experimental.mcp_server.loopback_oauth.time.time",
        lambda: transaction.created_at + 301,
    )

    with pytest.raises(HTTPException) as exc:
        await complete(redis, state, issuer, [], [])

    assert exc.value.status_code == 400
    assert issuer.requests == []


def test_completion_rejects_caller_supplied_binding_fields() -> None:
    with pytest.raises(ValidationError):
        LoopbackOAuthCompletionRequest.model_validate(
            {"state": "x" * 43, "code": "fake-code", "user_id": "mallory", "server_id": "other"}
        )


def test_relay_auth_rejects_missing_and_wrong_bearer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LITELLM_LOOPBACK_OAUTH_RELAY_SECRET", "correct-service-secret-with-32-bytes")

    for authorization in (None, "Bearer wrong-service-secret-with-32-bytes"):
        with pytest.raises(HTTPException) as exc:
            authenticate_loopback_oauth_relay(authorization)
        assert exc.value.status_code == 401

    authenticate_loopback_oauth_relay("Bearer correct-service-secret-with-32-bytes")


@pytest.mark.asyncio
async def test_wrong_server_binding_fails_before_exchange() -> None:
    redis: Final = FakeRedis()
    state, _ = await transaction_from_start(redis)
    issuer: Final = FakeIssuer()

    async def wrong_server(server_id: str) -> MCPServer | None:
        return server(f"wrong-{server_id}")

    with pytest.raises(HTTPException) as exc:
        await complete(redis, state, issuer, [], [], wrong_server)

    assert exc.value.status_code == 400
    assert issuer.requests == []


@pytest.mark.asyncio
async def test_start_enforces_three_active_transactions_per_user_server() -> None:
    redis: Final = FakeRedis()
    for _ in range(3):
        await start_loopback_oauth(redis=redis, server=server(), user_id="alice")

    with pytest.raises(HTTPException) as exc:
        await start_loopback_oauth(redis=redis, server=server(), user_id="alice")

    assert exc.value.status_code == 429


@pytest.mark.asyncio
async def test_consumed_and_denied_transactions_release_active_capacity() -> None:
    redis: Final = FakeRedis()
    states: Final = [await transaction_from_start(redis) for _ in range(3)]
    stored: Final[list[tuple[object, ...]]] = []
    await complete(redis, states[0][0], FakeIssuer(), stored, [])

    fourth: Final = await start_loopback_oauth(redis=redis, server=server(), user_id="alice")
    assert fourth.expires_in == 300
    await mark_loopback_oauth_ready(redis=redis, transaction_id=fourth.transaction_id)

    denied_state: Final = parse_qs(urlparse(fourth.authorization_url).query)["state"][0]

    async def get_server(server_id: str) -> MCPServer | None:
        return server(server_id)

    async def not_called(*args: object) -> None:
        pytest.fail(f"unexpected call: {args!r}")

    await complete_loopback_oauth(
        redis=redis,
        http_client=FakeIssuer(),
        payload=LoopbackOAuthCompletionRequest(state=denied_state, error="access_denied"),
        get_server=get_server,
        store_credential=not_called,
        invalidate_cache=not_called,
    )
    replacement: Final = await start_loopback_oauth(redis=redis, server=server(), user_id="alice")
    assert replacement.expires_in == 300


@pytest.mark.asyncio
async def test_denial_consumes_transaction_without_exchange_or_store() -> None:
    redis: Final = FakeRedis()
    state, _ = await transaction_from_start(redis)
    issuer: Final = FakeIssuer()

    async def get_server(server_id: str) -> MCPServer | None:
        return server(server_id)

    result: Final = await complete_loopback_oauth(
        redis=redis,
        http_client=issuer,
        payload=LoopbackOAuthCompletionRequest(state=state, error="access_denied"),
        get_server=get_server,
        store_credential=lambda *_: pytest.fail("must not store"),
        invalidate_cache=lambda *_: pytest.fail("must not invalidate"),
    )

    assert result.outcome == "denied"
    assert issuer.requests == []


@pytest.mark.asyncio
async def test_exchange_failure_is_consumed_and_requires_new_start() -> None:
    redis: Final = FakeRedis()
    state, _ = await transaction_from_start(redis)
    issuer: Final = FakeIssuer(FakeResponse({}, failure=True))

    with pytest.raises(HTTPException) as first:
        await complete(redis, state, issuer, [], [])
    with pytest.raises(HTTPException) as replay:
        await complete(redis, state, issuer, [], [])

    assert first.value.status_code == 502
    assert replay.value.status_code == 400
    assert len(issuer.requests) == 1


@pytest.mark.asyncio
async def test_exchange_transport_failure_is_sanitized_502_and_consumed() -> None:
    redis: Final = FakeRedis()
    state, _ = await transaction_from_start(redis)
    stored: Final[list[tuple[object, ...]]] = []
    invalidated: Final[list[tuple[str, str]]] = []

    with pytest.raises(HTTPException) as first:
        await complete(redis, state, TransportFailureIssuer(), stored, invalidated)
    with pytest.raises(HTTPException) as replay:
        await complete(redis, state, FakeIssuer(), stored, invalidated)

    assert first.value.status_code == 502
    assert first.value.detail == {"error": "OAuth exchange failed; start again"}
    assert replay.value.status_code == 400
    assert stored == []
    assert invalidated == []


def test_server_binding_requires_exact_upstream_resource() -> None:
    wrong: Final = server().model_copy(update={"upstream_resource": None})

    with pytest.raises(HTTPException) as exc:
        from litellm.proxy._experimental.mcp_server.loopback_oauth import validate_loopback_oauth_server

        validate_loopback_oauth_server(wrong)

    assert exc.value.status_code == 400
