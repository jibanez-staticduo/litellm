"""
Tests for the Responses API streaming bridge in
litellm/responses/litellm_completion_transformation/streaming_iterator.py.

Ensures that when the underlying chat-completions stream includes tool_calls deltas,
LiteLLM emits Responses API streaming events (output_item.added + function_call_arguments.*).

Also ensures that tool calls that only appear in the final built response still get emitted
before response.completed, and that every event of a bridged stream carries the response id
spend tracking stores, so a follow-up previous_response_id still finds the conversation.
"""

import json
from typing import Final
from unittest.mock import AsyncMock, MagicMock

import pytest

from litellm.responses.litellm_completion_transformation.streaming_iterator import (
    LiteLLMCompletionStreamingIterator,
)
from litellm.responses.utils import ResponsesAPIRequestUtils
from litellm.types.llms.openai import ResponsesAPIStreamEvents
from litellm.types.utils import (
    Delta,
    ModelResponse,
    ModelResponseStream,
    StreamingChoices,
    Usage,
)

CHAT_COMPLETION_ID = "chatcmpl-77d33d09-effa-4cd2-9c0d-c742d4358256"
RESPONSE_ID_EVENT_TYPES = frozenset(
    {"response.created", "response.in_progress", "response.completed"}
)


@pytest.mark.asyncio
async def test_client_tool_search_stream_is_dispatched_as_search_not_function():
    arguments = {"query": "calendar create", "limit": 1}
    encoded = json.dumps(arguments)
    chunks = [
        ModelResponseStream(
            id=CHAT_COMPLETION_ID, model="qwen3.8-flash-next", created=1748575031,
            choices=[StreamingChoices(index=0, delta=Delta(role="assistant", tool_calls=[{
                "index": 0, "id": "call_search", "type": "function",
                "function": {"name": "tool_search", "arguments": encoded[:10]},
            }]))],
        ),
        ModelResponseStream(
            id=CHAT_COMPLETION_ID, model="qwen3.8-flash-next", created=1748575031,
            choices=[StreamingChoices(index=0, delta=Delta(tool_calls=[{
                "index": 0, "function": {"arguments": encoded[10:]},
            }]))],
        ),
        ModelResponseStream(
            id=CHAT_COMPLETION_ID, model="qwen3.8-flash-next", created=1748575031,
            choices=[StreamingChoices(index=0, delta=Delta(), finish_reason="tool_calls")],
        ),
    ]
    iterator = LiteLLMCompletionStreamingIterator(
        model="qwen3.8-flash-next", litellm_custom_stream_wrapper=_FakeStreamWrapper(chunks),
        request_input="Find calendar tools", custom_llm_provider="hosted_vllm",
        responses_api_request={"tool_choice": {"type": "tool_search"}, "tools": [{
            "type": "tool_search", "execution": "client", "description": "Find tools",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
        }]},
    )
    events = [event async for event in iterator]
    added = [e.item for e in events if e.type == "response.output_item.added" and e.item.type == "tool_search_call"]
    done = [e.item for e in events if e.type == "response.output_item.done" and e.item.type == "tool_search_call"]
    completed = next(e.response for e in events if e.type == "response.completed")
    final = [item for item in completed.output if item.type == "tool_search_call"]
    assert len(added) == len(done) == len(final) == 1
    for item in (*added, *done, *final):
        assert item.type == "tool_search_call"
        assert item.call_id == "call_search"
        assert item.execution == "client"
        assert item.id == added[0].id
    assert added[0].arguments == {}
    assert done[0].arguments == final[0].arguments == arguments
    assert done[0].status == final[0].status == "completed"
    assert not any(item.type == "function_call" for item in completed.output)
    assert not any(e.type.startswith("response.function_call_arguments.") for e in events)


