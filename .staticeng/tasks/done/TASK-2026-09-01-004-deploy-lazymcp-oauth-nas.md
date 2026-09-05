---
id: TASK-2026-09-01-004-deploy-lazymcp-oauth-nas
complexity: complex
track: implementation
slice: foundation
status: done
closed_by: product_manager
closed_on: 2026-09-05
closure_task: TASK-2026-09-05-003-close-dual-host-repair
scr: SCR-2026-09-01-001-upstream-main-integration
parent: null
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 1
---

# Task: Deploy LazyMCP OAuth to NAS

## PMA acceptance and archive

Closed under PMA's explicit functional repair/deployment acceptance in TASK-2026-09-05-003. The initial AC-5/AC-6 Astra and aggregate-MCP residuals were subsequently corrected and verified in TASK-2026-09-05-002, including its Reopen 1 and final dual-host parity checks. The original checklist and failed/partial findings below remain unchanged historical evidence, not retroactive full qualification passes. AC-7 recovery was prepared but unused; later explicit no-automatic-rollback direction and successful same-digest deployment supersede the old rollback-on-any-failure wording without claiming a new rollback exercise. Final accepted index is 0c8009530d20ca8a5306f38ff4f6aecb6e3261ded0c5e7336237033b6557717c, source 6ba4b3b366386e16364a6723c43319f4e52cc7a0. Closure excludes external Frigate availability, an all-provider/security qualification and indefinite memory stability. Evidence index: .staticeng/evidences/TASK-2026-09-05-003-close-dual-host-repair/SUMMARY.md

## Objective

After Fedora is independently approved, deploy the same immutable registry digest to NAS and validate complete parity with rollback prepared.

## Acceptance Criteria

- [x] AC-1: Fedora post-observation Tech Lead authorization passes before NAS mutation.
- [x] AC-2: Owner-only NAS backup/rollback artifacts capture selector/config/DB/state.
- [x] AC-3: Only NAS LiteLLM selector and Reopen 1 authorized containment change; only `litellm` is recreated with no dependencies.
- [x] AC-4: NAS runs the exact same registry digest/config image as Fedora with healthy, zero-restart, no-OOM state. Docker engines expose different local ID representations of that same OCI index.
- [ ] AC-5: Models, Responses, `/mcp`, MCP REST, LazyMCP discovery/challenges/real tool and public routes pass.
- [ ] AC-6: Bounded logs and observation show no new regressions; cross-host parity is recorded.
- [ ] AC-7: Rollback executes on failure and split release is resolved explicitly.

## Handoff

[Agent Message] From: product_manager To: developer

Do not begin until PMA changes this task to active after Fedora approval. NAS only, then cross-host parity. Never print secrets. Stop and follow authorized rollback on any failed gate.

## Blocker Report

[Agent Message] From: product_manager To: developer

NAS promotion is explicitly rejected because candidate qualification failed and Fedora deployment is unauthorized. Do not mutate NAS.

## Reopen History

### Reopen 1 - Verified Fedora product repair promotion

Historical rejection is superseded by the latest explicit user NAS authorization and Tech Lead functional/memory PASS in TASK-2026-09-05-001 logs/19-functional-memory-pass.md. Deploy ONLY `docker.staticduo.com/litellm@sha256:7b2368711ff10db3107772d627e03aa89319598f8897ff7431497775926b2eb9`, source `7a9ef0335303d973f3a228dcf7baadff18c82fb5`, after fresh NAS identity/architecture/schema/backup preflight. Preserve NAS-specific configuration, credentials, mounts, model/MCP catalog, and dependencies; do not copy Fedora settings blindly. Apply only candidate containment needed to avoid host exhaustion, documented against NAS capacity. Recreate only LiteLLM through its actual Compose path. Verify real SDK Responses JSON/stream, Chat, NAS read-only MCP/LazyMCP tool, discovery, readiness, resource behavior and at least 900 seconds observation. Recheck Fedora and prove identical image/source on both. No security remediation or harness repair. Recovery remains available for NAS failure; never restore DB destructively without approval.

[Agent Message] From: product_manager To: tech_lead

Execute promotion now; previous Fedora repair agent is paused, so you own the single implementation. Complete evidence and precise product/config diffs, then finalize required registries/docs before commit/non-force push to main. Verify local main and origin/main synchronization. Report deferred security separately. A successful deployment is not enough: both actual runtime validation and cross-host parity must pass before closure.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

Reopen 1 deployment and bounded memory verification completed. Both hosts select the authorized 7b236871 index, source 7a9ef0335303d973f3a228dcf7baadff18c82fb5. NAS container 6b6f8743c69dab2a768dc76bef046511c7486bf0627d3fc0bc0a587bd4ff314c and unchanged Fedora container 164bab0c75f9294a3a7977420c2fda7686acb7a7bc5317af2d0768021b721264 are healthy, restart 0, OOM false. NAS completed 900.46 seconds with 31/31 healthy/readiness/liveliness samples and zero cgroup max/OOM events

AC-1 through AC-4 pass. AC-5 is partial: real SDK Responses omitted/false/true, available-model Chat JSON/stream, public LazyMCP discovery/challenges/real Memory lookup, MCP REST, and Memory-selected standard /mcp initialize/list/real health tool pass. NAS public Astra Chat returns 429 with no deployments available/cooldown. Unscoped standard /mcp initialization returns 504 after 30 seconds; REST identifies three unhealthy Frigate registrations, while 24 registrations are healthy. Neither failure is reported as a pass or conclusively attributed to the image. No registration, credential, routing or provider repair was attempted

AC-6 memory and identity observation pass, but a clean-log/no-regression conclusion remains open for those live limitations. AC-7 recovery is prepared and unused: no data/host safety failure or proven candidate regression required rollback, both hosts remain on the same exact release, and no DB restore occurred. This task remains active for PMA disposition rather than being closed with failed live checks

Product documentation is not required: this task adds no product behavior or source change. Operational authorization, task state, preservation evidence, identity representation, command results and limitations are recorded in the task evidence and SCR. StaticEng validation passes with zero warnings. UI screenshots are not applicable

Evidence: `.staticeng/evidences/TASK-2026-09-01-004-deploy-lazymcp-oauth-nas/SUMMARY.md`. Protected recovery is host-local at /volume2/docker/litellm/releases/TASK-2026-09-01-004-reopen1 and must not enter Git. Existing unrelated harness changes remain preserved, not committed as NAS implementation

[Agent Message] From: tech_lead To: product_manager

NAS promotion, representative functional checks, 900-second resource gate and final Fedora/parity checks completed. Full AC-5/AC-6 closure remains pending because Astra Chat is in deployment cooldown and unscoped /mcp initialization times out with three unhealthy Frigate registrations. Keep both healthy contained runtimes selected while routing those concrete live limitations for disposition or same-scope diagnosis. Do not infer an all-provider/all-registration PASS or initiate unrelated security/harness remediation
