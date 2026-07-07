# TASK-2026-06-15-001 Investigation Summary

## Finding
The observed discrepancy is primarily a naming-surface mismatch, not missing upstream Memory MCP tools. `/v1/mcp/tools` enumerates the multi-server gateway view and always prefixes upstream tool names with the MCP server prefix. For the Memory MCP server, `neo4j_expand_neighbors` and `neo4j_shortest_paths` therefore appear as `memory-neo4j_expand_neighbors` and `memory-neo4j_shortest_paths`. The LiteLLM UI Memory MCP Tools page calls a different endpoint, `/mcp-rest/tools/list?server_id=<memory-server-id>`, which fetches one server with `add_prefix=False`, so the same upstream tools appear unprefixed as `neo4j_expand_neighbors` and `neo4j_shortest_paths`.

Confidence: high for the prefixing/UI-endpoint explanation. Medium for the historical 516-tool observation because the current runtime now returns 548 tools and includes the prefixed forms.

## AC-1: `/v1/mcp/tools` Code Path and Filtering/Prefixing
- `litellm/proxy/management_endpoints/mcp_management_endpoints.py:716` defines `GET /v1/mcp/tools`.
- `litellm/proxy/management_endpoints/mcp_management_endpoints.py:727` imports `_list_mcp_tools`.
- `litellm/proxy/management_endpoints/mcp_management_endpoints.py:729` calls `_list_mcp_tools(user_api_key_auth=..., mcp_servers=None)`.
- `litellm/proxy/_experimental/mcp_server/server.py:2177` defines `_list_mcp_tools`.
- `litellm/proxy/_experimental/mcp_server/server.py:2202` merges key toolset permissions before listing.
- `litellm/proxy/_experimental/mcp_server/server.py:1809` fetches upstream tools with `add_prefix=True`.
- `litellm/proxy/_experimental/mcp_server/server.py:1817` applies server-level allowlist/disallowlist.
- `litellm/proxy/_experimental/mcp_server/server.py:1819` applies key/team/org tool permissions.
- `litellm/proxy/_experimental/mcp_server/mcp_server_manager.py:2777` builds prefixed tool names.
- `litellm/proxy/_experimental/mcp_server/mcp_server_manager.py:2782` returns prefixed names when `add_prefix=True`.
- `litellm/proxy/_experimental/mcp_server/utils.py:245` implements `add_server_prefix_to_name`.
- `litellm/proxy/_experimental/mcp_server/utils.py:256` chooses the server prefix. In default mode, alias wins, so Memory alias `memory` produces `memory-<tool>`.

Runtime evidence:
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/02-runtime-v1-mcp-tools-sanitized.txt`
- Current `/v1/mcp/tools` returns 548 tools.
- Unprefixed `neo4j_expand_neighbors=False` and `neo4j_shortest_paths=False`.
- Prefixed `memory-neo4j_expand_neighbors=True` and `memory-neo4j_shortest_paths=True`.

## AC-2: UI Memory MCP Tools Code Path and Difference
- `ui/litellm-dashboard/src/components/mcp_tools/mcp_tools.tsx:117` calls `listMCPTools(accessToken, serverId, ...)`.
- `ui/litellm-dashboard/src/components/networking.tsx:5227` defines `listMCPTools`.
- `ui/litellm-dashboard/src/components/networking.tsx:5230` calls `/mcp-rest/tools/list?server_id=${serverId}`.
- `litellm/proxy/_experimental/mcp_server/rest_endpoints.py:549` defines the REST list-tools endpoint.
- `litellm/proxy/_experimental/mcp_server/rest_endpoints.py:391` fetches one server's tools with `add_prefix=False`.
- `litellm/proxy/_experimental/mcp_server/rest_endpoints.py:400` still applies server allowlist/disallowlist.
- `litellm/proxy/_experimental/mcp_server/rest_endpoints.py:404` applies key/team tool permissions if present.

Runtime evidence:
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/03-runtime-rest-tools-per-server-sanitized.txt`
- Memory server REST list returns 19 tools and includes unprefixed `neo4j_expand_neighbors` and `neo4j_shortest_paths`.
- Separate legacy Neo4j server REST list returns 6 tools: `get-schema`, `get_schema`, `read-cypher`, `read_cypher`, `write-cypher`, `write_cypher`.

