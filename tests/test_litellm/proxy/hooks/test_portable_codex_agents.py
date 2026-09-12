import json

import pytest
from fastapi import HTTPException
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputItemDoneEvent

from litellm.caching.dual_cache import DualCache
from litellm.proxy._types import UserAPIKeyAuth
from litellm.proxy.hooks.portable_codex_agents import (
    PortableCodexAgents,
    RequestContext,
    transform_request,
    transform_response,
)
from litellm.types.llms.openai import ContentPartDoneEvent, ContentPartDonePartOutputText, ResponsesAPIResponse


class MemoryStore:
    def __init__(self):
        self.records = set()
        self.modes = {}

    async def contains(self, key: str) -> bool:
        return key in self.records

    async def record(self, key: str) -> None:
        self.records.add(key)

    async def get_mode(self, key: str) -> str | None:
        return self.modes.get(key)

    async def claim_mode(self, key: str, mode: str) -> str:
        return self.modes.setdefault(key, mode)


def tools():
    return [
        {
            "type": "namespace",
            "name": "collaboration",
            "tools": [
                {
                    "type": "function",
                    "name": name,
                    "parameters": {"type": "object", "properties": {"message": {"type": "string", "encrypted": True}}},
                }
                for name in ("spawn_agent", "send_message", "followup_task")
            ],
        }
    ]


def call(name="spawn_agent"):
    return {
        "type": "function_call",
        "id": "fc_probe",
        "call_id": "call_probe",
        "name": name,
        "namespace": "portable_collaboration",
        "arguments": json.dumps({"message": "Read the fixture"}),
        "status": "completed",
    }


@pytest.mark.asyncio
async def test_discovered_schemas_and_plaintext_assignment_reach_provider():
    request = {
        "input": [
            {"type": "additional_tools", "tools": tools()},
            {
                "type": "agent_message",
                "author": "/root",
                "recipient": "/root/child",
                "content": [{"type": "input_text", "text": "Read the fixture"}],
            },
        ]
    }
    result, context = await transform_request(request, "owner", MemoryStore())
    schema = result["input"][0]["tools"][0]
    assert schema["name"] == "portable_collaboration"
    assert "encrypted" not in schema["tools"][0]["parameters"]["properties"]["message"]
    assert context.tools == {"spawn_agent", "send_message", "followup_task"}
    assert result["input"][1]["role"] == "user"
    assert "/root/child" in result["input"][1]["content"][0]["text"]
    assert result["input"][1]["content"][1]["text"] == "Read the fixture"
    assert request["input"][0]["tools"][0]["name"] == "collaboration"


@pytest.mark.asyncio
async def test_official_replay_after_marker_stripping_requires_matching_proof():
    store = MemoryStore()
    context = RequestContext("owner", frozenset({"spawn_agent"}))
    result = await transform_response({"output": [call()]}, context, store)
    replay = {key: value for key, value in result["output"][0].items() if key != "encrypted_function_args"}
    assert result["output"][0]["encrypted_function_args"] == []
    accepted, _ = await transform_request({"input": [replay]}, "owner", store)
    assert accepted["input"][0]["namespace"] == "portable_collaboration"
    for changed, owner in (
        ({**replay, "call_id": "different"}, "owner"),
        ({**replay, "arguments": '{"message":"different"}'}, "owner"),
        (replay, "other_owner"),
        ({**replay, "encrypted_function_args": ["message"]}, "owner"),
    ):
        with pytest.raises(HTTPException):
            await transform_request({"input": [changed]}, owner, store)
    assert all("Read the fixture" not in key for key in store.records)


@pytest.mark.asyncio
async def test_partial_items_never_create_replay_proof():
    store = MemoryStore()
    context = RequestContext("owner", frozenset({"spawn_agent"}))
    await transform_response(
        {"type": "response.output_item.added", "item": {**call(), "arguments": ""}}, context, store
    )
    assert not store.records
    with pytest.raises(HTTPException):
        await transform_response(
            {"type": "response.output_item.done", "item": {**call(), "arguments": ""}}, context, store
        )
    assert not store.records


