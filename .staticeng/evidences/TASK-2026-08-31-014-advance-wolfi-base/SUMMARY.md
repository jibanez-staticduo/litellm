# TASK-014 Implementation Evidence

## Summary

Exactly both root `Dockerfile` Wolfi defaults now use approved OCI index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`. No other TASK-014 source mutation was made. Native amd64 ABI/package checks pass, OCI provenance and the replacement eight-path freeze are recorded, and unavailable security gates are explicitly not cleared

## Acceptance Criteria Coverage

- **AC-1: PASS.** Implementation follows the exact Tech Lead approval and independently re-resolves the approved index/platform identities
- **AC-2: PASS.** Pre/post fingerprints and the reconstructed zero-context semantic diff prove exactly two substitutions; post-edit Dockerfile SHA-256 is `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`
- **AC-3: PASS FOR AUTHORIZED AMD64 PREFLIGHT.** Native amd64 proves glibc/locale/loader `2.44-r1`, all four Python packages `3.13.15-r4`, Python 3.13.15, x86_64, `cpython-313`, SOABI `cpython-313-x86_64-linux-gnu`, `import math`, and `GLIBC_2.44`; arm64 remains metadata-only and unauthorized
- **AC-4: PASS.** Frozen Python/Rust metadata and locks, Cargo, seven candidate paths, uv/Rust/UI identities, and application-only patch remain unchanged; TASK-006, deployment, production, commit, and push were not performed
- **AC-5: READY FOR TECH LEAD REVIEW.** Ordered manifest SHA-256 is `f7def12e07e90dbfe2a27651eab73617660191efeab7b97e7d200fc01ebd5e13`; combined tracked patch SHA-256 is `501797e94d980f1ed7f1293d4fe57adea61237f9107f0f0025a5a00d6bbd2751`

## Verification

- `.staticeng/evidences/TASK-2026-08-31-014-advance-wolfi-base/logs/01-exact-edit-and-static-checks.log`: exact edit, rollback fingerprint, and static preservation
- `.staticeng/evidences/TASK-2026-08-31-014-advance-wolfi-base/logs/02-oci-provenance.log`: replacement/rollback OCI provenance and native amd64 image identity
- `.staticeng/evidences/TASK-2026-08-31-014-advance-wolfi-base/logs/03-amd64-abi-apk.log`: ABI, package closure, APK artifacts/keys, and embedded Python SPDX fingerprints
- `.staticeng/evidences/TASK-2026-08-31-014-advance-wolfi-base/logs/04-eight-path-freeze-and-patches.log`: replacement manifest, patches, locks, and OCI identity freeze
- `.staticeng/evidences/TASK-2026-08-31-014-advance-wolfi-base/logs/05-sbom-scan-signature-availability.log`: available SBOM evidence and unavailable promotion gates
- `.staticeng/evidences/TASK-2026-08-31-014-advance-wolfi-base/logs/06-tech-lead-independent-review.log`: independent exact edit, freeze, OCI, ABI, and security-gate disposition

## Documentation Impact

No product, architecture, operator, or CodeMap documentation change is required. This bounded foundation pin changes no public behavior or navigable source structure

## Open Risks

Cosign verification, aggregate SBOM generation, and comparative CVE scanning are unavailable. The rolling APK repository is not an immutable package snapshot. TASK-006's builder/final manifests, parity, full build, runtime imports, entrypoint, and smoke gates remain unexecuted and unauthorized here. Arm64 and promotion remain unauthorized

Repository `staticeng_validate` also remains blocked by the known pre-existing missing-CodeMap inventory; this task adds no navigable source and no unrelated CodeMap repair was applied

## Recommended Next Step

Tech Lead review passes TASK-014 and authorizes TASK-006 Reopen 4 for isolated amd64 construction and smoke using the exact frozen inputs recorded in the task. Signature, aggregate SBOM, and vulnerability policy remain mandatory promotion gates
