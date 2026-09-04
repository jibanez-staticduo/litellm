---
id: TASK-2026-09-03-006-diagnose-fedora-candidate-live
complexity: complex
track: implementation
slice: qa
status: blocked
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-012-release-upstream-main-fedora
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 6
---

# Task: Diagnose Fedora candidate live

## Objective

Deploy the exact signed candidate during the authorized maintenance window, reproduce and root-cause the `defend_memory-find` timeout and unhealthy transition, apply only governed corrections, and leave Fedora either fully verified on an approved exact digest or safely rolled back.

## Acceptance Criteria

- [ ] AC-1: Fresh protected backup/restore verification, baseline, exact candidate/signature/attestation, and rollback unit pass before deployment.
- [ ] AC-2: Reproduce the timeout with correlated timestamps and bounded observability across LiteLLM health/event loop/DB pool/MCP transport and the upstream `defend` service without exposing secrets or payloads.
- [ ] AC-3: Identify root cause and classify whether configuration, healthcheck, timeout, connection pool, route/auth, upstream MCP, or candidate code is responsible.
- [ ] AC-4: Any correction uses the smallest governed task/review/build path; no ad-hoc untracked production patch is accepted.
- [ ] AC-5: Exact corrected or unchanged candidate passes health, models, Chat/Responses, MCP REST, LazyMCP discovery/challenges/DCR/audience, authorized real tools, clean logs, resource stability, and 900-second soak.
- [ ] AC-6: NAS remains untouched; Fedora rollback executes on stop conditions or window expiry.
- [ ] AC-7: Complete secret-free Evidence Packet and workflow closure are produced.

## Handoff

[Agent Message] From: product_manager To: tech_lead

The SCR maintenance amendment and TASK-007 diagnostic runbook are complete. Read them fully. Prior kernel evidence proves the candidate reached about 100.3 GiB anonymous RSS and was globally OOM-killed. Create a new fresh backup/isolated restore and exact rollback unit. Arm the one-second memory/health watcher and automatic rollback thresholds before selector mutation. Deploy the exact signed candidate, reproduce exactly one `defend_memory-find` call with concurrency one and 75-second client deadline, and capture bounded cgroup/process/health/DB/Redis/LazyMCP/upstream defend evidence without payloads or secrets. Roll back immediately at thresholds, data/security risk, or insufficient control. If root cause requires code/config correction, stop after rollback and return an exact governed implementation recommendation; do not patch production ad hoc. Leave Fedora healthy and NAS untouched.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

### Summary

REJECT candidate and PASS rollback. Fresh backup/isolated restore, identity/signature/attestation, rollback, and watchdog gates passed. The exact candidate deployed and remained healthy with bounded memory, but the required request was not sent because Fedora had no protected exact-audience DCR bearer. The client harness failed closed and automatic rollback restored the exact prior digest

### Work Performed

- Created the fresh owner-only database backup/checksum/list and verified it through an isolated exact-image restore
- Armed independent memory, health, and dependency samplers before changing the selector
- Deployed only the exact signed candidate by changing `LITELLM_IMAGE` and recreating only `litellm --no-deps`
- Rejected use of a legacy API key as a substitute for the required exact-audience bearer
- Automatically rolled back without sending the candidate request and verified exact rollback health, protected state, dependencies, migrations, MCP initialize, and real tool behavior

### Acceptance Criteria Coverage

- **AC-1: PASS.** Every fresh pre-deployment safety and identity gate passed
- **AC-2: FAIL.** Observability was active, but no authorized candidate request was sent
- **AC-3: PARTIAL.** Historical global OOM is candidate-process resource exhaustion; exact allocation phase remains unknown
- **AC-4: PASS.** No ad-hoc production correction occurred
- **AC-5: FAIL.** Candidate real-tool, full final gates, and soak did not run
- **AC-6: PASS.** Exact rollback passed and NAS remained untouched
- **AC-7: PASS FOR FAILED OUTCOME.** Evidence and workflow records are complete and secret-free

### Documentation Impact

No steady-state product, architecture, technical, or CodeMap documentation is required because no runtime behavior or maintained source changed

### Open Risks

The candidate remains blocked. The exact allocation site is unproven, and any retry still requires the same automatic watchdog because Fedora Compose has no cgroup memory ceiling

### Recommended Next Step

PMA should create an exact-audience credential-preparation task using the existing DCR flow, then reopen this task for one fresh protected retry. Do not patch production or touch NAS

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT CANDIDATE; VERIFIED ROLLBACK PASS. Preflight and protected deployment controls passed, but the required exact-audience bearer was unavailable, so no candidate tool request was sent. Automatic rollback restored the exact prior digest, and Fedora passes health, migrations, protected-state, dependency, MCP initialize, and real-tool verification. NAS was untouched. Route a governed exact-audience credential-preparation task before reopening TASK-006

## Reopen History

### Reopen 1 - Candidate-live DCR bootstrap

