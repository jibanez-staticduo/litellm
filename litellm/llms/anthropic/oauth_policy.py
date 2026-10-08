from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Final
from urllib.parse import urlsplit

from pydantic import JsonValue, TypeAdapter, ValidationError

from .authenticator import AnthropicAuthenticator, AnthropicOAuthConfig
from .common_utils import AnthropicError

ANTHROPIC_OAUTH_COMPATIBILITY_VERSION: Final = "2.1.286"
ANTHROPIC_OAUTH_BILLING_HEADER: Final = (
    f"x-anthropic-billing-header: cc_version={ANTHROPIC_OAUTH_COMPATIBILITY_VERSION}; cc_entrypoint=cli; cch=00000;"
)
ANTHROPIC_OAUTH_USER_AGENT: Final = "litellm-anthropic-subscription/1.0"
_SYSTEM: Final[TypeAdapter[JsonValue]] = TypeAdapter(JsonValue)
_SYSTEM_BLOCK: Final = TypeAdapter(dict[str, JsonValue])
_SYSTEM_BLOCKS: Final = TypeAdapter(list[JsonValue])
_OVERRIDES: Final = TypeAdapter(dict[str, object])
_HEADERS: Final = TypeAdapter(dict[str, str])
_OAUTH_FIELDS: Final = (
    "use_anthropic_oauth",
    "anthropic_auth_profile",
    "anthropic_token_dir",
    "anthropic_oauth_compatibility",
    "anthropic_execution_mode",
    "anthropic_credential_mode",
)


def is_anthropic_oauth_managed(params: Mapping[str, object]) -> bool:
    return params.get("use_anthropic_oauth") is True


def is_anthropic_native_client(params: Mapping[str, object]) -> bool:
    if params.get("anthropic_execution_mode") != "native_client":
        return False
    if not is_anthropic_oauth_managed(params) or params.get("custom_llm_provider") not in (None, "anthropic"):
        raise AnthropicError(400, "The native client requires a managed Anthropic deployment")
    return True


def native_client_auth_headers(headers: object, token: str) -> dict[str, str]:
    validated: Final = _HEADERS.validate_python(headers)
    return _HEADERS.validate_python(
        MappingProxyType(
            {
                **MappingProxyType(
                    {
                        name: value
                        for name, value in validated.items()
                        if name.lower()
                        not in ("authorization", "x-api-key", "api-key", "x-litellm-api-key", "host", "content-length")
                    }
                ),
                "authorization": f"Bearer {token}",
            }
        )
    )


def native_client_metadata(metadata: object, params: Mapping[str, object]) -> JsonValue:
    original: Final = _SYSTEM.validate_python(metadata)
    if not isinstance(original, dict) or not isinstance(user_id := original.get("user_id"), str):
        return original
    try:
        identity: Final = _SYSTEM.validate_json(user_id)
    except ValidationError:
        return original
    if not isinstance(identity, dict) or "account_uuid" not in identity:
        return original
    config: Final = anthropic_oauth_config(params)
    if config is None:
        raise AnthropicError(400, "Native client account identity requires a managed profile")
    account_uuid: Final = AnthropicAuthenticator(config).get_account_uuid()
    aligned: Final = _SYSTEM_BLOCK.validate_python(MappingProxyType({**identity, "account_uuid": account_uuid}))
    return _SYSTEM_BLOCK.validate_python(MappingProxyType({**original, "user_id": _SYSTEM.dump_json(aligned).decode()}))


def native_client_request_body(body: object, params: Mapping[str, object], model: str) -> dict[str, JsonValue]:
    original: Final = _SYSTEM_BLOCK.validate_python(body)
    metadata: Final = original.get("metadata")
    return _SYSTEM_BLOCK.validate_python(
        MappingProxyType(
            {
                **original,
                **(
                    MappingProxyType({"metadata": native_client_metadata(metadata, params)})
                    if metadata is not None
                    else MappingProxyType({})
                ),
                "model": model,
            }
        )
    )


