from __future__ import annotations

import asyncio
import contextvars
from collections.abc import Mapping, Sequence
from typing import Protocol, TypeAlias

from mcp.types import CallToolResult
from mcp.types import Tool as MCPTool

from litellm.proxy._experimental.mcp_server.db import OAuthCredentialPayload
from litellm.proxy._experimental.mcp_server.mcp_server_manager import MCPServerManager
from litellm.proxy.common_utils.proxy_rate_limit_error import ProxyRateLimitError
from staticduo_litellm.lazy.ports import AuthContext
from staticduo_litellm.lazy.types import CatalogEntry, LazyCatalog

from .mcp_types import MCPServer, UserAPIKeyAuth

HeaderMap: TypeAlias = dict[str, str]
ServerHeaders: TypeAlias = dict[str, HeaderMap]
ServerList: TypeAlias = list[MCPServer]
ToolList: TypeAlias = list[MCPTool]
Arguments: TypeAlias = dict[str, object]


class MCPOperationBindings(Protocol):
    async def _mcp_server_rate_limit_rejection(
        self, server: MCPServer, user_api_key_auth: UserAPIKeyAuth | None
    ) -> ProxyRateLimitError | None: ...


class CoreMCPBindings(Protocol):
    global_mcp_server_manager: MCPServerManager
    operations: MCPOperationBindings
    _mcp_active_toolset_id: contextvars.ContextVar[str | None]
    MCP_TOOL_LISTING_TIMEOUT: float

    def _prepare_mcp_server_headers(
        self,
        server: MCPServer,
        mcp_server_auth_headers: ServerHeaders | None,
        mcp_auth_header: str | None,
        oauth2_headers: HeaderMap | None,
        raw_headers: HeaderMap | None,
        user_api_key_auth: UserAPIKeyAuth | None = None,
        scope_servers: ServerList | None = None,
    ) -> tuple[HeaderMap | str | None, HeaderMap | None]: ...

    async def _get_user_oauth_extra_headers_from_db(
        self,
        server: MCPServer,
        user_api_key_auth: UserAPIKeyAuth | None,
        prefetched_creds: Mapping[str, OAuthCredentialPayload] | None = None,
    ) -> HeaderMap | None: ...

    def filter_tools_by_allowed_tools(self, tools: ToolList, mcp_server: MCPServer) -> ToolList: ...

    async def filter_tools_by_key_team_permissions(
        self, tools: ToolList, server_id: str, user_api_key_auth: UserAPIKeyAuth | None
    ) -> ToolList: ...

    def apply_tool_overrides(self, tools: ToolList, mcp_server: MCPServer) -> ToolList: ...

    def get_auth_context(self) -> AuthContext: ...

    def _lazymcp_cache_scope(
        self,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_servers: Sequence[str] | None,
        mcp_server_auth_headers: ServerHeaders | None,
        oauth2_headers: HeaderMap | None,
        raw_headers: HeaderMap | None,
        client_ip: str | None,
    ) -> str: ...

    async def _lazymcp_cache_get(self, key: str) -> object | None: ...

    async def _lazymcp_cache_set(self, key: str, value: object) -> None: ...

    def invalidate_lazymcp_cache(self) -> None: ...

    async def _merge_toolset_permissions(self, user_api_key_auth: UserAPIKeyAuth | None) -> UserAPIKeyAuth | None: ...

    async def _get_lazymcp_allowed_servers(
        self, user_api_key_auth: UserAPIKeyAuth | None, mcp_servers: Sequence[str] | None, client_ip: str | None
    ) -> ServerList: ...

    async def _get_lazymcp_server_tools(
        self,
        server: MCPServer,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_server_auth_headers: ServerHeaders | None,
        oauth2_headers: HeaderMap | None,
        raw_headers: HeaderMap | None,
        scope_servers: ServerList | None = None,
    ) -> ToolList: ...

    def _consume_lazymcp_listing_task(self, task: asyncio.Task[object]) -> None: ...

    async def _get_bounded_lazymcp_server_tools(
        self,
        server: MCPServer,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_server_auth_headers: ServerHeaders | None,
        oauth2_headers: HeaderMap | None,
        raw_headers: HeaderMap | None,
        scope_servers: ServerList,
    ) -> tuple[ToolList, str]: ...

    async def _get_bounded_lazymcp_catalog_server_entry(
        self,
        server: MCPServer,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_server_auth_headers: ServerHeaders | None,
        oauth2_headers: HeaderMap | None,
        raw_headers: HeaderMap | None,
        scope_servers: ServerList,
    ) -> CatalogEntry: ...

    async def _get_lazymcp_catalog(
        self,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_servers: Sequence[str] | None,
        mcp_server_auth_headers: ServerHeaders | None,
        oauth2_headers: HeaderMap | None,
        raw_headers: HeaderMap | None,
        client_ip: str | None,
    ) -> LazyCatalog: ...

    def _resolve_lazymcp_tool(
        self, tools: Sequence[MCPTool], server: MCPServer, requested_name: str
    ) -> tuple[MCPTool | None, Mapping[str, str] | None]: ...

    async def _lazymcp_describe(self, arguments: Arguments) -> Mapping[str, object]: ...

    async def _lazymcp_status(self) -> Arguments: ...

    async def _lazymcp_call(self, arguments: Arguments) -> CallToolResult: ...

    async def _get_allowed_mcp_servers(
        self, user_api_key_auth: UserAPIKeyAuth | None, mcp_servers: Sequence[str] | None, client_ip: str | None = None
    ) -> ServerList: ...

    def strip_known_server_prefix(self, name: str, server: MCPServer | None) -> str: ...

    async def call_mcp_tool(
        self,
        name: str,
        arguments: Arguments,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_auth_header: str | None,
        mcp_servers: Sequence[str],
        mcp_server_auth_headers: ServerHeaders | None,
        oauth2_headers: HeaderMap | None,
        raw_headers: HeaderMap | None,
        client_ip: str | None,
        *,
        metadata: Mapping[str, object],
    ) -> CallToolResult: ...
