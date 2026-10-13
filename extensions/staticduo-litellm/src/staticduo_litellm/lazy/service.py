from __future__ import annotations

import json
from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from mcp.types import CallToolResult, TextContent
from pydantic import TypeAdapter

if TYPE_CHECKING:
    from .ports import MCPPorts

from .schema import (
    LAZYMCP_AUTH_REQUIRED_ERROR,
    LAZYMCP_UNAVAILABLE_SERVER_ERROR,
    LAZYMCP_UNAVAILABLE_TOOL_ERROR,
    server_description,
    server_label,
    tool_summary,
)


class ServiceService:
    ports: MCPPorts

    async def describe(
        self,
        arguments: dict[str, object],  # mutable-ok: framework contract requires mutable request or response containers
    ) -> Mapping[str, object]:
        (
            user_api_key_auth,
            mcp_auth_header,
            mcp_servers,
            mcp_server_auth_headers,
            oauth2_headers,
            raw_headers,
            client_ip,
        ) = self.ports.get_auth_context()
        server_name = arguments.get(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            "server"
        )
        tool_name = arguments.get("tool")  # rebind-ok: framework flow intentionally updates request or lifecycle state
        if server_name:
            allowed_servers = await self.ports.lazy_allowed_servers(  # rebind-ok: framework flow intentionally updates request or lifecycle state
                user_api_key_auth=user_api_key_auth,
                mcp_servers=mcp_servers,
                client_ip=client_ip,
            )
            selected_server = next(  # rebind-ok: framework flow intentionally updates request or lifecycle state
                (server for server in allowed_servers if server_label(server).lower() == str(server_name).lower()),
                None,
            )
            if selected_server is None:
                return LAZYMCP_UNAVAILABLE_SERVER_ERROR
            tools, auth_status = await self.ports.bounded_server_tools(
                server=selected_server,
                user_api_key_auth=user_api_key_auth,
                mcp_auth_header=mcp_auth_header,
                mcp_server_auth_headers=mcp_server_auth_headers,
                oauth2_headers=oauth2_headers,
                raw_headers=raw_headers,
                scope_servers=[selected_server],
            )
            if auth_status == "auth_required":
                return {
                    "server": server_label(selected_server),
                    "description": server_description(selected_server),
                    "tools": [],
                    "auth_status": auth_status,
                }
            if tool_name:
                selected_tool, resolution_error = self.ports.resolve_tool(tools, selected_server, str(tool_name))
                if selected_tool is None:
                    return resolution_error or LAZYMCP_UNAVAILABLE_TOOL_ERROR
                return {
                    "server": server_label(selected_server),
                    "tool": tool_summary(selected_tool, include_schema=True),
                }
            response: Final[  # mutable-ok: SDK JSON response is assembled before returning
                dict[str, object]
            ] = {
                "server": server_label(selected_server),
                "description": server_description(selected_server),
                "tools": [tool_summary(tool, include_schema=True) for tool in tools],
            }
            if auth_status not in ("not_required", "connected"):
                response["auth_status"] = auth_status
            return response

        catalog = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            await self.ports.catalog(
                user_api_key_auth=user_api_key_auth,
                mcp_auth_header=mcp_auth_header,
                mcp_servers=mcp_servers,
                mcp_server_auth_headers=mcp_server_auth_headers,
                oauth2_headers=oauth2_headers,
                raw_headers=raw_headers,
                client_ip=client_ip,
            )
        )
        return {
            "servers": [
                {
                    "name": item["name"],
                    "description": item["description"],
                    "tool_count": item["tool_count"],
                }
                for item in catalog.get(
                    "servers",
                    [],
                )
            ]
        }

    async def status(
        self,
    ) -> dict[  # mutable-ok: framework contract requires mutable request or response containers
        str, object
    ]:
        (
            user_api_key_auth,
            mcp_auth_header,
            mcp_servers,
            mcp_server_auth_headers,
            oauth2_headers,
            raw_headers,
            client_ip,
        ) = self.ports.get_auth_context()
        catalog = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            await self.ports.catalog(
                user_api_key_auth=user_api_key_auth,
                mcp_auth_header=mcp_auth_header,
                mcp_servers=mcp_servers,
                mcp_server_auth_headers=mcp_server_auth_headers,
                oauth2_headers=oauth2_headers,
                raw_headers=raw_headers,
                client_ip=client_ip,
            )
        )
        return {
            "enabled": True,
            "mode": "lazymcp",
            "visible_server_count": catalog.get("server_count", 0),
            "visible_tool_count": catalog.get("tool_count", 0),
            "route_restricted": bool(mcp_servers),
            "requested_server_count": len(mcp_servers or []),
            "toolset_scoped": self.ports.active_toolset.get() is not None,
            "servers": [
                {
                    "name": item["name"],
                    "tool_count": item["tool_count"],
                    "auth_status": item.get("auth_status", "not_required"),
                }
                for item in catalog.get(
                    "servers",
                    [],
                )
            ],
        }

    async def call(
        self,
        arguments: dict[str, object],  # mutable-ok: framework contract requires mutable request or response containers
    ) -> CallToolResult:
        server_name = arguments.get(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            "server"
        )
        tool_name = arguments.get("tool")  # rebind-ok: framework flow intentionally updates request or lifecycle state
        tool_arguments = arguments.get(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            "arguments"
        )
        if not isinstance(server_name, str) or not isinstance(tool_name, str) or not isinstance(tool_arguments, dict):
            return CallToolResult(
                content=[
                    TextContent(
                        text=json.dumps(
                            {
                                "error": "Invalid LazyMCP arguments.",
                                "details": "mcp_call requires server, tool, and arguments.",
                            }
                        ),
                        type="text",
                    )
                ],
                is_error=True,
            )

        (
            user_api_key_auth,
            mcp_auth_header,
            mcp_servers,
            mcp_server_auth_headers,
            oauth2_headers,
            raw_headers,
            client_ip,
        ) = self.ports.get_auth_context()
        allowed_servers = await self.ports.lazy_allowed_servers(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            user_api_key_auth=user_api_key_auth,
            mcp_servers=mcp_servers,
            client_ip=client_ip,
        )
        selected_server = next(  # rebind-ok: framework flow intentionally updates request or lifecycle state
            (server for server in allowed_servers if server_label(server).lower() == server_name.lower()),
            None,
        )
        if selected_server is None:
            return CallToolResult(
                content=[TextContent(text=json.dumps(LAZYMCP_UNAVAILABLE_SERVER_ERROR), type="text")],
                is_error=True,
            )
        if selected_server.needs_user_oauth_token and not await self.ports.has_user_oauth_token(
            selected_server, user_api_key_auth
        ):
            return CallToolResult(
                content=[TextContent(text=json.dumps(LAZYMCP_AUTH_REQUIRED_ERROR), type="text")],
                is_error=True,
            )
        visible_tools: Final = await self.ports.server_tools(
            selected_server,
            user_api_key_auth,
            mcp_auth_header,
            mcp_server_auth_headers,
            oauth2_headers,
            raw_headers,
        )
        selected_tool, resolution_error = self.ports.resolve_tool(visible_tools, selected_server, tool_name)
        if selected_tool is None:
            return CallToolResult(
                content=[
                    TextContent(
                        text=json.dumps(resolution_error or LAZYMCP_UNAVAILABLE_TOOL_ERROR),
                        type="text",
                    )
                ],
                is_error=True,
            )
        return await self.ports.call_mcp_tool(
            name=selected_tool.name,
            arguments=TypeAdapter(dict[str, object]).validate_python(tool_arguments),
            user_api_key_auth=user_api_key_auth,
            mcp_auth_header=mcp_auth_header,
            mcp_servers=[server_label(selected_server)],
            mcp_server_auth_headers=mcp_server_auth_headers,
            oauth2_headers=oauth2_headers,
            raw_headers=raw_headers,
            client_ip=client_ip,
            metadata={
                "source": "lazymcp",
                "lazy_mcp": True,
                "lazy_mcp_gateway_tool": "mcp_call",
                "lazy_mcp_server": server_name,
                "lazy_mcp_tool": tool_name,
                "delegated_tool_name": tool_name,
                "server_name": server_name,
            },
        )
