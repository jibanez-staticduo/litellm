---
id: TASK-2026-08-19-042-diagnose-nas-public-primary-gate
complexity: tiny
track: investigation
slice: qa
status: cancelled
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-038-deploy-nas-clean-telemetry-198
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-042 - Diagnose NAS Public Primary Gate

## Objective
Establish whether the failed public-primary gate was a real routing/functionality defect or an opaque combined assertion, and define evidence-complete assertions for retry.

## Safety
- Read-only against restored NAS; at most one bounded no-retry public request if required.
- Do not deploy, restart, edit models/routing/auth, or move tags.

## Acceptance Criteria
- [ ] AC-1: Inspect exact current public primary/fallback configuration and selection identifiers.
- [ ] AC-2: Recover or reproduce sanitized public request status/error/selection independently.
- [ ] AC-3: Classify runtime defect versus harness/evidence defect.
- [ ] AC-4: Define separate persisted status, lifecycle/error, and deployment-selection assertions; approve/reject retry.

## Handoff
[Agent Message] From: product_manager To: tech_lead

Diagnose the opaque public-primary failure read-only and return exact separated evidence gates plus retry decision.

# Post Implementation Task Updates

## PMA Cancellation
- Cancelled after the user directed deployment without further automatic rollback.
- Public status, SSE lifecycle, error, and deployment selection will be inspected separately during in-place deployment verification.
