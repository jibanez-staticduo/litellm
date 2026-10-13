"""Exercise the configured callback through LiteLLM's leaf-method dispatcher."""

import json
from unittest.mock import patch

import pytest

import litellm
from litellm.caching.dual_cache import DualCache
from litellm.proxy._types import UserAPIKeyAuth
from litellm.proxy.common_utils.callback_utils import initialize_callbacks_on_proxy
from litellm.proxy.hooks import portable_codex_agents as configured_module
from litellm.proxy.utils import ProxyLogging
from staticduo_litellm.compatibility.hooks import PortableCodexAgents

from tests.unit.proxy.hooks.test_portable_codex_agents import MemoryStore, call, tools


@pytest.mark.asyncio
async def test_configured_callback_dispatches_request_and_completed_stream(tmp_path):
    callback_path = "litellm.proxy.hooks.portable_codex_agents.portable_codex_agents"
    configured = PortableCodexAgents(frozenset({"portable"}), MemoryStore())
    assert type(configured_module.portable_codex_agents) is PortableCodexAgents
    with patch.object(litellm, "callbacks", []), patch.object(configured_module, "portable_codex_agents", configured):
        initialize_callbacks_on_proxy(
            value=[callback_path],
            premium_user=False,
            config_file_path=str(tmp_path / "config.yaml"),
            litellm_settings={},
        )
        callback = litellm.callbacks[0]
        assert type(callback) is PortableCodexAgents
        dispatcher = ProxyLogging(user_api_key_cache=DualCache())
        auth = UserAPIKeyAuth(api_key="fixture-key", request_route="/v1/responses")
        request = await dispatcher.pre_call_hook(
            auth,
            {"model": "portable", "tools": tools(), "input": [], "client_metadata": {"thread_id": "fixture"}},
            "aresponses",
        )
        assert request["tools"][0]["name"] == "portable_collaboration"
        assert request["litellm_metadata"]["litellm_portable_codex_agents"]["owner"]

        async def upstream():
            yield {"type": "response.output_item.done", "item": call()}
            yield {"type": "response.completed", "response": {"output": [call()]}}

        result = [
            chunk async for chunk in dispatcher.async_post_call_streaming_iterator_hook(upstream(), auth, request)
        ]
        assert result[0]["item"]["namespace"] == "collaboration"
        completed = result[1]["response"]["output"][0]
        assert completed["encrypted_function_args"] == []
        assert json.loads(completed["arguments"])["message"] == "Read the fixture"
