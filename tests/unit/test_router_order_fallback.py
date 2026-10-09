from collections.abc import Mapping
from functools import partial
from pathlib import Path
from queue import SimpleQueue
from pydantic import JsonValue, TypeAdapter
from litellm.llms.anthropic import oauth_policy
from litellm.llms.anthropic.authenticator import AnthropicAuthenticator
from litellm.llms.anthropic.chat import handler as anthropic_chat_handler
from litellm.llms.anthropic.common_utils import AnthropicError
from litellm.llms.custom_httpx.http_handler import AsyncHTTPHandler, HTTPHandler
from litellm.proxy._types import UserAPIKeyAuth
from litellm.utils import _get_deployment_order

"""
Tests for order-based fallback routing.

When deployments have `order` set in litellm_params, lower order deployments
should be tried first, and higher order deployments should be used as fallbacks
when lower order deployments fail.
"""

import json
from typing import Final, Optional

import httpx
import pytest
import respx
from openai import AsyncOpenAI

import litellm
from litellm import Router
from litellm.integrations.custom_logger import CustomLogger
from litellm.router_utils.prompt_caching_cache import PromptCachingCache
from litellm.types.router import RouterRateLimitError
from litellm.utils import get_deployment_order, get_order_filtered_deployments

# ---------------------------------------------------------------------------
# Unit tests for get_order_filtered_deployments
# ---------------------------------------------------------------------------


class TestGetOrderFilteredDeployments:
    def _make_deployment(self, order: Optional[int], dep_id: str) -> dict:
        params: dict = {"model": "gpt-4o", "api_key": "key"}
        if order is not None:
            params["order"] = order
        return {
            "model_name": "test-model",
            "litellm_params": params,
            "model_info": {"id": dep_id},
        }

    def test_returns_min_order_group(self):
        deps = [
            self._make_deployment(1, "a"),
            self._make_deployment(2, "b"),
            self._make_deployment(1, "c"),
        ]
        result = get_order_filtered_deployments(deps)
        assert len(result) == 2
        assert all(d["model_info"]["id"] in ("a", "c") for d in result)

    def test_target_order_filters_to_exact_level(self):
        deps = [
            self._make_deployment(1, "a"),
            self._make_deployment(2, "b"),
            self._make_deployment(3, "c"),
        ]
        result = get_order_filtered_deployments(deps, target_order=2)
        assert len(result) == 1
        assert result[0]["model_info"]["id"] == "b"

    def test_target_order_no_match_returns_empty(self):
        deps = [
            self._make_deployment(1, "a"),
            self._make_deployment(2, "b"),
        ]
        result = get_order_filtered_deployments(deps, target_order=99)
        assert result == []

    def test_target_order_no_match_does_not_reselect_lower_order(self):
        deps = [
            self._make_deployment(1, "a"),
            self._make_deployment(2, "b"),
        ]
        remaining_after_pre_call = [deps[0]]
        result = get_order_filtered_deployments(remaining_after_pre_call, target_order=2)
        assert result == []

    def test_no_order_set_returns_all(self):
        deps = [
            self._make_deployment(None, "a"),
            self._make_deployment(None, "b"),
        ]
        result = get_order_filtered_deployments(deps)
        assert len(result) == 2

    def test_empty_list(self):
        result = get_order_filtered_deployments([])
        assert result == []

    def test_single_order_returns_all_with_that_order(self):
        deps = [
            self._make_deployment(1, "a"),
            self._make_deployment(1, "b"),
        ]
        result = get_order_filtered_deployments(deps)
        assert len(result) == 2


def test_get_deployment_order_returns_unvalidated_order():
    assert get_deployment_order({"litellm_params": {"order": "first"}}) == "first"


# ---------------------------------------------------------------------------
# Integration tests for order-based fallback in Router
# ---------------------------------------------------------------------------


def test_router_order_without_pre_call_checks():
    """Order filtering should work even when enable_pre_call_checks=False (default)."""
    router = Router(
        model_list=[
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "key",
                    "mock_response": "from order 1",
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "key",
                    "mock_response": "from order 2",
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
        ],
        num_retries=0,
        enable_pre_call_checks=False,
    )

    for _ in range(20):
        response = router.completion(
            model="test-model",
            messages=[{"role": "user", "content": "hi"}],
        )
        assert response._hidden_params["model_id"] == "1"


