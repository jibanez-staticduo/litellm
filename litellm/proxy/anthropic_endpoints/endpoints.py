"""
Unified /v1/messages endpoint - (Anthropic Spec)
"""

from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Final

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, JsonValue, TypeAdapter, ValidationError
from typing_extensions import ReadOnly, TypedDict

import litellm
from litellm.anthropic_interface.exceptions import (
    AnthropicErrorDetail,
    AnthropicErrorResponse,
    AnthropicExceptionMapping,
)
from litellm.integrations.custom_guardrail import ModifyResponseException
from litellm.litellm_core_utils.get_llm_provider_logic import get_llm_provider
from litellm.llms.anthropic import oauth_policy
from litellm.llms.anthropic.common_utils import AnthropicError, is_anthropic_oauth_key
from litellm.llms.anthropic.count_tokens.token_counter import anthropic_count_tokens_handler
from litellm.llms.anthropic.pass_through.context_management import (
    AnthropicContextManagementError,
)
from litellm.llms.base_llm.guardrail_translation.utils import (
    blocked_response_usage as _blocked_response_usage,
)
from litellm.proxy._types import *
from litellm.proxy.auth.auth_checks import can_key_call_resolved_model
from litellm.proxy.auth.user_api_key_auth import user_api_key_auth
from litellm.proxy.common_request_processing import (
    ProxyBaseLLMRequestProcessing,
    create_response,
    log_llm_api_exception,
    proxy_exception_from_http_exception,
    resolve_litellm_call_id,
)
from litellm.proxy.common_utils.error_body_call_id import error_body_call_id
from litellm.proxy.common_utils.http_parsing_utils import _read_request_body
from litellm.proxy.common_utils.openai_error_payload import (
    LITELLM_CALL_ID_HEADER,
    error_status_code,
    openai_error_param,
    openai_error_type,
    with_litellm_call_id,
)
from litellm.types.utils import TokenCountResponse

router: Final = APIRouter()
_NATIVE_COUNT_BODY: Final = TypeAdapter(dict[str, JsonValue])
_NATIVE_COUNT_MESSAGES: Final = TypeAdapter(list[dict[str, JsonValue]])


class _OAuthCountTokensBody(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)
    model: str
    messages: Sequence[Mapping[str, JsonValue]]
    tools: Sequence[Mapping[str, JsonValue]] | None = None
    system: JsonValue = None


class _OAuthCountTokensParams(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)
    model: str
    custom_llm_provider: str | None = None
    api_base: str | None = None
    use_anthropic_oauth: bool = False
    anthropic_auth_profile: str | None = None
    anthropic_token_dir: str | None = None
    anthropic_oauth_compatibility: str | None = None


class _OAuthCountTokensDeployment(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)
    litellm_params: _OAuthCountTokensParams


class _OAuthCountTokensAliases(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, from_attributes=True)
    aliases: Mapping[str, str] | None = None
    team_model_aliases: Mapping[str, str] | None = None


class _OAuthCountTokensRoutingMetadata(TypedDict):
    user_api_key_team_id: ReadOnly[str | None]


