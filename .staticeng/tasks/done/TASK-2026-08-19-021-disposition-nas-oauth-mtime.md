---
id: TASK-2026-08-19-021-disposition-nas-oauth-mtime
complexity: tiny
track: investigation
slice: qa
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-020-migrate-nas-198-startup-wrapper
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-021 - Disposition NAS OAuth Mtime Drift

## Objective
Determine whether the single OAuth token mtime advance is expected live refresh behavior and establish a safe just-in-time credential-metadata baseline for NAS deployment authorization.

## Safety
- Read-only; do not inspect credential contents, deploy, restart, edit auth/config/models, or move tags.
- Compare only presence, owner/mode, size, mtime, and sanitized service logs.

## Acceptance Criteria
- [ ] AC-1: Correlate the mtime change with expected runtime OAuth refresh and exclude unauthorized file replacement or auth-flow trigger.
- [ ] AC-2: Confirm modes/ownership/presence and all unaffected credential metadata remain safe.
- [ ] AC-3: Define a just-in-time pre/post comparison that tolerates expected refresh without masking account loss or permission drift.
- [ ] AC-4: Approve or reject NAS deployment.

## Handoff
[Agent Message] From: product_manager To: tech_lead

Disposition the mtime drift read-only and return an explicit NAS deployment approval/rejection with a safe credential-metadata gate.

# Post Implementation Task Updates

## Tech Lead: Post Investigation Expectations
- AC-3 passed, AC-2 partial, AC-1 failed, and AC-4 rejected NAS deployment.
- Credential drift correlated with failed OAuth refresh and device-auth prompt, not routine successful refresh.
- Exact just-in-time metadata/log gate is recorded in evidence.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Read-only metadata and sanitized logs attribute the mtime write to the running authenticator's atomic writer, not an unexplained replacement
- The write coincided with failed OAuth refresh and device-code authentication initiation at `2026-08-18T23:03:32Z`; AC-1 therefore fails
- All unaffected credential metadata matched the approved baseline, but legacy permissive auth-directory and two non-empty credential-file modes remain an open security risk
- NAS deployment decision: REJECT pending profile reauthorization, permission remediation, and a passing just-in-time gate
- Exact pre/post metadata and sanitized-log criteria are recorded under `.staticeng/evidences/TASK-2026-08-19-021-disposition-nas-oauth-mtime/`
- No credential content was read and no NAS runtime or host state was changed
- Product documentation and CodeMap updates are not required
