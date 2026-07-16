---
id: TASK-2026-07-14-002-reauth-account2-create-account3-nas
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

# Task: TASK-2026-07-14-002 - Reauth Account2 and Create Account3 on NAS

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
On `litellm.staticduo.com` local/NAS, trigger a fresh device-auth flow for account2, clone every current `chatgpt-account2/*` deployment into `chatgpt-account3/*` using profile `account3`, add matching `@staticeng/opencode-litellm` overrides to the NAS OpenCode config, then trigger account3 device auth.

## Scope
- NAS/local only; do not change Fedora.
- Inventory every account2 deployment and clone full settings/pricing/model_info to account3, changing only public alias/profile/IDs as required.
- Preserve all existing models/settings.
- Update the NAS OpenCode `opencode.json` `@staticeng/opencode-litellm` overrides, cloning all account2 entries to account3.
- Back up OpenCode config mode 0600; structured atomic edit and validation.
- Trigger exactly one device-auth request for account2 and one for account3.
- Do not complete either login.
- Device-auth URLs/codes are transient: return directly to PMA only; never persist to task/evidence/memory/git.
- Do not expose auth files, tokens, keys, headers, DB URLs, account IDs, prompts, responses, or session identifiers.

## Acceptance Criteria
- [x] AC-1: Every current NAS account2 deployment has an account3 clone with profile `account3` and equivalent settings/pricing.
- [x] AC-2: Matching account3 OpenCode plugin overrides exist and unrelated config is preserved.
- [x] AC-3: NAS health/admin/OpenCode config validation passes and no pre-existing model is lost.
- [x] AC-4: Exactly one account2 auth trigger yields transient URL/code.
- [x] AC-5: Exactly one account3 auth trigger yields transient URL/code.
- [x] AC-6: Neither login is completed by the agent and no auth material is persisted in repo artifacts.
- [x] AC-7: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-14-002-reauth-account2-create-account3-nas/` with setup/validation evidence excluding transient auth details.

## Handoff
[Agent Message] From: product_manager To: developer

On NAS/local only, safely inventory account2 models, clone all to account3 with `chatgpt_auth_profile: account3`, clone corresponding OpenCode LiteLLM overrides with backup/validation, then trigger exactly one device-auth request for account2 and one for account3. Return both transient URL/codes only in your final response. Never write auth details to files/evidence/memory/git. Do not complete login or commit.

# Post Implementation Task Updates

## QA: Post-Implementation Validation

### Summary
- QA reviewed the complete task and existing evidence packet without rerunning authentication or inference and without accessing or changing runtime, configuration, or auth state
- The evidence is internally consistent, secret-safe, and sufficient for closure

### Acceptance Criteria Coverage
- AC-1: PASS. `inventory-before.log`, `setup.log`, and `validation.log` show eight source account2 deployments, eight account3 clones, profile `account3`, matching physical models, and equivalent non-identity settings, metadata, and pricing
- AC-2: PASS. Seven account3 OpenCode overrides match the seven account2 overrides after public ID/name adaptation; structured atomic editing, unrelated-config preservation, and a mode-`0600` backup are documented
- AC-3: PASS. All 26 pre-existing deployments remain present; post-change model/admin/readiness checks, database connectivity, JSON parsing, and resolved OpenCode config validation pass
- AC-4: PASS. Evidence records one account2 device flow, zero retries, and an incomplete authorization timeout; transient URL/code details are deliberately excluded
- AC-5: PASS. Evidence records one account3 device flow, zero retries, and an incomplete authorization timeout; transient URL/code details are deliberately excluded
- AC-6: PASS. The agent did not complete either login. Later completion is explicitly attributed to an external actor, and repository evidence contains only sanitized field-presence and result metadata
- AC-7: PASS. The evidence packet contains `SUMMARY.md`, pre-change inventory, setup evidence, and validation evidence with no persisted auth values or transient device details

### Documentation Impact
- Operational evidence only; no product or user-facing documentation change is required

### Open Risks
- Exact transient URL/code values and their direct handoff cannot be persisted or independently revalidated by design; the sanitized device-flow attestations and subsequent successful per-profile verification provide the available closure evidence
- Post-auth inference was performed before this QA review, but QA performed no new authentication or inference and made no runtime changes

### QA Recommendation
- Close the task; AC-1 through AC-7 are traceable to the existing sanitized evidence packet
