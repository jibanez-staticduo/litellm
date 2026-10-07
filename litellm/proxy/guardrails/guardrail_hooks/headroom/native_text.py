from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import chain
from typing import Final, Literal, TypeAlias, cast

NativeRequestFormat: TypeAlias = Literal["responses", "anthropic", "chat"]
TextPath: TypeAlias = tuple[str | int, ...]


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    fields: Final = cast("Mapping[object, object]", value)  # cast-ok: isinstance checked the mapping container
    if not all(isinstance(key, str) for key in fields):
        return None
    return cast("Mapping[str, object]", fields)  # cast-ok: string keys checked above


def _sequence(value: object) -> Sequence[object] | None:
    return cast("Sequence[object]", value) if isinstance(value, list) else None  # cast-ok: JSON array container checked


@dataclass(frozen=True, slots=True)
class NativeTextSlot:
    path: TextPath
    text: str
    role: str
    tool_call_id: str | None = None

    def message(self) -> dict[str, object]:  # mutable-ok: compressor HTTP payload requires a JSON object
        return {  # mutable-ok: compressor HTTP payload requires a JSON object
            "role": self.role,
            "content": self.text,
            "headroom_native_text_path": list(self.path),  # mutable-ok: compressor path marker is a JSON array
            **(
                {"tool_call_id": self.tool_call_id}  # mutable-ok: optional compressor JSON field
                if self.tool_call_id is not None
                else {}  # mutable-ok: optional JSON
            ),
        }


def _role(item: Mapping[str, object], request_format: NativeRequestFormat) -> str | None:
    if request_format == "responses":
        kind: Final = item.get("type")
        if kind in ("function_call", "custom_tool_call"):
            return "assistant"
        if kind in ("function_call_output", "custom_tool_call_output"):
            return "tool"
        if kind not in (None, "message"):
            return None
    value: Final = item.get("role")
    return value if isinstance(value, str) else None


def _calls(item: Mapping[str, object], request_format: NativeRequestFormat) -> tuple[tuple[str, str], ...]:
    if request_format == "responses" and item.get("type") in ("function_call", "custom_tool_call"):
        response_call_id: Final = item.get("call_id")
        response_name: Final = item.get("name")
        return (
            ((response_call_id, response_name),)
            if isinstance(response_call_id, str) and isinstance(response_name, str)
            else ()
        )
    blocks: Final = _sequence(item.get("content") if request_format == "anthropic" else item.get("tool_calls"))
    if blocks is None or item.get("role") != "assistant":
        return ()
    return tuple(
        (call_id, name)
        for block in blocks
        if (fields := _mapping(block)) is not None
        and (request_format != "anthropic" or fields.get("type") == "tool_use")
        and isinstance(call_id := fields.get("id"), str)
        and isinstance(name := (_mapping(fields.get("function")) or fields).get("name"), str)
    )


def _has_cache_control(value: object) -> bool:
    fields: Final = _mapping(value)
    if fields is not None:
        return "cache_control" in fields or any(_has_cache_control(part) for part in fields.values())
    parts: Final = _sequence(value)
    return parts is not None and any(_has_cache_control(part) for part in parts)


def _leaf_slots(value: object, path: TextPath, role: str, call_id: str | None) -> tuple[NativeTextSlot, ...]:
    if isinstance(value, str):
        return (NativeTextSlot(path, value, role, call_id),) if value else ()
    fields: Final = _mapping(value)
    if fields is not None:
        text: Final = fields.get("text")
        return (
            (NativeTextSlot((*path, "text"), text, role, call_id),)
            if fields.get("type") in ("text", "input_text", "output_text") and isinstance(text, str) and text
            else ()
        )
    parts: Final = _sequence(value)
    if parts is None:
        return ()
    return tuple(
        NativeTextSlot((*path, index, "text"), part_text, role, call_id)
        for index, part in enumerate(parts)
        if (part_fields := _mapping(part)) is not None
        and part_fields.get("type") in ("text", "input_text", "output_text")
        and isinstance(part_text := part_fields.get("text"), str)
        and part_text
    )


def _anthropic_block_slots(
    block: Mapping[str, object], path: TextPath, role: str, protected_call_ids: frozenset[str]
) -> tuple[NativeTextSlot, ...]:
    if block.get("type") != "tool_result":
        return _leaf_slots(block, path, role, None)
    tool_id: Final = block.get("tool_use_id")
    if not isinstance(tool_id, str) or tool_id in protected_call_ids:
        return ()
    return _leaf_slots(block.get("content"), (*path, "content"), "tool", tool_id)


