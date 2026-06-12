---
task_id: TASK-2026-06-12-002-release-onboarding-fix
complexity: standard
track: implementation
slice: core
status: todo
assigned_to: tech_lead
handoff_from: product_manager
scr: SCR-2026-06-12-001-onboarding-claim-session-token
parent: TASK-2026-06-12-001-fix-onboarding-claim-session
discussion: DISCUSSION-003
---

# Commit And Release Onboarding Fix

## Classification

- complexity: standard
- track: implementation
- slice: core

## Context

The onboarding claim session contract fix is implemented and reviewed in `TASK-2026-06-12-001-fix-onboarding-claim-session`. The user now explicitly requested committing the fix and releasing it on both this host and Fedora.

Release script:
- `/home/staticduo/git/release-litellm.sh`
- Default production workdir: `/home/staticduo/git/litellm-production-main`
- Local stack dir: `/volume2/docker/litellm`
- Fedora host: `fedora`
- Fedora stack dir: `/home/staticduo/docker/litellm`

Important constraints:
- Do not use the `litellm_admin` MCP in this environment.
- Preserve unrelated dirty worktree changes. There are existing MCP-related dirty files in `/home/staticduo/git/litellm`; do not include them in the onboarding commit unless they are already committed in the production release workspace.
- Commit only intended onboarding fix files and required StaticEng release/onboarding artifacts.
- Verify release evidence without logging secrets.

## Acceptance Criteria

AC-1. The onboarding fix is committed with a clear task-scoped commit message.

AC-2. The release image is built and pushed with a unique tag and stable tag by `/home/staticduo/git/release-litellm.sh`.

AC-3. The local LiteLLM stack on this host is updated to the new image and reports healthy/running.

AC-4. The Fedora LiteLLM stack is updated to the new image and reports healthy/running.

AC-5. Evidence includes commit hash, image tag, release log, local verification, and Fedora verification.

AC-6. No secrets, passwords, master keys, full invitation tokens, or session tokens are logged in evidence.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-06-12-002-release-onboarding-fix/` with:
- `SUMMARY.md` mapping ACs to verification.
- `logs/` containing commit/status/release/local/Fedora verification logs.
- redacted logs only; do not include `.env` contents or secrets.

## Handoff

[Agent Message] From: product_manager To: tech_lead
Please perform safe commit and release execution for the onboarding fix. Inspect both `/home/staticduo/git/litellm` and `/home/staticduo/git/litellm-production-main` before committing or releasing. Preserve unrelated dirty changes. Use the release script to deploy to both local and Fedora. Return Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, Recommended Next Step with exact commit hash, image tag, and verification evidence paths.
