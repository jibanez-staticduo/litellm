---
id: TASK-2026-08-18-005-set-nas-gpt-alias-primary-account
complexity: standard
track: implementation
slice: logic
status: done
scr: SCR-2026-08-18-001-nas-gpt-alias-primary-account
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-18-005 - Set NAS GPT Alias Primary Account

## Objective
Make the default `chatgpt` account the primary deployment for every NAS LiteLLM `gpt-*` alias backed by the ChatGPT Responses provider, without changing Fedora or removing account2/account3 deployments.

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** logic

## Safety And Existing State
- NAS is healthy on recovered LiteLLM 1.92.0 with an exact 40-model inventory.
- The unfinished NAS 1.98.0 release is cancelled and must not be resumed.
- Back up affected routing rows/config before mutation.
- Do not expose credentials, alter auth files, remove deployments, change non-`gpt-*` aliases, or modify Fedora.
- Scope is the eight ChatGPT Responses aliases identified in preflight, from `gpt-5.3-codex` through `gpt-5.6-terra`; explicitly exclude the unrelated OpenAI speech route `gpt-4o-mini-tts`.

## Acceptance Criteria
- [ ] AC-1: Inventory all NAS ChatGPT Responses aliases matching `gpt-*` and record their current primary/default account selection without secrets; document the explicit `gpt-4o-mini-tts` exclusion.
- [ ] AC-2: Back up every affected routing/config row and establish an exact rollback procedure.
- [ ] AC-3: For every `gpt-*` alias, the primary deployment uses the default `chatgpt` account, never account2 or account3.
- [ ] AC-4: Account2/account3 deployments remain present and available; non-`gpt-*` aliases and total model inventory are unchanged.
- [ ] AC-5: Bounded routing smokes for representative `gpt-*` aliases prove the selected deployment/profile is default `chatgpt` using sanitized structured logs.
- [ ] AC-6: NAS remains healthy with readiness/liveliness HTTP 200, stable restart count, and `OOM=false`; Fedora remains unchanged.
- [ ] AC-7: Produce an AC-mapped evidence packet and record whether steady-state product documentation needs updating.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-18-005-set-nas-gpt-alias-primary-account/` with `SUMMARY.md` and sanitized logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Apply the approved SCR only on NAS. Make default `chatgpt` primary for every `gpt-*` alias while retaining account2/account3 deployments as non-primary and preserving all unrelated routes. Back up first, verify all matching aliases, capture sanitized routing proof, and do not resume the 1.98.0 release. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-7 pass
- Inventoried the eight scoped ChatGPT Responses aliases and confirmed all eight used account2 before mutation; explicitly excluded and preserved `gpt-4o-mini-tts`
- Created a mode-0600 exact eight-row NAS rollback transaction before mutation, with a checked restore and runtime reload procedure
- Removed only the scoped public rows' `chatgpt_auth_profile` key, then used the supported model-update endpoint to reload DB-backed models
- Verified all eight public primary deployments use the default profile while eight account2, eight account3, and eight qualified default deployments remain present
- Preserved the exact 40-model inventory, all 32 unrelated model rows, credentials, auth files, container identity, and Fedora
- Two bounded stateless no-retry Responses smokes returned HTTP 200 and selected the expected default-profile public deployments
- NAS remains healthy with readiness and liveliness HTTP 200, zero restarts, and `OOM=false`; Fedora remains unchanged
- Evidence: `.staticeng/evidences/TASK-2026-08-18-005-set-nas-gpt-alias-primary-account/SUMMARY.md`
- Documentation impact: no steady-state product or architecture documentation update is required
- `staticeng_validate` remains blocked by pre-existing repository-wide CodeMap gaps; its broad repair dry run was not applied in this atomic routing task

## QA Engineer: Post Implementation Expectations
- Independent read-only verification passed QA AC-1 through AC-4 with no runtime discrepancy.
- All eight scoped aliases resolve through the default profile; account2/account3 deployments and fallback targets remain present.
- `gpt-4o-mini-tts`, the 40-model inventory, NAS health, and Fedora state remain unchanged.
- Evidence contains no detected credential or private-data patterns.
- The unrelated repository-wide CodeMap validation debt remains explicitly recorded and is not safe to broaden into this routing task.

## PMA Final Closure
- Parent AC-1 through AC-7 passed with independent QA confirmation.
- Documentation closure: no steady-state product or architecture documentation update is required; the approved SCR and evidence are sufficient.
- Authorized for finalization and commit of non-secret StaticEng closure artifacts.
