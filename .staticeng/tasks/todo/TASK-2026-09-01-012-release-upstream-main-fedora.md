---
id: TASK-2026-09-01-012-release-upstream-main-fedora
complexity: complex
track: implementation
slice: polish
status: active
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

Final candidate authorization passes and fork `main` is already synchronized at `761742b1c98e68502e7b638bb61d8a0a5e93c4bc` with only evidence changes after qualified source. Deploy only `docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`, requiring config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` and source `bf58974a935521fa570fa7e280c51a00b2e5b54e`. Before selector mutation create owner-only rollback artifacts and a fresh custom-format Fedora DB backup with checksum/list and isolated restore verification. Change only `LITELLM_IMAGE`, recreate only `litellm --no-deps`, then verify exact identity/migrations/health/models/fallbacks/dependencies/config hashes/Responses/MCP/LazyMCP discovery/challenges/DCR audience/authorized `defend_memory-find`/logs and continuous 900-second soak with minute-15 full rerun. Any failure triggers exact previous-digest rollback and full verification; never auto-restore DB. Do not move mutable tags or touch NAS. Never expose secrets.