async def _count_tokens_with_oauth(
    request: Request,
    request_data: Mapping[str, JsonValue],
    user_api_key_dict: UserAPIKeyAuth,
    oauth_header: str | None,
) -> Mapping[str, JsonValue] | JSONResponse | None:
    from litellm.proxy.proxy_server import llm_router

    data: Final = request_data
    body: Final = _OAuthCountTokensBody.model_validate(data)
    if llm_router is None:
        if oauth_header is None:
            return None
        raise HTTPException(status_code=400, detail="OAuth token counting requires a configured Anthropic deployment")

    aliases: Final = _OAuthCountTokensAliases.model_validate(user_api_key_dict)
    team_aliases: Final = aliases.team_model_aliases or MappingProxyType({})
    key_aliases: Final = aliases.aliases or MappingProxyType({})
    team_model: Final = team_aliases.get(body.model, body.model)
    key_model: Final = key_aliases.get(team_model, team_model)
    global_model: Final = litellm.model_alias_map.get(key_model, key_model)
    routed_model: Final = key_aliases.get(global_model, global_model)
    if oauth_header is None and not llm_router.anthropic_oauth_model_group_is_managed(routed_model):
        return None
    await can_key_call_resolved_model(
        model=body.model,
        llm_model_list=None,
        valid_token=user_api_key_dict,
        llm_router=llm_router,
    )
    metadata: Final[_OAuthCountTokensRoutingMetadata] = {"user_api_key_team_id": user_api_key_dict.team_id}
    routing_kwargs: Final = _NATIVE_COUNT_BODY.validate_python(MappingProxyType({"metadata": metadata}))
    deployment: Final = _OAuthCountTokensDeployment.model_validate(
        await llm_router.async_get_available_deployment(  # pyright: ignore[reportUnknownMemberType]  # validate the legacy router result at this boundary
            model=routed_model,
            request_kwargs=routing_kwargs,
        )
    )
    params: Final = deployment.litellm_params
    oauth_params: Final = _NATIVE_COUNT_BODY.validate_python(params.model_dump())
    managed: Final = oauth_policy.is_anthropic_oauth_managed(oauth_params)
    if not managed and oauth_header is None:
        return None
    upstream_model, provider, _, _ = get_llm_provider(
        model=params.model,
        custom_llm_provider=params.custom_llm_provider,
    )
    if provider != "anthropic":
        raise HTTPException(status_code=400, detail="OAuth token counting requires the native Anthropic provider")
    if not managed and params.api_base not in (
        None,
        "https://api.anthropic.com",
        "https://api.anthropic.com/",
        "https://api.anthropic.com/v1",
        "https://api.anthropic.com/v1/",
    ):
        raise HTTPException(status_code=400, detail="Client OAuth token counting requires the native Anthropic API")

    try:
        oauth_policy.validate_anthropic_oauth_request_overrides(data, oauth_params)
        oauth_headers: Final = MappingProxyType({"authorization": oauth_header}) if oauth_header else None
        managed_token: Final = oauth_policy.resolve_anthropic_oauth_access_token(
            oauth_params, api_base=params.api_base, headers=oauth_headers
        )
        oauth_token: Final = (
            managed_token if managed else oauth_header.removeprefix("Bearer ").strip() if oauth_header else None
        )
        if oauth_token is None:
            raise AnthropicError(401, "No Anthropic OAuth credential available for token counting")
        return await anthropic_count_tokens_handler.handle_count_tokens_request(
            model=upstream_model,
            messages=_NATIVE_COUNT_MESSAGES.validate_python(body.messages),
            api_key=oauth_token,
            tools=_NATIVE_COUNT_MESSAGES.validate_python(body.tools) if body.tools is not None else None,
            system=oauth_policy.apply_anthropic_oauth_system(body.system, oauth_params),
            optional_params=MappingProxyType(data),
            extra_headers=request.headers,
        )
    except AnthropicError as exc:
        try:
            error_body: Final = _NATIVE_COUNT_BODY.validate_json(exc.message)
        except ValidationError:
            return JSONResponse(
                status_code=exc.status_code,
                content=AnthropicExceptionMapping.transform_to_anthropic_error(
                    status_code=exc.status_code, raw_message=exc.message
                ),
            )
        return JSONResponse(status_code=exc.status_code, content=error_body)


def _with_provider_specific_fields(exc: ProxyException, detail: AnthropicErrorDetail) -> AnthropicErrorDetail:
    if not exc.provider_specific_fields:
        return detail
    with_fields: Final[AnthropicErrorDetail] = {**detail, "provider_specific_fields": exc.provider_specific_fields}
    return with_fields


def _anthropic_error_detail(
    exc: ProxyException, detail: AnthropicErrorDetail, call_id: str | None
) -> AnthropicErrorDetail:
    if call_id is None:
        return _with_provider_specific_fields(exc, detail)
    with_call_id: Final[AnthropicErrorDetail] = {
        **_with_provider_specific_fields(exc, detail),
        "litellm_call_id": call_id,
    }
    return with_call_id