def test_router_order_no_fallback_when_healthy():
    """When order=1 is healthy, order=2 should never be used."""
    router = Router(
        model_list=[
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "key",
                    "mock_response": "from order 1",
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "key",
                    "mock_response": "from order 2",
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
        ],
        num_retries=0,
    )

    for _ in range(50):
        response = router.completion(
            model="test-model",
            messages=[{"role": "user", "content": "hi"}],
        )
        assert response._hidden_params["model_id"] == "1"


@pytest.mark.asyncio
async def test_router_order_fallback_on_failure():
    """When order=1 fails, order=2 should be tried as fallback."""
    router = Router(
        model_list=[
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "bad-key",
                    "mock_response": Exception("connection error"),
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "good-key",
                    "mock_response": "success from order 2",
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
        ],
        num_retries=0,
    )

    response = await router.acompletion(
        model="test-model",
        messages=[{"role": "user", "content": "hi"}],
    )
    assert response._hidden_params["model_id"] == "2"


@pytest.mark.asyncio
async def test_router_order_fallback_three_levels():
    """When order=1 and order=2 both fail, order=3 should be tried."""
    router = Router(
        model_list=[
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "bad",
                    "mock_response": Exception("fail 1"),
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "bad",
                    "mock_response": Exception("fail 2"),
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "good",
                    "mock_response": "success from order 3",
                    "order": 3,
                },
                "model_info": {"id": "3"},
            },
        ],
        num_retries=0,
    )

    response = await router.acompletion(
        model="test-model",
        messages=[{"role": "user", "content": "hi"}],
    )
    assert response._hidden_params["model_id"] == "3"


@pytest.mark.asyncio
async def test_router_order_fallback_then_external_fallback():
    """When all order levels fail, external fallbacks should be tried."""
    router = Router(
        model_list=[
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "bad",
                    "mock_response": Exception("fail order 1"),
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "bad",
                    "mock_response": Exception("fail order 2"),
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
            {
                "model_name": "fallback-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "good",
                    "mock_response": "success from external fallback",
                },
                "model_info": {"id": "fallback"},
            },
        ],
        fallbacks=[{"test-model": ["fallback-model"]}],
        num_retries=0,
    )

    response = await router.acompletion(
        model="test-model",
        messages=[{"role": "user", "content": "hi"}],
    )
    assert response._hidden_params["model_id"] == "fallback"


@pytest.mark.asyncio
async def test_router_order_fallback_with_non_standard_fallbacks():
    """Non-standard fallback formats (e.g. fallbacks=["model-name"]) passed
    per-request should still be tried after all order levels are exhausted."""
    router = Router(
        model_list=[
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "bad",
                    "mock_response": Exception("fail order 1"),
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "bad",
                    "mock_response": Exception("fail order 2"),
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
            {
                "model_name": "fallback-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "good",
                    "mock_response": "success from non-standard fallback",
                },
                "model_info": {"id": "fallback"},
            },
        ],
        num_retries=0,
    )

    response = await router.acompletion(
        model="test-model",
        messages=[{"role": "user", "content": "hi"}],
        fallbacks=["fallback-model"],  # non-standard format, passed per-request
    )
    assert response._hidden_params["model_id"] == "fallback"


