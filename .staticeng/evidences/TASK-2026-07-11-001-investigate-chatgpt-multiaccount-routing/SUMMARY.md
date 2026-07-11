# ChatGPT Multiaccount Routing Investigation

## Summary
Fedora regular and account2 ChatGPT deployments are correctly isolated in live and persistent model configuration. The observed transition from `chatgpt/gpt-5.6-sol` to `chatgpt-account2/gpt-5.6-sol` occurred in a nested fallback attempt, not through load balancing or implicit account selection.

## Root Cause
- Router fallback handling mutates shared request kwargs and model-group metadata in place. A nested fallback therefore replaces the logical requested group with the physical fallback group.
- Error reporting and subsequent fallback lookup use the mutated group, while the provider exception still reports the original physical provider model. This creates the mixed diagnostic observed by the user.
- No current persistent Fedora alias, model-group membership, global fallback, key fallback, team fallback, Hermes rule, or OpenClaw rule maps regular Sol to account2 Sol.
- The historical source of the account2 fallback candidate is not retained. Request-level `fallbacks` are accepted and are the most likely source; current logs do not record fallback provenance.
- Account2 has no reusable OAuth credentials on Fedora, so selecting it enters device auth.
- Device auth is not single-flight. Concurrent/retried requests may all pass the cooldown check before a marker is written, causing multiple device-code requests and HTTP 429.

## Configuration Findings
- Regular group: `chatgpt/gpt-5.6-sol`, one default-profile deployment.
- Account2 group: `chatgpt-account2/gpt-5.6-sol`, one account2-profile deployment.
- Both use provider model `chatgpt/gpt-5.6-sol`; account selection is deployment-specific through `chatgpt_auth_profile`.
- Router group lookup is exact; regular balancing cannot select account2.
- No credentials were read, renewed, deleted, replaced, or exposed.

## Source References
- `litellm/router_utils/fallback_event_handlers.py`
- `litellm/router.py`
- `litellm/proxy/common_request_processing.py`
- `litellm/proxy/route_llm_request.py`
- `litellm/llms/chatgpt/authenticator.py`
- `litellm/llms/chatgpt/responses/transformation.py`

## Required Implementation
1. Preserve immutable requested/logical model identity separately from current fallback/deployment group.
2. Stop mutating shared fallback kwargs; clone state per attempt.
3. Record secret-safe fallback provenance and attempt routing identity.
4. Prevent cross-auth-profile fallback unless explicitly configured.
5. Serialize device authorization per resolved auth profile and use atomic credential writes.
6. Prevent router retries from launching repeated interactive auth flows.
7. Add tests for regular/account2 routing, auth failures, retry/fallback, concurrency, and state isolation.

## Open Risk
The exact historical component that supplied account2 as a fallback candidate cannot be recovered because the original request fallback field and provenance were not retained. New instrumentation is required to identify future sources without logging request content or secrets.
