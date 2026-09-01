---
id: TASK-2026-09-01-001-qualify-lazymcp-oauth-release
complexity: complex
track: implementation
slice: qa
status: active
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: null
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 0
---

# Task: Qualify LazyMCP OAuth release

## Objective

Clear every retained promotion gate for exact amd64 candidate `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e` before any host deployment.

## Acceptance Criteria

- [ ] AC-1: Download checksum-pinned Syft, Grype, and Cosign into an owner-only temporary directory and record verified versions/checksums without installing system-wide.
- [ ] AC-2: Produce exact-image Syft, SPDX, and CycloneDX SBOMs and immutable checksums for final candidate and required comparative subjects.
- [ ] AC-3: Update one Grype database, freeze its identity, and scan old base, new base, exact R6 builder, and exact final candidate using that same database.
- [ ] AC-4: Independently disposition all Critical/High findings; reject any Critical, fixable High, or new High without a documented time-bounded exception.
- [ ] AC-5: Verify Wolfi signature/attestations and uv provenance; document Rust/UI publisher-signature availability and any required explicit exception.
- [ ] AC-6: Publish the exact local image to a unique immutable private-registry candidate tag, prove registry manifest config digest equals the local image ID, and produce a signable digest reference.
- [ ] AC-7: Sign/attest and verify the exact registry digest using an existing approved keyless/KMS policy; if no approved signing identity is available, block without inventing one.
- [ ] AC-8: Execute one real authorized registered MCP tool through the candidate against an isolated clone or approved Fedora preflight environment without logging credentials or payload content.
- [ ] AC-9: Preserve production and deployment state; create a complete secret-free Evidence Packet and signed pass/reject handoff.

# Post Implementation Task Updates

## QA Engineer: Post Implementation Expectations

Qualification verdict: **REJECT FOR PROMOTION AND DEPLOYMENT**

- AC-1 passed
- AC-2 and AC-3 are partial because the exact R6 builder was not retained; all available subjects and the exact final candidate have aggregate SBOM/scan evidence
- AC-4 failed because exact final `restrictedpython 8.1` has fixable High `GHSA-ffg3-p8fm-mjx2`, fixed in 8.3, with no approved exception
- AC-5 is partial: Wolfi signature and attestations pass; uv/Rust/UI publisher identity verification is incomplete and has no approved exception
- AC-6 passed with immutable candidate digest `sha256:9f642cc38083d1600e62cfb473799a7d52ba89f6c8ff0c4a00940cddc386e619`; registry config equals local image ID
- AC-7 is blocked because no approved keyless/KMS identity was available; no identity was invented
- AC-8 is blocked for the candidate. One real registered tool passed through the existing LazyMCP gateway, but no isolated candidate-bound DB/config clone was available and deployment was prohibited
- AC-9 passed for preservation/evidence and rejects release overall. Production remained healthy and unchanged; no deployment, restart, production mutation, commit, or Git push occurred

Evidence: `.staticeng/evidences/TASK-2026-09-01-001-qualify-lazymcp-oauth-release/SUMMARY.md`

[Agent Message] From: qa_engineer To: product_manager

REJECT. The exact published candidate has a fixable High and cannot satisfy promotion policy. Exact R6 builder, approved signing identity, and candidate-bound real-tool evidence are also blocked. Do not promote or deploy

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-09-01-001-qualify-lazymcp-oauth-release/` with `SUMMARY.md` and owner-only logs/artifacts. Never store registry auth, keys, tokens, cookies, request/response content, DB URLs, or environment dumps.

## Handoff

[Agent Message] From: product_manager To: qa_engineer

Execute promotion gates only; do not deploy/restart/replace Fedora or NAS. Use checksum-pinned standalone tools described in the tool-specialist handoff. The exact candidate is local image ID `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`; fail on identity drift. Reconstruct/retain the exact R6 builder only from frozen TASK-005/TASK-006 inputs if required. Publish only a unique immutable candidate tag, never `latest` or `stable`. Use existing approved registry/signing identities only and never expose credentials. For the real tool gate, prefer an isolated DB/config clone; if impossible, define a tightly bounded Fedora canary gate for Tech Lead rather than touching production under this task. Return the shared output contract with explicit pass/reject per AC.
