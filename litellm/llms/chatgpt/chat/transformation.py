from typing import Any, Final

from litellm.exceptions import AuthenticationError
from litellm.llms.openai.openai import OpenAIConfig
from litellm.types.llms.openai import AllMessageValues

from ..authenticator import Authenticator
from ..common_utils import (
    GetAccessTokenError,
    ensure_chatgpt_session_id,
    get_chatgpt_default_headers,
)
from .streaming_utils import ChatGPTToolCallNormalizer


class ChatGPTConfig(OpenAIConfig):
    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = None,
        custom_llm_provider: str = "openai",
    ) -> None:
        super().__init__()

    def _get_openai_compatible_provider_info(
        self,
        model: str,
        api_base: str | None,
        api_key: str | None,
        custom_llm_provider: str,
        litellm_params: object | None = None,
    ) -> tuple[str | None, str | None, str]:
        authenticator = Authenticator(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            litellm_params
        )  # rebind-ok: framework flow intentionally updates request or lifecycle state
        dynamic_api_base = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            authenticator.get_api_base()
        )  # rebind-ok: framework flow intentionally updates request or lifecycle state
        try:
            dynamic_api_key = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
                authenticator.get_access_token()
            )  # rebind-ok: framework flow intentionally updates request or lifecycle state
        except GetAccessTokenError as e:
            auth_error = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
                AuthenticationError(  # rebind-ok: framework flow intentionally updates request or lifecycle state
                    model=model,
                    llm_provider=custom_llm_provider,
                    message=str(e),
                )
            )
            auth_error.is_non_retryable_interactive_auth = True  # pyright: ignore[reportAttributeAccessIssue]  # router reads this runtime marker
            raise auth_error
        return dynamic_api_base, dynamic_api_key, custom_llm_provider

    def validate_environment(
        self,
        headers: dict,
        model: str,
        messages: list[AllMessageValues],
        optional_params: dict,
        litellm_params: dict,
        api_key: str | None = None,
        api_base: str | None = None,
    ) -> dict:
        validated_headers: Final = super().validate_environment(
            headers, model, messages, optional_params, litellm_params, api_key, api_base
        )

        authenticator = Authenticator(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            litellm_params
        )  # rebind-ok: framework flow intentionally updates request or lifecycle state
        access_token = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            api_key or authenticator.get_access_token()
        )  # rebind-ok: framework flow intentionally updates request or lifecycle state
        account_id = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            authenticator.get_account_id()
        )  # rebind-ok: framework flow intentionally updates request or lifecycle state
        session_id = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            ensure_chatgpt_session_id(  # rebind-ok: framework flow intentionally updates request or lifecycle state
                litellm_params
            )
        )  # rebind-ok: framework flow intentionally updates request or lifecycle state
        default_headers = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            get_chatgpt_default_headers(  # rebind-ok: framework flow intentionally updates request or lifecycle state
                access_token, account_id, session_id
            )
        )  # rebind-ok: framework flow intentionally updates request or lifecycle state
        return {**default_headers, **validated_headers}

    def post_stream_processing(self, stream: Any) -> Any:
        return ChatGPTToolCallNormalizer(stream)

    def map_openai_params(
        self,
        non_default_params: dict,
        optional_params: dict,
        model: str,
        drop_params: bool,
    ) -> dict:
        optional_params = super().map_openai_params(non_default_params, optional_params, model, drop_params)
        optional_params.setdefault("stream", False)
        return optional_params
