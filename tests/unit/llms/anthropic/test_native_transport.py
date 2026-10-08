import copy
from collections.abc import Mapping
from types import MappingProxyType
from typing import Final
from unittest.mock import patch

import pytest

from litellm.llms.anthropic.chat.transformation import AnthropicConfig
from litellm.llms.anthropic.common_utils import AnthropicError
from litellm.llms.anthropic.native_transport import (
    NATIVE_IDENTITY_FIELD,
    AnthropicNativeIdentity,
    decode_native_tool_call_id,
    is_anthropic_native_sdk,
    native_sdk_connection,
)
from litellm.llms.anthropic.pass_through.messages.transformation import AnthropicMessagesConfig
from litellm.types.router import GenericLiteLLMParams

_ENVIRONMENT: Final = MappingProxyType(
    {"ANTHROPIC_NATIVE_SDK_BASE_URL": "http://native-broker:8765", "ANTHROPIC_NATIVE_SDK_KEY": "private-test-key"}
)
_PARAMS: Final[Mapping[str, object]] = MappingProxyType(
    {
        "use_anthropic_oauth": True,
        "anthropic_execution_mode": "native_sdk",
        "anthropic_auth_profile": "fixed",
        NATIVE_IDENTITY_FIELD: AnthropicNativeIdentity("owner-hash", "selected-deployment"),
    }
)


@pytest.mark.parametrize("identifier", ("litellm_native_tool_!", "litellm_native_tool_e30"))
def test_native_tool_replay_rejects_malformed_payload(identifier: str) -> None:
    with pytest.raises(AnthropicError, match="Invalid native SDK tool replay"):
        decode_native_tool_call_id(identifier)


def test_broker_credentials_and_identity_are_separate_from_provider_credentials() -> None:
    params: Final = MappingProxyType({**_PARAMS, "api_key": "unused-api-key", "api_base": "https://unused.invalid"})
    connection: Final = native_sdk_connection(params, environment=_ENVIRONMENT)
    assert connection.url() == "http://native-broker:8765/v1/messages"
    assert connection.url("count_tokens") == "http://native-broker:8765/v1/messages/count_tokens"
    assert connection.headers["authorization"] == "Bearer private-test-key"
    assert connection.headers["x-litellm-native-owner"] == "owner-hash"
    assert connection.headers["x-litellm-native-profile"] == params["anthropic_auth_profile"]
    assert connection.headers["x-litellm-native-deployment"] == "selected-deployment"
    assert "unused-api-key" not in str(connection.headers)
    assert "private-test-key" not in repr(connection)


@pytest.mark.parametrize(
    "identity", (None, {"owner": "spoof", "deployment": "spoof"}, AnthropicNativeIdentity("owner"))
)
def test_native_sdk_rejects_untrusted_or_incomplete_identity(identity: object) -> None:
    with pytest.raises(AnthropicError, match="authenticated server"):
        native_sdk_connection(MappingProxyType({**_PARAMS, NATIVE_IDENTITY_FIELD: identity}), environment=_ENVIRONMENT)


@pytest.mark.parametrize(
    "environment",
    (
        {},
        {"ANTHROPIC_NATIVE_SDK_BASE_URL": "https://api.anthropic.com", "ANTHROPIC_NATIVE_SDK_KEY": "key"},
        {"ANTHROPIC_NATIVE_SDK_BASE_URL": "http://user:password@broker", "ANTHROPIC_NATIVE_SDK_KEY": "key"},
        {"ANTHROPIC_NATIVE_SDK_BASE_URL": "http://broker/path", "ANTHROPIC_NATIVE_SDK_KEY": "key"},
        {"ANTHROPIC_NATIVE_SDK_BASE_URL": "http://broker?query", "ANTHROPIC_NATIVE_SDK_KEY": "key"},
        {"ANTHROPIC_NATIVE_SDK_BASE_URL": "http://broker", "ANTHROPIC_NATIVE_SDK_KEY": "key\nheader"},
    ),
)
def test_native_sdk_rejects_missing_or_unsafe_broker_environment(environment: Mapping[str, str]) -> None:
    with pytest.raises(AnthropicError, match="environment configuration"):
        native_sdk_connection(_PARAMS, environment=environment)


@pytest.mark.parametrize(
    "override", ({"use_anthropic_oauth": False}, {"anthropic_auth_profile": None}, {"custom_llm_provider": "openai"})
)
def test_native_sdk_requires_managed_provider_and_fixed_profile(override: Mapping[str, object]) -> None:
    with pytest.raises(AnthropicError, match="fixed profile"):
        is_anthropic_native_sdk(MappingProxyType({**_PARAMS, **override}))


def test_identity_survives_pydantic_and_router_copy_without_becoming_json_authority() -> None:
    identity: Final = AnthropicNativeIdentity("owner", "deployment")
    params: Final = GenericLiteLLMParams.model_validate({**_PARAMS, NATIVE_IDENTITY_FIELD: identity})
    assert params.model_dump()[NATIVE_IDENTITY_FIELD] is identity
    assert copy.deepcopy(identity) is identity
    with pytest.raises(AttributeError, match="immutable"):
        setattr(identity, "_owner", "spoof")


def test_chat_and_messages_select_native_auth_and_url_before_api_or_oauth_resolution() -> None:
    params: Final = dict(_PARAMS)
    with patch.dict("os.environ", {**_ENVIRONMENT, "ANTHROPIC_API_KEY": "global-api-key"}):
        connection: Final = native_sdk_connection(params)
        chat_headers: Final = AnthropicConfig().validate_environment(
            headers={"x-api-key": "caller-key"},
            model="claude-test",
            messages=[],
            optional_params={},
            litellm_params=params,
            api_key="caller-key",
            api_base="https://api.anthropic.com",
        )
        messages_headers, base = AnthropicMessagesConfig().validate_anthropic_messages_environment(
            headers={"authorization": "Bearer caller-token"},
            model="claude-test",
            messages=[],
            optional_params={},
            litellm_params=params,
            api_key="caller-key",
            api_base="https://api.anthropic.com",
        )
        url: Final = AnthropicMessagesConfig().get_complete_url(
            api_base="https://caller.invalid",
            api_key="caller-key",
            model="claude-test",
            optional_params={},
            litellm_params=params,
        )
    assert chat_headers == connection.headers
    assert messages_headers == connection.headers
    assert base == connection.api_base
    assert url == connection.url()


@pytest.mark.asyncio
async def test_async_messages_selects_native_identity_before_api_or_federation_resolution() -> None:
    params: Final = dict(_PARAMS)
    with patch.dict("os.environ", {**_ENVIRONMENT, "ANTHROPIC_API_KEY": "global-api-key"}):
        connection: Final = native_sdk_connection(params)
        headers, base = await AnthropicMessagesConfig().avalidate_anthropic_messages_environment(
            headers={"authorization": "Bearer caller-token"},
            model="claude-test",
            messages=[],
            optional_params={},
            litellm_params=params,
            api_key="caller-key",
            api_base="https://api.anthropic.com",
        )
    assert headers == connection.headers
    assert base == connection.api_base
