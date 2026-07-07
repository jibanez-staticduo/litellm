---
id: TASK-2026-07-07-004-investigate-chatgpt-multi-account-auth
complexity: standard
track: investigation
slice: logic
status: done
scr: null
parent: null
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-07-004 - Investigate ChatGPT Multi-Account Auth

## Classification
- **complexity:** standard
- **track:** investigation
- **slice:** logic

## Objective
Investigate how LiteLLM's `chatgpt` subscription provider authenticates, stores tokens, refreshes sessions, and maps configured models to that auth context. Determine whether one LiteLLM proxy can safely expose multiple ChatGPT subscription accounts as separate provider/model namespaces such as `chatgpt/gpt-5.5`, `chatgpt2/gpt-5.5`, `chatgpt3/gpt-5.5`, each with distinct access tokens, refresh tokens, account IDs, and session state.

## User Need
The user has multiple ChatGPT subscription accounts and wants a single LiteLLM instance to route requests to each account independently. The current understanding is that LiteLLM may only support one ChatGPT auth context globally, possibly because login is driven through a log-emitted URL and shared credential files.

## Scope
- Inspect the existing ChatGPT provider implementation and login/authenticator code.
- Identify the current credential storage path, refresh-token ownership, account/session handling, and model/provider resolution path.
- Determine whether aliases like `chatgpt2` can be supported externally/config-only, via a lightweight plugin/provider wrapper, or only via core changes.
- Identify security and operational constraints for storing multiple refresh tokens without logging secrets.
- Do not implement changes in this task.

## Acceptance Criteria
- [x] AC-1: Explain the current ChatGPT auth/login flow, including how the login URL is surfaced, where credentials are stored, and how refresh happens.
- [x] AC-2: Explain why current model/provider resolution does or does not allow multiple independent `chatgpt` auth contexts.
- [x] AC-3: Provide at least two feasible design options for multi-account support, with implementation effort, risks, and likely files/modules affected.
- [x] AC-4: Recommend a preferred path for this fork, including whether an SCR and follow-up implementation task are required.
- [x] AC-5: Keep all findings free of raw tokens, refresh tokens, cookies, or other secrets.

## Expected Evidence
- Investigation notes in this task file under `# Investigation Findings` or a linked non-secret report.
- File/module references with line numbers where relevant.
- No code or configuration changes beyond StaticEng task/discussion artifacts.

## Active Discussions
- DISCUSSION-002: Investigate multi-account ChatGPT subscription auth in LiteLLM

## PMA Handoff
[Agent Message] From: product_manager To: technical_architect

Please investigate the ChatGPT subscription auth path in LiteLLM for multi-account feasibility. Focus on the existing `litellm/llms/chatgpt` implementation, provider/model resolution, token refresh and credential storage. Do not implement code. Return a concise but evidence-backed feasibility report covering AC-1 through AC-5, including specific files and line references. Avoid exposing any secrets or local credential values.

# Investigation Findings

## Technical Architect Notes
- Current auth is single-context: `Authenticator` reads `CHATGPT_TOKEN_DIR` or `~/.config/litellm/chatgpt`, then `CHATGPT_AUTH_FILE` or `auth.json`; tokens are refreshed in-place from the same file and account ID is derived from token claims.
- Device login prints a verification URL and user code to stdout, then polls/exchanges credentials and persists `access_token`, `refresh_token`, `id_token`, `expires_at`, and `account_id` in that one auth file. No raw secret values recorded here.
- Provider resolution only recognizes literal `chatgpt`; aliases like `chatgpt2/gpt-5.5` are not supported config-only because `chatgpt2` is neither in `provider_list` nor `LlmProviders`, and the ChatGPT configs instantiate an unparameterized `Authenticator()`.
- Feasible designs: (1) core multi-profile support via `chatgpt_auth_profile`/`chatgpt_token_dir` per deployment, preferred for this fork; (2) register provider aliases (`chatgpt2`, `chatgpt3`) mapped to ChatGPT configs with alias-specific auth files; (3) external process-per-account proxies with distinct env vars, lowest code risk but operationally heavier.
- Preferred path requires an SCR and follow-up implementation task because it changes provider auth contracts, config schema expectations, secret storage semantics, and tests.

# PMA Closure

## Acceptance Criteria Coverage
- AC-1: Covered by source inspection of `litellm/llms/chatgpt/authenticator.py`, `common_utils.py`, and ChatGPT transformations.
- AC-2: Covered by source inspection of provider registration, provider resolution, router validation, and ChatGPT config instantiation.
- AC-3: Covered with three options: core auth profiles, provider aliases, and external process-per-account routing.
- AC-4: Preferred path is core auth profiles plus SCR before implementation; immediate workaround is process-per-account routing.
- AC-5: No raw tokens, refresh tokens, cookies, or secret values were inspected or recorded.

## Documentation Impact
- No product docs updated; this was an investigation-only task.
- Future implementation should update ChatGPT provider configuration docs and operator login guidance.

## Open Risks
- `staticeng_validate` remains known non-green because of unrelated CodeMap/link inventory debt.
- Multi-account support touches credential storage and refresh semantics, so implementation must include secret-safe tests and no-token logging verification.

## Recommended Next Step
- Open an SCR for ChatGPT multi-account auth profiles if the user approves implementation.
