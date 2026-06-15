# TASK-2026-06-12-001 Fix Onboarding Claim Session

## Summary

Implemented the onboarding claim response contract so a successful first-time claim returns a UI session token, success redirect URL, user email, and sanitized user object. Reopen fix: the claim path now validates the short-lived onboarding token from `GET /onboarding/get_token`, verifies the user still exists, reserves the invitation with `accepted_at`, rolls the reservation back if password update or session minting fails, and returns the session if the post-success accepted_at refresh fails because the invitation is already marked accepted.

## Acceptance Criteria Coverage

- AC-1: Covered by `test_onboarding_get_token_happy` and `test_get_token_returns_onboarding_token_without_minting_ui_key`; valid unused invite returns 200 and onboarding credentials.
- AC-2: Covered by claim response contract tests and existing frontend form tests; backend now returns `token` so the UI does not enter the missing-token error path. Local frontend test execution was blocked by the Vitest/Vite ESM loader issue logged in `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/frontend-onboarding-tests.log`.
- AC-3: Covered by `test_claim_onboarding_link_happy` and `test_claim_token_sets_accepted_at_after_password_written`; `POST /onboarding/claim_token` returns `token` and `login_url`.
- AC-4: Covered by `test_claim_token_sets_accepted_at_after_password_written` and `test_claim_token_returns_session_when_final_invite_update_fails`; successful claims reserve the invitation as accepted with `accepted_at` before session minting and return a session even if the later timestamp refresh fails.
- AC-5: Covered by `test_claim_token_rejects_already_used_link` and `test_claim_token_rejects_concurrent_reuse_before_password_write`; accepted or concurrently reserved invitations fail.
- AC-6: Covered by backend tests for valid claim response, already accepted invitation, missing user, mismatched user_id, expired invitation, missing/wrong onboarding token, invalid bearer token, password update exception rollback, final invite update failure behavior, and session mint rollback.
- AC-7: Evidence logs use placeholder invite IDs, test passwords, and synthetic token names only; no full live invite tokens, master keys, session tokens, or real passwords are included.

## Verification

- PASS: `uv run ruff check litellm/proxy/proxy_server.py tests/test_litellm/proxy/auth/test_onboarding.py tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py` in `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/ruff-check.log`.
- PASS: `uv run python -m pytest tests/test_litellm/proxy/auth/test_onboarding.py tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py` (`26 passed, 22 warnings`) in `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/backend-onboarding-tests.log`.
- PASS: `python -m py_compile litellm/proxy/proxy_server.py` in `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/syntax-check.log`.
- BLOCKED: `npm test -- --run src/app/onboarding/OnboardingForm.test.tsx src/app/\(dashboard\)/hooks/onboarding/useOnboarding.test.ts` failed before tests ran due to `ERR_REQUIRE_ESM` loading `vite` through `vitest/dist/config.cjs`; see `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/frontend-onboarding-tests.log`.
- BLOCKED: `staticeng_validate` failed on pre-existing repository CodeMap coverage/configuration issues unrelated to this task; see `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/staticeng-validate.log`.

## Files Changed

- `litellm/proxy/proxy_server.py`
- `tests/test_litellm/proxy/auth/test_onboarding.py`
- `tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py`
- `ui/litellm-dashboard/src/components/networking.tsx`
- `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/ruff-check.log`
- `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/backend-onboarding-tests.log`
- `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/frontend-onboarding-tests.log`
- `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/syntax-check.log`
- `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/staticeng-validate.log`