@pytest.mark.parametrize("choice", [
    {"type": "tool_search"},
    {"type": "function", "name": "lookup_probe"},
    {"type": "custom", "name": "apply_patch"},
    {"type": "function", "name": "exec", "namespace": "functions"},
    {"type": "custom", "name": "exec", "namespace": "functions"},
])
def test_created_event_preserves_responses_tool_choice(choice):
    iterator = LiteLLMCompletionStreamingIterator(
        model="qwen3.8-flash-next", litellm_custom_stream_wrapper=_FakeStreamWrapper([]),
        request_input="Use the tool", responses_api_request={"tool_choice": choice},
    )
    event = iterator.create_response_created_event()
    assert event.model_dump()["response"]["tool_choice"] == choice


def _chunk(content: str, finish_reason: str | None = None) -> ModelResponseStream:
    return ModelResponseStream(
        id=CHAT_COMPLETION_ID,
        created=1748575031,
        model="claude-haiku-4-5",
        object="chat.completion.chunk",
        choices=[
            StreamingChoices(
                index=0,
                delta=Delta(role="assistant", content=content),
                finish_reason=finish_reason,
            )
        ],
    )


class _FakeStreamWrapper:
    def __init__(self, chunks):
        self._chunks = list(chunks)
        self.logging_obj = MagicMock()

    def __iter__(self):
        return self

    def __next__(self):
        if not self._chunks:
            raise StopIteration
        return self._chunks.pop(0)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._chunks:
            raise StopAsyncIteration
        return self._chunks.pop(0)


def _build_iterator(chunks) -> LiteLLMCompletionStreamingIterator:
    return LiteLLMCompletionStreamingIterator(
        model="claude-haiku-4-5",
        litellm_custom_stream_wrapper=_FakeStreamWrapper(chunks),
        request_input="What is the weather in San Francisco?",
        responses_api_request={},
        custom_llm_provider="anthropic",
        litellm_metadata={},
    )


def _response_ids(events) -> list[str]:
    return [
        event.response.id
        for event in events
        if getattr(event, "type", None) in RESPONSE_ID_EVENT_TYPES
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [False, True])
@pytest.mark.parametrize("empty_prefix", [False, True])
async def test_reasoning_lifecycle_survives_wire_serialization(sync, empty_prefix):
    reasoning = ModelResponseStream(
        id=CHAT_COMPLETION_ID,
        model="claude-haiku-4-5",
        created=1748575031,
        choices=[StreamingChoices(index=0, delta=Delta(reasoning_content="Check the sum."))],
    )
    iterator = _build_iterator(
        ([_chunk("")] if empty_prefix else [])
        + [reasoning, _chunk("42"), _chunk("", finish_reason="stop")]
    )
    events = list(iterator) if sync else [event async for event in iterator]
    wire = [json.loads(event.model_dump_json(exclude_none=True, exclude_unset=True)) for event in events]
    added = [event for event in wire if event["type"] == "response.output_item.added"]
    assert [event["item"]["type"] for event in added] == ["reasoning", "message"]
    assert [event["output_index"] for event in added] == [0, 1]
    reasoning_id = added[0]["item"]["id"]
    delta = next(event for event in wire if event["type"] == "response.reasoning_text.delta")
    assert delta["content_index"] == 0
    assert delta["item_id"] == reasoning_id
    assert delta["delta"] == "Check the sum."
    part_added = next(event for event in wire if event["type"] == "response.content_part.added")
    assert part_added["content_index"] == 0
    assert wire.index(part_added) < wire.index(delta)
    done = [event for event in wire if event["type"] == "response.output_item.done"]
    assert [event["item"]["type"] for event in done] == ["reasoning", "message"]
    assert done[0]["item"]["id"] == reasoning_id
    assert done[0]["item"]["content"][0]["text"] == "Check the sum."
    assert wire.index(done[0]) < wire.index(added[1])
    assert done[1]["item"]["content"][0]["text"] == "42"
    assert done[0]["item"]["summary"] == []
    assert done[0]["item"]["content"][0]["type"] == "reasoning_text"
    assert not any("reasoning_summary" in event["type"] for event in wire)
    completed = next(event["response"] for event in wire if event["type"] == "response.completed")
    saved = next(item for item in completed["output"] if item["type"] == "reasoning")
    assert saved["summary"] == []
    assert saved["content"] == done[0]["item"]["content"]
    from litellm.responses.litellm_completion_transformation.transformation import LiteLLMCompletionResponsesConfig
    replayed = LiteLLMCompletionResponsesConfig.transform_responses_api_input_to_messages(
        [saved, {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "42"}]}],
        responses_api_request={}, replay_reasoning=True,
    )
    assert replayed[0]["reasoning_content"] == "Check the sum."
    assert replayed[0]["content"] == [{"type": "text", "text": "42"}]
    content_done = next(event for event in wire if event["type"] == "response.content_part.done" and event["output_index"] == 1)
    assert content_done["part"]["type"] == "output_text"
    assert content_done["output_index"] == 1


