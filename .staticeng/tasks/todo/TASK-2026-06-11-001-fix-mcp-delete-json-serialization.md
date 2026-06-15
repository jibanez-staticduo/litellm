---
task_id: TASK-2026-06-11-001-fix-mcp-delete-json-serialization
complexity: standard
track: implementation
slice: core
status: todo
assigned_to: developer
handoff_from: product_manager
scr: SCR-2026-06-11-001-mcp-delete-graphql-json-serialization
parent: TASK-2026-06-10-001-fix-mcp-delete-stale-permissions
discussion: DISCUSSION-002
---

# Fix MCP Delete JSON Serialization

## Classification

- complexity: standard
- track: implementation
- slice: core

## Context

On Fedora `litellm.defend.tech`, deleting the Keycloak MCP server failed with:

`DELETE /v1/mcp/server/16010c20-88dd-4f12-9025-9dd84bafc283` -> 500

Stack trace points to `cleanup_mcp_server_references` updating `LiteLLM_ObjectPermissionTable.mcp_tool_permissions` with a Python dict. Existing object permission helper paths serialize `mcp_tool_permissions` via `safe_dumps` to avoid Prisma GraphQL parser issues with UUID-like keys.

Relevant file:
- `litellm/proxy/_experimental/mcp_server/db.py`

Relevant tests:
- `tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py`
- `tests/test_litellm/proxy/management_helpers/test_object_permission_utils.py`

## Acceptance Criteria

AC-1. Deleting an MCP server with object permission `mcp_tool_permissions` keyed by server UUID does not raise Prisma GraphQL parse errors.

AC-2. Cleanup removes the deleted server id from `mcp_servers` and `mcp_tool_permissions`.

AC-3. Regression tests cover the serialization behavior.

AC-4. Fedora `litellm.defend.tech` can delete the Keycloak MCP server or has the MCP removed through the fixed endpoint.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-06-11-001-fix-mcp-delete-json-serialization/` with:
- `SUMMARY.md` mapping ACs to verification.
- logs for tests and release/deploy if PMA runs it.

## Handoff

[Agent Message] From: product_manager To: developer
Please implement the serialization fix with minimal code change and tests. Do not touch `litellm.staticduo.com`. Return Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, Recommended Next Step.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Implemented minimal serialization fix in `litellm/proxy/_experimental/mcp_server/db.py`: cleaned `mcp_tool_permissions` are now returned as `safe_dumps(updated_permissions)` for both dict and string inputs when a server ID is removed.
- Updated regression coverage in `tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py` using UUID-like MCP server IDs and asserting Prisma update data stores `mcp_tool_permissions` as a JSON string with the deleted server removed.
- Created evidence under `.staticeng/evidences/TASK-2026-06-11-001-fix-mcp-delete-json-serialization/` with AC mapping and attempted verification logs.
- Verification blocked locally: targeted pytest fails during import because `openai` is missing; targeted ruff fails because `ruff` is not installed.
- `staticeng_validate` was attempted and failed on pre-existing CodeMap link/coverage issues unrelated to this task.
- Did not touch `litellm.staticduo.com`; Fedora delete verification remains pending for PMA/release owner.
