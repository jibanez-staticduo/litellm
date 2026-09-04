---
id: TASK-2026-09-03-017-fix-internal-user-login
complexity: standard
track: implementation
slice: logic
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: developer
handoff_from: product_manager
reopened_count: 2
---

# Task: Fix internal-user login

## Objective

Apply the smallest approved source or harness correction enabling the temporary least-privilege principal to log in exactly once through supported behavior.

## Acceptance Criteria

- [x] AC-1: Correct only the proven login boundary without weakening authentication.
- [x] AC-2: Add mutation-sensitive create/update/login/incorrect-password/identity/cleanup regressions.
- [x] AC-3: Full auth/proxy/source/build/security qualification passes.
- [x] AC-4: Tech Lead reviews, commits, and pushes; no source change requires rebuilding or signing, and no production mutation occurred.

## Handoff

[Agent Message] From: product_manager To: developer

TASK-016 proves no runtime source defect: database-backed `/login` requires case-insensitive `user_email`, while password update is keyed by returned `user_id`. Add a focused disposable lifecycle regression that creates both a unique generated email and opaque ID, updates password by returned ID, logs in by email, rejects ID and wrong-password login, verifies least privilege, and deletes/restores baseline. Update the maintenance harness/task contract to use email only for login; do not broaden authentication or change runtime source. Run auth/proxy/source/static gates and return for Tech Lead commit/push. No image rebuild, deployment, Fedora/NAS mutation.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary

PASS for implementation and ready for Tech Lead review. Added a focused live database-backed lifecycle regression and updated the maintenance contract to use `user_email` for local database login while retaining returned `user_id` for update, grants, cleanup, and baseline proof. Runtime source is unchanged

### Work Performed

Extended the typed e2e transport with form-post support that captures only status, redirect location, and the UI token cookie needed to validate identity. Extended management test models/client for password-only user update and least-privilege read-back. Added one lifecycle regression covering generated distinct identities, supported create/update/login behavior, negative credentials, least privilege, strict deletion, baseline restoration, and post-delete rejection. Added its coverage-registry cell and corrected the governing SCR plus TASK-006 maintenance harness wording

Ran the regression against a fresh labelled disposable PostgreSQL database after applying all 161 migrations and a local source proxy. Ran mapped auth/login/management tests, e2e harness and registry tests, raw-HTTP confinement, Ruff, basedpyright, and StaticEng validation. Removed all disposable resources and temporary files

### Acceptance Criteria Coverage

- **AC-1: PASS.** Authentication remains email-only for database users; no runtime or authentication source changed
- **AC-2: PASS.** The live lifecycle regression is mutation-sensitive across identity mapping, password verification, update scope, least privilege, deletion, and baseline restoration
- **AC-3: PASS.** Focused live, auth, proxy, management, e2e source, type, lint, coverage, and StaticEng gates pass
- **AC-4: READY FOR TECH LEAD.** Developer made no commit, push, build, signing, publication, deployment, Fedora, or NAS change

### Documentation Impact

Updated the approved SCR and TASK-006 operational harness contract. No steady-state product or architecture documentation and no CodeMap update is required because runtime behavior and source navigation remain unchanged

### Open Risks

The new regression intentionally does not prove or authorize login by user ID. It requires a migrated disposable database and live proxy, as expected for the existing e2e harness

### Recommended Next Step

Tech Lead reviews and owns commit/push. PMA may then reopen TASK-006 with the corrected email-login procedure and all prior safety boundaries intact

### Signed Handoff

[Agent Message] From: developer To: product_manager

TASK-017 PASS FOR TECH LEAD REVIEW. The focused disposable DB lifecycle regression and email-login maintenance correction are complete. Email success, ID/wrong-password failure, least privilege, deletion, baseline restoration, mapped source tests, e2e gates, type/lint, and StaticEng validation pass. Runtime auth source is unchanged; no rebuild, commit, push, deploy, Fedora, or NAS action occurred

## Tech Lead: Post Implementation Expectations

### Summary

REJECT. The runtime-auth boundary and email-versus-ID lifecycle are correct, and the mapped gates pass, but AC-2 is not mutation-sensitive for the generated UI session key or least-privilege enforcement

### Work Performed

