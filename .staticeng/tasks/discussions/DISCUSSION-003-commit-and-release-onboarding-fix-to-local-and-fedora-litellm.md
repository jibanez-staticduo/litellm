---
id: DISCUSSION-003
title: "Commit and release onboarding fix to local and Fedora LiteLLM"
status: closed
summarized_by: business_analyst
source: runtime-transcript
---

# Discussion Summary

## Topic
Commit and release the completed LiteLLM onboarding claim-token session-contract fix on the local host and Fedora deployment.

## Purpose
Capture the PMA handoff and user request so the next workflow can safely commit the reviewed onboarding fix, release it locally and on Fedora, and validate the production-like onboarding path.

## Repository Truth Relevant To This Discussion
- `TASK-2026-06-11-003-clone-selected-mcps-fedora` is already marked completed in `.staticeng/tasks/todo/TASK-2026-06-11-003-clone-selected-mcps-fedora.md` and registered in `.staticeng/tasks/done.md`.
- The onboarding bug fix has been implemented and reviewed by Tech Lead.
- The primary backend change is in `litellm/proxy/proxy_server.py:13570`.
- The frontend logging cleanup is in `ui/litellm-dashboard/src/components/networking.tsx:2071`.
- Implementation evidence exists under `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/`.

## Facts Established
- `POST /onboarding/claim_token` now returns `token`, `login_url`, `user_email`, and `user`.
- `GET /onboarding/get_token` now returns a short onboarding token instead of a premature final session token.
- Claim flow validates the short onboarding token before creating a session.
- Invite one-time behavior is preserved: the invite is reserved with `is_accepted=True`, rollback occurs if saving the password or creating the session fails, and reusing the invite still fails.
- `console.log(data)` was removed from the frontend claim path to avoid logging responses that contain tokens.
- Backend validation passed with `uv run ruff check litellm/proxy/proxy_server.py tests/test_litellm/proxy/auth/test_onboarding.py tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py`.
- Backend tests passed with `uv run python -m pytest tests/test_litellm/proxy/auth/test_onboarding.py tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py`; result was `26 passed`.
- Frontend tests were attempted but blocked by a local `Vitest/Vite ERR_REQUIRE_ESM` issue; the blocker is documented in evidence.
- `staticeng_validate` remains blocked by preexisting CodeMap issues, not by the onboarding fix.
- No commit had been made at the time of this discussion.
- No Fedora deploy had been performed at the time of this discussion.

## Requirements Captured
- Commit the completed onboarding fix.
- Release/deploy the fix on the current local host.
- Release/deploy the fix on Fedora.
- Validate the deployed fix with a new invite against `https://litellm.defend.tech`.
- Preserve all security-relevant behavior around token handling and invite one-time use.
- Avoid reintroducing frontend logging of token-bearing responses.
- Use existing implementation evidence and validation logs when preparing closure or release notes.

## Constraints
- Do not treat the blocked frontend test run as proof of failure; it is blocked by local `Vitest/Vite ERR_REQUIRE_ESM` and already documented.
- Do not treat the blocked `staticeng_validate` result as caused by this fix; it is due to preexisting CodeMap problems.
- Commit and release should include the reviewed fix and its StaticEng evidence/task closure artifacts as appropriate.
- Production-like validation should use a new invite because invite reuse is expected to fail.
- Any public-facing commit or PR text should follow repository guidance in `CLAUDE.md`, including no AI attribution and no customer names.

## Non-Goals
- Do not redesign the onboarding flow beyond committing and releasing the already implemented fix.
- Do not change invite one-time semantics.
- Do not broaden scope to resolve unrelated CodeMap validation issues.
- Do not broaden scope to fix the local frontend `Vitest/Vite ERR_REQUIRE_ESM` blocker unless PMA creates or assigns separate work.
- Do not use a reused invite as the success validation path.

## Decisions Made
- Proceed with commit of the completed onboarding fix.
- Proceed with release on both the local host and Fedora.
- Validate release using a fresh invite at `https://litellm.defend.tech`.
- Carry forward the existing backend test and lint results as valid implementation evidence.
- Treat frontend test and StaticEng validation blockers as known preexisting/local blockers rather than release blockers for this specific fix, unless later validation reveals otherwise.

## Assumptions
- The Tech Lead review is complete and no further product requirement review is needed before commit/release.
- The repository state still contains the implemented onboarding fix and related evidence artifacts.
- The deployment process for the local host and Fedora already exists or is known to the implementation/release agent.
- A fresh invite can be created or obtained for validation on `https://litellm.defend.tech`.

## Open Questions
- What exact release commands or runbook should be used for the current local host deployment?
- What exact release commands or runbook should be used for the Fedora LiteLLM deployment?
- Who will provide or create the fresh invite needed for validation on `https://litellm.defend.tech`?
- Should the blocked frontend test and `staticeng_validate` results be re-run after deployment, or only referenced from existing evidence?

## Risks Or Concerns
- Deploying without a fresh-invite validation could miss environment-specific onboarding failures.
- Accidentally testing with a reused invite will fail by design and may be misread as a regression.
- Token-bearing response data must not be logged in the frontend or release/debug output.
- Local frontend test infrastructure has a known ESM blocker, reducing frontend automated validation coverage.
- Preexisting CodeMap validation issues may obscure StaticEng closure checks if not clearly documented.

## Referenced Files Or Areas
- `.staticeng/tasks/todo/TASK-2026-06-11-003-clone-selected-mcps-fedora.md`
- `.staticeng/tasks/done.md`
- `litellm/proxy/proxy_server.py:13570`
- `ui/litellm-dashboard/src/components/networking.tsx:2071`
- `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/backend-onboarding-tests.log`
- `.staticeng/evidences/TASK-2026-06-12-001-fix-onboarding-claim-session/logs/ruff-check.log`
- `tests/test_litellm/proxy/auth/test_onboarding.py`
- `tests/test_litellm/proxy/proxy_server/test_routes_onboarding.py`
- `https://litellm.defend.tech`

## Recommended Workflow Next Step
- assigned_to: tech_lead
- why: Commit and release are implementation/release authority actions; Tech Lead should verify the intended diff, commit the reviewed fix and evidence, deploy locally and to Fedora, then validate onboarding with a fresh invite on `https://litellm.defend.tech`.
