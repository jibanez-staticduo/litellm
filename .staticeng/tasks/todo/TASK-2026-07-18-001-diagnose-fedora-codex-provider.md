---
id: TASK-2026-07-18-001-diagnose-fedora-codex-provider
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

# Task: TASK-2026-07-18-001 - Diagnose Fedora Codex Provider

## Objective
Identify why Fedora Codex disconnects while sending Responses API requests through its local model-provider proxy to `litellm.defend.tech`, without changing runtime or configuration.

## Scope
- Inspect Fedora Codex configuration, app-server/provider processes, service state, and secret-safe logs.
- Trace the local ephemeral endpoint shown by Codex (`127.0.0.1:<port>/model-provider/v1/responses`) to its upstream LiteLLM route.
- Check LiteLLM and network readiness without exposing credentials, prompts, responses, or authorization material.
- Do not restart services, edit files, authenticate accounts, or send more than one bounded no-retry inference probe if diagnosis requires it.

## Acceptance Criteria
- [ ] AC-1: The failed request path and owning processes are mapped from Codex to LiteLLM.
- [ ] AC-2: Relevant Codex and LiteLLM logs identify the concrete failure or narrow it to a verified boundary.
- [ ] AC-3: Current configurations and service health are checked without secret disclosure or mutation.
- [ ] AC-4: A minimal repair plan, preservation constraints, and verification plan are returned to PMA.

## Handoff
[Agent Message] From: product_manager To: developer

Investigate read-only on Fedora over SSH. Classify the concrete failure using service/process/config/log evidence. Preserve secrets and avoid runtime changes. Return the shared handoff contract with exact safe repair steps and evidence locations; do not implement the repair.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Root cause: `codex-optima.service`, owner of `127.0.0.1:34160`, was stopped by SIGTERM and remained inactive; LiteLLM itself is healthy.
- The failed Codex request never reached LiteLLM.
- Configuration and credential bindings are present; no config or secret change is indicated.
- Product documentation is not required; operational service ownership should be captured in repair evidence.
