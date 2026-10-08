"""Resolve the canonical deployment prices for the memory aliases."""

from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

from pydantic import BaseModel, JsonValue, TypeAdapter

import litellm
from litellm.cost_calculator import get_usage_object

if TYPE_CHECKING:
    from litellm.router import Router

MEMORY_LUNA_MODEL: Final = "chatgpt/gpt-6-luna"
_JSON_MAPPING: Final = TypeAdapter(dict[str, JsonValue])
_OBJECT_MAPPING: Final = TypeAdapter(Mapping[str, object])
_EMPTY_MAPPING: Final[Mapping[str, object]] = MappingProxyType({})


@dataclass(frozen=True)
class MemoryLunaReference:
    model_id: str
    rates: Mapping[str, JsonValue]


def _pricing_field(key: str, value: JsonValue) -> bool:
    return (("cost" in key or "multiplier" in key) and isinstance(value, (int, float))) or (
        key in ("off_peak_pricing", "tiered_pricing") and isinstance(value, (dict, list))
    )


def _deployment_reference(router: "Router", deployment: Mapping[str, object]) -> MemoryLunaReference:
    model_info: Final = _JSON_MAPPING.validate_python(deployment["model_info"])
    params: Final = _JSON_MAPPING.validate_python(deployment["litellm_params"])
    model_id: Final = model_info.get("id")
    model: Final = params.get("model")
    if not isinstance(model_id, str) or not isinstance(model, str):
        raise ValueError("memory Luna pricing: invalid canonical deployment")
    info: Final = _JSON_MAPPING.validate_python(router.get_deployment_model_info(model_id=model_id, model_name=model))
    rates: Final = MappingProxyType({key: value for key, value in info.items() if _pricing_field(key, value)})
    for key in ("input_cost_per_token", "output_cost_per_token"):
        if (
            not isinstance((rate := rates.get(key)), (int, float))
            or isinstance(rate, bool)
            or not isfinite(rate)
            or rate <= 0
        ):
            raise ValueError("memory Luna pricing: canonical token rates unavailable")
    cost_entries: Final = _OBJECT_MAPPING.validate_python(getattr(litellm, "model_cost"))
    registered: Final = _JSON_MAPPING.validate_python(cost_entries.get(model_id, _EMPTY_MAPPING))
    if any(registered.get(key) != value for key, value in rates.items()):
        raise ValueError("memory Luna pricing: canonical deployment rates not registered")
    return MemoryLunaReference(model_id=model_id, rates=rates)


def memory_luna_reference(router: "Router | None") -> MemoryLunaReference:
    if router is None:
        raise ValueError("memory Luna pricing: canonical router unavailable")
    deployments: Final = router.get_model_list(model_name="gpt-6-luna") or ()
    references: Final = tuple(_deployment_reference(router, deployment) for deployment in deployments)
    if not references or any(reference.rates != references[0].rates for reference in references):
        raise ValueError("memory Luna pricing: missing or ambiguous canonical deployments")
    return references[0]


def memory_luna_response(result: object, custom_llm_provider: str | None) -> BaseModel | Mapping[str, JsonValue]:
    usage: Final = get_usage_object(completion_response=result)
    if usage is None:
        raise ValueError("memory Luna pricing: missing token usage")
    hidden: Final = _OBJECT_MAPPING.validate_python(getattr(result, "_hidden_params", None) or MappingProxyType({}))
    if hidden.get("additional_costs") or getattr(usage, "additional_usage", None) or custom_llm_provider == "azure_ai":
        raise ValueError("memory Luna pricing: unsupported provider additional usage/costs")
    if not isinstance(result, (BaseModel, dict)):
        raise ValueError("memory Luna pricing: unsupported response shape")
    data: Final = _JSON_MAPPING.validate_python(result.model_dump() if isinstance(result, BaseModel) else result)
    raw_usage: Final = data.get("usage")
    if not isinstance(raw_usage, dict):
        raise ValueError("memory Luna pricing: unsupported token usage")
    # Reconstruct the response without provider monetary hints or private hidden costs.
    response_data: Final = MappingProxyType({key: value for key, value in data.items() if key != "_hidden_params"})
    priced_data: Final = MappingProxyType(
        {
            **response_data,
            "model": MEMORY_LUNA_MODEL,
            "usage": _JSON_MAPPING.validate_python(
                MappingProxyType({key: value for key, value in raw_usage.items() if key != "cost"})
            ),
        }
    )
    return (
        type(result).model_validate(priced_data)
        if isinstance(result, BaseModel)
        else _JSON_MAPPING.validate_python(priced_data)
    )
