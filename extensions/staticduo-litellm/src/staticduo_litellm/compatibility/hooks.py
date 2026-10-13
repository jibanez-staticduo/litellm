"""LiteLLM callback integration for Portable Codex policies."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import AsyncIterator, Mapping
from typing import Final

from fastapi import HTTPException
from pydantic import BaseModel
from redis.asyncio import Redis
from redis.exceptions import RedisError

from litellm.caching.dual_cache import DualCache
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy._types import UserAPIKeyAuth
from litellm.types.utils import CallTypesLiteral
from staticduo_litellm.codex.portable import (
    CONTEXT,
    ROUTES,
    PortableTransportError,
    ReplayStore,
    RequestContext,
    items,
    needs_transport,
    object_mapping,
)
from staticduo_litellm.codex.portable import (
    has_legacy_history as policy_has_legacy_history,
)
from staticduo_litellm.codex.portable import (
    mode_key as policy_mode_key,
)
from staticduo_litellm.codex.portable import (
    transform_request as policy_transform_request,
)
from staticduo_litellm.codex.portable import (
    transform_response as policy_transform_response,
)


class RedisReplayStore:
    def __init__(self, client: Redis[str]) -> None:
        self.client = client

    async def contains(self, key: str) -> bool:
        try:
            return bool(await self.client.exists(key))
        except RedisError:
            raise HTTPException(503, "Portable agent replay storage is unavailable.") from None

    async def record(self, key: str) -> None:
        try:
            await self.client.set(key, "1")
        except RedisError:
            raise HTTPException(503, "Portable agent replay storage is unavailable.") from None

    async def get_mode(self, key: str) -> str | None:
        try:
            value: Final = await self.client.get(key)
        except RedisError:
            raise HTTPException(503, "Portable agent replay storage is unavailable.") from None
        if value is not None and value not in ("legacy", "portable"):
            raise HTTPException(503, "Portable agent thread mode is invalid.")
        return value

    async def claim_mode(self, key: str, mode: str) -> str:
        try:
            await self.client.set(key, mode, nx=True)
        except RedisError:
            raise HTTPException(503, "Portable agent replay storage is unavailable.") from None
        selected: Final = await self.get_mode(key)
        if selected is None:
            raise HTTPException(503, "Portable agent thread mode could not be recorded.")
        return selected


def mode_key(data: Mapping[str, object], owner: str) -> str:
    try:
        return policy_mode_key(data, owner)
    except PortableTransportError as error:
        raise HTTPException(error.status_code, error.detail) from None


async def has_legacy_history(data: Mapping[str, object], owner: str, store: ReplayStore) -> bool:
    try:
        return await policy_has_legacy_history(data, owner, store)
    except PortableTransportError as error:
        raise HTTPException(error.status_code, error.detail) from None


async def transform_request(
    original: Mapping[str, object], owner: str, store: ReplayStore, *, native_history: bool = False
) -> tuple[Mapping[str, object], RequestContext]:
    try:
        result, context = await policy_transform_request(original, owner, store, native_history=native_history)
    except PortableTransportError as error:
        raise HTTPException(error.status_code, error.detail) from None
    return {**result}, context


async def transform_response(
    value: Mapping[str, object], context: RequestContext, store: ReplayStore
) -> Mapping[str, object]:
    try:
        return {**await policy_transform_response(value, context, store)}
    except PortableTransportError as error:
        raise HTTPException(error.status_code, error.detail) from None


def _owner(auth: UserAPIKeyAuth) -> str:
    identity: Final = auth.api_key or auth.user_id
    if not identity:
        raise HTTPException(400, "Portable agent transport requires an authenticated identity.")
    return hashlib.sha256(json.dumps((auth.team_id, identity)).encode()).hexdigest()


class PortableCodexAgents(CustomLogger):
    def __init__(
        self, models: frozenset[str], store: ReplayStore | None, native_models: frozenset[str] = frozenset()
    ) -> None:
        super().__init__()  # pyright: ignore[reportUnknownMemberType]  # Upstream CustomLogger has untyped **kwargs.
        self.models = models
        self.store = store
        self.native_models = native_models

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: Mapping[str, object],
        call_type: CallTypesLiteral,
    ) -> dict[str, object]:  # mutable-ok: LiteLLM pre-call ABI returns a mutable request payload
        metadata: Final = object_mapping(data.get("metadata"))
        clean_metadata: Final = {key: value for key, value in metadata.items() if key != CONTEXT}
        internal: Final = object_mapping(data.get("litellm_metadata"))
        clean_internal: Final = {key: value for key, value in internal.items() if key != CONTEXT}
        if call_type != "aresponses" or data.get("model") not in self.models or not needs_transport(data):
            return {
                **data,
                **({"metadata": clean_metadata} if "metadata" in data else {}),
                **({"litellm_metadata": clean_internal} if "litellm_metadata" in data else {}),
            }
        if self.store is None:
            raise HTTPException(503, "Portable Codex transport requires PORTABLE_CODEX_REDIS_URL.")
        owner: Final = _owner(user_api_key_dict)
        key: Final = mode_key(data, owner)
        existing: Final = await self.store.get_mode(key)
        legacy: Final = existing is None and await has_legacy_history(data, owner, self.store)
        if legacy and data.get("model") not in self.native_models:
            raise HTTPException(
                400, "Legacy encrypted collaboration requires a native provider or a fresh portable task."
            )
        mode: Final = existing or await self.store.claim_mode(key, "legacy" if legacy else "portable")
        if mode == "legacy" and data.get("model") not in self.native_models:
            raise HTTPException(
                400, "This legacy task requires a native Responses provider. Start a fresh portable task."
            )
        transformed, context = await transform_request(data, owner, self.store, native_history=mode == "legacy")
        return {
            **transformed,
            **({"metadata": clean_metadata} if "metadata" in data else {}),
            "litellm_metadata": {**clean_internal, CONTEXT: {"owner": context.owner, "tools": sorted(context.tools)}},
        }

    def _context(self, data: Mapping[str, object], auth: UserAPIKeyAuth) -> RequestContext | None:
        fields: Final = object_mapping(object_mapping(data.get("litellm_metadata")).get(CONTEXT))
        if not fields or auth.request_route not in ROUTES:
            return None
        if fields.get("owner") != _owner(auth):
            raise HTTPException(400, "Portable transport request identity changed.")
        return RequestContext(str(fields["owner"]), frozenset(str(name) for name in items(fields.get("tools"))))

    async def _rewrite(self, response: object, context: RequestContext) -> object:
        if self.store is None:
            raise HTTPException(503, "Portable Codex replay storage is not configured.")
        if isinstance(response, BaseModel):
            original: Final = response.model_dump(mode="json")
            rewritten: Final = await transform_response(original, context, self.store)
            if rewritten == original:
                return response
            validated: Final = type(response).model_validate(rewritten)
            return response.model_copy(deep=True, update=validated.__dict__)
        normalized: Final = object_mapping(response)
        if isinstance(response, Mapping):
            return await transform_response(normalized, context, self.store)
        return response

    async def async_post_call_success_hook(
        self,
        data: Mapping[str, object],
        user_api_key_dict: UserAPIKeyAuth,
        response: object,
    ) -> object:
        context: Final = self._context(data, user_api_key_dict)
        return await self._rewrite(response, context) if context else response

    async def async_post_call_streaming_iterator_hook(  # pyright: ignore[reportIncompatibleMethodOverride]  # Responses SSE includes SDK events beyond CustomLogger completion streams.
        self,
        user_api_key_dict: UserAPIKeyAuth,
        response: AsyncIterator[object],
        request_data: Mapping[str, object],
    ) -> AsyncIterator[object]:
        context: Final = self._context(request_data, user_api_key_dict)
        async for chunk in response:
            yield await self._rewrite(chunk, context) if context else chunk


def _configured_callback() -> PortableCodexAgents:
    models: Final = frozenset(
        name.strip() for name in os.environ.get("PORTABLE_CODEX_MODELS", "").split(",") if name.strip()
    )
    url: Final = os.environ.get("PORTABLE_CODEX_REDIS_URL", "")
    host: Final = os.environ.get("REDIS_HOST")
    client: Final = (
        Redis.from_url(url, decode_responses=True, socket_timeout=5, socket_connect_timeout=5)
        if url
        else Redis(
            host=host,
            port=int(os.environ.get("REDIS_PORT", "6379")),
            username=os.environ.get("REDIS_USERNAME") or None,
            password=os.environ.get("REDIS_PASSWORD") or None,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        if host
        else None
    )
    native_models: Final = frozenset(
        name.strip() for name in os.environ.get("PORTABLE_CODEX_NATIVE_MODELS", "").split(",") if name.strip()
    )
    return PortableCodexAgents(models, RedisReplayStore(client) if client else None, native_models)


portable_codex_agents: Final = _configured_callback()
