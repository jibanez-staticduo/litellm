---
id: TASK-2026-07-12-001-remove-fedora-account2-models
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

# Task: TASK-2026-07-12-001 - Remove Fedora Account2 Models

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
Remove every Fedora LiteLLM deployment whose public model name starts with `chatgpt-account2/`, because Fedora does not yet have a second ChatGPT account.

## Scope
- Target Fedora LiteLLM only (`litellm.defend.tech` / SSH alias `fedora`).
- Inventory exact `chatgpt-account2/*` deployment names and IDs first.
- Remove all and only those deployments via LiteLLM admin API where possible.
- Preserve all regular `chatgpt/*` models and every unrelated model.
- Do not delete or modify auth files, credentials, fallbacks, images, or container configuration.
- Verify health and model inventory after deletion.
- Do not run provider completions or device auth.
- Remove the same `chatgpt-account2/*` model entries from Fedora `opencode_defend` `opencode.json`, specifically the `opencode-litellm` plugin override/catalog, while preserving all other OpenCode config and models.

## Acceptance Criteria
- [x] AC-1: All Fedora `chatgpt-account2/*` deployments are removed.
- [x] AC-2: All regular Fedora `chatgpt/*` deployments remain present and unchanged.
- [x] AC-3: All unrelated Fedora model deployments remain present; no unintended deletion.
- [x] AC-4: Fedora health/readiness/liveliness and `/model/info` pass after removal.
- [x] AC-5: No credential/auth file or account2 auth flow is touched.
- [x] AC-6: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-12-001-remove-fedora-account2-models/` with `SUMMARY.md` and safe logs.
- [x] AC-7: Fedora `opencode_defend` `opencode.json` `opencode-litellm` override contains no `chatgpt-account2/*` entries and preserves all other entries/settings.

## Handoff
[Agent Message] From: product_manager To: developer

On Fedora only, remove every model deployment whose public `model_name` starts with `chatgpt-account2/`. Inventory first, delete only exact deployment IDs through admin API, and verify regular `chatgpt/*` plus all unrelated models are preserved. Do not touch credentials/auth files or run inference/auth. Keep evidence secret-safe. Do not commit.

## Scope Extension
[Agent Message] From: product_manager To: developer

Also remove every `chatgpt-account2/*` model from Fedora `opencode_defend`'s `opencode.json`, specifically the `opencode-litellm` plugin override/model catalog. Back up the config with mode 0600, edit structurally, preserve every non-account2 setting/model, validate JSON/OpenCode config, and reload/restart only if required. Add sanitized pre/post model lists and rollback instructions to the same evidence packet. Do not expose secrets or full config contents.

## Implementation Findings

- Fedora OpenCode config resolved to `/home/staticduo/.config/opencode/opencode.json`
- Removed 7 `chatgpt-account2/*` keys only from the `@staticeng/opencode-litellm` override catalog
- Backup created at `/home/staticduo/.config/opencode/opencode.json.backup-20260712T074223Z-remove-account2` with mode `0600`
- Sanitized non-target catalog and non-catalog config digests match before and after
- JSON validation and `opencode debug config` passed; no restart was performed
- Existing OpenCode sessions require an owner restart to load config-time changes; new processes load the updated config
- Evidence and rollback commands are recorded in the existing task evidence packet

# Post Implementation Task Updates

## PMA Final Closure

### Summary
- Removed all seven `chatgpt-account2/*` Fedora LiteLLM deployments by exact deployment ID.
- Removed matching seven entries from Fedora OpenCode `@staticeng/opencode-litellm` overrides.
- Preserved all regular ChatGPT and unrelated models/settings.

### Verification
- Fedora account2 count: 7 -> 0.
- Fedora non-account2 deployments: all 12 name/ID pairs preserved exactly.
- Regular ChatGPT deployments: all 7 preserved exactly.
- `/model/info`, `/v1/models`, readiness, and liveliness HTTP 200; container healthy.
- OpenCode JSON and `opencode debug config` validation passed.

### Documentation Impact
- Evidence-only operational model/config removal documentation.

### Open Risks
- Existing already-running OpenCode sessions may retain startup-time config until restarted; new processes use updated config.
