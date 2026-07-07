---
id: TASK-2026-07-07-007-remove-defend-account2-model
complexity: standard
track: implementation
slice: foundation
status: done
scr: null
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-07-007 - Remove Mistaken Defend Account2 Model

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
Remove the mistakenly added `defend-account2/gpt-5.5` LiteLLM model deployment from the local/NAS LiteLLM database. `defend/gpt-5.5` is a model backed by another LiteLLM and should not have an account2 ChatGPT clone.

## Scope
- Remove only `defend-account2/gpt-5.5` from the local/NAS LiteLLM database.
- Keep all `chatgpt-account2/*` deployments.
- Keep `defend/gpt-5.5` unchanged.
- Do not rebuild/redeploy the image.
- Do not perform ChatGPT login.
- Do not expose secrets.

## Acceptance Criteria
- [x] AC-1: `defend-account2/gpt-5.5` is removed from LiteLLM database/model inspection.
- [x] AC-2: `defend/gpt-5.5` remains present and unchanged.
- [x] AC-3: `chatgpt-account2/gpt-5.3-codex`, `chatgpt-account2/gpt-5.3-codex-spark`, `chatgpt-account2/gpt-5.4`, `chatgpt-account2/gpt-5.4-mini`, and `chatgpt-account2/gpt-5.5` remain present with `chatgpt_auth_profile: account2`.
- [x] AC-4: LiteLLM remains healthy after removal.
- [x] AC-5: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-07-007-remove-defend-account2-model/` with `SUMMARY.md` and safe logs.

## Active Discussions
- DISCUSSION-003: Remove mistaken defend account2 LiteLLM model

## Handoff
[Agent Message] From: product_manager To: developer

Please remove only the mistaken `defend-account2/gpt-5.5` model deployment from the local/NAS LiteLLM database. Do not touch `defend/gpt-5.5` or the `chatgpt-account2/*` deployments. Verify via model inspection and direct DB check if needed. Capture safe evidence. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Removed only `defend-account2/gpt-5.5` from local/NAS LiteLLM using the LiteLLM admin API `POST /model/delete` against the target model id.
- No rebuild, redeploy, restart, ChatGPT login, live ChatGPT invocation, or application code change was performed.

### Verification
- `defend-account2/gpt-5.5` is absent from DB and `/model/info`.
- `defend/gpt-5.5` remains present.
- All required `chatgpt-account2/*` deployments remain present with `chatgpt_auth_profile = account2` in direct DB inspection.
- `/health/readiness`, `/health/liveliness`, and Docker health are healthy.

### Evidence
- `.staticeng/evidences/TASK-2026-07-07-007-remove-defend-account2-model/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-07-07-007-remove-defend-account2-model/logs/`

## PMA Final Closure

### Acceptance Criteria Coverage
- AC-1 through AC-5 are satisfied by evidence summary and logs.
- PMA rechecked Docker health for the running `litellm` container.

### Documentation Impact
- Evidence-only operational correction; no product docs required.

### Open Risks
- Account2 ChatGPT auth still requires user login later.
