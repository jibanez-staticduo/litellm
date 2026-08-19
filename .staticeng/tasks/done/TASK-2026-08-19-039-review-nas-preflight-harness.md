---
id: TASK-2026-08-19-039-review-nas-preflight-harness
complexity: tiny
track: investigation
slice: qa
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-038-deploy-nas-clean-telemetry-198
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-039 - Review NAS Preflight Harness

## Objective
Correct the three preflight assumptions about protected mount type, credential directory names, and Fedora SSH execution identity without weakening security gates.

## Acceptance Criteria
- [x] AC-1: Define correct protected directory metadata/hash gate.
- [x] AC-2: Define exact credential directory discovery limited to approved chatgpt/anthropic paths.
- [x] AC-3: Define safe Fedora isolation check under `staticduo` or verified literal endpoint.
- [x] AC-4: Approve/reject one corrected parent attempt.

## Handoff
[Agent Message] From: product_manager To: tech_lead

Review the three preflight-only harness assumptions read-only and return exact corrected gates plus retry decision.

# Post Implementation Task Updates

## Tech Lead: Post Investigation Expectations
- AC-1 through AC-4 passed.
- Exact protected-directory, credential-directory, and Fedora SSH isolation gates are recorded in parent Reopen 1.
- One corrected attempt approved after shell validation.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Current parent harness: **REJECTED AS WRITTEN**
- Retry disposition: **APPROVE EXACTLY ONE CORRECTED PARENT ATTEMPT** after all fail-closed gates in `.staticeng/evidences/TASK-2026-08-19-039-review-nas-preflight-harness/SUMMARY.md` are incorporated and `bash -n` passes
- Protected mount correction: handle the root-owned empty `op_service_account_token` directory as directory metadata plus an empty-tree digest and preserve its exact read-only bind tuple
- Credential correction: inspect only the literal `chatgpt-auth` and `anthropic-auth` direct-child roots, reject symlinks/special files/permission drift, and never read credential contents
- Fedora correction: pin `staticduo@fedora-ssh.staticduo.com`, assert remote user and uid before metadata inspection, and require byte-identical before/after isolation projections
- Product documentation is not required for this preflight-only investigation
