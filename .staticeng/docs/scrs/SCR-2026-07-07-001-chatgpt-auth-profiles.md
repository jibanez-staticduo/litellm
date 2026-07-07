---
scr_id: SCR-2026-07-07-001-chatgpt-auth-profiles
status: implemented
owner: product_manager
created: 2026-07-07
related_task: TASK-2026-07-07-005-implement-chatgpt-auth-profiles
---

# SCR-2026-07-07-001: ChatGPT Multi-Account Auth Profiles

## Problem

LiteLLM's ChatGPT subscription provider currently uses one process-wide auth context. `Authenticator` selects a single token directory/file from `CHATGPT_TOKEN_DIR` and `CHATGPT_AUTH_FILE`, then every `chatgpt` deployment uses an unparameterized `Authenticator()`. This prevents one LiteLLM instance from routing separate user-facing model namespaces such as `chatgpt/gpt-5.5` and `chatgpt2/gpt-5.5` to different ChatGPT subscription accounts.

## Approved Behavior

LiteLLM must support multiple independent ChatGPT subscription auth profiles in one process. Each model deployment using `custom_llm_provider: chatgpt` may optionally select a ChatGPT auth profile or explicit auth file/directory. Requests for one deployment must use only that deployment's configured ChatGPT auth context, including access token, refresh token, account ID, and device-login cooldown state.

Existing single-account behavior remains the default when no profile-specific configuration is provided.

## Configuration Contract

The implementation should support deployment-level LiteLLM params for ChatGPT auth selection:

- `chatgpt_auth_profile`: logical profile name. When set, credentials are stored under a profile-specific auth file below the configured/default token root.
- `chatgpt_token_dir`: optional explicit token directory for this deployment.
- `chatgpt_auth_file`: optional explicit auth file name or path for this deployment.

Model names such as `chatgpt2/gpt-5.5` may be exposed as LiteLLM `model_name` aliases, but the underlying provider should remain `custom_llm_provider: chatgpt` with a distinct auth profile. Do not add hardcoded providers like `chatgpt2`, `chatgpt3`, or `chatgpt4`.

## Scope

In scope:
- ChatGPT chat completions auth profile selection.
- ChatGPT Responses API auth profile selection.
- Backward-compatible default auth behavior.
- Unit/regression tests proving profile-specific auth file selection and isolation.
- Secret-safe handling; no token values in logs or evidence.

Out of scope:
- Adding hardcoded provider aliases such as `chatgpt2`.
- Running live ChatGPT logins or collecting real tokens.
- Releasing/deploying a new image.
- Cleaning unrelated StaticEng CodeMap debt.

## Acceptance Criteria

AC-1. Existing deployments with `custom_llm_provider: chatgpt` and no new params still use the default `CHATGPT_TOKEN_DIR`/`CHATGPT_AUTH_FILE` behavior.

AC-2. A deployment with `chatgpt_auth_profile: account2` uses a separate auth file/path from the default profile.

AC-3. A deployment with explicit `chatgpt_token_dir` and/or `chatgpt_auth_file` uses that configured credential location without affecting other deployments.

AC-4. Chat completions and Responses API both select the same profile-specific auth context for access token and account ID.

AC-5. User-facing model aliases can remain arbitrary model names while the underlying provider remains `chatgpt`.

AC-6. Tests cover default behavior, profile behavior, explicit file/dir behavior, and no cross-profile token leakage.

AC-7. No access tokens, refresh tokens, cookies, private keys, session tokens, or auth URLs that could grant access are logged or committed.
