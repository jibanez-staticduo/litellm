---
id: TASK-2026-09-03-004-sign-attest-release-images
complexity: complex
track: implementation
slice: qa
status: active
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-012-release-upstream-main-fedora
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: Sign and attest release images

## Objective

Publish the exact qualified builder/final images under unique quarantine tags and establish a StaticDuo-controlled Cosign trust root, signatures, SPDX/CycloneDX/SLSA attestations, and fresh verification for exact registry digests.

## Acceptance Criteria

- [ ] AC-1: Create or use one PMA-approved StaticDuo signing identity; private material remains owner-only outside repository/evidence and public verification material/fingerprint is retained.
- [ ] AC-2: Publish exact builder/final local image IDs under unique immutable quarantine tags without moving mutable release tags.
- [ ] AC-3: Prove each registry manifest config digest equals the qualified local image ID.
- [ ] AC-4: Sign both exact registry digests and attach SPDX, CycloneDX, and SLSA v1 attestations bound to source and evidence checksums.
- [ ] AC-5: Fresh-process verification validates signatures, predicate types, sole subjects, source revision, image identities, and referrer persistence.
- [ ] AC-6: No secret material is logged/tracked; failed tags/referrers are quarantined; no deployment occurs.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Do not begin until PMA activates after TASK-003 passes. The user authorizes release completion, and PMA approves creation of a dedicated self-managed StaticDuo LiteLLM release key only if no existing approved KMS/key is available. Store private key and password in separate owner-only files outside the repository and Syncthing-shared config; never print them or capture commands with tracing. Retain only the public key, fingerprint, non-secret signer identifier, signatures, attestations, predicate checksums, and verification output. Publish only unique quarantine builder/final tags and operate by exact digest. No mutable tags or deployment.
