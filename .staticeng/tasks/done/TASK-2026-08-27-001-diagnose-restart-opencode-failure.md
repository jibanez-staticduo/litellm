---
id: TASK-2026-08-27-001-diagnose-restart-opencode-failure
complexity: standard
track: investigation
slice: qa
status: done

# Post Implementation Task Updates

## Tester: Post Implementation Expectations
- NAS deferred activation completed successfully.
- All running fleet OpenCode runtimes load official 1.18.23 and plugin 0.2.1; pi5 has no active runtime.
- Fedora Defend lanes remain intentionally masked and separate from primary reasoning behavior.
scr: null
parent: TASK-2026-08-26-017-migrate-shared-opencode-contracts
assigned_to: tester
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-27-001 - Diagnose restart_opencode Failure

## Objective
Assess the fleet restart command that partially failed on Fedora and left NAS activation deferred, without mutating services while the reasoning migration task remains active.

## Acceptance Criteria
- [ ] AC-1: Confirm final command exit state and per-host service/process health after the run.
- [ ] AC-2: Explain Fedora masked/missing defend/OpenChamber unit failures and whether they affect OpenCode reasoning rollout.
- [ ] AC-3: Determine NAS deferred activation state and whether a later safe activation is required after Task 017 closes.
- [ ] AC-4: Confirm hosts that restarted loaded official OpenCode 1.18.23 and identify plugin version where safely observable.
- [ ] AC-5: Return exact non-mutating remediation plan; do not restart/edit/unmask services.

## Expected Evidence
- Signed read-only handoff with host status, relevant unit names, and safe next actions.
