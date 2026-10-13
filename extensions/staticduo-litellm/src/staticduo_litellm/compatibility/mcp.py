from __future__ import annotations

import contextvars
from collections.abc import Awaitable, Callable, Mapping, Sequence
from types import MappingProxyType, ModuleType
from typing import Final, Protocol, TypeAlias, cast  # noqa: TID251  # typed core ABI adapter boundary

from mcp.types import CallToolResult
from mcp.types import Tool as MCPTool

from litellm._internal_context import with_service_target
from litellm._logging import verbose_logger
from litellm.proxy._experimental.mcp_server.utils import MCP_SERVERS_TARGET
from litellm.types.mcp import MCPAuth
from staticduo_litellm.lazy.ports import AuthContext, CatalogIdentity
from staticduo_litellm.lazy.schema import (
    LAZYMCP_CACHE_TTL_SECONDS,
    LAZYMCP_PERMISSION_MAP_ADAPTER,
    LAZYMCP_SERVER_LIST_ADAPTER,
)
from staticduo_litellm.lazy.types import CatalogEntry, LazyCatalog

from .mcp_bindings import CoreMCPBindings, ServerList, ToolList
from .mcp_types import MCPServer, UserAPIKeyAuth

CacheEntries: TypeAlias = dict[str, object]


class MemoryCache(Protocol):
    @property
    def cache_dict(self) -> CacheEntries: ...


class CacheAccess(Protocol):
    @property
    def in_memory_cache(self) -> MemoryCache | None: ...

    async def async_get_cache(self, *, key: str) -> object: ...


class CoreMCPAdapter:
    def __init__(self, core: ModuleType) -> None:
        self.core: Final = cast(CoreMCPBindings, core)  # cast-ok: canonical core ABI adapter

    @with_service_target(MCP_SERVERS_TARGET)
    async def cache_get(self, key: str) -> object | None:
        try:
            from litellm.proxy.proxy_server import user_api_key_cache

            cache: Final = cast(CacheAccess, user_api_key_cache)  # cast-ok: canonical cache ABI
            value: Final = await cache.async_get_cache(key=key)
        except Exception as e:  # noqa: BLE001  # boundary failure is converted to a safe MCP outcome
            verbose_logger.debug("LazyMCP cache get failed for %s: %s", key, e)
            return None
        else:
            return value

    @with_service_target(MCP_SERVERS_TARGET)
    async def cache_set(self, key: str, value: object) -> None:
        try:
            from litellm.proxy.proxy_server import user_api_key_cache

            await user_api_key_cache.async_set_cache(
                key=key,
                value=value,
                ttl=LAZYMCP_CACHE_TTL_SECONDS,
            )
        except Exception as e:  # noqa: BLE001  # boundary failure is converted to a safe MCP outcome
            verbose_logger.debug("LazyMCP cache set failed for %s: %s", key, e)

    @staticmethod
    def invalidate_lazymcp_cache() -> None:
        """Evict LazyMCP entries from the in-memory DualCache layer only."""
        try:
            from litellm.proxy.proxy_server import user_api_key_cache

            cache: Final = cast(CacheAccess, user_api_key_cache)  # cast-ok: canonical cache ABI
            in_memory: Final = cache.in_memory_cache
            if in_memory is None:
                return
            cache_dict: Final = in_memory.cache_dict
            for key in tuple(cache_dict):
                if key.startswith("lazymcp:"):
                    cache_dict.pop(key, None)
        except Exception as e:  # noqa: BLE001  # boundary failure is converted to a safe MCP outcome
            verbose_logger.warning("invalidate_lazymcp_cache failed: %s", e)

    async def merge_toolset_permissions(
        self,
        user_api_key_auth: UserAPIKeyAuth | None,
    ) -> UserAPIKeyAuth | None:
        if user_api_key_auth is None or user_api_key_auth.object_permission is None:
            return user_api_key_auth
        object_permission: Final = user_api_key_auth.object_permission
        toolset_ids: Final = tuple(object_permission.mcp_toolsets or ())
        if not toolset_ids:
            return user_api_key_auth
        toolset_permissions: Final = await self.core.global_mcp_server_manager.resolve_toolset_tool_permissions(
            toolset_ids=list(toolset_ids), requires_fresh_policy=user_api_key_auth.requires_fresh_policy
        )
        if not toolset_permissions:
            return user_api_key_auth
        existing_permissions: Final[Mapping[str, Sequence[str]]] = (
            object_permission.mcp_tool_permissions or MappingProxyType({})
        )
        merged_permissions: Final = LAZYMCP_PERMISSION_MAP_ADAPTER.validate_python(
            MappingProxyType(
                {
                    **existing_permissions,
                    **MappingProxyType(
                        {
                            server_id: tuple(frozenset(existing_permissions.get(server_id, ())) | frozenset(tool_names))
                            for server_id, tool_names in toolset_permissions.items()
                        }
                    ),
                }
            )
        )
        merged_servers: Final = LAZYMCP_SERVER_LIST_ADAPTER.validate_python(
            frozenset(object_permission.mcp_servers or ()) | frozenset(merged_permissions)
        )
        updated_permission: Final = object_permission.model_copy(
            update=MappingProxyType({"mcp_servers": merged_servers, "mcp_tool_permissions": merged_permissions})
        )
        return user_api_key_auth.model_copy(update=MappingProxyType({"object_permission": updated_permission}))

    async def allowed_servers(
        self,
        user_api_key_auth: UserAPIKeyAuth | None,
        mcp_servers: list[str] | None,  # mutable-ok: framework contract requires mutable request or response containers
        client_ip: str | None,
    ) -> list[MCPServer]:  # mutable-ok: framework contract requires mutable request or response containers
        user_api_key_auth = await self.core._merge_toolset_permissions(  # rebind-ok: framework flow intentionally updates request or lifecycle state  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations
            user_api_key_auth
        )
        return await self.core._get_allowed_mcp_servers(  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations
            user_api_key_auth=user_api_key_auth,
            mcp_servers=mcp_servers,
            client_ip=client_ip,
        )

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
        rate_limit_error: Final = await self.core.operations._mcp_server_rate_limit_rejection(server, user_api_key_auth)  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations
        if rate_limit_error is not None:
            raise rate_limit_error
        server_auth_header, extra_headers = self.core._prepare_mcp_server_headers(  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations
            server=server,
            mcp_server_auth_headers=mcp_server_auth_headers,
            mcp_auth_header=mcp_auth_header,
            oauth2_headers=oauth2_headers,
            raw_headers=raw_headers,
            user_api_key_auth=user_api_key_auth,
            scope_servers=scope_servers,
        )
        if extra_headers is None and server.auth_type == MCPAuth.oauth2:
            extra_headers = await self.core._get_user_oauth_extra_headers_from_db(  # rebind-ok: framework flow intentionally updates request or lifecycle state  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations
                server=server,
                user_api_key_auth=user_api_key_auth,
            )
        from litellm.proxy.proxy_server import proxy_logging_obj

        tools = await self.core.global_mcp_server_manager._get_tools_from_server(  # pyright: ignore[reportPrivateUsage]  # server transport owns this internal manager operation operation  # rebind-ok: framework flow intentionally updates request or lifecycle state
            server=server,
            mcp_auth_header=server_auth_header,
            extra_headers=extra_headers,
            add_prefix=True,
            raw_headers=raw_headers,
            client_ip=self.core.get_auth_context()[-1],
            proxy_logging_obj=proxy_logging_obj,
            user_api_key_auth=user_api_key_auth,
            oauth2_headers=oauth2_headers,
        )
        tools = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            self.core.filter_tools_by_allowed_tools(tools, server)
        )
        tools = await self.core.filter_tools_by_key_team_permissions(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            tools=tools,
            server_id=server.server_id,
            user_api_key_auth=user_api_key_auth,
        )
        return self.core.apply_tool_overrides(tools, server)


