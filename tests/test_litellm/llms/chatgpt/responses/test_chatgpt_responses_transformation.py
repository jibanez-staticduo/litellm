"""
Tests for ChatGPT subscription Responses API transformation

Source: litellm/llms/chatgpt/responses/transformation.py
"""

import json
from copy import deepcopy
from unittest.mock import MagicMock, patch

import httpx
import pytest
from pydantic import BaseModel, model_serializer

import litellm
from litellm.llms.chatgpt.common_utils import get_chatgpt_session_id
from litellm.llms.chatgpt.responses.transformation import ChatGPTResponsesAPIConfig
from litellm.llms.openai.common_utils import OpenAIError
from litellm.main import responses_api_bridge_check
from litellm.types.router import GenericLiteLLMParams
from litellm.types.utils import LlmProviders
from litellm.utils import ProviderConfigManager


class TestChatGPTResponsesAPITransformation:
    @pytest.mark.parametrize("encrypted_content", [None, "", 123])
    def test_foreign_raw_reasoning_removed_without_changing_conversation(self, encrypted_content):
        history = [
            {"role": "user", "content": "Update the script"},
            {
                "type": "reasoning",
                "id": "qwen_reasoning",
                "summary": [],
                "content": [{"type": "reasoning_text", "text": "Inspect then patch."}],
                "encrypted_content": encrypted_content,
            },
            {"type": "function_call", "call_id": "call_exec", "name": "exec_command", "arguments": '{"cmd":"pwd"}'},
            {"type": "function_call_output", "call_id": "call_exec", "output": "/workspace"},
            {
                "type": "custom_tool_call",
                "call_id": "call_patch",
                "name": "apply_patch",
                "input": "*** Begin Patch\n*** End Patch",
            },
            {"type": "custom_tool_call_output", "call_id": "call_patch", "output": "Success"},
            {
                "type": "tool_search_call",
                "call_id": "call_search",
                "execution": "client",
                "arguments": {"query": "read file"},
            },
            {"type": "tool_search_output", "call_id": "call_search", "execution": "client", "tools": []},
            {"role": "assistant", "content": [{"type": "output_text", "text": "Patched."}]},
        ]
        original = deepcopy(history)
        request = ChatGPTResponsesAPIConfig().transform_responses_api_request(
            model="gpt-6-astra",
            input=history,
            response_api_optional_request_params={},
            litellm_params=GenericLiteLLMParams(),
            headers={},
        )

        assert request["input"] == [original[0], *original[2:]]
        assert history == original

    def test_encrypted_reasoning_preserved_without_raw_content(self):
        history = [
            {
                "type": "reasoning",
                "id": "rs_signed",
                "status": "completed",
                "encrypted_content": "opaque-signed-reasoning",
                "summary": [{"type": "summary_text", "text": "Checked the script."}],
                "content": [{"type": "reasoning_text", "text": "Raw reasoning."}],
            }
        ]
        original = deepcopy(history)
        request = ChatGPTResponsesAPIConfig().transform_responses_api_request(
            model="gpt-6-astra",
            input=history,
            response_api_optional_request_params={},
            litellm_params=GenericLiteLLMParams(),
            headers={},
        )

        assert request["input"] == [{key: value for key, value in original[0].items() if key != "content"}]
        assert history == original

    @pytest.mark.parametrize("content_fields", [{}, {"content": []}])
    def test_native_reasoning_without_raw_content_unchanged(self, content_fields):
        history = [
            {
                "type": "reasoning",
                "id": "rs_native",
                "summary": [],
                "encrypted_content": "native-signed-reasoning",
                **content_fields,
            }
        ]
        original = deepcopy(history)
        request = ChatGPTResponsesAPIConfig().transform_responses_api_request(
            model="gpt-6-astra",
            input=history,
            response_api_optional_request_params={},
            litellm_params=GenericLiteLLMParams(),
            headers={},
        )

        assert request["input"] == original
        assert history == original

    def test_reasoning_filter_preserves_caller_history_during_cache_cleanup(self):
        history = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Continue",
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
            }
        ]
        original = deepcopy(history)
        request = ChatGPTResponsesAPIConfig().transform_responses_api_request(
            model="gpt-6-astra",
            input=history,
            response_api_optional_request_params={},
            litellm_params=GenericLiteLLMParams(),
            headers={},
        )

        assert "cache_control" not in request["input"][0]["content"][0]
        assert history == original

    def test_guardian_preserves_strict_output_schema(self):
        text = {
            "format": {
                "type": "json_schema",
                "name": "review",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {"allowed": {"type": "boolean"}},
                    "required": ["allowed"],
                    "additionalProperties": False,
                },
            }
        }
        request = ChatGPTResponsesAPIConfig().transform_responses_api_request(
            model="codex-auto-review",
            input="Review the command pwd",
            response_api_optional_request_params={"text": text},
            litellm_params=GenericLiteLLMParams(),
            headers={},
        )
        assert request["text"] == text

    @pytest.mark.parametrize("input_value", ["hi", "", [{"role": "user", "content": "hi"}]])
    def test_chatgpt_responses_normalizes_string_input(self, input_value):
        request = ChatGPTResponsesAPIConfig().transform_responses_api_request(
            model="chatgpt/gpt-6-astra",
            input=input_value,
            response_api_optional_request_params={},
            litellm_params=GenericLiteLLMParams(),
            headers={},
        )

        expected = (
            [{"role": "user", "content": [{"type": "input_text", "text": input_value}]}]
            if isinstance(input_value, str)
            else input_value
        )
        assert request["input"] == expected

    @pytest.mark.parametrize("as_model", [False, True])
    @pytest.mark.parametrize(
        ("session_fields", "expected"),
        [
            ({"litellm_session_id": "explicit", "session_id": "session", "litellm_trace_id": "trace"}, "explicit"),
            ({"session_id": "session", "litellm_trace_id": "trace"}, "session"),
            ({"litellm_trace_id": "trace"}, "metadata-session"),
            ({"litellm_session_id": "", "session_id": 123}, "123"),
        ],
    )
    def test_session_id_does_not_serialize_recursive_metadata(self, as_model, session_fields, expected):
        metadata = {"session_id": "metadata-session"}
        metadata["history"] = metadata
        values = {**session_fields, "metadata": metadata}
        params = GenericLiteLLMParams(**values) if as_model else values

        assert get_chatgpt_session_id(params) == expected

    @pytest.mark.parametrize(
        ("session_fields", "expected"),
        [
            ({"litellm_trace_id": "trace", "litellm_call_id": "call"}, "trace"),
            ({"litellm_call_id": "call"}, "call"),
            ({}, None),
        ],
    )
    def test_session_id_does_not_serialize_unrelated_params(self, session_fields, expected):
        serialize_history = MagicMock(return_value={})

        class History(BaseModel):
            @model_serializer
            def serialize(self):
                return serialize_history()

        params = GenericLiteLLMParams(**session_fields, history=History())

        assert get_chatgpt_session_id(params) == expected
        serialize_history.assert_not_called()

    @pytest.mark.parametrize(
        "model_name",
        [
            "chatgpt/gpt-5.5",
            "chatgpt/gpt-5.6-luna",
            "chatgpt/gpt-5.6-sol",
            "chatgpt/gpt-5.6-terra",
            "chatgpt/gpt-5.4",
            "chatgpt/gpt-5.4-pro",
            "chatgpt/gpt-5.3-chat-latest",
            "chatgpt/gpt-5.3-instant",
            "chatgpt/gpt-5.3-codex",
            "chatgpt/gpt-5.3-codex-spark",
        ],
    )
    def test_chatgpt_provider_config_registration(self, model_name):
        config = ProviderConfigManager.get_provider_responses_api_config(
            model=model_name,
            provider=LlmProviders.CHATGPT,
        )

        assert config is not None
        assert isinstance(config, ChatGPTResponsesAPIConfig)
        assert config.custom_llm_provider == LlmProviders.CHATGPT

    @pytest.mark.parametrize(
        "model_name",
        [
            "chatgpt/gpt-5.5",
            "chatgpt/gpt-5.6-luna",
            "chatgpt/gpt-5.6-sol",
            "chatgpt/gpt-5.6-terra",
        ],
    )
    def test_chatgpt_responses_model_metadata(self, model_name: str, local_model_cost_map: None) -> None:
        model_info = litellm.get_model_info(model_name)

        assert model_info["litellm_provider"] == "chatgpt"
        assert model_info["mode"] == "responses"
        assert model_info["supported_endpoints"] == [
            "/v1/chat/completions",
            "/v1/responses",
        ]
        assert model_info["max_input_tokens"] == 1050000
        assert model_info["max_output_tokens"] == 128000

    @pytest.mark.parametrize(
        "model_name",
        [
            "gpt-5.5",
            "gpt-5.6-luna",
            "gpt-5.6-sol",
            "gpt-5.6-terra",
        ],
    )
    def test_chatgpt_models_bridge_chat_completions_to_responses(
        self, model_name: str, local_model_cost_map: None
    ) -> None:
        """A chat completions request for these models must take the Responses bridge.

        `gpt-5.6-*` also exists as an openai chat model, so an unregistered
        chatgpt model resolves to mode "chat" here and never reaches the bridge.
        """
        model_info, resolved_model = responses_api_bridge_check(
            model=model_name,
            custom_llm_provider="chatgpt",
        )

        assert model_info["mode"] == "responses"
        assert resolved_model == model_name

    @patch("litellm.llms.chatgpt.responses.transformation.Authenticator")
    def test_chatgpt_responses_endpoint_url(self, mock_authenticator_class):
        mock_auth_instance = MagicMock()
        mock_auth_instance.get_api_base.return_value = "https://chatgpt.example.com"
        mock_authenticator_class.return_value = mock_auth_instance

        config = ChatGPTResponsesAPIConfig()

        url = config.get_complete_url(api_base=None, litellm_params={})
        assert url == "https://chatgpt.example.com/responses"

        custom_url = config.get_complete_url(api_base="https://custom.chatgpt.com", litellm_params={})
        assert custom_url == "https://custom.chatgpt.com/responses"

        url_with_slash = config.get_complete_url(api_base="https://chatgpt.example.com/", litellm_params={})
        assert url_with_slash == "https://chatgpt.example.com/responses"

    @patch("litellm.llms.chatgpt.responses.transformation.Authenticator")
    def test_validate_environment_headers(self, mock_authenticator_class):
        mock_auth_instance = MagicMock()
        mock_auth_instance.get_access_token.return_value = "access-123"
        mock_auth_instance.get_account_id.return_value = "acct-123"
        mock_authenticator_class.return_value = mock_auth_instance

        config = ChatGPTResponsesAPIConfig()
        litellm_params = GenericLiteLLMParams(
            litellm_session_id="session-123",
            chatgpt_auth_profile="account2",
        )
        headers = config.validate_environment(
            headers={"originator": "custom-origin"},
            model="gpt-5.2",
            litellm_params=litellm_params,
        )

        assert headers["Authorization"] == "Bearer access-123"
        assert headers["ChatGPT-Account-Id"] == "acct-123"
        assert headers["originator"] == "custom-origin"
        assert headers["content-type"] == "application/json"
        assert headers["accept"] == "text/event-stream"
        assert headers["session_id"] == "session-123"
        assert mock_authenticator_class.call_args.args == (litellm_params,)

    @pytest.mark.parametrize(
        "model_name",
        [
            "chatgpt/gpt-5.2-codex",
            "chatgpt/gpt-5.3-codex",
        ],
    )
    def test_chatgpt_forces_streaming_and_reasoning_include(self, model_name):
        config = ChatGPTResponsesAPIConfig()
        request = config.transform_responses_api_request(
            model=model_name,
            input="hi",
            response_api_optional_request_params={},
            litellm_params=GenericLiteLLMParams(),
            headers={},
        )

        assert request["stream"] is True
        assert "reasoning.encrypted_content" in request["include"]
        assert request["instructions"].startswith("You are Codex, based on GPT-5.")

    def test_chatgpt_codex_responses_lite_disables_parallel_tool_calls(self):
        config = ChatGPTResponsesAPIConfig()
        request = config.transform_responses_api_request(
            model="chatgpt/gpt-5.6-sol",
            input="hi",
            response_api_optional_request_params={"parallel_tool_calls": True},
            litellm_params=GenericLiteLLMParams(),
            headers={"x-openai-internal-codex-responses-lite": "true"},
        )

        assert request["parallel_tool_calls"] is False

        standard_request = config.transform_responses_api_request(
            model="chatgpt/gpt-5.6-sol",
            input="hi",
            response_api_optional_request_params={"parallel_tool_calls": True},
            litellm_params=GenericLiteLLMParams(),
            headers={},
        )

        assert "parallel_tool_calls" not in standard_request

    @pytest.mark.parametrize(
        "model_name",
        [
            "chatgpt/gpt-5.2-codex",
            "chatgpt/gpt-5.3-codex-spark",
        ],
    )
    def test_chatgpt_drops_unsupported_responses_params(self, model_name):
        config = ChatGPTResponsesAPIConfig()
        request = config.transform_responses_api_request(
            model=model_name,
            input="hi",
            response_api_optional_request_params={
                # unsupported by ChatGPT Codex
                "user": "user_123",
                "temperature": 0.2,
                "top_p": 0.9,
                "context_management": [{"type": "compaction", "compact_threshold": 200000}],
                "metadata": {"foo": "bar"},
                "max_output_tokens": 123,
                "stream_options": {"include_usage": True},
                # supported and should be preserved
                "truncation": "auto",
                "previous_response_id": "resp_123",
                "reasoning": {"effort": "medium"},
                "tools": [{"type": "function", "function": {"name": "hello"}}],
                "tool_choice": {"type": "function", "function": {"name": "hello"}},
            },
            litellm_params=GenericLiteLLMParams(),
            headers={},
        )

        assert "user" not in request
        assert "temperature" not in request
        assert "top_p" not in request
        assert "context_management" not in request
        assert "metadata" not in request
        assert "max_output_tokens" not in request
        assert "stream_options" not in request

        assert request["truncation"] == "auto"
        assert request["previous_response_id"] == "resp_123"
        assert request["reasoning"] == {"effort": "medium"}
        assert request["tools"] == [{"type": "function", "function": {"name": "hello"}}]
        assert request["tool_choice"] == {
            "type": "function",
            "function": {"name": "hello"},
        }

    @pytest.mark.parametrize(
        ("model_name", "response_model"),
        [
            ("chatgpt/gpt-5.2-codex", "gpt-5.2-codex"),
            ("chatgpt/gpt-5.3-codex", "gpt-5.3-codex"),
        ],
    )
    def test_chatgpt_non_stream_sse_response_parsing(self, model_name: str, response_model: str):
        config = ChatGPTResponsesAPIConfig()
        response_payload = {
            "id": "resp_test",
            "object": "response",
            "created_at": 1700000000,
            "status": "completed",
            "model": response_model,
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "Hello!"}],
                }
            ],
        }
        sse_body = "\n".join(
            [
                f"data: {json.dumps({'type': 'response.completed', 'response': response_payload})}",
                "data: [DONE]",
                "",
            ]
        )
        raw_response = httpx.Response(200, headers={"content-type": "text/event-stream"}, text=sse_body)
        logging_obj = MagicMock()

        parsed = config.transform_response_api_response(
            model=model_name,
            raw_response=raw_response,
            logging_obj=logging_obj,
        )

        assert parsed.output_text == "Hello!"

    @pytest.mark.parametrize(
        ("model_name", "response_model"),
        [
            ("chatgpt/gpt-5.2-codex", "gpt-5.2-codex"),
            ("chatgpt/gpt-5.3-codex", "gpt-5.3-codex"),
        ],
    )
    def test_chatgpt_non_stream_sse_response_recovers_output_items(self, model_name: str, response_model: str):
        config = ChatGPTResponsesAPIConfig()
        response_payload = {
            "id": "resp_test",
            "object": "response",
            "created_at": 1700000000,
            "status": "completed",
            "model": response_model,
            "output": [],
        }
        streamed_output_item = {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": "Hello from stream!"}],
        }
        sse_body = "\n".join(
            [
                f"data: {json.dumps({'type': 'response.output_item.done', 'output_index': 0, 'item': streamed_output_item})}",
                f"data: {json.dumps({'type': 'response.completed', 'response': response_payload})}",
                "data: [DONE]",
                "",
            ]
        )
        raw_response = httpx.Response(200, headers={"content-type": "text/event-stream"}, text=sse_body)
        logging_obj = MagicMock()

        parsed = config.transform_response_api_response(
            model=model_name,
            raw_response=raw_response,
            logging_obj=logging_obj,
        )

        assert parsed.output_text == "Hello from stream!"

    def test_chatgpt_non_stream_sse_recovers_whitespace_padded_chunks(self):
        """Chunks with leading whitespace before `data:` must still parse.

        `_strip_sse_data_from_chunk` only matches the prefix at position 0,
        so without an outer `.strip()` such chunks would fail JSON parsing
        and silently drop the contained event.
        """
        config = ChatGPTResponsesAPIConfig()
        response_payload = {
            "id": "resp_test",
            "object": "response",
            "created_at": 1700000000,
            "status": "completed",
            "model": "gpt-5.4",
            "output": [],
        }
        streamed_output_item = {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": "Recovered from padded"}],
        }
        sse_body = "\n".join(
            [
                f"   data:  {json.dumps({'type': 'response.output_item.done', 'output_index': 0, 'item': streamed_output_item})}   ",
                f"\tdata: {json.dumps({'type': 'response.completed', 'response': response_payload})}",
                "data: [DONE]",
                "",
            ]
        )
        raw_response = httpx.Response(200, headers={"content-type": "text/event-stream"}, text=sse_body)
        logging_obj = MagicMock()

        parsed = config.transform_response_api_response(
            model="chatgpt/gpt-5.4",
            raw_response=raw_response,
            logging_obj=logging_obj,
        )

        assert parsed.output_text == "Recovered from padded"

    def test_chatgpt_accumulates_multiple_output_item_done_events(self):
        config = ChatGPTResponsesAPIConfig()
        reasoning_item = {
            "id": "rs_test",
            "type": "reasoning",
            "summary": [],
            "encrypted_content": "ENCRYPTED",
        }
        message_item = {
            "id": "msg_test",
            "type": "message",
            "role": "assistant",
            "status": "completed",
            "content": [
                {
                    "type": "output_text",
                    "text": "hello world",
                    "annotations": [],
                }
            ],
        }
        response_payload = {
            "id": "resp_test",
            "object": "response",
            "created_at": 1700000000,
            "status": "completed",
            "model": "gpt-5.3-codex",
            "output": [],
            "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        }
        sse_body = "\n".join(
            [
                f"data: {json.dumps({'type': 'response.output_item.done', 'output_index': 0, 'item': reasoning_item})}",
                f"data: {json.dumps({'type': 'response.output_item.done', 'output_index': 1, 'item': message_item})}",
                f"data: {json.dumps({'type': 'response.completed', 'response': response_payload})}",
                "data: [DONE]",
                "",
            ]
        )
        raw_response = httpx.Response(200, headers={"content-type": "text/event-stream"}, text=sse_body)

        parsed = config.transform_response_api_response(
            model="chatgpt/gpt-5.3-codex",
            raw_response=raw_response,
            logging_obj=MagicMock(),
        )

        assert len(parsed.output) == 2
        assert parsed.output[0].type == "reasoning"
        assert parsed.output[1].type == "message"
        assert parsed.output_text == "hello world"

    def test_chatgpt_prefers_nonempty_completed_output_over_accumulated(self):
        config = ChatGPTResponsesAPIConfig()
        stray_item = {
            "id": "msg_stray",
            "type": "message",
            "role": "assistant",
            "status": "completed",
            "content": [{"type": "output_text", "text": "stray", "annotations": []}],
        }
        canonical_item = {
            "id": "msg_canonical",
            "type": "message",
            "role": "assistant",
            "status": "completed",
            "content": [{"type": "output_text", "text": "canonical", "annotations": []}],
        }
        response_payload = {
            "id": "resp_test",
            "object": "response",
            "created_at": 1700000000,
            "status": "completed",
            "model": "gpt-5.3-codex",
            "output": [canonical_item],
        }
        sse_body = "\n".join(
            [
                f"data: {json.dumps({'type': 'response.output_item.done', 'output_index': 0, 'item': stray_item})}",
                f"data: {json.dumps({'type': 'response.completed', 'response': response_payload})}",
                "data: [DONE]",
                "",
            ]
        )
        raw_response = httpx.Response(200, headers={"content-type": "text/event-stream"}, text=sse_body)

        parsed = config.transform_response_api_response(
            model="chatgpt/gpt-5.3-codex",
            raw_response=raw_response,
            logging_obj=MagicMock(),
        )

        assert len(parsed.output) == 1
        assert parsed.output_text == "canonical"

    @pytest.mark.parametrize(
        "error_chunk",
        [
            {
                "type": "response.failed",
                "response": {"error": {"message": "ChatGPT upstream failed"}},
            },
            {
                "type": "error",
                "error": {"message": "ChatGPT upstream failed"},
            },
        ],
    )
    def test_chatgpt_non_stream_sse_response_raises_openai_error(self, error_chunk):
        config = ChatGPTResponsesAPIConfig()
        sse_body = "\n".join(
            [
                f"data: {json.dumps(error_chunk)}",
                "data: [DONE]",
                "",
            ]
        )
        raw_response = httpx.Response(502, headers={"content-type": "text/event-stream"}, text=sse_body)
        logging_obj = MagicMock()

        with pytest.raises(OpenAIError) as exc_info:
            config.transform_response_api_response(
                model="chatgpt/gpt-5.4",
                raw_response=raw_response,
                logging_obj=logging_obj,
            )

        assert "ChatGPT upstream failed" in str(exc_info.value)
        assert exc_info.value.status_code == 502