def _anthropic_error_json_response(exc: ProxyException, request: Request) -> JSONResponse:
    from litellm.proxy.proxy_server import (
        _close_dangling_otel_server_span,  # pyright: ignore[reportPrivateUsage]  # proxy_server keeps the span-close helper private; error JSONResponses returned by the route must stamp the OTel server span like the global ProxyException handler does
        general_settings_view,
    )

    status_code: Final = int(exc.code) if exc.code is not None and exc.code.isdigit() else 500
    _close_dangling_otel_server_span(request, status_code, exc=exc)
    envelope: Final = AnthropicExceptionMapping.transform_to_anthropic_error(
        status_code=status_code,
        raw_message=exc.message,
        request_id=request.headers.get("x-request-id"),
    )
    body_call_id: Final = error_body_call_id(general_settings_view(), exc.headers.get(LITELLM_CALL_ID_HEADER))
    content: Final[AnthropicErrorResponse] = {
        **envelope,
        "error": _anthropic_error_detail(exc, envelope["error"], body_call_id),
    }
    return JSONResponse(status_code=status_code, content=content, headers=exc.headers)


def _strip_total_tokens_from_anthropic_response(response: Any) -> None:
    """Remove the OpenAI-flavored `usage.total_tokens` field that LiteLLM
    injects into Anthropic /v1/messages responses.

    The Anthropic /v1/messages spec only defines:
        input_tokens, output_tokens, cache_creation_input_tokens,
        cache_read_input_tokens, cache_creation.{ephemeral_5m,ephemeral_1h}
    The streaming SSE path (message_delta.usage) already does not include
    total_tokens; this brings the non-streaming path into the same shape.

    Handles both shapes returned by `base_process_llm_request`:
    - plain `dict` (most common — `AnthropicMessagesResponse` is a TypedDict
      and is `dict` at runtime)
    - Pydantic model whose `usage` attribute is dict-shaped (e.g. a
      BaseModel that holds raw Anthropic usage as a `dict[str, int]`)

    Streaming results (StreamingResponse, AsyncIterator, etc.) and Pydantic
    models with strongly-typed Usage sub-models are left untouched —
    those paths either have separate serialization handling or impose
    type constraints the helper does not try to subvert.
    """
    if response is None:
        return
    if isinstance(response, dict):
        usage = response.get("usage")
        if isinstance(usage, dict) and "total_tokens" in usage:
            usage.pop("total_tokens", None)
        return
    # Pydantic-model fallback: only mutate if `usage` is a dict.
    usage = getattr(response, "usage", None)
    if isinstance(usage, dict) and "total_tokens" in usage:
        usage.pop("total_tokens", None)


