import type { MCPConnector } from "./mcp_connect";

export const LAZY_MCP_CONNECTOR: MCPConnector = {
  endpointPath: "/lazymcp",
  endpointName: "LazyMCP",
  serverLabel: "litellm-lazymcp",
  openAIPathSuffix: "/lazymcp",
  zapierLabel: "LiteLLM LazyMCP",
  heading: "Connect to your MCP client with LazyMCP",
  description:
    "LazyMCP connects MCP clients to LiteLLM while exposing only three gateway tools: mcp_describe, mcp_call, and mcp_status. This avoids sending every upstream MCP tool schema to the model on each request. LazyMCP respects virtual key, team, access group, toolset, and request-header permissions. The x-mcp-servers header works the same as standard MCP and server descriptions help the model choose the right server.",
};
