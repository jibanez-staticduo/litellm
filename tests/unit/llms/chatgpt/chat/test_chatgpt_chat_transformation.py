from typing import Final
from unittest.mock import MagicMock, patch

import pytest

import litellm
from litellm.llms.chatgpt.chat.transformation import ChatGPTConfig
from litellm.types.llms.openai import ResponsesAPIResponse


@patch(
    "litellm.llms.chatgpt.chat.transformation.Authenticator"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
def test_chatgpt_chat_auth_uses_litellm_params_for_token_and_account(mock_authenticator_class):
    mock_auth_instance = MagicMock()
    mock_auth_instance.get_api_base.return_value = "https://chatgpt.example.com"
    mock_auth_instance.get_access_token.return_value = "access-123"
    mock_auth_instance.get_account_id.return_value = "acct-123"
    mock_authenticator_class.return_value = mock_auth_instance
    litellm_params = {
        "custom_llm_provider": "chatgpt",
        "chatgpt_auth_profile": "account2",
        "litellm_session_id": "session-123",
    }

    config = ChatGPTConfig()
    api_base, api_key, provider = config.get_openai_compatible_provider_info(
        model="gpt-5.4",
        api_base=None,
        api_key=None,
        custom_llm_provider="chatgpt",
        litellm_params=litellm_params,
    )
    headers = config.validate_environment(
        headers={},
        model="gpt-5.4",
        messages=[],
        optional_params={},
        litellm_params=litellm_params,
        api_key=api_key,
        api_base=api_base,
    )

    assert api_base == "https://chatgpt.example.com"
    assert api_key == "access-123"
    assert provider == "chatgpt"
    assert headers["Authorization"] == "Bearer access-123"
    assert headers["ChatGPT-Account-Id"] == "acct-123"
    assert headers["session_id"] == "session-123"
    assert mock_authenticator_class.call_args_list[0].args == (litellm_params,)
    assert mock_authenticator_class.call_args_list[1].args == (litellm_params,)


@patch(
    "litellm.responses.main.base_llm_http_handler.response_api_handler"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
@patch(
    "litellm.llms.chatgpt.responses.transformation.Authenticator"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
@patch(
    "litellm.llms.chatgpt.chat.transformation.Authenticator"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
def test_litellm_completion_preserves_chatgpt_auth_params_into_provider(
    mock_chat_authenticator_class, mock_responses_authenticator_class, mock_response_api_handler, tmp_path
):
    mock_auth_instance = MagicMock()
    mock_auth_instance.get_api_base.return_value = "https://chatgpt.example.com"
    mock_auth_instance.get_access_token.return_value = "access-123"
    mock_auth_instance.get_account_id.return_value = "acct-123"
    mock_chat_authenticator_class.return_value = mock_auth_instance
    mock_responses_authenticator_class.return_value = mock_auth_instance
    response: Final = ResponsesAPIResponse(
        id="resp_123",
        created_at=123,
        model="non-responses-test-model",
        object="response",
        output=[
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "ok"}],
            }
        ],
    )

    def provider_call(**kwargs):
        provider_config = kwargs["responses_api_provider_config"]
        headers = provider_config.validate_environment(
            headers={}, model=kwargs["model"], litellm_params=kwargs["litellm_params"]
        )
        assert kwargs["custom_llm_provider"] == "chatgpt"
        assert kwargs["litellm_params"].chatgpt_auth_profile == "account2"
        assert kwargs["litellm_params"].chatgpt_token_dir == token_dir
        assert kwargs["litellm_params"].chatgpt_auth_file == auth_file
        assert headers["Authorization"] == "Bearer access-123"
        assert headers["ChatGPT-Account-Id"] == "acct-123"
        return response

    mock_response_api_handler.side_effect = provider_call
    token_dir = str(tmp_path / "tokens")
    auth_file = "account2-auth.json"

    litellm.completion(
        model="chatgpt/non-responses-test-model",
        messages=[{"role": "user", "content": "hi"}],
        chatgpt_auth_profile="account2",
        chatgpt_token_dir=token_dir,
        chatgpt_auth_file=auth_file,
    )

    assert mock_response_api_handler.call_count == 1
    litellm_params = mock_response_api_handler.call_args.kwargs["litellm_params"]
    assert mock_chat_authenticator_class.call_args.args[0].chatgpt_auth_profile == "account2"
    assert mock_chat_authenticator_class.call_args.args[0].chatgpt_token_dir == token_dir
    assert mock_chat_authenticator_class.call_args.args[0].chatgpt_auth_file == auth_file
    assert mock_responses_authenticator_class.call_args.args == (litellm_params,)


@patch(
    "litellm.responses.main.base_llm_http_handler.response_api_handler"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
@patch(
    "litellm.llms.chatgpt.responses.transformation.Authenticator"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
@patch(
    "litellm.llms.chatgpt.chat.transformation.Authenticator"
)  # test-quality-ok: isolates router deployment resolution during initialization
def test_router_deployment_chatgpt_auth_params_survive_into_provider(
    mock_chat_authenticator_class, mock_responses_authenticator_class, mock_response_api_handler, tmp_path
):
    mock_auth_instance = MagicMock()
    mock_auth_instance.get_api_base.return_value = "https://chatgpt.example.com"
    mock_auth_instance.get_access_token.return_value = "access-123"
    mock_auth_instance.get_account_id.return_value = "acct-123"
    mock_chat_authenticator_class.return_value = mock_auth_instance
    mock_responses_authenticator_class.return_value = mock_auth_instance
    token_dir = str(tmp_path / "tokens")
    auth_file = "account2-auth.json"
    response: Final = ResponsesAPIResponse(
        id="resp_123",
        created_at=123,
        model="non-responses-test-model",
        object="response",
        output=[
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "ok"}],
            }
        ],
    )

    def provider_call(**kwargs):
        provider_config = kwargs["responses_api_provider_config"]
        headers = provider_config.validate_environment(
            headers={}, model=kwargs["model"], litellm_params=kwargs["litellm_params"]
        )
        assert kwargs["custom_llm_provider"] == "chatgpt"
        assert kwargs["litellm_params"].chatgpt_auth_profile == "account2"
        assert kwargs["litellm_params"].chatgpt_token_dir == token_dir
        assert kwargs["litellm_params"].chatgpt_auth_file == auth_file
        assert headers["Authorization"] == "Bearer access-123"
        assert headers["ChatGPT-Account-Id"] == "acct-123"
        return response

    mock_response_api_handler.side_effect = provider_call
    router = litellm.Router(
        model_list=[
            {
                "model_name": "profile-alias",
                "litellm_params": {
                    "model": "chatgpt/non-responses-test-model",
                    "chatgpt_auth_profile": "account2",
                    "chatgpt_token_dir": token_dir,
                    "chatgpt_auth_file": auth_file,
                },
            }
        ]
    )

    router.completion(
        model="profile-alias",
        messages=[{"role": "user", "content": "hi"}],
    )

    assert mock_response_api_handler.call_count == 1
    litellm_params = mock_response_api_handler.call_args.kwargs["litellm_params"]
    assert mock_chat_authenticator_class.call_args.args[0].chatgpt_auth_profile == "account2"
    assert mock_chat_authenticator_class.call_args.args[0].chatgpt_token_dir == token_dir
    assert mock_chat_authenticator_class.call_args.args[0].chatgpt_auth_file == auth_file
    assert mock_responses_authenticator_class.call_args.args == (litellm_params,)


