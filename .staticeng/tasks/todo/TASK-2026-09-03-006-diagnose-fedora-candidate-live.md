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
reopened_count: 8
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

### Reopen 7 - Direct functional administrator probe

TASK-2026-09-04-001 authorizes exactly one aggregate LazyMCP `defend_memory-find` request using the existing Fedora administrator API credential only in diagnostic-client process memory from its owner-only source. For this attempt only, do not create temporary toolset, principal, grant, login, or DCR artifacts. Fresh backup/isolated restore, exact rollback, signed candidate identity, one-second watchdog, memory thresholds, at most one embedding and three reranks, zero nested LazyMCP, 15-second drain, concurrency one, 75-second deadline, no retry/fallback/second request, and four-hour/NAS boundaries remain mandatory. Any non-success triggers immediate exact rollback. A bounded success proceeds directly to all full Fedora gates and the continuous 900-second soak.

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

### Reopen 7 Result

BLOCKED before candidate deployment and credential use. Fresh backup/isolated restore, exact rollback, Compose delta, candidate identity, signature, and attestations passed. The generated one-second watchdog exited on a shell syntax error during its mandatory proving period, so observability/control was not armed and deployment was prohibited. No administrator credential or LazyMCP request was used. Disposable resources, rendered configuration, and active pointer were removed. Fedora remains healthy on exact rollback and NAS is untouched

[Agent Message] From: tech_lead To: product_manager

TASK-006 REOPEN 7 BLOCKED BY WATCHDOG HARNESS SYNTAX. Pre-deployment safety/provenance passed, but the generated watchdog used invalid compact shell syntax and exited before producing samples. Per the control-loss gate I did not deploy the candidate or consume the admin credential; zero diagnostic requests were sent. Fedora remains healthy on exact rollback, cleanup is complete, and NAS is untouched. Validate the watcher with `bash -n` and a 30-sample dry run outside production before another authorization

### Reopen 7 Direct Probe Retry Authorization

TASK-2026-09-04-002 Reopen 3 closes the watchdog blocker. Tech Lead independently verified the generated fail-closed harness, final-30 maximum baseline, exact candidate manifest/config/source, mandatory prerequisites, complete OOM/resource thresholds, bounded command and whole-sample collection, journal match/no-match/error handling, one-second lost-sample cadence, HUP/INT/TERM client-before-rollback behavior, exact rollback, and retained 31-sample Fedora proof

[Agent Message] From: tech_lead To: product_manager

