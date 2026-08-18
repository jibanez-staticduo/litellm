---
id: TASK-2026-08-18-015-verify-stream-safe-198-candidate
complexity: standard
track: investigation
slice: qa
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-014-build-stream-safe-198-candidate
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-18-015 - Verify Stream-Safe 1.98.0 Candidate

## Objective
Independently verify the candidate image identity, embedded source guards, test evidence, stable-tag non-promotion, host baselines, and deployment/rollback gates before any host deployment.

## Acceptance Criteria
- [ ] AC-1: Resolve candidate manifest/config identity independently and confirm linux/amd64, version 1.98.0, and revision `b0dfe2e7a7`.
- [ ] AC-2: Inspect image source to confirm both sync/async post-merge stream guards and ChatGPT fake-stream bypass.
- [ ] AC-3: Validate 146-test evidence and run bounded independent image/import checks with no failure/skip.
- [ ] AC-4: Confirm stable tag remains unchanged and both host rollback/preservation baselines are complete and secret-safe.
- [ ] AC-5: Approve or reject Fedora canary deployment by immutable digest.

## Handoff
[Agent Message] From: product_manager To: qa_engineer

Perform independent read-only candidate QA. Do not deploy, edit hosts, move tags, or modify source/evidence. Return a signed approve/reject handback.

# Post Implementation Task Updates

## QA Engineer: Post Investigation Expectations
- AC-1 through AC-5 passed.
- Fedora canary approved only by immutable digest `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`.
- Runtime functionality remains gated on the Fedora deployment task; NAS remains untouched.
