from typing import Final

"""Compatibility facade; implementation lives in staticduo_litellm."""

from staticduo_litellm.providers.anthropic.oauth_policy import (
    _HEADERS,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _OAUTH_FIELDS,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _OVERRIDES,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _SYSTEM,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _SYSTEM_BLOCK,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _SYSTEM_BLOCKS,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    ANTHROPIC_OAUTH_BILLING_HEADER,
    ANTHROPIC_OAUTH_COMPATIBILITY_VERSION,
    ANTHROPIC_OAUTH_USER_AGENT,
    _is_billing_block,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _validate_native_overrides,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _validate_oauth_headers,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _validate_oauth_setting,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    anthropic_oauth_config,
    apply_anthropic_oauth_system,
    is_anthropic_native_client,
    is_anthropic_oauth_managed,
    native_client_auth_headers,
    native_client_metadata,
    native_client_request_body,
    normalize_anthropic_oauth_headers,
    resolve_anthropic_oauth_access_token,
    validate_anthropic_oauth_destination,
    validate_anthropic_oauth_request_overrides,
)

__all__: Final = (
    "ANTHROPIC_OAUTH_BILLING_HEADER",
    "ANTHROPIC_OAUTH_COMPATIBILITY_VERSION",
    "ANTHROPIC_OAUTH_USER_AGENT",
    "_HEADERS",
    "_OAUTH_FIELDS",
    "_OVERRIDES",
    "_SYSTEM",
    "_SYSTEM_BLOCK",
    "_SYSTEM_BLOCKS",
    "_is_billing_block",
    "_validate_native_overrides",
    "_validate_oauth_headers",
    "_validate_oauth_setting",
    "anthropic_oauth_config",
    "apply_anthropic_oauth_system",
    "is_anthropic_native_client",
    "is_anthropic_oauth_managed",
    "native_client_auth_headers",
    "native_client_metadata",
    "native_client_request_body",
    "normalize_anthropic_oauth_headers",
    "resolve_anthropic_oauth_access_token",
    "validate_anthropic_oauth_destination",
    "validate_anthropic_oauth_request_overrides",
)
