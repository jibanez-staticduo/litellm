import json

import pytest
from unittest.mock import AsyncMock, Mock, patch

from litellm import Router
from litellm.llms.chatgpt.chat.transformation import ChatGPTConfig
from litellm.llms.chatgpt.common_utils import InteractiveAuthError
from litellm.llms.chatgpt.responses.transformation import ChatGPTResponsesAPIConfig

from litellm.router_utils.fallback_event_handlers import (
    get_fallback_model_group,
    run_async_fallback,
    validate_chatgpt_model_group_profiles,
)


class StreamingWrapper:
    def __init__(self):
        self._hidden_params = {"additional_headers": {}}


class FakeRouter:
    def log_retry(self, kwargs, e):
        return kwargs

    async def async_function_with_fallbacks(self, *args, **kwargs):
        return StreamingWrapper()

    def get_model_list(self, model_name):
        return []


class AlwaysFailRouter:
    def log_retry(self, kwargs, e):
        return kwargs

    async def async_function_with_fallbacks(self, *args, **kwargs):
        raise RuntimeError("fallback model also failed")

    def get_model_list(self, model_name):
        return []


@pytest.mark.asyncio
async def test_run_async_fallback_adds_errors_when_opted_in():
    response = await run_async_fallback(
        litellm_router=FakeRouter(),
        fallback_model_group=["fallback-model"],
        original_model_group="primary-model",
        original_exception=RuntimeError("upstream limited request"),
        max_fallbacks=3,
        fallback_depth=0,
        include_fallback_errors=True,
    )

    additional_headers = response._hidden_params["additional_headers"]
    assert additional_headers["x-litellm-attempted-fallbacks"] == 1
    assert json.loads(additional_headers["x-litellm-fallback-errors"]) == [
        {
            "message": "upstream limited request",
            "type": "RuntimeError",
            "param": None,
            "code": None,
        }
    ]


@pytest.mark.asyncio
async def test_run_async_fallback_omits_errors_without_opt_in():
    response = await run_async_fallback(
        litellm_router=FakeRouter(),
        fallback_model_group=["fallback-model"],
        original_model_group="primary-model",
        original_exception=RuntimeError("upstream limited request"),
        max_fallbacks=3,
        fallback_depth=0,
    )

    additional_headers = response._hidden_params["additional_headers"]
    assert additional_headers["x-litellm-attempted-fallbacks"] == 1
    assert "x-litellm-fallback-errors" not in additional_headers


@pytest.mark.asyncio
async def test_run_async_fallback_raises_when_all_fallbacks_fail():
    with pytest.raises(RuntimeError, match="fallback model also failed"):
        await run_async_fallback(
            litellm_router=AlwaysFailRouter(),
            fallback_model_group=["fallback-model"],
            original_model_group="primary-model",
            original_exception=RuntimeError("original request failed"),
            max_fallbacks=3,
            fallback_depth=0,
            include_fallback_errors=True,
        )


class RecordingRouter:
    def __init__(self):
        self.received_kwargs = None

    def log_retry(self, kwargs, e):
        return kwargs

    async def async_function_with_fallbacks(self, *args, **kwargs):
        self.received_kwargs = kwargs
        return StreamingWrapper()

    def get_model_list(self, model_name):
        return []


@pytest.mark.asyncio
async def test_run_async_fallback_forwards_include_fallback_errors_to_nested_call():
    """A nested fallback (multi-hop) must keep collecting errors, so the opt-in
    flag has to reach the nested async_function_with_fallbacks call."""
    router = RecordingRouter()
    await run_async_fallback(
        litellm_router=router,
        fallback_model_group=["fallback-model"],
        original_model_group="primary-model",
        original_exception=RuntimeError("upstream limited request"),
        max_fallbacks=3,
        fallback_depth=0,
        include_fallback_errors=True,
    )

    assert router.received_kwargs.get("include_fallback_errors") is True


@pytest.mark.asyncio
async def test_run_async_fallback_does_not_forward_flag_without_opt_in():
    router = RecordingRouter()
    await run_async_fallback(
        litellm_router=router,
        fallback_model_group=["fallback-model"],
        original_model_group="primary-model",
        original_exception=RuntimeError("upstream limited request"),
        max_fallbacks=3,
        fallback_depth=0,
    )

    assert "include_fallback_errors" not in router.received_kwargs


@pytest.mark.asyncio
async def test_run_async_fallback_skips_original_model_group():
    response = await run_async_fallback(
        litellm_router=FakeRouter(),
        fallback_model_group=["primary-model", "fallback-model"],
        original_model_group="primary-model",
        original_exception=RuntimeError("original failed"),
        max_fallbacks=3,
        fallback_depth=0,
    )

    assert response._hidden_params["additional_headers"]["x-litellm-attempted-fallbacks"] == 1