TASK-009 resolves the circular prerequisite: the rollback image cannot mint a candidate-only token, so deploy under the already armed watcher, complete S256 PKCE on the candidate with the existing authorized principal, enforce the T+7-minute cutoff, prove exact and cross-audience behavior, immediately execute one bounded real-tool request, destroy all credential artifacts, and continue diagnosis or rollback. Create a fresh backup/restore and rollback unit again. Follow TASK-009 exactly; no credential substitution or ad-hoc patch.

### Reopen 2 - Browserless authorized-principal bootstrap

The user confirms no Agent Jake/browser automation is available and explicitly authorizes the Fedora maintenance investigation. TASK-010 proves the candidate supports a browserless normal `/login` session followed by public S256 PKCE DCR and deliberate consent. PMA authorizes use of one existing username/password Fedora UI principal only if it is already configured and currently authorized for `defend_memory`; secrets must be consumed from owner-only local files or inherited descriptors without printing, copying to evidence, or entering command arguments. PMA explicitly approves the single exact-resource `/authorize/complete` consent POST. Keep the watchdog armed across login, DCR, audience tests, one diagnostic call, and cleanup. Enforce T+7, destroy all cookie/token/code/verifier/client artifacts, and capture TASK-011's nested-call counters: at most one embedding, three reranks, zero nested LazyMCP, and complete cancellation drain within 15 seconds. If no qualifying principal exists or any bound is exceeded, roll back without substitution or a second request.

### Reopen 3 - Temporary least-privilege diagnostic principal

TASK-012 amends the SCR and authorizes exactly one temporary `internal_user_viewer` because no eligible existing principal exists. Before any creation, prove supported create/grant/remove/delete APIs and arm an independent cleanup worker. Capture baseline non-secret user/key/membership/grant counts and existing `defend_memory` toolset membership. Create high-entropy credentials owner-only outside repository/Syncthing, block model access, grant only exact existing `defend_memory`, and create no team/org/global/admin membership. Then follow TASK-010 PKCE and TASK-011 instrumentation exactly. On every exit: revoke refresh/client material where supported, destroy access/cookie/verifier/code/password artifacts, remove exact grant, delete principal and any key/session/membership, and prove baseline restoration through supported APIs. Any cleanup mismatch is a critical stop requiring candidate rollback and explicit incident evidence.

### Reopen 4 - Two-step supported principal transaction

TASK-013 authorizes the exact supported sequence required by the live API: arm cleanup first; `/user/new` creates only the least-privilege non-login principal; the immediately following request is `/user/update` setting only the generated password; then verify unchanged least-privilege state and first login. No intervening request, grant, key, membership, login, or DCR action is allowed. Any update or verification failure deletes the principal, proves baseline restoration, and stops before candidate use. All Reopen 3 DCR, watchdog, one-call, cleanup, rollback, four-hour and NAS boundaries remain unchanged.

### Reopen 5 - Temporary one-tool Defend toolset

TASK-014 and TASK-015 authorize one task-owned temporary toolset through supported APIs containing exactly `{"server_id":"54a0ad17239e9f184882cf47e3ac277c","tool_name":"find"}` with canonical SHA-256 `e08d6ac35d8ceea4eaaaaccce855a9df910684f3f54cff9cce26797dd33ae6cd`. Reject name collisions, extra members, updates, reuse, ambiguity, or broader grants. Create and exact-read-back the toolset before granting the temporary principal. On every exit, destroy tokens/sessions, remove the principal grant, delete the principal and related objects, then delete the toolset by returned ID and prove all baseline counts/digests restored. All prior backup, watchdog, DCR, one-call, memory-counter, rollback, deadline, secret and NAS boundaries remain mandatory.

### Reopen 6 - Correct email login and explicit key cleanup

TASK-016/017 prove the supported lifecycle: create unique `user_email` plus opaque `user_id`, set password by returned ID, and submit the email in `/login`'s `username` field. Preserve ID for management/cleanup only. After use, explicitly delete the separately addressable UI key before deleting the principal, destroy all client-held cookie/token/code/verifier/password artifacts immediately, and never retain/poll/reuse the credential in maintenance. Verify storage absence and baseline restoration; the observed 60-second cache expiry is fallback evidence only, not permission to delay cleanup. All prior toolset, watchdog, one-call, rollback and deadline constraints remain mandatory.

### Reopen 2 Result

BLOCKED before deployment. The only discovered owner-only username/password file has a valid protected shape but matches zero existing Fedora database users and does not match the configured proxy-admin pair. No qualifying existing `defend_memory`-authorized principal can be proven, so PMA's explicit stop condition applies. No backup, watchdog, selector mutation, login, DCR, consent, token, diagnostic request, rollback, or NAS action occurred. Fedora remains healthy on the exact prior digest with 161 completed migrations

[Agent Message] From: tech_lead To: product_manager

TASK-006 REOPEN 2 BLOCKED PRE-DEPLOYMENT. Secret-safe checks found no qualifying existing username/password principal: the only owner-only credential file matches neither an existing Fedora database user nor the configured UI administrator. Per the handoff, I did not substitute credentials or deploy the candidate. Fedora remains healthy on exact rollback digest with readiness/liveliness 200, restart 0, OOM false, and 161 migrations; no auth artifacts or NAS action exist. The secret owner must provide an already authorized existing principal through owner-only files or inherited descriptors before another reopen

