"""
Tests for AI Usage Chat module.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from litellm.constants import DEFAULT_COMPETITOR_DISCOVERY_MODEL
from litellm.proxy.management_endpoints.usage_endpoints import ai_usage_chat
from litellm.proxy.management_endpoints.usage_endpoints.ai_usage_chat import (
    TOOL_HANDLERS,
    TOOLS_ADMIN,
    TOOLS_BASE,
    USAGE_AI_MODEL_ENV,
    _create_completion,
    _build_system_prompt,
    _summarise_entity_data,
    _resolve_default_model,
    _summarise_usage_data,
    stream_usage_ai_chat,
)


@pytest.fixture(autouse=True)
def _unit_tests_start_without_proxy_router():
    """Keep the module-level fallback deterministic; router preference is tested explicitly."""
    with patch(  # test-quality-ok: process-global routing seam
        "litellm.proxy.proxy_server.llm_router",
        None,
    ):
        yield


SAMPLE_AGGREGATED_RESPONSE = {
    "results": [
        {
            "date": "2025-01-15",
            "metrics": {
                "spend": 50.25,
                "prompt_tokens": 20000,
                "completion_tokens": 10000,
                "total_tokens": 30000,
                "api_requests": 500,
                "successful_requests": 480,
                "failed_requests": 20,
                "cache_read_input_tokens": 0,
                "cache_creation_input_tokens": 0,
            },
            "breakdown": {
                "models": {
                    "gpt-4": {
                        "metrics": {
                            "spend": 40.0,
                            "api_requests": 300,
                            "total_tokens": 25000,
                        },
                        "metadata": {},
                        "api_key_breakdown": {},
                    },
                },
                "providers": {
                    "openai": {
                        "metrics": {"spend": 50.25, "api_requests": 500},
                        "metadata": {},
                        "api_key_breakdown": {},
                    },
                },
                "api_keys": {
                    "sk-test123": {
                        "metrics": {"spend": 50.25},
                        "metadata": {"key_alias": "Production Key"},
                    },
                },
                "model_groups": {},
                "mcp_servers": {},
                "entities": {},
            },
        },
    ],
    "metadata": {
        "total_spend": 50.25,
        "total_api_requests": 500,
        "total_successful_requests": 480,
        "total_failed_requests": 20,
        "total_tokens": 30000,
    },
}

SAMPLE_TEAM_RESPONSE = {
    "results": [
        {
            "date": "2025-01-15",
            "metrics": {"spend": 100.0, "api_requests": 1000, "total_tokens": 50000},
            "breakdown": {
                "entities": {
                    "team-1": {
                        "metrics": {
                            "spend": 60.0,
                            "api_requests": 600,
                            "total_tokens": 30000,
                        },
                        "metadata": {"alias": "Engineering"},
                        "api_key_breakdown": {},
                    },
                    "team-2": {
                        "metrics": {
                            "spend": 40.0,
                            "api_requests": 400,
                            "total_tokens": 20000,
                        },
                        "metadata": {"alias": "Marketing"},
                        "api_key_breakdown": {},
                    },
                },
                "models": {},
                "providers": {},
                "api_keys": {},
                "model_groups": {},
                "mcp_servers": {},
            },
        },
    ],
    "metadata": {"total_spend": 100.0, "total_api_requests": 1000},
}


class TestToolSchemas:
    def test_admin_tools_include_all(self):
        assert len(TOOLS_ADMIN) == 3
        names = {t["function"]["name"] for t in TOOLS_ADMIN}
        assert "get_usage_data" in names
        assert "get_team_usage_data" in names
        assert "get_tag_usage_data" in names

    def test_base_tools_restricted_to_usage_only(self):
        assert len(TOOLS_BASE) == 1
        assert TOOLS_BASE[0]["function"]["name"] == "get_usage_data"

    def test_admin_prompt_mentions_all_tools(self):
        prompt = _build_system_prompt(is_admin=True)
        assert "get_usage_data" in prompt
        assert "get_team_usage_data" in prompt
        assert "get_tag_usage_data" in prompt

    def test_non_admin_prompt_only_mentions_usage_tool(self):
        prompt = _build_system_prompt(is_admin=False)
        assert "get_usage_data" in prompt
        assert "get_team_usage_data" not in prompt
        assert "get_tag_usage_data" not in prompt

    def test_system_prompt_includes_todays_date(self):
        from datetime import date

        prompt = _build_system_prompt(is_admin=True)
        assert date.today().isoformat() in prompt


class TestSummariseUsageData:
    def test_summarise_includes_totals(self):
        summary = _summarise_usage_data(SAMPLE_AGGREGATED_RESPONSE)
        assert "$50.25" in summary
        assert "500" in summary

    def test_summarise_includes_models(self):
        summary = _summarise_usage_data(SAMPLE_AGGREGATED_RESPONSE)
        assert "gpt-4" in summary

    def test_summarise_includes_providers(self):
        summary = _summarise_usage_data(SAMPLE_AGGREGATED_RESPONSE)
        assert "openai" in summary

    def test_summarise_handles_empty_data(self):
        empty = {"results": [], "metadata": {}}
        summary = _summarise_usage_data(empty)
        assert "no data" in summary.lower()


class TestSummariseEntityData:
    def test_team_summary_includes_teams(self):
        summary = _summarise_entity_data(SAMPLE_TEAM_RESPONSE, "Team")
        assert "Engineering" in summary
        assert "Marketing" in summary
        assert "$60.0" in summary
        assert "$40.0" in summary

    def test_team_summary_empty(self):
        empty = {"results": [], "metadata": {}}
        summary = _summarise_entity_data(empty, "Team")
        assert "No Team usage data" in summary


class TestStreamUsageAiChat:
    @pytest.mark.asyncio
    async def test_stream_emits_status_events(self):
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "get_usage_data"
        mock_tool_call.function.arguments = json.dumps(
            {
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
            }
        )

        mock_first_response = MagicMock()
        mock_first_response.choices = [MagicMock()]
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_first_response.choices[0].message.model_dump.return_value = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "get_usage_data",
                        "arguments": '{"start_date":"2025-01-01","end_date":"2025-01-31"}',
                    },
                }
            ],
        }

        async def mock_stream():
            chunk = MagicMock()
            chunk.choices = [MagicMock()]
            chunk.choices[0].delta.content = "Total spend is $50.25"
            yield chunk

        with (
            patch("litellm.proxy.management_endpoints.usage_endpoints.ai_usage_chat.litellm") as mock_litellm,
            patch(
                "litellm.proxy.management_endpoints.usage_endpoints.ai_usage_chat._fetch_usage_data",
                new_callable=AsyncMock,
            ) as mock_fetch,
        ):
            mock_litellm.acompletion = AsyncMock(
                side_effect=[
                    mock_first_response,
                    mock_stream(),
                ]
            )
            mock_fetch.return_value = SAMPLE_AGGREGATED_RESPONSE

            events = []
            async for event in stream_usage_ai_chat(
                messages=[{"role": "user", "content": "What is my total spend?"}],
                model="gpt-4o-mini",
                user_id="user-123",
                is_admin=True,
            ):
                events.append(json.loads(event.replace("data: ", "").strip()))

            status_events = [e for e in events if e["type"] == "status"]
            tool_call_events = [e for e in events if e["type"] == "tool_call"]
            chunk_events = [e for e in events if e["type"] == "chunk"]
            done_events = [e for e in events if e["type"] == "done"]

            assert len(status_events) >= 1
            assert "Thinking" in status_events[0]["message"]
            assert len(tool_call_events) >= 1
            assert tool_call_events[0]["tool_name"] == "get_usage_data"
            assert tool_call_events[0]["status"] in ("running", "complete")
            assert len(chunk_events) >= 1
            assert len(done_events) == 1

    @pytest.mark.asyncio
    async def test_stream_handles_team_tool(self):
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_team"
        mock_tool_call.function.name = "get_team_usage_data"
        mock_tool_call.function.arguments = json.dumps(
            {
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
            }
        )

        mock_first_response = MagicMock()
        mock_first_response.choices = [MagicMock()]
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_first_response.choices[0].message.model_dump.return_value = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_team",
                    "type": "function",
                    "function": {
                        "name": "get_team_usage_data",
                        "arguments": '{"start_date":"2025-01-01","end_date":"2025-01-31"}',
                    },
                }
            ],
        }

        async def mock_stream():
            chunk = MagicMock()
            chunk.choices = [MagicMock()]
            chunk.choices[0].delta.content = "Engineering is the top team."
            yield chunk

        with (
            patch("litellm.proxy.management_endpoints.usage_endpoints.ai_usage_chat.litellm") as mock_litellm,
            patch(
                "litellm.proxy.management_endpoints.usage_endpoints.ai_usage_chat._fetch_team_usage_data",
                new_callable=AsyncMock,
            ) as mock_fetch,
        ):
            mock_litellm.acompletion = AsyncMock(
                side_effect=[
                    mock_first_response,
                    mock_stream(),
                ]
            )
            mock_fetch.return_value = SAMPLE_TEAM_RESPONSE

            events = []
            async for event in stream_usage_ai_chat(
                messages=[{"role": "user", "content": "Which team spends the most?"}],
                model="gpt-4o-mini",
                is_admin=True,
            ):
                events.append(json.loads(event.replace("data: ", "").strip()))

            chunk_events = [e for e in events if e["type"] == "chunk"]
            assert len(chunk_events) >= 1
            assert "Engineering" in chunk_events[0]["content"]

    @pytest.mark.asyncio
    async def test_stream_handles_error(self):
        with patch("litellm.proxy.management_endpoints.usage_endpoints.ai_usage_chat.litellm") as mock_litellm:
            mock_litellm.acompletion = AsyncMock(side_effect=Exception("LLM error"))

            events = []
            async for event in stream_usage_ai_chat(
                messages=[{"role": "user", "content": "test"}],
            ):
                events.append(json.loads(event.replace("data: ", "").strip()))

            error_events = [e for e in events if e["type"] == "error"]
            assert len(error_events) == 1
            assert "internal error" in error_events[0]["message"].lower()

    @pytest.mark.asyncio
    async def test_non_admin_enforces_user_id(self):
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_456"
        mock_tool_call.function.name = "get_usage_data"
        mock_tool_call.function.arguments = json.dumps(
            {
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "user_id": "other-user",
            }
        )

        mock_first_response = MagicMock()
        mock_first_response.choices = [MagicMock()]
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_first_response.choices[0].message.model_dump.return_value = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_456",
                    "type": "function",
                    "function": {
                        "name": "get_usage_data",
                        "arguments": '{"start_date":"2025-01-01","end_date":"2025-01-31","user_id":"other-user"}',
                    },
                }
            ],
        }

        async def mock_stream():
            chunk = MagicMock()
            chunk.choices = [MagicMock()]
            chunk.choices[0].delta.content = "Data."
            yield chunk

        mock_fetch = AsyncMock(return_value=SAMPLE_AGGREGATED_RESPONSE)

        with (
            patch("litellm.proxy.management_endpoints.usage_endpoints.ai_usage_chat.litellm") as mock_litellm,
            patch.dict(
                "litellm.proxy.management_endpoints.usage_endpoints.ai_usage_chat.TOOL_HANDLERS",
                {
                    "get_usage_data": {
                        "fetch": mock_fetch,
                        "summarise": _summarise_usage_data,
                        "label": "global usage data",
                    }
                },
            ),
        ):
            mock_litellm.acompletion = AsyncMock(
                side_effect=[
                    mock_first_response,
                    mock_stream(),
                ]
            )

            events = []
            async for event in stream_usage_ai_chat(
                messages=[{"role": "user", "content": "Show data"}],
                model="gpt-4o-mini",
                user_id="my-user-id",
                is_admin=False,
            ):
                events.append(event)

            mock_fetch.assert_called_once_with(
                start_date="2025-01-01",
                end_date="2025-01-31",
                user_id="my-user-id",
            )


class TestUsageAiChatServiceAccountGuard:
    """
    Security regression: a non-admin caller with user_id=None (service-account
    key) must be rejected at the endpoint boundary, before any tool dispatch.
    """

    @pytest.mark.asyncio
    async def test_non_admin_with_user_id_none_is_rejected(self):
        from fastapi import HTTPException

        from litellm.proxy._types import LitellmUserRoles, UserAPIKeyAuth
        from litellm.proxy.management_endpoints.usage_endpoints.endpoints import (
            ChatMessage,
            UsageAIChatRequest,
            usage_ai_chat,
        )

        service_account_key = UserAPIKeyAuth(
            user_id=None,
            user_role=LitellmUserRoles.INTERNAL_USER,
        )
        request = MagicMock()
        body = UsageAIChatRequest(
            messages=[ChatMessage(role="user", content="hi")],
            model="gpt-4o-mini",
        )

        with pytest.raises(HTTPException) as exc_info:
            await usage_ai_chat(
                data=body,
                request=request,
                user_api_key_dict=service_account_key,
            )

        assert exc_info.value.status_code == 403
        assert "Service-account keys" in str(exc_info.value.detail)

    def test_resolve_fetch_kwargs_tripwire_fires_on_none_user_id(self):
        """
        Defense-in-depth: if a future endpoint forgets the entry guard and
        a non-admin caller with user_id=None reaches _resolve_fetch_kwargs,
        the tripwire must fire rather than issuing an unscoped query.
        """
        from litellm.proxy.management_endpoints.usage_endpoints.ai_usage_chat import (
            _resolve_fetch_kwargs,
        )

        with pytest.raises(ValueError, match="Non-admin caller has user_id=None; refusing to issue an") as exc_info:
            _resolve_fetch_kwargs(
                fn_name="get_usage_data",
                fn_args={"start_date": "2025-01-01", "end_date": "2025-01-31"},
                user_id=None,
                is_admin=False,
            )
        assert "Endpoint-level guard missing" in str(exc_info.value)


class TestUsageAiChatKeepalive:
    async def _collect_endpoint_body(self, monkeypatch, interval, delay=0.3) -> tuple[list[bytes], dict]:
        import asyncio

        import litellm
        from fastapi.responses import StreamingResponse
        from litellm.proxy._types import LitellmUserRoles, UserAPIKeyAuth
        from litellm.proxy.management_endpoints.usage_endpoints.endpoints import (
            ChatMessage,
            UsageAIChatRequest,
            usage_ai_chat,
        )

        monkeypatch.setattr(litellm, "sse_keepalive_ping_interval_seconds", interval)

        async def slow_acompletion(**kwargs):
            await asyncio.sleep(delay)
            response = MagicMock()
            response.choices = [MagicMock()]
            response.choices[0].message.tool_calls = None
            response.choices[0].message.content = "Total spend is $50.25"
            return response

        with patch(  # test-quality-ok: timed completion seam isolates SSE heartbeat behavior
            "litellm.proxy.management_endpoints.usage_endpoints.ai_usage_chat._create_completion",
            new=AsyncMock(side_effect=slow_acompletion),
        ):
            response = await usage_ai_chat(
                data=UsageAIChatRequest(messages=[ChatMessage(role="user", content="hi")], model="gpt-4o-mini"),
                request=MagicMock(),
                user_api_key_dict=UserAPIKeyAuth(user_id="admin", user_role=LitellmUserRoles.PROXY_ADMIN),
            )
            assert isinstance(response, StreamingResponse)
            chunks = [chunk if isinstance(chunk, bytes) else chunk.encode() async for chunk in response.body_iterator]
        return chunks, dict(response.headers)

    @pytest.mark.asyncio
    async def test_endpoint_pings_while_the_planning_completion_is_still_running(self, monkeypatch):
        chunks, headers = await self._collect_endpoint_body(monkeypatch, interval=0.05)

        assert headers["content-type"].startswith("text/event-stream")
        assert headers["cache-control"] == "no-cache"
        assert headers["x-accel-buffering"] == "no"
        assert chunks[0].startswith(b'data: {"type": "status"')
        assert chunks[1] == b": ping\n\n"
        assert chunks.count(b": ping\n\n") >= 3
        assert b'"content": "Total spend is $50.25"' in b"".join(chunks)
        assert chunks[-1] == b'data: {"type": "done"}\n\n'

    @pytest.mark.asyncio
    async def test_endpoint_stream_is_untouched_while_keepalives_are_unconfigured(self, monkeypatch):
        chunks, _ = await self._collect_endpoint_body(monkeypatch, interval=None, delay=0.15)

        assert b": ping\n\n" not in chunks
        assert chunks[0].startswith(b'data: {"type": "status"')
        assert chunks[-1] == b'data: {"type": "done"}\n\n'


def _planning_response(content="Total spend is $50.25"):
    """Build a completion response with no tool calls, i.e. the direct-answer path."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.tool_calls = None
    response.choices[0].message.content = content
    return response


