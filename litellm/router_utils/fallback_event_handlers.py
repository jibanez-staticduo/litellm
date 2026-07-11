import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

import litellm
from litellm._logging import verbose_router_logger
from litellm.integrations.custom_logger import CustomLogger
from litellm.litellm_core_utils.sensitive_data_masker import mask_sensitive_structure
from litellm.router_utils.add_retry_fallback_headers import (
    add_fallback_headers_to_response,
    get_fallback_error_info,
)
from litellm.router_utils.batch_utils import _get_router_metadata_variable_name
from litellm.router_utils.cooldown_handlers import (
    _first_present,  # pyright: ignore[reportPrivateUsage] - shared internal helper, used across router_utils
    _set_cooldown_deployments,  # pyright: ignore[reportPrivateUsage] - shared helper, used across router_utils
    cast_exception_status_to_int,
    is_advisor_orchestration_failure,
)
from litellm.router_utils.router_callbacks.track_deployment_metrics import (
    increment_deployment_failures_for_current_minute,
)
from litellm.types.router import LiteLLMParamsTypedDict

if TYPE_CHECKING:
    from litellm.router import Router as _Router

    LitellmRouter = _Router
else:
    LitellmRouter = Any

_router_fallback_identity: ContextVar[Optional[Tuple[object, object]]] = ContextVar(
    "router_fallback_identity", default=None
)


def _check_stripped_model_group(model_group: str, fallback_key: str) -> bool:
    """
    Handles wildcard routing scenario

    where fallbacks set like:
    [{"gpt-3.5-turbo": ["claude-3-haiku"]}]

    but model_group is like:
    "openai/gpt-3.5-turbo"

    Returns:
    - True if the stripped model group == fallback_key
    """
    for provider in litellm.provider_list:
        if isinstance(provider, Enum):
            _provider = provider.value
        else:
            _provider = provider
        if model_group.startswith(f"{_provider}/"):
            stripped_model_group = model_group.replace(f"{_provider}/", "")
            if stripped_model_group == fallback_key:
                return True
    return False


def get_fallback_model_group(fallbacks: list[Any], model_group: str) -> tuple[list[str] | None, int | None]:
    """
    Returns:
    - fallback_model_group: List[str] of fallback model groups. example: ["gpt-4", "gpt-3.5-turbo"]
    - generic_fallback_idx: int of the index of the generic fallback in the fallbacks list.

    Checks:
    - exact match
    - stripped model group match
    - generic fallback
    """
    generic_fallback_idx: int | None = None
    stripped_model_fallback: list[str] | None = None
    fallback_model_group: list[str] | None = None
    ## check for specific model group-specific fallbacks
    for idx, item in enumerate(fallbacks):
        if isinstance(item, dict):
            if list(item.keys())[0] == model_group:  # check exact match
                fallback_model_group = item[model_group]
                break
            elif _check_stripped_model_group(
                model_group=model_group, fallback_key=list(item.keys())[0]
            ):  # check generic fallback
                stripped_model_fallback = item[list(item.keys())[0]]
            elif list(item.keys())[0] == "*":  # check generic fallback
                generic_fallback_idx = idx
        elif isinstance(item, str):
            fallback_model_group = [item]
    ## if none, check for generic fallback
    if fallback_model_group is None:
        if stripped_model_fallback is not None:
            fallback_model_group = stripped_model_fallback
        elif generic_fallback_idx is not None:
            fallback_model_group = fallbacks[generic_fallback_idx]["*"]

    return fallback_model_group, generic_fallback_idx


def _chatgpt_auth_profiles(litellm_router: LitellmRouter, model_group: object) -> Optional[frozenset[str]]:
    if not isinstance(model_group, str):
        return None
    deployments = litellm_router.get_model_list(model_name=model_group) or []
    identities = []
    for deployment in deployments:
        if not isinstance(deployment, dict):
            continue
        params = deployment.get("litellm_params") or {}
        physical_model = params.get("model")
        provider = params.get("custom_llm_provider")
        is_chatgpt = provider == "chatgpt" or (
            isinstance(physical_model, str) and physical_model.startswith("chatgpt/")
        )
        if is_chatgpt:
            identities.append(str(params.get("chatgpt_auth_profile") or "default"))
    return frozenset(identities)


def _is_cross_profile_fallback(
    litellm_router: LitellmRouter, source_model_group: str, target_model_group: object
) -> bool:
    source_profiles = _chatgpt_auth_profiles(litellm_router, source_model_group)
    target_profiles = _chatgpt_auth_profiles(litellm_router, target_model_group)
    if source_profiles is None or target_profiles is None:
        return True
    if not source_profiles and not target_profiles:
        return False
    if not source_profiles or not target_profiles:
        return True
    return len(source_profiles) != 1 or len(target_profiles) != 1 or source_profiles != target_profiles


def get_internal_router_fallback_identity() -> Optional[Tuple[object, object]]:
    return _router_fallback_identity.get()


