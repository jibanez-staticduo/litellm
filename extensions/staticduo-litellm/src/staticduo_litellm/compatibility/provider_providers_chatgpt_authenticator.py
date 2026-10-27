"""LiteLLM dependencies for the versioned provider extension."""

from typing import Final

from litellm.llms.chatgpt import oauth_engine

JSON_OBJECT_ADAPTER: Final = oauth_engine._JSON_OBJECT_ADAPTER  # pyright: ignore[reportPrivateUsage]  # compatibility owns the upstream adapter
optional_str: Final = oauth_engine._optional_str  # pyright: ignore[reportPrivateUsage]  # compatibility owns the upstream helper
token_refresh_timeout: Final = oauth_engine._token_refresh_timeout  # pyright: ignore[reportPrivateUsage]  # compatibility owns the upstream helper

from litellm._logging import verbose_logger
from litellm.constants import HTTP_HANDLER_CONNECT_TIMEOUT_SECONDS
from litellm.litellm_core_utils.asyncify import can_block_current_thread
from litellm.litellm_core_utils.request_timeout_resolver import (
    get_configured_request_timeout,
)
from litellm.llms.chatgpt.common_utils import (
    CHATGPT_API_BASE,
    CHATGPT_AUTH_BASE,
    CHATGPT_CLIENT_ID,
    CHATGPT_DEVICE_CODE_URL,
    CHATGPT_DEVICE_TOKEN_URL,
    CHATGPT_DEVICE_VERIFY_URL,
    CHATGPT_OAUTH_TOKEN_URL,
    GetAccessTokenError,
    GetDeviceCodeError,
    InteractiveAuthError,
    RefreshAccessTokenError,
    decode_jwt_claims,
    extract_chatgpt_account_id,
)
from litellm.llms.chatgpt.oauth_engine import (
    DEVICE_CODE_COOLDOWN_SECONDS,
    DEVICE_CODE_POLL_SLEEP_SECONDS,
    DEVICE_CODE_TIMEOUT_SECONDS,
    OPENAI_AUTH_CLAIM_KEY,
    TOKEN_EXPIRY_SKEW_SECONDS,
    TOKEN_REFRESH_TIMEOUT_SECONDS,
    ChatGPTOAuthEngine,
    JsonObject,
)
from litellm.llms.custom_httpx.http_handler import HTTPHandler
from litellm.llms.custom_httpx.http_handler import (
    get_httpx_client as _upstream_httpx_client,  # pyright: ignore[reportUnknownVariableType]  # upstream handler signature is legacy
)


def get_httpx_client() -> HTTPHandler:
    return _upstream_httpx_client()


__all__: Final = (
    "CHATGPT_API_BASE",
    "CHATGPT_AUTH_BASE",
    "CHATGPT_CLIENT_ID",
    "CHATGPT_DEVICE_CODE_URL",
    "CHATGPT_DEVICE_TOKEN_URL",
    "CHATGPT_DEVICE_VERIFY_URL",
    "CHATGPT_OAUTH_TOKEN_URL",
    "DEVICE_CODE_COOLDOWN_SECONDS",
    "DEVICE_CODE_POLL_SLEEP_SECONDS",
    "DEVICE_CODE_TIMEOUT_SECONDS",
    "HTTP_HANDLER_CONNECT_TIMEOUT_SECONDS",
    "OPENAI_AUTH_CLAIM_KEY",
    "TOKEN_EXPIRY_SKEW_SECONDS",
    "TOKEN_REFRESH_TIMEOUT_SECONDS",
    "ChatGPTOAuthEngine",
    "GetAccessTokenError",
    "GetDeviceCodeError",
    "HTTPHandler",
    "InteractiveAuthError",
    "JsonObject",
    "RefreshAccessTokenError",
    "can_block_current_thread",
    "decode_jwt_claims",
    "extract_chatgpt_account_id",
    "get_configured_request_timeout",
    "verbose_logger",
)
