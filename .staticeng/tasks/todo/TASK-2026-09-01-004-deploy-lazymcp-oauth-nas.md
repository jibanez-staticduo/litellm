---
id: TASK-2026-09-01-004-deploy-lazymcp-oauth-nas
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

# Task: Deploy LazyMCP OAuth to NAS

## Objective

After Fedora is independently approved, deploy the same immutable registry digest to NAS and validate complete parity with rollback prepared.

## Acceptance Criteria

- [ ] AC-1: Fedora post-observation Tech Lead authorization passes before NAS mutation.
- [ ] AC-2: Owner-only NAS backup/rollback artifacts capture selector/config/DB/state.
- [ ] AC-3: Only NAS LiteLLM selector changes and only `litellm` is recreated with no dependencies.
- [ ] AC-4: NAS runs the exact same registry digest/config image ID as Fedora with healthy, zero-restart, no-OOM state.
- [ ] AC-5: Models, Responses, `/mcp`, MCP REST, LazyMCP discovery/challenges/real tool and public routes pass.
- [ ] AC-6: Bounded logs and observation show no new regressions; cross-host parity is recorded.
- [ ] AC-7: Rollback executes on failure and split release is resolved explicitly.

## Handoff

[Agent Message] From: product_manager To: developer

Do not begin until PMA changes this task to active after Fedora approval. NAS only, then cross-host parity. Never print secrets. Stop and follow authorized rollback on any failed gate.

## Blocker Report

[Agent Message] From: product_manager To: developer

NAS promotion is explicitly rejected because candidate qualification failed and Fedora deployment is unauthorized. Do not mutate NAS.
