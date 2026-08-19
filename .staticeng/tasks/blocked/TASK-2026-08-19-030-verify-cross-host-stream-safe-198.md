---
id: TASK-2026-08-19-030-verify-cross-host-stream-safe-198
complexity: standard
track: investigation
slice: qa
status: blocked
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-010-design-stream-safe-198-release
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-030 - Verify Cross-Host Stream-Safe 1.98.0

## Objective
Independently verify both NAS and Fedora are healthy, functional, preserved, and running the same stream-safe 1.98.0 digest before stable promotion.

## Acceptance Criteria
- [ ] AC-1: Both hosts run manifest `sha256:42d365...115b`, config `sha256:45a019...c73`, version 1.98.0, revision `b0dfe2e7a7`, with embedded stream guards.
- [ ] AC-2: Both hosts pass health/readiness/liveliness, zero new restarts/OOM, clean release logs, and current observation checks.
- [ ] AC-3: NAS exact 32-model/default-account2/account3-quarantine topology and Fedora exact 27-model/two-account topology match evidence.
- [ ] AC-4: Native Responses, corrected Codex public functionality, quota dispositions, profile selection, and absence of `Stream must be set to true` are independently verified.
- [ ] AC-5: LazyMCP matrices pass on both hosts and dependencies/unrelated services remain unchanged.
- [ ] AC-6: Review all evidence/security and approve or reject stable promotion to the candidate digest.

## Handoff
[Agent Message] From: product_manager To: qa_engineer

Perform independent read-only cross-host release QA. Do not mutate runtime, tags, models, routing, credentials, source, tasks, or evidence. Return explicit stable-promotion approval/rejection.

# Post Implementation Task Updates

## QA Engineer: Post Investigation Expectations
- AC-1, AC-3, AC-4, and AC-5 passed; AC-2 and AC-6 failed.
- Both hosts are functionally healthy on the intended candidate and no stream/auth/device/migration errors were found.
- Stable promotion is blocked by success-telemetry callback tracebacks, world-writable NAS evidence directories, weaker Fedora evidence chain, and missing stable tag.

## Blocker Report
- Fix telemetry callback errors and prove clean logs.
- Secure/rehash NAS evidence and produce equivalent Fedora hash-chain evidence.
- Reconcile stable tag, then reopen this same QA task for promotion review.
