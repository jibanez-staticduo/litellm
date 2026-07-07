# Reopen Code Path Delta Summary

Key-specific root cause evidence from code inspection:

- `litellm/proxy/management_endpoints/mcp_management_endpoints.py:729` calls `_list_mcp_tools(...)` for `/v1/mcp/tools`.
- `litellm/proxy/_experimental/mcp_server/server.py:1819` calls `filter_tools_by_key_team_permissions(...)` after server allowlist filtering.
- `litellm/proxy/_experimental/mcp_server/server.py:2115` calls `MCPRequestHandler.get_allowed_tools_for_server(...)`.
- `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:887` defines `get_allowed_tools_for_server`.
- `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:906` loads key object permissions.
- `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:910` loads team object permissions.
- `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:938` applies team tool restrictions when present.
- `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:949` can further intersect agent tool permissions.
- `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:968` can further intersect org tool permissions.

UI/REST delta:

- `ui/litellm-dashboard/src/components/networking.tsx:5230` calls `/mcp-rest/tools/list?server_id=...`.
- `litellm/proxy/_experimental/mcp_server/rest_endpoints.py:391` fetches single-server tools with `add_prefix=False`.
- `litellm/proxy/_experimental/mcp_server/rest_endpoints.py:404` only checks `user_api_key_auth.object_permission.mcp_tool_permissions` in this path.
- The REST UI path does not call `MCPRequestHandler.get_allowed_tools_for_server`, so it does not inherit team/org/agent tool restrictions the same way `/v1/mcp/tools` does.

Conclusion:

The exact OpenCode key has no key-level `object_permission_id`, but belongs to StaticTeam. StaticTeam has Memory server `mcp_tool_permissions` that omit `neo4j_expand_neighbors` and `neo4j_shortest_paths`. `/v1/mcp/tools` correctly applies inherited team tool permissions and filters them out. The UI REST endpoint shows all 19 Memory server allowlisted tools because it does not apply inherited team restrictions in the same way.
