# TASK-2026-06-10-001 Fix MCP Delete Stale Permission References

## Summary

Implemented MCP delete cleanup for object permissions and user credentials, plus stricter permission expansion so stale permission-only IDs are not treated as real MCP server access.

## Acceptance Criteria Coverage

- AC-1: Existing MCP server deletion removes the MCP server row and removes its id from object permission `mcp_servers` arrays.
  - Covered by `TestRemoveMCPServer::test_delete_existing_server_cleans_permissions_and_credentials` and `test_cleanup_mcp_server_references_removes_permissions_and_credentials`.
- AC-2: Existing MCP server deletion removes entries keyed by that server id from `mcp_tool_permissions` where present.
  - Covered by `test_cleanup_mcp_server_references_removes_permissions_and_credentials`.
- AC-3: Existing MCP server deletion removes `LiteLLM_MCPUserCredentials` rows associated with the server id.
  - Covered by `test_cleanup_mcp_server_references_removes_permissions_and_credentials`.
- AC-4: Deleting a non-existent but referenced server id performs stale-reference cleanup and returns a non-error cleanup response.
  - Covered by `TestRemoveMCPServer::test_delete_missing_referenced_server_returns_cleanup_response`.
- AC-5: Deleting a non-existent unreferenced server id returns a clear 404.
  - Covered by `TestRemoveMCPServer::test_delete_missing_unreferenced_server_returns_404`.
- AC-6: Listing/permission expansion does not expose stale permission-only server ids as real MCP servers or grant access to them.
  - Covered by `test_resolve_team_allowed_mcp_servers_string_tool_permissions`, `test_resolve_team_allowed_mcp_servers_dict_tool_permissions`, `test_resolve_team_allowed_mcp_servers_filters_stale_ids_from_db_lookup`, and `test_resolve_mcp_server_identifiers_does_not_resolve_unknown_ids`.
- AC-7: Automated regression tests cover the behaviors above.
  - Covered by full MCP endpoint/helper regression run.

## Verification

- `uv run python -m pytest tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py tests/test_litellm/proxy/management_helpers/test_object_permission_utils.py`
  - PASS: 110 passed, 7 warnings.
  - Log: `.staticeng/evidences/TASK-2026-06-10-001-fix-mcp-delete-stale-permissions/logs/pytest-mcp-regression.log`
- `uv run ruff check litellm/proxy/_experimental/mcp_server/db.py litellm/proxy/management_endpoints/mcp_management_endpoints.py litellm/proxy/management_helpers/object_permission_utils.py tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py tests/test_litellm/proxy/management_helpers/test_object_permission_utils.py`
  - PASS.
  - Log: `.staticeng/evidences/TASK-2026-06-10-001-fix-mcp-delete-stale-permissions/logs/ruff-check.log`

## Diff Evidence

- `.staticeng/evidences/TASK-2026-06-10-001-fix-mcp-delete-stale-permissions/logs/diff-stat.log`

## Screenshots

No UI changes; screenshots not required.