def test_tool_call_delta_is_emitted_as_responses_events():
    iterator = LiteLLMCompletionStreamingIterator(
        model="test-model",
        litellm_custom_stream_wrapper=AsyncMock(),
        request_input="Test input",
        responses_api_request={},
    )

    # A streaming chunk with tool_calls delta but no text
    chunk = ModelResponseStream(
        id="chunk-1",
        created=123,
        model="test-model",
        object="chat.completion.chunk",
        choices=[
            StreamingChoices(
                finish_reason=None,
                index=0,
                delta=Delta(
                    role="assistant",
                    content="",
                    tool_calls=[
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": "do_thing", "arguments": '{"x":1}'},
                        }
                    ],
                ),
            )
        ],
    )

    evt1 = iterator._transform_chat_completion_chunk_to_response_api_chunk(chunk)
    assert evt1 is not None
    assert evt1.type == ResponsesAPIStreamEvents.OUTPUT_ITEM_ADDED
    assert evt1.output_index == 1

    # The arguments are now chunked, so we get the first delta chunk
    evt2 = iterator._transform_chat_completion_chunk_to_response_api_chunk(chunk)
    assert evt2 is not None
    assert evt2.type == ResponsesAPIStreamEvents.FUNCTION_CALL_ARGUMENTS_DELTA
    assert evt2.item_id == "fc_call_1"
    assert evt2.output_index == 1
    # The delta will be a chunk of the arguments, not the full arguments
    assert len(evt2.delta) <= 10  # Chunks are max 10 characters


def test_tool_calls_present_only_in_final_response_are_emitted_before_completed():
    iterator = LiteLLMCompletionStreamingIterator(
        model="test-model",
        litellm_custom_stream_wrapper=AsyncMock(),
        request_input="Test input",
        responses_api_request={},
    )

    # Construct a final ModelResponse with tool_calls on the message.
    # We bypass the stream builder and directly set iterator.litellm_model_response.
    response = ModelResponse(
        id="resp-1",
        created=123,
        model="test-model",
        object="chat.completion",
        choices=[
            {
                "index": 0,
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_2",
                            "type": "function",
                            "function": {"name": "do_thing", "arguments": '{"y":2}'},
                            "index": 0,
                        }
                    ],
                },
            }
        ],
    )
    iterator.litellm_model_response = response

    # First common_done_event_logic call should yield tool events, not response.completed.
    evt1 = iterator.common_done_event_logic(sync_mode=True)
    assert evt1.type == ResponsesAPIStreamEvents.OUTPUT_ITEM_ADDED
    assert evt1.output_index == 1

    # Now delta events are emitted (arguments split into chunks)
    # Collect all delta events
    delta_events = []
    while True:
        evt = iterator.common_done_event_logic(sync_mode=True)
        if evt.type == ResponsesAPIStreamEvents.FUNCTION_CALL_ARGUMENTS_DELTA:
            delta_events.append(evt)
        else:
            break

    # Verify we got delta events
    assert len(delta_events) > 0
    # Verify they reconstruct the original arguments
    concatenated_args = "".join(evt.delta for evt in delta_events)
    assert concatenated_args == '{"y":2}'

    # The last event should be FUNCTION_CALL_ARGUMENTS_DONE
    assert evt.type == ResponsesAPIStreamEvents.FUNCTION_CALL_ARGUMENTS_DONE
    assert evt.item_id == "fc_call_2"
    assert evt.output_index == 1
    assert evt.arguments == '{"y":2}'

    evt_final = iterator.common_done_event_logic(sync_mode=True)
    assert evt_final.type == ResponsesAPIStreamEvents.OUTPUT_ITEM_DONE
    assert evt_final.output_index == 1


