from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Final

from mcp.types import Tool as MCPTool

if TYPE_CHECKING:
    from staticduo_litellm.compatibility.mcp_types import MCPServer

    from .ports import MCPPorts

from .schema import (
    LAZYMCP_AMBIGUOUS_TOOL_ERROR,
    LAZYMCP_UNAVAILABLE_TOOL_ERROR,
)


class ResolverService:
    ports: MCPPorts

    def resolve_tool(
        self, tools: Sequence[MCPTool], server: MCPServer, requested_name: str
    ) -> tuple[MCPTool | None, Mapping[str, str] | None]:
        exact_match: Final = next((tool for tool in tools if tool.name == requested_name), None)
        if exact_match is not None:
            return exact_match, None
        local_matches: Final = tuple(
            tool for tool in tools if self.ports.strip_known_server_prefix(tool.name, server) == requested_name
        )
        if len(local_matches) == 1:
            return local_matches[0], None
        if len(local_matches) > 1:
            return None, LAZYMCP_AMBIGUOUS_TOOL_ERROR
        return None, LAZYMCP_UNAVAILABLE_TOOL_ERROR
