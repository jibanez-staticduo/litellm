---
id: TASK-2026-09-01-011-qualify-upstream-isolated-candidate
complexity: complex
track: implementation
slice: qa
status: todo
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-010-integrate-upstream-main
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 2
---

# Task: Qualify isolated upstream candidate

## Objective

Build and comprehensively validate a clean immutable Docker candidate in an isolated environment separate from Fedora and NAS, retaining exact builder/final identities and all promotion evidence.

## Acceptance Criteria

- [ ] AC-1: Candidate and exact builder derive from clean reviewed commits and are retained by immutable identity.
- [ ] AC-2: Isolated DB/config/catalog permits real model, Responses, MCP, LazyMCP discovery/challenge/DCR/audience, initialize, and registered-tool tests.
- [ ] AC-3: Health, migrations, permissions, upstream auth, model inventory, logs, reconnect, and preservation gates pass.
- [ ] AC-4: Exact builder/final SBOMs, same-database scans, signatures/attestations/provenance, and independent Critical/High disposition pass.
- [ ] AC-5: No Fedora/NAS mutation occurs; candidate Evidence Packet is complete and secret-free.

## Handoff

[Agent Message] From: product_manager To: qa_engineer

Integration is independently approved at exact merge commit `0573332425de92ad8f17f6eb3196fce0d3ce7f22`. Build from a clean detached worktree at that commit under `/tmp/opencode`; retain exact builder and final identities. Use isolated containers, network, volumes, PostgreSQL, config and a synthetic registered MCP tool so no production DB/credentials/mounts are used. Execute complete health, migration, models, Responses, MCP/LazyMCP discovery/challenge/DCR/audience/isolation/reconnect/real-tool/log/preservation gates. Produce exact builder/final SBOMs and same-database scans; verify provenance/signing policy and reject fixable High/Critical findings. Do not push fork main, publish mutable tags, deploy, or change Fedora/NAS. Return complete Evidence Packet and signed pass/reject.

## Blocker Report

[Agent Message] From: qa_engineer To: product_manager

The active Docker daemon identifies as NAS (`hostname=nas`, Docker root `/volume2/@docker`) and cannot satisfy third-host isolation. No build/runtime mutation occurred. Resume only after PMA supplies a proven runner distinct from Fedora and NAS.

## Reopen History

### Reopen 1 - User-authorized disposable Docker validation

The user explicitly authorizes building and testing in a standalone disposable Docker stack on the current daemon instead of requiring a third physical host, provided it is isolated from the running LiteLLM, uses no production DB/config/credentials, and every disposable container/network/volume/builder/worktree is destroyed before Fedora deployment. Build from exact fork-main commit `9374aae27c93d509a12f167c6bb1f83815ed3db1`, whose parent contains the approved merge. Use unique task labels/names and ports, retain only immutable image/evidence identities, and prove the existing production container remains unchanged before and after cleanup.

### Reopen 2 - Fresh credential-safe validation session

Reopen 1 stopped before mutation after an overbroad production inspection returned secret-bearing environment data to the agent-session boundary. Start in a fresh QA session and never run broad `docker inspect`, inspect `.Config`, read production Compose/env/config, or access production mounts. Production invariants may use only allowlisted `docker ps --no-trunc --filter name=^/litellm$ --format '{{.ID}} {{.Image}} {{.Status}}'` and `docker inspect --format '{{.Id}} {{.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}} {{.RestartCount}} {{.State.OOMKilled}}' litellm`. Continue the exact disposable build/qualification/cleanup contract; do not use or repeat any exposed value.

### Reopen 2 Result

Exact build rejected before candidate creation: Python `3.13.15-r4` requires GLIBC 2.44 while the committed Wolfi base supplies 2.43. All disposable resources were destroyed and production remained unchanged. Resume only after TASK-2026-09-02-002 produces an independently reviewed exact commit.

#### Reopen 1 Result

REJECT. QA stopped during preflight after a broad production-container inspection returned credential-bearing environment values. Values are omitted from task evidence. No detached worktree, builder, image, disposable stack, runtime test, SBOM, scan, signature, attestation, registry publication, deployment, or production mutation followed

[Agent Message] From: qa_engineer To: product_manager

REJECT. Reopen 1 triggered the SCR secret-leakage stop condition before candidate construction. No production object was mutated, but affected credentials should be rotated by an authorized operator before a fresh isolated qualification attempt

### Reopen 2 Result

REJECT. The clean detached exact commit `9374aae27c93d509a12f167c6bb1f83815ed3db1` fails the exact `linux/amd64` builder target at the first frozen sync. Its committed immutable Wolfi base supplies glibc 2.43, while the rolling repository supplies pinned Python `3.13.15-r4`, whose `math` extension requires `GLIBC_2.44`. No exact builder or final image was emitted, so runtime and supply-chain gates stopped fail-closed

A disposable diagnostic build changing only the build-base argument to the previously reviewed glibc 2.44 Wolfi digest completed the builder target, confirming the committed default base is the discriminating input. That image was not treated as a candidate and was destroyed with both task builders, caches, worktrees, and all other disposable resources. Production was observed only through the Reopen 2 allowlisted formats and retained identical identity, image, running/healthy state, restart count, and OOM state

[Agent Message] From: qa_engineer To: product_manager

REJECT. Exact commit `9374aae27c93d509a12f167c6bb1f83815ed3db1` cannot emit its exact builder because Python `3.13.15-r4` requires `GLIBC_2.44` but the committed Wolfi base supplies glibc 2.43. Behavioral and supply-chain gates remain fail-closed. Cleanup is complete, and production identity and health are unchanged

### Reopen 3 Pending - Reviewed Wolfi correction

TASK-2026-09-02-002 passed independent Tech Lead review and restores both coherent glibc 2.44 Wolfi defaults. This task returns to `todo` pending PMA activation against the exact pushed correction commit. Prior Reopen 2 rejection remains historical evidence and does not qualify the corrected source. Publication, promotion, deployment, Fedora/NAS mutation, and arm64 remain unauthorized

# Post Implementation Task Updates

## QA Engineer: Post Implementation Expectations

- AC-1: FAIL because the exact clean source build fails before emitting the mandatory exact builder or final image
- AC-2: UNVERIFIED because the mandatory build gate stopped before an isolated runtime stack could be created
- AC-3: UNVERIFIED because no exact candidate exists for runtime qualification
- AC-4: UNVERIFIED because no exact builder or final image exists for SBOM, scan, signing, attestation, provenance, or vulnerability disposition
- AC-5: PASS for safety and rejection evidence because production remained unchanged and healthy under only allowlisted observations, all disposable resources were destroyed, and evidence is secret-free
- Product documentation is not required because no product behavior or source structure changed
- Evidence: `.staticeng/evidences/TASK-2026-09-01-011-qualify-upstream-isolated-candidate/SUMMARY.md`
