---
id: TASK-2026-09-01-003-deploy-lazymcp-oauth-fedora
complexity: complex
track: implementation
slice: foundation
status: blocked
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: Deploy LazyMCP OAuth to Fedora

## Objective

Deploy the independently qualified immutable candidate to Fedora only, validate every release gate, and complete the observation window with rollback prepared.

## Acceptance Criteria

- [ ] AC-1: Qualification and Tech Lead promotion authorization pass before mutation.
- [ ] AC-2: Owner-only backup and rollback evidence capture current selector/config/DB/state.
- [ ] AC-3: Only the Fedora LiteLLM image selector changes; only service `litellm` is recreated with no dependencies.
- [ ] AC-4: Exact registry digest/config image ID, health, readiness/liveness, zero restarts, and no OOM are verified.
- [ ] AC-5: Models, Responses, `/mcp`, MCP REST, all LazyMCP discovery/challenge forms, authorized initialize and real registered tool pass.
- [ ] AC-6: Bounded logs and 15-minute observation show no new migration/auth/MCP/traceback/5xx regressions.
- [ ] AC-7: Evidence and signed handoff authorize or reject NAS promotion; rollback is executed on failure.

## Handoff

[Agent Message] From: product_manager To: developer

Do not begin until PMA changes this task to active with exact qualified registry digest and Tech Lead handoff. Fedora only. Preserve all unrelated config and never print secrets. Stop on any failed gate and follow the authorized rollback; do not touch NAS.

## Blocker Report

[Agent Message] From: product_manager To: developer

Deployment is explicitly rejected by Tech Lead. Candidate manifest `sha256:9f642cc38083d1600e62cfb473799a7d52ba89f6c8ff0c4a00940cddc386e619` contains a fixable High vulnerability and lacks exact-builder qualification, approved signing/attestation, complete publisher provenance disposition, durable scan/SBOM artifacts, and candidate-bound real-tool proof. Do not mutate Fedora.