def validate_chatgpt_model_group_profiles(deployments: List[Dict[str, Any]], model_group: str) -> None:
    profiles = frozenset(
        str(params.get("chatgpt_auth_profile") or "default")
        for deployment in deployments
        for params in ((deployment.get("litellm_params") or {}),)
        if params.get("custom_llm_provider") == "chatgpt"
        or (isinstance(params.get("model"), str) and params["model"].startswith("chatgpt/"))
    )
    if len(profiles) > 1:
        raise ValueError(f"ChatGPT model group {model_group!r} contains mixed authentication profiles")


async def run_async_fallback(
    *args: tuple[Any],
    litellm_router: LitellmRouter,
    fallback_model_group: list[str],
    original_model_group: str,
    original_exception: Exception,
    max_fallbacks: int,
    fallback_depth: int,
    include_fallback_errors: bool = False,
    **kwargs,
) -> Any:
    """
    Loops through all the fallback model groups and calls kwargs["original_function"] with the arguments and keyword arguments provided.

    If the call is successful, it logs the success and returns the response.
    If the call fails, it logs the failure and continues to the next fallback model group.
    If all fallback model groups fail, it raises the most recent exception.

    Args:
        litellm_router: The litellm router instance.
        *args: Positional arguments.
        fallback_model_group: List[str] of fallback model groups. example: ["gpt-4", "gpt-3.5-turbo"]
        original_model_group: The original model group. example: "gpt-3.5-turbo"
        original_exception: The original exception.
        **kwargs: Keyword arguments. `attempted_targets` carries the fallback attempts
            already made for this request, created on the first hop and shared by reference
            for the rest of the walk. A target already in it is skipped, so neither a
            fallback graph that loops back on itself nor a client-side fallback list
            re-walked at each level can repeat an attempt that has already failed. Identity
            comes from `fallback_attempt_key`, so an entry that overrides request params or
            re-targets the failed group with a different deployment selection stays distinct
            from a bare name.

    Returns:
        The response from the successful fallback model group.
    Raises:
        The most recent exception if all fallback model groups fail.
    """

    ### BASE CASE ### MAX FALLBACK DEPTH REACHED
    if fallback_depth >= max_fallbacks:
        raise original_exception

    error_from_fallbacks = original_exception
    fallback_errors = (get_fallback_error_info(original_exception),)
    logical_model_group = kwargs.get("logical_model_group", original_model_group)
    requested_model = kwargs.get("original_requested_model", logical_model_group)
    base_kwargs = dict(kwargs)

    for attempt, mg in enumerate(fallback_model_group, start=1):
        if mg == original_model_group:
            continue
        target_model_group = mg if isinstance(mg, str) else mg.get("model")
        if not getattr(litellm_router, "allow_chatgpt_cross_profile_fallback", False) and _is_cross_profile_fallback(
            litellm_router, logical_model_group, target_model_group
        ):
            verbose_router_logger.warning(
                "router_fallback_denied logical_model_group=%s current_model_group=%s reason=chatgpt_cross_profile",
                mask_sensitive_structure(logical_model_group),
                mask_sensitive_structure(target_model_group),
            )
            continue
        attempt_kwargs = dict(base_kwargs)
        try:
            attempt_kwargs = litellm_router.log_retry(kwargs=attempt_kwargs, e=original_exception)
            if isinstance(mg, str):
                attempt_kwargs["model"] = mg
            elif isinstance(mg, dict):
                attempt_kwargs.update(mg)
            current_model_group = attempt_kwargs.get("model")
            metadata = dict(attempt_kwargs.get("metadata") or {})
            metadata.update(
                {
                    "model_group": current_model_group,
                    "logical_model_group": logical_model_group,
                    "original_requested_model": requested_model,
                    "fallback_source_model_group": original_model_group,
                    "fallback_attempt": attempt,
                    "fallback_reason": type(original_exception).__name__,
                }
            )
            attempt_kwargs["metadata"] = metadata
            attempt_kwargs["logical_model_group"] = logical_model_group
            attempt_kwargs["original_requested_model"] = requested_model
            attempt_kwargs.pop("_router_fallback_identity", None)
            current_fallback_depth = fallback_depth + 1
            attempt_kwargs["fallback_depth"] = current_fallback_depth
            attempt_kwargs["max_fallbacks"] = max_fallbacks
            if include_fallback_errors:
                attempt_kwargs["include_fallback_errors"] = include_fallback_errors
            verbose_router_logger.info(
                "router_fallback request_id_hash=%s requested_model=%s logical_model_group=%s current_model_group=%s "
                "selected_profile=%s deployment_prefix=%s attempt=%s fallback_source=%s fallback_reason=%s",
                hashlib.sha256(
                    str(metadata.get("request_id") or metadata.get("litellm_call_id") or "").encode()
                ).hexdigest()[:12],
                mask_sensitive_structure(requested_model),
                mask_sensitive_structure(logical_model_group),
                mask_sensitive_structure(current_model_group),
                next(iter(_chatgpt_auth_profiles(litellm_router, current_model_group) or ("none",))),
                str(metadata.get("deployment_id") or "none")[:8],
                attempt,
                mask_sensitive_structure(original_model_group),
                type(original_exception).__name__,
            )
            identity_token = _router_fallback_identity.set((requested_model, logical_model_group))
            try:
                response = await litellm_router.async_function_with_fallbacks(*args, **attempt_kwargs)
            finally:
                _router_fallback_identity.reset(identity_token)
            verbose_router_logger.info("Successful fallback b/w models.")
            response = add_fallback_headers_to_response(
                response=response,
                attempted_fallbacks=current_fallback_depth,
                fallback_errors=(list(fallback_errors) if include_fallback_errors else None),
            )
            # callback for successfull_fallback_event():
            await log_success_fallback_event(
                original_model_group=original_model_group,
                kwargs=attempt_kwargs,
                original_exception=original_exception,
            )
            return response
        except Exception as e:
            error_from_fallbacks = e
            fallback_errors = fallback_errors + (get_fallback_error_info(e),)
            await log_failure_fallback_event(
                original_model_group=original_model_group,
                kwargs=attempt_kwargs,
                original_exception=original_exception,
            )
            logging_obj = kwargs.get("litellm_logging_obj")
            if logging_obj is not None and logging_obj.model_call_details.get("has_logged_async_failure", False):
                _trigger_cooldown_for_failed_deployment(
                    litellm_router=litellm_router,
                    kwargs=kwargs,
                    exception=e,
                )
    raise error_from_fallbacks


