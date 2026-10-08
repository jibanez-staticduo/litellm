"""
Anthropic CountTokens API handler.

Uses httpx for HTTP requests instead of the Anthropic SDK.
"""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

import httpx
from pydantic import JsonValue, TypeAdapter

import litellm
from litellm._logging import verbose_logger
from litellm.litellm_core_utils.asyncify import asyncify
from litellm.llms.anthropic.common_utils import AnthropicError, AnthropicModelInfo
from litellm.llms.anthropic.count_tokens.transformation import (
    AnthropicCountTokensConfig,
)
from litellm.llms.custom_httpx.http_handler import AsyncHTTPHandler, get_async_httpx_client

_COUNT_RESPONSE: Final = TypeAdapter(dict[str, JsonValue])
_COUNT_HEADERS: Final = TypeAdapter(dict[str, str])


class AnthropicCountTokensHandler(AnthropicCountTokensConfig):
    """
    Handler for Anthropic CountTokens API requests.

    Uses httpx for HTTP requests, following the same pattern as BedrockCountTokensHandler.
    """

    def __init__(self, http_client: AsyncHTTPHandler | None = None) -> None:
        self._http_client = http_client

    async def handle_count_tokens_request(
        self,
        model: str,
        messages: list[dict[str, JsonValue]],
        auth_header: Mapping[str, str] | None = None,
        api_base: str | None = None,
        timeout: float | httpx.Timeout | None = None,
        tools: list[dict[str, JsonValue]] | None = None,
        system: JsonValue = None,
        optional_params: Mapping[str, JsonValue] | None = None,
        extra_headers: Mapping[str, str] | None = None,
        native_params: Mapping[str, object] | None = None,
        native_client: bool = False,
        api_key: str | None = None,
    ) -> dict[str, JsonValue]:
        """
        Handle a CountTokens request using httpx.

        Args:
            model: The model identifier (e.g., "claude-3-5-sonnet-20241022")
            messages: The messages to count tokens for
            auth_header: The resolved Anthropic auth header (``AnthropicModelInfo.get_auth_header``)
            api_base: Optional deployment api_base the count-tokens path is appended to
            timeout: Optional timeout for the request (defaults to litellm.request_timeout)

        Returns:
            Dictionary containing token count response

        Raises:
            AnthropicError: If the API request fails
        """
        try:
            # Validate the request
            self.validate_request(model, messages, system=system, tools=tools)

            verbose_logger.debug("Processing Anthropic CountTokens request for model: %s", model)

            # Transform request to Anthropic format
            request_body: Final = (
                _COUNT_RESPONSE.validate_python(
                    MappingProxyType(
                        {**(optional_params or MappingProxyType({})), "model": model, "messages": messages}
                    )
                )
                if native_client
                else await asyncify(self.transform_request_to_count_tokens)(
                    model=model,
                    messages=messages,
                    tools=tools,
                    system=system,
                    optional_params=optional_params,
                )
            )

            verbose_logger.debug("Transformed request: %s", request_body)

            # Get endpoint URL
            from litellm.llms.anthropic.native_transport import native_sdk_connection

            native_connection: Final = native_sdk_connection(native_params) if native_params is not None else None
            endpoint_url: Final = (
                native_connection.url("count_tokens")
                if native_connection is not None
                else self.get_anthropic_count_tokens_endpoint(api_base)
            )

            verbose_logger.debug("Making request to: %s", endpoint_url)

            # Get required headers
            resolved_auth_header: Final = (
                auth_header if auth_header is not None else AnthropicModelInfo.get_auth_header(api_key)
            )
            if resolved_auth_header is None and native_connection is None:
                raise AnthropicError(401, "No Anthropic credential available for token counting")
            required_headers: Final = (
                native_connection.headers
                if native_connection is not None
                else self.get_count_tokens_headers(resolved_auth_header or MappingProxyType({}))
            )
            client_beta: Final = next(
                (
                    value
                    for name, value in (extra_headers or MappingProxyType({})).items()
                    if name.lower() == "anthropic-beta"
                ),
                "",
            )
            headers: Final = _COUNT_HEADERS.validate_python(
                MappingProxyType(
                    required_headers
                    if native_connection is not None
                    else MappingProxyType(
                        {
                            **required_headers,
                            "anthropic-beta": f"{required_headers['anthropic-beta']},{client_beta}"
                            if client_beta
                            else required_headers["anthropic-beta"],
                        }
                    )
                )
            )
            from litellm.llms.anthropic.oauth_policy import native_client_auth_headers

            request_headers: Final = (
                native_client_auth_headers(
                    extra_headers or MappingProxyType[str, str]({}),
                    (resolved_auth_header or MappingProxyType({})).get("authorization", "").removeprefix("Bearer "),
                )
                if native_client
                else headers
            )

            # Use LiteLLM's async httpx client
            async_client: Final = self._http_client or get_async_httpx_client(
                llm_provider=litellm.LlmProviders.ANTHROPIC
            )

            # Use provided timeout or fall back to litellm.request_timeout
            request_timeout: Final = timeout if timeout is not None else litellm.request_timeout

            response: Final = await async_client.post(
                endpoint_url,
                headers=request_headers,
                json=request_body,
                timeout=request_timeout,
            )

            verbose_logger.debug("Response status: %s", response.status_code)

            if response.status_code != 200:
                error_text: Final = response.text
                verbose_logger.error("Anthropic API error: %s", error_text)
                raise AnthropicError(
                    status_code=response.status_code,
                    message=error_text,
                )

            anthropic_response: Final = _COUNT_RESPONSE.validate_json(response.content)

            verbose_logger.debug("Anthropic response: %s", anthropic_response)

            # Return Anthropic response directly - no transformation needed
            return anthropic_response

        except AnthropicError:
            # Re-raise Anthropic exceptions as-is
            raise
        except httpx.HTTPStatusError as e:
            # HTTP errors - preserve the actual status code
            verbose_logger.error("HTTP error in CountTokens handler: %s", e)
            raise AnthropicError(
                status_code=e.response.status_code,
                message=e.response.text,
            )
        except Exception as e:
            verbose_logger.error("Error in CountTokens handler: %s", e)
            raise AnthropicError(
                status_code=500,
                message=f"CountTokens processing error: {e}",
            )
