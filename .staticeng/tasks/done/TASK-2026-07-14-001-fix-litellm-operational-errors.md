---
id: TASK-2026-07-14-001-fix-litellm-operational-errors
complexity: standard
track: implementation
slice: logic
status: done
scr: null
parent: TASK-2026-07-13-002-investigate-litellm-errors-both
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-14-001 - Fix LiteLLM Operational Errors

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** logic

## Objective
Reduce actionable NAS/Fedora LiteLLM errors through DB/client configuration and operational tuning, then decide with evidence whether any remaining reproducible defect requires upstream replay and a new image.

## Scope
- Attribute Fedora invalid model requests to exact unavailable model names and affected local clients using sanitized fields only; correct known Fedora Hermes/OpenClaw/OpenCode catalogs/defaults if stale.
- Attribute NAS 507 and LazyMCP 500 errors to sanitized error classes/routes and correct DB/client/MCP config where safe.
- Review NAS retry/cooldown/fallback settings and apply bounded DB-backed tuning only if it reduces provider-error fan-out without disabling valid cross-account failover.
- Preserve models, credentials, prompts, responses, and identities.
- Re-measure bounded errors after changes.
- If a reproducible code bug remains, stop and create upstream replay + implementation/release tasks; do not silently patch old history.

## Acceptance Criteria
- [x] AC-1: Fedora unavailable model names and stale client catalogs are identified and corrected where under our control.
- [x] AC-2: NAS 507 and LazyMCP 500 causes are identified and corrected where config/client-related.
- [x] AC-3: Retry/fallback tuning is DB-backed, bounded, and preserves explicit bidirectional account failover.
- [x] AC-4: Post-change error measurement shows improvement or documents unavoidable provider/client errors.
- [x] AC-5: Regular/account2 Sol remain operational on both instances.
- [x] AC-6: Any remaining code defect has a reproducible test and a proposed upstream replay/release task.
- [x] AC-7: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-14-001-fix-litellm-operational-errors/` with `SUMMARY.md` and safe logs.

## Handoff
[Agent Message] From: product_manager To: developer

Fix the actionable errors found in the parent investigation using DB/client/MCP configuration first. Attribute invalid model names and route-specific failures safely, correct stale catalogs/configs, tune retries/fallbacks only through DB-backed settings, then re-measure. Preserve explicit account failover and all credentials/models. If a reproducible code bug remains, stop and report the upstream replay/code/release plan rather than patching immediately. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Changes
- Removed stale Fedora Hermes/OpenClaw catalog models absent from live LiteLLM; defaults/fallbacks preserved.
- Reduced NAS DB-backed `router_settings.num_retries` from 3 to 1; preserved cooldown, allowed fails, and all 8 fallback rules.
- Restarted affected gateways/LiteLLM and validated health.

### Root Causes
- NAS 507: upstream ChatGPT `Insufficient Storage`, not LiteLLM budget/quota policy.
- NAS LazyMCP 500: stale caller-key authentication failures before MCP dispatch; current client/discovery healthy.
- Fedora 400: unavailable aliases `qwen3` and `deepseek_v4_flash`; stale local catalogs cleaned where controlled.
- Remaining NAS 429/503: provider rate-limit/availability conditions.

### Verification
- Post-change window: no Fedora unavailable-model errors, NAS 507s, or LazyMCP 500s.
- Fedora catalogs have zero entries absent from live inventory.
- NAS live settings show `num_retries=1`; all fallback rules preserved.
- Sol models were not changed and remain operational per parent evidence/current traffic.

## PMA Final Closure

### Acceptance Criteria Coverage
- AC-1 through AC-7 satisfied by evidence.

### Documentation Impact
- Evidence-only operational tuning documentation.

### Release Decision
- No reproducible code defect remains; upstream replay/new image is not required for these errors.
