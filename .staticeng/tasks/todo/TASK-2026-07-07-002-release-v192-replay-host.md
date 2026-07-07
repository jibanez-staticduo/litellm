---
task_id: TASK-2026-07-07-002-release-v192-replay-host
complexity: standard
track: implementation
slice: qa
status: todo
assigned_to: developer
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

## Blocker Report

Release was attempted on 2026-07-07 after committing the StaticEng preflight artifacts that made the source worktree dirty.

The release script successfully built and pushed `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-20260707`, created rollback tag `docker.staticduo.com/litellm:rollback-20260707-131635`, updated the local stack, recreated `litellm`, and skipped Fedora deploy.

Post-deploy readiness and LazyMCP smoke worked, but recent logs showed a release-blocking regression:

```text
Spend tracking - failed to update user/team spend in cache. Budget enforcement may use stale spend values. ... name 'CacheCodec' is not defined
```

The release was rolled back to `docker.staticduo.com/litellm:rollback-20260707-131635`. Rollback verification passed: container running, Docker health healthy, readiness `200 {"status":"healthy","db":"connected"}`, liveliness `200 "I'm alive!"`.

Resolution needed: fix the missing `CacheCodec` import/availability in `litellm/proxy/proxy_server.py`, verify spend/cache behavior, then retry the release.

## Reopen History

- 2026-07-07: PMA reopened after user approved fixing, testing, rebuilding, and retrying the release. Scope remains the same release blocker. Do not use `workflow_runner` for this reopen. Assigned to `developer` for a minimal code fix plus targeted verification and local release retry.

## Reopen Acceptance Criteria Addendum

AC-11. `CacheCodec` is available in `litellm/proxy/proxy_server.py` spend tracking cache update paths without introducing broad refactors.

AC-12. Targeted tests cover or exercise spend/cache behavior enough to catch the prior `NameError`.

AC-13. Code fix and any pre-release StaticEng state are committed before retrying the release, because `/home/staticduo/git/release-litellm.sh` requires a clean source worktree.

AC-14. Release retry uses a new image tag, not the previously failed tag. Use `staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707` unless there is a clear reason to choose another unique tag.

AC-15. Release retry remains local-host-only: `--no-upstream-merge --no-fedora-deploy`, push only to `origin`, never to `upstream`.

AC-16. If the retry succeeds, production ends on the new cachecodecfix image, healthy, with readiness DB connected and no new `CacheCodec is not defined` log entries after deployment. If it fails, rollback to the previous healthy image and report exact state.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- 2026-07-07 pre-release fix: Added the missing `CacheCodec` import to `litellm/proxy/proxy_server.py`.
- Added focused regression coverage for cached user/team spend serialization in `tests/test_litellm/proxy/proxy_server/test_spend_counters.py`.
- Pre-release verification passed: `py_compile`, focused `CacheCodec` import check, and targeted pytest (`test_cache_codec.py` plus `test_spend_counters.py`).
- Next step: commit and push this pre-release fix/state to `origin main`, then run the local-host-only release retry from a clean source worktree with tag `staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`.
