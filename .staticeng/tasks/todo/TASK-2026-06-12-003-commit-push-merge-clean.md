---
task_id: TASK-2026-06-12-003-commit-push-merge-clean
complexity: standard
track: implementation
slice: core
status: todo
assigned_to: tech_lead
handoff_from: product_manager
scr: none
parent: TASK-2026-06-12-002-release-onboarding-fix
discussion: none
---

# Commit Push Merge And Clean Worktree

## Classification

- complexity: standard
- track: implementation
- slice: core

## Context

The user requested: commit all current `/home/staticduo/git/litellm` changes, push them, split into separate commits with clear explanations, then merge this branch into main without deleting the branch.

Current branch at task creation:
- `staticduo-production-main`
- Upstream/tracking shown as `fork/main`
- Remote `fork` is `git@github.com:jibanez-staticduo/litellm.git`
- Remote `origin` is upstream BerriAI and should not be pushed to for this task.

Current dirty changes are expected and should be separated logically:
1. MCP delete/idempotency cleanup code and tests:
   - `litellm/proxy/_experimental/mcp_server/db.py`
   - `litellm/proxy/management_endpoints/mcp_management_endpoints.py`
   - `tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py`
2. Onboarding claim session fix code and tests:
   - `litellm/proxy/proxy_server.py`
   - `tests/test_litellm/proxy/auth/test_onboarding.py`
   - `tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py`
   - `ui/litellm-dashboard/src/components/networking.tsx`
3. StaticEng SCR/task/evidence/discussion artifacts under `.staticeng/`.

Important release context:
- The onboarding fix has already been released from `/home/staticduo/git/litellm-production-main` and pushed to `fork/main` through commit `50c1450db4df39c2658439e5507ac6e1091dbb5b`.
- This task is to clean and reconcile the `/home/staticduo/git/litellm` worktree and branch state per the user's request.

## Acceptance Criteria

AC-1. All current intended changes in `/home/staticduo/git/litellm` are committed in logical, separate commits with clear messages.

AC-2. The current branch is pushed to the `fork` remote without pushing to upstream `origin`.

AC-3. The branch is merged into `main` for the fork/repo without deleting `staticduo-production-main`.

AC-4. Worktrees involved in this task end clean or any residual intentionally untracked/dirty files are explicitly reported.

AC-5. Verification includes `git status`, recent log, remote branch state, and merge result.

AC-6. No secrets, `.env` contents, passwords, tokens, master keys, or session tokens are committed or logged.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-06-12-003-commit-push-merge-clean/` with:
- `SUMMARY.md` mapping ACs to verification.
- logs for pre-status, diffs reviewed, commits, push, merge, final status.

## Handoff

[Agent Message] From: product_manager To: tech_lead
Please execute the user's git cleanup request safely. Inspect status/diff/log before each commit. Stage only intended logical groups. Do not push to `origin`; use the private `fork` remote. Preserve the branch; do not delete `staticduo-production-main`. If `main` ambiguity exists, prefer the fork's main (`fork/main`) rather than upstream BerriAI `origin/main`, and report the exact local/remote refs used. Return Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, Recommended Next Step with commit hashes and final status.
