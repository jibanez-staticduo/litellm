---
id: TASK-2026-09-01-005-review-release-qualification
complexity: standard
track: investigation
slice: qa
status: active
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-09-01-001-qualify-lazymcp-oauth-release
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: Review LazyMCP release qualification

## Objective

Independently disposition failed promotion gates and explicitly authorize or reject Fedora/NAS deployment.

## Acceptance Criteria

- [ ] AC-1: Verify candidate/registry identity and qualification evidence integrity.
- [ ] AC-2: Independently disposition the fixable High finding and missing builder/signing/provenance/candidate-bound real-tool gates.
- [ ] AC-3: Confirm production preservation and whether any deployment is authorized.
- [ ] AC-4: Return findings first with exact remediation requirements and signed verdict.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Read TASK-001 qualification and TASK-002 release design. Independently review the fixed High vulnerability, incomplete exact-builder comparison, publisher/signing evidence, and candidate-bound real-tool block. Do not mutate source, registry tags, hosts, DB, containers, or deployments. Explicitly approve or reject Fedora/NAS deployment and update this task with signed findings.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

### Findings

1. **BLOCKER: the exact final candidate violates the mandatory vulnerability policy.** Frozen Grype DB v6.1.9 reports one fixable High, `GHSA-ffg3-p8fm-mjx2`, in `restrictedpython 8.1`, fixed in 8.3. No approved time-bounded exception exists. This independently requires rejection of manifest `sha256:9f642cc38083d1600e62cfb473799a7d52ba89f6c8ff0c4a00940cddc386e619`
2. **BLOCKER: candidate authenticity is not established.** The published registry digest has no approved signature or attestation because no approved keyless/KMS identity was available. Wolfi verification does not authenticate the assembled LiteLLM candidate
3. **BLOCKER: the mandatory candidate-bound real-tool gate did not run.** The successful real registered tool call used the existing gateway, not the candidate. It therefore proves neither the candidate's registered catalog path nor its encryption, authorization, audience, and upstream execution behavior
4. **BLOCKER: exact build-subject qualification is incomplete.** The exact R6 builder was not retained. R4 builder SBOM/scan results cannot substitute for R6, and reconstructing from rolling APK inputs would not prove identity with the builder that emitted the retained final image
5. **BLOCKER: publisher provenance policy is unresolved.** uv has digest and attestation-manifest metadata but no verified signing identity; Rust and UI bases are digest-pinned Official Images without verified Cosign publisher signatures. No explicit approved exception defines acceptable alternate provenance
6. **HIGH: the repository evidence packet is not independently durable enough for release approval.** Full SBOMs and scans remain only under `/tmp/opencode`; repository evidence contains summaries and selected checksums, but no complete sanitized artifact checksum manifest or retained machine-readable scan outputs. The recorded identities are internally consistent, but the scan and provenance conclusions cannot be fully reproduced from the packet alone
7. **MEDIUM: production preservation evidence is split across packets.** Qualification directly records one unchanged production container, while the release-design read-only baseline records both Fedora and NAS healthy. This is sufficient to find no evidence of mutation, but neither host is authorized to deploy until fresh dual-host preflight is captured under the deployment tasks

### Release Design Disposition

The Fedora-first/NAS-second design is directionally acceptable and fail-closed: digest-only selection, exact config identity, fresh host-local rollback units, Fedora soak before NAS, host-specific preservation, and split-release rollback are appropriate. It correctly requires qualification PASS and Tech Lead authorization before any pull or selector mutation. Its execution sections remain dormant because those prerequisites are not met

### Deployment Verdict

**REJECT / UNAUTHORIZED.** Do not deploy, pull for deployment, promote, retag, sign retroactively as a substitute for rebuild qualification, restart, or change selectors on Fedora or NAS. TASK-003 and TASK-004 must remain blocked. The unique candidate tag may remain quarantined for forensic reference, but manifest `sha256:9f642cc38083d1600e62cfb473799a7d52ba89f6c8ff0c4a00940cddc386e619` is permanently rejected under the current no-fixable-High policy

### Exact Remediation Path

1. Open a governed implementation task to update `restrictedpython` to 8.3 or a later policy-approved fixed version, update locks as required, and run mapped unit, integration, lint, and type checks
2. Freeze new source, dependency, base, toolchain, and package identities; build a new amd64 candidate and retain/tag the exact builder emitted by that build. Do not reuse the rejected final manifest or infer an R6 builder retrospectively
3. Generate and retain owner-only machine-readable Syft, SPDX, CycloneDX, and Grype outputs for old base, new base, exact retained builder, and exact new final candidate. Add a secret-free SHA-256 manifest to repository evidence
4. Scan all four subjects with one newly frozen Grype DB. Independently reject every Critical, fixable High, and new High unless PMA supplies a Product Owner-approved, time-bounded SCR exception before qualification
5. Have the security/product authority define an approved keyless or KMS signing identity and explicit acceptance policy for uv, Rust, and UI publisher provenance. Record approved alternate-provenance exceptions where signatures are unavailable
6. Publish only the new exact candidate to a new unique tag, prove registry manifest config digest equals its local image ID, sign and attest that exact digest, then verify signatures and attestations against the approved identity policy
7. Build an isolated candidate-bound clone of the required catalog/database/encryption/config authorization state, or separately authorize a tightly bounded Fedora preflight canary. Execute discovery, exact audience authorization, initialize, and one real registered tool through the new candidate without retaining secrets or payloads
8. Repeat TASK-001 qualification from AC-1 through AC-9 against only the new identities. Any source, lock, base, builder, final image, scan DB, signing policy, or harness change invalidates prior qualification evidence
9. Return the complete packet for independent Tech Lead review. Only a signed PASS may activate TASK-003; TASK-004 remains blocked until Fedora completes every gate and the full 15-minute observation in TASK-002

### Acceptance Criteria Coverage

- **AC-1: PASS WITH EVIDENCE LIMITATION.** Candidate config, unique tag, registry manifest, and registry config identities agree. Evidence summaries are internally consistent, but full machine-readable artifacts are temporary rather than durably packetized
- **AC-2: PASS.** The fixable High, missing exact builder, incomplete publisher policy, unsigned/unattested digest, and non-candidate real-tool execution are independently dispositioned as release blockers
- **AC-3: PASS.** No reviewed evidence shows production mutation; Fedora and NAS deployment are explicitly rejected and unauthorized
- **AC-4: PASS.** Findings, exact remediation, and signed verdict are recorded here and in `.staticeng/evidences/TASK-2026-09-01-005-review-release-qualification/SUMMARY.md`

### Documentation Impact

No product, architecture, source, registry, or CodeMap change is required. The existing SCR and architecture contract already require staged immutable promotion and candidate-bound real-tool verification. This update records an operational release rejection only

[Agent Message] From: tech_lead To: product_manager

REJECT / UNAUTHORIZED. Do not deploy the rejected digest to Fedora or NAS. A fixable High, absent exact builder, unsigned candidate, unresolved publisher provenance, non-durable full artifacts, and missing candidate-bound real-tool proof block release. Execute the nine-step remediation path in this task, then return a wholly new candidate for independent qualification
