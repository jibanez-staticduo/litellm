---
id: TASK-2026-09-04-001-authorize-direct-functional-probe
complexity: tiny
track: spec
slice: foundation
status: done
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

- [x] AC-1: Use the existing administrator credential only in process memory from its owner-only Fedora source; never print, copy, hash, persist, or include it in arguments/evidence.
- [x] AC-2: Invoke exactly one `defend_memory-find` request through the candidate LazyMCP transport with concurrency one and 75-second deadline.
- [x] AC-3: Keep fresh backup, exact rollback, one-second watchdog, nested-call counters, memory thresholds, and no-second-request rule.
- [x] AC-4: Skip temporary toolset/principal/DCR creation for this diagnostic only; do not weaken steady-state auth behavior or alter configuration.
- [x] AC-5: If the request succeeds, run full functional gates and 900-second soak; if it fails or memory grows, rollback immediately. NAS remains untouched.

## Handoff

[Agent Message] From: product_manager To: business_analyst

The Product Owner explicitly directs functional-first diagnosis and wants security topics reported later. Amend the maintenance SCR to allow one direct administrator-authenticated LazyMCP tool call solely to reproduce the candidate runtime failure. This replaces, for this attempt only, temporary principal/toolset/DCR bootstrap. Preserve secret handling, backup, watchdog, OOM/data/rollback stop gates, exact digest, one request, four-hour deadline, and NAS isolation. Complete immediately; no runtime mutation.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary

PASS. Amended the approved SCR to authorize one direct administrator-authenticated candidate LazyMCP diagnostic request while prohibiting temporary toolset, principal, grant, login, and DCR bootstrap for this attempt

### Work Performed

- Limited credential use to the existing Fedora administrator API credential loaded from its owner-only source into diagnostic-client process memory, with no printing, copying, hashing, persistence, environment export, arguments, logs, traces, or evidence retention
- Authorized exactly one `defend_memory-find` request through the candidate aggregate `/lazymcp` transport with concurrency one, the unchanged harmless TASK-007 request, a 75-second deadline, and no retry, fallback, alternate credential, or second request
- Preserved fresh backup and isolated restore, exact candidate and rollback identities, one-second watchdog, existing memory and host thresholds, nested maxima of one embedding, three reranks, zero nested LazyMCP calls, and complete drain within 15 seconds
- Required immediate exact-digest rollback for request failure, auth rejection, timeout, ambiguity, memory growth, counter excess, failed drain, unhealthy state, or any retained safety gate
- Required a successful bounded request to continue through every full Fedora release gate and the continuous 900-second soak before Tech Lead PASS, within the existing four-hour maintenance deadline
- Performed documentation-only work with no credential access and no source, runtime, host, service, database, registry, Fedora, or NAS mutation

### Acceptance Criteria Coverage

- **AC-1: PASS.** The SCR permits only in-process use from the owner-only Fedora source and prohibits every named disclosure or retention channel
- **AC-2: PASS.** The SCR authorizes exactly one candidate aggregate LazyMCP request at concurrency one with a 75-second deadline and no retry
- **AC-3: PASS.** Fresh backup and restore proof, exact rollback, the one-second TASK-007 watchdog, unchanged memory thresholds, nested-call maxima, 15-second drain, and no-second-request rule remain mandatory
- **AC-4: PASS.** Temporary toolset, principal, grant, login, and DCR bootstrap are superseded and prohibited only for this attempt; steady-state auth and final release gates remain unchanged
- **AC-5: PASS.** Request failure or memory growth requires immediate rollback, while success requires all full Fedora gates and a continuous 900-second soak; NAS access and mutation remain prohibited

### Documentation Impact

Updated `.staticeng/docs/scrs/SCR-2026-09-01-001-upstream-main-integration.md`, this task, task registries, and task evidence. No product overview, feature list, architecture, technical, or CodeMap update is required because this is a single-run diagnostic authorization and does not change steady-state product behavior

### Open Risks

The administrator credential may be rejected by the candidate LazyMCP route. That outcome consumes the one request and requires rollback without credential repair, DCR fallback, or retry. Candidate memory behavior remains potentially catastrophic, so execution remains prohibited without the exact armed watchdog and rollback controls

### Recommended Next Step

PMA should reopen TASK-006 for the single direct candidate probe under this amendment. On a bounded request PASS, complete every full Fedora gate and the 900-second soak. On any failure, roll back immediately and return the secret-free diagnostic classification

### Signed Handoff

[Agent Message] From: business_analyst To: product_manager

TASK-2026-09-04-001 PASS. The SCR now authorizes exactly one direct candidate aggregate LazyMCP `defend_memory-find` request using the existing Fedora administrator API credential only in diagnostic-client process memory from its owner-only source. For this attempt, temporary toolset, principal, grant, login, and DCR bootstrap are superseded and prohibited. Keep concurrency one, the 75-second deadline, no retry or second request, exact candidate and rollback digests, fresh backup and isolated restore, the one-second TASK-007 watchdog and unchanged memory thresholds, one embedding and three rerank maxima, zero nested LazyMCP calls, and 15-second drain. Any request or safety failure requires immediate rollback. Only bounded success may proceed to all full Fedora gates and the continuous 900-second soak within four hours. NAS remains untouched. No runtime mutation occurred