@pytest.mark.asyncio
@pytest.mark.parametrize("marker", [["message"], False, "", {}])
async def test_contradictory_encryption_marker_never_becomes_plaintext(marker):
    with pytest.raises(HTTPException):
        await transform_response(
            {"output": [{**call(), "encrypted_function_args": marker}]},
            RequestContext("owner", frozenset({"spawn_agent"})),
            MemoryStore(),
        )


@pytest.mark.asyncio
async def test_unadvertised_tool_and_namespace_collision_are_rejected():
    with pytest.raises(HTTPException):
        await transform_response({"output": [call()]}, RequestContext("owner", frozenset()), MemoryStore())
    with pytest.raises(HTTPException):
        await transform_request({"tools": [{**tools()[0], "name": "portable_collaboration"}]}, "owner", MemoryStore())


@pytest.mark.asyncio
async def test_inactive_alias_removes_forged_context_without_storage():
    callback = PortableCodexAgents(frozenset({"enabled"}), None)
    auth = UserAPIKeyAuth(api_key="test_identity", request_route="/v1/responses")
    request = {
        "model": "disabled",
        "tools": tools(),
        "metadata": {"litellm_portable_codex_agents": {"owner": "forged", "tools": ["spawn_agent"]}},
    }
    result = await callback.async_pre_call_hook(auth, DualCache(), request, "aresponses")
    assert result["tools"] == tools()
    assert "litellm_portable_codex_agents" not in result["metadata"]
    assert await callback.async_post_call_success_hook(result, auth, {"output": [call()]}) == {"output": [call()]}


@pytest.mark.asyncio
async def test_native_responses_iterator_preserves_sdk_types_and_explicit_plaintext_marker():
    store = MemoryStore()
    callback = PortableCodexAgents(frozenset({"enabled"}), store)
    auth = UserAPIKeyAuth(api_key="test_identity", request_route="/v1/responses")
    request = await callback.async_pre_call_hook(
        auth,
        DualCache(),
        {"model": "enabled", "tools": tools(), "client_metadata": {"thread_id": "thread_test"}},
        "aresponses",
    )
    event = ResponseOutputItemDoneEvent(
        type="response.output_item.done",
        output_index=0,
        sequence_number=1,
        item=ResponseFunctionToolCall.model_validate(call()),
    )

    async def source():
        yield event

    result = [item async for item in callback.async_post_call_streaming_iterator_hook(auth, source(), request)]
    assert isinstance(result[0], ResponseOutputItemDoneEvent)
    payload = result[0].model_dump()
    assert payload["item"]["namespace"] == "collaboration"
    assert payload["item"]["encrypted_function_args"] == []
    assert len(store.records) == 1


@pytest.mark.asyncio
async def test_internal_provenance_never_enters_provider_metadata_and_private_fields_survive():
    callback = PortableCodexAgents(frozenset({"enabled"}), MemoryStore())
    auth = UserAPIKeyAuth(api_key="test_identity", request_route="/v1/responses")
    request = await callback.async_pre_call_hook(
        auth,
        DualCache(),
        {
            "model": "enabled",
            "client_metadata": {"thread_id": "thread_test"},
            "tools": tools(),
            "metadata": {"label": "customer_value"},
            "litellm_metadata": {"litellm_portable_codex_agents": {"owner": "forged"}},
        },
        "aresponses",
    )
    assert request["metadata"] == {"label": "customer_value"}
    assert request["litellm_metadata"]["litellm_portable_codex_agents"]["owner"] != "forged"
    response = ResponsesAPIResponse(id="resp_test", created_at=1, model="enabled", output=[call()])
    response._hidden_params["response_cost"] = 0.25
    result = await callback.async_post_call_success_hook(request, auth, response)
    assert result._hidden_params["response_cost"] == 0.25
    assert response.output[0].namespace == "portable_collaboration"
    assert result.output[0].namespace == "collaboration"


