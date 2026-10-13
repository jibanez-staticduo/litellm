from typing import Final

"""Compatibility facade; implementation lives in staticduo_litellm."""

from staticduo_litellm.providers.anthropic.native_transport import (
    _HEADER_IDENTITY,
    _NATIVE_HEADERS,
    _NATIVE_TOOL_CALLER,
    _NATIVE_TOOL_ID_PREFIX,
    _NATIVE_TOOL_REPLAY,
    NATIVE_IDENTITY_FIELD,
    NATIVE_SDK_MAPPING,
    AnthropicNativeConnection,
    AnthropicNativeIdentity,
    AnthropicNativeToolReplay,
    decode_native_tool_call_id,
    encode_native_tool_call_id,
    is_anthropic_native_sdk,
    native_sdk_connection,
)

__all__: Final = ('NATIVE_IDENTITY_FIELD', 'NATIVE_SDK_MAPPING', '_HEADER_IDENTITY', '_NATIVE_HEADERS', '_NATIVE_TOOL_CALLER', '_NATIVE_TOOL_ID_PREFIX', '_NATIVE_TOOL_REPLAY', 'AnthropicNativeConnection', 'AnthropicNativeIdentity', 'AnthropicNativeToolReplay', 'decode_native_tool_call_id', 'encode_native_tool_call_id', 'is_anthropic_native_sdk', 'native_sdk_connection')
