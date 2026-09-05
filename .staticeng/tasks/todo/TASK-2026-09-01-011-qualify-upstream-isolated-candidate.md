---
id: TASK-2026-09-01-011-qualify-upstream-isolated-candidate
complexity: complex
track: implementation
slice: qa
status: superseded
superseded_by: TASK-2026-09-05-003-close-dual-host-repair
supersession_note: All reopen results retained; Reopen 6 qualification applies only to its exact earlier subjects.
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-010-integrate-upstream-main
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 6
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

TASK-2026-09-02-002 passed independent Tech Lead review and restores both coherent glibc 2.44 Wolfi defaults. PMA activates qualification against exact pushed fork-main commit `165a94ecfbf21d7ff4626815ac6b298ac34e2adb`. Rebuild from a clean detached worktree and rerun every behavioral and supply-chain gate from the beginning. Prior Reopen 2 rejection remains historical evidence and does not qualify the corrected source. Publication, promotion, deployment, Fedora/NAS mutation, and arm64 remain unauthorized

### Reopen 3 Result

REJECT. Exact clean commit `165a94ecfbf21d7ff4626815ac6b298ac34e2adb` emitted retained amd64 builder `sha256:e0c530bb94b6fb9fde38d1d32d2662177ebef280cdcb4bc7b3c8e68e4d71e104` and final `sha256:00b239d81b428a143d50a695c59839e0c387df0f66da116d80e5b79c8c524889`. A uniquely labelled isolated PostgreSQL/config/provider/FastMCP stack passed all required functional gates, including exact six-alias discovery, aggregate/scoped/toolset challenges, DCR access/refresh/replay isolation, reconnect, permissions, upstream-auth separation and candidate-bound registered real synthetic tool execution

Durable exact builder/final SPDX and CycloneDX SBOMs plus same-frozen-Grype-DB scans were retained. The final has zero High/Critical, but the builder has six fixable High matches in setuptools, quinn-proto and rustls-webpki. No approved signing identity was available, so exact builder/final signatures and attestations are absent. All disposable containers, network, volume, task builder/cache, worktree, tools, vulnerability DB and temporary artifacts were destroyed; only immutable images/evidence remain. Production stayed unchanged under only the allowlisted observations

# Post Implementation Task Updates

## QA Engineer: Post Implementation Expectations

- AC-1: PASS because exact clean source emitted retained immutable amd64 builder and final identities bound to the full source revision
- AC-2: PASS because the isolated synthetic stack exercised the full model, Responses, MCP and LazyMCP protocol contract, including candidate-bound real tool execution
- AC-3: PASS because health, migrations, restart, permissions, upstream auth, inventory, logs, reconnect and preservation gates passed
- AC-4: FAIL because the exact builder has six fixable High findings and exact builder/final signing and attestation remain absent
- AC-5: PASS because production remained unchanged under only allowlisted observations, all disposable resources and caches were destroyed, evidence is secret-free, and no push/publication/deployment/Fedora/NAS mutation occurred
- Product documentation is not required because no product behavior or source structure changed
- Evidence: `.staticeng/evidences/TASK-2026-09-01-011-qualify-upstream-isolated-candidate/SUMMARY.md`

[Agent Message] From: qa_engineer To: product_manager

REJECT. Exact amd64 builder `sha256:e0c530bb94b6fb9fde38d1d32d2662177ebef280cdcb4bc7b3c8e68e4d71e104` and final `sha256:00b239d81b428a143d50a695c59839e0c387df0f66da116d80e5b79c8c524889` pass every isolated functional gate, but the builder has six fixable High findings and exact signing/attestation is absent. Cleanup is complete and production is unchanged. Do not promote or deploy

Resume only after TASK-2026-09-02-004 produces a reviewed exact commit and TASK-2026-09-02-003 defines signing policy.

### Reopen 4 - Security-remediated fork main

TASK-2026-09-02-004 passed independent review and is pushed at exact commit `a826c38dc0737afd9eef00a2e9f50d2413ca92eb`. Rebuild wholly new exact builder/final subjects from this clean commit and rerun every functional and supply-chain gate. Publication and signing may use only unique quarantine tags and an explicitly approved signer; absence of a signer must be reported separately from functional/security qualification. Destroy the disposable runtime stack before Fedora authorization.

### Reopen 4 Result

REJECT. Exact clean commit `a826c38dc0737afd9eef00a2e9f50d2413ca92eb` emitted retained amd64 builder `sha256:5b7f6e5ef88d88b0db36473d75ec25b48512dbd4e26fe7484bd7775223aee6f6` and final `sha256:eeb98cc84cd1f3b73ce1dc584ac9922e47515fc3db46beb8825283fddf6b2820`. Exact builder/final/base/uv SPDX and CycloneDX SBOMs plus same-frozen-DB scans pass with zero Critical and zero fixable High, and the prior six builder High matches are removed

