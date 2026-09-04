# Read-Only API And Source Findings

## Supported Runtime Reads

Supported `litellm_admin-list_mcp_servers` returned 27 servers from the NAS/staticduo LiteLLM. Prior governed topology memory explicitly distinguishes that admin MCP from Fedora Defend. The relevant sanitized NAS projection was:

```text
server_id=937e3e97-c5d7-4968-af73-831db0b810b7
server_name=Memory
alias=memory
transport=http
auth_type=none
allowed_tools includes find
mcp_access_groups=memory,openclaw,opencode
```

No credential, URL, static header, environment variable, tool input, response content, or private payload was retained

Supported `mcp_describe` for server `memory` returned 19 tool schemas and identified the NAS gateway tool as `memory-find`. No tool was called. This result verifies the upstream `find` plus alias-prefix naming rule only. The NAS UUID is not Fedora identity and must never be used in the temporary Fedora toolset

Supported `litellm_admin-admin_request` was attempted read-only for `GET /v1/mcp/tools` and timed out. The generic admin MCP correctly blocked `/mcp-rest/tools/list` as a runtime path. Neither outcome mutated state. They reinforce the execution requirement to use the candidate's supported HTTP read API directly and stop on timeout rather than infer membership

Unauthenticated read-only GETs to Fedora `/v1/mcp/server`, `/mcp-rest/tools/list?mcp_server_name=defend_memory`, and `/v1/mcp/toolset` each returned HTTP 401. This proves the public supported routes are reachable and protected, but reveals no catalog identity. No credential substitution or secret access was attempted

Reopen 1 used the PMA-authorized existing administrator credential from Fedora's owner-owned mode-0600 host-local source. A first fail-closed run sent the same two authorized GET classes but found zero rows because it incorrectly expected `allowed_tools` to contain `find`; the active row uses an empty server allowlist. No state changed. After inspecting only the safe matching-row shape, the corrected single in-memory client sent `GET /v1/mcp/server` and `GET /mcp-rest/tools/list?server_id=<resolved-id>`. It required one active alias/server-name match with HTTP transport and no upstream auth, then required one `find` whose metadata matched the same ID and alias. The only retained outputs are:

```text
server_id=54a0ad17239e9f184882cf47e3ac277c
membership_sha256=e08d6ac35d8ceea4eaaaaccce855a9df910684f3f54cff9cce26797dd33ae6cd
```

The credential was never printed, hashed, copied, exported, supplied in command arguments, or retained in evidence. No complete API response, tool schema, description, arguments, private payload, URL, header, or credential-bearing field was retained

## Source Contract

- `litellm/types/mcp_server/mcp_toolset.py` defines members as exactly `server_id` plus `tool_name`; create accepts name, optional description, and tools; update accepts required ID plus optional replacement fields
- `litellm/proxy/management_endpoints/mcp_management_endpoints.py` exposes `POST /v1/mcp/toolset` (201), `GET /v1/mcp/toolset`, `GET /v1/mcp/toolset/{id}`, `PUT /v1/mcp/toolset`, and `DELETE /v1/mcp/toolset/{id}` (202). Mutations require `proxy_admin`; admin-view reads can list/get
- `litellm/proxy/_experimental/mcp_server/toolset_db.py` generates the ID on create, stores the tool array, replaces supplied fields on update, and deletes only the toolset row
- `litellm/proxy/_experimental/mcp_server/mcp_server_manager.py` resolves toolset members directly into `{server_id: [tool_name]}`. The stored name is the upstream name as written, never the gateway-prefixed name
- `litellm/proxy/_experimental/mcp_server/rest_endpoints.py` exposes supported single-server and toolset-scoped metadata listing. Single-server list responses carry `mcp_info.server_id` and alias
- `litellm/proxy/management_endpoints/internal_user_endpoints.py` supports explicit object-permission unlink with `/user/update` and removes keys, invitations, and memberships before `/user/delete`; toolset deletion itself does not clean those references

## Prior Governed Evidence

The latest Fedora preflight returned HTTP 200 with zero toolsets, zero `defend_memory` matches, and no principal creation. Earlier Fedora evidence established an active MCP row with alias `defend_memory`, transport `http`, auth type `none`, and route-visible tool `defend_memory-find`, but did not retain its UUID. This design resolves the stable part as upstream member `find` and makes the missing UUID an exact supported-read precondition. The executor must not infer it from NAS, history, alias, URL, or database state

## Mutation Boundary

This task performed no toolset/principal CRUD, no direct DB access, no upstream tool invocation, no source/config/runtime change, no deploy, and no NAS access. Reopen 1's only host action was the explicitly authorized Fedora read-only API pair with in-memory credential consumption