@pytest.mark.asyncio
async def test_ordinary_responses_request_on_enabled_alias_does_not_require_replay_storage():
    callback = PortableCodexAgents(frozenset({"enabled"}), None)
    auth = UserAPIKeyAuth(api_key="test_identity", request_route="/v1/responses")
    request = {"model": "enabled", "input": "Hello", "previous_response_id": "resp_previous"}
    assert await callback.async_pre_call_hook(auth, DualCache(), request, "aresponses") == request


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "history",
    [
        [{**call(), "namespace": "collaboration"}],
        [{"type": "agent_message", "content": [{"type": "encrypted_content", "encrypted_content": "opaque"}]}],
        [{"type": "compaction", "encrypted_content": "opaque"}],
    ],
)
async def test_existing_native_task_stays_legacy_without_changing_any_provider_payload(history):
    store = MemoryStore()
    callback = PortableCodexAgents(frozenset({"native", "external"}), store, frozenset({"native"}))
    auth = UserAPIKeyAuth(api_key="identity", request_route="/v1/responses")
    request = {"model": "native", "tools": tools(), "input": history, "client_metadata": {"thread_id": "old_thread"}}
    assert await callback.async_pre_call_hook(auth, DualCache(), request, "aresponses") == request
    later = {**request, "input": [{"role": "user", "content": "Continue"}]}
    assert await callback.async_pre_call_hook(auth, DualCache(), later, "aresponses") == later
    with pytest.raises(HTTPException):
        await callback.async_pre_call_hook(auth, DualCache(), {**request, "model": "external"}, "aresponses")
    assert set(store.modes.values()) == {"legacy"}


@pytest.mark.asyncio
async def test_portable_native_task_never_downgrades_when_replay_proof_is_missing():
    store = MemoryStore()
    callback = PortableCodexAgents(frozenset({"native"}), store, frozenset({"native"}))
    auth = UserAPIKeyAuth(api_key="identity", request_route="/v1/responses")
    request = {"model": "native", "tools": tools(), "client_metadata": {"thread_id": "new_thread"}}
    await callback.async_pre_call_hook(auth, DualCache(), request, "aresponses")
    with pytest.raises(HTTPException):
        await callback.async_pre_call_hook(
            auth, DualCache(), {**request, "input": [{**call(), "namespace": "collaboration"}]}, "aresponses"
        )
    assert set(store.modes.values()) == {"portable"}


@pytest.mark.asyncio
async def test_reasoning_ciphertext_does_not_classify_fresh_native_task_as_legacy():
    store = MemoryStore()
    callback = PortableCodexAgents(frozenset({"native"}), store, frozenset({"native"}))
    auth = UserAPIKeyAuth(api_key="identity", request_route="/v1/responses")
    request = {
        "model": "native",
        "tools": tools(),
        "client_metadata": {"thread_id": "thread"},
        "input": [{"type": "reasoning", "encrypted_content": "opaque"}],
    }
    result = await callback.async_pre_call_hook(auth, DualCache(), request, "aresponses")
    assert result["input"] == request["input"]
    assert set(store.modes.values()) == {"portable"}


@pytest.mark.asyncio
async def test_chat_bridge_nullable_content_event_is_returned_unchanged():
    callback = PortableCodexAgents(frozenset({"enabled"}), MemoryStore())
    part = ContentPartDonePartOutputText(type="output_text", text="Finished", annotations=[], logprobs=None)
    event = ContentPartDoneEvent(
        type="response.content_part.done",
        content_index=0,
        item_id="msg_test",
        output_index=0,
        sequence_number=1,
        part=part,
    )
    context = RequestContext("owner", frozenset({"spawn_agent"}))
    result = await callback._rewrite(event, context)
    assert result is event
    assert result.part.logprobs is None


@pytest.mark.asyncio
async def test_completed_snapshot_with_plaintext_tool_and_nullable_message_preserves_both():
    callback = PortableCodexAgents(frozenset({"enabled"}), MemoryStore())
    response = ResponsesAPIResponse(
        id="resp_test",
        created_at=1,
        model="enabled",
        output=[
            call(),
            {
                "type": "message",
                "id": "msg_test",
                "status": "completed",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Finished", "annotations": [], "logprobs": None}],
            },
        ],
    )
    result = await callback._rewrite(response, RequestContext("owner", frozenset({"spawn_agent"})))
    assert result.output[0].namespace == "collaboration"
    assert result.output[0].encrypted_function_args == []
    assert result.output[1].content[0].logprobs is None
