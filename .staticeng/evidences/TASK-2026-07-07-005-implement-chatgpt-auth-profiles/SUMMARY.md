# Evidence Summary: TASK-2026-07-07-005

## Summary
Implemented deployment-level ChatGPT auth profile selection for the existing `chatgpt` provider and resolved critic reopen blockers. The reopened change validates profile names as logical names only, preserves ChatGPT auth params through public chat completion, Router, and chat-to-Responses bridge paths, reserves the params as LiteLLM-level fields, and blocks client request bodies from selecting ChatGPT auth files/profiles by default at the proxy safety boundary.

## Work Performed
- Updated `litellm/llms/chatgpt/authenticator.py` to accept optional LiteLLM params, resolve `chatgpt_auth_profile`, `chatgpt_token_dir`, and `chatgpt_auth_file`, and reject unsafe logical profile names.
- Updated ChatGPT chat and Responses transformations to instantiate `Authenticator` with request/deployment params instead of a process-wide auth context.
- Added ChatGPT auth params to `GenericLiteLLMParams`, `LiteLLMParamsTypedDict`, supplemental provider param extraction, final completion `litellm_params`, and `all_litellm_params`.
- Added proxy request-body rejection for `chatgpt_auth_profile`, `chatgpt_token_dir`, and `chatgpt_auth_file` unless an existing client-side credential opt-in applies.
- Added regression tests for traversal/unsafe profile rejection, public `litellm.completion` plumbing, Router deployment plumbing, chat-completion-to-Responses bridge plumbing, reserved param classification, and proxy request-body filtering.

## Acceptance Criteria Coverage
- AC-1: PASS. `test_default_auth_file_uses_environment_fallbacks` verifies default `CHATGPT_TOKEN_DIR` and `CHATGPT_AUTH_FILE` behavior remains intact when no new params are set.
- AC-2: PASS. `test_auth_profile_selects_profile_auth_file` verifies `chatgpt_auth_profile` selects a separate profile file under the configured/default token root; `test_auth_profile_rejects_unsafe_logical_names` verifies traversal and unsafe names are rejected.
- AC-3: PASS. `test_explicit_relative_auth_file_uses_configured_token_dir` and `test_explicit_absolute_auth_file_isolated_from_token_dir` verify explicit directory/file resolution without affecting other deployments.
- AC-4: PASS. Chat, Responses, public `litellm.completion`, Router, and chat-to-Responses bridge tests verify the selected LiteLLM params are passed into the auth context used for access token and account ID.
- AC-5: PASS. `test_chatgpt_chat_arbitrary_model_alias_keeps_chatgpt_provider` verifies an arbitrary user-facing model name keeps the underlying provider as `chatgpt`; no `chatgpt2` provider alias was added.
- AC-6: PASS. The targeted pytest run covers default, profile, explicit path, unsafe profile rejection, public path propagation, bridge propagation, and isolation/no cross-profile leakage cases.
- AC-7: PASS. Evidence and tests use synthetic placeholder values only. No real access tokens, refresh tokens, cookies, private keys, session tokens, or auth URLs are included.
- AC-8: PASS. Evidence packet exists with `SUMMARY.md` and `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/` under `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/`.

## Verification Commands
- `uv run python -m pytest tests/test_litellm/llms/chatgpt/test_chatgpt_authenticator.py tests/test_litellm/llms/chatgpt/chat/test_chatgpt_chat_transformation.py tests/test_litellm/llms/chatgpt/responses/test_chatgpt_responses_transformation.py tests/test_litellm/proxy/auth/test_auth_utils.py::test_chatgpt_auth_selection_fields_rejected_from_request_body_by_default` -> PASS, 51 passed, 1 warning. See `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/pytest-chatgpt-auth-profiles-reopen.log`.
- `uv run ruff format --check litellm/llms/chatgpt/authenticator.py litellm/main.py litellm/types/utils.py litellm/proxy/auth/auth_utils.py tests/test_litellm/llms/chatgpt/test_chatgpt_authenticator.py tests/test_litellm/llms/chatgpt/chat/test_chatgpt_chat_transformation.py tests/test_litellm/proxy/auth/test_auth_utils.py` -> PASS. See `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/ruff-format-check-reopen-2.log`.
- `uv run ruff check litellm/llms/chatgpt/authenticator.py litellm/main.py litellm/types/utils.py litellm/proxy/auth/auth_utils.py tests/test_litellm/llms/chatgpt/test_chatgpt_authenticator.py tests/test_litellm/llms/chatgpt/chat/test_chatgpt_chat_transformation.py tests/test_litellm/proxy/auth/test_auth_utils.py` -> PASS. See `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/ruff-check-reopen-2.log`. The `litellm/types/utils.py` `# noqa` cleanup is required by this targeted ruff check when `types/utils.py` is included.
- `make pre-commit` -> PASS during developer reopen with only the expected unstaged/untracked changes notice. See `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/make-pre-commit-reopen.log`.
- PMA final staged `make pre-commit` attempt -> FAIL/TIMEOUT due unrelated repo-wide lint/format/budget issues and command timeout, not targeted ChatGPT auth profile files. See `.staticeng/evidences/TASK-2026-07-07-005-implement-chatgpt-auth-profiles/logs/make-pre-commit-pma-final.log`.
- `staticeng_validate` tool -> FAIL due broad pre-existing StaticEng CodeMap/config debt unrelated to this task; output lists missing repo CodeMaps and stale `.staticeng/codemap.yml` links.

## Open Risks
- `staticeng_validate` remains blocked by broad pre-existing StaticEng CodeMap/config debt. Applying repair would create many unrelated artifacts and was not performed.
- Client-side auth override behavior now uses the existing proxy-wide/model-level client credential opt-in boundary. That preserves existing behavior but still means admins who explicitly opt in can allow these sensitive fields.

## Recommended Next Step
PMA/Tech Lead should review the scoped code/test diff and the remaining StaticEng validation debt separately before final closure.
