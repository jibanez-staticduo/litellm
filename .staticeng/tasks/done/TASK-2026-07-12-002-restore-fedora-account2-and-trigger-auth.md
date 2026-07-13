---
id: TASK-2026-07-12-002-restore-fedora-account2-and-trigger-auth
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

# Task: TASK-2026-07-12-002 - Restore Fedora Account2 Models and Trigger Auth

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
Restore Fedora LiteLLM account2 ChatGPT deployments and matching Fedora OpenCode `@staticeng/opencode-litellm` overrides, then trigger one account2 request to obtain a transient device-auth URL/code for the user.

## Models
- `chatgpt-account2/gpt-5.3-codex`
- `chatgpt-account2/gpt-5.4`
- `chatgpt-account2/gpt-5.4-mini`
- `chatgpt-account2/gpt-5.5`
- `chatgpt-account2/gpt-5.6-luna`
- `chatgpt-account2/gpt-5.6-sol`
- `chatgpt-account2/gpt-5.6-terra`

## Scope
- Fedora only.
- Clone each regular `chatgpt/*` deployment's current settings/pricing into an account2 public alias and add `chatgpt_auth_profile: account2`.
- Restore matching OpenCode overrides in `/home/staticduo/.config/opencode/opencode.json` under `@staticeng/opencode-litellm`, preserving all other settings.
- Back up OpenCode config with mode 0600.
- Verify health, model visibility, pricing/profile settings, and exact preservation of all pre-existing rows/settings.
- Trigger one minimal request to `chatgpt-account2/gpt-5.6-sol` only after setup.
- Device-auth URL/code is transient: never write it to repo evidence, memory, logs, task files, or git; return directly to PMA only.
- Do not complete login.

## Acceptance Criteria
- [x] AC-1: Seven Fedora account2 LiteLLM deployments exist with `chatgpt_auth_profile: account2` and current matching regular settings/pricing.
- [x] AC-2: Seven matching OpenCode plugin overrides exist and all unrelated config is preserved.
- [x] AC-3: Fedora LiteLLM health/admin validation passes; no pre-existing models are lost.
- [x] AC-4: OpenCode JSON and resolved config validation pass.
- [x] AC-5: One account2 request triggers device auth and transient URL/code is returned only to PMA.
- [x] AC-6: Login is not completed by the agent and no secret/auth material is persisted in repo evidence.
- [x] AC-7: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-12-002-restore-fedora-account2-and-trigger-auth/` with setup/validation evidence excluding transient auth details.

## Handoff
[Agent Message] From: product_manager To: developer

Restore all seven Fedora account2 LiteLLM models by cloning matching regular settings and adding `chatgpt_auth_profile: account2`. Restore matching OpenCode plugin overrides structurally with backup and validation. Preserve all other models/settings. Then trigger exactly one account2 Sol request and return the transient device-auth URL/code directly to PMA only; never write it to files/evidence/memory/git. Do not complete login or commit.

# Post Implementation Task Updates

## PMA Final Closure

### Summary
- Restored seven account2 deployments and seven OpenCode plugin overrides on Fedora.
- User completed device authorization; account2 Sol smoke returned HTTP 200 without a new device-code prompt.
- Dual-account QA confirmed account2 operational; regular account selected correctly but was rate-limited.

### Acceptance Criteria Coverage
- AC-1 through AC-7 satisfied by sanitized evidence.

### Documentation Impact
- Evidence-only operational setup documentation.

### Open Risks
- Existing OpenCode processes may need restart to load startup-time catalog changes.

## QA Post-Auth Verification

After the user completed device authorization, QA inspected the Fedora account2 auth file without reading values into evidence: the file exists, has mode `0600`, has a current UTC mtime, parses as a JSON object, and contains non-empty access-token, refresh-token, and account-ID keys.

Exactly one minimal request to Fedora local LiteLLM model `chatgpt-account2/gpt-5.6-sol` returned HTTP `200` and the exact harmless sentinel. Request-scoped container logs identified the selected account2 deployment and contained no new device-code/auth prompt. The selected profile was not emitted in available structured response headers or logs; the sanitized deployment validation already confirms `chatgpt_auth_profile: account2`. Credentials, auth contents, account ID, response body, identifiers, URL, and code were not persisted.

## QA Dual-Account Smoke

QA sent exactly one additional harmless request to each Fedora-local Sol public model with distinct exact sentinels and no retries. `chatgpt/gpt-5.6-sol` selected its matching public deployment but returned HTTP `429` with a sanitized rate-limit classification, so its sentinel did not match; provider configuration uses the `chatgpt/` physical prefix, while no backend API prefix or selected profile was available in the failed request's sanitized headers/logs. `chatgpt-account2/gpt-5.6-sol` returned HTTP `200`, matched its exact sentinel, reported the matching public response/deployment model, used the configured `chatgpt/` physical provider prefix and `https://chatgpt.com/backend-api/codex` backend prefix, and emitted no structured selected profile; prior sanitized deployment validation confirms profile `account2`. Neither request produced a new device-code/auth prompt. Proxy credentials, headers, auth contents, response bodies, response identifiers, and raw logs were not persisted.
