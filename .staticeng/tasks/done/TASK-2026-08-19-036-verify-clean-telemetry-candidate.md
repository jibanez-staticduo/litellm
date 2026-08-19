---
id: TASK-2026-08-19-036-verify-clean-telemetry-candidate
complexity: standard
track: investigation
slice: qa
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-035-build-clean-telemetry-198-candidate
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-036 - Verify Clean-Telemetry Candidate

## Objective
Independently verify replacement image identity, embedded fixes, tests, stable non-promotion, and deployment readiness.

## Acceptance Criteria
- [ ] AC-1: Resolve manifest/config, architecture, version, and revision independently.
- [ ] AC-2: Inspect/execute all stream, logging, fake-stream, and cache contracts in-image.
- [ ] AC-3: Independently verify focused regression evidence with no failures/skips.
- [ ] AC-4: Confirm stable and both hosts remain unchanged with valid rollback references.
- [ ] AC-5: Approve/reject Fedora-first deployment.

## Handoff
[Agent Message] From: product_manager To: qa_engineer

Perform independent read-only candidate QA. Do not deploy, edit hosts/source/evidence, or move tags. Return explicit approval/rejection.

# Post Implementation Task Updates

## QA Engineer: Post Investigation Expectations
- AC-1 through AC-5 passed.
- Fedora-first deployment approved; NAS remains gated on Fedora runtime success.