The isolated PostgreSQL/config/provider/FastMCP stack passes migrations, restart, health, inventory, Chat, Responses, upstream-auth separation, MCP REST, permissions, registered real synthetic tool, spend and preservation gates. All six required LazyMCP discovery aliases return HTTP 404 from the exact runtime, blocking challenge, DCR audience/access-refresh/replay and aggregate/scoped/toolset LazyMCP gates. No approved candidate signing material is available, so exact signatures/attestations are absent but are not the sole blocker

All disposable runtime/build resources were destroyed, only retained immutable local images and evidence remain, and production stayed unchanged under credential-safe allowlisted observations. No publication, deployment, Fedora action or NAS mutation occurred

### Reopen 5 - Final source and harness commit

TASK-2026-09-02-006 passed independent review and is pushed at exact fork-main commit `3ad43aa9c9eb4c14ed2fedbac734dd0775925dca`. Build wholly new exact builder/final subjects and rerun the complete corrected qualification. Start the runtime with explicit `PROXY_BASE_URL=https://candidate.invalid`; retain negative unset/HTTP fail-closed packaged tests. All disposable runtime/build resources must be destroyed before handoff. Candidate signing remains a separate final gate.

### Reopen 6 - Tornado-remediated final candidate

TASK-2026-09-03-001 passed independent review and is pushed at exact fork-main commit `bf58974a935521fa570fa7e280c51a00b2e5b54e`. Build wholly new exact builder/final subjects and rerun the complete corrected functional and supply-chain matrix. Require zero Critical and zero High in both exact subjects under one current frozen scanner database. Destroy every disposable test container, network, volume, builder, cache, worktree and synthetic credential before Fedora authorization; retain only immutable release images and durable secret-free evidence. Signing/publication remains a separate final release gate.

# Post Implementation Task Updates

## QA Engineer: Reopen 4 Post Implementation Expectations

- AC-1: PASS because wholly new exact clean-source amd64 builder/final identities are retained with full revision labels
- AC-2: FAIL because all six LazyMCP discovery aliases return 404 and dependent challenge/DCR/transport gates cannot run
- AC-3: FAIL because non-LazyMCP operational gates pass but LazyMCP reconnect and preservation remain blocked by missing discovery
- AC-4: FAIL because exact SBOM/scan/provenance gates pass with zero Critical/fixable High, but no approved signer exists and candidate signatures/attestations are absent
- AC-5: PASS because evidence is secret-free, cleanup is complete, production is unchanged and no publication/deployment/Fedora/NAS mutation occurred
- Product documentation and CodeMap changes are not required because QA changed no product behavior or source structure
- Evidence: `.staticeng/evidences/TASK-2026-09-01-011-qualify-upstream-isolated-candidate/SUMMARY.md`

[Agent Message] From: qa_engineer To: product_manager

REJECT. Exact Reopen 4 builder/final security qualification passes with zero Critical and zero fixable High, but all six required LazyMCP discovery aliases return 404. Approved signing material is also absent, so signing is not the sole blocker. Cleanup is complete and production is unchanged. Do not promote or deploy

### Reopen 5 Pending - Corrected Trusted-Public-Base Harness

TASK-2026-09-02-005 proved the Reopen 4 image has all six registered routes and no routing defect. The prior harness omitted the trusted public origin required for a non-loopback Docker peer, so its 404 responses were the intended fail-closed result. Reuse unchanged retained final image `sha256:eeb98cc84cd1f3b73ce1dc584ac9922e47515fc3db46beb8825283fddf6b2820` first, with no rebuild, and add only `PROXY_BASE_URL=https://candidate.invalid` to the existing secret-free candidate environment. Internal HTTP transport remains unchanged

Before the positive run, prove the same immutable image returns generic HTTP 404 `{"detail":"Not Found"}` for all six aliases both with `PROXY_BASE_URL` unset and with `PROXY_BASE_URL=http://candidate.invalid` from a non-loopback peer. For the corrected positive run, require HTTP 200 and exact metadata for all six aliases: aggregate resources use `https://candidate.invalid/lazymcp`, scoped resources use `https://candidate.invalid/lazymcp/team-a`, toolset resources use `https://candidate.invalid/toolset/tools-a/lazymcp`, and every document uses `authorization_servers: ["https://candidate.invalid/mcp"]`. Require OpenAPI to contain all six templates without treating schema presence as runtime success

Rerun the complete prior functional contract against the corrected positive instance, including exact aggregate/scoped/toolset challenges, DCR code/access/refresh/replay and audience isolation, LazyMCP initialize/list/call, registered real synthetic tool behavior, reconnect with zero discovery 404s, readiness, `/mcp`, MCP REST, permissions, model/Responses behavior, logs, restart and preservation. Evidence must record the exact image ID before and after, the complete environment-name allowlist with values redacted except the reserved public base, request/response status and exact public metadata/challenges, production allowlisted pre/post invariants, and zero remaining task-labelled containers/networks/volumes. Do not read production configuration or credentials. Signing/attestation remains a separate blocker. No publication, deployment, Fedora action or NAS mutation is authorized