Reviewed the complete task, SCR correction, maintenance-harness correction, changed e2e transport/models/client/test, coverage mapping, and evidence. Confirmed that no runtime source changed. Reran the mapped auth, login, internal-user, e2e harness, coverage-registry, raw-HTTP confinement, Ruff, basedpyright, and StaticEng gates

### Acceptance Criteria Coverage

- **AC-1: PASS.** The diff changes tests, harness support, and governed documentation only. Database login remains email-only, and management/update/cleanup remain keyed by returned user ID
- **AC-2: FAIL.** The test proves user deletion and post-delete credential rejection, but never proves the generated UI session key is absent or unusable after deletion. It also checks least-privilege metadata and JWT claims without exercising an operation that an elevated session would incorrectly allow
- **AC-3: PASS FOR MAPPED REVIEW GATES.** Fresh review runs passed 139 auth/login/internal-user tests, 27 e2e harness/registry tests, strict registry collection, raw-HTTP confinement, Ruff, basedpyright, and StaticEng validation
- **AC-4: BLOCKED.** No close, commit, or push is authorized while AC-2 remains open

### Documentation Impact

The SCR and TASK-006 wording correctly preserve the email-versus-ID boundary. No additional steady-state product, architecture, or CodeMap update is required for this rejection

### Open Risks

A regression that leaves the generated dashboard session key usable after `/user/delete`, or mints an over-privileged session key while retaining viewer claims, would pass the current lifecycle test

### Recommended Next Step

PMA should return TASK-017 to Developer for the smallest same-task test correction: retain the generated session key, prove it is rejected after user deletion, and add one enforced least-privilege denial using that session. Then rerun the live disposable lifecycle and mapped gates for Tech Lead rereview

## Reopen History

### Reopen 1 - Session cleanup and enforced least privilege

Retain the generated session key, use it to attempt one forbidden management or model operation and require denial, then delete the user and prove that exact session key is rejected/absent. Correct evidence claims and rerun the disposable lifecycle plus mapped gates. Do not change runtime authentication.

### Reopen 2 - Prove cache-expiry revocation

Tech Lead proved post-delete `/user/info` HTTP 404 means cached bearer admission still succeeds before missing-user handling. Preserve authoritative `/key/info` absence and zero-row proof, then poll a harmless retained-key admission request only through the documented authorization-cache expiry and require a true authentication denial. Record bounded expiry duration and correct evidence semantics. If expiry cannot be bounded safely within the maintenance contract, stop and route an explicit runtime cache-invalidation fix rather than weakening the requirement.

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

TASK-017 REJECTED. Runtime auth is unchanged, email login with returned-ID management is correct, wrong-password and ID login reject, and mapped gates pass. The lifecycle regression does not prove generated session-key cleanup or enforce least privilege behavior, so AC-2 remains open. No commit or push occurred

## Developer Reopen 1: Post Implementation Expectations

### Summary

PASS for Reopen 1 and ready for Tech Lead rereview. The regression now retains the generated UI session key, proves enforced viewer denial before deletion, and proves exact key absence plus loss of its user binding after `/user/delete`

### Work Performed

Added typed result-returning management helpers for `/user/info`, `/user/list`, and `/key/info`. The lifecycle test proves the retained session key exists, permits self-info, and is denied 403 on proxy-admin-only user listing. After strict user deletion it requires exact-key `/key/info` 404, deleted-user `/user/info` 404 under that same key, zero task-owned user/key database rows, restored baseline, and failed email/password login

Ran the final regression against the disposable migrated PostgreSQL and local source proxy, then reran 139 mapped auth/login/management tests, 27 harness tests, strict coverage, raw-HTTP confinement, Ruff, basedpyright, and StaticEng validation. Removed all disposable resources and temporary artifacts

### Acceptance Criteria Coverage

- **AC-1: PASS.** Runtime authentication and source remain unchanged
- **AC-2: PASS.** Enforced least privilege and exact generated-session cleanup are now mutation-sensitive
- **AC-3: PASS.** All requested live, mapped, harness, lint, type, and static gates pass
- **AC-4: READY FOR TECH LEAD REREVIEW.** No commit, push, build, signing, publication, deployment, Fedora, or NAS action occurred

### Documentation Impact

