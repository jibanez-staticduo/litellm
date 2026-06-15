# TASK-2026-06-11-002 MCP Delete Idempotent Missing

## Summary

Implemented idempotent no-op behavior for `DELETE /v1/mcp/server/{server_id}` when the MCP server row is already absent and no stale references exist.

## Acceptance Criteria Coverage

- AC-1: Covered. Existing missing-server stale-reference path still returns `202` with `cleaned_stale_references: true`.
- AC-2: Covered. Missing server ids with no references now return `202` with `deleted: false` and `cleaned_stale_references: false`.
- AC-3: Covered. Existing server delete path still calls `delete_mcp_server`, removes from the manager, and reloads the registry.
- AC-4: Covered. Regression test updated for missing unreferenced server no-op response.

## Verification

- `uv run pytest tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py -k 'TestRemoveMCPServer or cleanup_mcp_server_references'` passed. See `.staticeng/evidences/TASK-2026-06-11-002-mcp-delete-idempotent-missing/logs/pytest-targeted.log`.
- `uv run ruff check litellm/proxy/management_endpoints/mcp_management_endpoints.py tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py` passed. See `.staticeng/evidences/TASK-2026-06-11-002-mcp-delete-idempotent-missing/logs/ruff-check.log`.

## Screenshots

No UI changes; screenshots are not required.
