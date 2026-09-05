---
id: TASK-2026-09-01-012-release-upstream-main-fedora
complexity: complex
track: implementation
slice: polish
status: superseded
superseded_by: TASK-2026-09-05-003-close-dual-host-repair
supersession_note: Candidate release failure and verified rollback remain historical; later repaired deployment is a distinct accepted result.
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

- [x] AC-1: Independent source/candidate/security approval authorizes release.
- [x] AC-2: Reviewed commits are pushed to fork `main` without force and exact remote ancestry is verified.
- [x] AC-3: Exact candidate registry digest/config identity is proven and Fedora rollback artifacts are complete.
- [ ] AC-4: Fedora-only deployment changes only LiteLLM image selector/service and passes health/models/Responses/MCP/LazyMCP/real-tool/log/observation gates.
- [x] AC-5: Failure triggers authorized rollback; NAS remains unchanged.
- [ ] AC-6: Final evidence, docs, registries, and durable memory are closed.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Final candidate authorization passes and fork `main` is already synchronized at `761742b1c98e68502e7b638bb61d8a0a5e93c4bc` with only evidence changes after qualified source. Deploy only `docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`, requiring config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` and source `bf58974a935521fa570fa7e280c51a00b2e5b54e`. Before selector mutation create owner-only rollback artifacts and a fresh custom-format Fedora DB backup with checksum/list and isolated restore verification. Change only `LITELLM_IMAGE`, recreate only `litellm --no-deps`, then verify exact identity/migrations/health/models/fallbacks/dependencies/config hashes/Responses/MCP/LazyMCP discovery/challenges/DCR audience/authorized `defend_memory-find`/logs and continuous 900-second soak with minute-15 full rerun. Any failure triggers exact previous-digest rollback and full verification; never auto-restore DB. Do not move mutable tags or touch NAS. Never expose secrets.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

### Summary

REJECT release and PASS rollback. The exact candidate was deployed after every pre-mutation backup and identity gate passed. The mandatory authorized `defend_memory-find` call timed out and the candidate became unhealthy before soak, so the exact prior digest was restored immediately. Rollback verification passed against the upgraded 161-migration schema

### Work Performed

- Pushed and verified the prerequisite release authorization closure on fork `main` without force
- Created the fresh protected rollback unit and custom database dump/checksum/list, completed isolated restore verification, and cleaned all disposable resources
- Changed only Fedora `LITELLM_IMAGE`, recreated only `litellm` with `--no-deps`, and deployed the exact signed digest/config/source
- Passed initial identity, migration, health, inventory, preservation, Chat, Responses, MCP REST, standard MCP, discovery, challenge, DCR, initialize, and audience checks
- Rolled back immediately after the authorized real-tool timeout and unhealthy transition; did not restore the database
- Verified exact rollback identity, health, schema compatibility, inventory, dependencies, protected state, Responses, MCP, LazyMCP, real tool, and bounded logs

### Acceptance Criteria Coverage

- **AC-1: PASS.** Independent source/candidate/security authorization was exact and fresh
- **AC-2: PASS.** Fork `main` and remote ancestry/content passed without force
- **AC-3: PASS.** Release identity and complete fresh rollback/backup/restore artifacts passed
- **AC-4: FAIL.** Candidate failed the authorized real-tool and health gates before the 900-second soak
- **AC-5: PASS.** Exact rollback was triggered and fully verified; NAS remained unchanged
- **AC-6: PASS FOR FAILED OUTCOME.** Evidence and closure records are complete and secret-free

### Documentation Impact

No product, architecture, technical, or CodeMap update is required because the candidate was rejected and steady-state behavior remains on the prior image

### Open Risks

- The candidate real-tool timeout and unhealthy transition require focused investigation before any retry
- Fedora production retains the successfully applied 161-migration schema; the prior image is verified compatible

### Recommended Next Step

PMA should keep the candidate blocked and route investigation. Reopen this task only after a new authorization; any retry requires a fresh protected database backup and restore verification

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT FEDORA RELEASE; VERIFIED ROLLBACK PASS. Candidate `docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3` passed all preflight, backup/restore, identity, migration, preservation, model, Responses, MCP, discovery, challenge, DCR, initialize, and audience gates before mandatory authorized `defend_memory-find` timed out and health became unhealthy. Exact prior digest `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04` is restored and passes full rollback verification against 161 migrations. No database restore, tag move, or NAS mutation occurred
