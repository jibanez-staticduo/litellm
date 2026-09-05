---
id: TASK-2026-09-03-004-sign-attest-release-images
complexity: complex
track: implementation
slice: qa
status: superseded
superseded_by: TASK-2026-09-05-003-close-dual-host-repair
supersession_note: Historical signatures and attestations cover their earlier digests; final-image refresh remains deferred.
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

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- AC-1: PASS. No approved existing StaticDuo signer was available. Created PMA-approved dedicated signer `staticduo-litellm-release-self-managed-v1`; encrypted private key/password are separate owner-only files outside repository/Syncthing, while public verification material and fingerprints are retained
- AC-2: PASS. Published exact builder/final only under unique quarantine tags without moving a mutable release tag
- AC-3: PASS. Registry builder manifest `sha256:8ff106da74054123f9e5fb742e8c008656b11f46148e40d742fde9332d101daa` resolves to qualified config `sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac`; final manifest `sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3` resolves to qualified config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915`
- AC-4: PASS. Both exact digest references have signatures plus SPDX, CycloneDX, and SLSA provenance v1 attestations bound to exact source `bf58974a935521fa570fa7e280c51a00b2e5b54e` and qualification evidence checksums
- AC-5: PASS. Fresh verification proved cryptography, transparency-log inclusion, exact predicate types/content, sole manifest subjects, source revision, image/config identities, and four persisted OCI referrers per digest
- AC-6: PASS. No private/password material is tracked or logged, no failed registry identity remains, and no mutable tag, deployment, Fedora, or NAS mutation occurred
- Product, architecture, technical, and CodeMap documentation are not required because no product behavior or maintained source/tooling structure changed
- Evidence: `.staticeng/evidences/TASK-2026-09-03-004-sign-attest-release-images/SUMMARY.md`

[Agent Message] From: tech_lead To: product_manager

PASS. Exact qualified builder `docker.staticduo.com/litellm@sha256:8ff106da74054123f9e5fb742e8c008656b11f46148e40d742fde9332d101daa` and final `docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3` are published under unique quarantine tags, proven to contain the exact qualified configs, signed with the approved StaticDuo trust root, and freshly verified with SPDX, CycloneDX, and SLSA provenance v1 attestations bound to source `bf58974a935521fa570fa7e280c51a00b2e5b54e`. No secret, mutable tag, deployment, Fedora, or NAS mutation occurred
