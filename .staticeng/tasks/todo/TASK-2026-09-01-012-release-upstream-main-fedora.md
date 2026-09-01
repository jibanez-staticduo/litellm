---
id: TASK-2026-09-01-012-release-upstream-main-fedora
complexity: complex
track: implementation
slice: polish
status: todo
scr: SCR-2026-09-01-001-upstream-main-integration
parent: null
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: Release upstream integration to main and Fedora

## Objective

After complete independent approval, push the reviewed integration to fork `main`, publish the exact qualified digest, deploy Fedora only with rollback, and validate full behavior and observation.

## Acceptance Criteria

- [ ] AC-1: Independent source/candidate/security approval authorizes release.
- [ ] AC-2: Reviewed commits are pushed to fork `main` without force and exact remote ancestry is verified.
- [ ] AC-3: Exact candidate registry digest/config identity is proven and Fedora rollback artifacts are complete.
- [ ] AC-4: Fedora-only deployment changes only LiteLLM image selector/service and passes health/models/Responses/MCP/LazyMCP/real-tool/log/observation gates.
- [ ] AC-5: Failure triggers authorized rollback; NAS remains unchanged.
- [ ] AC-6: Final evidence, docs, registries, and durable memory are closed.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Do not begin until PMA activates this task with final candidate authorization. Push fork `main` first only if all approval gates pass, then deploy exact digest to Fedora with rollback. NAS is explicitly out of scope. Never force-push or expose secrets.
