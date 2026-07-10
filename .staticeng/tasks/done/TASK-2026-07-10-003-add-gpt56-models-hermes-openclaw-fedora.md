---
id: TASK-2026-07-10-003-add-gpt56-models-hermes-openclaw-fedora
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

# Task: TASK-2026-07-10-003 - Add GPT-5.6 Models to Hermes and OpenClaw on Fedora

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
Update Fedora's Hermes and OpenClaw model catalogs to expose six LiteLLM-backed ChatGPT 5.6 models while preserving their existing default model (`gpt-5.5`) and all existing models/settings.

## Target Models
Default ChatGPT account:
- `chatgpt/gpt-5.6-sol`
- `chatgpt/gpt-5.6-terra`
- `chatgpt/gpt-5.6-luna`

Second ChatGPT account:
- `chatgpt-account2/gpt-5.6-sol`
- `chatgpt-account2/gpt-5.6-terra`
- `chatgpt-account2/gpt-5.6-luna`

## User Requirements
- Configure both Hermes and OpenClaw on Fedora.
- Both point to `https://litellm.staticduo.com/v1`.
- Add all six models to each application's selectable/known model catalog.
- Keep current default model unchanged (`gpt-5.5`).
- Preserve all existing models and unrelated settings.
- Do not run account2 authentication or real completion calls.

## Scope
- Read-only inspect actual Fedora Hermes and OpenClaw configs and service state first.
- Back up config files before mutation, without copying secrets into repository evidence.
- Make minimal config changes using native CLI/config APIs where safe, or structured YAML/JSON edits preserving permissions.
- Restart/reload relevant gateway/services only if required for catalog changes to take effect.
- Validate config syntax and confirm all six new model IDs are recognized/present.
- Do not expose API keys, tokens, cookies, auth headers, `.env`, private keys, sessions, or user message data.

## Acceptance Criteria
- [x] AC-1: Hermes Fedora catalog contains all six target models.
- [x] AC-2: OpenClaw Fedora catalog contains all six target models.
- [x] AC-3: Hermes default model remains its existing GPT-5.5 selection.
- [x] AC-4: OpenClaw default model remains its existing GPT-5.5 selection.
- [x] AC-5: All pre-existing Hermes/OpenClaw models and unrelated config settings remain present.
- [x] AC-6: Config syntax/native validation and service/gateway status checks pass after updates.
- [x] AC-7: Backups and rollback instructions are captured in secret-safe evidence.
- [x] AC-8: No account2 authentication or completion calls are performed.
- [x] AC-9: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-10-003-add-gpt56-models-hermes-openclaw-fedora/` with `SUMMARY.md` and safe logs.

## Expected Evidence
- `SUMMARY.md` mapping AC-1 through AC-9.
- `logs/` with sanitized pre/post model lists, validation/status, backup paths, and rollback commands.
- Never copy full config files or secret values into evidence.

## Handoff
[Agent Message] From: product_manager To: developer

Please configure Fedora Hermes and OpenClaw to expose all six target LiteLLM ChatGPT 5.6 model IDs. Start with read-only inspection and determine each app's native model catalog schema and current default. Back up configs, make the smallest structured edits, preserve defaults and all existing models/settings, validate syntax/status, and avoid completion/auth calls. Keep all evidence secret-safe. Do not commit; PMA owns closure.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Added all six target GPT-5.6 model IDs to Fedora Hermes provider `openclaw-litellm.models`.
- Added all six targets to Fedora OpenClaw provider `litellm.models` and selectable `agents.defaults.models`.
- Preserved both GPT-5.5 defaults and all pre-existing model entries/settings.
- Restarted both gateways to load changes; both are active/running.

### Backups
- Hermes: `/home/staticduo/.hermes/config.yaml.bak.TASK-2026-07-10-003.20260710T152203Z`.
- OpenClaw: `/home/staticduo/.openclaw/openclaw.json.bak.TASK-2026-07-10-003.20260710T152203Z`.
- Both backups mode `0600`.

### Verification
- Hermes models: 18 -> 24; default remains `chatgpt/gpt-5.5`.
- OpenClaw provider models: 12 -> 18; selectable models: 18 -> 24; default remains `litellm/chatgpt/gpt-5.5`.
- Both base URLs remain `https://litellm.staticduo.com/v1`.
- YAML/JSON parsing and native config validation passed.
- `hermes config check`, `hermes doctor`, `openclaw config validate`, and both gateway status commands exited successfully.
- No auth or inference calls were made.

## PMA Final Closure

### Acceptance Criteria Coverage
- AC-1 through AC-9 are satisfied by evidence summary and logs.

### Documentation Impact
- Evidence-only operational agent configuration documentation.

### Open Risks
- Hermes doctor retains pre-existing non-blocking provider/setup warnings.
- Functional inference was intentionally not tested per task safety scope.