def normalize_anthropic_oauth_headers(
    headers: object, managed: bool
) -> dict[str, str]:  # mutable-ok: HTTP provider adapters require header dictionaries
    validated: Final = _HEADERS.validate_python(headers)
    if not managed:
        return validated
    return _HEADERS.validate_python(
        MappingProxyType(
            {
                **MappingProxyType({name: value for name, value in validated.items() if name.lower() != "user-agent"}),
                "user-agent": ANTHROPIC_OAUTH_USER_AGENT,
            }
        )
    )


def validate_anthropic_oauth_destination(api_base: str | None) -> str:
    destination: Final = api_base or "https://api.anthropic.com"
    parsed: Final = urlsplit(destination)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "api.anthropic.com"
        or parsed.path not in ("", "/", "/v1/messages", "/v1/messages/count_tokens")
        or parsed.query
        or parsed.fragment
    ):
        raise AnthropicError(400, "Central Anthropic OAuth requires the official HTTPS Anthropic endpoint")
    return destination


def validate_anthropic_oauth_request_overrides(
    request_params: Mapping[str, object], deployment_params: Mapping[str, object]
) -> None:
    nested: Final = request_params.get("extra_body")
    carriers: Final = (
        (request_params, _OVERRIDES.validate_python(nested)) if isinstance(nested, Mapping) else (request_params,)
    )
    managed: Final = is_anthropic_oauth_managed(deployment_params)
    from .native_transport import is_anthropic_native_sdk

    native: Final = is_anthropic_native_sdk(deployment_params)
    for carrier in carriers:
        for name in _OAUTH_FIELDS:
            _validate_oauth_setting(name, carrier, deployment_params, managed)
        if not managed:
            continue
        if native:
            _validate_native_overrides(carrier)
        if any(
            carrier.get(name) is not None for name in ("api_key", "auth_token", "litellm_credential_name", "client")
        ):
            raise AnthropicError(400, "Client credentials cannot override central Anthropic OAuth")
        for name in ("api_base", "base_url"):
            if carrier.get(name) is not None and carrier[name] != deployment_params.get("api_base"):
                raise AnthropicError(400, "Request cannot override the Anthropic OAuth destination")
        if carrier.get("custom_llm_provider") not in (None, "anthropic"):
            raise AnthropicError(400, "Request cannot override the Anthropic OAuth provider")
        for name in ("headers", "extra_headers"):
            _validate_oauth_headers(carrier.get(name), allow_client_auth=is_anthropic_native_client(deployment_params))


def _validate_native_overrides(carrier: Mapping[str, object]) -> None:
    from .native_transport import NATIVE_IDENTITY_FIELD, AnthropicNativeIdentity

    identity: Final = carrier.get(NATIVE_IDENTITY_FIELD)
    if identity is not None and not isinstance(identity, AnthropicNativeIdentity):
        raise AnthropicError(400, "Request cannot override the native SDK server identity")
    if any(
        carrier.get(name) is not None
        for name in ("anthropic_native_sdk_base_url", "anthropic_native_sdk_key", "settings", "setting_sources")
    ):
        raise AnthropicError(400, "Request cannot override the native SDK engine configuration")


def _validate_oauth_setting(
    name: str, carrier: Mapping[str, object], deployment_params: Mapping[str, object], managed: bool
) -> None:
    if name not in carrier:
        return
    supplied: Final = carrier[name]
    if not managed:
        if supplied is not None and not (name == "use_anthropic_oauth" and supplied is False):
            raise AnthropicError(400, "Request cannot enable or select central Anthropic OAuth")
        return
    configured: Final = (
        deployment_params.get(name) or "default" if name == "anthropic_auth_profile" else deployment_params.get(name)
    )
    if supplied is not None and supplied != configured:
        raise AnthropicError(400, "Request cannot override the Anthropic OAuth deployment policy")