async def log_success_fallback_event(original_model_group: str, kwargs: dict, original_exception: Exception):
    """
    Log a successful fallback event to all registered callbacks.

    Uses LoggingCallbackManager.get_custom_loggers_for_type() to get deduplicated
    CustomLogger instances from all callback lists.

    Args:
        original_model_group (str): The original model group before fallback.
        kwargs (dict): kwargs for the request

    Note:
        Errors during logging are caught and reported but do not interrupt the process.
    """
    # Get deduplicated CustomLogger instances from all callback lists
    custom_loggers: Final = litellm.logging_callback_manager.get_custom_loggers_for_type(CustomLogger)

    for _callback_custom_logger in custom_loggers:
        try:
            await _callback_custom_logger.log_success_fallback_event(
                original_model_group=original_model_group,
                kwargs=kwargs,
                original_exception=original_exception,
            )
        except Exception as e:
            verbose_router_logger.error("Error in log_success_fallback_event: %s", e)


async def log_failure_fallback_event(original_model_group: str, kwargs: dict, original_exception: Exception):
    """
    Log a failed fallback event to all registered callbacks.

    Uses LoggingCallbackManager.get_custom_loggers_for_type() to get deduplicated
    CustomLogger instances from all callback lists.

    Args:
        original_model_group (str): The original model group before fallback.
        kwargs (dict): kwargs for the request

    Note:
        Errors during logging are caught and reported but do not interrupt the process.
    """
    # Get deduplicated CustomLogger instances from all callback lists
    custom_loggers: Final = litellm.logging_callback_manager.get_custom_loggers_for_type(CustomLogger)

    for _callback_custom_logger in custom_loggers:
        try:
            await _callback_custom_logger.log_failure_fallback_event(
                original_model_group=original_model_group,
                kwargs=kwargs,
                original_exception=original_exception,
            )
        except Exception as e:
            verbose_router_logger.error("Error in log_failure_fallback_event: %s", e)


def _check_non_standard_fallback_format(fallbacks: list[Any] | None) -> bool:
    """
    Checks if the fallbacks list is a list of strings or a list of dictionaries.

    If
    - List[str]: e.g. ["claude-3-haiku", "openai/o-1"]
    - List[Dict[<LiteLLMParamsTypedDict>, Any]]: e.g. [{"model": "claude-3-haiku", "messages": [{"role": "user", "content": "Hey, how's it going?"}]}]

    If [{"gpt-3.5-turbo": ["claude-3-haiku"]}] then standard format.
    """
    if fallbacks is None or not isinstance(fallbacks, list) or len(fallbacks) == 0:
        return False
    if all(isinstance(item, str) for item in fallbacks):
        return True
    elif all(isinstance(item, dict) for item in fallbacks):
        for item in fallbacks:
            for key in LiteLLMParamsTypedDict.__annotations__:
                if key in item:
                    # If the value is a list, it's likely a standard fallback model group mapping
                    # (e.g. {"model": ["backup"]}) rather than a parameter override.
                    if not isinstance(item[key], list):
                        return True

    return False


def run_non_standard_fallback_format(fallbacks: list[str] | list[dict[str, Any]], model_group: str):
    pass
