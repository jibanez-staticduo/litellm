# TASK-2026-09-01-011 Reopen 3 Evidence Summary

## Summary

REJECT. Exact clean commit `165a94ecfbf21d7ff4626815ac6b298ac34e2adb` now emits and retains exact `linux/amd64` builder `sha256:e0c530bb94b6fb9fde38d1d32d2662177ebef280cdcb4bc7b3c8e68e4d71e104` and final `sha256:00b239d81b428a143d50a695c59839e0c387df0f66da116d80e5b79c8c524889`. The isolated synthetic PostgreSQL/config/model/MCP stack passed behavioral gates, including a candidate-bound registered real synthetic tool. Promotion remains fail-closed because the exact builder has six fixable High scan matches and no approved exact builder/final signature or attestation exists

All disposable containers, network, volume, task builder/cache, worktree, downloaded tooling, vulnerability database and temporary artifacts were destroyed. The exact immutable images and durable repository evidence were retained as authorized. Production identity and health remained byte-for-byte unchanged under only the two credential-safe allowlisted observations

## Work Performed

- Built the exact detached clean source twice as explicit builder/final targets and verified source/ancestry, labels, amd64 architecture, Python 3.13.15, glibc 2.44, Rust 1.97.1, native imports, Prisma and normal entrypoint
- Started an isolated labelled stack with empty PostgreSQL, test-owned config, one authenticated synthetic OpenAI-compatible upstream and one FastMCP upstream; used no production data, config, network, mounts or credentials
- Passed empty-DB migrations, idempotent restart, readiness/liveness, exact model inventory, Chat Completions and Responses non-stream/stream/usage/logging, upstream-auth isolation, MCP REST and permissions
- Passed all six LazyMCP discovery aliases, exact aggregate/scoped/toolset challenges, DCR code/access/refresh/replay and cross-audience isolation, three initialize/list shapes, aggregate/toolset real upstream tool calls, and 360/360 reconnect discovery probes
- Generated and retained exact builder/final SPDX and CycloneDX SBOMs plus same-frozen-Grype-DB machine-readable scans under `artifacts/`; verified Wolfi provenance, and documented unavailable/unverified external and candidate signing dispositions
- Destroyed every disposable object and cache; retained only immutable images/evidence; proved production unchanged and ran StaticEng validation

## Acceptance Criteria Coverage

- **AC-1: PASS.** Exact clean source and ancestry are recorded; exact amd64 builder/final images are retained by immutable image ID and full revision label
- **AC-2: PASS.** Isolated PostgreSQL, config, synthetic provider and registered FastMCP state exercised model, Responses, MCP, six discovery aliases, challenges, DCR/audience/replay, initialize and authorized real synthetic tool behavior
- **AC-3: PASS.** Health, 161 migrations plus idempotent restart, permissions, upstream credential separation, exact inventory, successful spend rows, clean logs, reconnect and preservation gates passed
- **AC-4: FAIL.** Durable exact builder/final SBOM and same-database scans exist, and final has zero High/Critical, but builder has six fixable High matches. Exact builder/final signature/attestation is also absent because no approved signing identity exists and publication is unauthorized
- **AC-5: PASS FOR SAFETY AND EVIDENCE.** Evidence is synthetic and secret-free; cleanup is complete; no mutable tag, publication, push, deployment, Fedora action or NAS production mutation occurred; production stayed unchanged

## Documentation Impact

Product, architecture, technical and CodeMap documentation are not changed because qualification changed no product behavior or source structure. This task/evidence update records the operational outcome

## Open Risks

- Exact builder contains six fixable High matches in setuptools, quinn-proto and rustls-webpki, violating the governing zero-fixable-High release policy
- Exact builder/final images are local immutable Docker identities, not registry digests, and have no approved signature or attestation
- uv has OCI provenance but no Cosign signature; Rust and Node official images expose no Cosign signatures under the tested policy
- Promotion and TASK-012 deployment remain prohibited despite complete functional qualification

## Recommended Next Step

PMA should reject promotion and route a governed build-stage dependency remediation for the six fixable High findings. Establish an approved signing identity and candidate publication/attestation procedure, produce a new exact commit and builder/final subjects, then rerun TASK-011 supply-chain and affected runtime gates from the beginning

## Signed Handoff

[Agent Message] From: qa_engineer To: product_manager

REJECT. Exact amd64 builder `sha256:e0c530bb94b6fb9fde38d1d32d2662177ebef280cdcb4bc7b3c8e68e4d71e104` and final `sha256:00b239d81b428a143d50a695c59839e0c387df0f66da116d80e5b79c8c524889` pass every isolated functional gate, but the builder has six fixable High findings and exact signing/attestation is absent. Cleanup is complete and production is unchanged. Do not promote or deploy
