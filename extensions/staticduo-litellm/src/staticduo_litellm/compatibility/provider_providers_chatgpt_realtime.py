from typing import Final

"""LiteLLM dependencies for the versioned provider extension."""

from litellm.constants import REALTIME_WEBSOCKET_MAX_MESSAGE_SIZE_BYTES
from litellm.exceptions import AuthenticationError
from litellm.llms.chatgpt.common_utils import without_oauth_identity_headers
from litellm.llms.chatgpt.responses.transformation import ChatGPTResponsesAPIConfig
from litellm.llms.openai.realtime.handler import OpenAIRealtime
from litellm.llms.openai.realtime.http_transformation import OpenAIRealtimeHTTPConfig
from litellm.types.realtime import RealtimeQueryParams
from litellm.types.router import GenericLiteLLMParams
from litellm.types.utils import LlmProviders
from litellm.utils import get_model_info
from staticduo_litellm.compatibility.provider_http import get_async_httpx_client

__all__: Final = (
    "REALTIME_WEBSOCKET_MAX_MESSAGE_SIZE_BYTES",
    "AuthenticationError",
    "ChatGPTResponsesAPIConfig",
    "GenericLiteLLMParams",
    "LlmProviders",
    "OpenAIRealtime",
    "OpenAIRealtimeHTTPConfig",
    "RealtimeQueryParams",
    "get_async_httpx_client",
    "get_model_info",
    "without_oauth_identity_headers",
)
