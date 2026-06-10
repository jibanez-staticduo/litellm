---
task_id: TASK-2026-06-10-001-fix-mcp-delete-stale-permissions
complexity: standard
track: implementation
slice: core
status: completed
assigned_to: developer
handoff_from: product_manager
scr: SCR-2026-06-10-001-mcp-delete-stale-permissions
parent: none
discussion: DISCUSSION-002
remote_context: fedora:/home/staticduo/docker/litellm
user_session_to_resume: ses_14e184372ffeBXz62QER3qNtxT
---

# Fix MCP Delete Stale Permission References

## Classification

- complexity: standard
- track: implementation
- slice: core

## Context

The user reported a production-like issue on Fedora under `fedora:/home/staticduo/docker/litellm`. Do not use this session's `litellm_admin` MCP server because it does not point to the affected instance.

Observed version/image: LiteLLM package 1.88.0, `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260608-fix-mcp-null-maps`.

Affected endpoint: `DELETE /v1/mcp/server/{server_id}`.

Relevant tables:
- `LiteLLM_MCPServerTable`
- `LiteLLM_ObjectPermissionTable`
- `LiteLLM_TeamTable`
- `LiteLLM_MCPUserCredentials`

Relevant config: `general_settings.user_mcp_management_mode: restricted`.

Repro symptom: UI attempted to delete `server_id=5f303ed9-3916-40e7-b3b7-40d7498b054b`; backend returned 404. That id did not exist in `LiteLLM_MCPServerTable`, but did appear in `LiteLLM_ObjectPermissionTable.mcp_servers` for a team permission associated with StaticTeam. Several similar stale references exist.

Hypothesis: list/permission expansion exposes ids from `object_permission.mcp_servers` without validating they still exist, then delete only deletes from `litellm_mcpservertable` and leaves object permission/tool permission/credential data stale.

## Requirements

Implement the approved behavior in `SCR-2026-06-10-001-mcp-delete-stale-permissions.md`.

Be careful with current worktree state. `.staticeng` artifacts may already be dirty and are orchestrator state. Do not overwrite unrelated user changes. If non-StaticEng unexpected code changes appear, stop and report to PMA.

## Acceptance Criteria

AC-1. Existing MCP server deletion removes the MCP server row and removes its id from object permission `mcp_servers` arrays.

AC-2. Existing MCP server deletion removes entries keyed by that server id from `mcp_tool_permissions` where present.

AC-3. Existing MCP server deletion removes `LiteLLM_MCPUserCredentials` rows associated with the server id.

AC-4. Deleting a non-existent but referenced server id performs stale-reference cleanup and returns a non-error cleanup response.

AC-5. Deleting a non-existent unreferenced server id returns a clear 404.

AC-6. Listing/permission expansion does not expose stale permission-only server ids as real MCP servers or grant access to them.

AC-7. Automated regression tests cover the behaviors above.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-06-10-001-fix-mcp-delete-stale-permissions/` with:
- `SUMMARY.md` mapping each AC to verification.
- `logs/` containing test output, lint output if run, and diff/stat evidence.
- No screenshots required unless UI verification is added.

## Suggested Investigation Targets

- `litellm/proxy/management_endpoints/mcp_management_endpoints.py`
- `litellm/proxy/_experimental/mcp_server/db.py`
- `litellm/proxy/management_helpers/object_permission_utils.py`
- `tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py`
- `tests/test_litellm/proxy/management_helpers/test_object_permission_utils.py`

## Handoff

[Agent Message] From: product_manager To: developer
Please implement this task only after confirming the worktree is safe. Resume or consult the prior remote session `ses_14e184372ffeBXz62QER3qNtxT` if useful via opencode on `fedora:/home/staticduo/docker/litellm`, but do not use the current LiteLLM admin MCP because it points elsewhere. Return the shared output contract: Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, Recommended Next Step. Include exact verification commands and evidence paths.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

Implemented MCP server delete cleanup for object permission `mcp_servers`, `mcp_tool_permissions`, and MCP user credentials. Non-existent referenced server ids now return a 202 cleanup response; non-existent unreferenced ids still return 404. Team permission expansion now filters unresolved stale ids instead of granting/listing them as accessible servers.

Evidence created under `.staticeng/evidences/TASK-2026-06-10-001-fix-mcp-delete-stale-permissions/` with AC mapping, pytest output, ruff output, and diff stat.
