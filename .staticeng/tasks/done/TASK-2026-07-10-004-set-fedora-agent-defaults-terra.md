---
id: TASK-2026-07-10-004-set-fedora-agent-defaults-terra
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

# Task: TASK-2026-07-10-004 - Set Fedora Agent Defaults to GPT-5.6 Terra

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
Change Fedora Hermes and OpenClaw default models from GPT-5.5 to the default-account GPT-5.6 Terra model while preserving all model catalogs and unrelated settings.

## Required Defaults
- Hermes: `chatgpt/gpt-5.6-terra`
- OpenClaw: `litellm/chatgpt/gpt-5.6-terra`

## Scope
- Inspect current defaults and service status first.
- Back up both configs with mode `0600` before mutation.
- Change only the default/primary model fields.
- Preserve model catalogs, provider configuration, fallbacks, and unrelated settings.
- Validate YAML/JSON and native app config.
- Restart/reload gateways if required and verify status.
- Do not run authentication or completion/inference calls.
- Do not expose secrets or full config contents.

## Acceptance Criteria
- [x] AC-1: Hermes default is `chatgpt/gpt-5.6-terra`.
- [x] AC-2: OpenClaw default is `litellm/chatgpt/gpt-5.6-terra`.
- [x] AC-3: Existing model catalogs and unrelated settings are preserved.
- [x] AC-4: Config parsing/native validation passes for both apps.
- [x] AC-5: Both gateways are active/running after required restart/reload.
- [x] AC-6: Secret-safe backups and rollback commands are captured.
- [x] AC-7: No auth or inference calls are made.
- [x] AC-8: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-10-004-set-fedora-agent-defaults-terra/` with `SUMMARY.md` and safe logs.

## Handoff
[Agent Message] From: product_manager To: developer

Please set Fedora Hermes default to `chatgpt/gpt-5.6-terra` and OpenClaw default to `litellm/chatgpt/gpt-5.6-terra`. Start read-only, back up both configs, change only the default fields, preserve catalogs/settings, validate, restart gateways if needed, and verify status. Do not run auth/inference calls or expose secrets. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Hermes default changed from `chatgpt/gpt-5.5` to `chatgpt/gpt-5.6-terra`.
- OpenClaw default changed from `litellm/chatgpt/gpt-5.5` to `litellm/chatgpt/gpt-5.6-terra`.
- Only `model.default` and `agents.defaults.model.primary` changed.

### Backups
- Hermes: `/home/staticduo/.hermes/config.yaml.bak-terra-20260710T235442+0200`.
- OpenClaw: `/home/staticduo/.openclaw/openclaw.json.bak-terra-20260710T235442+0200`.
- Both backups use mode `0600`.

### Verification
- YAML/JSON parsing passed.
- `hermes config check`, `hermes doctor`, and `openclaw config validate` passed.
- OpenClaw provider/catalog/fallback state was preserved; model count remains 19.
- Both gateways restarted and are active/running.
- No auth or inference calls were made.

## PMA Final Closure

### Acceptance Criteria Coverage
- AC-1 through AC-8 satisfied by evidence summary and logs.

### Documentation Impact
- Evidence-only operational configuration update.

### Open Risks
- Hermes doctor retains pre-existing optional provider/tool warnings.
