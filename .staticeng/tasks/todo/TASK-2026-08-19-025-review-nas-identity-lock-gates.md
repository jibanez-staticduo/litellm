---
id: TASK-2026-08-19-025-review-nas-identity-lock-gates
complexity: standard
track: investigation
slice: qa
status: active
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-024-deploy-nas-stream-safe-198
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-025 - Review NAS Identity And Lock Gates

## Objective
Classify the candidate manifest/config identity mismatch assertion and recurring credential lock-file ctime-only drift, then define corrected non-weakening gates for one controlled redeployment.

## Safety
- Read-only; both hosts remain on restored pre-release images and stable untouched.
- Do not inspect credential contents, deploy, restart, edit config/models/auth, or move tags.

## Acceptance Criteria
- [ ] AC-1: Verify registry manifest digest versus Docker config image ID semantics and define correct identity assertions.
- [ ] AC-2: Identify the salted lock-file path type/role and determine whether ctime-only drift is expected lock lifecycle behavior.
- [ ] AC-3: Confirm no credential file content/size/mtime/ownership/mode drift, auth failure, or device flow accompanied the lock drift.
- [ ] AC-4: Define exact corrected gates and approve/reject one parent redeployment.

## Handoff
[Agent Message] From: product_manager To: tech_lead

Review the false-positive candidate identity and lock-file gates read-only. Return exact corrected assertions and an approve/reject decision for one controlled redeployment.
