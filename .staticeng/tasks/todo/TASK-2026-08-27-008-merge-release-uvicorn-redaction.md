---
id: TASK-2026-08-27-008-merge-release-uvicorn-redaction
complexity: standard
track: implementation
slice: polish
status: active
scr: null
parent: TASK-2026-08-26-023-fix-uvicorn-access-redaction
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-27-008 - Merge and release Uvicorn redaction fix

## Objective
Finalize the reviewed access-log correction in Git main, deploy an immutable main-commit artifact to Fedora and NAS, verify both runtimes, and remove any merged source branch.

## Acceptance Criteria
- [ ] AC-1: Commit only the intended source, tests, Task 023 closure/evidence, and this release closure state on `main`; push successfully to `origin/main`.
- [ ] AC-2: Confirm whether a separate feature branch exists locally or remotely; delete it only after proving its work is contained in `main`, or record that no branch exists.
- [ ] AC-3: Build and publish one immutable image attributable to the resulting main commit, then deploy that exact digest to Fedora and NAS with rollback references captured.
- [ ] AC-4: Both Fedora and NAS remain healthy, LazyMCP responds, redacted access logging works, and bounded post-deployment logs contain no formatter traceback or raw probe marker.
- [ ] AC-5: Final evidence identifies the Git commit, image digest, both running image IDs, rollback digests, verification results, and documentation impact.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/` with `SUMMARY.md` and redacted logs for Git scope, branch disposition, image provenance, both deployments, and verification.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** Git diff/status/log and remote verification
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/`
- [ ] AC-2
  - **Method:** local/remote branch containment inspection
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/`
- [ ] AC-3
  - **Method:** immutable image build/push and scoped host deployments
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/`
- [ ] AC-4
  - **Method:** host health, LazyMCP smoke, and bounded clean logs
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/`
- [ ] AC-5
  - **Method:** evidence review and registry closure
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/SUMMARY.md`

## Handoff
[Agent Message] From: product_manager To: tech_lead

This is the authorized direct-path commit/release task. The current branch is already `main`; do not manufacture a merge commit or branch. Preserve unrelated dirty files and untracked CodeMaps. Stage only the reviewed correction, its tests, relevant Task 023 closure/evidence, and this task's required closure artifacts. Build and deploy only after the commit is on `origin/main`.
