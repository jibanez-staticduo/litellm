---
scr_id: SCR-2026-06-12-001-onboarding-claim-session-token
status: implemented
owner: product_manager
created: 2026-06-12
related_task: TASK-2026-06-12-001-fix-onboarding-claim-session
---

# SCR-2026-06-12-001: Onboarding Claim Session Token Contract

## Problem

A new LiteLLM user can open an unused invitation link and submit a password, but the Admin UI then shows `Failed to start session. Please try again.` The first `POST /onboarding/claim_token` returns 200 and consumes the invitation, while later retries return 401 because the link is already accepted.

The likely contract mismatch is that the frontend expects the claim response to include a session token, but the backend claim endpoint may return only the user object in the deployed image.

## Approved Behavior

After a valid first-time password claim, the onboarding flow must either return a response containing the session data required by the UI or redirect the user to a working login path. The invitation must still be marked used after a successful claim, and reused/expired/mismatched invitations must remain rejected.

## Scope

In scope:
- Backend and/or frontend onboarding claim flow.
- Regression tests for valid claim response contract and rejected invalid claims.
- Local validation against relevant tests.

Out of scope:
- Email delivery changes.
- Allowing consumed invitations to be reused.
- Logging passwords, full invitation tokens, master keys, or session tokens.
- Using the `litellm_admin` MCP in this environment.

## Acceptance Criteria

AC-1. With a new unused invite, `GET /onboarding/get_token?invite_link=<id>` returns 200.

AC-2. The user can create a password through the UI flow without seeing `Failed to start session. Please try again.`

AC-3. `POST /onboarding/claim_token` returns a response that lets the frontend start a session or redirect correctly.

AC-4. The invitation is marked used after a successful claim.

AC-5. Reusing the accepted invitation still fails correctly.

AC-6. Tests cover valid claim response contract, already accepted invitation, missing user or mismatched user_id, and expired invitation.

AC-7. No passwords, full invitation tokens, master keys, or session tokens are logged or committed in code/evidence.
