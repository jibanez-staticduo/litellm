---
scr_id: SCR-2026-06-11-002-mcp-delete-idempotent-missing
status: approved
owner: product_manager
created: 2026-06-11
related_task: TASK-2026-06-11-002-mcp-delete-idempotent-missing
---

# SCR-2026-06-11-002: Idempotent MCP Delete For Missing Servers

## Problem

Fedora `litellm.defend.tech` can still show stale MCP servers in the UI/client state. When the user clicks delete for a server id that no longer exists in `LiteLLM_MCPServerTable` and no longer has stale permission references, the backend returns 404. This breaks the delete UX even though the desired terminal state is already achieved.

Observed example: deleting Syncthing `e73c4c37-4466-4ee3-a200-30b9be4eca2c` returned 404, while the server did not exist and was not returned by `/v1/mcp/server`.

## Approved Behavior

`DELETE /v1/mcp/server/{server_id}` should be idempotent. If the MCP server does not exist, the endpoint should still return `202 Accepted` with a message indicating whether stale references were cleaned or the server was already absent.

## Acceptance Criteria

AC-1. Missing MCP server ids with stale references still clean references and return 202.

AC-2. Missing MCP server ids with no references return 202 no-op rather than 404.

AC-3. Existing MCP server deletes still remove the row, clean permissions/credentials, and reload the MCP registry.

AC-4. Regression tests cover the no-op missing id behavior.