@pytest.mark.asyncio
async def test_router_order_fallback_with_wildcard_model_group():
    """Wildcard model groups should also advance across order levels."""
    router = Router(
        model_list=[
            {
                "model_name": "openai/*",
                "litellm_params": {
                    "model": "openai/*",
                    "api_key": "bad",
                    "mock_response": Exception("fail order 1"),
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "openai/*",
                "litellm_params": {
                    "model": "openai/*",
                    "api_key": "good",
                    "mock_response": "success from wildcard order 2",
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
        ],
        num_retries=0,
    )

    response = await router.acompletion(
        model="openai/gpt-4.1-mini",
        messages=[{"role": "user", "content": "hi"}],
    )
    assert response._hidden_params["model_id"] == "2"


@pytest.mark.asyncio
async def test_router_order_fallback_with_hidden_model_group_alias():
    router = Router(
        model_list=[
            {
                "model_name": "canonical-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "bad",
                    "mock_response": Exception("fail order 1"),
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "canonical-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "good",
                    "mock_response": "success from order 2",
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
        ],
        model_group_alias={"hidden-alias": {"model": "canonical-model", "hidden": True}},
        num_retries=0,
    )

    assert "hidden-alias" not in {deployment["model_name"] for deployment in router.get_model_list() or []}

    response = await router.acompletion(
        model="hidden-alias",
        messages=[{"role": "user", "content": "hi"}],
    )

    assert response._hidden_params["model_id"] == "2"


@pytest.mark.asyncio
async def test_router_order_fallback_does_not_reselect_order_1_when_order_2_is_filtered_out():
    class _DropOrder2(CustomLogger):
        async def async_filter_deployments(
            self, model, healthy_deployments, messages, request_kwargs=None, parent_otel_span=None
        ):
            return [d for d in healthy_deployments if get_deployment_order(d) != 2]

    drop_order_2: Final = _DropOrder2()
    router = Router(
        model_list=[
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "key",
                    "mock_response": "litellm.RateLimitError",
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "key",
                    "mock_response": "success from order 2",
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
        ],
        num_retries=0,
    )
    litellm.callbacks.append(drop_order_2)
    try:
        with pytest.raises(RouterRateLimitError, match="No deployments available") as exc_info:
            await router.acompletion(
                model="test-model",
                messages=[{"role": "user", "content": "hi"}],
            )
        assert "success from order 2" not in str(exc_info.value)
    finally:
        litellm.callbacks.remove(drop_order_2)


@pytest.mark.asyncio
async def test_router_order_fallback_ignores_prompt_cache_pin_on_target_order():
    messages = [{"role": "user", "content": "word " * 5000}]
    router = Router(
        model_list=[
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "bad",
                    "mock_response": Exception("azure peak load"),
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "good",
                    "mock_response": "success from order 2",
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
        ],
        num_retries=0,
        optional_pre_call_checks=["prompt_caching"],
    )
    await PromptCachingCache(cache=router.cache).async_add_model_id(
        model_id="1",
        messages=messages,
        tools=None,
    )
    response = await router.acompletion(model="test-model", messages=messages)
    assert response._hidden_params["model_id"] == "2"


@pytest.mark.asyncio
async def test_router_order_fallback_retries_keep_target_order():
    seen_target_orders: Final = []

    class _RecordTargetOrder(CustomLogger):
        async def async_filter_deployments(
            self, model, healthy_deployments, messages, request_kwargs=None, parent_otel_span=None
        ):
            seen_target_orders.append((request_kwargs or {}).get("_target_order"))
            return healthy_deployments

    recorder: Final = _RecordTargetOrder()
    router = Router(
        model_list=[
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "bad",
                    "mock_response": Exception("fail order 1"),
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "gpt-4o",
                    "api_key": "bad",
                    "mock_response": Exception("fail order 2"),
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
        ],
        num_retries=1,
    )
    litellm.callbacks.append(recorder)
    try:
        with pytest.raises(Exception, match="fail order 2"):
            await router.acompletion(
                model="test-model",
                messages=[{"role": "user", "content": "hi"}],
            )
    finally:
        litellm.callbacks.remove(recorder)
    assert seen_target_orders.count(2) >= 2


@pytest.mark.asyncio
async def test_generic_api_call_strips_target_order_from_provider_kwargs():
    captured: Final = {}

    async def _fake_provider(**provider_kwargs):
        captured.update(provider_kwargs)
        return "ok"

    router = Router(
        model_list=[
            {
                "model_name": "test-model",
                "litellm_params": {"model": "gpt-4o", "api_key": "key", "order": 2},
                "model_info": {"id": "2"},
            },
        ],
    )
    response = await router._ageneric_api_call_with_fallbacks_helper(
        model="test-model",
        original_generic_function=_fake_provider,
        _target_order=2,
        messages=[{"role": "user", "content": "hi"}],
    )
    assert response == "ok"
    assert captured["model"] == "gpt-4o"
    assert "_target_order" not in captured


@pytest.mark.asyncio
async def test_text_completion_order_fallback_hop_does_not_send_target_order_upstream():
    upstream_bodies: Final[list[dict]] = []

    def _upstream(request: httpx.Request) -> httpx.Response:
        upstream_bodies.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "id": "cmpl-1",
                "object": "text_completion",
                "created": 0,
                "model": "gpt-3.5-turbo-instruct",
                "choices": [{"text": "ok from order 2", "index": 0, "logprobs": None, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            },
        )

    upstream_client: Final = AsyncOpenAI(
        api_key="key",
        base_url="http://upstream.test",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(_upstream)),
    )
    router = Router(
        model_list=[
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "text-completion-openai/gpt-3.5-turbo-instruct",
                    "api_key": "key",
                    "mock_response": Exception("fail order 1"),
                    "order": 1,
                },
                "model_info": {"id": "1"},
            },
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "text-completion-openai/gpt-3.5-turbo-instruct",
                    "api_key": "key",
                    "api_base": "http://upstream.test",
                    "order": 2,
                },
                "model_info": {"id": "2"},
            },
        ],
        num_retries=0,
    )
    try:
        response = await router.atext_completion(model="test-model", prompt="hi", client=upstream_client)
    finally:
        await upstream_client.close()

    assert response._hidden_params["model_id"] == "2"
    assert upstream_bodies
    assert all("_target_order" not in body for body in upstream_bodies)



