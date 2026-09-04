# TASK-2026-09-03-006 Evidence Summary

## Reopen 7 Direct Probe Retry 2

TASK-003 passed, commit `c29aa24e2af283337281908ca9a7df4a786839f5` was non-force pushed, and TASK-006 resumed immediately. Execution stopped before backup completion, watcher activation, candidate deployment, and credential use because a read-only raw container inspection expanded sensitive runtime environment values into the private agent tool channel. The incomplete empty attempt and resume pointer were removed. No selector mutation, service recreation, request, database restore, or NAS action occurred. Fedora remains healthy on the exact rollback digest with readiness and liveliness 200, restart 0, and OOM false. A governed credential-rotation incident is required before another authorization

## Summary

REJECT candidate and PASS rollback. A fresh protected backup and isolated restore, exact identity checks, rollback unit, and one-second watchdog passed before the exact signed candidate deployed. The diagnostic request did not run because the protected Fedora client credential was a legacy API key, not the required exact-audience DCR bearer. The client harness then failed closed before sending a request, and automatic rollback restored the exact prior digest. Fedora is healthy; NAS was untouched

The prior incident root cause remains candidate-process resource exhaustion: kernel evidence shows about 100.3 GiB anonymous RSS before a global OOM kill. This attempt narrowed the immediate execution blocker to credential governance, but did not identify the candidate allocation site because no authorized exact-audience request was sent

## Work Performed

- Pushed the approved SCR amendment, TASK-006, and TASK-007 runbook before production action
- Created owner-only Fedora attempt `TASK-2026-09-03-006-20260903T231759Z`, fresh custom-format database dump/checksum/list, and an isolated restore using the exact PostgreSQL image; verified 161 migrations, 81 public tables, zero task-artifact tables, and cleanup
- Freshly verified the candidate manifest, source, amd64 platform, signature, SPDX, CycloneDX, and SLSA attestations; prepared and syntax-checked an idempotent exact-digest rollback unit
- Armed independent one-second memory/process/host watchdog plus health and dependency samplers before selector mutation, then captured more than 30 seconds of rollback baseline
- Changed only `LITELLM_IMAGE`, recreated only `litellm --no-deps`, and verified candidate identity, startup, health, migrations, zero restart/OOM, and bounded memory
- Stopped before the reproduction when the required exact-audience bearer was unavailable and the attempted client harness failed closed; automatic rollback restored the exact prior digest
- Verified five-minute rollback stability, exact identity, health/readiness/liveliness, migrations, inventory APIs, unchanged protected state and dependencies, MCP initialize, and a successful real `defend_memory-find` through the rollback image

## Acceptance Criteria Coverage

- **AC-1: PASS.** Fresh protected backup/restore, baseline, exact candidate/signature/attestation, and rollback unit all passed before deployment
- **AC-2: FAIL.** Correlated resource/health/dependency observability ran, but the one authorized candidate `defend_memory-find` request was not sent because no exact-audience DCR bearer was available
- **AC-3: PARTIAL.** The prior timeout/unhealthy transition is conclusively classified as candidate-process resource exhaustion culminating in global OOM. The exact allocating request phase remains unproven
- **AC-4: PASS.** No production code, configuration, timeout, healthcheck, pool, credential scope, database row, or host capacity was patched ad hoc
- **AC-5: FAIL.** The candidate did not execute the required real tool, full verification matrix, or 900-second soak and is not released
- **AC-6: PASS.** Automatic rollback restored the exact prior digest and NAS remained untouched
- **AC-7: PASS FOR FAILED OUTCOME.** Secret-free repository evidence, host-local protected artifacts, and task/registry updates record the rejected attempt and verified rollback

## Safe Runtime Evidence

```text
preflight started: 2026-09-03T23:17:59Z
candidate deployment T0: 2026-09-03T23:29:36Z
rollback started: 2026-09-03T23:31:36Z
candidate samples: 112 at one-second cadence
candidate memory range: 33,992,704 to 1,482,137,600 bytes
candidate swap maximum: 0 bytes
candidate memory PSI full avg10 maximum: 0.00
candidate PID maximum: 47
dependency restarts/OOM: 0 / 0
new kernel OOM events: 0
rollback real tool: HTTP 200, JSON-RPC result present, isError false
production database restore: not performed
NAS mutation: none
```

## Root Cause And Governed Fix

The previous live failure is a candidate-process memory blowup, not a healthcheck-only, DB/Redis pool, route/auth, or upstream-service restart explanation. The candidate reached about 100.3 GiB anonymous RSS and was globally OOM-killed while Defend and data dependencies stayed running

This attempt exposed a separate prerequisite defect: the available protected Fedora client header is a legacy API key, while TASK-007 requires an exact-audience DCR bearer for `/toolset/defend_memory/lazymcp`. Substituting the admin key would weaken the security gate and is prohibited

The smallest governed next path is a dedicated credential-preparation task that performs the existing DCR authorization-code flow for the exact toolset resource, stores the short-lived bearer in an owner-only non-Syncthing file, proves cross-audience rejection, and hands only that protected file location to a reopened TASK-006. The retry must recreate a fresh backup and rollback unit, arm the same watchdog first, and send exactly one 75-second request. If the bounded retry reproduces memory growth after upstream acceptance, route a separate LiteLLM source task around `_lazymcp_call`/`call_mcp_tool` and reentrant embedding/rerank response retention, with a regression that asserts cancellation and bounded RSS before building a new signed candidate

## Documentation Impact