Corrected evidence to distinguish metadata checks from enforced denial and to identify the exact authoritative session-key cleanup proofs. No SCR, product, architecture, or CodeMap change is needed for Reopen 1

### Open Risks

The authorization cache may retain a deleted key's prior 403 response class briefly. Authoritative `/key/info`, deleted-user resolution, and direct database absence all prove the key cannot be used as a surviving user session

### Recommended Next Step

Tech Lead should rereview AC-2 and own commit/push if approved

### Signed Handoff

[Agent Message] From: developer To: product_manager

TASK-017 REOPEN 1 PASS FOR TECH LEAD REREVIEW. Retained-session least-privilege denial, exact-key deletion, deleted-user binding failure, zero task user/key rows, baseline restoration, and all requested gates pass. Runtime auth is unchanged and no prohibited action occurred

## Tech Lead Reopen 1: Post Implementation Expectations

### Summary

REJECT. Session-key existence, enforced viewer denial, database deletion, and mapped gates pass, but the retained key is not proven unusable after deletion. The post-delete `/user/info` HTTP 404 proves the cached key still authenticates and reaches the endpoint handler

### Work Performed

Rereviewed the exact Reopen 1 diff, lifecycle assertions, cache behavior, evidence, task and SCR boundaries. Confirmed no runtime source changed. Reran the 139 mapped auth/login/internal-user tests, 27 e2e harness/registry tests, strict coverage collection, raw-HTTP confinement, Ruff, basedpyright, and StaticEng validation

### Acceptance Criteria Coverage

- **AC-1: PASS.** Only tests, harness support, coverage mapping, SCR wording, tasks, and evidence changed. Runtime authentication remains unchanged
- **AC-2: FAIL.** The retained session key exists before deletion and receives the expected 403 on proxy-admin-only `/user/list`. After deletion, master-authenticated `/key/info` proves the database row is absent, but retained-key `/user/info` returns 404 rather than 401/403. That response is generated only after bearer authentication and self-access authorization succeed, so it proves the cached deleted key remains usable for an allowed management request. Exact-key unusability and the SCR's negative admission requirement are not satisfied
- **AC-3: PASS FOR MAPPED REVIEW GATES.** Fresh runs passed all requested mapped, harness, registry, raw-HTTP, lint, type, and static gates
- **AC-4: BLOCKED.** No close, commit, or push is authorized while AC-2 remains open

### Documentation Impact

No further SCR, product, architecture, or CodeMap change is needed for this rejection. Evidence must stop describing a retained-key 404 as inability to use the key

### Open Risks

The deleted session key remains admitted from authorization cache until expiry. Database absence alone does not prove credential revocation at the request boundary

### Recommended Next Step

PMA should return the same task to Developer. Poll a harmless retained-key request through cache expiry and require an authentication denial, while separately retaining authoritative `/key/info` 404 and zero database rows. If immediate revocation is required instead, stop and route a separately approved runtime fix because this task prohibits runtime-auth changes

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

TASK-017 REOPEN 1 REJECTED. Pre-delete key existence and viewer denial pass, and post-delete database absence is proven. Retained-key `/user/info` returns handler-level 404, proving cached authentication still succeeds rather than proving the key unusable. AC-2 remains open. No commit or push occurred

## Developer Reopen 2: Post Implementation Expectations

### Summary

PASS for Reopen 2 and ready for Tech Lead rereview. The effective disposable auth-cache TTL is 60 seconds. The regression preserves immediate authoritative deletion proof, classifies post-delete handler 404 correctly, and requires true retained-key 401 denial within the TTL plus a bounded 10-second margin

### Work Performed

Traced `UserAPIKeyCacheTTLEnum`, `user_api_key_cache` initialization, `general_settings.user_api_key_cache_ttl`, `IdentityStore`, `_cache_key_object`, `_cache_management_object`, and `get_management_object_ttl`. Added an e2e TTL setting defaulted to the documented 60 seconds and a bounded at-most-once-per-second poll of harmless `/user/list` under the retained key

Ran the complete disposable lifecycle. Immediately after delete, exact-key `/key/info` returned 404 and direct database checks showed zero task users/keys, while retained-key `/user/info` returned handler 404 as expected during cached admission. The harmless admission probe reached true 401 after 60.50 seconds, inside the 70-second test bound

### Acceptance Criteria Coverage

