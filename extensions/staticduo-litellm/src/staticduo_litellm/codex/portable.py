"""Opt-in plaintext collaboration transport for official Codex clients."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from itertools import chain
from typing import Final, Literal, Protocol

from pydantic import TypeAdapter

_NAMESPACE: Final = "portable_collaboration"
_MESSAGE_TOOLS: Final = frozenset({"spawn_agent", "send_message", "followup_task"})
CONTEXT: Final = "litellm_portable_codex_agents"
_MAPPING: Final = TypeAdapter(dict[str, object])
_ITEMS: Final = TypeAdapter(list[object])
_JSON: Final = TypeAdapter(object)
ROUTES: Final = frozenset({"/responses", "/v1/responses", "/openai/responses", "/openai/v1/responses"})


class ReplayStore(Protocol):
    async def contains(self, key: str) -> bool: ...

    async def record(self, key: str) -> None: ...

    async def get_mode(self, key: str) -> str | None: ...

    async def claim_mode(self, key: str, mode: str) -> str: ...


@dataclass(frozen=True, slots=True)
class PortableTransportError(Exception):
    status_code: int
    detail: str


@dataclass(frozen=True, slots=True)
class RequestContext:
    owner: str
    tools: frozenset[str]


def object_mapping(value: object) -> Mapping[str, object]:
    return _MAPPING.validate_python(value) if isinstance(value, Mapping) else {}


def items(value: object) -> tuple[object, ...]:
    return tuple(_ITEMS.validate_python(value)) if isinstance(value, list) else ()


def _has_collaboration_tool(value: object) -> bool:
    tool: Final = object_mapping(value)
    return (tool.get("type") == "namespace" and tool.get("name") in ("collaboration", _NAMESPACE)) or any(
        _has_collaboration_tool(item) for item in items(tool.get("tools"))
    )


def needs_transport(data: Mapping[str, object]) -> bool:
    return any(_has_collaboration_tool(tool) for tool in items(data.get("tools"))) or any(
        object_mapping(item).get("type") == "agent_message"
        or object_mapping(item).get("namespace") == "collaboration"
        or (object_mapping(item).get("type") == "additional_tools" and _has_collaboration_tool(item))
        for item in items(data.get("input"))
    )


def mode_key(data: Mapping[str, object], owner: str) -> str:
    metadata: Final = object_mapping(data.get("client_metadata"))
    headers: Final = object_mapping(object_mapping(data.get("proxy_server_request")).get("headers"))
    thread: Final = metadata.get("thread_id") or headers.get("thread_id")
    if not isinstance(thread, str) or not thread:
        raise PortableTransportError(400, "Portable collaboration requires the stable Codex thread_id.")
    return "litellm:portable_codex_agents:mode:v1:" + hashlib.sha256(json.dumps((owner, thread)).encode()).hexdigest()


async def has_legacy_history(data: Mapping[str, object], owner: str, store: ReplayStore) -> bool:
    for value in items(data.get("input")):
        if await _is_legacy_item(value, owner, store):
            return True
    return False


def _message_arguments_kind(item: Mapping[str, object]) -> Literal["plaintext", "invalid", "opaque"]:
    arguments: Final = item.get("arguments")
    if not isinstance(arguments, str):
        return "invalid"
    try:
        parsed: Final = _JSON.validate_json(arguments)
    except ValueError:
        return "opaque"
    return "plaintext" if isinstance(object_mapping(parsed).get("message"), str) else "invalid"


async def _is_legacy_item(value: object, owner: str, store: ReplayStore) -> bool:
    item: Final = object_mapping(value)
    if item.get("type") in ("compaction", "context_compaction"):
        return True
    if item.get("type") == "agent_message" and any(
        object_mapping(block).get("type") == "encrypted_content" for block in items(item.get("content"))
    ):
        return True
    if (
        item.get("type") == "function_call"
        and item.get("namespace") == "collaboration"
        and item.get("name") in _MESSAGE_TOOLS
    ):
        marker: Final = item.get("encrypted_function_args")
        if marker not in (None, []):
            return True
        if (
            marker is None
            and _message_arguments_kind(item) == "opaque"
            and not await store.contains(_replay_key(owner, item))
        ):
            return True
    return False


def _replay_key(owner: str, item: Mapping[str, object]) -> str:
    call_id: Final = item.get("call_id")
    arguments: Final = item.get("arguments")
    if not isinstance(call_id, str) or not call_id or not isinstance(arguments, str):
        raise PortableTransportError(400, "Portable agent call is missing its identity or arguments.")
    digest: Final = hashlib.sha256(json.dumps((owner, item.get("name"), call_id, arguments)).encode()).hexdigest()
    return "litellm:portable_codex_agents:v1:" + digest


def _rewrite_tool(value: object) -> tuple[object, frozenset[str]]:
    tool: Final = object_mapping(value)
    if tool.get("type") == "namespace" and tool.get("name") == _NAMESPACE:
        raise PortableTransportError(400, "Portable collaboration namespace is reserved by the adapter.")
    if tool.get("type") != "namespace":
        return value, frozenset()
    if tool.get("name") != "collaboration":
        nested: Final = tuple(_rewrite_tool(item) for item in items(tool.get("tools")))
        return {**tool, "tools": [item for item, _ in nested]}, frozenset(
            chain.from_iterable(names for _, names in nested)
        )
    functions: Final = tuple(object_mapping(item) for item in items(tool.get("tools")))
    return {
        **tool,
        "name": _NAMESPACE,
        "tools": [_plaintext_schema(function) for function in functions],
    }, frozenset(str(function["name"]) for function in functions if isinstance(function.get("name"), str))


def _plaintext_schema(function: Mapping[str, object]) -> Mapping[str, object]:
    if function.get("name") not in _MESSAGE_TOOLS:
        return function
    parameters: Final = object_mapping(function.get("parameters"))
    properties: Final = object_mapping(parameters.get("properties"))
    message: Final = object_mapping(properties.get("message"))
    if message.get("type") != "string":
        raise PortableTransportError(400, "Portable collaboration requires a string message schema.")
    return {
        **function,
        "parameters": {
            **parameters,
            "properties": {
                **properties,
                "message": {key: value for key, value in message.items() if key != "encrypted"},
            },
        },
    }


async def transform_request(
    original: Mapping[str, object], owner: str, store: ReplayStore, *, native_history: bool = False
) -> tuple[Mapping[str, object], RequestContext]:
    if original.get("previous_response_id"):
        raise PortableTransportError(
            400, "Portable agent transport requires full history; previous_response_id is unsupported."
        )
    tools: Final = tuple(_rewrite_tool(tool) for tool in items(original.get("tools")))
    discovered_tools: Final = chain.from_iterable(
        items(object_mapping(item).get("tools"))
        for item in items(original.get("input"))
        if object_mapping(item).get("type") == "additional_tools"
    )
    discovered: Final = tuple(names for _, names in (_rewrite_tool(tool) for tool in discovered_tools))
    input_items: Final = [
        await _request_item(item, owner, store, native_history=native_history) for item in items(original.get("input"))
    ]
    choice: Final = object_mapping(original.get("tool_choice"))
    rewritten_choice: Final = (
        {**choice, "namespace": _NAMESPACE} if choice.get("namespace") == "collaboration" else choice
    )
    return {
        **original,
        **({"tools": [tool for tool, _ in tools]} if "tools" in original else {}),
        **({"input": input_items} if isinstance(original.get("input"), list) else {}),
        **({"tool_choice": rewritten_choice} if choice else {}),
    }, RequestContext(owner, frozenset(chain.from_iterable((*discovered, *(names for _, names in tools)))))


async def _request_item(value: object, owner: str, store: ReplayStore, *, native_history: bool = False) -> object:
    item: Final = object_mapping(value)
    if item.get("type") == "additional_tools":
        return {**item, "tools": [_rewrite_tool(tool)[0] for tool in items(item.get("tools"))]}
    if item.get("type") == "function_call" and item.get("namespace") == "collaboration":
        if native_history:
            native_marker: Final = item.get("encrypted_function_args")
            if native_marker not in (None, []):
                return value
            if (
                native_marker is None
                and (item.get("name") not in _MESSAGE_TOOLS or _message_arguments_kind(item) == "opaque")
                and not await store.contains(_replay_key(owner, item))
            ):
                return value
        if item.get("name") in _MESSAGE_TOOLS:
            marker: Final = item.get("encrypted_function_args")
            if marker not in (None, []):
                raise PortableTransportError(400, "Encrypted collaboration history cannot use portable transport.")
            if _message_arguments_kind(item) != "plaintext":
                raise PortableTransportError(400, "Portable collaboration arguments require a plaintext message string.")
            _replay_key(owner, item)
        return {**item, "namespace": _NAMESPACE}
    if item.get("type") != "agent_message":
        return value
    content: Final = item.get("content")
    blocks: Final = ({"type": "input_text", "text": content},) if isinstance(content, str) else items(content)
    if not blocks or any(object_mapping(block).get("type") != "input_text" for block in blocks):
        if native_history:
            return value
        raise PortableTransportError(400, "Encrypted agent assignments require a fresh task using portable transport.")
    return {
        "type": "message",
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": json.dumps({"author": item.get("author"), "recipient": item.get("recipient")}),
            },
            *blocks,
        ],
    }


async def _response_item(value: object, context: RequestContext, store: ReplayStore, complete: bool) -> object:
    item: Final = object_mapping(value)
    if item.get("type") != "function_call" or item.get("namespace") != _NAMESPACE:
        return value
    if item.get("name") not in context.tools:
        raise PortableTransportError(502, "Upstream returned an unadvertised portable collaboration tool.")
    if item.get("name") not in _MESSAGE_TOOLS:
        if complete:
            await store.record(_replay_key(context.owner, item))
        return {**item, "namespace": "collaboration"}
    if item.get("encrypted_function_args") not in (None, []):
        raise PortableTransportError(502, "Upstream returned encrypted portable collaboration arguments.")
    if complete:
        try:
            arguments: Final = _JSON.validate_json(str(item.get("arguments")))
        except ValueError:
            raise PortableTransportError(502, "Upstream returned invalid portable collaboration arguments.") from None
        if not isinstance(object_mapping(arguments).get("message"), str):
            raise PortableTransportError(502, "Upstream returned a portable call without a plaintext message string.")
        await store.record(_replay_key(context.owner, item))
    return {**item, "namespace": "collaboration", "encrypted_function_args": []}


async def transform_response(
    value: Mapping[str, object], context: RequestContext, store: ReplayStore
) -> Mapping[str, object]:
    direct: Final = object_mapping(await _response_item(value, context, store, True))
    nested: Final = object_mapping(direct.get("response"))
    return {
        **direct,
        **(
            {
                "item": await _response_item(
                    direct["item"], context, store, direct.get("type") == "response.output_item.done"
                )
            }
            if "item" in direct
            else {}
        ),
        **(
            {"output": [await _response_item(item, context, store, True) for item in items(direct["output"])]}
            if "output" in direct
            else {}
        ),
        **({"response": await transform_response(nested, context, store)} if nested else {}),
    }
