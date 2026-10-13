"""LiteLLM dependencies for the private pricing policies."""

from collections.abc import Mapping
from typing import TYPE_CHECKING

from pydantic import BaseModel, JsonValue, TypeAdapter

from staticduo_litellm.pricing import memory_luna
from staticduo_litellm.pricing.catalog import apply_catalog_overlay
from staticduo_litellm.pricing.memory_luna import MEMORY_LUNA_MODEL, MemoryLunaReference

if TYPE_CHECKING:
    from litellm.router import Router


def memory_luna_reference(router: "Router | None") -> MemoryLunaReference:
    import litellm

    return memory_luna.memory_luna_reference(
        router, TypeAdapter(Mapping[str, object]).validate_python(getattr(litellm, "model_cost"))
    )


def memory_luna_response(result: object, custom_llm_provider: str | None) -> BaseModel | Mapping[str, JsonValue]:
    from litellm.cost_calculator import get_usage_object

    return memory_luna.memory_luna_response(result, custom_llm_provider, get_usage_object)


__all__ = [
    "MEMORY_LUNA_MODEL",
    "MemoryLunaReference",
    "apply_catalog_overlay",
    "memory_luna_reference",
    "memory_luna_response",
]
