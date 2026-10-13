from __future__ import annotations

from typing import Final, cast  # noqa: TID251  # typed Redis and HTTP client ABI adapters

from fastapi import HTTPException

from litellm.proxy.common_utils.encrypt_decrypt_utils import decrypt_value_helper, encrypt_value_helper
from staticduo_litellm.lazy.loopback_oauth import LoopbackOAuthHTTPClient, LoopbackOAuthRedis

__all__ = ["decrypt_value_helper", "encrypt_value_helper", "get_loopback_oauth_http_client", "get_loopback_oauth_redis"]


def get_loopback_oauth_redis() -> LoopbackOAuthRedis:
    from litellm.proxy.proxy_server import redis_usage_cache

    if redis_usage_cache is None:
        raise HTTPException(status_code=503, detail={"error": "Loopback OAuth is unavailable"})
    return cast(LoopbackOAuthRedis, redis_usage_cache.init_async_client())  # pyright: ignore[reportUnknownMemberType]  # Redis stubs omit async client response types  # cast-ok: installed core object implements the versioned adapter protocol


def get_loopback_oauth_http_client() -> LoopbackOAuthHTTPClient:
    from litellm.llms.custom_httpx.http_handler import (
        get_async_httpx_client,  # pyright: ignore[reportUnknownVariableType]  # core factory has untyped optional arguments
    )
    from litellm.types.llms.custom_http import httpxSpecialProvider

    client: Final = get_async_httpx_client(llm_provider=httpxSpecialProvider.Oauth2Check)
    return cast(LoopbackOAuthHTTPClient, client)  # cast-ok: canonical HTTP client ABI