@router.post(
    "/v1/messages",
    tags=["[beta] Anthropic `/v1/messages`"],
    dependencies=[Depends(user_api_key_auth)],
)
async def anthropic_response(
    fastapi_response: Response,
    request: Request,
    user_api_key_dict: UserAPIKeyAuth = Depends(user_api_key_auth),
):
    """
    Use `{PROXY_BASE_URL}/anthropic/v1/messages` instead - [Docs](https://docs.litellm.ai/docs/pass_through/anthropic_completion).

    This was a BETA endpoint that calls 100+ LLMs in the anthropic format.
    """
    from litellm.proxy.proxy_server import (
        general_settings,
        llm_router,
        proxy_config,
        proxy_logging_obj,
        user_api_base,
        user_max_tokens,
        user_model,
        user_request_timeout,
        user_temperature,
        version,
    )

    data: Final = await _read_request_body(request=request)
    base_llm_response_processor: Final = ProxyBaseLLMRequestProcessing(data=data)
    try:
        result: Final = await base_llm_response_processor.base_process_llm_request(
            request=request,
            fastapi_response=fastapi_response,
            user_api_key_dict=user_api_key_dict,
            route_type="anthropic_messages",
            proxy_logging_obj=proxy_logging_obj,
            llm_router=llm_router,
            general_settings=general_settings,
            proxy_config=proxy_config,
            select_data_generator=None,
            model=None,
            user_model=user_model,
            user_temperature=user_temperature,
            user_request_timeout=user_request_timeout,
            user_max_tokens=user_max_tokens,
            user_api_base=user_api_base,
            version=version,
        )
        # Optionally strip the non-Anthropic `usage.total_tokens` field
        # LiteLLM adds internally. Anthropic's official /v1/messages spec
        # only defines input_tokens / output_tokens / cache_*_input_tokens;
        # total_tokens is an OpenAI convention. Default off
        # (`litellm.strip_anthropic_total_tokens = False`) to preserve
        # backward compatibility for clients that currently read it; set
        # to True to align the wire response with the spec (and with the
        # streaming SSE path, which already omits total_tokens).
        # spend_logs / Prometheus still compute total internally — this
        # only affects the wire response.
        if litellm.strip_anthropic_total_tokens:
            _strip_total_tokens_from_anthropic_response(result)
        return result
    except ModifyResponseException as e:
        # Guardrail flagged content in passthrough mode - return 200 with violation message
        _data: Final = e.request_data
        await proxy_logging_obj.post_call_failure_hook(
            user_api_key_dict=user_api_key_dict,
            original_exception=e,
            request_data=_data,
        )

        # Create Anthropic-formatted response with violation message
        import uuid

        from litellm.types.utils import AnthropicMessagesResponse

        # Report the blocked LLM response's real token usage (carried on the
        # exception) instead of discarding it; zero for pre-call blocks.
        _usage: Final = _blocked_response_usage(e.original_response)

        _anthropic_response: Final = AnthropicMessagesResponse(
            id=f"msg_{uuid.uuid4()}",
            type="message",
            role="assistant",
            content=[{"type": "text", "text": e.message}],
            model=e.model,
            stop_reason="end_turn",
            usage=_usage,
        )

        if data.get("stream", None) is not None and data["stream"] is True:
            # For streaming, use the standard SSE data generator
            async def _passthrough_stream_generator():
                yield _anthropic_response

            selected_data_generator: Final = ProxyBaseLLMRequestProcessing.async_sse_data_generator(
                response=_passthrough_stream_generator(),
                user_api_key_dict=user_api_key_dict,
                request_data=_data,
                proxy_logging_obj=proxy_logging_obj,
            )

            return await create_response(
                generator=selected_data_generator,
                media_type="text/event-stream",
                headers={},
            )

        return _anthropic_response
    except AnthropicContextManagementError as e:
        if e.status_code >= 500:
            # Server-side polyfill failures hit the failure hook for spend/alert
            # parity with the generic handler; 4xx validation errors do not.
            await proxy_logging_obj.post_call_failure_hook(
                user_api_key_dict=user_api_key_dict,
                original_exception=e,
                request_data=base_llm_response_processor.data,
            )
        body: Final = AnthropicExceptionMapping.transform_to_anthropic_error(
            status_code=e.status_code,
            raw_message=e.message,
            request_id=request.headers.get("x-request-id"),
        )
        return JSONResponse(status_code=e.status_code, content=body)
    except Exception as e:
        await proxy_logging_obj.post_call_failure_hook(
            user_api_key_dict=user_api_key_dict, original_exception=e, request_data=base_llm_response_processor.data
        )
        log_llm_api_exception(e, base_llm_response_processor.litellm_call_id)

        if isinstance(e, ProxyException):
            return _anthropic_error_json_response(
                with_litellm_call_id(e, base_llm_response_processor.litellm_call_id), request
            )

        # Extract model_id from request metadata (same as success path)
        litellm_metadata: Final = data.get("litellm_metadata", {}) or {}
        model_info: Final = litellm_metadata.get("model_info", {}) or {}
        model_id: Final = model_info.get("id", "") or ""

        # Get headers
        headers: Final = ProxyBaseLLMRequestProcessing.get_custom_headers(
            user_api_key_dict=user_api_key_dict,
            call_id=base_llm_response_processor.litellm_call_id,
            model_id=model_id,
            version=version,
            response_cost=0,
            model_region=getattr(user_api_key_dict, "allowed_model_region", ""),
            request_data=data,
            timeout=getattr(e, "timeout", None),
            litellm_logging_obj=None,
        )

        if isinstance(e, HTTPException):
            return _anthropic_error_json_response(proxy_exception_from_http_exception(e, headers), request)

        error_msg: Final = f"{e}"
        return _anthropic_error_json_response(
            ProxyException(
                message=getattr(e, "message", error_msg),
                type=openai_error_type(e, error_status_code(e, 500)),
                param=openai_error_param(e),
                code=error_status_code(e, 500),
                headers=headers,
            ),
            request,
        )


