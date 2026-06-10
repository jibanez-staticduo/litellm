---
id: DISCUSSION-002
title: "Fix LiteLLM MCP server delete stale permission references"
status: closed
summarized_by: business_analyst
source: runtime-transcript
---

# Discussion Summary

## Topic
Fix LiteLLM MCP server deletion so stale permission references do not surface as real servers or break deletion UX.

## Purpose
Capture a reproducible LiteLLM MCP management bug and convert the investigation notes into workflow-ready requirements for implementation and verification.

## Repository Truth Relevant To This Discussion
- The observed issue is in a separate LiteLLM instance on Fedora, accessible via `ssh fedora`, at `home/staticduo/docker/litellm`.
- The current repository context is LiteLLM, but the configured LiteLLM MCP tool available to agents does not point to the affected Fedora LiteLLM instance and must not be used for this investigation or fix.
- Observed LiteLLM package version is `1.88.0`.
- Observed Docker image is `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260608-fix-mcp-null-maps`.
- Affected endpoint is `DELETE /v1/mcp/server/{server_id}`.
- Relevant config is `general_settings.user_mcp_management_mode: restricted`.
- Relevant data tables are `LiteLLM_MCPServerTable`, `LiteLLM_ObjectPermissionTable`, `LiteLLM_TeamTable`, and `LiteLLM_MCPUserCredentials`.

## Facts Established
- The MCP servers UI attempted to delete `server_id=5f303ed9-3916-40e7-b3b7-40d7498b054b`.
- Backend responded `404 Not Found` to `DELETE /v1/mcp/server/5f303ed9-3916-40e7-b3b7-40d7498b054b`.
- That `server_id` does not exist in `LiteLLM_MCPServerTable`.
- The same `server_id` exists in `LiteLLM_ObjectPermissionTable.mcp_servers` for an object permission associated with team `StaticTeam`.
- There are multiple similar stale MCP server references in permissions.
- Current deletion code calls `delete_mcp_server(prisma_client, server_id)`.
- Current `delete_mcp_server` behavior only deletes from `litellm_mcpservertable`.
- The endpoint contains TODOs for deleting from virtual keys and teams, but does not currently clean `LiteLLM_ObjectPermissionTable.mcp_servers` or related MCP user credentials.
- The suspected permission/listing flow expands `object_permission.mcp_servers` without validating that each ID still exists in `LiteLLM_MCPServerTable`.
- Because stale IDs can be exposed by listing/UI flows, the UI may present nonexistent server IDs as deletable MCP servers.
- When deleting a real MCP server, current behavior appears likely to leave orphaned references in `LiteLLM_ObjectPermissionTable`, causing future UX/API errors.

## Requirements Captured
- `DELETE /v1/mcp/server/{server_id}` must delete a real MCP server and consistently clean related references.
- Deleting a real MCP server must remove the `server_id` from `LiteLLM_ObjectPermissionTable.mcp_servers` wherever it appears.
- Deleting a real MCP server must delete associated `LiteLLM_MCPUserCredentials` records.
- Deleting a real MCP server should clean toolset/tool permission references such as `mcp_tool_permissions` when the current model stores the deleted `server_id` there.
- Deletion cleanup should cover permissions for teams, keys, users, organizations, agents, and end-users where those object permissions apply.
- MCP server listing/expansion used by the UI must not expose stale IDs as real deletable servers.
- Permission expansion must not grant access through MCP server IDs that no longer exist in `LiteLLM_MCPServerTable`.
- Backend behavior for deleting a nonexistent `server_id` that is still referenced in permissions must be explicit and UX-safe.
- Backend behavior for deleting a nonexistent, unreferenced `server_id` must return a clear 404 if idempotent cleanup is not applicable.
- Caches or MCP registries must be invalidated after successful deletion cleanup commits.
- Tests must cover deleting an existing MCP server, stale permission cleanup, credential cleanup, listing behavior for stale IDs, stale referenced delete semantics, and stale permissions not granting access.

