import base64
import hashlib
import hmac
import os
import secrets
import time
from collections.abc import Awaitable, Callable
from typing import Final, Literal, Protocol, cast
from urllib.parse import urlencode

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, model_validator

from litellm._logging import verbose_proxy_logger
from litellm.proxy.common_utils.encrypt_decrypt_utils import decrypt_value_helper, encrypt_value_helper
from litellm.types.mcp import MCPAuth
from litellm.types.mcp_server.mcp_server_manager import MCPServer

LOOPBACK_REDIRECT_URI: Final = "http://127.0.0.1:43119/callback"
LOOPBACK_TRANSACTION_TTL_SECONDS: Final = 300
LOOPBACK_MAX_ACTIVE_TRANSACTIONS: Final = 3
LOOPBACK_START_RATE_LIMIT: Final = 10
LOOPBACK_COMPLETION_RATE_LIMIT: Final = 30
LOOPBACK_RATE_WINDOW_SECONDS: Final = 60
LOOPBACK_PUBLIC_CLIENT_ID: Final = "6d465f583e1e4ce5801b1616f735670c"
LOOPBACK_SERVER_ID: Final = "74d40886-9a8d-44da-941a-4c490bb7c8da"
LOOPBACK_RESOURCE: Final = "https://mcp.lovable.dev"
LOOPBACK_ISSUER: Final = "https://lovable.dev/oauth"
LOOPBACK_AUTHORIZATION_URL: Final = "https://lovable.dev/oauth/authorize"
LOOPBACK_TOKEN_URL: Final = "https://lovable.dev/oauth/token"
LOOPBACK_REGISTRATION_URL: Final = "https://lovable.dev/oauth/register"
LOOPBACK_SCOPES: Final = (
    "offline",
    "projects:read",
    "projects:write",
    "projects:create",
    "workspaces:read",
    "workspaces:write",
)
_TRANSACTION_PREFIX: Final = "litellm:mcp:loopback_oauth:transaction"
_TRANSACTION_ACTIVE_PREFIX: Final = "litellm:mcp:loopback_oauth:transaction_active"
_ACTIVE_PREFIX: Final = "litellm:mcp:loopback_oauth:active"
_RATE_PREFIX: Final = "litellm:mcp:loopback_oauth:rate"
_STATUS_PREFIX: Final = "litellm:mcp:loopback_oauth:status"
_STATUS_PHASE_PREFIX: Final = "litellm:mcp:loopback_oauth:status_phase"


class LoopbackOAuthRedis(Protocol):
    async def eval(self, script: str, numkeys: int, *keys_and_args: object) -> object: ...


class LoopbackOAuthHTTPResponse(Protocol):
    def raise_for_status(self) -> None: ...

    def json(self) -> object: ...


class LoopbackOAuthHTTPClient(Protocol):
    async def post(self, url: str, *, headers: dict[str, str], data: dict[str, str]) -> LoopbackOAuthHTTPResponse: ...


class LoopbackOAuthStartResponse(BaseModel):
    authorization_url: str
    transaction_id: str
    expires_in: Literal[300] = 300


class LoopbackOAuthReadyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str = Field(min_length=43, max_length=128)


class LoopbackOAuthStatusResponse(BaseModel):
    status: Literal["pending", "ready", "connected", "denied", "failed"]


class LoopbackOAuthCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: str = Field(min_length=43, max_length=128)
    code: str | None = Field(default=None, min_length=1, max_length=2048)
    error: str | None = Field(default=None, min_length=1, max_length=128)
    error_description: str | None = Field(default=None, max_length=512)

    @model_validator(mode="after")
    def validate_shape(self) -> "LoopbackOAuthCompletionRequest":
        if (self.code is None) == (self.error is None):
            raise ValueError("exactly one of code or error is required")
        return self


class LoopbackOAuthCompletionResponse(BaseModel):
    outcome: Literal["connected", "denied"]


class _TokenResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    access_token: str = Field(min_length=1, max_length=16384)
    refresh_token: str | None = Field(default=None, max_length=16384)
    expires_in: int | None = Field(default=None, gt=0, le=31_536_000)
    scope: str | None = Field(default=None, max_length=2048)
    token_type: str | None = Field(default=None, max_length=64)


