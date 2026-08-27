---
id: TASK-2026-08-27-008-merge-release-uvicorn-redaction
complexity: standard
track: implementation
slice: polish
status: done
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
- [x] AC-1: Commit only the intended source, tests, Task 023 closure/evidence, and this release closure state on `main`; push successfully to `origin/main`.
- [x] AC-2: Confirm whether a separate feature branch exists locally or remotely; delete it only after proving its work is contained in `main`, or record that no branch exists.
- [x] AC-3: Build and publish one immutable image attributable to the resulting main commit, then deploy that exact digest to Fedora and NAS with rollback references captured.
- [x] AC-4: Both Fedora and NAS remain healthy, LazyMCP responds, redacted access logging works, and bounded post-deployment logs contain no formatter traceback or raw probe marker.
- [x] AC-5: Final evidence identifies the Git commit, image digest, both running image IDs, rollback digests, verification results, and documentation impact.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/` with `SUMMARY.md` and redacted logs for Git scope, branch disposition, image provenance, both deployments, and verification.

## Acceptance Criteria Verification Map
- [x] AC-1
  - **Method:** Git diff/status/log and remote verification
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/`
- [x] AC-2
  - **Method:** local/remote branch containment inspection
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/`
- [x] AC-3
  - **Method:** immutable image build/push and scoped host deployments
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/`
- [x] AC-4
  - **Method:** host health, LazyMCP smoke, and bounded clean logs
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/`
- [x] AC-5
  - **Method:** evidence review and registry closure
  - **Evidence:** `.staticeng/evidences/TASK-2026-08-27-008-merge-release-uvicorn-redaction/SUMMARY.md`

## Handoff
[Agent Message] From: product_manager To: tech_lead

This is the authorized direct-path commit/release task. The current branch is already `main`; do not manufacture a merge commit or branch. Preserve unrelated dirty files and untracked CodeMaps. Stage only the reviewed correction, its tests, relevant Task 023 closure/evidence, and this task's required closure artifacts. Build and deploy only after the commit is on `origin/main`.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Committed and pushed the reviewed correction and Task 023 closure as `64a3b83bf0bdd8813890d20ba7b6b57fc034bb95` on `main`
- Confirmed no distinct local or `origin` branch matching the Uvicorn redaction fix existed, so no branch deletion was required
- Built once from an isolated clean worktree at the exact main commit and published immutable image `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`
- Captured Fedora rollback digest `sha256:85349c2990080596f7e6281c4ca13344506ded9460eba388286024044a766f0c` and NAS rollback digest `sha256:8a688990cb66fa7bd804fc8ac7423dd487dfd876d10fa7ef384096ab373ff6e5`
- Deployed the exact release digest to Fedora first and NAS second by changing only each stack's `LITELLM_IMAGE` and recreating only `litellm` with `--no-deps`
- Verified both containers healthy with zero restarts and OOM false, readiness HTTP 200, connected LazyMCP status, expected redacted access output, zero raw probe-marker occurrences, and zero matching formatter errors in bounded post-deployment logs
- Product, architecture, technical, and CodeMap documentation updates are not required for this internal logging compatibility release
- AC-1 through AC-5 pass; rollback was not required
