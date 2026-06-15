# TASK-2026-06-11-001 Fix MCP Delete JSON Serialization Evidence

## Summary

Implemented the MCP delete cleanup serialization fix so cleaned `mcp_tool_permissions` are written as a JSON string via `safe_dumps`, including when the ORM supplies the field as a Python dict with UUID-like server IDs.

## Acceptance Criteria Coverage

- AC-1: Covered by code change in `litellm/proxy/_experimental/mcp_server/db.py`; `_get_mcp_tool_permissions_without_server` now serializes the updated permission map before `LiteLLM_ObjectPermissionTable` updates, preventing Prisma GraphQL parsing of raw UUID-like keys.
- AC-2: Covered by regression test update in `tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py`; cleanup removes the deleted UUID-like server ID from `mcp_servers` and from parsed `mcp_tool_permissions`.
- AC-3: Regression test updated to assert `mcp_tool_permissions` passed to Prisma update is a string and JSON-decodes to the expected remaining permissions.
- AC-4: Not verified by developer. Per task handoff, did not touch `litellm.staticduo.com`; Fedora deployment/delete verification remains for PMA/release owner.

## Verification

- Targeted pytest attempted: `python -m pytest tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py -k "cleanup_mcp_server_references"`.
  - Result: blocked before collection by missing local dependency `openai`.
  - Log: `.staticeng/evidences/TASK-2026-06-11-001-fix-mcp-delete-json-serialization/logs/pytest-targeted.log`.
- Targeted ruff attempted: `python -m ruff check litellm/proxy/_experimental/mcp_server/db.py tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py`.
  - Result: blocked because `ruff` is not installed in this Python environment.
  - Log: `.staticeng/evidences/TASK-2026-06-11-001-fix-mcp-delete-json-serialization/logs/ruff-targeted.log`.

## StaticEng Validation

- `staticeng_validate` attempted.
  - Result: failed on pre-existing repository CodeMap coverage/link issues unrelated to this task.
  - Log: `.staticeng/evidences/TASK-2026-06-11-001-fix-mcp-delete-json-serialization/logs/staticeng-validate.log`.

## Notes

No production host was touched.