_OPENAI_RESPONSES_URL: Final = "https://api.openai.com/v1/responses"
_MANTLE_RESPONSES_URL: Final = "https://bedrock-mantle.us-east-1.api.aws/openai/v1/responses"
_OVERLOADED_UPSTREAM: Final = {"error": {"message": "overloaded", "type": "server_error", "code": "server_error"}}


def _completed_response_body(response_id: str, model: str, text: str) -> dict[str, object]:
    return {
        "id": response_id,
        "object": "response",
        "created_at": 0,
        "status": "completed",
        "model": model,
        "output": [
            {
                "id": f"msg_{response_id}",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [{"type": "output_text", "text": text, "annotations": []}],
            }
        ],
        "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
    }


def _responses_history_with_order_1_reasoning() -> list[dict]:
    return [
        {"type": "message", "role": "user", "content": "What is 17*23?"},
        {
            "type": "reasoning",
            "id": "rs_order1",
            "encrypted_content": "gAAAAA-minted-by-order-1",
            "summary": [{"type": "summary_text", "text": "multiply 17 by 23"}],
        },
        {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "391"}]},
        {"type": "message", "role": "user", "content": "And 19*21?"},
    ]


def _responses_history_without_order_1_encrypted_reasoning() -> list[dict]:
    return [
        {"type": "message", "role": "user", "content": "What is 17*23?"},
        {"type": "reasoning", "summary": [{"type": "summary_text", "text": "multiply 17 by 23"}]},
        {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "391"}]},
        {"type": "message", "role": "user", "content": "And 19*21?"},
    ]


def _openai_then_mantle_order_router() -> Router:
    return Router(
        model_list=[
            {
                "model_name": "gpt-6-astra",
                "litellm_params": {"model": "openai/gpt-6-astra", "api_key": "openai-key", "order": 1},
                "model_info": {"id": "openai-order-1"},
            },
            {
                "model_name": "gpt-6-astra",
                "litellm_params": {
                    "model": "bedrock_mantle/openai.gpt-6-astra",
                    "api_key": "mantle-bearer-token",
                    "aws_region_name": "us-east-1",
                    "order": 2,
                },
                "model_info": {"id": "mantle-order-2"},
            },
        ],
        num_retries=0,
    )


def _two_openai_orders_on_one_encryption_boundary_router() -> Router:
    return Router(
        model_list=[
            {
                "model_name": "gpt-6-astra",
                "litellm_params": {
                    "model": "openai/gpt-6-astra",
                    "api_base": "https://api.openai.com/v1",
                    "api_key": "openai-key",
                    "order": 1,
                },
                "model_info": {"id": "openai-order-1"},
            },
            {
                "model_name": "gpt-6-astra",
                "litellm_params": {
                    "model": "openai/gpt-6-astra-mini",
                    "api_base": "https://api.openai.com/v1",
                    "api_key": "openai-key",
                    "order": 2,
                },
                "model_info": {"id": "openai-order-2"},
            },
        ],
        num_retries=0,
    )


