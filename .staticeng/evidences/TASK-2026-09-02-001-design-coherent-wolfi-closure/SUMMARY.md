# TASK-2026-09-02-001 Evidence Summary

## Summary

PASS for research. Current fork main `9374aae27c93d509a12f167c6bb1f83815ed3db1` retained the TASK-014 Python, uv, Rust, venv, Prisma, and runtime contracts but upstream integration replaced both reviewed glibc 2.44 Wolfi defaults with index `sha256:a31344ab2cb8618db84f535eec56f76f6178b142cb92cb2e48676cc2dcebea72`. TASK-011 Reopen 2 proves that index's amd64 base cannot execute rolling Python 3.13.15-r4 because its `math` extension needs `GLIBC_2.44`

The smallest coherent correction is exactly two root Dockerfile substitutions restoring reviewed Wolfi index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d` for build and runtime. Required amd64 child is `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd`; arm64 child `sha256:fce2a4534bdae72009371dab1c87d322f255b40daff82b857e98c4a0890b361e` is metadata only. The resulting Dockerfile SHA-256 is `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`, byte-identical to the independently approved TASK-014 file

## Work Performed

- Read TASK-011 Reopen 2 and raw rejection ledger, TASK-013, TASK-014 and independent evidence, successful prior amd64 packaging/runtime evidence, current Dockerfile, upstream merge conflict decision, governing SCR, and task state
- Compared current Dockerfile SHA-256 `e7e669bfd09b5beb9ec27fc1a976bf90232adf7144fda5def7a761e2ddbcad11` with TASK-014 and proved the proposed file is an exact prior-approved reconstruction
- Re-resolved current and replacement Wolfi OCI index/platform identities plus preserved uv, Rust, and UI identities without pulling, building, or changing repository or host state
- Reviewed official Chainguard package-retention and signature/attestation guidance and separated present ABI coherence from immutable APK reproducibility
- Defined exact implementation limits, amd64 tests, manifest refreeze, supply-chain gates, rollback, and arm64 boundary in the task record

## Frozen Identities

| Input | OCI index | Required amd64 child |
| --- | --- | --- |
| Wolfi build/runtime | `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d` | `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd` |
| uv 0.11.7 | `sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a` | `sha256:733b4042187702f832f7fdecb3aff14a61b288c4ca37af188bb5715c1caebaf8` |
| Rust 1.97.1 | `sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3` | `sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b` |
| Node 24.19 UI | `sha256:d32cdf619f63fe0471182d08996dd516c6275bb5fd31ae06e55a570bd9e1ad43` | `sha256:2a49bdf71e9fd965a58c1703fd9ddd205b34e5782b692a72dd1d248abb0beb43` |

The replacement Wolfi amd64 config digest is `sha256:a7b2e90a205a20887d43148b4509171ac7f321cf9812e3bc3154a88e6775d140`. Arm64 OCI identities are recorded in the task and authorize no arm64 execution or release

## Acceptance Criteria Coverage

- **AC-1: PASS.** Current Dockerfile and upstream merge decision were compared against TASK-013/TASK-014 and TASK-011 Reopen 2. The only required correction is both Wolfi defaults
- **AC-2: PASS.** Exact OCI index, amd64 child/config, Python 3.13.15-r4 ABI, Rust/uv/UI identities, and prior full amd64 compatibility evidence are frozen
- **AC-3: PASS.** The task defines the exact two-line correction, no-change boundary, full tests, current-source manifest refreeze, immutable-APK follow-up, rollback, and arm64 restriction
- **AC-4: PASS.** Only task/evidence records changed. No source, Dockerfile, lock, test, image, container, builder, registry, host, production, deployment, commit, push, or CodeMap mutation occurred

## Mutable APK Disposition

The base correction establishes coherent glibc/Python ABI for the current transaction but does not freeze unversioned direct or transitive APKs. Chainguard documents bounded retention for non-latest public packages and recommends internal mirroring when versions are pinned. TASK-002 must retain exact signed index bytes, resolved APK artifacts and hashes, package manifests, and builder/final SBOM evidence. Promotion remains blocked if that exact closure cannot be independently verified

A durable reproducible build contract requires a separate approved architecture task for immutable mirrored APK closure or digest-pinned build/runtime foundation images. It must include ownership, refresh and CVE policy, per-platform closure, signatures, attestations, SBOMs, retention, and rollback

## Documentation Impact

No product, public interface, steady-state application architecture, or CodeMap update is required. A future maintained APK snapshot or foundation-image mechanism requires separate architecture documentation

## Open Risks

- Current source has not yet built with the correction; prior TASK-014/TASK-006 success cannot qualify the new exact commit
- Public APK indexes and unversioned package closure remain mutable and retention-bound
- Arm64 remains metadata-only and unauthorized pending native build/runtime/security validation
- Signature/attestation, aggregate SBOM, same-database scans, Critical/High disposition, and real isolated integration gates remain mandatory promotion blockers

## Recommended Next Step

Activate TASK-2026-09-02-002 for the exact two substitutions, bounded amd64 build/package validation, current-candidate refreeze, independent Tech Lead review, and commit. Then rerun TASK-011 from the beginning against that exact reviewed commit

## Signed Handoff

[Agent Message] From: technical_architect To: product_manager

PASS investigation. Restore both reviewed Wolfi glibc 2.44 defaults only, require replacement index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d` and amd64 child `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd`, and require resulting Dockerfile SHA-256 `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`. Preserve every other current input, build and requalify current source on amd64, retain exact APK transaction evidence, and keep promotion fail-closed until immutable package/provenance/SBOM/scan gates pass. Arm64 and all host/deployment mutation remain unauthorized
