---
id: TASK-2026-07-10-001-set-chatgpt-56-pricing
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

# Task: TASK-2026-07-10-001 - Set ChatGPT 5.6 Pricing

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
Verify official GPT-5.6 Sol/Terra/Luna API pricing and update the local/NAS and Fedora LiteLLM model registrations for all default and account2 ChatGPT 5.6 aliases.

## Pricing Source
OpenAI published GPT-5.6 pricing per 1M tokens:
- GPT-5.6 Sol: $5 input / $30 output
- GPT-5.6 Terra: $2.50 input / $15 output
- GPT-5.6 Luna: $1 input / $6 output

Use per-token LiteLLM values:
- Sol: input `0.000005`, output `0.00003`
- Terra: input `0.0000025`, output `0.000015`
- Luna: input `0.000001`, output `0.000006`

## Scope
- Update pricing metadata for local/NAS:
  - `chatgpt/gpt-5.6-sol`
  - `chatgpt/gpt-5.6-terra`
  - `chatgpt/gpt-5.6-luna`
  - `chatgpt-account2/gpt-5.6-sol`
  - `chatgpt-account2/gpt-5.6-terra`
  - `chatgpt-account2/gpt-5.6-luna`
- Update pricing metadata for Fedora for the same default/account2 5.6 aliases.
- Preserve all non-pricing settings.
- Do not run ChatGPT auth or completion calls.
- Do not expose secrets.

## Acceptance Criteria
- [x] AC-1: Pricing source and conversion are recorded in evidence.
- [x] AC-2: Local/NAS all six 5.6 aliases have correct input/output costs.
- [x] AC-3: Fedora all six 5.6 aliases have correct input/output costs.
- [x] AC-4: Existing model definitions remain present and no unrelated models are mutated.
- [x] AC-5: Local/NAS and Fedora health/admin model inspection succeeds after updates.
- [x] AC-6: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-10-001-set-chatgpt-56-pricing/` with `SUMMARY.md` and safe logs.

## Handoff
[Agent Message] From: product_manager To: developer

Please update LiteLLM pricing metadata for GPT-5.6 Sol/Terra/Luna on local/NAS and Fedora, including account2 aliases. Start with read-only inventory, identify the exact pricing fields used by existing model registrations, update only pricing fields for the target aliases, and verify with `/model/info`. Use admin API if possible, direct DB only if needed. Do not run auth/completion calls. Keep evidence secret-safe. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Updated GPT-5.6 pricing metadata on local/NAS and Fedora using LiteLLM admin API `POST /model/update`.
- Updated only `litellm_params.input_cost_per_token` and `litellm_params.output_cost_per_token` for target aliases.
- Did not use direct DB writes, auth endpoints, completion calls, image rebuilds, or deployments.

### Final Pricing
- Sol: input `0.000005`, output `0.00003`.
- Terra: input `0.0000025`, output `0.000015`.
- Luna: input `0.000001`, output `0.000006`.

### Verification
- Local/NAS six target aliases verified with correct costs in `/model/info`.
- Fedora six target aliases verified with correct costs in `/model/info`.
- `model_info.input_cost_per_token` and `model_info.output_cost_per_token` match on all target rows.
- Non-pricing sanitized fields were preserved for all target aliases.
- Local and Fedora `/model/info`, `/health/readiness`, and `/health/liveliness` returned HTTP 200.

## PMA Final Closure

### Acceptance Criteria Coverage
- AC-1 through AC-6 are satisfied by evidence summary and logs.

### Documentation Impact
- Evidence-only operational pricing update documentation.

### Open Risks
- No live ChatGPT completion or auth calls were run by request; validation covers admin metadata and health only.
