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
reopened_count: 0
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