def test_tool_call_arguments_are_chunked_to_match_openai_behavior():
    """
    Test that large tool call arguments are split into smaller chunks (size 10)
    to replicate OpenAI's native streaming behavior.

    This is especially important for providers like Bedrock that send complete
    arguments at once, which need to be split to match OpenAI's token-by-token streaming.
    """
    iterator = LiteLLMCompletionStreamingIterator(
        model="test-model",
        litellm_custom_stream_wrapper=AsyncMock(),
        request_input="Test input",
        responses_api_request={},
    )

    # Create a chunk with a large arguments string that should be split
    large_arguments = (
        '{"param1": "value1", "param2": "value2", "param3": "value3"}'  # 67 chars
    )
    chunk = ModelResponseStream(
        id="chunk-1",
        created=123,
        model="test-model",
        object="chat.completion.chunk",
        choices=[
            StreamingChoices(
                finish_reason=None,
                index=0,
                delta=Delta(
                    role="assistant",
                    content="",
                    tool_calls=[
                        {
                            "id": "call_test",
                            "type": "function",
                            "function": {
                                "name": "test_function",
                                "arguments": large_arguments,
                            },
                        }
                    ],
                ),
            )
        ],
    )

    # Process the chunk once - it queues all events internally
    evt = iterator._transform_chat_completion_chunk_to_response_api_chunk(chunk)

    # First event should be OUTPUT_ITEM_ADDED
    assert evt is not None
    assert evt.type == ResponsesAPIStreamEvents.OUTPUT_ITEM_ADDED
    assert evt.output_index == 1
    assert hasattr(evt, "__dict__") and "sequence_number" in evt.__dict__

    # Collect all remaining delta events from the pending queue by creating empty chunks
    delta_events = []
    empty_chunk = ModelResponseStream(
        id="chunk-1",
        created=123,
        model="test-model",
        object="chat.completion.chunk",
        choices=[
            StreamingChoices(
                finish_reason=None,
                index=0,
                delta=Delta(role="assistant", content=""),
            )
        ],
    )

    # Keep draining pending events (expected: ceil(67 / 10) = 7 delta events)
    while iterator._pending_tool_events:
        evt = iterator._transform_chat_completion_chunk_to_response_api_chunk(
            empty_chunk
        )
        if evt and evt.type == ResponsesAPIStreamEvents.FUNCTION_CALL_ARGUMENTS_DELTA:
            delta_events.append(evt)

    # Verify multiple delta events were created (at least 6 chunks for 67 chars)
    assert len(delta_events) >= 6  # 67 chars split into chunks of max 10 chars each

    # Verify each delta is at most 10 characters
    for evt in delta_events:
        assert len(evt.delta) <= 10
        assert evt.item_id == "fc_call_test"
        assert evt.output_index == 1
        assert hasattr(evt, "__dict__") and "sequence_number" in evt.__dict__

    # Verify all deltas concatenated equal the original arguments
    concatenated = "".join(evt.delta for evt in delta_events)
    assert concatenated == large_arguments

    # Verify sequence numbers are increasing
    sequence_numbers = [evt.__dict__["sequence_number"] for evt in delta_events]
    assert sequence_numbers == sorted(sequence_numbers)
    assert len(set(sequence_numbers)) == len(sequence_numbers)  # All unique