## AC-3: Configuration, Access Groups, Cache, Logs, Drift
Configuration evidence:
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/04-runtime-mcp-server-inventory-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/05-db-mcp-config-sanitized.txt`
- Memory server: `server_id=937e3e97-c5d7-4968-af73-831db0b810b7`, name `Memory`, alias `memory`, 19 `allowed_tools`, access groups `opencode,memory,openclaw`, `tool_allowlist_enforced=true`.
- Memory server allowlist includes `neo4j_expand_neighbors` and `neo4j_shortest_paths`.
- Legacy Neo4j server: `server_id=dbf6a1ae-f5c2-4bfa-ac24-2c6c29168348`, name `Neo4j`, alias `neo4j`, 6 `allowed_tools`, access group `memory_legacy`. It does not expose expand/shortest path tools.
- StaticTeam has a team-level `mcp_tool_permissions` list for the Memory server that omits `neo4j_expand_neighbors` and `neo4j_shortest_paths`, but current sanitized key checks found no active StaticTeam keys and no active unblocked virtual keys directly carrying these MCP permissions. This is a potential historical/alternate-key filter to verify if the original OpenCode key was not the master key used in this investigation.

Log/cache evidence:
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/06-litellm-recent-mcp-logs-sanitized.txt`
- Logs show successful `/v1/mcp/tools`, `/mcp-rest/tools/list`, and `/lazymcp` requests with no relevant tool-listing errors in the inspected window.
- `litellm/proxy/_experimental/mcp_server/server.py:2231` defines a 300-second LazyMCP catalog cache, but `/v1/mcp/tools` uses `_list_mcp_tools`, not the LazyMCP catalog. No stale cache evidence was found for `/v1/mcp/tools`.
- `litellm/proxy/_experimental/mcp_server/server.py:795` and `litellm/proxy/_experimental/mcp_server/server.py:2733` show LazyMCP itself exposes only gateway tools (`mcp_describe`, `mcp_call`, `mcp_status`), with upstream tools inside the describe/catalog payload.

## AC-4: Most Likely Root Cause and Next Steps
Most likely root cause: `/v1/mcp/tools` is behaving as designed by returning globally unique, server-prefixed tool names. The UI Memory server page is also behaving as designed by returning one server's unprefixed tools. The tools are present in `/v1/mcp/tools` under `memory-neo4j_expand_neighbors` and `memory-neo4j_shortest_paths`, not under the raw upstream names.

Secondary possibility: if the original OpenCode LazyMCP key still observes 516 tools and no prefixed `memory-neo4j_*` expand/shortest tools, then that specific key is likely using stale auth/cache or a narrower key/team/org `mcp_tool_permissions` ceiling. StaticTeam's team-level Memory tool permissions currently omit both tools, which could explain the older observation for a team-scoped key, but the current runtime evidence with the master key does not reproduce it.

Recommended next diagnostic:
1. Re-run the endpoint with the exact configured OpenCode LazyMCP key and check for `memory-neo4j_expand_neighbors` and `memory-neo4j_shortest_paths`, not the unprefixed names.
2. If the exact key still misses the prefixed forms, inspect that key's `team_id`, `object_permission_id`, inherited team/org/agent `mcp_tool_permissions`, and route restrictions; update the relevant permissions or rotate the key after confirming intended access.
3. If the goal is API/UI naming parity, open an implementation task to either document that `/v1/mcp/tools` returns prefixed names or add an explicit server-scoped listing mode/metadata that includes both `name` and `upstream_name`.

## Reopen Addendum: Exact OpenCode Key Root Cause
PMA's reopened finding is reproduced with the exact configured OpenCode LazyMCP key from `/home/staticduo/.config/opencode/opencode.json`, without exposing the key. The configured header value includes a `Bearer ` prefix; LiteLLM strips that before hashing and resolves it to the `OpenCode` virtual key.

