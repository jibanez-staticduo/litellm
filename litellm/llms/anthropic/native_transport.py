import base64
import binascii
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Final, Literal
from urllib.parse import urlsplit

from pydantic import JsonValue, TypeAdapter

from .common_utils import AnthropicError

NATIVE_IDENTITY_FIELD: Final = "_anthropic_native_identity"
NATIVE_SDK_MAPPING: Final = TypeAdapter(Mapping[str, object])
_HEADER_IDENTITY: Final = re.compile(r"^[a-zA-Z0-9_.:-]{1,256}$")
_NATIVE_HEADERS: Final = TypeAdapter(dict[str, str])
_NATIVE_TOOL_ID_PREFIX: Final = "litellm_native_tool_"
_NATIVE_TOOL_CALLER: Final = TypeAdapter(Mapping[str, JsonValue])


@dataclass(frozen=True, slots=True)
class AnthropicNativeToolReplay:
    identifier: str
    caller: Mapping[str, JsonValue]


_NATIVE_TOOL_REPLAY: Final = TypeAdapter(AnthropicNativeToolReplay)


def encode_native_tool_call_id(tool_call: Mapping[str, object]) -> str | None:
    identifier: Final = tool_call.get("id")
    caller: Final = tool_call.get("caller")
    if identifier is not None and not isinstance(identifier, str):
        raise AnthropicError(400, "Invalid native SDK tool replay identifier")
    if identifier is None or caller is None:
        return identifier
    parsed_caller: Final = _NATIVE_TOOL_CALLER.validate_python(caller)
    payload: Final = AnthropicNativeToolReplay(identifier, parsed_caller)
    encoded: Final = base64.urlsafe_b64encode(_NATIVE_TOOL_REPLAY.dump_json(payload)).decode().rstrip("=")
    return f"{_NATIVE_TOOL_ID_PREFIX}{encoded}"


def decode_native_tool_call_id(identifier: str) -> AnthropicNativeToolReplay | None:
    if not identifier.startswith(_NATIVE_TOOL_ID_PREFIX):
        return None
    encoded: Final = identifier.removeprefix(_NATIVE_TOOL_ID_PREFIX)
    try:
        payload: Final = _NATIVE_TOOL_REPLAY.validate_json(
            base64.b64decode(encoded + "=" * (-len(encoded) % 4), altchars=b"-_", validate=True)
        )
    except (binascii.Error, ValueError) as exc:
        raise AnthropicError(400, "Invalid native SDK tool replay identifier") from exc
    return payload


class AnthropicNativeIdentity:
    __slots__ = ("_deployment", "_owner")

    def __init__(self, owner: str, deployment: str | None = None) -> None:
        if not _HEADER_IDENTITY.fullmatch(owner) or (
            deployment is not None and not _HEADER_IDENTITY.fullmatch(deployment)
        ):
            raise AnthropicError(400, "Invalid native SDK server identity")
        object.__setattr__(self, "_owner", owner)
        object.__setattr__(self, "_deployment", deployment)

    _owner: str
    _deployment: str | None

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Native SDK server identities are immutable")

    def __copy__(self) -> "AnthropicNativeIdentity":
        return self

    def __deepcopy__(self, memo: Mapping[int, object]) -> "AnthropicNativeIdentity":
        return self

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def deployment(self) -> str | None:
        return self._deployment


@dataclass(frozen=True, slots=True)
class AnthropicNativeConnection:
    api_base: str
    headers: Mapping[str, str] = field(repr=False)

    def request_headers(self) -> dict[str, str]:  # mutable-ok: provider HTTP adapters require writable headers
        return _NATIVE_HEADERS.validate_python(self.headers)

    def url(self, endpoint: Literal["messages", "count_tokens"] = "messages") -> str:
        return f"{self.api_base}/v1/messages" + ("/count_tokens" if endpoint == "count_tokens" else "")


def is_anthropic_native_sdk(params: Mapping[str, object]) -> bool:
    mode: Final = params.get("anthropic_execution_mode")
    if mode is None:
        return False
    if mode != "native_sdk":
        raise AnthropicError(400, "Unsupported Anthropic execution mode")
    profile: Final = params.get("anthropic_auth_profile")
    if (
        params.get("use_anthropic_oauth") is not True
        or not isinstance(profile, str)
        or not _HEADER_IDENTITY.fullmatch(profile)
        or params.get("custom_llm_provider") not in (None, "anthropic")
    ):
        raise AnthropicError(400, "The native SDK requires a managed Anthropic deployment with a fixed profile")
    return True


def native_sdk_connection(
    params: Mapping[str, object], *, environment: Mapping[str, str] | None = None
) -> AnthropicNativeConnection:
    if not is_anthropic_native_sdk(params):
        raise AnthropicError(400, "The deployment does not select the native SDK")
    identity: Final = params.get(NATIVE_IDENTITY_FIELD)
    if not isinstance(identity, AnthropicNativeIdentity) or identity.deployment is None:
        raise AnthropicError(401, "The native SDK requires an authenticated server owner and selected deployment")
    configured: Final = environment if environment is not None else os.environ
    base: Final = configured.get("ANTHROPIC_NATIVE_SDK_BASE_URL", "").rstrip("/")
    key: Final = configured.get("ANTHROPIC_NATIVE_SDK_KEY", "")
    parsed: Final = urlsplit(base)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.hostname.lower() == "api.anthropic.com"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
        or not key
        or not all(33 <= ord(character) <= 126 for character in key)
    ):
        raise AnthropicError(400, "Invalid or missing native SDK broker environment configuration")
    return AnthropicNativeConnection(
        api_base=base,
        headers=MappingProxyType(
            {
                "authorization": f"Bearer {key}",
                "content-type": "application/json",
                "anthropic-version": "2023-06-01",
                "x-litellm-native-profile": str(params["anthropic_auth_profile"]),
                "x-litellm-native-owner": identity.owner,
                "x-litellm-native-deployment": identity.deployment,
            }
        ),
    )