class TestAskAiModelResolution:
    def test_default_model_follows_env_override(self, monkeypatch):
        monkeypatch.setenv(USAGE_AI_MODEL_ENV, "qwen3.8-flash-next-codex")

        assert _resolve_default_model() == "qwen3.8-flash-next-codex"

    def test_default_model_falls_back_to_constant_without_env(self, monkeypatch):
        monkeypatch.setenv(USAGE_AI_MODEL_ENV, "   ")
        assert _resolve_default_model() == DEFAULT_COMPETITOR_DISCOVERY_MODEL

        monkeypatch.delenv(USAGE_AI_MODEL_ENV, raising=False)
        assert _resolve_default_model() == DEFAULT_COMPETITOR_DISCOVERY_MODEL

    @pytest.mark.asyncio
    async def test_completion_goes_through_router_when_configured(self, monkeypatch):
        router = MagicMock()
        router.acompletion = AsyncMock(return_value="routed")
        direct = AsyncMock(return_value="direct")
        monkeypatch.setattr("litellm.proxy.proxy_server.llm_router", router)
        monkeypatch.setattr(ai_usage_chat.litellm, "acompletion", direct)

        result = await _create_completion(
            model="qwen3.8-flash-next-codex", messages=[{"role": "user", "content": "hi"}]
        )

        assert result == "routed"
        router.acompletion.assert_awaited_once_with(
            model="qwen3.8-flash-next-codex", messages=[{"role": "user", "content": "hi"}]
        )
        direct.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_completion_falls_back_to_direct_call_without_router(self, monkeypatch):
        direct = AsyncMock(return_value="direct")
        monkeypatch.setattr(ai_usage_chat.litellm, "acompletion", direct)

        result = await _create_completion(model="gpt-4o-mini", messages=[{"role": "user", "content": "hi"}])

        assert result == "direct"
        direct.assert_awaited_once_with(model="gpt-4o-mini", messages=[{"role": "user", "content": "hi"}])

    @pytest.mark.asyncio
    async def test_stream_sends_env_model_and_role_tools_to_router(self, monkeypatch):
        monkeypatch.setenv(USAGE_AI_MODEL_ENV, "qwen3.8-flash-next-codex")
        router = MagicMock()
        router.acompletion = AsyncMock(return_value=_planning_response())
        monkeypatch.setattr("litellm.proxy.proxy_server.llm_router", router)

        events = []
        async for event in stream_usage_ai_chat(
            messages=[{"role": "user", "content": "Reply only OK."}],
            model=None,
            user_id="user-123",
            is_admin=False,
        ):
            events.append(json.loads(event.replace("data: ", "").strip()))

        assert [e["type"] for e in events] == ["status", "chunk", "done"]
        assert events[1]["content"] == "Total spend is $50.25"
        kwargs = router.acompletion.await_args.kwargs
        assert kwargs["model"] == "qwen3.8-flash-next-codex"
        assert [t["function"]["name"] for t in kwargs["tools"]] == [t["function"]["name"] for t in TOOLS_BASE]

    @pytest.mark.asyncio
    async def test_explicit_model_still_wins_over_env_default(self, monkeypatch):
        monkeypatch.setenv(USAGE_AI_MODEL_ENV, "qwen3.8-flash-next-codex")
        router = MagicMock()
        router.acompletion = AsyncMock(return_value=_planning_response())
        monkeypatch.setattr("litellm.proxy.proxy_server.llm_router", router)

        async for _ in stream_usage_ai_chat(
            messages=[{"role": "user", "content": "hi"}],
            model="gpt-4o-mini",
            user_id="user-123",
            is_admin=True,
        ):
            pass

        assert router.acompletion.await_args.kwargs["model"] == "gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_final_stream_survives_framing_only_chunks(self, monkeypatch):
        first = MagicMock()
        first.choices = [MagicMock()]
        first.choices[0].message.tool_calls = [MagicMock()]
        first.choices[0].message.tool_calls[0].id = "call_1"
        first.choices[0].message.tool_calls[0].function.name = "get_usage_data"
        first.choices[0].message.tool_calls[0].function.arguments = json.dumps(
            {"start_date": "2025-01-01", "end_date": "2025-01-31"}
        )
        first.choices[0].message.model_dump.return_value = {"role": "assistant", "content": None, "tool_calls": []}

        empty_chunk = MagicMock(spec_set=["choices"])
        empty_chunk.choices = []
        text_chunk = MagicMock()
        text_chunk.choices = [MagicMock()]
        text_chunk.choices[0].delta.content = "done talking"

        async def final_stream():
            yield empty_chunk
            yield text_chunk

        router = MagicMock()
        router.acompletion = AsyncMock(side_effect=[first, final_stream()])
        monkeypatch.setattr("litellm.proxy.proxy_server.llm_router", router)

        async def fake_fetch(**kwargs):
            return SAMPLE_AGGREGATED_RESPONSE

        monkeypatch.setitem(ai_usage_chat.TOOL_HANDLERS["get_usage_data"], "fetch", fake_fetch)

        events = []
        async for event in stream_usage_ai_chat(
            messages=[{"role": "user", "content": "What is my total spend?"}],
            model="qwen3.8-flash-next-codex",
            user_id="admin",
            is_admin=True,
        ):
            events.append(json.loads(event.replace("data: ", "").strip()))

        assert [e["type"] for e in events if e["type"] in ("chunk", "done", "error")] == ["chunk", "done"]
        assert [e["content"] for e in events if e["type"] == "chunk"] == ["done talking"]
        assert router.acompletion.await_count == 2
        assert [call.kwargs["model"] for call in router.acompletion.await_args_list] == [
            "qwen3.8-flash-next-codex",
            "qwen3.8-flash-next-codex",
        ]
        assert router.acompletion.await_args_list[1].kwargs["stream"] is True
        assert router.acompletion.await_args_list[1].kwargs["messages"][-1]["role"] == "tool"
