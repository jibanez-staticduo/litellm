---
id: TASK-2026-07-11-001-investigate-chatgpt-multiaccount-routing
complexity: complex
track: investigation
slice: logic
status: done
scr: null
parent: null
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-11-001 - Investigate ChatGPT Multiaccount Routing

## Classification
- **complexity:** complex
- **track:** investigation
- **slice:** logic

## Objective
Reproduce and identify the exact root cause by which a Fedora LiteLLM request for `chatgpt/gpt-5.6-sol` is reported/retried as `chatgpt-account2/gpt-5.6-sol`, then define the minimal safe implementation slices. Investigation only: do not implement or alter credentials.

## Observed Failure
- Original model: `chatgpt/gpt-5.6-sol`
- Received model group: `chatgpt-account2/gpt-5.6-sol`
- Account2 device auth attempted and returned HTTP 429.
- Fallback lookup then used the account2 group rather than the original logical group.

## Scope
- Inspect Fedora live and persistent LiteLLM model/router/fallback config.
- Reproduce minimally with sanitized routing evidence.
- Trace model, model_name, model_group, deployment ID, provider, auth profile, retry, fallback, and exception propagation.
- Check whether regular model groups include account2 deployments or aliases/mappings.
- Check global/shared auth state, token stores, caches, and device-code concurrency.
- Identify why persisted OAuth is not reused and whether concurrent device-code calls can cause 429.
- Do not renew/delete/replace credentials and do not expose tokens, cookies, device codes, headers, prompts, responses, or DB URLs.

## Acceptance Criteria
- [x] AC-1: Exact pre-fix reproduction is captured with sanitized routing identity fields.
- [x] AC-2: Exact transformation path from regular logical model to account2 group is identified.
- [x] AC-3: Live/persistent model group membership, aliases, retries, and fallbacks are compared.
- [x] AC-4: OAuth profile isolation and device-code concurrency behavior are analyzed.
- [x] AC-5: Root cause is classified as config, code, or both, with affected files/modules.
- [x] AC-6: Atomic implementation/test/release slices are recommended against user AC-1 through AC-9.
- [x] AC-7: Evidence is secret-safe and no credential mutation occurs.

## Expected Evidence
- `.staticeng/evidences/TASK-2026-07-11-001-investigate-chatgpt-multiaccount-routing/SUMMARY.md`
- `logs/` containing sanitized pre-fix reproduction and configuration/routing comparisons.

## Handoff
[Agent Message] From: product_manager To: technical_architect

Investigate only. Reproduce the Fedora issue safely, trace the exact identity mutation through routing/retry/fallback/auth, and return the root cause before any implementation. Do not fix symptoms by adding account2 fallbacks. Do not alter credentials or expose secrets. Provide atomic implementation slices and test requirements if code/config changes are needed.

# Investigation Findings

## Root Cause
- Fedora regular and account2 model groups are isolated: each has one distinct deployment ID; regular does not contain account2.
- Both groups share physical provider model `chatgpt/gpt-5.6-sol`; account isolation is through deployment-specific `chatgpt_auth_profile` and distinct auth files.
- `run_async_fallback()` mutates shared kwargs in place, replacing `kwargs["model"]` and `metadata["model_group"]` with the fallback candidate. Nested retry/fallback processing then loses immutable logical request identity and reports/looks up fallback using account2.
- No persistent Fedora alias or regular-Sol-to-account2 fallback exists. Current Hermes/OpenClaw, YAML, global, key, and team settings do not explain the historical candidate. The most likely historical source is a request-level fallback or changed runtime override, but provenance was not retained.
- Fedora account2 has no reusable OAuth token; once accidentally selected it correctly enters device auth.
- Device auth cooldown is race-prone: concurrent callers can request device codes before the marker is persisted; writes are unlocked/non-atomic. Router retries amplify the 429 risk.

## Affected Modules
- `litellm/router_utils/fallback_event_handlers.py`
- `litellm/router.py`
- `litellm/proxy/common_request_processing.py`
- `litellm/proxy/route_llm_request.py`
- `litellm/llms/chatgpt/authenticator.py`
- mapped router/auth tests.

## PMA Decision
- This is an unequivocal bug fix; no SCR is required.
- Implementation must preserve immutable logical identity, add safe fallback provenance logs, enforce explicit cross-profile failover, serialize device auth per profile, classify interactive auth retries safely, and add regression tests.

## Documentation Impact
- Implementation evidence must document logical model identity, selected deployment/account, OAuth isolation, and fallback semantics.
