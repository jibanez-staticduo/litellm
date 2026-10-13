from typing import Final

"""Public entry point with ordered initialization of the LiteLLM runtime."""

from importlib import import_module

# Core facades load the implementation directly while LiteLLM initializes.
import_module("litellm")
from staticduo_litellm.providers.anthropic._authenticator import (
    ANTHROPIC_OAUTH_CLIENT_ID,
    ANTHROPIC_OAUTH_TOKEN_URL,
    TOKEN_EXPIRY_SKEW_SECONDS,
    AnthropicAuthenticator,
    AnthropicAuthError,
    AnthropicOAuthConfig,
)

__all__: Final = (
    "ANTHROPIC_OAUTH_CLIENT_ID",
    "ANTHROPIC_OAUTH_TOKEN_URL",
    "TOKEN_EXPIRY_SKEW_SECONDS",
    "AnthropicAuthError",
    "AnthropicAuthenticator",
    "AnthropicOAuthConfig",
)