## Constraints
- Do not use or modify the currently configured LiteLLM MCP tool because it does not target the affected Fedora LiteLLM instance.
- Investigation or reproduction against the affected deployment should use `ssh fedora` and the directory `home/staticduo/docker/litellm` if remote instance access is needed.
- The user provided an existing opencode session ID for the Fedora context: `ses_14e184372ffeBXz62QER3qNtxT`.
- Behavior must account for `general_settings.user_mcp_management_mode: restricted`.
- Deletion cleanup should be transactional to avoid partial deletion and orphaned references.
- Do not silently invent semantics for nonexistent server deletion without a product/technical decision.

## Non-Goals
- Do not operate on the wrong LiteLLM instance through the available LiteLLM MCP integration.
- Do not only patch the UI; backend cleanup and permission correctness are required.
- Do not rely solely on deleting from `LiteLLM_MCPServerTable`; related permission and credential cleanup is part of the expected behavior.
- Do not allow stale permission references to continue granting MCP access or appearing as valid servers.

## Decisions Made
- The issue should be fixed in backend deletion and listing/permission expansion behavior, not treated as only a data-cleanup incident.
- Stale references in `LiteLLM_ObjectPermissionTable.mcp_servers` must be cleaned when deleting MCP servers.
- Associated MCP user credentials must be removed when their MCP server is deleted.
- Listing or expansion should compare permission references against `LiteLLM_MCPServerTable` and filter or mark stale references so the UI does not present them as real servers.
- A semantic decision is required for nonexistent but referenced delete requests: preferred direction is idempotent cleanup with `200`/`202` plus warning; alternative is a clear error after cleanup rules are defined.

## Assumptions
- The affected code path exists in the local LiteLLM repository and can be updated from this workspace or coordinated with the Fedora working copy.
- `LiteLLM_ObjectPermissionTable.mcp_servers` stores MCP server IDs in an array-like structure that can contain stale IDs.
- Toolset/tool permission data may include MCP server IDs, but the exact current schema/use must be confirmed before implementation.
- Cache or registry invalidation hooks exist or can be identified in the MCP management code path.
- Team `StaticTeam` is an observed example, not the only affected object permission scope.

## Open Questions
- What final HTTP semantics should `DELETE /v1/mcp/server/{server_id}` use when the ID does not exist in `LiteLLM_MCPServerTable` but is still referenced in permissions: `200`, `202`, or an error response after cleanup?
- Should stale references be silently filtered from listing results, returned with a stale marker for admin cleanup, or exposed through a dedicated cleanup/status endpoint?
- Which exact object permission scopes currently store `mcp_servers` and must be updated: teams, keys, users, organizations, agents, end-users, or additional object types?
- Which exact tables/fields store `mcp_tool_permissions` or toolset references to MCP server IDs in the current schema?
- What cache/registry invalidation functions must run after MCP server deletion and permission cleanup?
- Should a migration or one-off cleanup task be provided for already-stale production data?

## Risks Or Concerns
- Partial deletion without a transaction could delete the server while leaving permissions and credentials inconsistent.
- Cleaning only team permissions may miss keys, users, organizations, agents, or end-users and leave stale access paths.
- Filtering stale IDs only in the UI would hide symptoms but leave backend access-control inconsistency.
- Incorrect idempotent delete semantics could hide user mistakes or make debugging real missing-server errors harder.
- Directly using the wrong LiteLLM MCP integration could modify or inspect the wrong environment.
- Schema assumptions around tool permissions/toolsets may be wrong and require code inspection before implementation.

## Referenced Files Or Areas
- `DELETE /v1/mcp/server/{server_id}` MCP server delete endpoint.
- MCP server listing and permission expansion logic used by the UI.
- `delete_mcp_server(prisma_client, server_id)` helper/function.
- `litellm_mcpservertable` / `LiteLLM_MCPServerTable`.
- `LiteLLM_ObjectPermissionTable.mcp_servers`.
- `LiteLLM_TeamTable`.
- `LiteLLM_MCPUserCredentials`.
- Tool permission/toolset storage related to `mcp_tool_permissions`.
- MCP cache or registry invalidation code paths.
- Fedora deployment path: `home/staticduo/docker/litellm`.
- Fedora opencode session: `ses_14e184372ffeBXz62QER3qNtxT`.

## Recommended Workflow Next Step
- assigned_to: tech_lead
- why: Confirm deletion semantics and schema impact, then create or assign an implementation task with acceptance criteria covering transactional cleanup, stale listing behavior, credential cleanup, tests, and safe handling of the Fedora instance constraint.
