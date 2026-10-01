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
)


def is_anthropic_oauth_managed(params: Mapping[str, object]) -> bool:
    return params.get("use_anthropic_oauth") is True


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
    for carrier in carriers:
        for name in _OAUTH_FIELDS:
            _validate_oauth_setting(name, carrier, deployment_params, managed)
        if not managed:
            continue
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
            _validate_oauth_headers(carrier.get(name))


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


def _validate_oauth_headers(headers: object) -> None:
    if isinstance(headers, Mapping) and any(
        header.lower() in ("authorization", "x-api-key") for header in _OVERRIDES.validate_python(headers)
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
    try:
        return AnthropicOAuthConfig.model_validate(
            _OVERRIDES.validate_python(
                MappingProxyType(
                    {
                        "use_anthropic_oauth": True,
                        "anthropic_auth_profile": params.get("anthropic_auth_profile") or "default",
                        "anthropic_token_dir": params.get("anthropic_token_dir"),
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
    config: Final = anthropic_oauth_config(params)
    if config is None:
        return None
    validate_anthropic_oauth_destination(api_base)
    if headers is not None and any(name.lower() in ("authorization", "x-api-key") for name in headers):
        raise AnthropicError(400, "Client credentials cannot override central Anthropic OAuth")
    return token_provider(config) if token_provider is not None else AnthropicAuthenticator(config).get_access_token()


def apply_anthropic_oauth_system(system: object, params: Mapping[str, object]) -> JsonValue:
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