def test_tool_call_delta_without_id_uses_index_mapping():
    iterator = LiteLLMCompletionStreamingIterator(
        model="test-model",
        litellm_custom_stream_wrapper=AsyncMock(),
        request_input="Test input",
        responses_api_request={},
    )

    chunks = [
        [
            {
                "index": 0,
                "id": "call_abc123",
                "type": "function",
                "function": {"name": "get_weather", "arguments": '{"lo'},
            }
        ],
        [{"index": 0, "type": "function", "function": {"arguments": 'cation":'}}],
        [{"index": 0, "type": "function", "function": {"arguments": ' "New'}}],
        [{"index": 0, "type": "function", "function": {"arguments": ' York"}'}}],
    ]

    for tool_calls in chunks:
        iterator._queue_tool_call_delta_events(tool_calls)

    all_events = []
    while iterator._pending_tool_events:
        all_events.append(iterator._pending_tool_events.pop(0))

    delta_events = [
        evt
        for evt in all_events
        if evt.type == ResponsesAPIStreamEvents.FUNCTION_CALL_ARGUMENTS_DELTA
    ]
    streamed_arguments = "".join(evt.delta for evt in delta_events)

    assert streamed_arguments == '{"location": "New York"}'

    output_item_added_events = [
        evt
        for evt in all_events
        if evt.type == ResponsesAPIStreamEvents.OUTPUT_ITEM_ADDED
    ]
    assert len(output_item_added_events) == 1
    assert output_item_added_events[0].item.id == "fc_call_abc123"
    assert output_item_added_events[0].item.call_id == "call_abc123"


def test_parallel_tool_calls_without_ids_use_index_mapping():
    iterator = LiteLLMCompletionStreamingIterator(
        model="test-model",
        litellm_custom_stream_wrapper=AsyncMock(),
        request_input="Test input",
        responses_api_request={},
    )

    iterator._queue_tool_call_delta_events(
        [
            {
                "index": 0,
                "id": "call_a",
                "type": "function",
                "function": {"name": "tool_a", "arguments": '{"x":'},
            },
            {
                "index": 1,
                "id": "call_b",
                "type": "function",
                "function": {"name": "tool_b", "arguments": '{"y":'},
            },
        ]
    )
    iterator._queue_tool_call_delta_events(
        [
            {"index": 0, "type": "function", "function": {"arguments": "1}"}},
            {"index": 1, "type": "function", "function": {"arguments": "2}"}},
        ]
    )

    all_events = []
    while iterator._pending_tool_events:
        all_events.append(iterator._pending_tool_events.pop(0))

    output_item_added_events = [
        evt
        for evt in all_events
        if evt.type == ResponsesAPIStreamEvents.OUTPUT_ITEM_ADDED
    ]
    assert len(output_item_added_events) == 2

    delta_events = [
        evt
        for evt in all_events
        if evt.type == ResponsesAPIStreamEvents.FUNCTION_CALL_ARGUMENTS_DELTA
    ]
    arguments_by_call_id = {}
    for evt in delta_events:
        arguments_by_call_id.setdefault(evt.item_id, "")
        arguments_by_call_id[evt.item_id] += evt.delta

    assert arguments_by_call_id["fc_call_a"] == '{"x":1}'
    assert arguments_by_call_id["fc_call_b"] == '{"y":2}'


def test_reused_index_with_new_call_id_marks_fallback_ambiguous():
    iterator = LiteLLMCompletionStreamingIterator(
        model="test-model",
        litellm_custom_stream_wrapper=AsyncMock(),
        request_input="Test input",
        responses_api_request={},
    )

    iterator._queue_tool_call_delta_events(
        [
            {
                "index": 0,
                "id": "call_a",
                "type": "function",
                "function": {"name": "tool_a", "arguments": '{"a":'},
            }
        ]
    )
    iterator._queue_tool_call_delta_events(
        [
            {
                "index": 0,
                "id": "call_b",
                "type": "function",
                "function": {"name": "tool_b", "arguments": '{"b":'},
            }
        ]
    )
    # Ambiguous chunk: index reused and id missing. We should skip fallback rather than misroute.
    iterator._queue_tool_call_delta_events(
        [
            {
                "index": 0,
                "type": "function",
                "function": {"arguments": "1}"},
            }
        ]
    )

    all_events = []
    while iterator._pending_tool_events:
        all_events.append(iterator._pending_tool_events.pop(0))

    delta_events = [
        evt
        for evt in all_events
        if evt.type == ResponsesAPIStreamEvents.FUNCTION_CALL_ARGUMENTS_DELTA
    ]
    arguments_by_call_id = {}
    for evt in delta_events:
        arguments_by_call_id.setdefault(evt.item_id, "")
        arguments_by_call_id[evt.item_id] += evt.delta

    assert arguments_by_call_id["fc_call_a"] == '{"a":'
    assert arguments_by_call_id["fc_call_b"] == '{"b":'
    assert arguments_by_call_id["fc_call_a"] != '{"a":1}'
    assert arguments_by_call_id["fc_call_b"] != '{"b":1}'


