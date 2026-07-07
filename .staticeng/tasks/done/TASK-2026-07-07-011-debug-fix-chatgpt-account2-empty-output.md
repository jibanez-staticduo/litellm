---
id: TASK-2026-07-07-011-debug-fix-chatgpt-account2-empty-output
complexity: standard
track: implementation
slice: logic
status: done
scr: null
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 1
---

# Task: TASK-2026-07-07-011 - Debug and Fix ChatGPT Account2 Empty Output

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** logic

## Objective
Diagnose and fix why `chatgpt-account2/gpt-5.5` and `chatgpt-account2/gpt-5.4` reach LiteLLM but fail with `ChatgptException - Unknown items in responses API response: []`, while the regular `chatgpt/gpt-5.5` path works.

## Background
- Current local image contains ChatGPT auth profiles and account2 DB deployments.
- `auth.json` and `account2.json` both exist with access token, refresh token, account id, and future expiry.
- DB inspection shows `chatgpt/gpt-5.5` and `chatgpt-account2/gpt-5.5` are equivalent except account2 has `chatgpt_auth_profile: account2`.
- Account2 smoke requests fail after login with empty Responses API output/items, not with a device-code prompt.

## Scope
- Add safe diagnostic logging or temporary local diagnostics as needed to compare the regular/default and account2 paths.
- Do not log or commit access tokens, refresh tokens, cookies, API keys, master keys, private keys, auth files, DB URLs, or raw secret-bearing headers.
- Determine whether the failure is auth-context propagation, session id handling, account id/header mismatch, ChatGPT response/event shape, model entitlement, or parser behavior.
- Implement the minimal code fix if the root cause is in LiteLLM.
- Add/update regression tests for the discovered failure mode.
- Build/deploy a new local image only if needed to validate the fix against the live account2 path.
- Do not deploy to Fedora.

## Acceptance Criteria
- [x] AC-1: Safe diagnostics identify the concrete root cause or prove the failure is an external account entitlement/ChatGPT response condition.
- [x] AC-2: If the root cause is LiteLLM, code is fixed with focused tests.
- [x] AC-3: `chatgpt-account2/gpt-5.5` is re-tested after the fix or root-cause investigation with sanitized result.
- [x] AC-4: Existing `chatgpt/gpt-5.5` behavior is not regressed.
- [x] AC-5: No secrets are written to repo artifacts, logs, memory, or final report.
- [x] AC-6: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-07-011-debug-fix-chatgpt-account2-empty-output/` with `SUMMARY.md` and safe logs.

## Active Discussions
- DISCUSSION-004: Debug and fix ChatGPT account2 empty Responses output

## Handoff
[Agent Message] From: product_manager To: developer

Please debug and fix the account2 empty Responses output bug. Start by safely instrumenting/diagnosing the live local container path: compare regular `chatgpt/gpt-5.5` vs `chatgpt-account2/gpt-5.5` request construction, auth profile selection, account id shape only, session id behavior, response content-type/status/event types, and output item shape. Never print tokens, cookies, auth headers, DB URLs, master keys, or raw auth files. If the issue is in LiteLLM, implement a minimal fix and tests; if it is external entitlement/ChatGPT behavior, prove that with safe evidence. Do not commit; PMA owns closure.

## Critic Review Findings

[Agent Message] From: critic To: product_manager

No high-severity blocker, but two medium findings need resolution before closure:

- Medium: recovered output is attached after response post-processing, so recovered items may skip ID/container/encrypted-content normalization. Consider attaching recovered output before response ID/container post-processing or re-running relevant response-output normalization after attach.
- Medium: recovery records raw chunks before provider-specific streaming transforms. Providers may normalize streamed items during transform; if such a provider also returns empty completed output, recovered response output could contain pre-transform raw items while emitted events contain normalized ones. Prefer recording from the transformed event or applying provider normalization before storing recovered items.

Test coverage requested before closure:
- `output_text.done`-only recovery.
- precedence when both `output_item.done` and `output_text.done` arrive.
- preserving non-empty completed output.
- provider/post-processing behavior if feasible.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Root cause: ChatGPT streamed the real message in `response.output_item.done` / `response.output_text.done`, while the final `response.completed.response.output` was empty. The Chat Completions bridge used only the final completed response output and therefore saw `[]`.
- Fix: `litellm/responses/streaming_iterator.py` now records transformed/post-processed streamed output items and attaches them to the completed response only when completed output is empty.
- Critic reopen resolved by recording recovered output after provider streaming transform and post-processing, plus additional tests.

### Verification
- `uv run python -m pytest tests/test_litellm/responses/test_streaming_iterator.py tests/test_litellm/llms/chatgpt/responses/test_chatgpt_responses_transformation.py tests/test_litellm/completion_extras/test_litellm_responses_transformation_transformation.py` -> 37 passed.
- `uv run ruff check litellm/responses/streaming_iterator.py tests/test_litellm/responses/test_streaming_iterator.py` -> pass.
- `uv run ruff format --check litellm/responses/streaming_iterator.py tests/test_litellm/responses/test_streaming_iterator.py` -> pass.
- `git diff --check` -> pass.
- Live hotpatch smoke: `chatgpt/gpt-5.5`, `chatgpt-account2/gpt-5.5`, and `chatgpt-account2/gpt-5.4` returned HTTP 200 with sanitized `pong`.

### Evidence
- `.staticeng/evidences/TASK-2026-07-07-011-debug-fix-chatgpt-account2-empty-output/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-07-07-011-debug-fix-chatgpt-account2-empty-output/logs/`

## PMA Final Closure

### Acceptance Criteria Coverage
- AC-1 through AC-6 are satisfied by tests, live hotpatch smoke, safe diagnostics, and evidence.

### Documentation Impact
- No public docs changed; evidence documents the operational root cause and fix.

### Open Risks
- Local container is currently hotpatched; follow-up task will rebuild/deploy a durable local image from the committed fix.
