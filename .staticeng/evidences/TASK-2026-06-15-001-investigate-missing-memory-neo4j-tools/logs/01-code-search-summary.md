# Code Search Summary

Commands/sources inspected:
- Grep for `/v1/mcp/tools`, `mcp/tools`, `list_mcp_tools`, `neo4j_expand_neighbors`, `neo4j_shortest_paths` in `/home/staticduo/git/litellm`.
- Read relevant MCP backend files and UI networking/components.

Key code references:
- `litellm/proxy/management_endpoints/mcp_management_endpoints.py:716`: `GET /v1/mcp/tools` route.
- `litellm/proxy/management_endpoints/mcp_management_endpoints.py:727`: imports `_list_mcp_tools`.
- `litellm/proxy/management_endpoints/mcp_management_endpoints.py:729`: calls `_list_mcp_tools(user_api_key_auth=..., mcp_servers=None)`.
- `litellm/proxy/_experimental/mcp_server/server.py:2177`: `_list_mcp_tools` entry point.
- `litellm/proxy/_experimental/mcp_server/server.py:2202`: merges toolset permissions before listing.
- `litellm/proxy/_experimental/mcp_server/server.py:1809`: fetches tools from each allowed server with `add_prefix=True`.
- `litellm/proxy/_experimental/mcp_server/server.py:1817`: applies server `allowed_tools` / `disallowed_tools`.
- `litellm/proxy/_experimental/mcp_server/server.py:1819`: applies key/team/org tool permissions.
- `litellm/proxy/_experimental/mcp_server/server.py:2115`: gets key/team/org allowed tools for one server.
- `litellm/proxy/_experimental/mcp_server/mcp_server_manager.py:2776`: records original upstream name.
- `litellm/proxy/_experimental/mcp_server/mcp_server_manager.py:2777`: builds prefixed name with server prefix.
- `litellm/proxy/_experimental/mcp_server/mcp_server_manager.py:2782`: returns prefixed tool name when `add_prefix=True`.
- `litellm/proxy/_experimental/mcp_server/utils.py:245`: `add_server_prefix_to_name` implementation.
- `litellm/proxy/_experimental/mcp_server/utils.py:256`: `get_server_prefix`, alias first in default mode.
- `ui/litellm-dashboard/src/components/networking.tsx:5227`: UI `listMCPTools` helper.
- `ui/litellm-dashboard/src/components/networking.tsx:5230`: UI uses `/mcp-rest/tools/list?server_id=...`, not `/v1/mcp/tools`.
- `litellm/proxy/_experimental/mcp_server/rest_endpoints.py:549`: REST tools-list route.
- `litellm/proxy/_experimental/mcp_server/rest_endpoints.py:391`: REST single-server listing fetches with `add_prefix=False`.
- `litellm/proxy/_experimental/mcp_server/rest_endpoints.py:400`: REST route still applies server allowlist/disallowlist.
- `litellm/proxy/_experimental/mcp_server/rest_endpoints.py:404`: REST route applies key/team tool permissions if present.
- `litellm/proxy/_experimental/mcp_server/server.py:795`: LazyMCP list-tools exposes only gateway tools.
- `litellm/proxy/_experimental/mcp_server/server.py:2733`: LazyMCP gateway tool names are `mcp_describe`, `mcp_call`, `mcp_status`.

Search result: the literal unprefixed tool names `neo4j_expand_neighbors` and `neo4j_shortest_paths` only appear in the task file inside this repository. They are runtime upstream MCP tools, not hardcoded LiteLLM tools.