@pytest.mark.asyncio
async def test_responses_order_fallback_hop_drops_the_encrypted_reasoning_the_next_provider_cannot_decrypt(
    respx_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(litellm, "disable_aiohttp_transport", True)
    openai_route: Final = respx_mock.post(_OPENAI_RESPONSES_URL).mock(
        return_value=httpx.Response(500, json=_OVERLOADED_UPSTREAM)
    )
    mantle_route: Final = respx_mock.post(_MANTLE_RESPONSES_URL).mock(
        return_value=httpx.Response(200, json=_completed_response_body("resp_mantle", "openai.gpt-6-astra", "399"))
    )

    response = await _openai_then_mantle_order_router().aresponses(
        model="gpt-6-astra", input=_responses_history_with_order_1_reasoning(), store=False
    )

    assert response._hidden_params["model_id"] == "mantle-order-2"
    assert json.loads(openai_route.calls.last.request.read())["input"] == _responses_history_with_order_1_reasoning()
    assert (
        json.loads(mantle_route.calls.last.request.read())["input"]
        == _responses_history_without_order_1_encrypted_reasoning()
    )


@pytest.mark.asyncio
async def test_responses_order_fallback_hop_keeps_the_encrypted_reasoning_the_same_boundary_can_decrypt(
    respx_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(litellm, "disable_aiohttp_transport", True)
    openai_route: Final = respx_mock.post(_OPENAI_RESPONSES_URL).mock(
        side_effect=[
            httpx.Response(500, json=_OVERLOADED_UPSTREAM),
            httpx.Response(200, json=_completed_response_body("resp_order2", "gpt-6-astra-mini", "399")),
        ]
    )

    response = await _two_openai_orders_on_one_encryption_boundary_router().aresponses(
        model="gpt-6-astra", input=_responses_history_with_order_1_reasoning(), store=False
    )

    assert response._hidden_params["model_id"] == "openai-order-2"
    assert [json.loads(call.request.read())["input"] for call in openai_route.calls] == [
        _responses_history_with_order_1_reasoning(),
        _responses_history_with_order_1_reasoning(),
    ]


def test_fallback_hop_reads_the_deployment_that_just_failed_from_the_metadata_bucket_it_writes():
    router: Final = _two_openai_orders_on_one_encryption_boundary_router()
    order_2: Final = router.get_deployment(model_id="openai-order-2").model_dump(exclude_none=True)
    hop_input: Final = _responses_history_with_order_1_reasoning()
    hop_kwargs: Final = {
        "model": "gpt-6-astra",
        "input": hop_input,
        "fallback_depth": 1,
        "metadata": {"model_info": {"id": "openai-order-1"}},
        "litellm_metadata": {"previous_models": [{"deployment_id": None}]},
    }

    router._update_kwargs_with_deployment(deployment=order_2, kwargs=hop_kwargs)

    assert hop_input == _responses_history_with_order_1_reasoning()
    assert hop_kwargs["metadata"]["model_info"]["id"] == "openai-order-2"


def test_check_non_standard_fallback_format():
    from litellm.router_utils.fallback_event_handlers import (
        check_non_standard_fallback_format,
    )

    # Standard formats
    assert check_non_standard_fallback_format([{"gpt-3.5-turbo": ["claude-3-haiku"]}]) == False
    assert check_non_standard_fallback_format([{"model": ["qwen-backup"]}]) == False
    assert check_non_standard_fallback_format([{"model": ["qwen-backup"], "region": ["us-east-1"]}]) == False

    # Non-standard formats
    assert check_non_standard_fallback_format([{"model": "qwen-backup"}]) == True
    assert (
        check_non_standard_fallback_format([{"model": "qwen-backup", "messages": [{"role": "user", "content": "hi"}]}])
        == True
    )
    assert check_non_standard_fallback_format([{"model": ["qwen-backup"], "api_key": "some-key"}]) == True


def _anthropic_oauth_policy_router(defaults: Mapping[str, object] | None = None, *, blocked: bool = False) -> Router:
    return Router(
        model_list=[
            {
                "model_name": "subscription",
                "litellm_params": {
                    "model": "anthropic/unit-test-model",
                    "use_anthropic_oauth": True,
                    "anthropic_auth_profile": "work",
                    "anthropic_token_dir": "/server/tokens",
                    "anthropic_oauth_compatibility": "claude_code",
                },
                "model_info": {"id": "subscription-id", "blocked": blocked},
            },
            {
                "model_name": "api",
                "litellm_params": {"model": "openai/unit-test-model", "api_key": "server-api-key"},
                "model_info": {"id": "api-id"},
            },
        ],
        model_group_alias={"subscription-alias": "subscription"},
        default_litellm_params=dict(defaults or {}),
        fallbacks=[{"subscription": ["api"]}],
        default_fallbacks=["api"],
        num_retries=0,
        enable_pre_call_checks=False,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("async_completion", [False, True], ids=["sync", "async"])
async def test_anthropic_oauth_router_http_payload_excludes_routing_controls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, async_completion: bool
) -> None:
    prompt: Final = "Return the word accepted"
    max_tokens: Final = 32
    synthetic_token: Final = "sk-ant-oat01-router-fixture"
    (tmp_path / "work.json").write_text(
        json.dumps({"access_token": synthetic_token, "expires_at": 3600.0, "scope": "user:inference"})
    )
    monkeypatch.setattr(oauth_policy, "AnthropicAuthenticator", partial(AnthropicAuthenticator, clock=lambda: 0.0))
    monkeypatch.setenv("LITELLM_LOCAL_ANTHROPIC_BETA_HEADERS", "true")
    requests: Final[SimpleQueue[httpx.Request]] = SimpleQueue()

    def respond(request: httpx.Request) -> httpx.Response:
        requests.put(request)
        return httpx.Response(
            200,
            json={
                "id": "msg_router_subscription",
                "type": "message",
                "role": "assistant",
                "model": "unit-test-model",
                "content": [{"type": "text", "text": "accepted"}],
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        )

    transport: Final = httpx.MockTransport(respond)
    sync_client: Final = HTTPHandler(client=httpx.Client(transport=transport))
    async_client: Final = AsyncHTTPHandler(transport=transport)

    def sync_http_client(params: Mapping[str, object] | None = None) -> HTTPHandler:
        return sync_client

    def async_http_client(llm_provider: litellm.LlmProviders) -> AsyncHTTPHandler:
        return async_client

    monkeypatch.setattr(anthropic_chat_handler, "get_httpx_client", sync_http_client)
    monkeypatch.setattr(anthropic_chat_handler, "get_async_httpx_client", async_http_client)
    router: Final = Router(
        model_list=[
            {
                "model_name": "subscription",
                "litellm_params": {
                    "model": "anthropic/unit-test-model",
                    "use_anthropic_oauth": True,
                    "anthropic_auth_profile": "work",
                    "anthropic_token_dir": str(tmp_path),
                    "anthropic_oauth_compatibility": "claude_code",
                },
                "model_info": {"id": "subscription-id"},
            }
        ],
        model_group_alias={"subscription-alias": "subscription"},
        num_retries=0,
        timeout=10.0,
    )
    try:
        response: Final = (
            await router.acompletion(
                model="subscription-alias", messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens
            )
            if async_completion
            else router.completion(
                model="subscription-alias", messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens
            )
        )
    finally:
        sync_client.close()
        await async_client.close()

    request: Final = requests.get_nowait()
    payload: Final = TypeAdapter(dict[str, JsonValue]).validate_json(request.content)
    assert requests.empty()
    assert request.headers["authorization"] == f"Bearer {synthetic_token}"
    assert "x-api-key" not in request.headers
    assert request.url.host == "api.anthropic.com"
    assert set(payload) == {"model", "messages", "max_tokens", "system"}
    assert payload["model"] == "unit-test-model"
    assert payload["messages"] == [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    assert payload["max_tokens"] == max_tokens
    assert isinstance(response, litellm.ModelResponse)
    assert response.choices[0].message.content == "accepted"


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize(
    "override",
    [
        {"use_anthropic_oauth": False},
        {"anthropic_auth_profile": "personal"},
        {"anthropic_token_dir": "/caller/tokens"},
        {"anthropic_oauth_compatibility": "caller-preset"},
        {"api_key": "caller-api-key"},
        {"api_base": "https://caller.invalid"},
        {"base_url": "https://caller.invalid"},
        {"custom_llm_provider": "openai"},
        {"extra_headers": {"AUTHORIZATION": "Bearer caller-token"}},
        {"headers": {"X-API-Key": "caller-api-key"}},
    ],
)
def test_anthropic_oauth_selected_deployment_rejects_caller_overrides(
    nested: bool, override: Mapping[str, object]
) -> None:
    router: Final = _anthropic_oauth_policy_router()
    deployment: Final = router.get_available_deployment(model="subscription")
    kwargs: Final = {"extra_body": dict(override)} if nested else dict(override)
    with pytest.raises(AnthropicError):
        router._update_kwargs_with_deployment(deployment=deployment, kwargs=kwargs)
    assert router.get_model_info(id="subscription-id")["litellm_params"]["anthropic_auth_profile"] == "work"


@pytest.mark.parametrize("function_name", [None, "_ageneric_api_call_with_fallbacks", "generic_api_call"])
def test_anthropic_oauth_selected_deployment_pins_policy_and_preserves_non_auth_headers(
    function_name: str | None,
) -> None:
    router: Final = _anthropic_oauth_policy_router(
        {"api_key": "default-api-key", "api_base": "https://default.invalid", "temperature": 0.4}
    )
    deployment: Final = router.get_available_deployment(model="subscription")
    body: Final = {"temperature": 0.2}
    headers: Final = {"X-Trace": "trace"}
    kwargs: Final = {"disable_fallbacks": False, "extra_headers": headers, "extra_body": body}
    router._update_kwargs_with_deployment(deployment=deployment, kwargs=kwargs, function_name=function_name)
    assert kwargs["use_anthropic_oauth"] is True
    assert kwargs["anthropic_auth_profile"] == deployment["litellm_params"]["anthropic_auth_profile"]
    assert kwargs["anthropic_token_dir"] == deployment["litellm_params"]["anthropic_token_dir"]
    assert kwargs["anthropic_oauth_compatibility"] == deployment["litellm_params"]["anthropic_oauth_compatibility"]
    assert kwargs["api_key"] is None
    assert kwargs["api_base"] is None
    assert kwargs["custom_llm_provider"] == "anthropic"
    assert kwargs["disable_fallbacks"] is True
    assert kwargs["fallbacks"] is None
    assert kwargs["context_window_fallbacks"] is None
    assert kwargs["content_policy_fallbacks"] is None
    assert kwargs["extra_headers"] == headers
    assert kwargs["extra_body"] == body
    assert kwargs["temperature"] == 0.4
    assert headers == {"X-Trace": "trace"}
    assert body == {"temperature": 0.2}
    assert router.get_model_info(id="subscription-id")["model_info"]["id"] == "subscription-id"


@pytest.mark.parametrize("managed", [False, True])
def test_anthropic_oauth_spend_attribution_cannot_be_supplied_by_caller(managed: bool) -> None:
    router: Final = _anthropic_oauth_policy_router()
    deployment: Final = router.get_available_deployment(model="subscription" if managed else "api")
    kwargs: Final = {
        "metadata": {"used_server_oauth_token": not managed, "anthropic_auth_profile": "caller"},
        "litellm_metadata": {
            "used_server_oauth_token": not managed,
            "used_client_oauth_token": True,
            "anthropic_auth_profile": "caller",
        },
    }
    router._update_kwargs_with_deployment(deployment=deployment, kwargs=kwargs)
    for bucket_name in ("metadata", "litellm_metadata"):
        assert kwargs[bucket_name]["used_server_oauth_token"] is managed
        assert kwargs[bucket_name]["anthropic_auth_profile"] == ("work" if managed else None)
        if managed:
            assert kwargs[bucket_name]["used_client_oauth_token"] is False


@pytest.mark.parametrize("nested", [False, True])
def test_anthropic_oauth_cannot_be_enabled_on_api_deployment(nested: bool) -> None:
    router: Final = _anthropic_oauth_policy_router()
    deployment: Final = router.get_available_deployment(model="api")
    override: Final = {"use_anthropic_oauth": True, "anthropic_auth_profile": "work"}
    kwargs: Final = {"extra_body": override} if nested else override
    with pytest.raises(AnthropicError):
        router._update_kwargs_with_deployment(deployment=deployment, kwargs=kwargs)


def test_anthropic_oauth_policy_preserves_api_dynamic_credentials_and_body() -> None:
    router: Final = _anthropic_oauth_policy_router()
    deployment: Final = router.get_available_deployment(model="api")
    body: Final = {"temperature": 0.2}
    kwargs: Final = {
        "model": "api",
        "api_key": "caller-api-key",
        "extra_body": body,
        "metadata": {"model_group": "api"},
    }
    router._update_kwargs_with_deployment(deployment=deployment, kwargs=kwargs)
    assert kwargs["api_key"] == "caller-api-key"
    assert kwargs["extra_body"] is body
    assert kwargs["model_info"]["original_model_id"] == "api-id"


@pytest.mark.parametrize("model", ["subscription", "subscription-alias", "subscription-id"])
@pytest.mark.parametrize("fallbacks", [["api"], [{"model": "api", "use_anthropic_oauth": False}], None])
@pytest.mark.asyncio
async def test_anthropic_oauth_caller_cannot_enable_cross_provider_fallback(
    model: str, fallbacks: list[object] | None
) -> None:
    router: Final = _anthropic_oauth_policy_router()
    failure: Final = RuntimeError("subscription unavailable")

    async def provider_call(**kwargs: object) -> object:
        if kwargs["model"] == "api":
            return litellm.ModelResponse()
        raise failure

    request: Final = {"fallbacks": fallbacks} if fallbacks is not None else {}
    with pytest.raises(RuntimeError) as raised:
        await router.async_function_with_fallbacks(
            model=model, original_function=provider_call, disable_fallbacks=False, **request
        )
    assert raised.value is failure


@pytest.mark.asyncio
async def test_anthropic_oauth_generic_dispatch_carries_server_policy() -> None:
    router: Final = _anthropic_oauth_policy_router()

    async def provider_call(**kwargs: object) -> Mapping[str, object]:
        return kwargs

    result: Final = await router._ageneric_api_call_with_fallbacks_helper(
        model="subscription",
        original_generic_function=provider_call,
        disable_fallbacks=False,
        extra_headers={"X-Trace": "trace"},
    )
    assert result["model"] == "anthropic/unit-test-model"
    assert result["use_anthropic_oauth"] is True
    assert result["anthropic_auth_profile"] == "work"
    assert result["api_key"] is None
    assert result["disable_fallbacks"] is True
    assert result["extra_headers"] == {"X-Trace": "trace"}


@pytest.mark.asyncio
async def test_anthropic_oauth_missing_deployment_cannot_use_generic_passthrough() -> None:
    router: Final = _anthropic_oauth_policy_router(blocked=True)

    async def provider_call(**kwargs: object) -> Mapping[str, object]:
        raise AssertionError("A managed deployment failure must not dispatch generic passthrough")

    with pytest.raises(RouterRateLimitError):
        await router._ageneric_api_call_with_fallbacks_helper(
            model="subscription", original_generic_function=provider_call, passthrough_on_no_deployment=True
        )


def test_anthropic_oauth_default_fallback_cannot_enter_subscription() -> None:
    router: Final = _anthropic_oauth_policy_router()
    router.fallbacks = [{"*": ["subscription"]}]
    with pytest.raises(litellm.BadRequestError, match="Default fallback cannot select"):
        router.get_available_deployment(model="unconfigured-model")


def test_anthropic_oauth_deployment_cannot_mirror_into_silent_provider() -> None:
    with pytest.raises(ValueError, match="silent model"):
        Router._deployment_params_with_request_reasoning_override(
            {"use_anthropic_oauth": True, "silent_model": "api"}, {}
        )


async def _select_mixed_anthropic_oauth_group(
    router: Router, async_selection: bool, request_kwargs: Mapping[str, object]
) -> None:
    request: Final = dict(request_kwargs)
    if async_selection:
        await router.async_get_available_deployment(model="mixed", request_kwargs=request)
        return
    router.get_available_deployment(model="mixed", request_kwargs=request)


@pytest.mark.parametrize("async_selection", [False, True])
@pytest.mark.parametrize(
    "second_params",
    [
        {"model": "anthropic/unit-test-model", "api_key": "server-api-key"},
        {"model": "anthropic/unit-test-model", "use_anthropic_oauth": True, "anthropic_auth_profile": "personal"},
        {"model": "anthropic/unit-test-model", "use_anthropic_oauth": True, "anthropic_token_dir": "/other/tokens"},
    ],
)
@pytest.mark.asyncio
async def test_anthropic_oauth_model_group_rejects_mixed_accounts_before_selection(
    async_selection: bool, second_params: Mapping[str, object]
) -> None:
    router: Final = Router(
        model_list=[
            {
                "model_name": "mixed",
                "litellm_params": {"model": "anthropic/unit-test-model", "use_anthropic_oauth": True},
            },
            {"model_name": "mixed", "litellm_params": dict(second_params)},
        ],
        num_retries=0,
        enable_pre_call_checks=False,
    )
    with pytest.raises(ValueError, match="Anthropic OAuth model group"):
        await _select_mixed_anthropic_oauth_group(router, async_selection, {})


@pytest.mark.parametrize("async_selection", [False, True])
@pytest.mark.parametrize("managed_second", [False, True])
@pytest.mark.asyncio
async def test_anthropic_oauth_access_groups_cannot_hide_mixed_deployment_policy(
    async_selection: bool, managed_second: bool
) -> None:
    router: Final = Router(
        model_list=[
            {
                "model_name": "mixed",
                "litellm_params": {
                    "model": "anthropic/unit-test-model",
                    "use_anthropic_oauth": True,
                    "anthropic_auth_profile": "private",
                },
                "model_info": {"id": "private-profile", "access_groups": ["private-access"]},
            },
            {
                "model_name": "mixed",
                "litellm_params": {
                    "model": "anthropic/unit-test-model",
                    "use_anthropic_oauth": managed_second,
                    "anthropic_auth_profile": "public" if managed_second else None,
                    "api_key": None if managed_second else "api-key",
                },
                "model_info": {"id": "public-profile", "access_groups": ["public-access"]},
            },
        ],
        num_retries=0,
        enable_pre_call_checks=False,
    )
    request: Final = {"metadata": {"user_api_key_auth": UserAPIKeyAuth(models=["public-access"])}}
    visible: Final = router._filter_deployments_by_model_access_groups(
        model="mixed",
        healthy_deployments=router.get_model_list(model_name="mixed"),
        request_kwargs=request,
        request_team_id=None,
    )
    assert tuple(row["model_info"]["id"] for row in visible) == ("public-profile",)
    with pytest.raises(ValueError, match="Anthropic OAuth model group"):
        await _select_mixed_anthropic_oauth_group(router, async_selection, request)
