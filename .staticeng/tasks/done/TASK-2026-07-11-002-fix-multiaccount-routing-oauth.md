---
id: TASK-2026-07-11-002-fix-multiaccount-routing-oauth
complexity: complex
track: implementation
slice: logic
status: done
scr: null
parent: TASK-2026-07-11-001-investigate-chatgpt-multiaccount-routing
assigned_to: developer
handoff_from: product_manager
reopened_count: 6
---

# Task: TASK-2026-07-11-002 - Fix Multiaccount Routing and OAuth

## Classification
- **complexity:** complex
- **track:** implementation
- **slice:** logic

## Objective
Fix LiteLLM multiaccount ChatGPT routing identity, fallback semantics, structured observability, and per-profile device-auth concurrency based on TASK-2026-07-11-001 findings.

## Required Behavior
- Regular model requests never use account2 deployment/credentials without explicit cross-profile failover policy.
- Account2 requests remain isolated to account2.
- Immutable requested/logical identity remains distinct from current group, selected account, and physical deployment through retries/fallbacks/errors.
- Fallback handling does not mutate caller/shared kwargs.
- Device auth is single-flight per stable resolved auth-profile key; parallel callers do not request multiple codes.
- Interactive auth failures do not trigger repeated device flows through router retries.
- Logs expose sanitized routing identity/provenance without secrets.

## Acceptance Criteria
- [x] AC-1: Regular ChatGPT request cannot select account2 credentials/deployment without explicit policy.
- [x] AC-2: Explicit account2 request uses only account2.
- [x] AC-3: `original_model`, logical group, selected account, current group, and physical deployment remain distinct.
- [x] AC-4: Fallback lookup/diagnostics preserve correct logical identity.
- [x] AC-5: Device auth is single-flight per account/profile under concurrency.
- [x] AC-6: OAuth files/session state use stable profile-specific keys and atomic writes.
- [x] AC-7: Tests cover regular/account2, OAuth failures, retries, fallbacks, concurrency, and no contamination.
- [x] AC-8: Secret-safe structured routing logs include request-id hash, requested model, logical/current group, selected account, deployment prefix, attempt, fallback source/reason.
- [x] AC-9: Targeted/full relevant tests and lint pass without skips; unrelated model routing remains unchanged.
- [x] AC-10: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-11-002-fix-multiaccount-routing-oauth/` with pre/post tests, logs, and `SUMMARY.md` mapping user AC-1 through AC-9.

## Implementation Guidance
- Clone fallback kwargs and metadata per attempt in `litellm/router_utils/fallback_event_handlers.py`.
- Introduce immutable requested/logical group fields without changing provider request payloads.
- Clarify fallback lookup semantics in `litellm/router.py` and preserve initial logical identity in errors/callback metadata.
- Add safe provenance at request merge and fallback attempt boundaries.
- Validate auth-profile boundaries before fallback deployment selection; default deny cross-profile unless explicit opt-in.
- Refactor `litellm/llms/chatgpt/authenticator.py` for per-profile single-flight, atomic writes, and retry-safe interactive auth.
- Use existing mapped router/auth tests and add focused concurrency/regression tests.
- No real credentials/device auth in tests.

## Handoff
[Agent Message] From: product_manager To: developer

Implement the root-cause fix, not an account2 fallback workaround. Preserve immutable logical identity, isolate profiles, serialize device auth, make auth writes atomic, prevent retry-driven device-code storms, add sanitized provenance logs, and provide comprehensive focused tests/evidence. Do not deploy or commit; PMA will review before release.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Preserved immutable requested/logical routing identity across sync/async selection, retries, fallbacks, errors, and callbacks.
- Enforced ChatGPT profile homogeneity before sync and async deployment selection.
- Cross-profile fallback is denied by default and can only be enabled by strict trusted Router configuration, not request input.
- Added authoritative post-selection structured routing events and sanitized fallback events.
- Added per-profile thread/process single-flight, portable POSIX/Windows lock paths, atomic owner-only auth writes, and locked read-modify-write merging.
- Interactive auth errors are non-retryable before retry-policy evaluation.

### Verification
- Focused suite: 49 passed; five Python 3.12 multiprocessing fork warnings.
- Mapped suite: 38 passed; four pre-existing async cleanup warnings.
- Ruff format/check, `git diff --check`, and `make pre-commit`: passed.
- Critic final review: APPROVED, clean-code score 9/10.

### Evidence
- `.staticeng/evidences/TASK-2026-07-11-002-fix-multiaccount-routing-oauth/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-07-11-002-fix-multiaccount-routing-oauth/logs/`

## PMA Final Closure

### Acceptance Criteria Coverage
- Task AC-1 through AC-10 and user AC-1 through AC-9 are satisfied by implementation, tests, and evidence.

### Documentation Impact
- Evidence documents logical identity, account selection, OAuth serialization, fallback policy, and structured routing logs.

### Open Risks
- Native Windows behavior is simulated on Linux; native Windows CI remains desirable.
- Test suites retain non-blocking multiprocessing and async cleanup warnings.
