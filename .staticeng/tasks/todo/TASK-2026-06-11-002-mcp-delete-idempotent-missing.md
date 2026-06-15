---
task_id: TASK-2026-06-11-002-mcp-delete-idempotent-missing
complexity: standard
track: implementation
slice: core
status: todo
assigned_to: developer
handoff_from: product_manager
scr: SCR-2026-06-11-002-mcp-delete-idempotent-missing
parent: TASK-2026-06-11-001-fix-mcp-delete-json-serialization
discussion: DISCUSSION-002
---

# Make MCP Delete Idempotent For Missing Servers

## Context

After hotpatching MCP delete cleanup serialization, deleting Keycloak succeeded. Deleting Syncthing still returned 404 because the server id was already absent from `LiteLLM_MCPServerTable` and no stale references existed. The UI/client can still attempt to delete such ids, so the backend should treat missing deletes as an accepted no-op.

Affected endpoint:
- `DELETE /v1/mcp/server/{server_id}` in `litellm/proxy/management_endpoints/mcp_management_endpoints.py`

## Acceptance Criteria

AC-1. Missing MCP server ids with stale references still clean references and return 202.

AC-2. Missing MCP server ids with no references return 202 no-op rather than 404.

AC-3. Existing MCP server deletes still remove the row, clean permissions/credentials, and reload the MCP registry.

AC-4. Regression tests cover the no-op missing id behavior.

## Expected Evidence

Update or create `.staticeng/evidences/TASK-2026-06-11-002-mcp-delete-idempotent-missing/` with SUMMARY.md and test logs.

## Handoff

[Agent Message] From: product_manager To: developer
Implement minimal code/test changes so missing MCP server deletes are idempotent 202 responses. Do not touch `litellm.staticduo.com`. Return the shared output contract.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Implemented idempotent `202 Accepted` response for missing MCP server ids when no stale references exist.
- Preserved existing `202 Accepted` cleanup response for missing ids with stale references.
- Preserved existing delete behavior for real server rows, including manager removal and database registry reload.
- Added regression coverage by changing the missing unreferenced delete test from expected `404` to the new no-op `202` body.
- Evidence written to `.staticeng/evidences/TASK-2026-06-11-002-mcp-delete-idempotent-missing/`.
- Verification passed: targeted pytest and ruff logs are in the evidence directory.