class LoopbackOAuthTransaction(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: str
    server_id: str
    redirect_uri: str
    code_verifier: str
    scopes: tuple[str, ...]
    resource: str
    client_id: str
    issuer: str
    authorization_url: str
    token_url: str
    created_at: int
    transaction_id: str


class LoopbackOAuthStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: str
    server_id: str
    transaction_id: str
    status: Literal["pending", "ready", "connected", "denied", "failed"]
    created_at: int


_START_SCRIPT: Final = """
local now = tonumber(ARGV[1])
redis.call('ZREMRANGEBYSCORE', KEYS[3], '-inf', now)
if redis.call('ZCARD', KEYS[3]) >= tonumber(ARGV[4]) then return 0 end
local stored = redis.call('SET', KEYS[1], ARGV[2], 'EX', tonumber(ARGV[3]), 'NX')
if not stored then return 0 end
redis.call('SET', KEYS[2], KEYS[3], 'EX', tonumber(ARGV[3]))
redis.call('SET', KEYS[4], ARGV[6], 'EX', tonumber(ARGV[3]))
redis.call('SET', KEYS[5], 'pending', 'EX', tonumber(ARGV[3]))
redis.call('ZADD', KEYS[3], now + tonumber(ARGV[3]), ARGV[5])
redis.call('EXPIRE', KEYS[3], tonumber(ARGV[3]))
return 1
"""
_CONSUME_SCRIPT: Final = """
local value = redis.call('GET', KEYS[1])
if not value then return false end
local active_key = redis.call('GET', KEYS[2])
redis.call('DEL', KEYS[1])
redis.call('DEL', KEYS[2])
if active_key then redis.call('ZREM', active_key, ARGV[1]) end
return value
"""
_STATUS_GET_SCRIPT: Final = "return redis.call('GET', KEYS[1])"
_STATUS_TRANSITION_SCRIPT: Final = """
local current = redis.call('GET', KEYS[2])
if not current or current ~= ARGV[1] then return 0 end
redis.call('SET', KEYS[1], ARGV[2], 'EX', tonumber(ARGV[4]))
redis.call('SET', KEYS[2], ARGV[3], 'EX', tonumber(ARGV[4]))
return 1
"""
_RATE_SCRIPT: Final = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then redis.call('EXPIRE', KEYS[1], tonumber(ARGV[1])) end
return count
"""


def _redis_eval_exception(exc: Exception) -> HTTPException:
    verbose_proxy_logger.warning("loopback_oauth_redis outcome=unavailable")
    return HTTPException(status_code=503, detail={"error": "Loopback OAuth is unavailable"})


def get_loopback_oauth_redis() -> LoopbackOAuthRedis:
    from litellm.proxy.proxy_server import redis_usage_cache

    if redis_usage_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Loopback OAuth is unavailable"})
    return cast(
        LoopbackOAuthRedis,
        redis_usage_cache.init_async_client(),  # pyright: ignore[reportUnknownMemberType]  # Redis library stubs omit response typing
    )


def get_loopback_oauth_http_client() -> LoopbackOAuthHTTPClient:
    from litellm.llms.custom_httpx.http_handler import (
        get_async_httpx_client,  # pyright: ignore[reportUnknownVariableType]  # legacy factory params are untyped
    )
    from litellm.types.llms.custom_http import httpxSpecialProvider

    return cast(
        LoopbackOAuthHTTPClient,
        get_async_httpx_client(llm_provider=httpxSpecialProvider.Oauth2Check),
    )


def _safe_server_key(user_id: str, server_id: str) -> str:
    return hashlib.sha256(f"{user_id}\0{server_id}".encode()).hexdigest()


def _transaction_key(state: str) -> str:
    return f"{_TRANSACTION_PREFIX}:{hashlib.sha256(state.encode()).hexdigest()}"


def _transaction_active_key(state: str) -> str:
    return f"{_TRANSACTION_ACTIVE_PREFIX}:{hashlib.sha256(state.encode()).hexdigest()}"


def _active_key(user_id: str, server_id: str) -> str:
    return f"{_ACTIVE_PREFIX}:{_safe_server_key(user_id, server_id)}"


def _status_key(transaction_id: str) -> str:
    return f"{_STATUS_PREFIX}:{hashlib.sha256(transaction_id.encode()).hexdigest()}"


def _status_phase_key(transaction_id: str) -> str:
    return f"{_STATUS_PHASE_PREFIX}:{hashlib.sha256(transaction_id.encode()).hexdigest()}"


def _correlation(state: str) -> str:
    key: Final = os.getenv("LITELLM_LOOPBACK_OAUTH_LOG_KEY", "loopback-oauth-correlation").encode()
    return hmac.new(key, state.encode(), hashlib.sha256).hexdigest()[:12]


def _configured_relay_secret() -> str:
    secret_file: Final = os.getenv("LITELLM_LOOPBACK_OAUTH_RELAY_SECRET_FILE")
    if secret_file:
        try:
            with open(secret_file, encoding="utf-8") as file:
                return file.read().strip()
        except OSError:
            return ""
    return os.getenv("LITELLM_LOOPBACK_OAUTH_RELAY_SECRET", "")


def authenticate_loopback_oauth_relay(authorization: str | None) -> None:
    expected: Final = _configured_relay_secret()
    supplied: Final = authorization[7:] if authorization and authorization.startswith("Bearer ") else ""
    if len(expected) < 32 or not hmac.compare_digest(supplied.encode(), expected.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": "Unauthorized"})


def validate_loopback_oauth_server(server: MCPServer) -> None:
    actual: Final = (
        server.server_id,
        server.alias,
        server.url,
        server.auth_type,
        server.oauth2_flow,
        server.issuer,
        server.authorization_url,
        server.token_url,
        server.registration_url,
        server.client_id,
        tuple(server.scopes or ()),
        server.upstream_resource,
    )
    expected: Final = (
        LOOPBACK_SERVER_ID,
        "lovable",
        LOOPBACK_RESOURCE,
        MCPAuth.oauth2,
        "authorization_code",
        LOOPBACK_ISSUER,
        LOOPBACK_AUTHORIZATION_URL,
        LOOPBACK_TOKEN_URL,
        LOOPBACK_REGISTRATION_URL,
        LOOPBACK_PUBLIC_CLIENT_ID,
        LOOPBACK_SCOPES,
        LOOPBACK_RESOURCE,
    )
    if actual != expected:
        raise HTTPException(status_code=400, detail={"error": "Server is not configured for loopback OAuth"})


def is_loopback_oauth_server_candidate(server: MCPServer) -> bool:
    try:
        validate_loopback_oauth_server(server)
    except HTTPException:
        return False
    return True


def _encrypt_status(status_record: LoopbackOAuthStatus) -> str:
    return encrypt_value_helper(status_record.model_dump_json())


def _decode_status(encrypted: str | bytes) -> LoopbackOAuthStatus:
    value: Final = encrypted.decode() if isinstance(encrypted, bytes) else encrypted
    decrypted: Final = decrypt_value_helper(value=value, key="loopback_oauth_status")
    if not isinstance(decrypted, str):
        raise HTTPException(status_code=404, detail={"error": "Transaction not found"})
    try:
        return LoopbackOAuthStatus.model_validate_json(decrypted)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"error": "Transaction not found"}) from exc


async def _get_status(redis: LoopbackOAuthRedis, transaction_id: str) -> LoopbackOAuthStatus:
    try:
        encrypted: Final = await redis.eval(_STATUS_GET_SCRIPT, 1, _status_key(transaction_id))
    except Exception as exc:
        raise _redis_eval_exception(exc) from exc
    if not encrypted:
        raise HTTPException(status_code=404, detail={"error": "Transaction not found"})
    return _decode_status(cast(str | bytes, encrypted))


async def _transition_status(
    redis: LoopbackOAuthRedis, current: LoopbackOAuthStatus, updated: LoopbackOAuthStatus
) -> None:
    remaining: Final = max(1, updated.created_at + LOOPBACK_TRANSACTION_TTL_SECONDS - int(time.time()))
    try:
        transitioned: Final = await redis.eval(
            _STATUS_TRANSITION_SCRIPT,
            2,
            _status_key(updated.transaction_id),
            _status_phase_key(updated.transaction_id),
            current.status,
            _encrypt_status(updated),
            updated.status,
            remaining,
        )
    except Exception as exc:
        raise _redis_eval_exception(exc) from exc
    if int(cast(int, transitioned)) != 1:
        raise HTTPException(status_code=409, detail={"error": "Transaction status changed"})


async def _enforce_rate_limit(redis: LoopbackOAuthRedis, key: str, limit: int) -> None:
    try:
        count: Final = await redis.eval(_RATE_SCRIPT, 1, key, LOOPBACK_RATE_WINDOW_SECONDS)
    except Exception as exc:
        raise _redis_eval_exception(exc) from exc
    if int(cast(int, count)) > limit:
        raise HTTPException(status_code=429, detail={"error": "Too many requests"})


async def start_loopback_oauth(
    *,
    redis: LoopbackOAuthRedis,
    server: MCPServer,
    user_id: str,
) -> LoopbackOAuthStartResponse:
    validate_loopback_oauth_server(server)
    await _enforce_rate_limit(
        redis,
        f"{_RATE_PREFIX}:start:{_safe_server_key(user_id, server.server_id)}",
        LOOPBACK_START_RATE_LIMIT,
    )
    state: Final = secrets.token_urlsafe(32)
    transaction_id: Final = secrets.token_urlsafe(32)
    verifier: Final = secrets.token_urlsafe(64)
    challenge: Final = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    now: Final = int(time.time())
    transaction: Final = LoopbackOAuthTransaction(
        user_id=user_id,
        server_id=server.server_id,
        redirect_uri=LOOPBACK_REDIRECT_URI,
        code_verifier=verifier,
        scopes=LOOPBACK_SCOPES,
        resource=LOOPBACK_RESOURCE,
        client_id=LOOPBACK_PUBLIC_CLIENT_ID,
        issuer=LOOPBACK_ISSUER,
        authorization_url=LOOPBACK_AUTHORIZATION_URL,
        token_url=LOOPBACK_TOKEN_URL,
        created_at=now,
        transaction_id=transaction_id,
    )
    status_record: Final = LoopbackOAuthStatus(
        user_id=user_id,
        server_id=server.server_id,
        transaction_id=transaction_id,
        status="pending",
        created_at=now,
    )
    encrypted: Final[str] = encrypt_value_helper(transaction.model_dump_json())
    try:
        stored: Final = await redis.eval(
            _START_SCRIPT,
            5,
            _transaction_key(state),
            _transaction_active_key(state),
            _active_key(user_id, server.server_id),
            _status_key(transaction_id),
            _status_phase_key(transaction_id),
            now,
            encrypted,
            LOOPBACK_TRANSACTION_TTL_SECONDS,
            LOOPBACK_MAX_ACTIVE_TRANSACTIONS,
            hashlib.sha256(state.encode()).hexdigest(),
            _encrypt_status(status_record),
        )
    except Exception as exc:
        raise _redis_eval_exception(exc) from exc
    if int(cast(int, stored)) != 1:
        raise HTTPException(status_code=429, detail={"error": "Too many active transactions"})
    params: Final = {
        "client_id": LOOPBACK_PUBLIC_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": LOOPBACK_REDIRECT_URI,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "scope": " ".join(LOOPBACK_SCOPES),
        "resource": LOOPBACK_RESOURCE,
    }
    verbose_proxy_logger.info(
        "loopback_oauth_start outcome=created server_id=%s correlation=%s",
        server.server_id,
        _correlation(state),
    )
    return LoopbackOAuthStartResponse(
        authorization_url=f"{LOOPBACK_AUTHORIZATION_URL}?{urlencode(params)}",
        transaction_id=transaction_id,
    )


async def mark_loopback_oauth_ready(*, redis: LoopbackOAuthRedis, transaction_id: str) -> LoopbackOAuthStatusResponse:
    current: Final = await _get_status(redis, transaction_id)
    if current.status != "pending":
        raise HTTPException(status_code=409, detail={"error": "Transaction is not pending"})
    ready: Final = current.model_copy(update={"status": "ready"})
    await _transition_status(redis, current, ready)
    return LoopbackOAuthStatusResponse(status="ready")


async def get_loopback_oauth_status(
    *, redis: LoopbackOAuthRedis, transaction_id: str, user_id: str, server_id: str
) -> LoopbackOAuthStatusResponse:
    current: Final = await _get_status(redis, transaction_id)
    if not hmac.compare_digest(current.user_id, user_id) or not hmac.compare_digest(current.server_id, server_id):
        raise HTTPException(status_code=404, detail={"error": "Transaction not found"})
    return LoopbackOAuthStatusResponse(status=current.status)


def _decode_transaction(encrypted: str) -> LoopbackOAuthTransaction:
    decrypted: Final = decrypt_value_helper(value=encrypted, key="loopback_oauth_transaction")
    if not isinstance(decrypted, str):
        raise HTTPException(status_code=400, detail={"error": "Invalid or expired transaction"})
    try:
        return LoopbackOAuthTransaction.model_validate_json(decrypted)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": "Invalid or expired transaction"}) from exc


def _validate_consumed_transaction(transaction: LoopbackOAuthTransaction, server: MCPServer) -> None:
    validate_loopback_oauth_server(server)
    expected: Final = (
        server.server_id,
        LOOPBACK_REDIRECT_URI,
        LOOPBACK_SCOPES,
        LOOPBACK_RESOURCE,
        LOOPBACK_PUBLIC_CLIENT_ID,
        LOOPBACK_ISSUER,
        LOOPBACK_AUTHORIZATION_URL,
        LOOPBACK_TOKEN_URL,
    )
    actual: Final = (
        transaction.server_id,
        transaction.redirect_uri,
        transaction.scopes,
        transaction.resource,
        transaction.client_id,
        transaction.issuer,
        transaction.authorization_url,
        transaction.token_url,
    )
    if actual != expected or transaction.created_at + LOOPBACK_TRANSACTION_TTL_SECONDS < int(time.time()):
        raise HTTPException(status_code=400, detail={"error": "Invalid or expired transaction"})


async def complete_loopback_oauth(
    *,
    redis: LoopbackOAuthRedis,
    http_client: LoopbackOAuthHTTPClient,
    payload: LoopbackOAuthCompletionRequest,
    get_server: Callable[[str], Awaitable[MCPServer | None]],
    store_credential: Callable[[str, str, str, str | None, int | None, list[str]], Awaitable[None]],
    invalidate_cache: Callable[[str, str], Awaitable[None]],
) -> LoopbackOAuthCompletionResponse:
    await _enforce_rate_limit(redis, f"{_RATE_PREFIX}:completion", LOOPBACK_COMPLETION_RATE_LIMIT)
    try:
        state_hash: Final = hashlib.sha256(payload.state.encode()).hexdigest()
        consumed: Final = await redis.eval(
            _CONSUME_SCRIPT,
            2,
            _transaction_key(payload.state),
            _transaction_active_key(payload.state),
            state_hash,
        )
    except Exception as exc:
        raise _redis_eval_exception(exc) from exc
    if not consumed:
        raise HTTPException(status_code=400, detail={"error": "Invalid or expired transaction"})
    transaction: Final = _decode_transaction(consumed.decode() if isinstance(consumed, bytes) else str(consumed))
    readiness: Final = await _get_status(redis, transaction.transaction_id)
    if readiness.status != "ready":
        raise HTTPException(status_code=400, detail={"error": "Invalid or expired transaction"})
    server: Final = await get_server(transaction.server_id)
    if server is None:
        raise HTTPException(status_code=400, detail={"error": "Invalid or expired transaction"})
    _validate_consumed_transaction(transaction, server)
    correlation: Final = _correlation(payload.state)
    if payload.error is not None:
        await _transition_status(
            redis,
            readiness,
            LoopbackOAuthStatus(
                user_id=transaction.user_id,
                server_id=transaction.server_id,
                transaction_id=transaction.transaction_id,
                status="denied",
                created_at=transaction.created_at,
            ),
        )
        verbose_proxy_logger.info(
            "loopback_oauth_complete outcome=denied server_id=%s correlation=%s",
            server.server_id,
            correlation,
        )
        return LoopbackOAuthCompletionResponse(outcome="denied")
    try:
        response: Final = await http_client.post(
            LOOPBACK_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "grant_type": "authorization_code",
                "code": cast(str, payload.code),
                "client_id": LOOPBACK_PUBLIC_CLIENT_ID,
                "redirect_uri": LOOPBACK_REDIRECT_URI,
                "code_verifier": transaction.code_verifier,
                "resource": LOOPBACK_RESOURCE,
            },
        )
        response.raise_for_status()
        token: Final = _TokenResponse.model_validate(response.json())
    except Exception as exc:
        await _transition_status(
            redis,
            readiness,
            LoopbackOAuthStatus(
                user_id=transaction.user_id,
                server_id=transaction.server_id,
                transaction_id=transaction.transaction_id,
                status="failed",
                created_at=transaction.created_at,
            ),
        )
        verbose_proxy_logger.warning(
            "loopback_oauth_complete outcome=exchange_failed server_id=%s correlation=%s",
            server.server_id,
            correlation,
        )
        raise HTTPException(status_code=502, detail={"error": "OAuth exchange failed; start again"}) from exc
    scopes: Final[list[str]] = token.scope.split() if token.scope else [str(scope) for scope in LOOPBACK_SCOPES]
    await store_credential(
        transaction.user_id,
        transaction.server_id,
        token.access_token,
        token.refresh_token,
        token.expires_in,
        scopes,
    )
    await invalidate_cache(transaction.user_id, transaction.server_id)
    await _transition_status(
        redis,
        readiness,
        LoopbackOAuthStatus(
            user_id=transaction.user_id,
            server_id=transaction.server_id,
            transaction_id=transaction.transaction_id,
            status="connected",
            created_at=transaction.created_at,
        ),
    )
    verbose_proxy_logger.info(
        "loopback_oauth_complete outcome=connected server_id=%s correlation=%s",
        server.server_id,
        correlation,
    )
    return LoopbackOAuthCompletionResponse(outcome="connected")
