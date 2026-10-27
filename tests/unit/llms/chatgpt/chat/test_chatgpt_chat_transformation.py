import asyncio
import base64
import json
from pathlib import Path
from types import MappingProxyType
from typing import Final
from unittest.mock import MagicMock, patch

import httpx
import pytest
import respx

import litellm
from litellm.integrations.dotprompt.dotprompt_manager import DotpromptManager
from litellm.litellm_core_utils.get_llm_provider_logic import get_llm_provider
from litellm.llms.chatgpt.authenticator import get_chatgpt_auth_file
from litellm.llms.chatgpt.chat.transformation import ChatGPTConfig
from litellm.llms.chatgpt.common_utils import ChatGPTAuthError
from litellm.types.llms.openai import ResponsesAPIResponse
from litellm.types.router import GenericLiteLLMParams


def _client_token(account_id: str) -> str:
    claims = json.dumps({"https://api.openai.com/auth": {"chatgpt_account_id": account_id}}).encode()
    payload = base64.urlsafe_b64encode(claims).decode().rstrip("=")
    return f"header.{payload}.signature"


@patch(
    "litellm.llms.chatgpt.chat.transformation.get_cached_authenticator"
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
    assert mock_authenticator_class.call_args_list[0].args == (get_chatgpt_auth_file(litellm_params),)
    assert mock_authenticator_class.call_args_list[1].args == (get_chatgpt_auth_file(litellm_params),)


def test_chatgpt_chat_provider_forwards_client_subscription_without_gateway_login():
    from litellm.llms.chatgpt.common_utils import CHATGPT_API_BASE

    token = _client_token("acct-client")
    config = ChatGPTConfig()
    params = {
        "provider_specific_header": {
            "custom_llm_provider": "chatgpt",
            "extra_headers": {"authorization": f"Bearer {token}", "x-litellm-api-key": "gateway"},
        }
    }

    assert config._get_openai_compatible_provider_info("gpt-5.4", None, None, "chatgpt", params) == (
        CHATGPT_API_BASE,
        token,
        "chatgpt",
    )


def test_chatgpt_chat_provider_rejects_client_subscription_custom_host():
    token = _client_token("acct-client")
    config = ChatGPTConfig()
    params = {"extra_headers": {"Authorization": f"Bearer {token}"}}

    with pytest.raises(ChatGPTAuthError, match="official HTTPS ChatGPT endpoint"):
        config._get_openai_compatible_provider_info("gpt-5.4", "https://attacker.example", None, "chatgpt", params)


GATEWAY_BASE = "https://chatgpt.example/backend-api/codex"


def _gateway_authenticator() -> MagicMock:
    authenticator = MagicMock()
    authenticator.get_api_base.return_value = GATEWAY_BASE
    authenticator.get_access_token.return_value = "gateway-access-token"
    return authenticator


def _provider_info(config: ChatGPTConfig, api_base: str | None, api_key: str | None):
    return config._get_openai_compatible_provider_info(
        model="gpt-5.4", api_base=api_base, api_key=api_key, custom_llm_provider="chatgpt"
    )


class TestChatGPTChatProviderInfo:
    def test_configured_key_uses_configured_base_without_gateway_login(self):
        authenticator = _gateway_authenticator()
        config = ChatGPTConfig(authenticator=authenticator)
        assert _provider_info(config, "http://127.0.0.1:9999", "configured-key") == (
            "http://127.0.0.1:9999",
            "configured-key",
            "chatgpt",
        )
        authenticator.get_access_token.assert_not_called()

    def test_configured_key_without_base_uses_gateway_base(self):
        assert _provider_info(ChatGPTConfig(authenticator=_gateway_authenticator()), None, "configured-key") == (
            GATEWAY_BASE,
            "configured-key",
            "chatgpt",
        )

    def test_gateway_login_is_never_sent_to_custom_base(self):
        assert _provider_info(
            ChatGPTConfig(authenticator=_gateway_authenticator()), "http://attacker.example", None
        ) == (
            "http://attacker.example",
            "gateway-access-token",
            "chatgpt",
        )

    def test_missing_gateway_login_raises_authentication_error(self):
        authenticator = _gateway_authenticator()
        authenticator.get_access_token.side_effect = litellm.AuthenticationError(
            model="gpt-5.4", llm_provider="chatgpt", message="not logged in"
        )
        with pytest.raises(litellm.AuthenticationError, match="not logged in"):
            _provider_info(ChatGPTConfig(authenticator=authenticator), None, None)


@patch(
    "litellm.responses.main.base_llm_http_handler.response_api_handler"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
@patch(
    "litellm.llms.chatgpt.responses.transformation.get_cached_authenticator"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
@patch(
    "litellm.llms.chatgpt.chat.transformation.get_cached_authenticator"
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
    assert mock_chat_authenticator_class.call_args.args == (get_chatgpt_auth_file(litellm_params),)
    assert mock_responses_authenticator_class.call_args.args == (get_chatgpt_auth_file(litellm_params),)


def test_validate_environment_uses_resolved_oauth_token_without_auth_file():
    authenticator = _gateway_authenticator()
    headers = ChatGPTConfig(authenticator=authenticator).validate_environment(
        headers={}, model="gpt-5.4", messages=[], optional_params={}, litellm_params={}
    )

    assert headers["Authorization"] == "Bearer gateway-access-token"


@patch(
    "litellm.responses.main.base_llm_http_handler.response_api_handler"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
@patch(
    "litellm.llms.chatgpt.responses.transformation.get_cached_authenticator"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
@patch(
    "litellm.llms.chatgpt.chat.transformation.get_cached_authenticator"
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
    assert mock_chat_authenticator_class.call_args.args == (get_chatgpt_auth_file(litellm_params),)
    assert mock_responses_authenticator_class.call_args.args == (get_chatgpt_auth_file(litellm_params),)


@patch(
    "litellm.responses.main.base_llm_http_handler.response_api_handler"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
@patch(
    "litellm.llms.chatgpt.chat.transformation.get_cached_authenticator"
)  # test-quality-ok: isolates the external or process-global boundary exercised by this regression
def test_chat_completion_to_responses_bridge_preserves_chatgpt_auth_params(
    mock_authenticator_class, mock_response_api_handler, tmp_path
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


def test_chatgpt_chat_arbitrary_model_alias_keeps_chatgpt_provider():
    mock_auth_instance = MagicMock()
    mock_auth_instance.get_api_base.return_value = "https://chatgpt.example.com"
    mock_auth_instance.get_access_token.return_value = "access-123"
    _, _, provider = ChatGPTConfig(authenticator=mock_auth_instance)._get_openai_compatible_provider_info(
        model="arbitrary/customer-facing-name",
        api_base=None,
        api_key=None,
        custom_llm_provider="chatgpt",
        litellm_params={},
    )

    assert provider == "chatgpt"


def _write_auth_record(path: Path, token: str, account_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "access_token": token,
                "account_id": account_id,
                "expires_at": 4102444800,
            }
        )
    )


@pytest.fixture
def auth_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    monkeypatch.setattr("time.time", lambda: 1700000000)
    default_dir: Final = tmp_path / "default"
    monkeypatch.setenv("CHATGPT_TOKEN_DIR", str(default_dir))
    monkeypatch.delenv("CHATGPT_AUTH_FILE", raising=False)
    _write_auth_record(default_dir / "auth.json", "token-default", "acct-default")
    file_a: Final = tmp_path / "account-a" / "auth.json"
    file_b: Final = tmp_path / "account-b" / "auth.json"
    _write_auth_record(file_a, "token-a", "acct-a")
    _write_auth_record(file_b, "token-b", "acct-b")
    return file_a, file_b


def _subscription_response(request: httpx.Request) -> httpx.Response:
    account: Final = request.headers["ChatGPT-Account-Id"]
    assert request.headers["Authorization"] in (
        f"Bearer token-{account.removeprefix('acct-')}",
        f"Bearer {_client_token(account)}",
    )
    assert "chatgpt_auth_file" not in request.content.decode()
    message: Final = {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": account, "annotations": []}],
    }
    response: Final = {
        "id": "resp_test",
        "object": "response",
        "created_at": 1700000000,
        "status": "completed",
        "model": "gpt-6.1-sol",
        "output": [message],
        "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
    }
    events: Final = (
        {"type": "response.created", "response": {**response, "status": "in_progress", "output": []}},
        {
            "type": "response.output_text.delta",
            "item_id": "msg_test",
            "output_index": 0,
            "content_index": 0,
            "delta": account,
        },
        {"type": "response.output_item.done", "output_index": 0, "item": message},
        {"type": "response.completed", "response": response},
    )
    return httpx.Response(
        200,
        text="".join(f"data: {json.dumps(event)}\n\n" for event in events),
        headers={"content-type": "text/event-stream"},
    )


class TestChatGPTMultiAccountChat:
    def test_validate_environment_uses_per_model_auth_file(self, auth_files: tuple[Path, Path]) -> None:
        file_a, file_b = auth_files
        config: Final = ChatGPTConfig()

        headers_a: Final = config.validate_environment(
            headers={},
            model="gpt-6.1-sol",
            messages=[],
            optional_params={},
            litellm_params={"chatgpt_auth_file": str(file_a)},
            api_key=None,
        )
        headers_b: Final = config.validate_environment(
            headers={},
            model="gpt-6.1-sol",
            messages=[],
            optional_params={},
            litellm_params={"chatgpt_auth_file": str(file_b)},
            api_key=None,
        )

        assert headers_a["Authorization"] == "Bearer token-a"
        assert headers_a["ChatGPT-Account-Id"] == "acct-a"
        assert headers_b["Authorization"] == "Bearer token-b"
        assert headers_b["ChatGPT-Account-Id"] == "acct-b"

    def test_validate_environment_defaults_to_global_auth_file(self, auth_files: tuple[Path, Path]) -> None:
        config: Final = ChatGPTConfig()

        headers: Final = config.validate_environment(
            headers={},
            model="gpt-6.1-sol",
            messages=[],
            optional_params={},
            litellm_params={},
            api_key="token-default",
        )

        assert headers["Authorization"] == "Bearer token-default"
        assert headers["ChatGPT-Account-Id"] == "acct-default"

    def test_provider_info_uses_per_model_auth_file(self, auth_files: tuple[Path, Path]) -> None:
        file_a, _ = auth_files
        config: Final = ChatGPTConfig()

        _, per_model_key, _ = config._get_openai_compatible_provider_info(
            "gpt-6.1-sol", None, None, "chatgpt", {"chatgpt_auth_file": str(file_a)}
        )
        _, default_key, _ = config._get_openai_compatible_provider_info("gpt-6.1-sol", None, None, "chatgpt")

        assert per_model_key == "token-a"
        assert default_key == "token-default"

    def test_get_llm_provider_threads_auth_file(self, auth_files: tuple[Path, Path]) -> None:
        file_a, _ = auth_files

        model, provider, dynamic_api_key, _ = get_llm_provider(
            model="chatgpt/gpt-6.1-sol",
            litellm_params=GenericLiteLLMParams(chatgpt_auth_file=str(file_a)),
        )

        assert model == "gpt-6.1-sol"
        assert provider == "chatgpt"
        assert dynamic_api_key == "token-a"


@pytest.mark.parametrize("endpoint", ["chat", "responses"])
@pytest.mark.parametrize("through_router", [False, True])
@pytest.mark.parametrize("with_prompt", [False, True])
@pytest.mark.parametrize("blocked_default", [False, True])
@pytest.mark.asyncio
async def test_requests_use_selected_subscription(
    auth_files: tuple[Path, Path],
    endpoint: str,
    through_router: bool,
    with_prompt: bool,
    blocked_default: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(litellm, "disable_aiohttp_transport", True)
    default_dir: Final = auth_files[0].parent / "missing-default"
    if blocked_default:
        default_dir.write_text("ordinary file")
    monkeypatch.setenv("CHATGPT_TOKEN_DIR", str(default_dir / "unused"))
    if with_prompt:
        monkeypatch.setattr(
            litellm,
            "callbacks",
            [
                DotpromptManager(
                    prompt_id="account-check",
                    prompt_data={"content": "Saved account prompt", "metadata": {"model": "chatgpt/gpt-6.1-sol"}},
                )
            ],
        )
    router: Final = (
        litellm.Router(
            model_list=[
                {
                    "model_name": f"account-{index}",
                    "litellm_params": {"model": "chatgpt/gpt-6.1-sol", "chatgpt_auth_file": str(path)},
                }
                for index, path in enumerate(auth_files)
            ]
        )
        if through_router
        else None
    )

    async def request(index: int, path: Path) -> str:
        params: Final = MappingProxyType(
            {
                "model": f"account-{index}" if router else "chatgpt/gpt-6.1-sol",
                **({"chatgpt_auth_file": str(path)} if router is None else {}),
                **({"prompt_id": "account-check"} if with_prompt else {}),
            }
        )
        if endpoint == "chat":
            result: Final = await (router.acompletion if router else litellm.acompletion)(
                **params, messages=[{"role": "user", "content": "Hello"}]
            )
            return result.choices[0].message.content
        response: Final = await (router.aresponses if router else litellm.aresponses)(
            **params, input=[{"role": "user", "content": "Hello"}]
        )
        return response.output[0].content[0].text

    with respx.mock as transport:
        transport.post("https://chatgpt.com/backend-api/codex/responses").mock(side_effect=_subscription_response)
        results: Final = await asyncio.gather(*(request(index, path) for index, path in enumerate(auth_files)))
        assert results == ["acct-a", "acct-b"]
        if with_prompt:
            assert all("Saved account prompt" in call.request.content.decode() for call in transport.calls)


@pytest.mark.parametrize("endpoint", ["chat", "responses"])
@pytest.mark.parametrize("configured_login", [False, True])
@pytest.mark.parametrize("with_prompt", [False, True])
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.asyncio
async def test_client_login_keeps_its_account_across_gateway_deployments(
    auth_files: tuple[Path, Path],
    endpoint: str,
    configured_login: bool,
    with_prompt: bool,
    stream: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(litellm, "disable_aiohttp_transport", True)
    monkeypatch.setenv("CHATGPT_TOKEN_DIR", str(auth_files[0].parent / "no-gateway-login"))
    if with_prompt:
        monkeypatch.setattr(
            litellm,
            "callbacks",
            [
                DotpromptManager(
                    prompt_id="client-account-check",
                    prompt_data={"content": "Saved client prompt", "metadata": {"model": "chatgpt/gpt-6.1-sol"}},
                )
            ],
        )
    router: Final = litellm.Router(
        model_list=[
            {
                "model_name": "subscriptions",
                "litellm_params": {"model": "chatgpt/gpt-6.1-sol"},
            }
            for _ in auth_files
        ],
        num_retries=0,
    )

    def reply(request: httpx.Request) -> httpx.Response:
        account: Final = request.headers["ChatGPT-Account-Id"]
        assert request.headers["Authorization"] == f"Bearer {_client_token(account)}"
        return _subscription_response(
            httpx.Request(
                "POST",
                request.url,
                content=request.content,
                headers={
                    **{key: value for key, value in request.headers.items() if key.lower() != "authorization"},
                    "Authorization": f"Bearer token-{account.removeprefix('acct-')}",
                },
            )
        )

    async def call(account: str) -> str:
        params: Final = MappingProxyType(
            {
                "model": "subscriptions",
                "stream": stream,
                **({"prompt_id": "client-account-check"} if with_prompt else {}),
                "provider_specific_header": {
                    "custom_llm_provider": "chatgpt",
                    "extra_headers": {"Authorization": f"Bearer {_client_token(account)}"},
                },
            }
        )
        response: Final = await (
            router.acompletion(**params, messages=[{"role": "user", "content": "Hello"}])
            if endpoint == "chat"
            else router.aresponses(**params, input=[{"role": "user", "content": "Hello"}])
        )
        if stream:
            chunks: Final = [part async for part in response]
            return (
                "".join(part.choices[0].delta.content or "" for part in chunks)
                if endpoint == "chat"
                else "".join(
                    getattr(part, "delta", "")
                    for part in chunks
                    if getattr(part, "type", "") == "response.output_text.delta"
                )
            )
        return response.choices[0].message.content if endpoint == "chat" else response.output[0].content[0].text

    with respx.mock as transport:
        transport.post("https://chatgpt.com/backend-api/codex/responses").mock(side_effect=reply)
        results: Final = await asyncio.gather(call("acct-client-a"), call("acct-client-b"))
        assert results == ["acct-client-a", "acct-client-b"]
        assert len(transport.calls) == 2


async def test_one_client_limit_does_not_cool_down_other_subscriptions(
    auth_files: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(litellm, "disable_aiohttp_transport", True)
    router: Final = litellm.Router(
        model_list=[
            {"model_name": "pool", "litellm_params": {"model": "chatgpt/gpt-6.1-sol", "chatgpt_auth_file": str(path)}}
            for path in auth_files
        ],
        num_retries=0,
        cooldown_time=60,
        routing_strategy="least-busy",
        allowed_fails=0,
        chatgpt_profile_pool_model_groups=["pool"],
    )
    headers: Final = {
        "custom_llm_provider": "chatgpt",
        "extra_headers": {"Authorization": f"Bearer {_client_token('acct-limited')}"},
    }
    with respx.mock as transport:
        route: Final = transport.post("https://chatgpt.com/backend-api/codex/responses")
        route.respond(
            429,
            headers={"retry-after": "60"},
            json={"error": {"message": "Usage limit reached", "type": "rate_limit_error"}},
        )
        for _ in range(2):
            with pytest.raises(litellm.RateLimitError):
                await router.aresponses(model="pool", input="Hello", provider_specific_header=headers)
            await asyncio.sleep(0)
        route.mock(side_effect=_subscription_response)
        response: Final = await router.aresponses(model="pool", input="Hello")
        assert response.output[0].content[0].text in ("acct-a", "acct-b")


@pytest.mark.parametrize("endpoint", ["chat", "responses"])
@pytest.mark.parametrize("async_call", [False, True])
@pytest.mark.parametrize("direct_headers", [False, True])
@pytest.mark.parametrize("configured_key", [False, True])
@pytest.mark.parametrize(
    "target", ["https://example.com/v1", "http://chatgpt.com/backend-api/codex", "https://chatgpt.com.example.com/v1"]
)
@pytest.mark.asyncio
async def test_client_login_cannot_be_redirected_to_another_host(
    endpoint: str, target: str, async_call: bool, direct_headers: bool, configured_key: bool
) -> None:
    headers: Final = {"Authorization": f"Bearer {_client_token('acct-client')}"}
    credential: Final = (
        {"extra_headers": headers}
        if direct_headers
        else {"provider_specific_header": {"custom_llm_provider": "chatgpt", "extra_headers": headers}}
    )
    params: Final = MappingProxyType(
        {
            "model": "chatgpt/gpt-6.1-sol",
            "api_base": target,
            **({"api_key": "configured-test-key"} if configured_key else {}),
            **credential,
        }
    )

    async def request() -> None:
        if endpoint == "chat":
            if async_call:
                await litellm.acompletion(**params, messages=[{"role": "user", "content": "Hello"}])
            else:
                litellm.completion(**params, messages=[{"role": "user", "content": "Hello"}])
        elif async_call:
            await litellm.aresponses(**params, input="Hello")
        else:
            litellm.responses(**params, input="Hello")

    with respx.mock as transport:
        with pytest.raises(litellm.BadRequestError, match="official HTTPS ChatGPT endpoint"):
            await request()
        assert len(transport.calls) == 0


async def test_cross_provider_fallback_does_not_receive_the_chatgpt_login(
    auth_files: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(litellm, "disable_aiohttp_transport", True)
    router: Final = litellm.Router(
        model_list=[
            {
                "model_name": "subscription",
                "litellm_params": {"model": "chatgpt/gpt-6.1-sol", "chatgpt_auth_file": str(auth_files[0])},
            },
            {
                "model_name": "api-fallback",
                "litellm_params": {"model": "openai/gpt-6.1-sol", "api_key": "sk-example-fallback"},
            },
        ],
        fallbacks=[{"subscription": ["api-fallback"]}],
        num_retries=0,
        allow_chatgpt_cross_profile_fallback=True,
    )
    with respx.mock as transport:
        transport.post("https://chatgpt.com/backend-api/codex/responses").respond(
            429, json={"error": {"message": "Usage limit reached", "type": "rate_limit_error"}}
        )
        fallback: Final = transport.post("https://api.openai.com/v1/responses").respond(
            200,
            json={
                "id": "resp_fallback",
                "object": "response",
                "created_at": 1700000000,
                "status": "completed",
                "model": "gpt-6.1-sol",
                "output": [
                    {
                        "id": "msg_fallback",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [{"type": "output_text", "text": "fallback", "annotations": []}],
                    }
                ],
                "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
            },
        )
        response: Final = await router.aresponses(
            model="subscription",
            input="Hello",
            provider_specific_header={
                "custom_llm_provider": "chatgpt",
                "extra_headers": {
                    "Authorization": f"Bearer {_client_token('acct-client')}",
                    "ChatGPT-Account-Id": "acct-client",
                },
            },
        )
        assert response.output[0].content[0].text == "fallback"
        assert fallback.calls.last.request.headers["Authorization"] == "Bearer sk-example-fallback"
        assert "ChatGPT-Account-Id" not in fallback.calls.last.request.headers


@pytest.mark.parametrize("endpoint", ["chat", "responses"])
@pytest.mark.parametrize("async_call", [False, True])
@pytest.mark.parametrize("with_prompt", [False, True])
@pytest.mark.asyncio
async def test_sdk_extra_headers_use_client_login_without_gateway_auth(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, endpoint: str, async_call: bool, with_prompt: bool
) -> None:
    blocked: Final = tmp_path / "blocked"
    blocked.write_text("ordinary file")
    token_dir = tmp_path / "blocked-token-dir"
    token_dir.write_text("ordinary file")
    monkeypatch.setenv("CHATGPT_TOKEN_DIR", str(token_dir))
    monkeypatch.delenv("CHATGPT_AUTH_FILE", raising=False)
    monkeypatch.setattr(litellm, "disable_aiohttp_transport", True)
    headers: Final = {"Authorization": f"Bearer {_client_token('acct-client-a')}"}
    prompt_params: Final = {"prompt_id": "sdk-client"} if with_prompt else {}
    if with_prompt:
        monkeypatch.setattr(
            litellm,
            "callbacks",
            [
                DotpromptManager(
                    prompt_id="sdk-client",
                    prompt_data={"content": "Hello", "metadata": {"model": "chatgpt/gpt-6-luna"}},
                )
            ],
        )
    with respx.mock as transport:
        transport.post("https://chatgpt.com/backend-api/codex/responses").mock(side_effect=_subscription_response)
        if endpoint == "chat":
            params: Final = {
                "model": "chatgpt/gpt-6.1-sol",
                "messages": [{"role": "user", "content": "Hello"}],
                "extra_headers": headers,
                **prompt_params,
            }
            result: Final = await litellm.acompletion(**params) if async_call else litellm.completion(**params)
            assert result.choices[0].message.content == "acct-client-a"
        else:
            response: Final = (
                await litellm.aresponses(
                    model="chatgpt/gpt-6.1-sol", input="Hello", extra_headers=headers, **prompt_params
                )
                if async_call
                else litellm.responses(
                    model="chatgpt/gpt-6.1-sol", input="Hello", extra_headers=headers, **prompt_params
                )
            )
            assert response.output[0].content[0].text == "acct-client-a"
        assert transport.calls.last.request.headers["Authorization"] == headers["Authorization"]
        assert len(transport.calls) == 1


@pytest.mark.parametrize("endpoint", ["chat", "responses"])
@pytest.mark.parametrize("sync", [False, True])
@pytest.mark.parametrize("credential_source", ["default", "file", "api_key"])
@pytest.mark.parametrize("authorization_header", [None, "Authorization", "authorization"])
@pytest.mark.asyncio
async def test_requests_preserve_gateway_token_and_selected_workspace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    endpoint: str,
    sync: bool,
    credential_source: str,
    authorization_header: str | None,
) -> None:
    monkeypatch.setattr("time.time", lambda: 1700000000)
    monkeypatch.setattr(litellm, "disable_aiohttp_transport", True)
    monkeypatch.setenv("CHATGPT_AUTH_FILE", str(tmp_path / "default.json"))
    token: Final = _client_token("acct-token-default")
    auth_file: Final = tmp_path / ("selected.json" if credential_source == "file" else "default.json")
    _write_auth_record(auth_file, token, "acct-saved-workspace")
    configured_token: Final = _client_token("acct-configured")
    expected_token: Final = configured_token if credential_source == "api_key" else token
    expected_account: Final = "acct-configured" if credential_source == "api_key" else "acct-saved-workspace"

    def reply(request: httpx.Request) -> httpx.Response:
        assert request.headers.get_list("authorization") == [f"Bearer {expected_token}"]
        assert request.headers.get_list("chatgpt-account-id") == [expected_account]
        assert request.headers["originator"] == "codex_cli_rs"
        return _subscription_response(
            httpx.Request(
                "POST",
                request.url,
                content=request.content,
                headers={
                    "Authorization": f"Bearer token-{expected_account.removeprefix('acct-')}",
                    "ChatGPT-Account-Id": expected_account,
                },
            )
        )

    params: Final = MappingProxyType(
        {
            "model": "chatgpt/gpt-6.1-sol",
            **({"chatgpt_auth_file": str(auth_file)} if credential_source == "file" else {}),
            **({"api_key": configured_token} if credential_source == "api_key" else {}),
            "extra_headers": {
                "originator": "codex_cli_rs",
                **({authorization_header: "Bearer sk-unrelated-example"} if authorization_header else {}),
            },
        }
    )
    with respx.mock as transport:
        transport.post("https://chatgpt.com/backend-api/codex/responses").mock(side_effect=reply)
        if endpoint == "chat":
            result: Final = (
                await asyncio.to_thread(litellm.completion, **params, messages=[{"role": "user", "content": "Hello"}])
                if sync
                else await litellm.acompletion(**params, messages=[{"role": "user", "content": "Hello"}])
            )
            assert result.choices[0].message.content == expected_account
        else:
            response: Final = (
                await asyncio.to_thread(litellm.responses, **params, input=[{"role": "user", "content": "Hello"}])
                if sync
                else await litellm.aresponses(**params, input=[{"role": "user", "content": "Hello"}])
            )
            assert response.output[0].content[0].text == expected_account