@pytest.mark.asyncio
async def test_streaming_events_share_the_chat_completion_response_id():
    """
    Every event of a bridged stream has to carry the same id, and that id has to decode
    to the chat completion id spend tracking stores as `request_id`. Otherwise a
    follow-up `previous_response_id` matches no session and the conversation is dropped.
    """
    iterator = _build_iterator([_chunk("Hello"), _chunk("!", finish_reason="stop")])

    events = [event async for event in iterator]

    response_ids = _response_ids(events)
    assert len(response_ids) == 3
    assert len(set(response_ids)) == 1
    decoded = ResponsesAPIRequestUtils._decode_responses_api_response_id(response_ids[0])
    assert decoded["response_id"] == CHAT_COMPLETION_ID
    assert decoded["custom_llm_provider"] == "anthropic"


def test_sync_streaming_events_share_the_chat_completion_response_id():
    iterator = _build_iterator([_chunk("Hello"), _chunk("!", finish_reason="stop")])

    events = list(iterator)

    response_ids = _response_ids(events)
    assert len(response_ids) == 3
    assert len(set(response_ids)) == 1
    assert (
        ResponsesAPIRequestUtils._decode_responses_api_response_id(response_ids[0])["response_id"]
        == CHAT_COMPLETION_ID
    )


@pytest.mark.asyncio
async def test_streaming_emits_every_chunk_after_priming_the_response_id():
    iterator = _build_iterator(
        [_chunk("Hel"), _chunk("lo"), _chunk("!", finish_reason="stop")]
    )

    events = [event async for event in iterator]

    deltas = "".join(
        event.delta for event in events if getattr(event, "type", None) == "response.output_text.delta"
    )
    assert deltas == "Hello!"


@pytest.mark.asyncio
async def test_streaming_response_id_falls_back_when_upstream_yields_nothing():
    iterator = _build_iterator([])

    events = [event async for event in iterator]

    response_ids = _response_ids(events)
    assert response_ids
    assert len(set(response_ids)) == 1
    assert response_ids[0].startswith("resp_")


def test_completed_event_restores_usage_hidden_by_stream_options_none():
    final_chunk = _chunk("", finish_reason="stop")
    final_chunk._hidden_params = {"usage": Usage(prompt_tokens=117, completion_tokens=5, total_tokens=122)}
    iterator = _build_iterator([_chunk("the document says hello"), final_chunk])

    events = list(iterator)

    completed = next(
        event for event in events if getattr(event, "type", None) == ResponsesAPIStreamEvents.RESPONSE_COMPLETED
    )
    assert completed.response.usage.input_tokens == 117
    assert completed.response.usage.output_tokens == 5


def test_object_tool_call_arguments_stream_as_valid_json():
    """A provider that sends decoded object arguments must still stream valid JSON.

    `str()` on a dict yields a Python repr with single quotes, which clients
    parsing function_call_arguments reject with errors like
    "Expecting ',' delimiter".
    """
    iterator = LiteLLMCompletionStreamingIterator(
        model="test-model",
        litellm_custom_stream_wrapper=AsyncMock(),
        request_input="Test input",
        responses_api_request={},
    )
    iterator._queue_tool_call_delta_events(
        [
            {
                "index": 0,
                "id": "call_obj",
                "type": "function",
                "function": {"name": "shell", "arguments": {"command": "ls", "flags": ["-l"]}},
            }
        ]
    )

    streamed_arguments = "".join(
        evt.delta
        for evt in iterator._pending_tool_events
        if evt.type == ResponsesAPIStreamEvents.FUNCTION_CALL_ARGUMENTS_DELTA
    )

    assert json.loads(streamed_arguments) == {"command": "ls", "flags": ["-l"]}


