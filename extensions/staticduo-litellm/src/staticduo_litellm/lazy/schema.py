from __future__ import annotations

import hashlib
import json
import re
from typing import TYPE_CHECKING, Final

from mcp.types import CallToolResult, TextContent
from mcp.types import Tool as MCPTool
from pydantic import TypeAdapter

if TYPE_CHECKING:
    from staticduo_litellm.compatibility.mcp_types import MCPServer

LAZYMCP_TOOL_NAMES = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
    "mcp_describe",
    "mcp_call",
    "mcp_status",
)
LAZYMCP_CACHE_TTL_SECONDS = 300  # rebind-ok: framework flow intentionally updates request or lifecycle state
LAZYMCP_UNAVAILABLE_SERVER_ERROR: Final = {"error": "MCP server is not available for this request."}
LAZYMCP_AUTH_REQUIRED_ERROR: Final = {"error": "MCP server authentication is required for this user."}
LAZYMCP_UNAVAILABLE_TOOL_ERROR: Final = {"error": "Tool is not available for this request."}
LAZYMCP_AMBIGUOUS_TOOL_ERROR: Final[dict[str, str]] = {  # mutable-ok: MCP errors are JSON object payloads
    "error": "Tool name is ambiguous within the selected MCP server."
}
LAZYMCP_PERMISSION_MAP_ADAPTER: Final = TypeAdapter(dict[str, list[str]])
LAZYMCP_SERVER_LIST_ADAPTER: Final = TypeAdapter(list[str])


def hash_value(value: object) -> str | None:
    if value is None:
        return None
    encoded = json.dumps(  # rebind-ok: framework flow intentionally updates request or lifecycle state
        value, sort_keys=True, default=str
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def safe_text(value: str | None, fallback: str) -> str:
    text = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
        re.sub(r"\s+", " ", value or "").strip() or fallback
    )
    text = re.sub(  # rebind-ok: framework flow intentionally updates request or lifecycle state
        r"https?://\S+", "[url]", text
    )
    if len(text) > 160:
        text = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
            text[:157].rstrip() + "..."
        )
    return text


def server_label(mcp_server: MCPServer) -> str:
    return str(mcp_server.alias or mcp_server.server_name or mcp_server.name or mcp_server.server_id)


def server_description(mcp_server: MCPServer) -> str:
    mcp_info = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
        mcp_server.mcp_info or {}
    )
    description = getattr(  # rebind-ok: framework flow intentionally updates request or lifecycle state
        mcp_server, "description", None
    ) or mcp_info.get("description")
    return safe_text(description, "No description configured.")


def summarize_schema(
    schema: object,
) -> dict[str, object]:  # mutable-ok: framework contract requires mutable request or response containers
    if not isinstance(schema, dict):
        return {}
    normalized: Final = TypeAdapter(dict[str, object]).validate_python(schema)
    properties = normalized.get(  # rebind-ok: framework flow intentionally updates request or lifecycle state
        "properties"
    )
    return {
        "type": normalized.get("type", "object"),
        "required": normalized.get(
            "required",
            [],
        ),
        "properties": (
            sorted(TypeAdapter(dict[str, object]).validate_python(properties)) if isinstance(properties, dict) else []
        ),
    }


def tool_summary(
    tool: MCPTool, include_schema: bool = False
) -> dict[str, object]:  # mutable-ok: framework contract requires mutable request or response containers
    summary: Final[dict[str, object]] = {  # mutable-ok: SDK JSON response is assembled before returning
        "name": tool.name,
        "description": safe_text(getattr(tool, "description", None), "No description configured."),
    }
    schema = getattr(  # rebind-ok: framework flow intentionally updates request or lifecycle state
        tool, "input_schema", None
    )
    if include_schema:
        summary["input_schema"] = schema or {}
    else:
        summary["input_schema_summary"] = summarize_schema(schema)
    return summary


def text_result(
    payload: dict[str, object],  # mutable-ok: framework contract requires mutable request or response containers
) -> CallToolResult:
    return CallToolResult(
        content=[TextContent(text=json.dumps(payload, default=str), type="text")],
        is_error=bool(payload.get("error")),
    )


def gateway_tools(
    description: str | None = None,
) -> list[MCPTool]:  # mutable-ok: framework contract requires mutable request or response containers
    describe_description = (  # rebind-ok: framework flow intentionally updates request or lifecycle state
        description or ("Describe MCP servers and tools available through the LiteLLM LazyMCP gateway.")
    )
    return [
        MCPTool(
            name="mcp_describe",
            description=describe_description,
            input_schema={
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "Optional MCP server name or alias to inspect.",
                    },
                    "tool": {
                        "type": "string",
                        "description": "Optional tool name within the selected MCP server.",
                    },
                },
            },
        ),
        MCPTool(
            name="mcp_call",
            description="Execute a tool from an MCP server available through the LiteLLM LazyMCP gateway. Use mcp_describe first to inspect available servers, tools, and schemas.",
            input_schema={
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "MCP server name or alias.",
                    },
                    "tool": {
                        "type": "string",
                        "description": "Tool name to execute on the selected MCP server.",
                    },
                    "arguments": {
                        "type": "object",
                        "description": "Arguments to pass to the selected MCP tool.",
                    },
                },
                "required": [
                    "server",
                    "tool",
                    "arguments",
                ],
                "additionalProperties": False,
            },
        ),
        MCPTool(
            name="mcp_status",
            description="Report safe diagnostics for the current LiteLLM LazyMCP view.",
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
    ]
