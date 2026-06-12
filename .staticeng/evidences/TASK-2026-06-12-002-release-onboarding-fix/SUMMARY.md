# TASK-2026-06-12-002 Release Onboarding Fix

## Summary

Prepared the onboarding claim session fix for production release. Release deployment evidence will be appended after the clean production worktree commit and release script run.

## Acceptance Criteria Coverage

- AC-1: Pending commit.
- AC-2: Pending release script execution.
- AC-3: Pending local stack verification.
- AC-4: Pending Fedora stack verification.
- AC-5: Pending release and verification logs.
- AC-6: Evidence logs avoid `.env` output, passwords, master keys, full invite tokens, and session tokens.

## Verification

- PASS: `uv run ruff check litellm/proxy/proxy_server.py tests/test_litellm/proxy/auth/test_onboarding.py tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py` in `logs/ruff-check.log`.
- PASS: `uv run python -m pytest tests/test_litellm/proxy/auth/test_onboarding.py tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py` after `uv sync --all-extras --group proxy-dev`; `26 passed, 22 warnings` in `logs/backend-onboarding-tests-rerun.log`.
- PASS: `python -m py_compile litellm/proxy/proxy_server.py` in `logs/syntax-check.log`.
- BLOCKED: `staticeng_validate` tool reports pre-existing CodeMap coverage/configuration issues in `/home/staticduo/git/litellm`; `staticeng_validate` CLI is not installed in the production worktree shell. See `logs/staticeng-validate.log` and StaticEng tool output in session.

## Files Changed

- `litellm/proxy/proxy_server.py`
- `tests/test_litellm/proxy/auth/test_onboarding.py`
- `tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py`
- `ui/litellm-dashboard/src/components/networking.tsx`
- `.staticeng/tasks/todo/TASK-2026-06-12-001-fix-onboarding-claim-session.md`
- `.staticeng/tasks/todo/TASK-2026-06-12-002-release-onboarding-fix.md`
- `.staticeng/evidences/TASK-2026-06-12-002-release-onboarding-fix/`
