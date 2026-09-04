---
id: TASK-2026-09-04-001-authorize-direct-functional-probe
complexity: tiny
track: spec
slice: foundation
status: active
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: Authorize direct functional probe

## Objective

Authorize one direct candidate LazyMCP `defend_memory-find` probe using the existing Fedora administrator API credential, bypassing temporary-principal and DCR bootstrap work that is not needed to reproduce the runtime memory failure.

## Acceptance Criteria

- [ ] AC-1: Use the existing administrator credential only in process memory from its owner-only Fedora source; never print, copy, hash, persist, or include it in arguments/evidence.
- [ ] AC-2: Invoke exactly one `defend_memory-find` request through the candidate LazyMCP transport with concurrency one and 75-second deadline.
- [ ] AC-3: Keep fresh backup, exact rollback, one-second watchdog, nested-call counters, memory thresholds, and no-second-request rule.
- [ ] AC-4: Skip temporary toolset/principal/DCR creation for this diagnostic only; do not weaken steady-state auth behavior or alter configuration.
- [ ] AC-5: If the request succeeds, run full functional gates and 900-second soak; if it fails or memory grows, rollback immediately. NAS remains untouched.

## Handoff

[Agent Message] From: product_manager To: business_analyst

The Product Owner explicitly directs functional-first diagnosis and wants security topics reported later. Amend the maintenance SCR to allow one direct administrator-authenticated LazyMCP tool call solely to reproduce the candidate runtime failure. This replaces, for this attempt only, temporary principal/toolset/DCR bootstrap. Preserve secret handling, backup, watchdog, OOM/data/rollback stop gates, exact digest, one request, four-hour deadline, and NAS isolation. Complete immediately; no runtime mutation.
