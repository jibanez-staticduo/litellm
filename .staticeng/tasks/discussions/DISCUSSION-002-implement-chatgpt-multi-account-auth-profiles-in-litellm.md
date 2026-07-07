---
id: DISCUSSION-002
title: "Implement ChatGPT multi-account auth profiles in LiteLLM"
status: closed
summarized_by: business_analyst
source: runtime-transcript
---

# Discussion Summary

## Topic
Implement support for multiple ChatGPT subscription auth profiles/accounts in one StaticDuo LiteLLM instance.

## Purpose
The user wants one LiteLLM deployment to expose multiple ChatGPT-backed model deployments that authenticate with different ChatGPT subscription accounts, instead of the current single global `chatgpt` auth context.

## Repository Truth Relevant To This Discussion
- Repo path: `/home/staticduo/git/litellm`.
- Current fork remote convention: `origin` is `git@github.com:jibanez-staticduo/litellm.git`; `upstream` is `https://github.com/BerriAI/litellm`.
- Current `main`/`origin/main` is a replay line based on `upstream/main` `79a6b8f7f0` (`v1.92.0-rc.1`), with StaticDuo commits replayed on top.
- Old main is preserved at `backup-main-before-upstream-v1.92` at `4f7364064d`.
- Known good image after v1.92 replay and CacheCodec fix: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`.
- Known good image digest: `docker.staticduo.com/litellm@sha256:23f346521079a27dfeb9039e73dc2328c268ec50d44e11dc662c33d78a006d86`.
- Local/NAS stack path: `/volume2/docker/litellm`.
- Fedora stack path: `/home/staticduo/docker/litellm` via SSH host `fedora`.
- Release script: `/home/staticduo/git/release-litellm.sh`.
- Recent release state: local/NAS and Fedora deployments are healthy on the known good image; readiness reports `{"status":"healthy","db":"connected"}`, liveliness returns `"I'm alive!"`, and LazyMCP/MCP smoke checks passed.
- `staticeng_validate` is currently not green because of pre-existing StaticEng metadata/CodeMap debt, specifically broken links in `.staticeng/codemap.yml` and many missing `codemap.yml` files across source directories; this is not considered a functional LiteLLM blocker.
- Prior ChatGPT auth investigation was recorded and pushed in commit `32d4f4d3a3` with message `chore: TASK-2026-07-07-004 record ChatGPT auth investigation`.
- Git was clean and `main` synchronized with `origin/main` after the investigation.

## Facts Established
- LiteLLM's current ChatGPT provider auth behaves as a single auth context per process.
- `Authenticator` uses one token directory/file selected by `CHATGPT_TOKEN_DIR` or default `~/.config/litellm/chatgpt`, and `CHATGPT_AUTH_FILE` or default `auth.json`: `litellm/llms/chatgpt/authenticator.py:31`.
- When the access token expires, the auth flow uses the stored `refresh_token` and rewrites the same auth file: `litellm/llms/chatgpt/authenticator.py:43`, `litellm/llms/chatgpt/authenticator.py:288`.
- When credentials are missing or invalid, ChatGPT auth starts a device-code login and prints `Visit ...` and `Enter code ...` instructions to stdout/logs: `litellm/llms/chatgpt/authenticator.py:143`.
- `account_id` is derived from the token and stored in the same auth file: `litellm/llms/chatgpt/authenticator.py:66`, `litellm/llms/chatgpt/authenticator.py:132`.
- ChatGPT requests include `Authorization`, `ChatGPT-Account-Id`, and session id headers: `litellm/llms/chatgpt/common_utils.py:228`.
- A model name such as `chatgpt2/gpt-5.5` will not work by config alone because LiteLLM currently recognizes only the literal provider `chatgpt`.
- The ChatGPT provider is registered in `litellm/constants.py:532`.
- The provider enum includes ChatGPT at `litellm/types/utils.py:3228`.
- Provider resolution has special handling only when `custom_llm_provider == "chatgpt"`: `litellm/litellm_core_utils/get_llm_provider_logic.py:729`.
- `ChatGPTConfig` and `ChatGPTResponsesAPIConfig` instantiate `Authenticator()` without deployment-specific parameters, so all deployments share the same auth file/env configuration: `litellm/llms/chatgpt/chat/transformation.py:24`, `litellm/llms/chatgpt/responses/transformation.py:35`.
- The user confirmed they want the recommended core auth-profile approach implemented.

## Requirements Captured
- Implement option 1 from the investigation: support ChatGPT auth profiles in core LiteLLM.
- Keep the real underlying provider as `chatgpt`.
- Allow each ChatGPT deployment to select a distinct auth context/profile, conceptually via configuration such as `chatgpt_auth_profile`, `chatgpt_token_dir`, or `chatgpt_auth_file`.
- Support N ChatGPT accounts without hardcoding provider names such as `chatgpt2`, `chatgpt3`, or `chatgpt4` in LiteLLM internals.
- Enable public model/deployment naming that can expose account-distinct models such as `chatgpt`, `chatgpt2`, `chatgpt3`, or `chatgpt4`, while internally routing them through `custom_llm_provider: chatgpt` with the selected auth profile.
- Ensure each configured profile can keep separate access tokens, refresh tokens, `account_id`, and session/auth state.
- Preserve existing single-account behavior for deployments that do not configure an auth profile/path.
- Ensure token refresh and auth-file writes use the deployment-selected profile rather than a global process-wide file.
- Ensure both Chat Completions and Responses API ChatGPT paths receive the deployment-specific auth context.
- Avoid exposing `.env`, master keys, API keys, tokens, cookies, private keys, session tokens, or raw auth files in logs, evidence, or discussion artifacts.
- Because this changes configuration semantics and credential handling, process it through StaticEng with an SCR before implementation unless PMA explicitly reclassifies the work.

## Constraints
- Do not solve this by relying on `chatgpt2/gpt-5.5` as a new provider string without core changes; LiteLLM only recognizes provider `chatgpt` today.
- Avoid hardcoded finite provider aliases (`chatgpt2`, `chatgpt3`, etc.) because that pollutes registries/enums, creates a fixed alias count, and is worse for upstreamability.
- Keep upstream history intact; work should continue on the replay-based `main` rather than resurrecting old local history.
- Preserve existing StaticDuo local changes, including LazyMCP, ChatGPT/private GPT, Responses usage, auth/cache, MCP, spend, and onboarding fixes.
- Treat `staticeng_validate` CodeMap/link failures as known StaticEng metadata debt unless they directly block this workflow.
- Any implementation evidence must not leak credentials or auth tokens.

## Non-Goals
- Do not implement multiple separate LiteLLM processes as the chosen solution.
- Do not build a front LiteLLM/proxy that routes to one backend LiteLLM instance per ChatGPT account as the primary solution.
- Do not add a fixed set of real providers named `chatgpt2`, `chatgpt3`, `chatgpt4`, etc.
- Do not expose or log ChatGPT access tokens, refresh tokens, session tokens, API keys, private keys, or `.env` contents.
- Do not treat the existing StaticEng CodeMap/link validation debt as part of the functional ChatGPT auth-profile scope unless separately tasked.

## Decisions Made
- Proceed with the recommended option: core ChatGPT auth profiles.
- Keep `custom_llm_provider: chatgpt` as the internal provider identity.
- Use deployment-level configuration to select separate auth profiles/paths for multiple ChatGPT accounts.
- Defer alias-provider and multi-process workaround approaches.
- Require SCR/product-spec handling before implementation because the change affects configuration behavior and credential handling.

## Assumptions
- The user wants one running LiteLLM service to host multiple ChatGPT subscription accounts concurrently.
- Deployment/model display names may use names such as `chatgpt2/gpt-5.5`, but internally those deployments should map to provider `chatgpt` with a selected profile.
- Existing environment variable behavior (`CHATGPT_TOKEN_DIR`, `CHATGPT_AUTH_FILE`) should remain the default fallback for backward compatibility.
- A profile can be represented by either a named profile under a managed token directory or an explicit token/auth file path, but the exact config schema still needs final specification.
- Device-code login flow can remain log/stdout-based, but should operate against the selected auth profile rather than a single global file.

## Open Questions
- What exact configuration keys should be approved for the feature: `chatgpt_auth_profile`, `chatgpt_token_dir`, `chatgpt_auth_file`, or another schema?
- Should `chatgpt_auth_profile` map to a subdirectory under `CHATGPT_TOKEN_DIR`, or should it map to a full auth file path, or both?
- How should LiteLLM validate and reject unsafe profile names or paths to prevent path traversal or accidental credential overlap?
- How should the login/device-code instructions identify which profile/deployment needs login without leaking sensitive data?
- Should profile configuration be allowed in `litellm_params`, `model_info`, environment variables, or a dedicated credential/config section?
- What test matrix is required across Chat Completions, Responses API, token refresh, missing credentials login, and backward compatibility?
- Should per-profile session id handling be persisted in the auth file, derived per request, or otherwise separated from the current global behavior?
- Should the SCR also update product docs and config examples for multi-account ChatGPT deployments?

## Risks Or Concerns
- Credential isolation risk: a bug could cause two deployments to share or overwrite the same auth file, refresh token, account id, or session state.
- Security risk: new config paths/profile names may enable path traversal or accidental exposure of token files if not validated and documented.
- Regression risk: changing `Authenticator` construction could break existing single-account ChatGPT deployments.
- Integration risk: both chat and responses transformations currently instantiate `Authenticator()` directly without parameters; deployment context must be threaded consistently.
- Operational risk: device-code login instructions in logs may be confusing when multiple profiles need login concurrently unless profile context is clear.
- Upstreamability risk: adding hardcoded aliases would be noisy; the selected profile approach reduces but does not eliminate upstream review concerns.
- Validation risk: repo-level `staticeng_validate` is already failing for unrelated metadata debt, so implementation verification must clearly separate functional test results from known StaticEng validation debt.

## Referenced Files Or Areas
- `litellm/llms/chatgpt/authenticator.py`
- `litellm/llms/chatgpt/common_utils.py`
- `litellm/llms/chatgpt/chat/transformation.py`
- `litellm/llms/chatgpt/responses/transformation.py`
- `litellm/constants.py`
- `litellm/types/utils.py`
- `litellm/litellm_core_utils/get_llm_provider_logic.py`
- `.staticeng/evidences/TASK-2026-07-07-001-sync-upstream-v192-replay/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-07-07-003-deploy-litellm-fedora/SUMMARY.md`
- `.staticeng/tasks/done/TASK-2026-07-07-003-deploy-litellm-fedora.md`
- `.staticeng/codemap.yml`
- `/home/staticduo/git/release-litellm.sh`
- `/volume2/docker/litellm`
- `/home/staticduo/docker/litellm`

## Recommended Workflow Next Step
- assigned_to: product_manager
- why: Create and approve an SCR plus an implementation task that specifies the ChatGPT auth-profile config schema, backward-compatibility behavior, credential isolation requirements, and acceptance criteria before Tech Lead/Coder implementation.
