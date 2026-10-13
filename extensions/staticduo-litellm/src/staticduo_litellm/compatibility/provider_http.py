"""Typed delegation to LiteLLM HTTP transports and OAuth environment validation."""

from collections.abc import Mapping
from typing import Final

import httpx
from pydantic import JsonValue, TypeAdapter

from litellm.llms.chatgpt.responses.transformation import ChatGPTResponsesAPIConfig
from litellm.llms.custom_httpx.http_handler import AsyncHTTPHandler
from litellm.llms.custom_httpx.http_handler import (
    get_async_httpx_client as _client,  # pyright: ignore[reportUnknownVariableType]  # upstream legacy optional params
)
from litellm.types.router import GenericLiteLLMParams
from litellm.types.utils import LlmProviders


def get_async_httpx_client(llm_provider: LlmProviders, params: Mapping[str, object] | None = None) -> AsyncHTTPHandler:
    return _client(llm_provider=llm_provider, params=dict(params) if params is not None else None)


def oauth_headers(params: GenericLiteLLMParams, model: str) -> Mapping[str, str]:
    result: Final = ChatGPTResponsesAPIConfig().validate_environment(  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]  # upstream headers have a legacy bare dict annotation
        headers={},
        model=model,
        litellm_params=params,
    )
    return TypeAdapter(Mapping[str, str]).validate_python(result)


async def live_get(handler: AsyncHTTPHandler, url: str, headers: Mapping[str, str]) -> httpx.Response:
    return await handler.get(url, headers=dict(headers), timeout=60, follow_redirects=False)  # pyright: ignore[reportUnknownMemberType]  # core transport optional params are legacy


async def live_post(
    handler: AsyncHTTPHandler, url: str, headers: Mapping[str, str], body: Mapping[str, JsonValue] | None
) -> httpx.Response:
    return await handler.post(url, headers=dict(headers), json=dict(body) if body is not None else None, timeout=60)  # pyright: ignore[reportUnknownMemberType]  # core transport optional params are legacy


async def hangup_post(handler: AsyncHTTPHandler, url: str, headers: Mapping[str, str]) -> httpx.Response:
    return await handler.post(url, headers=dict(headers), data=b"", timeout=10)  # pyright: ignore[reportUnknownMemberType]  # core transport optional params are legacy
