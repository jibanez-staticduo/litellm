---
task_id: TASK-2026-06-12-001-fix-onboarding-claim-session
complexity: standard
track: implementation
slice: core
status: done
assigned_to: product_manager
handoff_from: product_manager
scr: SCR-2026-06-12-001-onboarding-claim-session-token
parent: none
discussion: DISCUSSION-003
---

# Fix Onboarding Claim Session Contract

## Classification

- complexity: standard
- track: implementation
- slice: core

## Context

Fedora `litellm.defend.tech` shows `Failed to start session. Please try again.` after a new invited user submits email/password on the claim screen. The observed live sequence is:

- `GET /onboarding/get_token?invite_link=<invite-id>` -> 200
- first `POST /onboarding/claim_token` -> 200
- retries of `POST /onboarding/claim_token` -> 401
- later `GET /onboarding/get_token?invite_link=<invite-id>` -> 401

This indicates the first claim likely saves the password and consumes the invite, but the frontend does not receive the token/session contract it expects. The affected live invited email was `staticduo@gmail.com`; use it only as diagnostic context and do not hard-code it in code or tests.

Do not use the current environment's `litellm_admin` MCP because it points to a different LiteLLM instance.

Relevant files to inspect:
- `litellm/proxy/proxy_server.py`
- `tests/test_litellm/proxy/auth/test_onboarding.py`
- `tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py`
- `ui/litellm-dashboard/src/app/onboarding/OnboardingForm.tsx`
- `ui/litellm-dashboard/src/app/onboarding/OnboardingForm.test.tsx`
- hooks under `ui/litellm-dashboard/src/app/(dashboard)/hooks/onboarding/`

## Acceptance Criteria

AC-1. With a new unused invite, `GET /onboarding/get_token?invite_link=<id>` returns 200.

AC-2. The user can create a password through the UI flow without seeing `Failed to start session. Please try again.`

AC-3. `POST /onboarding/claim_token` returns a response that lets the frontend start a session or redirect correctly.

AC-4. The invitation is marked used after a successful claim.

AC-5. Reusing the accepted invitation still fails correctly.

AC-6. Tests cover valid claim response contract, already accepted invitation, missing user or mismatched user_id, and expired invitation.

AC-7. No passwords, full invitation tokens, master keys, or session tokens are logged or committed in code/evidence.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/` with:
- `SUMMARY.md` mapping ACs to verification.
- logs for targeted backend and frontend tests.
- no secrets, passwords, full invitation tokens, master keys, or session tokens.

No screenshots are required unless UI behavior is manually exercised in a browser.

## Handoff

[Agent Message] From: product_manager To: developer
Please implement the minimal safe fix for the onboarding claim session contract. Prefer backend compatibility if the frontend already expects a token from `claim_token`; otherwise adjust the frontend flow if safer. Preserve one-time invite semantics and avoid logging secrets. Run targeted backend/frontend tests if the environment supports them; if blocked, capture the blocker in evidence. Return Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, Recommended Next Step.

## Reopen History

- 2026-06-12: Reopened after Tech Lead review found same-scope consistency defects: invite reservation was not rolled back when password update raised, and final accepted_at update failure could leave password/session state inconsistent.

# Post Implementation Task Updates

## developer: Post Implementation Expectations

Implemented backend-compatible onboarding claim session handling in `litellm/proxy/proxy_server.py`. `GET /onboarding/get_token` now returns a short-lived onboarding JWT in the decoded `key` claim instead of minting a full UI session key on page load. `POST /onboarding/claim_token` now validates that onboarding JWT, verifies the user still exists, atomically reserves the unused invitation, writes the password, mints the final UI session JWT, finalizes `accepted_at`, and returns `login_url`, `token`, `user_email`, and sanitized `user` so the existing UI success path can start a session.

Added backend regression coverage in `tests/test_litellm/proxy/auth/test_onboarding.py` for missing user rollback. Existing onboarding tests cover valid claim response contract, already accepted invite, user ID mismatch, expired invite, wrong/missing onboarding token, concurrent reuse, and session mint rollback.

Removed a noisy `console.log(data)` from `ui/litellm-dashboard/src/components/networking.tsx` so claim responses are not logged in the browser console.

Evidence was created under `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/`. Backend targeted tests passed. Frontend targeted tests were attempted but blocked before execution by a local Vitest/Vite `ERR_REQUIRE_ESM` config-load failure; blocker is recorded in the evidence logs.

## developer: Reopen 1 Post Implementation Expectations

Addressed Tech Lead consistency findings in `litellm/proxy/proxy_server.py`. The invite reservation now writes `accepted_at` when it flips `is_accepted=True`, and password update exceptions now roll that reservation back before returning a 500. The final post-success invitation timestamp refresh is now best-effort: if it fails after the password and session token are created, the endpoint still returns the session because the invite is already accepted and has `accepted_at` from reservation time.

Added regression tests in `tests/test_litellm/proxy/auth/test_onboarding.py` for password update exception rollback and final invite update failure behavior. Updated evidence logs and summary; targeted backend onboarding tests now pass with 26 tests.

## developer: Reopen 1 Lint Fix

Removed the unused `pytest` import from `tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py`. Targeted ruff now passes, and targeted backend onboarding tests still pass with 26 tests. Evidence logs and summary were updated.
