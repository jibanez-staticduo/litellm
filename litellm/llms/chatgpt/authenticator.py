from typing import Final

"""Compatibility facade; implementation lives in staticduo_litellm."""

from staticduo_litellm.providers.chatgpt.authenticator import (
    _AUTH_LOCKS,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _AUTH_LOCKS_GUARD,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _JSON_OBJECT_ADAPTER,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _SAFE_AUTH_PROFILE_PATTERN,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    DEVICE_CODE_COOLDOWN_SECONDS,
    DEVICE_CODE_POLL_SLEEP_SECONDS,
    DEVICE_CODE_TIMEOUT_SECONDS,
    OPENAI_AUTH_CLAIM_KEY,
    TOKEN_EXPIRY_SKEW_SECONDS,
    TOKEN_REFRESH_TIMEOUT_SECONDS,
    Authenticator,
    JsonObject,
    _auth_lock,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _lock_auth_file,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _optional_str,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    _token_refresh_timeout,  # pyright: ignore[reportPrivateUsage]  # preserve the established private import ABI at this facade
    fcntl,
    get_cached_authenticator,
    get_chatgpt_auth_file,
    json,
    msvcrt,
    os,
    time,
)

__all__: Final = (
    "DEVICE_CODE_COOLDOWN_SECONDS",
    "DEVICE_CODE_POLL_SLEEP_SECONDS",
    "DEVICE_CODE_TIMEOUT_SECONDS",
    "OPENAI_AUTH_CLAIM_KEY",
    "TOKEN_EXPIRY_SKEW_SECONDS",
    "TOKEN_REFRESH_TIMEOUT_SECONDS",
    "_AUTH_LOCKS",
    "_AUTH_LOCKS_GUARD",
    "_JSON_OBJECT_ADAPTER",
    "_SAFE_AUTH_PROFILE_PATTERN",
    "Authenticator",
    "JsonObject",
    "_auth_lock",
    "_lock_auth_file",
    "_optional_str",
    "_token_refresh_timeout",
    "fcntl",
    "get_cached_authenticator",
    "get_chatgpt_auth_file",
    "json",
    "msvcrt",
    "os",
    "time",
)
