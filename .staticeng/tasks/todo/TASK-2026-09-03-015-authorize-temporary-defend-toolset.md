---
id: TASK-2026-09-03-015-authorize-temporary-defend-toolset
complexity: standard
track: spec
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: Authorize temporary Defend toolset

## Objective

Amend the maintenance contract to permit one temporary one-tool `defend_memory` toolset created and deleted through supported APIs for the diagnostic principal only.

## Acceptance Criteria

- [x] AC-1: Authorize one task-unique temporary toolset containing exactly existing Defend `memory-find`.
- [x] AC-2: Prohibit server/access-group grants, additional tools, direct DB changes, persistent reuse, or name collision.
- [x] AC-3: Require toolset creation before principal grant and deletion after principal/grant/token cleanup on every exit.
- [x] AC-4: Require before/after toolset counts, exact membership digest, and preservation of all non-task MCP resources.
- [x] AC-5: Preserve watchdog, backup, exact-digest, four-hour, rollback, secret, and NAS boundaries.

## Handoff

[Agent Message] From: product_manager To: business_analyst

The supported toolset collection is empty, but an existing Defend MCP server exposes memory-find. PMA authorizes one temporary least-privilege toolset through supported APIs solely for the temporary diagnostic principal and one request. Amend the SCR using TASK-014's exact architecture once available; no runtime mutation now.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary

Amended the approved upstream integration SCR to authorize exactly one task-owned temporary `defend_memory` toolset for the one-run Fedora diagnostic. The amendment freezes server ID `54a0ad17239e9f184882cf47e3ac277c`, canonical upstream tool `find`, and membership digest `e08d6ac35d8ceea4eaaaaccce855a9df910684f3f54cff9cce26797dd33ae6cd`. The toolset must be created before the principal grant and deleted only after complete token, grant, and principal cleanup

### Work Performed

- Replaced the unsupported assumption of an existing `defend_memory` toolset with one supported-API temporary lifecycle
- Required exact preflight server/tool mapping, collision rejection, HTTP 201 creation, collection and ID read-back, and HTTP 202 deletion followed by absence proof
- Limited the toolset to one exact `{server_id, tool_name}` member and prohibited updates, adoption, persistent reuse, extra tools, and every broader permission class
- Added complete toolset, server, user, association, key, membership, and non-task resource baseline and restoration requirements
- Preserved all maintenance watchdog, backup/restore, exact-digest, signature, attestation, two-hour checkpoint, four-hour deadline, rollback, secret, Fedora-only, and NAS-exclusion requirements
- Performed no runtime, host, database, source, service, registry, Fedora, or NAS mutation

### Acceptance Criteria Coverage

- **AC-1: PASS.** The SCR authorizes one exact-name temporary `defend_memory` toolset, uniquely bound by task description, execution correlation, returned ID, and baseline proof, containing only server `54a0ad17239e9f184882cf47e3ac277c` tool `find`
- **AC-2: PASS.** Name collision, reuse, adoption, update, extra members, server/access-group/direct-tool/model/admin/global rights, direct database access, and any unproven-row deletion are explicit stop conditions or prohibitions
- **AC-3: PASS.** The required order is baseline, create and verify toolset, arm cleanup, create and grant principal, one request, then token/session/grant/principal cleanup before toolset deletion on every exit
- **AC-4: PASS.** The SCR requires before/after counts and canonical digests, the exact membership digest, complete pagination, returned-ID absence, and preservation of every non-task MCP and authorization resource
- **AC-5: PASS.** Existing watchdog, backup and isolated restore, exact image and rollback digests, provenance, two-hour checkpoint, four-hour deadline, unconditional rollback, secret handling, Fedora-only, and NAS boundaries remain mandatory

### Documentation Impact

Updated `.staticeng/docs/scrs/SCR-2026-09-01-001-upstream-main-integration.md` as the approved operational source of truth. `.staticeng/docs/scrs/current.md` already lists this SCR as approved and remains correct. No product overview, feature list, architecture, technical, or CodeMap update is required because this is a one-run operational exception and adds no steady-state product behavior

### Open Risks

The supported toolset CRUD and principal grant operations are not transactional, and delete does not remove object-permission references. Execution must preserve exact ordering, retain task ownership by returned ID plus digest, and fail closed on ambiguous create, drift, incomplete pagination, or cleanup mismatch. Any unresolved task identity, grant, toolset, or baseline mismatch is a critical Fedora security incident and blocks release closure

### Recommended Next Step

PMA should accept this amendment and reopen `TASK-2026-09-03-006-diagnose-fedora-candidate-live` for Tech Lead with TASK-014's exact supported API contract. Runtime creation remains prohibited until PMA activates that execution

### Signed Handoff

[Agent Message] From: business_analyst To: product_manager

TASK-015 PASS. SCR `SCR-2026-09-01-001-upstream-main-integration` now authorizes exactly one task-owned temporary `defend_memory` toolset through supported APIs. It must contain only `{"server_id":"54a0ad17239e9f184882cf47e3ac277c","tool_name":"find"}` with canonical SHA-256 `e08d6ac35d8ceea4eaaaaccce855a9df910684f3f54cff9cce26797dd33ae6cd`. Reject every name collision, mismatch, ambiguous create, extra member, update, reuse, and broader server, access-group, direct-tool, model, admin, or global grant. Create and verify the toolset before granting the one temporary principal. On every exit, clear tokens, sessions, grants, and the principal before deleting the toolset by returned ID, then prove all toolset, server, user, association, key, membership, and non-task resource counts and digests equal baseline. All watchdog, backup/restore, exact-digest, provenance, two-hour, four-hour, rollback, secret, Fedora-only, and NAS boundaries remain unchanged. No runtime mutation occurred
