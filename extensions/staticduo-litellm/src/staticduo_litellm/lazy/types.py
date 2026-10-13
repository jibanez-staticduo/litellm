from __future__ import annotations

from collections.abc import Mapping, Sequence

from typing_extensions import ReadOnly, TypedDict


class CatalogEntry(TypedDict):
    server_id: ReadOnly[str]
    name: ReadOnly[str]
    description: ReadOnly[str]
    tool_count: ReadOnly[int]
    tools: ReadOnly[Sequence[Mapping[str, object]]]
    auth_status: ReadOnly[str]


class LazyCatalog(TypedDict):
    servers: ReadOnly[Sequence[CatalogEntry]]
    description: ReadOnly[str]
    server_count: ReadOnly[int]
    tool_count: ReadOnly[int]
