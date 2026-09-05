---
id: TASK-2026-09-01-004-deploy-lazymcp-oauth-nas
complexity: complex
track: implementation
slice: foundation
status: active
scr: SCR-2026-09-01-001-upstream-main-integration
parent: null
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 1
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

## Reopen History

### Reopen 1 - Verified Fedora product repair promotion

Historical rejection is superseded by the latest explicit user NAS authorization and Tech Lead functional/memory PASS in TASK-2026-09-05-001 logs/19-functional-memory-pass.md. Deploy ONLY `docker.staticduo.com/litellm@sha256:7b2368711ff10db3107772d627e03aa89319598f8897ff7431497775926b2eb9`, source `7a9ef0335303d973f3a228dcf7baadff18c82fb5`, after fresh NAS identity/architecture/schema/backup preflight. Preserve NAS-specific configuration, credentials, mounts, model/MCP catalog, and dependencies; do not copy Fedora settings blindly. Apply only candidate containment needed to avoid host exhaustion, documented against NAS capacity. Recreate only LiteLLM through its actual Compose path. Verify real SDK Responses JSON/stream, Chat, NAS read-only MCP/LazyMCP tool, discovery, readiness, resource behavior and at least 900 seconds observation. Recheck Fedora and prove identical image/source on both. No security remediation or harness repair. Recovery remains available for NAS failure; never restore DB destructively without approval.

[Agent Message] From: product_manager To: tech_lead

Execute promotion now; previous Fedora repair agent is paused, so you own the single implementation. Complete evidence and precise product/config diffs, then finalize required registries/docs before commit/non-force push to main. Verify local main and origin/main synchronization. Report deferred security separately. A successful deployment is not enough: both actual runtime validation and cross-host parity must pass before closure.
