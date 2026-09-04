---
id: TASK-2026-09-03-012-spec-temporary-diagnostic-principal
complexity: standard
track: spec
slice: foundation
status: active
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: Specify temporary diagnostic principal

## Objective

Define a least-privilege, time-bounded Fedora UI principal used only to complete exact-resource DCR and the single maintenance diagnostic request when no existing eligible principal is available.

## Acceptance Criteria

- [x] AC-1: Record PMA authorization to create one temporary local username/password principal through supported administrative APIs, not direct DB writes.
- [x] AC-2: Grant only the minimum existing `defend_memory` toolset permission and no model/admin/team/global privileges beyond login/DCR requirements.
- [x] AC-3: Use generated high-entropy credentials owner-only outside repo/Syncthing/evidence, with no secret logging or command arguments.
- [x] AC-4: Require immediate token revocation/destruction, grant removal, and principal deletion after success, rollback, failure, or four-hour expiry.
- [x] AC-5: Require before/after user/grant counts and non-secret identifiers to prove cleanup; preserve all other users and grants.

## Handoff

[Agent Message] From: product_manager To: business_analyst

No eligible existing username/password principal exists. The user authorizes active Fedora maintenance and wants diagnosis completed. PMA authorizes one temporary least-privilege local UI principal solely for exact-resource DCR and one bounded `defend_memory-find` request. Amend the SCR operational contract without weakening auth, granting broader rights, using direct DB writes, retaining the principal, or touching NAS. Set maximum lifetime to the remaining four-hour maintenance window and mandatory deletion on every exit. Update task/SCR and return signed handoff; no runtime mutation.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary

Amended the approved upstream integration SCR with a one-run temporary diagnostic principal contract. The contract permits exactly one local username/password principal for exact-resource DCR and the single `defend_memory-find` diagnostic request, while making least privilege, owner-only secret handling, unconditional cleanup, four-hour expiry, and before/after restoration proof mandatory

### Work Performed

Recorded PMA authorization and constrained the principal to `internal_user_viewer`, `models=["no-default-models"]`, no memberships or direct grants, no auto-created personal key, and exactly one non-empty object-permission grant to the existing `defend_memory` toolset. Defined supported `/user/new`, `/user/update`, `/login`, DCR, revocation, grant-clear, and `/user/delete` composition; independent cleanup enforcement; 256-bit password and 128-bit username entropy; owner-only tmpfs and inherited-descriptor handling; and secret-free before/after user, effective-grant, association, key, membership, and toolset proof. No source, runtime, host, database, registry, Fedora, or NAS mutation was performed

### Acceptance Criteria Coverage

- **AC-1: PASS.** The SCR records PMA authorization dated 2026-09-04 for one temporary local UI principal and permits only supported administrative/authentication APIs; direct DB, ORM, SQL, container-side application, and repair writes are prohibited
- **AC-2: PASS.** The only non-empty object permission is the resolved existing `defend_memory` toolset ID. The principal is a non-admin viewer with no model access, memberships, access groups, direct MCP server/tool grants, global permissions, or personal key creation
- **AC-3: PASS.** The contract requires CSPRNG credentials with at least 256 password bits and 128 unpredictable username bits, owner-only tmpfs/process/fd handling, and excludes secrets from repo, Syncthing, evidence, arguments, environment, logs, traces, and captures
- **AC-4: PASS.** Cleanup is required immediately after the one request and on every normal, failure, signal, watchdog, rollback, or expiry path. It revokes refresh, destroys every artifact, clears and unlinks grants, deletes session keys when addressable, and deletes the user no later than the remaining four-hour deadline
- **AC-5: PASS.** Baseline and final proof require equal global user and effective `defend_memory` assignment counts, equal non-task association counts/digests, zero task user/grants/keys/memberships/artifacts, unchanged toolset identity/membership, and preservation of every non-task user and grant

### Documentation Impact

Updated `.staticeng/docs/scrs/SCR-2026-09-01-001-upstream-main-integration.md` as the approved operational source of truth. The existing SCR registry remains correct. No product overview, feature list, architecture, technical, or CodeMap update is required because this is a one-run maintenance authorization and adds no steady-state product behavior

### Open Risks

Cleanup depends on supported APIs remaining reachable on either the candidate or restored rollback service. Principal creation is prohibited unless the independent cleanup path is proven and armed first. If cleanup cannot restore baseline, the release remains rejected and Tech Lead must declare a critical Fedora security incident. The API may retain an empty unlinked object-permission storage row, but it may retain no grant-bearing value or effective association; direct database deletion remains prohibited

### Recommended Next Step

PMA should accept this amendment and reopen `TASK-2026-09-03-006-diagnose-fedora-candidate-live` only after Tech Lead incorporates the new pre-creation baseline, exact grant-shape checks, independent cleanup worker, deletion deadline, and final restoration proof into the execution runbook

### Signed Handoff

[Agent Message] From: business_analyst To: product_manager

TASK-012 PASS. SCR `SCR-2026-09-01-001-upstream-main-integration` now authorizes exactly one temporary `internal_user_viewer` on Fedora through supported APIs, solely for S256 DCR at `https://litellm.defend.tech/toolset/defend_memory/lazymcp` and one bounded `defend_memory-find` request. Grant only the existing `defend_memory` toolset, block model access, add no memberships or broader permission, create no personal key, and keep all high-entropy credentials and OAuth artifacts owner-only outside repo, Syncthing, arguments, environment, logs, and evidence. Arm independent cleanup before creation. On every exit, revoke refresh, destroy tokens and local artifacts, clear and unlink every grant, delete task session keys where addressable, and delete the principal immediately, no later than the remaining four-hour deadline. Before/after supported-API proof must restore global user and effective grant counts, preserve all non-task associations and toolset membership, and show zero task identity, grant, key, membership, token, or artifact. If that lifecycle cannot be proved, do not create the principal; if cleanup fails, reject release, roll back, and escalate a critical Fedora security incident. No runtime, database, host, source, registry, or NAS mutation occurred in this specification task