### Reopen 3 Result

BLOCKED before principal creation and deployment. Fresh candidate, rollback, and live OpenAPI contract checks prove `/user/new` does not accept `password`; `NewUserRequest` drops it. `/user/update` can set a password, but using it as a follow-up would violate TASK-012's atomic password-backed creation gate and no-repair-before-use requirement. No principal, grant, key, membership, login, DCR, consent, token, request, selector change, rollback, or NAS action occurred. Fedora remains healthy on the exact prior digest

[Agent Message] From: tech_lead To: product_manager

TASK-006 REOPEN 3 BLOCKED PRE-CREATION. The supported API contract cannot perform the lifecycle authorized by TASK-012: `/user/new` has no password field in candidate, rollback, or live OpenAPI, and drops any supplied password. A separate `/user/update` can set it but is not authorized as follow-up repair. No production mutation or diagnostic request occurred; Fedora remains healthy on exact rollback and NAS is untouched. Amend the SCR for an explicitly verified two-step create-then-password transaction, or qualify a candidate that supports atomic password creation

### Reopen 4 Result

BLOCKED before watchdog, deployment, or principal creation. Fresh protected backup/isolated restore, rollback unit, candidate identity, signature, and attestations passed. The supported admin toolset read API returned HTTP 200 with zero toolsets, so the required existing `defend_memory` toolset ID and membership digest could not be resolved. Per TASK-012/013, no principal or substitute/broader grant was created. Fedora remained healthy on exact rollback; all disposable resources and task auth paths are absent; NAS was untouched

[Agent Message] From: tech_lead To: product_manager

TASK-006 REOPEN 4 BLOCKED AT EXISTING-TOOLSET BASELINE. Fresh backup/isolated restore, rollback, identity, signature, and attestation gates passed, but supported `GET /v1/mcp/toolset` returns an empty collection. There is no existing `defend_memory` toolset to grant under TASK-012/013. I did not create a toolset, infer an ID, broaden permissions, create the principal, deploy the candidate, or send a request. Fedora remains healthy on exact rollback, cleanup state is zero, and NAS is untouched. Route a governed toolset creation/configuration task or amend the grant contract after architecture/security review

### Reopen 5 Result

BLOCKED at first login before watchdog activation or candidate deployment. Fresh backup/restore, rollback, provenance, exact one-tool toolset create/read-back, cleanup arming, strict two-step principal transaction, and least-privilege read-back passed. The generated principal's first normal `/login` returned HTTP 401. No retry or repair occurred. Cleanup cleared/deleted the principal first, deleted the task-owned toolset last, restored baseline counts, destroyed all auth artifacts, and stopped the deadline worker. No DCR or diagnostic request was sent. Fedora remains healthy on exact rollback and NAS is untouched

[Agent Message] From: tech_lead To: product_manager

TASK-006 REOPEN 5 BLOCKED AT FIRST LOGIN. The exact toolset and strict two-step principal transaction passed, but the first generated-credential `/login` returned 401. I did not retry, repair, deploy the candidate, or send DCR/MCP requests. Supported cleanup removed the grant/principal before the toolset, restored the empty-toolset baseline, and destroyed artifacts. Fedora is healthy on exact rollback; NAS is untouched. Route an isolated authentication-contract investigation/regression for local users created by `/user/new` plus password-only `/user/update` before another production reopen

### Maintenance Harness Correction

TASK-016 proved that local database authentication resolves only case-insensitive `user_email`. On the next authorized reopen, generate distinct opaque `user_id` and unique non-routable `user_email` values, include both in `/user/new`, keep the immediate password-only `/user/update` and all grant/cleanup/baseline operations keyed by the returned `user_id`, and send only the exact generated `user_email` in `/login` form field `username`. Do not retry with `user_id`, broaden authentication, or change any other Reopen 3 through 5 boundary

### Reopen 6 Result

BLOCKED after successful corrected email login but before watchdog or candidate deployment. Fresh backup/restore, rollback, provenance, exact one-tool toolset, strict principal transaction, least-privilege read-back, email login, and UI-key capture passed. The task-local client failed when it attempted to pickle Python's lock-bearing `CookieJar`. No retry, DCR, consent, token, audience test, or diagnostic request occurred. Cleanup explicitly requested UI-key deletion, then cleared/deleted the principal and deleted the toolset last; counts returned to zero and all artifacts were destroyed. Fedora remains healthy on exact rollback; NAS is untouched

[Agent Message] From: tech_lead To: product_manager

TASK-006 REOPEN 6 BLOCKED BY MAINTENANCE CLIENT ARTIFACT HANDLING. Correct email login and explicit UI-key capture succeeded, proving the product auth correction. Before DCR, the task client tried to pickle `CookieJar` and failed on its internal `RLock`. I did not retry or deploy the candidate. Armed cleanup explicitly requested UI-key deletion, removed grant/principal before toolset, restored baseline, and destroyed artifacts. Fedora is healthy on exact rollback; NAS is untouched. Validate a single-process session or Mozilla/LWP cookie-jar harness in isolation before another reopen
