---
id: TASK-2026-09-04-003-fix-watchdog-proof-wiring
complexity: tiny
track: implementation
slice: qa
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: Fix watchdog proof wiring

## Objective

Ensure pre-deployment proof uses isolated proof state and a no-op rollback, never production control files/actions.

## Acceptance Criteria

- [x] AC-1: Proof has its own active pointer, logs, controls, and no-op rollback.
- [x] AC-2: 31-sample proof exits successfully without production selector/recreate/pointer mutation.
- [x] AC-3: Real watcher remains wired to exact production rollback after proof passes.
- [x] AC-4: Tests prove proof/real separation and no cross-state mutation.
- [x] AC-5: Tech Lead reviews/commits and immediately resumes direct probe.

## Handoff

[Agent Message] From: product_manager To: developer

Implement only proof-mode separation in the maintained watchdog harness/runbook: proof-owned pointer/log/control plus no-op rollback; real watcher unchanged. Test exact 31-sample proof leaves production control state untouched and real watcher retains exact rollback. No deploy/Fedora mutation, no broader changes. Return immediately for Tech Lead review.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary

Implemented an explicit proof runner and no-op rollback in the maintained watchdog generator. Proof execution now owns its active pointer, control directory, log, trigger state, and rollback marker outside the production root. The generated real watcher and exact production rollback script remain unchanged

### Work Performed

- Added generated `run-watchdog-proof.sh` with a fixed 31-sample limit, proof-owned pointer and log, explicit proof attempt injection, and rejection of proof state under the production root
- Added generated `proof-rollback.sh`, which records a proof-local marker and performs no selector edit, Compose action, active-pointer deletion, or other production operation
- Added proof success and failure tests that checksum production selector, recreate log, control, and active-pointer fixtures before and after execution
- Added negative no-cross-state tests for linked production pointer, control, and log paths, plus assertions that the real watcher still defaults to the exact production rollback
- Ran maintained and generated Bash syntax checks, the complete watchdog behavioral suite, ShellCheck, `git diff --check`, and `staticeng_validate`; all pass
- Performed no deployment, Fedora/NAS access or mutation, credential use, request, selector change, service recreation, commit, or push

### Acceptance Criteria Coverage

- **AC-1: PASS.** The proof runner uses a dedicated proof pointer, proof attempt controls, proof log, and no-op rollback
- **AC-2: PASS.** The exact proof runner completes 31 mocked samples with unchanged production pointer, selector, recreate log, and control state
- **AC-3: PASS.** The real watcher still defaults to its attempt-local production rollback script, whose exact digest selector and Compose recreation command are unchanged
- **AC-4: PASS.** Success, failure, linked-pointer, linked-control, linked-log, and production-root rejection tests establish proof/real separation and no cross-state mutation
- **AC-5: PENDING.** Tech Lead review, commit, and immediate TASK-006 direct-probe resume remain outside Developer authority

### Documentation Impact

No product, architecture, technical, or CodeMap update is required. This changes only the governed operational proof harness and its tests, not steady-state product or runtime behavior

### Open Risks

The proof is local and mocked as required by the no-Fedora boundary. Tech Lead must independently review the proof invocation and exact real rollback wiring before committing or resuming TASK-006

### Recommended Next Step

Tech Lead should review and rerun `.staticeng/evidences/TASK-2026-09-04-002-fix-fedora-watchdog-harness/harness/test-watchdog-harness.sh`, inspect the generated proof and production rollback wiring, commit the approved task artifacts, and immediately resume the authorized TASK-006 direct probe

### Signed Handoff

[Agent Message] From: developer To: product_manager

TASK-2026-09-04-003 AC-1 through AC-4 PASS. The maintained generator now emits a proof runner with proof-owned pointer, log, controls, and no-op rollback. Exact 31-sample success and forced-failure tests prove no production selector, recreate log, control, or active-pointer mutation; linked production state is rejected. The real watcher retains the unchanged exact rollback digest and Compose action. Bash syntax, complete behavioral tests, ShellCheck, diff check, and StaticEng validation pass. No deploy, Fedora/NAS mutation, credential use, request, commit, or push occurred. Route immediately to Tech Lead for AC-5 review/commit and TASK-006 resume

## Tech Lead: Post Implementation Expectations

### Summary

PASS. Independent review and rerun confirm proof-owned state, exact 31-sample success, no-op proof rollback, unchanged production fixtures, and unchanged real exact rollback wiring

### Work Performed

- Reviewed the bounded generator and behavioral-test diff against TASK-003
- Independently reran the complete watchdog suite and ShellCheck with no failures
- Verified successful and forced-failure proof paths leave the production pointer, selector, recreate log, and control fixture unchanged
- Verified the generated real watcher still defaults to the exact production rollback script, digest, and Compose recreation command
- Ran `git diff --check` and `staticeng_validate`; both pass

### Acceptance Criteria Coverage

- **AC-1: PASS.** Proof pointer, attempt controls, logs, trigger state, and rollback markers are proof-owned; rollback is no-op
- **AC-2: PASS.** The proof exits zero after exactly 31 samples without changing checked production state
- **AC-3: PASS.** Real watcher rollback wiring and exact rollback action are unchanged
- **AC-4: PASS.** Success, failure, and cross-state rejection tests pass independently
- **AC-5: PASS.** Tech Lead approved closure and resumes the already authorized TASK-006 direct probe immediately after push

### Documentation Impact

No product, architecture, technical, or CodeMap documentation update is required because this is a bounded operational proof-harness correction

### Open Risks

No TASK-003 functional, OOM, or rollback blocker remains. TASK-006 retains all existing fail-closed production safeguards and stop conditions

### Recommended Next Step

Resume TASK-006 Reopen 7 direct-probe retry under its existing exact-digest, backup, watchdog, one-request, rollback, deadline, and NAS boundaries

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

TASK-003 PASS AND CLOSED. Independent review confirms proof-owned state, exact 31-sample success, no-op proof rollback, no checked production mutation, and unchanged real exact rollback. The complete behavioral suite, ShellCheck, diff check, and StaticEng validation pass. I am committing and non-force pushing this closure, then immediately resuming the authorized TASK-006 direct probe in this session