def _item_slots(
    item: Mapping[str, object],
    path: TextPath,
    role: str,
    request_format: NativeRequestFormat,
    protected_call_ids: frozenset[str],
) -> tuple[NativeTextSlot, ...]:
    call_id: Final = item.get("call_id") if request_format == "responses" else item.get("tool_call_id")
    result_id: Final = call_id if isinstance(call_id, str) else None
    if result_id in protected_call_ids:
        return ()
    if request_format == "responses" and item.get("type") in ("function_call_output", "custom_tool_call_output"):
        return _leaf_slots(item.get("output"), (*path, "output"), "tool", result_id)
    content: Final = item.get("content")
    parts: Final = _sequence(content)
    if request_format != "anthropic" or parts is None:
        return _leaf_slots(content, (*path, "content"), role, result_id)
    block_slots: Final = (
        _anthropic_block_slots(block, (*path, "content", index), role, protected_call_ids)
        for index, part in enumerate(parts)
        if (block := _mapping(part)) is not None
    )
    return tuple(chain.from_iterable(block_slots))


def extract_native_text_slots(
    request: Mapping[str, object], request_format: NativeRequestFormat
) -> tuple[NativeTextSlot, ...]:
    key: Final = "input" if request_format == "responses" else "messages"
    raw: Final = _sequence(request.get(key))
    if raw is None or "cache_control" in request:
        return ()
    items: Final = tuple(_mapping(item) for item in raw)
    roles: Final = tuple(_role(item, request_format) if item is not None else None for item in items)
    last_user: Final = max((index for index, role in enumerate(roles) if role == "user"), default=-1)
    last_assistant: Final = max((index for index, role in enumerate(roles) if role == "assistant"), default=-1)
    assistant_start: Final = max(
        (index + 1 for index, role in enumerate(roles[:last_assistant]) if role not in (None, "assistant")), default=0
    )
    recent_calls: Final = chain.from_iterable(
        _calls(item, request_format) for item in items[assistant_start : last_assistant + 1] if item is not None
    )
    recent_call_ids: Final = frozenset(call_id for call_id, _ in recent_calls)
    recent_exchange_end: Final = next(
        (index for index in range(last_assistant + 1, len(roles)) if roles[index] not in (None, "tool", "function")),
        len(roles),
    )
    all_calls: Final = chain.from_iterable(_calls(item, request_format) for item in items if item is not None)
    retrieved_call_ids: Final = frozenset(
        call_id for call_id, name in all_calls if name == "headroom_retrieve" or name.endswith("__headroom_retrieve")
    )
    cached_prefix: Final = max((index for index, item in enumerate(raw) if _has_cache_control(item)), default=-1)
    protected_call_ids: Final = recent_call_ids | retrieved_call_ids
    eligible_slots: Final = (
        _item_slots(item, (key, index), role, request_format, protected_call_ids)
        for index, (item, role) in enumerate(zip(items, roles))
        if item is not None
        and role in ("user", "tool", "function")
        and index > cached_prefix
        and index != last_user
        and not (last_assistant >= 0 and last_assistant < index < recent_exchange_end)
    )
    return tuple(chain.from_iterable(eligible_slots))


def _patched_value(original: object, path: TextPath, replacement: str) -> object:
    if not path:
        return replacement
    head, *tail = path
    fields: Final = _mapping(original)
    if isinstance(head, str) and fields is not None:
        return {  # mutable-ok: copied provider JSON ancestor
            **fields,
            head: _patched_value(fields[head], tuple(tail), replacement),
        }
    elements: Final = _sequence(original)
    if isinstance(head, int) and elements is not None:
        return [  # mutable-ok: preserve the provider's original JSON array container
            _patched_value(value, tuple(tail), replacement) if index == head else value
            for index, value in enumerate(elements)
        ]
    raise ValueError("Native text slot no longer addresses the original request")


def patch_native_text_slots(
    request: Mapping[str, object], slots: Sequence[NativeTextSlot], returned_messages: Sequence[Mapping[str, object]]
) -> dict[str, object] | None:  # mutable-ok: patched provider request must retain its JSON object container
    if len(slots) != len(returned_messages):
        return None
    if any(
        not isinstance(text := returned.get("content"), str)
        or not text
        or returned != {**slot.message(), "content": text}  # mutable-ok: compare the exact compressor JSON row
        for slot, returned in zip(slots, returned_messages)
    ):
        return None
    from functools import reduce

    patched: Final = reduce(
        lambda original, pair: _patched_value(original, pair[0].path, str(pair[1]["content"])),
        ((slot, returned) for slot, returned in zip(slots, returned_messages) if slot.text != returned["content"]),
        request,
    )
    fields: Final = _mapping(patched)
    return dict(fields) if fields is not None else None  # mutable-ok: provider receives a copied JSON object


def has_native_retrieve_tool(request: Mapping[str, object]) -> bool:
    def contains(value: object) -> bool:
        entries: Final = _sequence(value)
        if entries is None:
            return False
        return any(
            tool.get("name") == "headroom_retrieve"
            or (
                (function := _mapping(tool.get("function"))) is not None and function.get("name") == "headroom_retrieve"
            )
            or contains(tool.get("tools"))
            for entry in entries
            if (tool := _mapping(entry)) is not None
        )

    if contains(request.get("tools")):
        return True
    raw_input: Final = _sequence(request.get("input"))
    return raw_input is not None and any(
        contains(item.get("tools"))
        for raw in raw_input
        if (item := _mapping(raw)) is not None and item.get("type") == "additional_tools"
    )
