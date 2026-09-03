# TASK-2026-09-01-012 Evidence Summary

## Summary

REJECT Fedora release and PASS verified rollback. The exact signed digest deployed after the protected database backup and isolated restore gate passed. Identity, migration, health, inventory, configuration preservation, Chat, Responses, MCP REST, standard MCP, all six LazyMCP discovery aliases, exact challenge variants, DCR, and cross-audience rejection passed initially. The required authorized `defend_memory-find` call then timed out, and the candidate became unhealthy with readiness and liveliness unavailable. The release was rolled back immediately to the exact prior digest without restoring the database. The prior image is healthy and functionally verified against the upgraded 161-migration schema

## Work Performed

- Pushed the prerequisite authorization closure to fork `main` without force, then verified remote ancestry and zero non-StaticEng changes after qualified source `bf58974a935521fa570fa7e280c51a00b2e5b54e`
- Freshly verified the final registry manifest/config chain, source label, amd64 platform, StaticDuo signature, SPDX/CycloneDX/SLSA attestations, transparency-log inclusion, and exact release annotations
- Created owner-only Fedora attempt `TASK-2026-09-01-012-20260903T212734Z` with mode `0700` directories and `0600` files, including exact rollback configuration and image inspection
- Created a fresh 202,546,183-byte custom PostgreSQL dump, verified its checksum and 417-line restore listing, restored it into isolated PostgreSQL, proved 151 baseline migrations and 81 public tables with zero task-artifact tables, then removed all isolated resources
- Pulled only final digest `sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`, proved config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915`, changed only `LITELLM_IMAGE`, and recreated only `litellm` with `--no-deps`
- Verified 161 successful migrations, exact model/fallback/MCP projections, unchanged dependencies and protected state, Chat, Responses, MCP REST, standard MCP, six discovery aliases, nine challenge cases, DCR, authorized initialize, and cross-audience rejection
- Stopped before soak completion when the authorized real-tool call timed out and health failed, then restored only the exact prior selector and recreated only `litellm` with `--no-deps`
- Verified the rollback digest, source, health, readiness/liveliness, zero restarts/OOM, 161-migration compatibility, exact inventory/fallback/MCP/dependency/protected state, Responses, MCP REST, standard MCP, LazyMCP list/status/describe, and authorized `defend_memory-find`

## Acceptance Criteria Coverage

- **AC-1: PASS.** Independent authorization, exact signed source/candidate, attestations, and security qualification were fresh and exact before mutation
- **AC-2: PASS.** Fork `main` was already synchronized, the authorization closure was pushed without force, and remote source ancestry/content were verified before deployment
- **AC-3: PASS.** Exact release and rollback identities were proven; the owner-only custom dump, checksum, list, isolated restore, migration count, schema count, leakage check, and cleanup passed
- **AC-4: FAIL.** Initial candidate identity, migrations, health, inventory, preservation, Chat, Responses, MCP, discovery, challenge, DCR, and audience gates passed, but authorized `defend_memory-find` timed out and the candidate became unhealthy before the required 900-second soak and minute-15 rerun
- **AC-5: PASS.** The exact prior digest was restored immediately, no database restore ran, rollback verification passed, and NAS remained untouched
- **AC-6: PASS FOR FAILED OUTCOME.** Secret-free evidence, task state, documentation impact, registry updates, validation, commit, push, and durable memory record the rejected release and verified rollback

## Exact Runtime Outcome

```text
candidate selector: docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
candidate config: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
candidate source: bf58974a935521fa570fa7e280c51a00b2e5b54e
candidate result: REJECTED
failure gate: authorized defend_memory-find timed out; candidate health became unhealthy
soak: not started because an earlier mandatory gate failed
rollback selector: docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
rollback config: sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42
rollback source: 64a3b83bf0bdd8813890d20ba7b6b57fc034bb95
rollback result: PASS
production DB restore: not performed
NAS mutation: none
```

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. The failed runtime result changes no steady-state behavior; this task and evidence packet are the operational source of truth

## Open Risks

- The candidate entered an unhealthy state under the production MCP/real-tool gate after earlier protocol and model checks passed
- Candidate logs include recurring unrelated live-traffic model errors as well as expected negative-auth errors, so a focused investigation must isolate the health and real-tool timeout root cause before any reauthorization
- Production now has the 161-migration schema. The exact prior image passed isolated qualification and live rollback verification against that state
- The protected database dump remains host-local rollback material and was not copied into repository evidence

## Recommended Next Step

PMA should keep this exact candidate blocked and route a focused Fedora-equivalent investigation of the authorized real-tool timeout and unhealthy transition. Any retry must reopen this task, create a new fresh protected backup/restore unit, and obtain a new Tech Lead authorization. Keep NAS and mutable tags untouched

## Signed Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT FEDORA RELEASE; VERIFIED ROLLBACK PASS. Exact signed candidate `docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3` deployed only after the fresh owner-only database dump/checksum/list and isolated restore passed. Identity, 161 migrations, health, inventory, preservation, Chat, Responses, MCP REST, standard MCP, all six discovery aliases, exact challenges, DCR, authorized initialize, and audience rejection passed initially. The mandatory authorized `defend_memory-find` call timed out and the candidate became unhealthy before soak, so I immediately restored exact prior digest `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`. Rollback now passes exact identity, health, readiness/liveliness, zero restart/OOM, 161-schema compatibility, inventory/fallback/MCP/dependencies/protected state, Responses, MCP REST, standard MCP, LazyMCP list/status/describe, and authorized `defend_memory-find`. No database restore, mutable-tag move, or NAS action occurred. Keep this candidate blocked pending focused investigation and fresh reauthorization