### Reopen 5 Result

REJECT. Exact clean commit `3ad43aa9c9eb4c14ed2fedbac734dd0775925dca` emitted retained amd64 builder `sha256:04bba4403ac7de87108c539e5e14982e55e3cecbf39b36a6794025cee23de5ad` and final `sha256:836d98e7ace653505888d47826ca47e8075a0e64d559c9c61dce5e6298103f0f`. The complete credential-safe isolated functional matrix passes, including packaged unset/HTTP fail-closed cases and positive HTTPS discovery, exact challenges, DCR audience/access-refresh/replay, aggregate/scoped/toolset initialize/list/call, real registered FastMCP tool, reconnect, migrations, restart, health, models, Chat, Responses, MCP REST, permissions, upstream auth, logs, spend and preservation

Exact builder/final SPDX and CycloneDX SBOMs were generated and scanned against one current frozen Grype 0.118.0 database. Both scans report zero Critical but one fixable High: Tornado 6.5.7 `GHSA-mpf4-983q-p7j4`, fixed in 6.5.8. Signing remains separately absent because no approved signer or publication was authorized. Every disposable runtime/build object, cache, tool and worktree was destroyed; only immutable builder/final images remain. Production stayed unchanged under credential-safe allowlisted observations. Do not promote or deploy

## QA Engineer: Reopen 5 Post Implementation Expectations

- AC-1: PASS because exact clean source emitted new retained amd64 builder/final identities with full revision labels
- AC-2: PASS because isolated model, Responses, MCP and full LazyMCP protocol/real-tool gates pass
- AC-3: PASS because migrations, health, restart, permissions, upstream auth, inventory, logs, reconnect, spend and preservation pass
- AC-4: FAIL because exact builder/final each contain one fixable High Tornado finding; signatures/attestations are separately absent
- AC-5: PASS because evidence is secret-free, cleanup is complete, production is unchanged and no publication/signing/deployment/Fedora/NAS mutation occurred
- Product documentation and CodeMap changes are not required because QA changed no product behavior or source structure
- Evidence: `.staticeng/evidences/TASK-2026-09-01-011-qualify-upstream-isolated-candidate/SUMMARY.md`

[Agent Message] From: qa_engineer To: product_manager

REJECT. Exact Reopen 5 builder `sha256:04bba4403ac7de87108c539e5e14982e55e3cecbf39b36a6794025cee23de5ad` and final `sha256:836d98e7ace653505888d47826ca47e8075a0e64d559c9c61dce5e6298103f0f` pass the full isolated functional matrix, but both contain fixable High `GHSA-mpf4-983q-p7j4` in Tornado 6.5.7. Signing is separately absent. Cleanup is complete and production is unchanged. Do not promote or deploy

### Reopen 6 Result

PASS. Exact clean commit `bf58974a935521fa570fa7e280c51a00b2e5b54e` emitted retained amd64 builder `sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac` and final `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915`. The complete credential-safe isolated functional matrix and negative trust cases pass. Exact base/uv/builder/final SPDX and CycloneDX SBOMs plus one frozen Grype 0.118.0 database scan set show zero Critical and zero High in both retained release subjects

All disposable runtime/build resources, scanner tools/database, worktree and synthetic credentials were destroyed. Only exact immutable builder/final images and durable secret-free evidence remain. Production stayed unchanged under credential-safe allowlisted observations. Signing, publication, deployment, Fedora and NAS remained untouched as required

## QA Engineer: Reopen 6 Post Implementation Expectations

- AC-1: PASS because exact clean source emitted new retained amd64 builder/final identities with full revision labels
- AC-2: PASS because isolated model, Responses, MCP and LazyMCP alias/challenge/DCR/audience/transport/registered-tool gates pass
- AC-3: PASS because migrations, health, restart, permissions, upstream auth, inventory, logs, reconnect, spend and preservation pass
- AC-4: PASS for the authorized Reopen 6 scope because exact base/uv/builder/final SBOMs, frozen-database scans, labels and input provenance pass with zero Critical and zero High in builder/final; signing and publication were explicitly excluded
- AC-5: PASS because evidence is secret-free, cleanup is complete, production is unchanged and no signing/publication/deployment/Fedora/NAS mutation occurred
- Product documentation and CodeMap changes are not required because QA changed no product behavior or source structure
- Evidence: `.staticeng/evidences/TASK-2026-09-01-011-qualify-upstream-isolated-candidate/SUMMARY.md`

[Agent Message] From: qa_engineer To: product_manager

PASS. Exact Reopen 6 amd64 builder `sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac` and final `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` pass the credential-safe isolated functional matrix and have zero Critical and zero High under one frozen Grype database. Cleanup is complete, production is unchanged, and no signing, publication or deployment occurred
