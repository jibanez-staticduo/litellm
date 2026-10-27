from collections.abc import Mapping
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    cast,  # noqa: TID251  # SDK input union omits Codex extensions that must survive replay
)

import httpx

from litellm.exceptions import AuthenticationError
from litellm.litellm_core_utils.core_helpers import process_response_headers
from litellm.litellm_core_utils.hidden_params import HIDDEN_PARAMS_ATTR, set_hidden_params
from litellm.litellm_core_utils.llm_response_utils.convert_dict_to_response import (
    safe_convert_created_field,
)
from litellm.litellm_core_utils.url_utils import join_api_base
from litellm.llms.openai.common_utils import OpenAIError
from litellm.llms.openai.responses.transformation import OpenAIResponsesAPIConfig
from litellm.responses.sse_output_recovery import (
    parse_sse_json_chunk,
    record_output_item_chunk,
    record_output_text_chunk,
)
from litellm.types.llms.openai import (
    ResponseInputParam,
    ResponsesAPIResponse,
    ResponsesAPIStreamEvents,
)
from litellm.types.router import GenericLiteLLMParams
from litellm.types.utils import LlmProviders

from ..authenticator import Authenticator, get_cached_authenticator, get_chatgpt_auth_file
from ..common_utils import (
    CHATGPT_API_BASE,
    GetAccessTokenError,
    ensure_chatgpt_session_id,
    get_chatgpt_client_credential,
    get_chatgpt_default_headers,
    get_chatgpt_default_instructions,
    strip_chatgpt_client_credential_headers,
)

if TYPE_CHECKING:
    from litellm.litellm_core_utils.litellm_logging import Logging as LiteLLMLoggingObj

_CHATGPT_SERVICE_TIERS: Final = {"default": "default", "priority": "priority", "fast": "priority"}


def _chatgpt_replay_item(item: object) -> object | None:
    if not isinstance(item, Mapping):
        return item
    fields: Final = cast(Mapping[str, object], item)  # cast-ok: Responses input items have string JSON keys
    if fields.get("type") != "reasoning" or not fields.get("content"):
        return fields
    encrypted: Final = fields.get("encrypted_content")
    if not isinstance(encrypted, str) or not encrypted:
        return None
    return {key: value for key, value in fields.items() if key != "content"}  # mutable-ok: outbound JSON item


