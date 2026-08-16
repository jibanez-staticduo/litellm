import json
from datetime import datetime
from types import SimpleNamespace

import httpx

from litellm.llms.chatgpt.responses.transformation import ChatGPTResponsesAPIConfig
from litellm.responses.streaming_iterator import BaseResponsesAPIStreamingIterator
from litellm.types.llms.openai import ResponsesAPIStreamEvents


class _NoopStreamingIterator(BaseResponsesAPIStreamingIterator):
    def _handle_logging_completed_response(self):
        pass


class _LoggingStub(SimpleNamespace):
    def _update_completion_start_time(self, completion_start_time):
        self.completion_start_time = completion_start_time


def _item_to_dict(item):
    if isinstance(item, dict):
        return item
    return item.model_dump()


class _NormalizingChatGPTResponsesAPIConfig(ChatGPTResponsesAPIConfig):
    def transform_streaming_response(self, model, parsed_chunk, logging_obj):
        event = super().transform_streaming_response(model, parsed_chunk, logging_obj)
        if getattr(event, "type", None) != ResponsesAPIStreamEvents.OUTPUT_ITEM_DONE:
            return event
        item = getattr(event, "item", None)
        content = getattr(item, "content", None)
        if content:
            if isinstance(content[0], dict):
                content[0]["text"] = "Normalized by provider"
            else:
                setattr(content[0], "text", "Normalized by provider")
        return event


def _make_iterator(config=None, litellm_metadata=None, custom_llm_provider=None):
    return _NoopStreamingIterator(
        response=httpx.Response(200),
        model="gpt-5.5",
        responses_api_provider_config=config or ChatGPTResponsesAPIConfig(),
        logging_obj=_LoggingStub(
            completion_start_time=None,
            model_call_details={},
            start_time=datetime.now(),
        ),
        litellm_metadata=litellm_metadata,
        custom_llm_provider=custom_llm_provider,
    )


def _message_item(text, item_id="msg_test"):
    return {
        "id": item_id,
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": text, "annotations": []}],
    }


def _response_payload(output):
    return {
        "id": "resp_test",
        "object": "response",
        "created_at": 1700000000,
        "status": "completed",
        "model": "gpt-5.5",
        "output": output,
        "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
    }


def _process_event(iterator, event):
    iterator._process_chunk(json.dumps(event))


def _complete(iterator, output=None):
    _process_event(iterator, {"type": "response.completed", "response": _response_payload(output or [])})


def _completed_output(iterator):
    return [_item_to_dict(item) for item in iterator.completed_response.response.output]


def test_completed_stream_response_recovers_empty_output_from_output_item_done():
    iterator = _make_iterator()

    _process_event(
        iterator,
        {
            "type": "response.output_item.done",
            "output_index": 0,
            "item": _message_item("Recovered from stream"),
        },
    )
    _complete(iterator)

    output = _completed_output(iterator)

    assert len(output) == 1
    assert output[0]["type"] == "message"
    assert output[0]["content"][0]["text"] == "Recovered from stream"


def test_completed_stream_response_recovers_empty_output_from_output_text_done_only():
    iterator = _make_iterator()

    _process_event(
        iterator,
        {
            "type": "response.output_text.done",
            "output_index": 0,
            "content_index": 0,
            "item_id": "msg_text_only",
            "text": "Recovered from text event",
        },
    )
    _complete(iterator)

    output = _completed_output(iterator)

    assert len(output) == 1
    assert output[0]["id"] == "msg_text_only"
    assert output[0]["content"][0]["text"] == "Recovered from text event"


def test_completed_stream_response_prefers_output_item_done_over_output_text_done():
    iterator = _make_iterator()

    _process_event(
        iterator,
        {
            "type": "response.output_text.done",
            "output_index": 0,
            "content_index": 0,
            "item_id": "msg_text_only",
            "text": "text only loses",
        },
    )
    _process_event(
        iterator,
        {
            "type": "response.output_item.done",
            "output_index": 0,
            "item": _message_item("item wins", "msg_item"),
        },
    )
    _complete(iterator)

    output = _completed_output(iterator)

    assert len(output) == 1
    assert output[0]["id"] == "msg_item"
    assert output[0]["content"][0]["text"] == "item wins"


def test_completed_stream_response_keeps_non_empty_completed_output():
    iterator = _make_iterator()

    _process_event(
        iterator,
        {
            "type": "response.output_item.done",
            "output_index": 0,
            "item": _message_item("streamed item"),
        },
    )
    _complete(iterator, [_message_item("canonical completed item", "msg_completed")])

    output = _completed_output(iterator)

    assert len(output) == 1
    assert output[0]["id"] == "msg_completed"
    assert output[0]["content"][0]["text"] == "canonical completed item"


def test_recovered_output_uses_provider_normalized_streaming_event():
    iterator = _make_iterator(config=_NormalizingChatGPTResponsesAPIConfig())

    _process_event(
        iterator,
        {
            "type": "response.output_item.done",
            "output_index": 0,
            "item": _message_item("raw provider text"),
        },
    )
    _complete(iterator)

    output = _completed_output(iterator)

    assert output[0]["content"][0]["text"] == "Normalized by provider"


def test_recovered_output_uses_post_processed_streaming_event():
    iterator = _make_iterator(
        litellm_metadata={
            "encrypted_content_affinity_enabled": True,
            "model_info": {"id": "model-id"},
        },
        custom_llm_provider="chatgpt",
    )
    reasoning_item = {
        "id": "rs_test",
        "type": "reasoning",
        "summary": [],
        "encrypted_content": "ciphertext",
    }

    _process_event(
        iterator,
        {
            "type": "response.output_item.done",
            "output_index": 0,
            "item": reasoning_item,
        },
    )
    _complete(iterator)

    output = _completed_output(iterator)

    assert output[0]["encrypted_content"].startswith("litellm_enc:")
