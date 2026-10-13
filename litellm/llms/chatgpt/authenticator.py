from typing import Final

"""Compatibility facade; implementation lives in staticduo_litellm."""

from staticduo_litellm.providers.chatgpt.authenticator import (
    _AUTH_LOCKS,
    _AUTH_LOCKS_GUARD,
    _JSON_OBJECT_ADAPTER,
    _SAFE_AUTH_PROFILE_PATTERN,
    DEVICE_CODE_COOLDOWN_SECONDS,
    DEVICE_CODE_POLL_SLEEP_SECONDS,
    DEVICE_CODE_TIMEOUT_SECONDS,
    OPENAI_AUTH_CLAIM_KEY,
    TOKEN_EXPIRY_SKEW_SECONDS,
    TOKEN_REFRESH_TIMEOUT_SECONDS,
    Authenticator,
    JsonObject,
    _auth_lock,
    _lock_auth_file,
    _optional_str,
    _token_refresh_timeout,
    fcntl,
    json,
    msvcrt,
    os,
    time,
)

__all__: Final = ('DEVICE_CODE_COOLDOWN_SECONDS', 'DEVICE_CODE_POLL_SLEEP_SECONDS', 'DEVICE_CODE_TIMEOUT_SECONDS', 'OPENAI_AUTH_CLAIM_KEY', 'TOKEN_EXPIRY_SKEW_SECONDS', 'TOKEN_REFRESH_TIMEOUT_SECONDS', '_AUTH_LOCKS', '_AUTH_LOCKS_GUARD', '_JSON_OBJECT_ADAPTER', '_SAFE_AUTH_PROFILE_PATTERN', 'Authenticator', 'JsonObject', '_auth_lock', '_lock_auth_file', '_optional_str', '_token_refresh_timeout', 'fcntl', 'json', 'msvcrt', 'os', 'time')