@router.post(
    "/v1/messages/count_tokens",
    tags=["[beta] Anthropic Messages Token Counting"],
    dependencies=[Depends(user_api_key_auth)],
)
async def count_tokens(
    request: Request,
    user_api_key_dict: UserAPIKeyAuth = Depends(user_api_key_auth),  # Used for auth
):
    """
    Count tokens for Anthropic Messages API format.
    
    This endpoint follows the Anthropic Messages API token counting specification.
    It accepts the same parameters as the /v1/messages endpoint but returns
    token counts instead of generating a response.
    
    Example usage:
    ```
    curl -X POST "http://localhost:4000/v1/messages/count_tokens?beta=true" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer your-key" \
      -d '{
        "model": "claude-3-sonnet-20240229",
        "messages": [{"role": "user", "content": "Hello Claude!"}]
      }'
    ```
    
    Returns: {"input_tokens": <number>}
    """
    from litellm.proxy.proxy_server import token_counter as internal_token_counter

    litellm_call_id: Final = resolve_litellm_call_id(request.headers.get("x-litellm-call-id"))
    try:
        request_data: Final = await _read_request_body(request=request)
        native_data: Final = _NATIVE_COUNT_BODY.validate_python(request_data)
        if not native_data.get("model"):
            raise HTTPException(status_code=400, detail={"error": "model parameter is required"})
        oauth_header: Final = request.headers.get("authorization")
        oauth_response: Final = await _count_tokens_with_oauth(
            request,
            native_data,
            user_api_key_dict,
            oauth_header if is_anthropic_oauth_key(oauth_header) else None,
        )
        if oauth_response is not None:
            return oauth_response
        data: Final[dict] = {**request_data}

        # Extract required fields
        model_name: Final = data.get("model")
        messages: Final = data.get("messages", [])

        if not messages:
            raise HTTPException(status_code=400, detail={"error": "messages parameter is required"})

        # Create TokenCountRequest for the internal endpoint
        from litellm.proxy._types import TokenCountRequest

        token_request: Final = TokenCountRequest(
            model=model_name,
            messages=messages,
            tools=data.get("tools"),
            system=data.get("system"),
        )

        # Call the internal token counter function with direct request flag set to False
        token_response: Final = await internal_token_counter(
            request=token_request,
            call_endpoint=True,
        )
        _token_response_dict: dict = {}
        if isinstance(token_response, TokenCountResponse):
            _token_response_dict = token_response.model_dump()
        elif isinstance(token_response, dict):
            _token_response_dict = token_response

        # Convert the internal response to Anthropic API format
        return {"input_tokens": _token_response_dict.get("total_tokens", 0)}

    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid native token counting request")
    except HTTPException:
        raise
    except ProxyException as e:
        status_code: Final = int(e.code) if e.code and e.code.isdigit() else 500
        detail: Final = AnthropicExceptionMapping.transform_to_anthropic_error(
            status_code=status_code,
            raw_message=e.message,
        )
        raise HTTPException(
            status_code=status_code,
            detail=detail,
        )
    except Exception as e:
        log_llm_api_exception(e, litellm_call_id)
        raise HTTPException(status_code=500, detail={"error": f"Internal server error: {e}"})


@router.post(
    "/api/event_logging/batch",
    tags=["[beta] Anthropic Event Logging"],
)
async def event_logging_batch(
    request: Request,
):
    """
    Stubbed endpoint for Anthropic event logging batch requests.

    This endpoint accepts event logging requests but does nothing with them.
    It exists to prevent 404 errors from Claude Code clients that send telemetry.
    """
    return {"status": "ok"}
