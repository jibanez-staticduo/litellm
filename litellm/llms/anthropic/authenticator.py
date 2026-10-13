from typing import Final

"""Compatibility facade; implementation lives in staticduo_litellm."""

from staticduo_litellm.providers.anthropic._authenticator import (
    _PROFILE_PATTERN,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    ANTHROPIC_OAUTH_CLIENT_ID,
    ANTHROPIC_OAUTH_TOKEN_URL,
    TOKEN_EXPIRY_SKEW_SECONDS,
    AnthropicAuthenticator,
    AnthropicAuthError,
    AnthropicOAuthConfig,
    _AuthFailure,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _Credential,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _NativeAccount,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _NativeCredential,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _NativeImport,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _NativeSettings,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _PersistedCredential,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _PositiveSeconds,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _raise_public,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _read_credential,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _RefreshRequest,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _RefreshResponse,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _ScopeList,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _scopes,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _Token,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _validate_credential,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _write_credential,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
)

__all__: Final = (
    "ANTHROPIC_OAUTH_CLIENT_ID",
    "ANTHROPIC_OAUTH_TOKEN_URL",
    "TOKEN_EXPIRY_SKEW_SECONDS",
    "_PROFILE_PATTERN",
    "AnthropicAuthError",
    "AnthropicAuthenticator",
    "AnthropicOAuthConfig",
    "_AuthFailure",
    "_Credential",
    "_NativeAccount",
    "_NativeCredential",
    "_NativeImport",
    "_NativeSettings",
    "_PersistedCredential",
    "_PositiveSeconds",
    "_RefreshRequest",
    "_RefreshResponse",
    "_ScopeList",
    "_Token",
    "_raise_public",
    "_read_credential",
    "_scopes",
    "_validate_credential",
    "_write_credential",
)
