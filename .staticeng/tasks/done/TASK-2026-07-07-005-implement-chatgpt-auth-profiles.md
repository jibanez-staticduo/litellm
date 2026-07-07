---
id: TASK-2026-07-07-005-implement-chatgpt-auth-profiles
complexity: standard
track: implementation
slice: logic
status: done
scr: SCR-2026-07-07-001-chatgpt-auth-profiles
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 1
---

# Task: TASK-2026-07-07-005 - Implement ChatGPT Auth Profiles

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** logic

## Objective
Implement core multi-profile auth support for LiteLLM's ChatGPT subscription provider so one LiteLLM process can expose multiple user-facing model aliases backed by different ChatGPT subscription credential files.

## SCR
- `.staticeng/docs/scrs/SCR-2026-07-07-001-chatgpt-auth-profiles.md`

## Background
Investigation found current ChatGPT auth is single-context: `Authenticator` reads one token dir/file from `CHATGPT_TOKEN_DIR` or `~/.config/litellm/chatgpt` plus `CHATGPT_AUTH_FILE` or `auth.json`; ChatGPT chat and Responses configs instantiate `Authenticator()` without deployment context.

Desired behavior is not hardcoded providers such as `chatgpt2`. Instead, configure user-facing model aliases that use underlying `custom_llm_provider: chatgpt` with profile-specific auth params.

## Scope
- Support deployment-level LiteLLM params:
  - `chatgpt_auth_profile`
  - `chatgpt_token_dir`
  - `chatgpt_auth_file`
- Preserve existing default behavior when these params are absent.
- Ensure ChatGPT chat completions and Responses API use the selected auth context consistently for token, account ID, API base, and headers.
- Add focused unit/regression tests without real tokens or live login.
- Do not release/deploy a new image in this task.
- Do not add provider aliases such as `chatgpt2` to global provider registries.

## Acceptance Criteria
- [x] AC-1: Existing `custom_llm_provider: chatgpt` deployments with no new params still use default `CHATGPT_TOKEN_DIR`/`CHATGPT_AUTH_FILE` behavior.
- [x] AC-2: `chatgpt_auth_profile` selects a separate profile-specific auth file/path from the default profile.
- [x] AC-3: Explicit `chatgpt_token_dir` and/or `chatgpt_auth_file` select the configured credential location without affecting other deployments.
- [x] AC-4: Chat completions and Responses API both use the same selected auth context for access token and account ID.
- [x] AC-5: User-facing model aliases can remain arbitrary model names while underlying provider remains `chatgpt`.
- [x] AC-6: Tests cover default behavior, profile behavior, explicit file/dir behavior, and isolation/no cross-profile token leakage.
- [x] AC-7: No access tokens, refresh tokens, cookies, private keys, session tokens, or auth URLs that could grant access are logged, committed, or included in evidence.
- [x] AC-8: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/` with `SUMMARY.md` and `logs/`.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/` with:
- `SUMMARY.md` mapping every AC to verification results.
- `logs/` containing safe test, lint/pre-commit, and status outputs.
- No screenshots required unless UI changes are introduced, which is not expected.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** unit test / code review
  - **Evidence:** `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/SUMMARY.md`
- [ ] AC-2
  - **Method:** unit test
  - **Evidence:** `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/`
- [ ] AC-3
  - **Method:** unit test
  - **Evidence:** `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/`
- [ ] AC-4
  - **Method:** unit test / code review
  - **Evidence:** `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/SUMMARY.md`
- [ ] AC-5
  - **Method:** code review / targeted test if feasible
  - **Evidence:** `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/SUMMARY.md`
- [ ] AC-6
  - **Method:** unit tests
  - **Evidence:** `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/`
- [ ] AC-7
  - **Method:** secret scan / review
  - **Evidence:** `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/`
- [ ] AC-8
  - **Method:** file inspection
  - **Evidence:** `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/SUMMARY.md`

## Active Discussions
- DISCUSSION-002: Implement ChatGPT multi-account auth profiles in LiteLLM

## Handoff
[Agent Message] From: product_manager To: developer

Please implement SCR-2026-07-07-001. Keep the solution minimal and backwards-compatible. Do not add `chatgpt2` as a provider; support multiple accounts by passing deployment-level auth profile/path params into the existing `chatgpt` provider. Add focused tests and evidence. Do not use or print real tokens. Run relevant tests and `make pre-commit` before committing readiness back to PMA; if `make pre-commit` is too broad or fails due unrelated repo state, capture the exact safe evidence and blocker.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Implementation Summary
- Implemented deployment-level ChatGPT auth params: `chatgpt_auth_profile`, `chatgpt_token_dir`, and `chatgpt_auth_file`.
- Updated ChatGPT chat completions and Responses API to create auth context from the selected LiteLLM params for access token, account ID, API base, and headers.
- Added typed LiteLLM param plumbing and supplemental provider param extraction for ChatGPT auth params.
- Added focused regression tests covering default env behavior, profile path behavior, explicit credential location behavior, profile isolation, chat/Responses auth context propagation, and arbitrary aliases over `custom_llm_provider: chatgpt`.

### Verification Results
- PASS: `uv run python -m pytest tests/test_litellm/llms/chatgpt/test_chatgpt_authenticator.py tests/test_litellm/llms/chatgpt/chat/test_chatgpt_chat_transformation.py tests/test_litellm/llms/chatgpt/responses/test_chatgpt_responses_transformation.py` (31 passed).
- PASS: targeted `ruff format --check` on touched code/test files.
- PASS: targeted `ruff check` on touched code/test files.
- FAIL: `make pre-commit` due unrelated repo-wide ruff/type budget failures, missing/deleted files in format checks, and missing frontend `openapi-typescript` binary. Captured in evidence.
- FAIL: `staticeng_validate` due pre-existing broad StaticEng CodeMap/config debt. Captured in evidence; repair dry-run showed a large unrelated artifact scope, so no repair was applied.

