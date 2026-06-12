# TASK-2026-06-12-002 Release Onboarding Fix

## Summary

Committed the onboarding claim session fix and released it to the local LiteLLM stack and Fedora using `/home/staticduo/git/release-litellm.sh`. The release image is `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260612-onboarding-claim-session`; the stable tag `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-latest` was pushed to the same digest.

## Acceptance Criteria Coverage

- AC-1: PASS. Source fix committed as `89cb8d2916d8551bef83ffbe3cbf121225af4f20`.
- AC-2: PASS. `/home/staticduo/git/release-litellm.sh --tag staticduo-gpt-lazymcp-main-20260612-onboarding-claim-session` built and pushed the unique tag plus `staticduo-gpt-lazymcp-main-latest`; digest `sha256:102158c62182f4db494be543dbb09580b4074dd69f87967a15e77ba3a5349a79`.
- AC-3: PASS. Local container `litellm` runs `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260612-onboarding-claim-session` with Docker health `healthy`; readiness returned `200` with `{"status":"healthy","db":"connected"}`.
- AC-4: PASS. Fedora container `litellm` runs `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260612-onboarding-claim-session` with Docker health `healthy`; readiness returned `200` with `{"status":"healthy","db":"connected"}`.
- AC-5: PASS. Evidence includes commit hashes, release log, local verification, Fedora verification, and readiness logs under this evidence directory.
- AC-6: PASS. Evidence logs avoid `.env` output, passwords, master keys, full invite tokens, and session tokens.

## Verification

- PASS: `uv run ruff check litellm/proxy/proxy_server.py tests/test_litellm/proxy/auth/test_onboarding.py tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py` in `logs/ruff-check.log`.
- PASS: `uv run python -m pytest tests/test_litellm/proxy/auth/test_onboarding.py tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py` after `uv sync --all-extras --group proxy-dev`; `26 passed, 22 warnings` in `logs/backend-onboarding-tests-rerun.log`.
- PASS: `python -m py_compile litellm/proxy/proxy_server.py` in `logs/syntax-check.log`.
- PASS: Commit verification captured `89cb8d2916d8551bef83ffbe3cbf121225af4f20` in `logs/commit-verification.log`. Follow-up evidence commit is `3d814838ae7f41efa44213bbf31201d17d42afcfe`.
- PASS: Release log in `logs/release.log` shows image build/push for `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260612-onboarding-claim-session`, stable tag push for `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-latest`, rollback tag `docker.staticduo.com/litellm:rollback-20260612-130841`, and deployment to local plus Fedora.
- PASS: Local verification in `logs/local-verification.log` and `logs/local-readiness.log` shows the new image running healthy with readiness `200`.
- PASS: Fedora verification in `logs/fedora-verification.log` and `logs/fedora-readiness.log` shows the new image running healthy with readiness `200`.
- BLOCKED: `staticeng_validate` tool reports pre-existing CodeMap coverage/configuration issues in `/home/staticduo/git/litellm`; `staticeng_validate` CLI is not installed in the production worktree shell. See `logs/staticeng-validate.log` and StaticEng tool output in session.

## Files Changed

- `litellm/proxy/proxy_server.py`
- `tests/test_litellm/proxy/auth/test_onboarding.py`
- `tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py`
- `ui/litellm-dashboard/src/components/networking.tsx`
- `.staticeng/tasks/todo/TASK-2026-06-12-001-fix-onboarding-claim-session.md`
- `.staticeng/tasks/todo/TASK-2026-06-12-002-release-onboarding-fix.md`
- `.staticeng/evidences/TASK-2026-06-12-002-release-onboarding-fix/`

## Release Details

- Source commit: `89cb8d2916d8551bef83ffbe3cbf121225af4f20`
- Evidence commit: `3d814838ae7f41efa44213bbf31201d17d42afcfe`
- Image tag: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260612-onboarding-claim-session`
- Stable tag: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-latest`
- Image digest: `sha256:102158c62182f4db494be543dbb09580b4074dd69f87967a15e77ba3a5349a79`
- Rollback tag: `docker.staticduo.com/litellm:rollback-20260612-130841`
