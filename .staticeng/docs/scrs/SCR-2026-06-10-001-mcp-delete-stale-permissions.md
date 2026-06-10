---
scr_id: SCR-2026-06-10-001-mcp-delete-stale-permissions
status: approved
owner: product_manager
created: 2026-06-10
related_task: TASK-2026-06-10-001-fix-mcp-delete-stale-permissions
---

# SCR-2026-06-10-001: MCP Delete Stale Permission Cleanup

## Problem

Deleting MCP servers can fail with a confusing 404 when the requested server id no longer exists in `LiteLLM_MCPServerTable` but remains referenced by object permissions. Existing deletes also risk leaving orphaned references in object permissions and user credentials.

## Approved Behavior

`DELETE /v1/mcp/server/{server_id}` must keep MCP server deletion and related cleanup consistent. When the server exists, delete it and remove related stale references from object permissions and MCP user credentials. When the server does not exist but references remain, clean those references and return a successful cleanup response rather than breaking the UX. When the server does not exist and has no related references, return a clear 404.

MCP server listing and permission expansion must not surface ids that do not exist in `LiteLLM_MCPServerTable` as real, deletable MCP servers.

## Scope

In scope:
- `LiteLLM_ObjectPermissionTable.mcp_servers` cleanup.
- `LiteLLM_ObjectPermissionTable.mcp_tool_permissions` cleanup where keyed by the server id.
- `LiteLLM_MCPUserCredentials` cleanup for the deleted server id.
- Tests covering existing deletes, stale referenced deletes, stale list/permission behavior, and credentials cleanup.

Out of scope:
- Manual production DB edits.
- Using this session's LiteLLM admin MCP server; it does not point at the affected Fedora instance.
- UI redesign.

## Acceptance Criteria

AC-1. Existing MCP server deletion removes the MCP server row and removes its id from object permission `mcp_servers` arrays.

AC-2. Existing MCP server deletion removes entries keyed by that server id from `mcp_tool_permissions` where present.

AC-3. Existing MCP server deletion removes `LiteLLM_MCPUserCredentials` rows associated with the server id.

AC-4. Deleting a non-existent but referenced server id performs stale-reference cleanup and returns a non-error cleanup response.

AC-5. Deleting a non-existent unreferenced server id returns a clear 404.

AC-6. Listing/permission expansion does not expose stale permission-only server ids as real MCP servers or grant access to them.

AC-7. Automated regression tests cover the behaviors above.
