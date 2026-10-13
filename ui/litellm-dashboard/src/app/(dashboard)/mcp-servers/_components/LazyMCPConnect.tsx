import MCPConnect, { type MCPConnectProps } from "./mcp_connect";
import { LAZY_MCP_CONNECTOR } from "./lazy_mcp_connector";

export default function LazyMCPConnect({
  currentServerAccessGroups,
}: Pick<MCPConnectProps, "currentServerAccessGroups">) {
  return <MCPConnect currentServerAccessGroups={currentServerAccessGroups} connector={LAZY_MCP_CONNECTOR} />;
}
