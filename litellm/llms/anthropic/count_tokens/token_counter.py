"""
Anthropic Token Counter implementation using the CountTokens API.
"""

import os
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Final

from pydantic import JsonValue, TypeAdapter

from litellm._logging import verbose_logger
from litellm.llms.anthropic import oauth_policy
from litellm.llms.anthropic.count_tokens.handler import AnthropicCountTokensHandler
from litellm.llms.anthropic.count_tokens.transformation import COUNT_TOKEN_OPTION_NAMES
from litellm.llms.base_llm.base_utils import BaseTokenCounter
from litellm.types.utils import LlmProviders, TokenCountResponse

# Global handler instance - reuse across all token counting requests
anthropic_count_tokens_handler: Final = AnthropicCountTokensHandler()
_COUNT_PARAMS: Final = TypeAdapter(Mapping[str, object])
_COUNT_MESSAGES: Final = TypeAdapter(list[dict[str, JsonValue]])
_COUNT_STRING: Final[TypeAdapter[str | None]] = TypeAdapter(str | None)
_COUNT_TOTAL: Final = TypeAdapter(int)
_COUNT_OPTIONS: Final = TypeAdapter(Mapping[str, JsonValue])
_EMPTY_COUNT_PARAMS: Final[Mapping[str, object]] = MappingProxyType({})


class AnthropicTokenCounter(BaseTokenCounter):
    """Token counter implementation for Anthropic provider using the CountTokens API."""

    def should_use_token_counting_api(
        self,
        custom_llm_provider: str | None = None,
    ) -> bool:
        return custom_llm_provider == LlmProviders.ANTHROPIC.value

    async def count_tokens(
        self,
        model_to_use: str,
        messages: Sequence[Mapping[str, JsonValue]] | None,
        contents: Sequence[Mapping[str, JsonValue]] | None,
        deployment: Mapping[str, object] | None = None,
        request_model: str = "",
        tools: Sequence[Mapping[str, JsonValue]] | None = None,
        system: object = None,
    ) -> TokenCountResponse | None:
        """
        Count tokens using Anthropic's CountTokens API.

        Args:
            model_to_use: The model identifier
            messages: The messages to count tokens for
            contents: Alternative content format (not used for Anthropic)
            deployment: Deployment configuration containing litellm_params
            request_model: The original request model name

        Returns:
            TokenCountResponse with token count, or None if counting fails
        """
        from litellm.llms.anthropic.common_utils import AnthropicError

        litellm_params: Final = _COUNT_PARAMS.validate_python(
            deployment.get("litellm_params", _EMPTY_COUNT_PARAMS) if deployment else _EMPTY_COUNT_PARAMS
        )
        managed: Final = oauth_policy.is_anthropic_oauth_managed(litellm_params)
        if not messages and not managed:
            return None
        if managed and messages is None:
            return TokenCountResponse(
                total_tokens=0,
                request_model=request_model,
                model_used=model_to_use,
                tokenizer_type="anthropic_api",
                error=True,
                error_message="Managed Anthropic token counting requires messages",
                status_code=400,
            )

        try:
            from litellm.llms.anthropic.native_transport import is_anthropic_native_sdk

            native: Final = is_anthropic_native_sdk(litellm_params)
            api_base: Final = (
                _COUNT_STRING.validate_python(litellm_params.get("api_base"), strict=True) if managed else None
            )
            managed_token: Final = (
                None if native else oauth_policy.resolve_anthropic_oauth_access_token(litellm_params, api_base=api_base)
            )
            api_key: Final = (
                ""
                if native
                else managed_token
                if managed
                else _COUNT_STRING.validate_python(litellm_params.get("api_key"), strict=True)
                or os.getenv("ANTHROPIC_API_KEY")
            )
            if not api_key and not native:
                if managed:
                    raise AnthropicError(401, "No managed Anthropic OAuth credential available for token counting")
                verbose_logger.warning("No Anthropic API key found for token counting")
                return None
            optional_params: Final = _COUNT_OPTIONS.validate_python(
                MappingProxyType(
                    {key: value for key, value in litellm_params.items() if key in COUNT_TOKEN_OPTION_NAMES}
                )
            )
            result: Final = await anthropic_count_tokens_handler.handle_count_tokens_request(
                model=model_to_use,
                messages=_COUNT_MESSAGES.validate_python(messages),
                api_key=api_key or "",
                tools=_COUNT_MESSAGES.validate_python(tools) if tools is not None else None,
                system=oauth_policy.apply_anthropic_oauth_system(system, litellm_params),
                optional_params=optional_params,
                native_params=litellm_params if native else None,
            )
            return TokenCountResponse(
                total_tokens=_COUNT_TOTAL.validate_python(result.get("input_tokens", 0), strict=True),
                request_model=request_model,
                model_used=model_to_use,
                tokenizer_type="anthropic_api",
                original_response=result,
            )
        except AnthropicError as e:
            verbose_logger.warning("Anthropic CountTokens API error: status=%s, message=%s", e.status_code, e.message)
            return TokenCountResponse(
                total_tokens=0,
                request_model=request_model,
                model_used=model_to_use,
                tokenizer_type="anthropic_api",
                error=True,
                error_message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            verbose_logger.warning("Error calling Anthropic CountTokens API: %s", e)
            return TokenCountResponse(
                total_tokens=0,
                request_model=request_model,
                model_used=model_to_use,
                tokenizer_type="anthropic_api",
                error=True,
                error_message=str(e),
                status_code=500,
            )