Key-specific evidence:
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/10-reopen-exact-key-vs-master-tools-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/11-reopen-exact-key-permissions-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/12-reopen-exact-key-rest-vs-v1-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/13-reopen-recent-mcp-logs-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/14-reopen-code-path-delta-summary.md`

Reproduced behavior:
- Exact OpenCode key: `/v1/mcp/tools` returns 516 tools.
- Master/admin context: `/v1/mcp/tools` returns 548 tools.
- The exact key is missing 32 tools that master sees; 30 are destructive/admin-style tools from other MCP servers, and the two Memory tools are `memory-neo4j_expand_neighbors` and `memory-neo4j_shortest_paths`.
- Exact key still sees `memory-neo4j_read_cypher`, `memory-neo4j_write_cypher`, `neo4j-read_cypher`, and `neo4j-write_cypher`.

Concrete root cause:
- The exact OpenCode virtual key has no key-level `object_permission_id`, no key-level `mcp_tool_permissions`, no `allowed_routes`, no org, and no agent.
- The key belongs to StaticTeam (`team_id=49cfd117-ef74-4eec-b26e-2d2ff083f5be`).
- StaticTeam has team-level Memory server tool permissions for server `937e3e97-c5d7-4968-af73-831db0b810b7` containing 17 Memory tools; it omits `neo4j_expand_neighbors` and `neo4j_shortest_paths`.
- `/v1/mcp/tools` applies inherited team tool permissions through `MCPRequestHandler.get_allowed_tools_for_server`, so the two tools are filtered out for this key.

UI/direct endpoint difference:
- With the same exact key, `/mcp-rest/tools/list?server_id=937e3e97-c5d7-4968-af73-831db0b810b7` returns all 19 Memory server tools, including unprefixed `neo4j_expand_neighbors` and `neo4j_shortest_paths`.
- Code inspection shows `/mcp-rest/tools/list` only checks `user_api_key_auth.object_permission.mcp_tool_permissions` in this path and does not call `MCPRequestHandler.get_allowed_tools_for_server`, so it does not apply inherited team/org/agent tool permissions like `/v1/mcp/tools` does. This is why the UI can show tools that `/v1/mcp/tools` filters for the same team-scoped key.

Stale cache assessment:
- This is not primarily stale cache. The DB row for the exact key and team permissions explain the 516-vs-548 delta exactly enough: the exact key is team-scoped and inherits StaticTeam's narrower Memory permission list.
- Recent sanitized logs show successful `/v1/mcp/tools`, `/mcp-rest/tools/list`, and `/lazymcp` requests with no relevant tool-listing errors.

Recommended safe fix:
1. If OpenCode should have these graph navigation tools, update StaticTeam's Memory `mcp_tool_permissions` for server `937e3e97-c5d7-4968-af73-831db0b810b7` to add `neo4j_expand_neighbors` and `neo4j_shortest_paths`; then let the normal management-object cache TTL expire or explicitly invalidate/restart the LiteLLM proxy.
2. Alternatively, grant the OpenCode key a key-specific object permission/toolset including those two tools if this should not apply to the whole StaticTeam.
3. Open a follow-up implementation task to align `/mcp-rest/tools/list` with `/v1/mcp/tools` inherited team/org/agent tool filtering, or intentionally document that admin/UI single-server listing is broader than runtime gateway listing.

## AC-5: Evidence Recorded Without Secrets
Evidence directory:
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/`

Evidence files:
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/01-code-search-summary.md`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/02-runtime-v1-mcp-tools-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/03-runtime-rest-tools-per-server-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/04-runtime-mcp-server-inventory-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/05-db-mcp-config-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/06-litellm-recent-mcp-logs-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/07-health-check-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/08-db-key-team-scope-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/09-active-key-scope-counts-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/10-reopen-exact-key-vs-master-tools-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/11-reopen-exact-key-permissions-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/12-reopen-exact-key-rest-vs-v1-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/13-reopen-recent-mcp-logs-sanitized.txt`
- `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/14-reopen-code-path-delta-summary.md`

Secret handling:
- Evidence omits API keys, tokens, cookies, database passwords, and full secret-bearing URLs.
- Runtime commands read secrets only inside the container or local process environment and wrote sanitized counts/names/config metadata only.
