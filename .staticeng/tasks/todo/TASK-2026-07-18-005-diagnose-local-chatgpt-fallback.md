---
id: TASK-2026-07-18-005-diagnose-local-chatgpt-fallback
complexity: standard
track: investigation
slice: foundation
status: done
scr: null
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-18-005 - Diagnose Local ChatGPT Fallback

## Objective
Determine why the LiteLLM instance on the current NAS does not advance to the next ChatGPT account after an account reaches rate limit.

## Scope
- Inspect the running NAS LiteLLM configuration, router settings, model deployments, cooldown state, and sanitized logs.
- Map the exact requested model group and configured fallback/deployment chain.
- Do not mutate runtime, configuration, credentials, or authentication state.
- Do not send inference requests unless existing evidence is insufficient; if required, return to PMA first.

## Acceptance Criteria
- [ ] AC-1: Identify the affected public model and account chain.
- [ ] AC-2: Identify the exact rate-limit error and LiteLLM routing decision.
- [ ] AC-3: Determine whether the fault is configuration, exception classification, affinity, cooldown, or provider behavior.
- [ ] AC-4: Return a minimal repair and verification plan without exposing secrets.

## Handoff
[Agent Message] From: product_manager To: developer

Investigate the current NAS LiteLLM read-only. Existing source changes in `litellm/proxy/_experimental/mcp_server/server.py` and its test are unrelated and must remain untouched. Use sanitized config/admin/log evidence; do not make inference requests or runtime changes. Return the shared handoff contract and exact minimal repair.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Root cause is DB-backed fallback configuration plus profile-qualified model semantics.
- Account2 deployments are absent from every unqualified public GPT fallback chain.
- Qualified `chatgpt/*` IDs intentionally remain pinned and do not rotate profiles; rotating clients must request unqualified `gpt-*` IDs.
- Rate-limit classification, Redis, cooldown, and retry handling are functioning as configured.