def test_streamed_anthropic_tool_call_events_correlate_on_normalized_item_id():
    iterator = LiteLLMCompletionStreamingIterator(
        model="test-model",
        litellm_custom_stream_wrapper=AsyncMock(),
        request_input="Test input",
        responses_api_request={},
    )

    response = ModelResponse(
        id="resp-anthropic",
        created=123,
        model="test-model",
        object="chat.completion",
        choices=[
            {
                "index": 0,
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "toolu_01AbCdEf",
                            "type": "function",
                            "function": {"name": "get_weather", "arguments": '{"city":"Paris"}'},
                            "index": 0,
                        }
                    ],
                },
            }
        ],
    )
    iterator.litellm_model_response = response

    events = []
    while True:
        evt = iterator.common_done_event_logic(sync_mode=True)
        events.append(evt)
        if evt.type == ResponsesAPIStreamEvents.OUTPUT_ITEM_DONE:
            break

    added = [e for e in events if e.type == ResponsesAPIStreamEvents.OUTPUT_ITEM_ADDED]
    deltas = [e for e in events if e.type == ResponsesAPIStreamEvents.FUNCTION_CALL_ARGUMENTS_DELTA]
    dones = [e for e in events if e.type == ResponsesAPIStreamEvents.FUNCTION_CALL_ARGUMENTS_DONE]
    item_dones = [e for e in events if e.type == ResponsesAPIStreamEvents.OUTPUT_ITEM_DONE]

    assert len(added) == 1 and len(dones) == 1 and len(item_dones) == 1 and deltas
    assert added[0].item.id == "fc_toolu_01AbCdEf"
    assert added[0].item.call_id == "toolu_01AbCdEf"
    assert item_dones[0].item.id == "fc_toolu_01AbCdEf"
    assert item_dones[0].item.call_id == "toolu_01AbCdEf"
    for evt in deltas + dones:
        assert evt.item_id == added[0].item.id


@pytest.mark.asyncio
@pytest.mark.parametrize("custom", [False, True])
async def test_additional_namespace_tool_stream_preserves_call_identity(custom):
    from copy import deepcopy

    arguments = json.dumps({"content": "print('hello')"}) if custom else '{"value":7}'
    tool = {"type": "custom" if custom else "function", "name": "exec", "description": "Run code"}
    request_input = [
        {
            "type": "additional_tools",
            "role": "developer",
            "tools": [
                {"type": "namespace", "name": "functions", "tools": [tool]},
            ],
        },
        {"role": "user", "content": "Run the code"},
    ]
    original = deepcopy(request_input)
    chunks = [
        ModelResponseStream(
            id=CHAT_COMPLETION_ID,
            model="qwen3.8-flash-next",
            created=1748575031,
            choices=[
                StreamingChoices(
                    index=0,
                    delta=Delta(
                        role="assistant",
                        tool_calls=[
                            {
                                "index": 0,
                                "id": "call_exec",
                                "type": "function",
                                "function": {"name": "functions__exec", "arguments": arguments[:8]},
                            }
                        ],
                    ),
                )
            ],
        ),
        ModelResponseStream(
            id=CHAT_COMPLETION_ID,
            model="qwen3.8-flash-next",
            created=1748575031,
            choices=[
                StreamingChoices(
                    index=0,
                    delta=Delta(
                        tool_calls=[
                            {
                                "index": 0,
                                "function": {"arguments": arguments[8:]},
                            }
                        ]
                    ),
                )
            ],
        ),
        ModelResponseStream(
            id=CHAT_COMPLETION_ID,
            model="qwen3.8-flash-next",
            created=1748575031,
            choices=[StreamingChoices(index=0, delta=Delta(), finish_reason="tool_calls")],
        ),
    ]
    iterator = LiteLLMCompletionStreamingIterator(
        model="qwen3.8-flash-next",
        litellm_custom_stream_wrapper=_FakeStreamWrapper(chunks),
        request_input=request_input,
        responses_api_request={},
        custom_llm_provider="hosted_vllm",
    )
    events = [event async for event in iterator]
    item_type = "custom_tool_call" if custom else "function_call"
    added = [e.item for e in events if e.type == "response.output_item.added" and e.item.type == item_type]
    done = [e.item for e in events if e.type == "response.output_item.done" and e.item.type == item_type]
    completed = next(e.response for e in events if e.type == "response.completed")
    final = [item for item in completed.output if item.type == item_type]
    assert len(added) == len(done) == len(final) == 1
    for item in (*added, *done, *final):
        assert item.name == "exec"
        assert item.namespace == "functions"
        assert item.call_id == "call_exec"
        assert item.id == added[0].id
    if custom:
        assert done[0].input == final[0].input == "print('hello')"
        deltas = [e.delta for e in events if e.type == "response.custom_tool_call_input.delta"]
        assert "".join(deltas) == "print('hello')"
        assert not any(e.type == "response.function_call_arguments.delta" for e in events)
    else:
        assert done[0].arguments == final[0].arguments == arguments
    assert request_input == original