### Evidence
- Evidence packet: `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/`
- Summary: `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/SUMMARY.md`
- Logs: `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/`

### Documentation Impact
- No product documentation update was required for this implementation task; the approved behavior is captured in SCR-2026-07-07-001 and evidence.

## Critic Review Findings

[Agent Message] From: critic To: product_manager

The implementation is not ready as-is. Blocking findings to resolve before PMA closure:

- High: `chatgpt_auth_profile` allows path traversal outside the token root. Reject profile names containing path separators, `..`, absolute paths, or otherwise failing a safe path/commonpath check.
- High: Chat completions can resolve the token from one auth profile but later build account/header context from another because final `litellm_params` creation does not include `chatgpt_auth_profile`, `chatgpt_token_dir`, or `chatgpt_auth_file`.
- High: Chat-completion to Responses bridge can lose the profile and fall back to default ChatGPT auth.
- High: The new params are not added to LiteLLM-level reserved params, so they may be classified as provider params, rejected, or leaked into provider request construction.
- Medium: Per-request client override of `chatgpt_auth_file`/profile/dir needs an explicit decision and guard; prefer deployment-config selection over arbitrary client-supplied auth file paths.
- Medium: Tests miss public plumbing paths through `litellm.completion`, router/model-list deployment params, and chat-to-Responses bridge, plus traversal rejection.

Please fix the blocking issues, add targeted regression tests for the public paths, update evidence, and rerun verification.

## Developer: Reopen Resolution

### Implementation Summary
- Fixed `chatgpt_auth_profile` traversal by treating profiles as logical names only and rejecting empty/whitespace-only values, path separators, `..`, absolute paths, dots, and unsafe characters.
- Preserved `chatgpt_auth_profile`, `chatgpt_token_dir`, and `chatgpt_auth_file` in final public chat completion `litellm_params` so provider resolution and `validate_environment` use the same ChatGPT auth context.
- Verified the chat-completion-to-Responses bridge preserves ChatGPT auth params into the Responses provider handler.
- Added the three ChatGPT auth params to `all_litellm_params` and kept typed/config support intact.
- Added proxy request-body blocking for the three ChatGPT auth selection fields by default, using the existing client-side credential opt-in boundary for any explicit admin override.

### Verification Results
- PASS: `uv run python -m pytest tests/test_litellm/llms/chatgpt/test_chatgpt_authenticator.py tests/test_litellm/llms/chatgpt/chat/test_chatgpt_chat_transformation.py tests/test_litellm/llms/chatgpt/responses/test_chatgpt_responses_transformation.py tests/test_litellm/proxy/auth/test_auth_utils.py::test_chatgpt_auth_selection_fields_rejected_from_request_body_by_default` (51 passed, 1 warning).
- PASS: `uv run ruff format --check litellm/llms/chatgpt/authenticator.py litellm/main.py litellm/types/utils.py litellm/proxy/auth/auth_utils.py tests/test_litellm/llms/chatgpt/test_chatgpt_authenticator.py tests/test_litellm/llms/chatgpt/chat/test_chatgpt_chat_transformation.py tests/test_litellm/proxy/auth/test_auth_utils.py`.
- PASS: `uv run ruff check litellm/llms/chatgpt/authenticator.py litellm/main.py litellm/types/utils.py litellm/proxy/auth/auth_utils.py tests/test_litellm/llms/chatgpt/test_chatgpt_authenticator.py tests/test_litellm/llms/chatgpt/chat/test_chatgpt_chat_transformation.py tests/test_litellm/proxy/auth/test_auth_utils.py`.
- PASS: `make pre-commit` completed with only the expected unstaged/untracked changes notice.
- FAIL: `staticeng_validate` remains blocked by broad pre-existing StaticEng CodeMap/config debt unrelated to this task.

### Evidence
- Updated evidence packet: `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/`
- Reopen pytest log: `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/pytest-chatgpt-auth-profiles-reopen.log`
- Reopen ruff logs: `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/ruff-format-check-reopen.log`, `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/ruff-check-reopen.log`
- Reopen pre-commit log: `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/make-pre-commit-reopen.log`

### Documentation Impact
- Product documentation changes were not required; behavior is covered by the approved SCR and implementation evidence. CodeMap validation remains blocked by pre-existing missing-map debt and was not repaired in this scoped reopen.

## PMA Final Closure

### Review
- Critic re-review found no blocking findings after reopen fixes.
- Residual risks are limited to existing admin opt-in client-side credential behavior and unrelated StaticEng CodeMap validation debt.

### Final Verification
- PASS: targeted ChatGPT auth profile pytest suite, 51 passed and 1 warning.
- PASS: targeted ruff format check, 8 files already formatted.
- PASS: targeted ruff check, all checks passed.
- PASS: `git diff --check`.
- PASS: developer `make pre-commit` after reopen, with only unstaged/untracked notice.
- FAIL: `staticeng_validate` remains blocked by pre-existing missing CodeMaps and stale `.staticeng/codemap.yml` links unrelated to this task.

### Documentation Closure
- SCR marked implemented and archived in SCR done registry.
- Task registry updated.
- Product docs beyond the SCR were not required for this fork-scoped implementation.