def _validate_oauth_headers(headers: object, *, allow_client_auth: bool = False) -> None:
    if isinstance(headers, Mapping) and any(
        (not allow_client_auth and header.lower() in ("authorization", "x-api-key"))
        or header.lower().startswith("x-litellm-native-")
        for header in _OVERRIDES.validate_python(headers)
    ):
        raise AnthropicError(400, "Client credentials cannot override central Anthropic OAuth")


def anthropic_oauth_config(params: Mapping[str, object]) -> AnthropicOAuthConfig | None:
    if not is_anthropic_oauth_managed(params):
        return None
    if params.get("custom_llm_provider") not in (None, "anthropic"):
        raise AnthropicError(400, "Central Anthropic OAuth is only supported by the direct Anthropic provider")
    if any(
        params.get(name) is not None for name in ("token_store", "anthropic_token_store", "anthropic_authenticator")
    ):
        raise AnthropicError(400, "Central Anthropic OAuth credentials must be resolved from the configured profile")
    compatibility: Final = params.get("anthropic_oauth_compatibility")
    if compatibility not in (None, "claude_code"):
        raise AnthropicError(400, "Unsupported Anthropic OAuth compatibility preset")
    if params.get("anthropic_credential_mode") == "claude_code" and not is_anthropic_native_client(params):
        raise AnthropicError(400, "Claude Code credential profiles require the native client execution mode")
    try:
        return AnthropicOAuthConfig.model_validate(
            _OVERRIDES.validate_python(
                MappingProxyType(
                    {
                        "use_anthropic_oauth": True,
                        "anthropic_auth_profile": params.get("anthropic_auth_profile") or "default",
                        "anthropic_token_dir": params.get("anthropic_token_dir"),
                        "anthropic_credential_mode": params.get("anthropic_credential_mode") or "managed",
                    }
                )
            )
        )
    except ValidationError:
        raise AnthropicError(400, "Invalid central Anthropic OAuth configuration") from None


def resolve_anthropic_oauth_access_token(
    params: Mapping[str, object],
    api_base: str | None = None,
    headers: Mapping[str, object] | None = None,
    *,
    token_provider: Callable[[AnthropicOAuthConfig], str] | None = None,
) -> str | None:
    from .native_transport import is_anthropic_native_sdk

    if is_anthropic_native_sdk(params):
        raise AnthropicError(400, "Subscription credentials belong to the native SDK engine")
    config: Final = anthropic_oauth_config(params)
    if config is None:
        return None
    validate_anthropic_oauth_destination(api_base)
    if (
        not is_anthropic_native_client(params)
        and headers is not None
        and any(name.lower() in ("authorization", "x-api-key") for name in headers)
    ):
        raise AnthropicError(400, "Client credentials cannot override central Anthropic OAuth")
    return token_provider(config) if token_provider is not None else AnthropicAuthenticator(config).get_access_token()


def apply_anthropic_oauth_system(system: object, params: Mapping[str, object]) -> JsonValue:
    from .native_transport import is_anthropic_native_sdk

    if is_anthropic_native_sdk(params) or is_anthropic_native_client(params):
        return _SYSTEM.validate_python(system)
    config: Final = anthropic_oauth_config(params)
    original: Final = _SYSTEM.validate_python(system)
    if config is None or params.get("anthropic_oauth_compatibility") != "claude_code":
        return original
    blocks: Final = (
        tuple(original)
        if isinstance(original, list)
        else (_SYSTEM_BLOCK.validate_python(MappingProxyType({"type": "text", "text": original})),)
        if original
        else ()
    )
    if any(_is_billing_block(block) for block in blocks):
        return original
    billing_block: Final = _SYSTEM_BLOCK.validate_python(
        MappingProxyType({"type": "text", "text": ANTHROPIC_OAUTH_BILLING_HEADER})
    )
    return _SYSTEM_BLOCKS.validate_python((billing_block, *blocks))


def _is_billing_block(block: JsonValue) -> bool:
    if not isinstance(block, dict):
        return False
    text: Final = block.get("text")
    return isinstance(text, str) and text.startswith("x-anthropic-billing-header:")
