from typing import Final

"""LiteLLM dependencies for the versioned provider extension."""

from litellm.constants import REALTIME_WEBSOCKET_MAX_MESSAGE_SIZE_BYTES
from litellm.llms.custom_httpx.http_handler import AsyncHTTPHandler, get_shared_realtime_ssl_context
from litellm.types.router import GenericLiteLLMParams
from litellm.types.utils import LlmProviders
from staticduo_litellm.compatibility.provider_http import get_async_httpx_client

__all__: Final = (
    "REALTIME_WEBSOCKET_MAX_MESSAGE_SIZE_BYTES",
    "AsyncHTTPHandler",
    "GenericLiteLLMParams",
    "LlmProviders",
    "get_async_httpx_client",
    "get_shared_realtime_ssl_context",
)
