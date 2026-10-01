from __future__ import annotations

import os

from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings


mcp: MCPServer = MCPServer("defend_memory")


@mcp.tool()
def find(query: str = "synthetic") -> str:
    """Return deterministic synthetic data without touching external services."""
    return f"synthetic:{query}"


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", "8000")),
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )
