from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import TYPE_CHECKING, Final

from mcp.types import Tool as MCPTool
from pydantic import TypeAdapter

from .types import CatalogEntry, LazyCatalog

if TYPE_CHECKING:
    from staticduo_litellm.compatibility.mcp_types import MCPServer, UserAPIKeyAuth

    from .ports import MCPPorts


from .schema import (
    hash_value,
    server_description,
    server_label,
    tool_summary,
)

verbose_logger: Final = logging.getLogger("LiteLLM")


class CatalogService:
    ports: MCPPorts

    def consume_listing_task(self, task: asyncio.Task[object]) -> None:
        with contextlib.suppress(BaseException):
            task.result()

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
        async def _list_tools() -> (
            tuple[  # mutable-ok: framework contract requires mutable request or response containers
                list[MCPTool], str
            ]
        ):
            auth_status = "not_required"  # rebind-ok: framework flow intentionally updates request or lifecycle state
            if server.needs_user_oauth_token:
                auth_status = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
                    "connected" if await self.ports.has_user_oauth_token(server, user_api_key_auth) else "auth_required"
                )
            if auth_status == "auth_required":
                return [], auth_status
            tools = await self.ports.server_tools(  # rebind-ok: framework flow intentionally updates request or lifecycle state
                server=server,
                user_api_key_auth=user_api_key_auth,
                mcp_auth_header=mcp_auth_header,
                mcp_server_auth_headers=mcp_server_auth_headers,
                oauth2_headers=oauth2_headers,
                raw_headers=raw_headers,
                scope_servers=scope_servers,
            )
            return tools, auth_status

        listing_task = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            asyncio.create_task(_list_tools())
        )
        try:
            done, _ = await asyncio.wait(
                (listing_task,),
                timeout=self.ports.listing_timeout,
            )
        except asyncio.CancelledError:
            listing_task.cancel()
            listing_task.add_done_callback(self.ports.consume_listing_task)
            raise
        if not done:
            listing_task.cancel()
            listing_task.add_done_callback(self.ports.consume_listing_task)
            verbose_logger.warning(
                "LazyMCP timed out listing tools for server %s",
                server_label(server),
            )
            return (
                [],
                "authentication_failed" if server.needs_user_oauth_token else "listing_failed",
            )
        try:
            return listing_task.result()
        except Exception as e:  # noqa: BLE001  # boundary failure is converted to a safe MCP outcome
            verbose_logger.exception(
                "LazyMCP failed to list tools for server %s: %s",
                server_label(server),
                e,
            )
            return (
                [],
                "authentication_failed" if server.needs_user_oauth_token else "listing_failed",
            )

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
    ) -> CatalogEntry:
        tools, auth_status = await self.ports.bounded_server_tools(
            server=server,
            user_api_key_auth=user_api_key_auth,
            mcp_auth_header=mcp_auth_header,
            mcp_server_auth_headers=mcp_server_auth_headers,
            oauth2_headers=oauth2_headers,
            raw_headers=raw_headers,
            scope_servers=scope_servers,
        )
        return {
            "server_id": server.server_id,
            "name": server_label(server),
            "description": server_description(server),
            "tool_count": len(tools),
            "tools": [tool_summary(tool) for tool in tools],
            "auth_status": auth_status,
        }

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
    ) -> LazyCatalog:
        effective_auth: Final = await self.ports.merge_toolset_permissions(user_api_key_auth)
        snapshot: Final = self.ports.current_snapshot()
        scope_hash: Final = self.ports.cache_scope(
            user_api_key_auth=effective_auth,
            mcp_auth_header=mcp_auth_header,
            mcp_servers=mcp_servers,
            mcp_server_auth_headers=mcp_server_auth_headers,
            oauth2_headers=oauth2_headers,
            raw_headers=raw_headers,
            client_ip=client_ip,
        )
        allowed_servers = await self.ports.allowed_servers(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            user_api_key_auth=effective_auth,
            mcp_servers=mcp_servers,
            client_ip=client_ip,
        )
        allowed_scope: Final = hash_value(tuple(sorted(server.server_id for server in allowed_servers)))
        cache_key = f"lazymcp:catalog:{snapshot.identity if snapshot is not None else 'uncaptured'}:{scope_hash}:{allowed_scope}"  # rebind-ok: framework flow intentionally updates request or lifecycle state
        has_user_oauth_server: Final = any(server.needs_user_oauth_token for server in allowed_servers)
        if not has_user_oauth_server:
            cached = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
                await self.ports.cache_get(cache_key)
            )
            if isinstance(cached, dict):
                return TypeAdapter(LazyCatalog).validate_python(cached)

        servers: Final = list(
            await asyncio.gather(
                *(
                    self.ports.catalog_entry(
                        server=server_item,
                        user_api_key_auth=user_api_key_auth,
                        mcp_auth_header=mcp_auth_header,
                        mcp_server_auth_headers=mcp_server_auth_headers,
                        oauth2_headers=oauth2_headers,
                        raw_headers=raw_headers,
                        scope_servers=allowed_servers,
                    )
                    for server_item in allowed_servers
                )
            )
        )

        description_lines: Final = [
            "Describe MCP servers and tools available through the LiteLLM LazyMCP gateway.",
            "",
            "Available MCP servers:",
        ]
        if servers:
            description_lines.extend(f"- {item['name']}: {item['description']}" for item in servers)
        else:
            description_lines.append("- No MCP servers are available for this request.")
        description_lines.extend(
            [
                "",
                'Call mcp_describe with {"server":"<name>"} to list tools for one server with input schemas.',
                'Call mcp_describe with {"server":"<name>","tool":"<tool_name>"} to get details for one tool with its input schema.',
                'Call mcp_call with {"server":"<name>","tool":"<tool_name>","arguments":{...}} to execute a tool.',
            ]
        )
        catalog: Final[LazyCatalog] = {
            "servers": servers,
            "description": "\n".join(description_lines),
            "server_count": len(servers),
            "tool_count": sum(item["tool_count"] for item in servers),
        }
        if not has_user_oauth_server:
            await self.ports.cache_set(cache_key, catalog)
        return catalog
