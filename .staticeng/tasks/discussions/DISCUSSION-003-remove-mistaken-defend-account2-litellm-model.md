---
id: DISCUSSION-003
title: "Remove mistaken defend account2 LiteLLM model"
status: closed
summarized_by: product_manager
source: runtime-transcript
---

# Discussion Summary

## Topic
Remove the mistakenly added `defend-account2/gpt-5.5` LiteLLM deployment.

## User Correction
The user clarified that `defend/gpt-5.5` is a model served by another LiteLLM, not a ChatGPT subscription model, so it should not have an account2 clone.

## Outcome
- Removed only `defend-account2/gpt-5.5` from the local/NAS LiteLLM deployment.
- Kept `defend/gpt-5.5` unchanged.
- Kept all required `chatgpt-account2/*` deployments.
- LiteLLM remained healthy.
- No rebuild, redeploy, restart, ChatGPT login, or live ChatGPT invocation was performed.

## Verification
- `defend-account2/gpt-5.5` is absent from DB and `/model/info`.
- `defend/gpt-5.5` remains present.
- `chatgpt-account2/gpt-5.3-codex`, `chatgpt-account2/gpt-5.3-codex-spark`, `chatgpt-account2/gpt-5.4`, `chatgpt-account2/gpt-5.4-mini`, and `chatgpt-account2/gpt-5.5` remain present with `chatgpt_auth_profile = account2`.
- Readiness, liveliness, and Docker health passed.

## Follow-Up
Account2 login still needs to be completed later by the user before real account2 ChatGPT calls succeed.