@pytest.mark.asyncio
async def test_run_async_fallback_preserves_caller_and_logical_identity():
    router = RecordingRouter()
    metadata = {"model_group": "primary-model", "request_id": "safe-id"}
    request_kwargs = {"model": "primary-model", "metadata": metadata}

    await run_async_fallback(
        litellm_router=router,
        fallback_model_group=["fallback-model"],
        original_model_group="primary-model",
        original_exception=RuntimeError("failed"),
        max_fallbacks=3,
        fallback_depth=0,
        **request_kwargs,
    )

    assert request_kwargs == {"model": "primary-model", "metadata": metadata}
    assert router.received_kwargs["model"] == "fallback-model"
    assert router.received_kwargs["metadata"] == {
        "model_group": "fallback-model",
        "request_id": "safe-id",
        "logical_model_group": "primary-model",
        "original_requested_model": "primary-model",
        "fallback_source_model_group": "primary-model",
        "fallback_attempt": 1,
        "fallback_reason": "RuntimeError",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "source_profile,target_profile,expected_model",
    [(None, "account2", None), ("account2", None, None), ("same", "same", "account2-model")],
)
async def test_run_async_fallback_cross_profile_is_denied(source_profile, target_profile, expected_model):
    class ProfileRouter(RecordingRouter):
        def get_model_list(self, model_name):
            profile = source_profile if model_name == "regular-model" else target_profile
            params = {"model": "chatgpt/gpt-5.6-sol"}
            if profile is not None:
                params["chatgpt_auth_profile"] = profile
            return [{"litellm_params": params}]

    router = ProfileRouter()
    if expected_model:
        await run_async_fallback(
            litellm_router=router,
            fallback_model_group=["account2-model"],
            original_model_group="regular-model",
            original_exception=RuntimeError("failed"),
            max_fallbacks=3,
            fallback_depth=0,
        )
    else:
        with pytest.raises(RuntimeError, match="failed"):
            await run_async_fallback(
                litellm_router=router,
                fallback_model_group=["account2-model"],
                original_model_group="regular-model",
                original_exception=RuntimeError("failed"),
                max_fallbacks=3,
                fallback_depth=0,
            )

    received_model = None if router.received_kwargs is None else router.received_kwargs["model"]
    assert received_model == expected_model


@pytest.mark.asyncio
async def test_run_async_fallback_preserves_non_copyable_values_by_identity():
    class NonCopyable:
        def __deepcopy__(self, memo):
            raise AssertionError("must not deepcopy opaque request values")

    opaque = NonCopyable()
    router = RecordingRouter()
    await run_async_fallback(
        litellm_router=router,
        fallback_model_group=["fallback-model"],
        original_model_group="primary-model",
        original_exception=RuntimeError("failed"),
        max_fallbacks=3,
        fallback_depth=0,
        client=opaque,
    )

    assert router.received_kwargs["client"] is opaque


def test_get_fallback_model_group_does_not_mutate_fallbacks():
    """A string fallback must be resolved without mutating the caller's
    fallbacks list, which is the live router config shared across requests."""
    fallbacks = [{"gpt-3.5-turbo": ["claude-3-haiku"]}, "gpt-4o-mini"]

    fallback_model_group, _ = get_fallback_model_group(fallbacks=fallbacks, model_group="unmatched-model")

    assert fallback_model_group == ["gpt-4o-mini"]
    assert fallbacks == [{"gpt-3.5-turbo": ["claude-3-haiku"]}, "gpt-4o-mini"]


def test_mixed_chatgpt_model_group_fails_closed_before_selection():
    deployments = [
        {"litellm_params": {"model": "chatgpt/gpt-5.6-sol"}},
        {
            "litellm_params": {
                "model": "chatgpt/gpt-5.6-sol",
                "chatgpt_auth_profile": "account2",
            }
        },
    ]

    with pytest.raises(ValueError, match="mixed authentication profiles"):
        validate_chatgpt_model_group_profiles(deployments, "regular-model")


def _mixed_profile_router():
    router = Router.__new__(Router)
    deployments = [
        {"litellm_params": {"model": "chatgpt/gpt-5.6-sol"}},
        {
            "litellm_params": {
                "model": "chatgpt/gpt-5.6-sol",
                "chatgpt_auth_profile": "account2",
            }
        },
    ]
    router._common_checks_available_deployment = Mock(return_value=("mixed", deployments))
    router.routing_strategy = "simple-shuffle"
    router.async_pre_routing_hook = AsyncMock(return_value=None)
    router._get_routing_context = Mock(return_value=("simple-shuffle", None))
    router.async_get_healthy_deployments = AsyncMock(return_value=deployments)
    return router


def test_router_sync_mixed_chatgpt_group_fails_before_selection():
    with pytest.raises(ValueError, match="mixed authentication profiles"):
        _mixed_profile_router().get_available_deployment(model="mixed", request_kwargs={})


