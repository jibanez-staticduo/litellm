from __future__ import annotations

import asyncio
import contextvars
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Protocol, TypeAlias

from mcp.types import CallToolResult
from mcp.types import Tool as MCPTool

from .types import CatalogEntry, LazyCatalog

if TYPE_CHECKING:
    from staticduo_litellm.compatibility.mcp_types import MCPServer, UserAPIKeyAuth


AuthContext: TypeAlias = tuple[
    "UserAPIKeyAuth | None",
    str | None,
    list[str] | None,
    dict[str, dict[str, str]] | None,
    dict[str, str] | None,
    dict[str, str] | None,
    str | None,
]


class CatalogIdentity(Protocol):
    @property
    def identity(self) -> str: ...


class MCPPorts(Protocol):
    @property
    def listing_timeout(self) -> float: ...

    @property
    def active_toolset(self) -> contextvars.ContextVar[str | None]: ...

    def get_auth_context(self) -> AuthContext: ...
    def current_snapshot(self) -> CatalogIdentity | None: ...
    async def has_user_oauth_token(self, server: MCPServer, auth: UserAPIKeyAuth | None) -> bool: ...

    def cache_scope(
        self,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_servers: list[str] | None,  # mutable-ok: framework contract requires mutable request or response containers
        mcp_server_auth_headers: dict[  # mutable-ok: framework contract requires mutable request or response containers
            str, dict[str, str]
        ]
        | None,
        oauth2_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        raw_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        client_ip: str | None,
    ) -> str: ...

    async def cache_get(self, key: str) -> object | None: ...

    async def cache_set(self, key: str, value: object) -> None: ...

    def invalidate_lazymcp_cache(
        self,
    ) -> None: ...

    async def merge_toolset_permissions(
        self,
        user_api_key_auth: UserAPIKeyAuth | None,
    ) -> UserAPIKeyAuth | None: ...

    async def lazy_allowed_servers(
        self,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_servers: list[str] | None,  # mutable-ok: framework contract requires mutable request or response containers
        client_ip: str | None,
    ) -> list[MCPServer]:  # mutable-ok: framework contract requires mutable request or response containers
        ...

    async def server_tools(
        self,
        server: MCPServer,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_server_auth_headers: dict[  # mutable-ok: framework contract requires mutable request or response containers
            str, dict[str, str]
        ]
        | None,
        oauth2_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        raw_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        scope_servers: list[MCPServer]  # mutable-ok: framework contract requires mutable request or response containers
        | None = None,
    ) -> list[MCPTool]:  # mutable-ok: framework contract requires mutable request or response containers
        ...

    def consume_listing_task(self, task: asyncio.Task[object]) -> None: ...

    async def bounded_server_tools(
        self,
        server: MCPServer,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_server_auth_headers: dict[  # mutable-ok: framework contract requires mutable request or response containers
            str, dict[str, str]
        ]
        | None,
        oauth2_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        raw_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        scope_servers: list[  # mutable-ok: framework contract requires mutable request or response containers
            MCPServer
        ],
    ) -> tuple[list[MCPTool], str]:  # mutable-ok: framework contract requires mutable request or response containers
        ...

    async def catalog_entry(
        self,
        server: MCPServer,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_server_auth_headers: dict[  # mutable-ok: framework contract requires mutable request or response containers
            str, dict[str, str]
        ]
        | None,
        oauth2_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        raw_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        scope_servers: list[  # mutable-ok: framework contract requires mutable request or response containers
            MCPServer
        ],
    ) -> CatalogEntry: ...

    async def catalog(
        self,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_servers: list[str] | None,  # mutable-ok: framework contract requires mutable request or response containers
        mcp_server_auth_headers: dict[  # mutable-ok: framework contract requires mutable request or response containers
            str, dict[str, str]
        ]
        | None,
        oauth2_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        raw_headers: dict[str, str]  # mutable-ok: framework contract requires mutable request or response containers
        | None,
        client_ip: str | None,
    ) -> LazyCatalog: ...

    def resolve_tool(
        self, tools: Sequence[MCPTool], server: MCPServer, requested_name: str
    ) -> tuple[MCPTool | None, Mapping[str, str] | None]: ...

    async def describe(
        self,
        arguments: dict[str, object],  # mutable-ok: framework contract requires mutable request or response containers
    ) -> Mapping[str, object]: ...

    async def status(
        self,
    ) -> dict[  # mutable-ok: framework contract requires mutable request or response containers
        str, object
    ]: ...

    async def call(
        self,
        arguments: dict[str, object],  # mutable-ok: framework contract requires mutable request or response containers
    ) -> CallToolResult: ...

    async def allowed_servers(
        self,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_servers: Sequence[str] | None,
        client_ip: str | None = None,
    ) -> list[MCPServer]:  # mutable-ok: upstream registry API returns MCP server lists
        ...

    def strip_known_server_prefix(self, name: str, server: MCPServer | None) -> str: ...

    async def call_mcp_tool(
        self,
        name: str,
        arguments: dict[str, object],  # mutable-ok: upstream dispatch accepts the validated JSON payload
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_servers: list[str],  # mutable-ok: upstream dispatch accepts the selected server list
        mcp_server_auth_headers: dict[str, dict[str, str]] | None,  # mutable-ok: upstream request-local credential map
        oauth2_headers: dict[str, str] | None,  # mutable-ok: upstream request-local OAuth map
        raw_headers: dict[str, str] | None,  # mutable-ok: upstream request-local header map
        client_ip: str | None,
        *,
        metadata: Mapping[str, object],
    ) -> CallToolResult: ...