def _tool_call_chunk(finish_reason: str | None = None) -> ModelResponseStream:
    return ModelResponseStream(
        id=CHAT_COMPLETION_ID,
        created=1748575031,
        model="claude-haiku-4-5",
        object="chat.completion.chunk",
        choices=[
            StreamingChoices(
                index=0,
                delta=Delta(
                    role="assistant",
                    content=None,
                    tool_calls=[
                        {
                            "id": "call_pwd",
                            "type": "function",
                            "function": {"name": "run_command", "arguments": '{"command":"pwd"}'},
                            "index": 0,
                        }
                    ],
                ),
                finish_reason=finish_reason,
            )
        ],
    )


def test_streamed_named_tool_choice_is_echoed_in_responses_api_shape() -> None:
    iterator: Final = LiteLLMCompletionStreamingIterator(
        model="claude-haiku-4-5",
        litellm_custom_stream_wrapper=_FakeStreamWrapper([_tool_call_chunk(finish_reason="tool_calls")]),
        request_input="Run the command pwd.",
        responses_api_request={
            "tools": [{"type": "function", "name": "run_command", "parameters": {"type": "object"}}],
            "tool_choice": {"type": "function", "name": "run_command"},
        },
        custom_llm_provider="anthropic",
        litellm_metadata={},
    )

    events: Final = list(iterator)

    response_events: Final = [event for event in events if getattr(event, "type", None) in RESPONSE_ID_EVENT_TYPES]
    assert [event.type for event in response_events] == [
        "response.created",
        "response.in_progress",
        "response.completed",
    ]
    assert [event.response.tool_choice for event in response_events] == [
        {"type": "function", "name": "run_command"},
        {"type": "function", "name": "run_command"},
        {"type": "function", "name": "run_command"},
    ]
    assert any(getattr(event, "type", None) == "response.output_item.done" for event in events)


def test_streamed_unrecognized_tool_choice_is_echoed_as_auto() -> None:
    iterator: Final = LiteLLMCompletionStreamingIterator(
        model="claude-haiku-4-5",
        litellm_custom_stream_wrapper=_FakeStreamWrapper([_tool_call_chunk(finish_reason="tool_calls")]),
        request_input="Run the command pwd.",
        responses_api_request={
            "tools": [{"type": "function", "name": "run_command", "parameters": {"type": "object"}}],
            "tool_choice": "any",
        },
        custom_llm_provider="anthropic",
        litellm_metadata={},
    )

    response_events: Final = [
        event for event in iterator if getattr(event, "type", None) in RESPONSE_ID_EVENT_TYPES
    ]

    assert [event.response.tool_choice for event in response_events] == ["auto", "auto", "auto"]