@pytest.mark.asyncio
async def test_router_async_mixed_chatgpt_group_fails_before_selection():
    with pytest.raises(ValueError, match="mixed authentication profiles"):
        await _mixed_profile_router().async_get_available_deployment(model="mixed", request_kwargs={})


def test_router_sync_selected_log_has_authoritative_profile_and_deployment(caplog):
    router = Router.__new__(Router)
    deployment = {
        "litellm_params": {"model": "chatgpt/gpt-5.6-sol"},
        "model_info": {"id": "deadbeefcafebabe"},
    }
    router._common_checks_available_deployment = Mock(return_value=("regular", [deployment]))
    router._filter_health_check_unhealthy_deployments = Mock(return_value=[deployment])
    router._filter_cooldown_deployments = Mock(return_value=[deployment])
    router._filter_blocked_deployments = Mock(return_value=[deployment])
    router.cooldown_cache = Mock()
    router.get_model_ids = Mock(return_value=[])
    router.enable_health_check_routing = False
    router.allowed_fails_policy = None
    router.enable_pre_call_checks = False
    router.routing_strategy = "simple-shuffle"
    router._get_routing_context = Mock(return_value=("simple-shuffle", None))
    with caplog.at_level("INFO", logger="LiteLLM Router"):
        router.get_available_deployment(model="regular", request_kwargs={"metadata": {"request_id": "raw-secret-id"}})
    event = next(record.message for record in caplog.records if "router_selected" in record.message)
    assert "selected_profile=default" in event
    assert "deployment_prefix=deadbeef" in event
    assert "raw-secret-id" not in event


@pytest.mark.parametrize("surface", ["chat", "responses"])
def test_router_interactive_auth_error_is_not_retried_for_chat_or_responses(surface):
    router = Router.__new__(Router)
    acquisition = Mock(side_effect=InteractiveAuthError(message="safe auth failure", status_code=401))
    with patch("litellm.llms.chatgpt.authenticator.Authenticator.get_access_token", acquisition):
        with pytest.raises(Exception) as caught:
            if surface == "chat":
                ChatGPTConfig()._get_openai_compatible_provider_info(
                    model="gpt-5.6-sol",
                    api_base=None,
                    api_key=None,
                    custom_llm_provider="chatgpt",
                )
            else:
                ChatGPTResponsesAPIConfig().validate_environment(headers={}, model="gpt-5.6-sol", litellm_params=None)

    assert getattr(caught.value, "is_non_retryable_interactive_auth", False) is True
    with pytest.raises(type(caught.value)):
        router.should_retry_this_error(
            error=caught.value,
            healthy_deployments=[{}, {}],
            all_deployments=[{}, {}],
            regular_fallbacks=["fallback"],
        )
    assert acquisition.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["chat", "responses"])
async def test_async_function_with_retries_interactive_auth_overrides_retry_policy(surface):
    router = Router.__new__(Router)
    router.fallbacks = [{"chatgpt-group": ["fallback"]}]
    router.context_window_fallbacks = []
    router.content_policy_fallbacks = []
    router.model_group_retry_policy = {"chatgpt-group": {"AuthenticationErrorRetries": 3}}
    router.retry_policy = None
    router.num_retries = 3
    router.get_model_list = Mock(return_value=[{}, {}])
    acquisition = Mock(side_effect=InteractiveAuthError(message="safe auth failure", status_code=401))

    def provider_call(**kwargs):
        if surface == "chat":
            return ChatGPTConfig()._get_openai_compatible_provider_info(
                model="gpt-5.6-sol",
                api_base=None,
                api_key=None,
                custom_llm_provider="chatgpt",
            )
        return ChatGPTResponsesAPIConfig().validate_environment(headers={}, model="gpt-5.6-sol", litellm_params=None)

    with patch("litellm.llms.chatgpt.authenticator.Authenticator.get_access_token", acquisition):
        with pytest.raises(Exception) as caught:
            await router.async_function_with_retries(
                original_function=provider_call,
                model="chatgpt-group",
                num_retries=3,
                metadata={"model_group": "chatgpt-group"},
            )

    assert getattr(caught.value, "is_non_retryable_interactive_auth", False) is True
    assert acquisition.call_count == 1


@pytest.mark.asyncio
async def test_fallback_dict_cannot_spoof_immutable_identity():
    router = RecordingRouter()
    await run_async_fallback(
        litellm_router=router,
        fallback_model_group=[
            {
                "model": "fallback-model",
                "logical_model_group": "spoofed",
                "original_requested_model": "spoofed",
            }
        ],
        original_model_group="primary-model",
        original_exception=RuntimeError("failed"),
        max_fallbacks=3,
        fallback_depth=0,
    )

    assert router.received_kwargs["logical_model_group"] == "primary-model"
    assert router.received_kwargs["original_requested_model"] == "primary-model"
