---
id: TASK-2026-08-19-023-quarantine-nas-invalid-account3
complexity: standard
track: implementation
slice: logic
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-022-repair-nas-chatgpt-auth-hygiene
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-023 - Quarantine NAS Invalid Account3

## Objective
Remove invalid account3 from active NAS model registrations and fallback routing so production remains functional without device-auth loops, while preserving an exact protected restoration backup.

## Safety
- Back up every affected account3 deployment and fallback row before mutation with exact rollback transaction and hashes.
- Preserve default and account2 deployments, public default-profile primaries, unrelated models, credentials, database, and services.
- Do not delete account3 credential backups; do not trigger authentication.
- Do not deploy 1.98.0 or move tags in this task.

## Acceptance Criteria
- [x] AC-1: Capture exact affected account3 deployments/fallback references and protected restoration procedure.
- [x] AC-2: Remove account3 deployments and all active fallback references to account3 using supported DB/admin paths.
- [x] AC-3: Public aliases retain default primary and account2 fallback; default/account2 qualified deployments remain intact.
- [x] AC-4: No pending/active device-auth flow or account3 auth attempt appears after reload/observation.
- [x] AC-5: Bounded default and account2/public fallback checks pass or return only documented quota, never auth/device-flow errors.
- [x] AC-6: NAS remains healthy; normalized remaining inventory/routing baseline is captured for release; Fedora candidate and registry candidate remain unchanged.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-023-quarantine-nas-invalid-account3/` with `SUMMARY.md` and sanitized logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Quarantine only invalid account3 from active NAS routing after exact protected backup. Preserve default/account2 and all unrelated state. Prove no device-auth loop and capture the new release baseline. Do not deploy 1.98.0, move tags, or commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1 through AC-6 passed.
- Eight invalid account3 deployments and eight fallback references were removed after exact protected backup.
- NAS release baseline is 32 models with default primaries, default-qualified deployments, and account2 fallbacks preserved.
- Default/account2/public checks pass HTTP 200; 14m58s observation showed no device-auth/account3 refresh activity.
- Account3 must not be restored before user-assisted reauthorization.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-6 passed
- Exact protected backup: `/volume2/docker/litellm/releases/20260819-quarantine-account3/`, owner `0:0`, mode 0700, with mode-0600 SQL, manifest, and rollback files
- Eight account3 deployments and eight account3 fallback references were removed through supported admin APIs; default, account2, public aliases, and unrelated state remain intact
- NAS remains healthy on unchanged 1.92.0 with the exact normalized 32-model release baseline in task evidence
- Fedora and the candidate registry digest remain unchanged; the parent task's missing stable tag remains unchanged
- No 1.98.0 deployment, tag movement, credential exposure, source change, or commit occurred
- No product documentation or CodeMap update is required