No steady-state product, architecture, technical, or CodeMap update is required. No supported behavior or maintained source structure changed

## Open Risks

- The exact candidate allocation site remains unknown because the required exact-audience candidate request was not sent
- The candidate remains blocked and must not be redeployed without a fresh authorization, fresh backup/restore, and protected exact-audience credential
- Fedora Compose still has no cgroup memory ceiling; the automatic watchdog remains mandatory for any retry

## Recommended Next Step

PMA should keep the candidate blocked, create the narrow exact-audience credential-preparation task, then reopen TASK-006 for one protected retry. Do not patch production, increase memory, extend timeouts, or touch NAS

## Signed Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT CANDIDATE; VERIFIED ROLLBACK PASS. Fresh backup/isolated restore, exact signature and attestation checks, rollback unit, and one-second watchdog passed before exact candidate deployment. Candidate startup remained healthy and bounded at about 1.48 GiB, but the required request was not sent because Fedora had only a legacy API key, not the exact-audience DCR bearer mandated by TASK-007. The client harness failed closed and automatic rollback began at `2026-09-03T23:31:36Z`. Exact prior digest is restored with healthy readiness/liveliness, zero restart/OOM, unchanged protected state and dependencies, 161 compatible migrations, five-minute stable memory, MCP initialize 200, and a successful rollback-image `defend_memory-find`. No database restore, ad-hoc production correction, or NAS action occurred. Create a governed exact-audience credential-preparation task before reopening this task

## Reopen 2 Outcome

Reopen 2 stopped at the mandatory principal preflight before any candidate deployment. The only owner-only username/password file found has the correct protected shape, but its username matches zero existing Fedora database users and both values differ from the configured proxy-admin pair. It therefore cannot be proven to represent an existing currently `defend_memory`-authorized principal

No backup or watchdog was started because selector mutation was already prohibited. No login, DCR registration, consent POST, token, request, or auth artifact was created. Fedora remained healthy on the exact rollback digest with 161 completed migrations and NAS remained untouched. See `logs/02-reopen2-preflight-blocker.md`

## Reopen 3 Outcome

Reopen 3 stopped at the required supported-API proof before creating a principal or deploying the candidate. Candidate, rollback, and live OpenAPI contracts all show that `NewUserRequest` does not define `password`; a supplied password is dropped. `/user/update` can set it, but the amended SCR prohibits follow-up repair before use and requires atomic password-backed creation. The root cause is a specification/API-contract mismatch

Fedora remained healthy on the exact rollback digest. No watchdog or rollback was needed because the selector did not change. There was no task-owned principal, grant, key, membership, auth workspace, DCR artifact, consent, or diagnostic request. NAS remained untouched. See `logs/03-reopen3-api-contract-blocker.md`

## Reopen 4 Outcome

Reopen 4 completed fresh backup/isolated restore, rollback-unit, candidate identity, signature, and attestation preparation, then stopped at the mandatory existing-toolset baseline. Supported admin `GET /v1/mcp/toolset` returned HTTP 200 with zero toolsets, so the required existing `defend_memory` toolset ID and membership digest could not be resolved

No principal was created and no watchdog/candidate/auth/request phase started. All disposable restore resources and rendered temporary configuration were removed, the active pointer was cleared, Fedora remained healthy on exact rollback, and NAS remained untouched. See `logs/04-reopen4-toolset-read-blocker.md`

## Reopen 5 Outcome

Reopen 5 passed fresh backup/isolated restore, rollback, exact candidate provenance, exact temporary one-tool toolset create/read-back, independent cleanup arming, and the strict `/user/new` then immediate password-only `/user/update` transaction. Least-privilege read-back passed, but the first required `/login` returned HTTP 401

The explicit stop gate triggered before watchdog activation or candidate deployment. Supported cleanup cleared/deleted the principal before deleting the toolset and restored the zero-toolset baseline. No DCR, consent, audience, or diagnostic request occurred; all task auth artifacts were destroyed; Fedora remained healthy on exact rollback; NAS was untouched. See `logs/05-reopen5-login-blocker.md`

## Reopen 6 Outcome

Reopen 6 proved the corrected email login path: fresh safety/provenance gates, exact temporary toolset, strict two-step principal transaction, least-privilege read-back, email login, and UI-key capture all passed. The task-local client then failed before DCR while trying to pickle Python's lock-bearing `CookieJar`

Cleanup explicitly requested UI-key deletion before grant/principal deletion, removed the toolset last, restored baseline counts, and destroyed all artifacts. The candidate was never deployed and no diagnostic request was sent. Fedora remained healthy on exact rollback; NAS was untouched. See `logs/06-reopen6-client-artifact-blocker.md`

## Reopen 7 Outcome

Reopen 7 passed fresh backup/isolated restore, rollback, exact candidate identity, signature, and attestations, then stopped before deployment because the generated one-second watchdog failed shell syntax during its mandatory proving period. No administrator credential was consumed and no LazyMCP request was sent

All disposable resources and rendered temporary configuration were removed, the active pointer was cleared, Fedora remained healthy on exact rollback, and NAS was untouched. See `logs/07-reopen7-watchdog-syntax-blocker.md`

The subsequently authorized retry used the reviewed TASK-002 generator and passed `bash -n`, fresh backup/restore, rollback, identity, and provenance. Its 31-sample proof ran with the production rollback action, which completed and removed the active pointer before deployment. The operation failed closed with zero credential use and zero requests; Fedora stayed healthy on exact rollback. This proof-mode contract mismatch is appended to the same Reopen 7 evidence