class ChatGPTResponsesAPIConfig(OpenAIResponsesAPIConfig):
    def __init__(self, authenticator: Authenticator | None = None) -> None:
        super().__init__()
        self.authenticator = authenticator

    @property
    def custom_llm_provider(self) -> LlmProviders:
        return LlmProviders.CHATGPT

    def _resolve_authenticator(self, litellm_params: GenericLiteLLMParams | None) -> Authenticator:
        auth_file: Final = get_chatgpt_auth_file(litellm_params)
        if auth_file:
            return get_cached_authenticator(auth_file)
        return self.authenticator or Authenticator(litellm_params)

    def validate_environment(
        self,
        headers: dict,
        model: str,
        litellm_params: GenericLiteLLMParams | None,
    ) -> dict:
        client_credential: Final = get_chatgpt_client_credential(headers)
        session_id: Final = ensure_chatgpt_session_id(litellm_params)
        if client_credential is not None:
            return {
                **get_chatgpt_default_headers(client_credential.access_token, client_credential.account_id, session_id),
                **strip_chatgpt_client_credential_headers(headers),
            }
        authenticator: Final = self._resolve_authenticator(litellm_params)
        safe_headers: Final = strip_chatgpt_client_credential_headers(headers)
        configured_api_key: Final = litellm_params.api_key if litellm_params is not None else None
        if configured_api_key and not get_chatgpt_auth_file(litellm_params):
            return {
                **get_chatgpt_default_headers(
                    configured_api_key, authenticator.get_account_id(configured_api_key), session_id
                ),
                **safe_headers,
            }
        try:
            access_token: Final = authenticator.get_access_token()
        except GetAccessTokenError as e:
            auth_error = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
                AuthenticationError(  # rebind-ok: framework flow intentionally updates request or lifecycle state
                    model=model,
                    llm_provider="chatgpt",
                    message=str(e),
                )
            )
            auth_error.is_non_retryable_interactive_auth = True  # pyright: ignore[reportAttributeAccessIssue]  # router reads this runtime marker
            raise auth_error

        account_id: Final = authenticator.get_account_id(access_token)
        default_headers: Final = get_chatgpt_default_headers(access_token, account_id, session_id)
        return {**default_headers, **safe_headers}

    def transform_responses_api_request(
        self,
        model: str,
        input: str | ResponseInputParam,
        response_api_optional_request_params: dict,
        litellm_params: GenericLiteLLMParams,
        headers: dict,
    ) -> dict:
        # The hosted endpoint rejects plaintext reasoning from compatible providers.
        # Work on a copy: the same stored history can later be replayed to its origin.
        replay_input: Final = (
            cast(  # cast-ok: preserve Responses input variants, removing incompatible reasoning fields/items only
                ResponseInputParam,
                [safe for item in deepcopy(input) if (safe := _chatgpt_replay_item(item)) is not None],
            )
            if isinstance(input, list)
            else input
        )
        request: Final = super().transform_responses_api_request(
            model,
            replay_input,
            response_api_optional_request_params,
            litellm_params,
            headers,
        )
        input_text: Final = request.get("input")
        if isinstance(input_text, str):
            request["input"] = [{"role": "user", "content": [{"type": "input_text", "text": input_text}]}]
        base_instructions: Final = get_chatgpt_default_instructions()
        existing_instructions: Final = request.get("instructions")
        if existing_instructions:
            if base_instructions not in existing_instructions:
                request["instructions"] = f"{base_instructions}\n\n{existing_instructions}"
        else:
            request["instructions"] = base_instructions
        request["store"] = False
        request["stream"] = True
        include: Final = list(request.get("include") or [])
        if "reasoning.encrypted_content" not in include:
            include.append("reasoning.encrypted_content")
        request["include"] = include

        allowed_keys: Final = {
            "model",
            "input",
            "instructions",
            "stream",
            "store",
            "include",
            "tools",
            "tool_choice",
            "reasoning",
            "previous_response_id",
            "truncation",
            "text",
        }
        is_codex_responses_lite: Final = any(key.lower() == "x-openai-internal-codex-responses-lite" for key in headers)
        request_items: Final = (
            (*request.items(), ("parallel_tool_calls", False)) if is_codex_responses_lite else request.items()
        )
        filtered: Final = {
            key: value
            for key, value in request_items
            if key in allowed_keys or (is_codex_responses_lite and key == "parallel_tool_calls")
        }
        requested_service_tier: Final[object] = request.get("service_tier")
        service_tier: Final = (
            _CHATGPT_SERVICE_TIERS.get(requested_service_tier) if isinstance(requested_service_tier, str) else None
        )
        return {**filtered, **({"service_tier": service_tier} if service_tier is not None else {})}

    def transform_response_api_response(
        self,
        model: str,
        raw_response: httpx.Response,
        logging_obj: "LiteLLMLoggingObj",
    ) -> ResponsesAPIResponse:
        body_text: Final = raw_response.text or ""
        if not self._should_parse_as_sse(raw_response=raw_response, body_text=body_text):
            return super().transform_response_api_response(
                model=model,
                raw_response=raw_response,
                logging_obj=logging_obj,
            )

        logging_obj.post_call(
            original_response=raw_response.text,
            additional_args={"complete_input_dict": {}},
        )

        completed_response, error_message = self._extract_completed_response_from_sse(body_text=body_text)
        if completed_response is None:
            raise OpenAIError(
                message=error_message or raw_response.text,
                status_code=raw_response.status_code,
            )

        self._attach_response_headers(completed_response=completed_response, raw_response=raw_response)
        return completed_response

    def _should_parse_as_sse(self, raw_response: httpx.Response, body_text: str) -> bool:
        content_type: Final = (raw_response.headers or {}).get("content-type", "")
        if "text/event-stream" in content_type.lower():
            return True
        trimmed_body: Final = body_text.lstrip()
        return bool(
            trimmed_body.startswith("event:")
            or trimmed_body.startswith("data:")
            or "\nevent:" in body_text
            or "\ndata:" in body_text
        )

    def _extract_completed_response_from_sse(self, body_text: str) -> tuple[ResponsesAPIResponse | None, str | None]:
        completed_response = None
        error_message = None
        streamed_output_items: Final[dict[int, dict[str, object]]] = {}
        text_only_output_items: Final[dict[int, dict[str, object]]] = {}
        for chunk in body_text.splitlines():
            parsed_chunk = parse_sse_json_chunk(chunk)
            if parsed_chunk is None:
                continue

            event_type = parsed_chunk.get("type")
            if event_type == ResponsesAPIStreamEvents.OUTPUT_ITEM_DONE:
                record_output_item_chunk(
                    parsed_chunk=parsed_chunk,
                    output_items=streamed_output_items,
                )
                continue

            if event_type == ResponsesAPIStreamEvents.OUTPUT_TEXT_DONE:
                record_output_text_chunk(
                    parsed_chunk=parsed_chunk,
                    output_items=streamed_output_items,
                    text_only_items=text_only_output_items,
                )
                continue

            if event_type == ResponsesAPIStreamEvents.RESPONSE_COMPLETED:
                # Real OUTPUT_ITEM_DONE events take precedence at any given
                # output_index, but text-only items at indices without a
                # matching OUTPUT_ITEM_DONE must still be preserved (e.g.
                # providers that emit only OUTPUT_TEXT_DONE for some indices).
                merged_items: dict[int, dict[str, object]] = {**text_only_output_items}
                merged_items.update(streamed_output_items)
                completed_response = self._build_completed_response_from_chunk(
                    parsed_chunk=parsed_chunk,
                    streamed_output_items=merged_items,
                )
                break

            if event_type in (
                ResponsesAPIStreamEvents.RESPONSE_FAILED,
                ResponsesAPIStreamEvents.ERROR,
            ):
                extracted_error = self._extract_error_message(parsed_chunk)
                if extracted_error is not None:
                    error_message = extracted_error

        return completed_response, error_message

    def _build_completed_response_from_chunk(
        self, parsed_chunk: Mapping[str, object], streamed_output_items: Mapping[int, dict[str, object]]
    ) -> ResponsesAPIResponse | None:
        response_payload = parsed_chunk.get("response")
        if not isinstance(response_payload, dict):
            return None
        response_payload = dict(response_payload)
        if not response_payload.get("output") and streamed_output_items:
            response_payload["output"] = [item for _, item in sorted(streamed_output_items.items())]
        if "created_at" in response_payload:
            response_payload["created_at"] = safe_convert_created_field(response_payload["created_at"])
        try:
            return ResponsesAPIResponse(**response_payload)
        except (TypeError, ValueError):
            return ResponsesAPIResponse.model_construct(**response_payload)

    def _extract_error_message(self, parsed_chunk: dict[str, Any]) -> str | None:
        error_obj: Final = parsed_chunk.get("error") or (parsed_chunk.get("response") or {}).get("error")
        if error_obj is None:
            top_level_message: Final = parsed_chunk.get("message")
            return top_level_message if isinstance(top_level_message, str) else None
        if isinstance(error_obj, dict):
            return error_obj.get("message") or str(error_obj)
        return str(error_obj)

    def _attach_response_headers(
        self,
        completed_response: ResponsesAPIResponse,
        raw_response: httpx.Response,
    ) -> None:
        raw_headers: Final = dict(raw_response.headers)
        processed_headers: Final = process_response_headers(raw_headers)
        if not hasattr(completed_response, HIDDEN_PARAMS_ATTR):
            set_hidden_params(completed_response, {})
        hidden_params: Final = cast(  # cast-ok: preserve dynamic mapping behavior
            dict[str, object], getattr(completed_response, HIDDEN_PARAMS_ATTR)
        )
        hidden_params["additional_headers"] = processed_headers
        hidden_params["headers"] = raw_headers

    @staticmethod
    def _build_completed_response(
        response_payload: dict,  # mutable-ok: framework contract requires mutable request or response containers
        accumulated_output_items: list,  # mutable-ok: framework contract requires mutable request or response containers
    ) -> ResponsesAPIResponse:  # mutable-ok: framework contract requires mutable request or response containers
        response_payload = dict(  # mutable-ok: framework contract requires mutable request or response containers; rebind-ok: framework flow intentionally updates request or lifecycle state
            response_payload
        )  # mutable-ok: framework contract requires mutable request or response containers; rebind-ok: framework flow intentionally updates request or lifecycle state
        if "created_at" in response_payload:
            response_payload[
                "created_at"
            ] = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
                safe_convert_created_field(  # rebind-ok: framework flow intentionally updates request or lifecycle state
                    response_payload["created_at"]
                )
            )  # rebind-ok: framework flow intentionally updates request or lifecycle state
        if not response_payload.get("output") and accumulated_output_items:
            response_payload["output"] = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
                accumulated_output_items  # rebind-ok: framework flow intentionally updates request or lifecycle state
            )
        try:
            return ResponsesAPIResponse(**response_payload)
        except Exception:
            return ResponsesAPIResponse.model_construct(**response_payload)

    def get_complete_url(
        self,
        api_base: str | None,
        litellm_params: object,
    ) -> str:
        default_api_base: Final = (
            self.authenticator.get_api_base()
            if self.authenticator is not None
            else Authenticator.get_api_base()
        )
        resolved_api_base: Final = api_base or default_api_base or CHATGPT_API_BASE
        return join_api_base(resolved_api_base, "responses")

    def supports_native_websocket(self) -> bool:
        """ChatGPT does not support native WebSocket for Responses API"""
        return False
