---
id: TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora
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

# Task: TASK-2026-07-09-001 - Add ChatGPT 5.6 Models Locally and on Fedora

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
Add new ChatGPT model aliases `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna` to the local/NAS LiteLLM instance and Fedora LiteLLM instance, modeled after the existing `chatgpt/gpt-5.5` deployment. Add them for both the default ChatGPT account and the account2 ChatGPT profile where applicable. On Fedora, also create account2 ChatGPT models so account2 can be authenticated later, without performing the auth flow now.

## User Requirements
- Local/NAS: add the three new models for the two ChatGPT providers/accounts currently present:
  - default ChatGPT account (`chatgpt/...` using default `auth.json`)
  - account2 (`chatgpt-account2/...` using `chatgpt_auth_profile: account2`)
- Fedora: add the same three default ChatGPT models.
- Fedora: additionally create second-account/account2 ChatGPT models for authentication later.
- Use the same shape/settings as existing `chatgpt/gpt-5.5` deployments unless a safer existing account2 template applies.
- Do not perform account2 authentication on Fedora.
- Do not rebuild/redeploy images unless necessary; this should be database/model-registration only.
- Do not expose `.env`, master keys, API keys, tokens, cookies, auth files, refresh tokens, private keys, session tokens, DB URLs, or auth headers.

## Naming Expectations
Default account models:
- `chatgpt/gpt-5.6-sol`
- `chatgpt/gpt-5.6-terra`
- `chatgpt/gpt-5.6-luna`

Account2 models:
- Prefer existing account2 naming convention: `chatgpt-account2/gpt-5.6-sol`, `chatgpt-account2/gpt-5.6-terra`, `chatgpt-account2/gpt-5.6-luna`.
- If Fedora needs additional account2 clones for existing ChatGPT models so the user can authenticate account2 there later, create them using the same account2 naming convention and `chatgpt_auth_profile: account2`.

## Scope
- Inspect current `chatgpt/gpt-5.5` definitions on local/NAS and Fedora.
- Add missing model definitions through admin API or direct DB mutation, preserving existing settings and adding only the intended model rows.
- Verify model visibility through `/model/info` or equivalent on both systems.
- Verify no existing model definitions were lost.
- Do not send real ChatGPT completion requests unless needed for model visibility, and do not trigger/complete account2 login.

## Acceptance Criteria
- [x] AC-1: Local/NAS default ChatGPT models `chatgpt/gpt-5.6-sol`, `chatgpt/gpt-5.6-terra`, and `chatgpt/gpt-5.6-luna` exist and mirror `chatgpt/gpt-5.5` settings except for model name/provider model target.
- [x] AC-2: Local/NAS account2 models `chatgpt-account2/gpt-5.6-sol`, `chatgpt-account2/gpt-5.6-terra`, and `chatgpt-account2/gpt-5.6-luna` exist with `chatgpt_auth_profile: account2`.
- [x] AC-3: Fedora default ChatGPT models `chatgpt/gpt-5.6-sol`, `chatgpt/gpt-5.6-terra`, and `chatgpt/gpt-5.6-luna` exist and mirror Fedora `chatgpt/gpt-5.5` settings.
- [x] AC-4: Fedora account2 ChatGPT models exist for the second account using `chatgpt_auth_profile: account2`, including the three new `gpt-5.6-*` aliases and any existing regular Fedora ChatGPT aliases needed for later account2 auth.
- [x] AC-5: Existing local/NAS and Fedora models remain present; no unintended deletions/renames.
- [x] AC-6: Local/NAS and Fedora health/admin model inspection succeeds after changes.
- [x] AC-7: No ChatGPT account2 auth flow is triggered or completed on Fedora.
- [x] AC-8: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/` with `SUMMARY.md` and safe logs.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-07-09-001-add-chatgpt-56-models-local-fedora/` containing:
- `SUMMARY.md` mapping AC-1 through AC-8.
- `logs/` with secret-safe pre/post inventories, mutation method, model comparison, and health/admin validation.

## Handoff
[Agent Message] From: product_manager To: developer

Please add the requested ChatGPT 5.6 model aliases locally and on Fedora, preserving all existing model definitions. Start with read-only inventories. Clone settings from `chatgpt/gpt-5.5`; for account2 use the existing account2 profile convention and `chatgpt_auth_profile: account2`. On Fedora, also create account2 models for the existing Fedora ChatGPT aliases so the user can authenticate later, but do not trigger or complete auth. Keep all evidence secret-safe. Do not commit; PMA owns closure.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Added requested ChatGPT 5.6 aliases on local/NAS and Fedora using LiteLLM admin API `POST /model/new`.
- No app code, image rebuild, deployment, auth file, or account2 authentication flow was changed.

### Local/NAS Models Created
- `chatgpt/gpt-5.6-sol`
- `chatgpt/gpt-5.6-terra`
- `chatgpt/gpt-5.6-luna`
- `chatgpt-account2/gpt-5.6-sol`
- `chatgpt-account2/gpt-5.6-terra`
- `chatgpt-account2/gpt-5.6-luna`

### Fedora Models Created
- `chatgpt/gpt-5.6-sol`
- `chatgpt/gpt-5.6-terra`
- `chatgpt/gpt-5.6-luna`
- `chatgpt-account2/gpt-5.3-codex`
- `chatgpt-account2/gpt-5.4`
- `chatgpt-account2/gpt-5.4-mini`
- `chatgpt-account2/gpt-5.5`
- `chatgpt-account2/gpt-5.6-sol`
- `chatgpt-account2/gpt-5.6-terra`
- `chatgpt-account2/gpt-5.6-luna`

### Verification
- Local `/health/readiness`, `/v1/models`, and `/model/info` returned HTTP 200; required local models are present; ChatGPT count is 16.
- Fedora `/health/readiness`, `/v1/models`, and `/model/info` returned HTTP 200; required Fedora models are present; ChatGPT count is 14.
- Inventory comparison reports `preserved_all_preexisting: true` and no removed rows for both local and Fedora.
- No account2 auth flow was triggered or completed on Fedora.

## PMA Final Closure

### Acceptance Criteria Coverage
- AC-1 through AC-8 are satisfied by evidence summary and logs.

### Documentation Impact
- Evidence-only operational model-registration documentation.

### Open Risks
- Fedora account2 models are visible and configured but intentionally unauthenticated until the user performs auth later.
- No live ChatGPT completion smoke was run for account2, by request.
