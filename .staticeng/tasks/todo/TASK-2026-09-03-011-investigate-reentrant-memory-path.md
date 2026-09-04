---
id: TASK-2026-09-03-011-investigate-reentrant-memory-path
complexity: complex
track: investigation
slice: logic
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Investigate reentrant memory path

## Objective

Determine from source and existing incident evidence whether `defend_memory-find` reenters Fedora LiteLLM for embeddings/reranking and which candidate path could grow to approximately 100 GiB RSS.

## Acceptance Criteria

- [x] AC-1: Trace the complete call graph from LazyMCP through defend-memory and any LiteLLM callbacks.
- [x] AC-2: Rank recursion, buffering, retry, transport/session, task fan-out, and payload-copy hypotheses with evidence.
- [x] AC-3: Compare candidate and rollback behavior at relevant source/config-shape boundaries without secret values.
- [x] AC-4: Define bounded confirmation instrumentation/tests suitable for the maintenance retry.
- [x] AC-5: Recommend minimal correction or next probe; no mutation.

## Handoff

[Agent Message] From: product_manager To: technical_architect

While browserless DCR is designed, inspect source, prior kernel/log evidence, and secret-free topology for the 100 GiB allocation path. Do not read secret values, issue production tool requests, modify source/config/hosts, or deploy. Update task/evidence with ranked hypotheses and exact probes.

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

### Summary

PASS investigation. `defend_memory-find` is intentionally reentrant: the outer LazyMCP call remains in Fedora LiteLLM while Defend calls the same proxy for one embedding and bounded reranking. The deterministic source path has no direct call back to LazyMCP or the memory-agent gateway, so it is not recursively cyclic by itself

Candidate-specific nested deployment routing or callback/cache feedback is the leading explanation for request multiplication toward approximately 100 GiB RSS. Deterministic fan-out and buffering rank as amplifiers. Retry, transport/session leakage, and a one-shot giant allocation rank lower but remain measurable gaps

### Work Performed

- Traced LazyMCP admission, ASGI buffering, MCP tool listing/call, session transport, guardrails/logging, Defend deterministic retrieval, and LiteLLM embedding/rerank callbacks
- Compared candidate and rollback source/config-shape boundaries and identified selected nested deployment plus normalized upstream authority as the missing control comparison
- Ranked six hypotheses and defined one-call route-cardinality, egress, task/socket, memory, and cancellation-drain instrumentation
- Defined conditional minimal fixes and isolated regressions in `.staticeng/evidences/TASK-2026-09-03-011-investigate-reentrant-memory-path/`
- Performed no production request, secret read, source/config/host mutation, or deployment

### Acceptance Criteria Coverage

- **AC-1: PASS.** Complete cross-repository call graph is recorded
- **AC-2: PASS.** Recursion, fan-out, buffering/payload copy, transport/session, retry, and allocation are ranked with evidence
- **AC-3: PASS.** Candidate/rollback comparison is secret-free and names the unresolved nested-route identity boundary
- **AC-4: PASS.** Exact bounded live counters and isolated tests are defined
- **AC-5: PASS.** Next probe and conditional minimal corrections are defined without mutation

### Documentation Impact

No steady-state documentation or CodeMap update is required because no supported behavior or maintained source structure changed

### Open Risks

The exact allocator remains unknown. Fedora still lacks a cgroup memory ceiling, and cancellation drain across the real streamable MCP transport is not covered by a production-equivalent regression

### Recommended Next Step

PMA should merge TASK-011's route-cardinality and normalized egress-authority counters into TASK-007 before the single candidate retry, then hand execution to Tech Lead under the existing watchdog and TASK-010 headless authorization precondition. Any nested count above one embedding or three reranks, any nested LazyMCP call, or any post-settlement arrival requires immediate rollback without a second request

### Signed Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-011 PASS. Source confirms bounded reentry but no intrinsic deterministic recursion. Candidate-specific model-route or callback/cache feedback is the leading hypothesis, with Defend fan-out and buffering as amplifiers. Instrument the one authorized retry for exact route counts and selected egress authority, require at most one nested embedding and three reranks with full 15-second drain, and roll back on any excess or continued arrivals. No production request, secret read, source/config/host mutation, or deployment occurred
