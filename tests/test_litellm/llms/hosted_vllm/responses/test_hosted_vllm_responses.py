"""
Tests for hosted_vllm responses API support.

Regression test for: https://github.com/BerriAI/litellm/issues
Bug: client.responses.create() raised TypeError: 'NoneType' object is not a mapping
when extra_body=None was passed through the responses→completion pipeline for
hosted_vllm (and any OpenAI-compatible provider using add_provider_specific_params_to_optional_params).
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath("../../../../.."))  # Adds the parent directory to the system path

import litellm
from litellm.llms.hosted_vllm.chat.transformation import HostedVLLMChatConfig
from litellm.llms.hosted_vllm.responses.transformation import (
    HostedVLLMResponsesAPIConfig,
)
from litellm.types.router import GenericLiteLLMParams
from litellm.types.utils import LlmProviders
from litellm.utils import ProviderConfigManager


def _make_mock_responses_api_response(content: str = "Hello! I'm doing well.") -> dict:
    return {
        "id": "resp-test123",
        "object": "response",
        "created_at": 1234567890,
        "model": "Qwen/Qwen3-8B",
        "output": [
            {
                "type": "message",
                "id": "msg-test123",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": content,
                        "annotations": [],
                    }
                ],
            }
        ],
        "status": "completed",
        "usage": {
            "input_tokens": 10,
            "output_tokens": 20,
            "total_tokens": 30,
        },
    }


def _make_mock_http_client(response_body: dict) -> MagicMock:
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/json"}
    mock_response.json.return_value = response_body
    mock_response.text = json.dumps(response_body)
    mock_client.post.return_value = mock_response
    return mock_client


def test_hosted_vllm_responses_create_with_string_input():
    """
    Test that hosted_vllm routes directly to the native /v1/responses endpoint
    when the Responses API config is registered, and correctly parses the response.
    """
    mock_client = _make_mock_http_client(_make_mock_responses_api_response("I'm doing well, thanks!"))

    with patch(
        "litellm.llms.custom_httpx.llm_http_handler._get_httpx_client",
        return_value=mock_client,
    ):
        response = litellm.responses(
            model="hosted_vllm/Qwen/Qwen3-8B",
            input="Hello, how are you?",
            api_base="https://test-vllm.example.com/v1",
            api_key="test-key",
        )

    from litellm.types.llms.openai import ResponsesAPIResponse

    assert response is not None
    assert isinstance(response, ResponsesAPIResponse)
    assert len(response.output) > 0
    output_message = response.output[0]
    assert output_message.role == "assistant"  # type: ignore[union-attr]
    assert len(output_message.content) > 0  # type: ignore[union-attr]
    assert "well" in output_message.content[0].text  # type: ignore[union-attr]


def test_hosted_vllm_responses_create_with_explicit_none_extra_body():
    """
    Directly verify the fix in add_provider_specific_params_to_optional_params:
    extra_body=None must not crash when building optional_params.
    """
    from litellm.utils import get_optional_params

    # This should not raise TypeError: 'NoneType' object is not a mapping
    optional_params = get_optional_params(
        model="Qwen/Qwen3-8B",
        custom_llm_provider="hosted_vllm",
        extra_body=None,
    )

    # extra_body=None should be normalized to an empty dict (or absent)
    assert optional_params.get("extra_body") is not None or "extra_body" not in optional_params


def test_hosted_vllm_provider_config_registration():
    """Test that ProviderConfigManager returns HostedVLLMResponsesAPIConfig for hosted_vllm."""
    config = ProviderConfigManager.get_provider_responses_api_config(
        model="hosted_vllm/Qwen/Qwen3-8B",
        provider=LlmProviders.HOSTED_VLLM,
    )

    assert config is not None
    assert isinstance(config, HostedVLLMResponsesAPIConfig)
    assert config.custom_llm_provider == LlmProviders.HOSTED_VLLM


def test_hosted_vllm_responses_api_url():
    """Test get_complete_url() constructs the correct URL."""
    config = HostedVLLMResponsesAPIConfig()

    # api_base without /v1
    url = config.get_complete_url(
        api_base="http://localhost:8000",
        litellm_params={},
    )
    assert url == "http://localhost:8000/v1/responses"

    # api_base with /v1
    url_with_v1 = config.get_complete_url(
        api_base="http://localhost:8000/v1",
        litellm_params={},
    )
    assert url_with_v1 == "http://localhost:8000/v1/responses"

    # api_base with trailing slash
    url_with_slash = config.get_complete_url(
        api_base="http://localhost:8000/v1/",
        litellm_params={},
    )
    assert url_with_slash == "http://localhost:8000/v1/responses"


def test_hosted_vllm_responses_api_url_requires_api_base():
    """Test get_complete_url() raises ValueError when api_base is not set."""
    config = HostedVLLMResponsesAPIConfig()

    with pytest.raises(ValueError, match="api_base not set"):
        config.get_complete_url(
            api_base=None,
            litellm_params={},
        )


def test_hosted_vllm_validate_environment_default_api_key():
    """Test validate_environment() defaults to 'fake-api-key' when no key is provided."""
    config = HostedVLLMResponsesAPIConfig()

    headers = config.validate_environment(
        headers={},
        model="Qwen/Qwen3-8B",
        litellm_params=GenericLiteLLMParams(),
    )

    assert headers.get("Authorization") == "Bearer fake-api-key"


def test_hosted_vllm_validate_environment_custom_api_key():
    """Test validate_environment() uses the provided api_key."""
    config = HostedVLLMResponsesAPIConfig()

    headers = config.validate_environment(
        headers={},
        model="Qwen/Qwen3-8B",
        litellm_params=GenericLiteLLMParams(api_key="my-custom-key"),
    )

    assert headers.get("Authorization") == "Bearer my-custom-key"


@pytest.mark.parametrize(
    ("public_effort", "upstream_effort"),
    [("off", "none"), ("low", "low"), ("high", "high"), ("max", "max")],
)
def test_deepseek_v4_native_responses_reasoning_policy(public_effort, upstream_effort):
    config = HostedVLLMResponsesAPIConfig()
    litellm_params = GenericLiteLLMParams(litellm_metadata={"model_group": "deepseek-v4-flash-fp8-mtp"})
    transformed = config.transform_responses_api_request(
        model="deepseek-ai/DeepSeek-V4-Flash",
        input="test",
        response_api_optional_request_params={"reasoning": {"effort": public_effort}},
        litellm_params=litellm_params,
        headers={},
    )
    transformed = config.finalize_request(
        model="deepseek-ai/DeepSeek-V4-Flash",
        request_data=transformed,
        litellm_params=litellm_params,
    )

    assert transformed["reasoning"] == {"effort": upstream_effort}


def test_deepseek_v4_native_responses_rejects_before_transport():
    mock_client = _make_mock_http_client(_make_mock_responses_api_response())

    with (
        patch(
            "litellm.llms.custom_httpx.llm_http_handler._get_httpx_client",
            return_value=mock_client,
        ),
        pytest.raises(Exception, match=r"Invalid reasoning_effort 'medium'.*deepseek-v4-flash-fp8-mtp"),
    ):
        litellm.responses(
            model="hosted_vllm/deepseek-ai/DeepSeek-V4-Flash",
            input="test",
            reasoning={"effort": "medium"},
            litellm_metadata={"model_group": "deepseek-v4-flash-fp8-mtp"},
            api_base="https://test-vllm.example.com/v1",
        )

    mock_client.post.assert_not_called()


@pytest.mark.parametrize(
    ("stream", "reasoning", "extra_body"),
    [
        (False, None, {"reasoning": {"effort": "medium"}}),
        (True, {"effort": "low"}, {"reasoning": {"effort": "xhigh"}}),
        (False, {"effort": "high"}, {"reasoning": {"effort": None}}),
    ],
)
def test_deepseek_v4_responses_extra_body_rejection_makes_no_transport_call(stream, reasoning, extra_body):
    mock_client = _make_mock_http_client(_make_mock_responses_api_response())

    with (
        patch(
            "litellm.llms.custom_httpx.llm_http_handler._get_httpx_client",
            return_value=mock_client,
        ),
        pytest.raises(Exception, match=r"Invalid reasoning_effort .*deepseek-v4-flash-fp8-mtp"),
    ):
        litellm.responses(
            model="hosted_vllm/deepseek-ai/DeepSeek-V4-Flash",
            input="test",
            reasoning=reasoning,
            extra_body=extra_body,
            litellm_metadata={"model_group": "deepseek-v4-flash-fp8-mtp"},
            api_base="https://test-vllm.example.com/v1",
            stream=stream,
        )

    mock_client.post.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True])
async def test_deepseek_v4_async_responses_extra_body_rejection_makes_no_transport_call(stream):
    mock_client = MagicMock()
    mock_client.post = MagicMock()

    with (
        patch(
            "litellm.llms.custom_httpx.llm_http_handler.get_async_httpx_client",
            return_value=mock_client,
        ),
        pytest.raises(Exception, match=r"Invalid reasoning_effort 'medium'.*deepseek-v4-flash-fp8-mtp"),
    ):
        await litellm.aresponses(
            model="hosted_vllm/deepseek-ai/DeepSeek-V4-Flash",
            input="test",
            extra_body={"reasoning": {"effort": "medium"}},
            litellm_metadata={"model_group": "deepseek-v4-flash-fp8-mtp"},
            api_base="https://test-vllm.example.com/v1",
            stream=stream,
        )

    mock_client.post.assert_not_called()


@pytest.mark.parametrize(
    ("stream", "extra_body", "error_pattern"),
    [
        (False, {"reasoning_effort": "medium"}, r"Invalid reasoning_effort 'medium'"),
        (
            True,
            {"reasoning": {"effort": "low"}, "reasoning_effort": "medium"},
            r"Conflicting reasoning values.*reasoning.effort='low'.*reasoning_effort='medium'",
        ),
        (
            False,
            {"reasoning": {"effort": "medium"}, "reasoning_effort": "low"},
            r"Conflicting reasoning values.*reasoning.effort='medium'.*reasoning_effort='low'",
        ),
    ],
)
def test_deepseek_v4_responses_compatibility_rejection_makes_no_transport_call(stream, extra_body, error_pattern):
    mock_client = _make_mock_http_client(_make_mock_responses_api_response())

    with (
        patch(
            "litellm.llms.custom_httpx.llm_http_handler._get_httpx_client",
            return_value=mock_client,
        ),
        pytest.raises(Exception, match=error_pattern),
    ):
        litellm.responses(
            model="hosted_vllm/deepseek-ai/DeepSeek-V4-Flash",
            input="test",
            extra_body=extra_body,
            litellm_metadata={"model_group": "deepseek-v4-flash-fp8-mtp"},
            api_base="https://test-vllm.example.com/v1",
            stream=stream,
        )

    mock_client.post.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True])
async def test_deepseek_v4_async_responses_compatibility_conflict_makes_no_transport_call(stream):
    mock_client = MagicMock()
    mock_client.post = MagicMock()

    with (
        patch(
            "litellm.llms.custom_httpx.llm_http_handler.get_async_httpx_client",
            return_value=mock_client,
        ),
        pytest.raises(
            Exception, match=r"Conflicting reasoning values.*reasoning.effort='high'.*reasoning_effort='xhigh'"
        ),
    ):
        await litellm.aresponses(
            model="hosted_vllm/deepseek-ai/DeepSeek-V4-Flash",
            input="test",
            extra_body={"reasoning": {"effort": "high"}, "reasoning_effort": "xhigh"},
            litellm_metadata={"model_group": "deepseek-v4-flash-fp8-mtp"},
            api_base="https://test-vllm.example.com/v1",
            stream=stream,
        )

    mock_client.post.assert_not_called()


def test_deepseek_v4_responses_equal_dual_reasoning_is_canonicalized():
    mock_client = _make_mock_http_client(_make_mock_responses_api_response())

    with patch(
        "litellm.llms.custom_httpx.llm_http_handler._get_httpx_client",
        return_value=mock_client,
    ):
        litellm.responses(
            model="hosted_vllm/deepseek-ai/DeepSeek-V4-Flash",
            input="test",
            extra_body={"reasoning": {"effort": "off"}, "reasoning_effort": "off"},
            litellm_metadata={"model_group": "deepseek-v4-flash-fp8-mtp"},
            api_base="https://test-vllm.example.com/v1",
        )

    sent_data = mock_client.post.call_args.kwargs["json"]
    assert sent_data["reasoning"] == {"effort": "none"}
    assert "reasoning_effort" not in sent_data


def test_unrelated_hosted_vllm_extra_body_behavior_is_unchanged():
    mock_client = _make_mock_http_client(_make_mock_responses_api_response())

    with patch(
        "litellm.llms.custom_httpx.llm_http_handler._get_httpx_client",
        return_value=mock_client,
    ):
        litellm.responses(
            model="hosted_vllm/Qwen/Qwen3-8B",
            input="test",
            extra_body={"reasoning": {"effort": "medium"}, "reasoning_effort": "xhigh"},
            litellm_metadata={"model_group": "qwen"},
            api_base="https://test-vllm.example.com/v1",
        )

    sent_data = mock_client.post.call_args.kwargs["json"]
    assert sent_data["reasoning"] == {"effort": "medium"}
    assert sent_data["reasoning_effort"] == "xhigh"


@pytest.mark.parametrize("stream", [False, True])
def test_deepseek_v4_responses_chat_bridge_reasoning_policy(stream):
    from litellm.responses.litellm_completion_transformation.transformation import (
        LiteLLMCompletionResponsesConfig,
    )

    bridge_request = LiteLLMCompletionResponsesConfig.transform_responses_api_request_to_chat_completion_request(
        model="deepseek-ai/DeepSeek-V4-Flash",
        input="test",
        responses_api_request={"reasoning": {"effort": "off"}},
        custom_llm_provider="hosted_vllm",
        stream=stream,
        metadata={"model_group": "deepseek-v4-flash-fp8-mtp"},
    )
    optional_params = HostedVLLMChatConfig().map_openai_params(
        non_default_params={
            "reasoning_effort": bridge_request["reasoning_effort"],
            "stream": bridge_request["stream"],
        },
        optional_params={},
        model=bridge_request["model"],
        drop_params=False,
    )
    transformed = HostedVLLMChatConfig().transform_request(
        model=bridge_request["model"],
        messages=bridge_request["messages"],
        optional_params=optional_params,
        litellm_params={"metadata": bridge_request["metadata"]},
        headers={},
    )
    transformed = HostedVLLMChatConfig().finalize_request(
        model=bridge_request["model"],
        request_data=transformed,
        litellm_params={"metadata": bridge_request["metadata"]},
    )

    assert transformed["reasoning_effort"] == "none"
    assert transformed.get("stream", False) is stream
