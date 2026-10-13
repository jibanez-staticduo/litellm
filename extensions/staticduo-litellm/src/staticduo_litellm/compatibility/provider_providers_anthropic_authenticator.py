from typing import Final

"""LiteLLM dependencies for the versioned provider extension."""

from litellm.llms.anthropic.common_utils import AnthropicError, is_anthropic_oauth_key

__all__: Final = ("AnthropicError", "is_anthropic_oauth_key")
