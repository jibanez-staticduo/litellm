---
id: TASK-2026-09-03-006-diagnose-fedora-candidate-live
complexity: complex
track: implementation
slice: qa
status: active
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-012-release-upstream-main-fedora
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 1
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
