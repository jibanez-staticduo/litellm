---
id: TASK-2026-09-03-007-plan-fedora-live-diagnostics
complexity: standard
track: investigation
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Plan Fedora live diagnostics

## Objective

Produce an executable read-only-first diagnostic plan for the candidate real-tool timeout and unhealthy transition during the four-hour maintenance window.

## Acceptance Criteria

- [x] AC-1: Map exact healthcheck command, timeout/retry/start-period, process/thread/event-loop/resource metrics, DB/Redis pools, MCP transport path, LazyMCP proxy path, and upstream defend service observability.
- [x] AC-2: Correlate prior failure timestamps/log evidence and define a minimal reproduction with bounded timeouts.
- [x] AC-3: Define secret-safe commands, sampling cadence, evidence filters, and immediate stop gates.
- [x] AC-4: Define decision tree for configuration-only, healthcheck-only, upstream MCP, infrastructure, or source-code root cause.
- [x] AC-5: Define exact fresh backup, deployment, 2-hour checkpoint, 4-hour deadline, correction review, rebuild/sign/redeploy, soak, and rollback sequence.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Read the failed Fedora evidence, amended SCR, current Fedora/defend topology, and relevant source/healthcheck code read-only. Design a concrete diagnostic runbook. Do not inspect secret values, mutate source/hosts/config/DB/containers, publish, or deploy. Update task/evidence and return signed execution handoff.

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

### Summary

Completed the read-only Fedora live diagnostic design and found stronger prior-failure evidence than the failed release packet retained. The candidate LiteLLM process was killed by the kernel global OOM killer at `2026-09-03T21:49:23Z` with about 100.3 GiB anonymous RSS. Docker restarted it with exit 137 before rollback. The exact execution runbook treats candidate memory growth as the primary incident signal and prevents another host-wide exhaustion with one-second sampling and automatic rollback gates

### Work Performed

- Correlated the failed release timeline, Docker events, kernel OOM record, current healthcheck, cgroup limits, process topology, database and Redis dependencies, MCP registration, and upstream Defend services without reading secret values
- Traced the request boundary from `/toolset/defend_memory/lazymcp` through `mcp_call`, upstream `defend-memory-mcp:8000/mcp`, and the upstream service's reentrant LiteLLM embedding and rerank calls
- Defined exact secret-safe instrumentation, evidence filters, one-call reproduction, health and pool probes, stop thresholds, decision tree, correction governance, timing checkpoints, rebuild/sign flow, full verification, soak, and rollback
- Performed no source, configuration, database, container, registry, Fedora service, NAS, Git ref, or deployment mutation

### Acceptance Criteria Coverage

- **AC-1: PASS.** The runbook maps the live readiness healthcheck, `30s` interval, `5s` timeout, three retries, `20s` start period, event-loop probes, cgroup/process metrics, Prisma and PostgreSQL pools, Redis clients, LazyMCP path, MCP transport, and Defend dependencies
- **AC-2: PASS.** The prior timeline is correlated to the second, including candidate start, successful gates, global OOM kill, automatic restart, rollback, and recovery. Reproduction is limited to one deterministic harmless call with one in-flight request and a 75-second client deadline
- **AC-3: PASS.** Commands use protected local files or process environment without printing credentials, retain only allowlisted metadata, sample memory each second and other layers at bounded cadence, and immediately roll back on fixed growth, pressure, identity, security, data, or observability gates
- **AC-4: PASS.** The decision tree distinguishes healthcheck-only, DB/Redis pool, route/auth, LazyMCP, upstream MCP, infrastructure/resource, and source-code outcomes. The prior event is already classified as candidate-process resource exhaustion, while the allocating source path still requires the bounded run
- **AC-5: PASS.** The runbook freezes fresh backup/restore, exact deployment, two-hour continue decision, earlier correction cutoffs, four-hour hard deadline, separate governed correction paths, rebuild/qualification/signing, 900-second soak, final rerun, and exact rollback verification

### Documentation Impact

No steady-state product, architecture, technical, or CodeMap document changes are required. This is a time-bounded release diagnostic plan, so the task evidence is the operational source of truth

### Open Risks

- The exact allocation site is not proven because the removed candidate container's application log and pre-kill process samples were not retained
- The live Compose service has no memory limit, while the prior candidate reached about 100.3 GiB RSS. The execution task must arm the automatic rollback watcher before selector mutation and must not rely on manual observation alone
- The Defend memory service calls the same LiteLLM service for embeddings and reranking while the original LazyMCP call remains open. This reentrant boundary is the leading path to discriminate, not yet a proven source defect
- A successful one-off retry is insufficient because the SCR rejects unexplained transient recovery

### Recommended Next Step

PMA should hand the evidence runbook to Tech Lead for `TASK-2026-09-03-006-diagnose-fedora-candidate-live`. Tech Lead must arm the protected rollback unit and watchdog before deployment, run one bounded call, classify the allocating boundary, and either use a separately approved correction path or restore the exact prior digest

### Signed Technical Architect Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-007 COMPLETE. Read-only evidence proves the prior candidate process, not the Defend dependencies, reached about 100.3 GiB anonymous RSS and was killed by the Fedora kernel global OOM killer at `2026-09-03T21:49:23Z`; Docker restarted it with exit 137 before exact rollback began. The executable runbook in `.staticeng/evidences/TASK-2026-09-03-007-plan-fedora-live-diagnostics/logs/01-fedora-live-diagnostic-runbook.md` arms one-second cgroup/process monitoring and automatic rollback before selector mutation, permits one 75-second deterministic `defend_memory-find` reproduction, and correlates liveness, readiness, backlog, asyncio tasks, Prisma/PostgreSQL, Redis, LazyMCP, MCP, Defend gateway, host pressure, and kernel events. It defines fail-closed classification, the two-hour decision, an earlier T+225 rollback cutoff, separate governed correction/rebuild/qualification/sign authorization, the full 900-second soak, and exact rollback. No source, host, config, DB, container, registry, deployment, Git ref, or NAS mutation was performed
