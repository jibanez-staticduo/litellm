from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

import pytest

from litellm.llms.anthropic.authenticator import AnthropicOAuthConfig
from litellm.llms.anthropic.common_utils import AnthropicError
from litellm.llms.anthropic.oauth_policy import (
    ANTHROPIC_OAUTH_BILLING_HEADER,
    ANTHROPIC_OAUTH_COMPATIBILITY_VERSION,
    ANTHROPIC_OAUTH_USER_AGENT,
    apply_anthropic_oauth_system,
    normalize_anthropic_oauth_headers,
    resolve_anthropic_oauth_access_token,
)

_MANAGED: Final[Mapping[str, object]] = MappingProxyType(
    {"use_anthropic_oauth": True, "anthropic_auth_profile": "work", "anthropic_oauth_compatibility": "claude_code"}
)


def test_managed_headers_set_honest_user_agent_without_mutating_caller_headers() -> None:
    headers: Final = MappingProxyType({"User-Agent": "caller-agent", "anthropic-beta": "client-beta"})
    assert normalize_anthropic_oauth_headers(headers, True) == {
        "user-agent": ANTHROPIC_OAUTH_USER_AGENT,
        "anthropic-beta": "client-beta",
    }
    assert normalize_anthropic_oauth_headers(headers, False) == headers
    assert headers["User-Agent"] == "caller-agent"


def _profile_token(config: AnthropicOAuthConfig) -> str:
    return f"subscription-token-for-{config.anthropic_auth_profile}"


def test_managed_credential_uses_selected_profile_and_ignores_server_api_key() -> None:
    params: Final = MappingProxyType({**_MANAGED, "api_key": "server-api-key"})
    assert resolve_anthropic_oauth_access_token(params, token_provider=_profile_token) == "subscription-token-for-work"
    assert params["api_key"] == "server-api-key"


@pytest.mark.parametrize(
    "destination",
    (
        "http://api.anthropic.com",
        "https://api.anthropic.com.evil.invalid",
        "https://api.anthropic.com@evil.invalid",
        "https://api.anthropic.com:444",
        "https://api.anthropic.com/v1/messages?target=evil",
        "https://api.anthropic.com/v1/responses",
    ),
)
def test_managed_destination_is_rejected_before_credentials_are_read(destination: str) -> None:
    def unreadable_credentials(config: AnthropicOAuthConfig) -> str:
        pytest.fail("The destination must be validated before requesting credentials")

    with pytest.raises(AnthropicError, match="official HTTPS"):
        resolve_anthropic_oauth_access_token(_MANAGED, destination, token_provider=unreadable_credentials)


@pytest.mark.parametrize("header", ("Authorization", "authorization", "X-Api-Key"))
def test_client_credentials_cannot_replace_managed_profile(header: str) -> None:
    with pytest.raises(AnthropicError, match="cannot override"):
        resolve_anthropic_oauth_access_token(
            _MANAGED, headers=MappingProxyType({header: "client-credential"}), token_provider=_profile_token
        )


@pytest.mark.parametrize("provider", ("openai", "bedrock", "vertex_ai"))
def test_managed_credentials_cannot_be_resolved_for_other_providers(provider: str) -> None:
    with pytest.raises(AnthropicError, match="direct Anthropic"):
        resolve_anthropic_oauth_access_token(
            MappingProxyType({**_MANAGED, "custom_llm_provider": provider}), token_provider=_profile_token
        )


def test_api_configuration_never_reads_managed_credentials() -> None:
    def unreadable_credentials(config: AnthropicOAuthConfig) -> str:
        pytest.fail("API deployments must not read subscription credentials")

    assert (
        resolve_anthropic_oauth_access_token(
            MappingProxyType({"use_anthropic_oauth": False}), token_provider=unreadable_credentials
        )
        is None
    )


@pytest.mark.parametrize("field", ("token_store", "anthropic_token_store", "anthropic_authenticator"))
def test_managed_credentials_cannot_be_injected_as_shared_request_objects(field: str) -> None:
    with pytest.raises(AnthropicError, match="configured profile"):
        resolve_anthropic_oauth_access_token(
            MappingProxyType({**_MANAGED, field: object()}), token_provider=_profile_token
        )


def test_compatibility_adds_derived_metadata_without_rewriting_cached_prompt() -> None:
    prompt: Final = [{"type": "text", "text": "Caller instructions", "cache_control": {"type": "ephemeral"}}]
    expected: Final = [{"type": "text", "text": ANTHROPIC_OAUTH_BILLING_HEADER}, *prompt]
    assert ANTHROPIC_OAUTH_COMPATIBILITY_VERSION in ANTHROPIC_OAUTH_BILLING_HEADER
    assert apply_anthropic_oauth_system(prompt, _MANAGED) == expected
    assert prompt == expected[1:]
    assert apply_anthropic_oauth_system(expected, _MANAGED) == expected


def test_compatibility_requires_an_explicit_managed_deployment_preset() -> None:
    assert apply_anthropic_oauth_system("Caller instructions", MappingProxyType({"use_anthropic_oauth": True})) == (
        "Caller instructions"
    )
    assert apply_anthropic_oauth_system(
        "Caller instructions", MappingProxyType({"anthropic_oauth_compatibility": "claude_code"})
    ) == ("Caller instructions")
    with pytest.raises(AnthropicError, match="Unsupported"):
        apply_anthropic_oauth_system(None, MappingProxyType({**_MANAGED, "anthropic_oauth_compatibility": "unknown"}))


def test_native_sdk_preserves_original_system_and_never_resolves_subscription_token() -> None:
    params: Final = MappingProxyType({**_MANAGED, "anthropic_execution_mode": "native_sdk"})
    original: Final = [{"type": "text", "text": "Original caller instructions"}]

    def unreadable_credentials(config: AnthropicOAuthConfig) -> str:
        pytest.fail("Native SDK transport must not read the subscription token")

    assert apply_anthropic_oauth_system(original, params) == original
    with pytest.raises(AnthropicError, match="native SDK"):
        resolve_anthropic_oauth_access_token(params, token_provider=unreadable_credentials)


@pytest.mark.parametrize(
    "override",
    (
        {"anthropic_execution_mode": "direct_http"},
        {"anthropic_auth_profile": "foreign"},
        {"api_key": "caller-key"},
        {"api_base": "http://foreign"},
        {"client": object()},
        {"_anthropic_native_identity": {"owner": "spoof", "deployment": "spoof"}},
        {"extra_headers": {"x-litellm-native-owner": "spoof"}},
        {"extra_headers": {"x-litellm-native-deployment": "spoof"}},
        {"anthropic_native_sdk_key": "caller-service-key"},
        {"settings": {"env": {"ANTHROPIC_API_KEY": "caller-key"}}},
    ),
)
def test_native_sdk_request_overrides_cannot_select_credentials_or_session_identity(
    override: Mapping[str, object],
) -> None:
    from litellm.llms.anthropic.oauth_policy import validate_anthropic_oauth_request_overrides

    params: Final = MappingProxyType({**_MANAGED, "anthropic_execution_mode": "native_sdk"})
    with pytest.raises(AnthropicError, match="cannot override"):
        validate_anthropic_oauth_request_overrides(override, params)


def test_request_cannot_enable_native_sdk_for_an_api_deployment() -> None:
    from litellm.llms.anthropic.oauth_policy import validate_anthropic_oauth_request_overrides

    with pytest.raises(AnthropicError, match="cannot enable"):
        validate_anthropic_oauth_request_overrides({"anthropic_execution_mode": "native_sdk"}, {})