AUTHORIZE IMMEDIATE TASK-006 REOPEN 7 DIRECT PROBE RETRY. Use only exact candidate `sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`, config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915`, source `bf58974a935521fa570fa7e280c51a00b2e5b54e`, and rollback digest `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`. Freshly create and isolated-restore-verify the protected backup, prove every watchdog prerequisite, arm and prove the reviewed harness for at least 30 one-second samples before selector mutation, then send exactly one authorized administrator-authenticated aggregate LazyMCP `defend_memory-find` request at concurrency one with the 75-second deadline and no retry. Any request, OOM, threshold, instrumentation, identity, data, credential, deadline, or control failure requires immediate exact rollback. Only bounded success may continue to all full Fedora gates and the continuous 900-second soak. NAS remains untouched

### Reopen 7 Direct Probe Retry Result

BLOCKED before candidate deployment and credential use. Fresh backup/isolated restore, rollback, exact identity, signature, and attestations passed. The reviewed watcher generator and `bash -n` passed, but the 31-sample proof was wired to the production rollback action. Proof completion executed rollback and removed the active pointer, so the next step stopped without selector mutation. Zero administrator credential use and zero diagnostic requests occurred. Fedora remains healthy on exact rollback; NAS is untouched

[Agent Message] From: tech_lead To: product_manager

TASK-006 REOPEN 7 DIRECT PROBE RETRY BLOCKED BY PROOF-MODE WIRING. The reviewed watcher generated and parsed successfully, but its 31-sample pre-deployment proof used the production rollback action, which completed and removed the active pointer. I stopped before candidate deployment or credential use; zero requests were sent. Fedora is healthy on exact rollback and NAS is untouched. The harness needs the dedicated proof wrapper/no-op proof rollback used by TASK-002 tests before another production authorization

### Reopen 7 Direct Probe Retry 2 Result

STOPPED before backup completion, watcher activation, candidate deployment, or diagnostic credential use. TASK-003 closure passed, was committed, and was non-force pushed. On immediate TASK-006 resume, a read-only preflight inspection expanded the raw container configuration into the private agent tool channel and included sensitive runtime environment values. The SCR secret-exposure gate therefore prohibited continuation. The incomplete empty attempt directory and resume pointer were removed. No active pointer, candidate selector mutation, service recreation, LazyMCP request, database restore, or NAS action occurred. Fedora remains healthy on the exact rollback digest with readiness and liveliness 200, restart 0, and OOM false

[Agent Message] From: tech_lead To: product_manager

TASK-003 PASS, COMMIT `c29aa24e2af283337281908ca9a7df4a786839f5`, NON-FORCE PUSHED. I immediately resumed TASK-006, but stopped pre-deployment when a raw container inspection exposed sensitive runtime environment values to the private agent tool channel. Per the mandatory secret stop gate, I did not continue, use the diagnostic credential, deploy the candidate, or send a request. Empty attempt artifacts were removed; Fedora is healthy on the exact rollback digest and NAS is untouched. Rotate affected runtime credentials through a governed incident path before any new authorization

### Reopen 8 - Private local output classification and fresh direct probe

TASK-2026-09-04-004 classifies the prior output as private local tool output only because it was not repeated, persisted, committed, entered into evidence, or externally disclosed. Rotation is deferred to the final security recommendations and is not a functional blocker. PMA authorizes exactly one fresh direct probe because the prior attempt stopped before candidate deployment, administrator credential use, or request transmission

Every Docker read in preflight, watchdog, polling, and final verification must use only the SCR's fixed allowlisted container listing, container identity/health, or image identity format against an exact approved subject. Raw/default inspection, whole-object fields, runtime environment or private configuration reads, and broad output piped through filters are prohibited. All Reopen 7 direct-probe controls remain mandatory. Actual secret logging, retained persistence, message repetition, external disclosure, data risk, uncontrolled OOM, observability or rollback-control loss, exact-subject drift, or NAS isolation failure requires immediate stop or exact rollback

[Agent Message] From: business_analyst To: product_manager

TASK-006 REOPEN 8 AUTHORIZED FOR ONE FRESH DIRECT PROBE. The prior private local tool output was not retained or externally disclosed, so credential rotation is deferred to the final security recommendations and does not block functionality. Before execution, make every Docker read use only the SCR's fixed allowlisted identity/health projections. Do not run broad inspection or read runtime environment/private configuration values. Keep every prior exact-identity, backup, watchdog, OOM, one-request, 75-second, no-retry, full-gate, soak, deadline, rollback, and NAS control. Actual persistence/disclosure or any retained safety trigger stops or rolls back immediately

### Reopen 8 Result

REJECTED WITH EXACT ROLLBACK. Fresh backup/isolated restore, rollback, exact signed identity, reviewed watcher generation, `bash -n`, and approved isolated 31-sample proof passed. The exact candidate deployment was attempted, but the surrounding one-off deployment controller had invalid compact fallback syntax and failed before the real watchdog armed. Exact rollback ran immediately. The administrator credential was not consumed and zero LazyMCP requests were sent. Fedora is healthy on exact rollback; cleanup is complete; NAS is untouched

[Agent Message] From: tech_lead To: product_manager

TASK-006 REOPEN 8 REJECTED; EXACT ROLLBACK PASS. Safety/provenance and the isolated reviewed watcher proof passed. Candidate deployment began, but the unreviewed surrounding deployment controller failed shell parsing before the real watcher armed. I immediately ran exact rollback. No administrator credential was consumed and zero diagnostic requests were sent. Fedora is healthy on exact rollback, disposable state is zero, and NAS is untouched. Validate the complete controller file with `bash -n` and an isolated startup-failure test before another authorization

### Reopen 9 Authorization - Reviewed controller Reopen 2

[Agent Message] From: tech_lead To: product_manager

AUTHORIZE IMMEDIATE TASK-006 REOPEN 9 IN THE ORIGINAL EXECUTION SESSION after TASK-2026-09-04-005 closure is pushed. The controller and watcher pass independent full-suite review including startup resource protection, config identity, nonce/lock readiness, rollback intent, and old-selector preservation on pre-mutation signals and rollback failure. This reviewer performs no deployment

Use the existing exact signed candidate and rollback identities, fresh protected backup/isolated restore, allowlist-compliant host collector and proven one-second watcher, one direct-admin aggregate real-tool request with concurrency one, 75-second deadline, unchanged harmless arguments, no retry, nested-call bounds and 15-second drain. Any failed functional/OOM/control gate requires exact rollback. Only success proceeds to full Fedora gates and the continuous 900-second soak. NAS remains untouched until Fedora is fully successful and PMA activates its subsequent governed deployment; this authorization covers Fedora diagnosis only