- **AC-1: PASS.** Runtime authentication and source remain unchanged
- **AC-2: PASS.** Exact storage deletion, handler semantics, bounded cache expiry, and true post-expiry authentication denial are mutation-sensitive
- **AC-3: PASS.** Live lifecycle, mapped auth/proxy/management, harness, registry, raw-HTTP, lint, type, and StaticEng gates pass
- **AC-4: READY FOR TECH LEAD REREVIEW.** No commit, push, build, signing, publication, deployment, Fedora, or NAS action occurred

### Documentation Impact

Corrected evidence semantics and documented the existing cache configuration/TTL path. No SCR, runtime, product, architecture, or CodeMap change is required

### Open Risks

Deletion revocation is not immediate in the no-Redis disposable runtime; cached bearer admission lasts up to the configured 60-second TTL. Requiring immediate invalidation would need a separately authorized runtime change

### Recommended Next Step

Tech Lead should rereview the bounded expiry and true-denial proof, then own commit/push if approved

### Signed Handoff

[Agent Message] From: developer To: product_manager

TASK-017 REOPEN 2 PASS FOR TECH LEAD REREVIEW. The documented/effective 60-second auth-cache TTL is now tested end to end. Immediate DB/key absence, handler-level 404 semantics, true 401 after 60.50 seconds, baseline restoration, and all requested gates pass. Runtime auth is unchanged and no prohibited action occurred

## Tech Lead Reopen 2: Post Implementation Expectations

### Summary

PASS and closed. Reopen 2 proves the exact disposable runtime's 60-second effective authorization-cache TTL, immediate storage cleanup, correct cached-handler semantics, and true retained-key authentication denial within a bounded 70-second window. Runtime authentication is unchanged

### Work Performed

Reviewed the complete task, SCR, maintenance correction, changed harness and exact lifecycle. Traced the default `UserAPIKeyCacheTTLEnum` value, cache initialization, configured override path, cache-first `IdentityStore`, and management-object TTL write. Confirmed the disposable no-Redis runtime has no override and therefore uses 60 seconds. Reran all mapped auth, login, internal-user, e2e harness, coverage, raw-HTTP, lint, type, and StaticEng gates

### Acceptance Criteria Coverage

- **AC-1: PASS.** No path under `litellm/` changed. Database login remains email-only while password update, grants, baseline checks, and cleanup retain returned-user-ID identity
- **AC-2: PASS.** The live regression covers distinct email and ID, password-only update, ID and wrong-password rejection, email login, stored and enforced least privilege, exact session-key existence, immediate user/key storage absence, cached handler-level 404, bounded cache expiry, true 401 denial, and restored user/key baseline
- **AC-3: PASS.** The live regression passed in 61.07 seconds with denial at 60.50 seconds. Fresh review runs passed 139 mapped auth/login/internal-user tests, 27 e2e harness/registry tests, strict coverage collection, raw-HTTP confinement, Ruff, basedpyright, and StaticEng validation
- **AC-4: PASS.** Tech Lead approved closure and owns the required non-force push. No source change requires image rebuild or signing, and no image, deployment, Fedora, or NAS action occurred

### Documentation Impact

The SCR and TASK-006 maintenance correction already express the email-versus-ID contract. No product, architecture, technical, or CodeMap update is required because runtime behavior and source navigation did not change

### Open Risks

Revocation after `/user/delete` alone is storage-immediate but cache-bounded. The maintenance cleanup remains compatible because its existing SCR requires deleting a separately addressable UI session key through the supported key API and destroying client-held auth artifacts immediately. The 60-second expiry proof is a bounded fallback, not authorization to retain or reuse a deleted credential during maintenance

### Recommended Next Step

PMA may reopen TASK-006 under its existing cleanup, watchdog, one-request, rollback, deadline, secret-handling, Fedora-only, and NAS-exclusion boundaries

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

TASK-017 REOPEN 2 PASS AND CLOSED. Exact session-key existence, viewer denial, immediate storage absence, cached handler 404, true 401 at 60.50 seconds within the documented 70-second bound, baseline restoration, and mapped gates pass. Runtime auth is unchanged. Maintenance must still explicitly delete the separately addressable UI key and destroy client auth artifacts immediately; cache expiry is fallback proof only
