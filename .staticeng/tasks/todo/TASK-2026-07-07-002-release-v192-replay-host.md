---
task_id: TASK-2026-07-07-002-release-v192-replay-host
complexity: standard
track: implementation
slice: qa
status: todo
assigned_to: workflow_runner
handoff_from: product_manager
scr: none
parent: TASK-2026-07-07-001-sync-upstream-v192-replay
discussion: DISCUSSION-002
---

# Release LiteLLM v1.92 Replay On This Host

## Classification

- complexity: standard
- track: implementation
- slice: qa

## Active Discussions

- DISCUSSION-002: Release LiteLLM v1.92 replay on this host

## Context

The user approved releasing the newly replayed LiteLLM fork main on this host and checking whether it works.

Current intended source:
- Worktree: `/home/staticduo/git/litellm`
- Branch: `main`
- Commit: `29373e89c1c33624cfbcbc7ec432886bc278b8cc`
- Remote `origin`: user's fork `git@github.com:jibanez-staticduo/litellm.git`
- Remote `upstream`: BerriAI `https://github.com/BerriAI/litellm`

Deployment stack:
- Local stack dir: `/volume2/docker/litellm`
- Compose file: `/volume2/docker/litellm/docker-compose.yaml`
- Existing container before task: `litellm` using `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260612-onboarding-claim-session`, healthy.
- `litellm-admin-mcp`, `litellm-admin-mcp-compat`, and `litellm-redis` are also running and should not be intentionally disturbed beyond normal compose dependency behavior.

Release script:
- `/home/staticduo/git/release-litellm.sh`
- Default values in the script point at older workdir/remotes and Fedora deploy, so pass explicit environment/flags.

Approved local-host-only release command:

```bash
PRODUCTION_WORKDIR=/home/staticduo/git/litellm \
UPSTREAM_REMOTE=upstream \
FORK_REMOTE=origin \
TAG=staticduo-gpt-lazymcp-v1.92-replay-20260707 \
/home/staticduo/git/release-litellm.sh --no-upstream-merge --no-fedora-deploy --tag staticduo-gpt-lazymcp-v1.92-replay-20260707
```

Expected script behavior:
- Requires clean source worktree before build.
- Builds Docker image from `/home/staticduo/git/litellm`.
- Pushes `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-20260707` and the stable tag.
- Creates/pushes rollback tag for the current deployed image if possible.
- Updates `/volume2/docker/litellm/.env` `LITELLM_IMAGE`.
- Runs `docker compose pull litellm` and `docker compose up -d litellm` for the local stack.
- Skips Fedora deploy.

Important safety notes:
- Do not push to `upstream`.
- Do not log or expose `.env` contents, master keys, API keys, tokens, cookies, or private keys.
- If verification needs a secret, use it locally without printing it.
- If the release fails after updating `.env` or container state, either roll back using the script-created rollback image or report a clear rollback command.
- The current dirty `.staticeng/.config/runtime/discussions.json` is expected from starting DISCUSSION-002; do not treat it as a product-code blocker, but include StaticEng closure artifacts in the final commit if changed.

## Acceptance Criteria

AC-1. Release uses source commit `29373e89c1c33624cfbcbc7ec432886bc278b8cc` from `/home/staticduo/git/litellm` `main`.

AC-2. Image `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-20260707` is built and pushed, or failure is reported before deployment with logs.

AC-3. Existing deployed image is recorded and rollback image/tag is created or rollback path is explicitly reported if rollback tagging is unavailable.

AC-4. Local stack `/volume2/docker/litellm` is updated to the new image and `litellm` container is running healthy.

AC-5. Fedora deploy is not performed.

AC-6. Post-deploy checks include at minimum container status, recent logs, `/health/readiness`, and one LazyMCP/MCP smoke check if feasible without exposing secrets.

AC-7. If the new release is unhealthy or core smoke checks fail, rollback is performed or the user is given a precise rollback command and current service impact.

AC-8. Evidence packet exists with `SUMMARY.md`, logs, final image tag/digest if available, verification output, and AC coverage.

AC-9. Final git worktree status is clean after committing StaticEng release evidence/closure artifacts, or any residual changes are explicitly reported.

AC-10. No secrets, `.env` contents, master keys, API keys, tokens, cookies, private keys, or session tokens are committed or logged.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-07-07-002-release-v192-replay-host/` with:
- `SUMMARY.md` mapping ACs to verification.
- `logs/` containing safe command output for preflight, build/push, deployment, health checks, smoke checks, final Docker state, and final git status.
- Do not store unredacted secrets or `.env` content in evidence.

## Handoff

[Agent Message] From: product_manager To: workflow_runner
Please release the current LiteLLM `main` commit `29373e89c1c33624cfbcbc7ec432886bc278b8cc` on this host using the explicit local-host-only release command in this task. Verify preflight state, run the release, confirm Fedora deploy is skipped, validate health/readiness and LazyMCP/MCP if feasible, handle rollback if needed, produce the evidence packet, update/archive the task, commit StaticEng evidence/closure artifacts, and push only to `origin`. Return Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, Recommended Next Step, final image tag/digest, container status, and rollback tag/path.