class LegacyMCPPorts:
    def __init__(self, core: ModuleType) -> None:
        self.core: Final = cast(CoreMCPBindings, core)  # cast-ok: canonical core ABI adapter

    @property
    def active_toolset(self) -> contextvars.ContextVar[str | None]:
        return self.core._mcp_active_toolset_id  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def listing_timeout(self) -> float:
        return self.core.MCP_TOOL_LISTING_TIMEOUT

    async def has_user_oauth_token(self, server: MCPServer, auth: UserAPIKeyAuth | None) -> bool:
        return await self.core.global_mcp_server_manager.has_user_oauth_token(server, auth)

    def current_snapshot(self) -> CatalogIdentity | None:
        return self.core.global_mcp_server_manager.catalog.current()

    @property
    def consume_listing_task(self) -> Callable[..., None]:
        return self.core._consume_lazymcp_listing_task  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def allowed_servers(self) -> Callable[..., Awaitable[ServerList]]:
        return self.core._get_allowed_mcp_servers  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def catalog_entry(self) -> Callable[..., Awaitable[CatalogEntry]]:
        return self.core._get_bounded_lazymcp_catalog_server_entry  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def bounded_server_tools(self) -> Callable[..., Awaitable[tuple[ToolList, str]]]:
        return self.core._get_bounded_lazymcp_server_tools  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def lazy_allowed_servers(self) -> Callable[..., Awaitable[ServerList]]:
        return self.core._get_lazymcp_allowed_servers  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def catalog(self) -> Callable[..., Awaitable[LazyCatalog]]:
        return self.core._get_lazymcp_catalog  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def server_tools(self) -> Callable[..., Awaitable[ToolList]]:
        return self.core._get_lazymcp_server_tools  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def cache_get(self) -> Callable[..., Awaitable[object | None]]:
        return self.core._lazymcp_cache_get  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def cache_scope(self) -> Callable[..., str]:
        return self.core._lazymcp_cache_scope  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def cache_set(self) -> Callable[..., Awaitable[None]]:
        return self.core._lazymcp_cache_set  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def _lazymcp_call(self) -> Callable[..., Awaitable[CallToolResult]]:
        return self.core._lazymcp_call  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def _lazymcp_describe(self) -> Callable[..., Awaitable[Mapping[str, object]]]:
        return self.core._lazymcp_describe  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def _lazymcp_status(self) -> Callable[..., Awaitable[Mapping[str, object]]]:
        return self.core._lazymcp_status  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def merge_toolset_permissions(self) -> Callable[..., Awaitable[UserAPIKeyAuth | None]]:
        return self.core._merge_toolset_permissions  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def resolve_tool(self) -> Callable[..., tuple[MCPTool | None, Mapping[str, str] | None]]:
        return self.core._resolve_lazymcp_tool  # pyright: ignore[reportPrivateUsage]  # versioned adapter delegates canonical core operations

    @property
    def call_mcp_tool(self) -> Callable[..., Awaitable[CallToolResult]]:
        return self.core.call_mcp_tool

    @property
    def get_auth_context(self) -> Callable[[], AuthContext]:
        return self.core.get_auth_context

    @property
    def invalidate_lazymcp_cache(self) -> Callable[[], None]:
        return self.core.invalidate_lazymcp_cache

    @property
    def strip_known_server_prefix(self) -> Callable[..., str]:
        return self.core.strip_known_server_prefix


invalidate_lazymcp_cache: Final = CoreMCPAdapter.invalidate_lazymcp_cache