@patch(
    "litellm.responses.main.base_llm_http_handler.response_api_handler"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
@patch(
    "litellm.llms.chatgpt.chat.transformation.Authenticator"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
def test_chat_completion_to_responses_bridge_preserves_chatgpt_auth_params(
    mock_authenticator_class,
    mock_response_api_handler,
    tmp_path,
):
    mock_auth_instance = MagicMock()
    mock_auth_instance.get_api_base.return_value = "https://chatgpt.example.com"
    mock_auth_instance.get_access_token.return_value = "access-123"
    mock_auth_instance.get_account_id.return_value = "acct-123"
    mock_authenticator_class.return_value = mock_auth_instance
    mock_response_api_handler.return_value = ResponsesAPIResponse(
        id="resp_123",
        created_at=123,
        model="gpt-5.4",
        object="response",
        output=[
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "ok"}],
            }
        ],
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
    )
    token_dir = str(tmp_path / "tokens")
    auth_file = "account2-auth.json"

    litellm.completion(
        model="chatgpt/responses/gpt-5.4",
        messages=[{"role": "user", "content": "hi"}],
        chatgpt_auth_profile="account2",
        chatgpt_token_dir=token_dir,
        chatgpt_auth_file=auth_file,
    )

    litellm_params = mock_response_api_handler.call_args.kwargs["litellm_params"]
    assert litellm_params.chatgpt_auth_profile == "account2"
    assert litellm_params.chatgpt_token_dir == token_dir
    assert litellm_params.chatgpt_auth_file == auth_file


@pytest.mark.parametrize("param", ["chatgpt_auth_profile", "chatgpt_token_dir", "chatgpt_auth_file"])
def test_chatgpt_auth_params_are_litellm_reserved_params(param):
    from litellm.types.utils import all_litellm_params

    assert param in all_litellm_params


@patch(
    "litellm.llms.chatgpt.chat.transformation.Authenticator"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
def test_chatgpt_chat_arbitrary_model_alias_keeps_chatgpt_provider(mock_authenticator_class):
    mock_auth_instance = MagicMock()
    mock_auth_instance.get_api_base.return_value = "https://chatgpt.example.com"
    mock_auth_instance.get_access_token.return_value = "access-123"
    mock_authenticator_class.return_value = mock_auth_instance

    _, _, provider = ChatGPTConfig()._get_openai_compatible_provider_info(
        model="arbitrary/customer-facing-name",
        api_base=None,
        api_key=None,
        custom_llm_provider="chatgpt",
        litellm_params={"chatgpt_auth_profile": "account2"},
    )

    assert provider == "chatgpt"
