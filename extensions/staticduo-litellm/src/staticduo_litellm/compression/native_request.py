from __future__ import annotations

import time
import uuid
from collections.abc import Mapping
from typing import Final

from pydantic import TypeAdapter

from .native_text import (
    NativeRequestFormat,
    extract_native_text_slots,
    has_native_retrieve_tool,
    patch_native_text_slots,
)
from .ports import NativeCompressionPorts

_TOOLS_ADAPTER: Final = TypeAdapter(list[object])


async def process_native_request(
    ports: NativeCompressionPorts,
    request_data: dict[str, object],  # mutable-ok: native provider request is the handler out-param
    request_format: NativeRequestFormat,
) -> dict[str, object]:  # mutable-ok: returns the handler request out-param
    if ports.should_bypass(request_data) or request_data.get("background"):
        return request_data
    original: Final[Mapping[str, object]] = dict(request_data)
    skip_tool: Final = ports.skip_tool
    only_tool: Final = ports.only_tool
    slots: Final = tuple(
        slot
        for slot in extract_native_text_slots(original, request_format)
        if not (skip_tool and slot.role in ("tool", "function"))
        and not (only_tool and slot.role not in ("tool", "function"))
    )
    if not slots:
        return request_data
    messages: Final = [slot.message() for slot in slots]
    model: Final = ports.model or original.get("model")
    start_time: Final = time.time()
    result: Final = await ports.compress(messages=messages, model=model if isinstance(model, str) else None)
    end_time: Final = time.time()
    patched: Final = patch_native_text_slots(original, slots, result.messages) if result.succeeded else None
    changed: Final = patched is not None and any(
        slot.text != returned["content"] for slot, returned in zip(slots, result.messages)
    )
    hashes: Final[frozenset[str]] = result.ccr_hashes if changed and ports.ccr_retrieval else frozenset()
    existing_retrieve: Final = has_native_retrieve_tool(original)
    raw_tools: Final = original.get("tools")
    tools: Final = _TOOLS_ADAPTER.validate_python(raw_tools) if isinstance(raw_tools, list) else None
    invalid_tools: Final = bool(hashes) and not existing_retrieve and "tools" in original and tools is None

    if patched is None or invalid_tools:
        if result.succeeded:
            ports.handle_failure(
                messages,
                "Headroom compression cannot be applied to the original request",
                {"reason": "invalid native text rewrite" if patched is None else "invalid native tools container"},
            )
        ports.record(
            guardrail_json_response={"error": "headroom compression unavailable; request forwarded uncompressed"},
            request_data=request_data,
            guardrail_status="guardrail_failed_to_respond",
            start_time=start_time,
            end_time=end_time,
        )
        ports.mark_applied(request_data)
        return request_data

    function: Final = ports.retrieve_function()
    native_tool: Final = (
        {"type": "function", **function}
        if request_format == "responses"
        else {
            "name": function["name"],
            "description": function["description"],
            "input_schema": function["parameters"],
        }
        if request_format == "anthropic"
        else ports.retrieve_tool()
    )
    issued_call_id: Final = (ports.resolve_call_id(original) or str(uuid.uuid4())) if hashes else None
    rewritten: Final = {
        **patched,
        **(
            {
                "tools": [
                    *(tools or ()),
                    native_tool,
                ]
            }
            if hashes and not existing_retrieve
            else {}
        ),
        **({"litellm_call_id": issued_call_id} if issued_call_id is not None else {}),
    }
    for key in ("input", "messages", "tools", "litellm_call_id"):
        if key in rewritten and rewritten[key] is not original.get(key):
            request_data[key] = rewritten[key]  # rebind-ok: native request is the handler's in-place out-param
    if issued_call_id is not None:
        ports.remember_hashes(issued_call_id, hashes)
    stats: Final[Mapping[str, object]] = (
        result.stats
        if changed
        else {
            **result.stats,
            "tokens_saved": 0,
            "tokens_after": result.stats.get("tokens_before", 0),
            "compression_ratio": 1.0,
            "transforms_applied": [],
        }
    )
    ports.record(
        guardrail_json_response=stats,
        request_data=request_data,
        guardrail_status="success",
        start_time=start_time,
        end_time=end_time,
    )
    ports.mark_applied(request_data)
    return request_data
