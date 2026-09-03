# TASK-2026-09-02-002 Evidence Summary

## Summary

PASS for the authorized implementation and amd64 compatibility scope. Exactly the two approved root `Dockerfile` Wolfi defaults changed to index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`. The resulting Dockerfile SHA-256 is exactly `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`

Fresh no-cache `linux/amd64` builder and final builds from detached worktree `/tmp/opencode/task002-wolfi-source` passed against committed defaults. The retained evidence records builder config ID `sha256:f4f4c9a09d7a4855c88d9683ae133474e913696a6c21587197efc99114196ccb` and final config ID `sha256:1b4e9b94c71d096ed59a89176af32c7066aecd5d19bfc4ec26727f7f2d183f45`. Python/glibc ABI, uvloop, Prisma, LiteLLM Rust bridge, representative native imports, copied ELF, normal entrypoint/readiness, clean shutdown, source, rollback, and StaticEng gates pass

All disposable images, containers, builders, and caches were removed after identities and package evidence were retained. Production remained unchanged under credential-safe allowlisted observations. No commit, push, publication, deployment, Fedora action, NAS action, production configuration access, or arm64 execution occurred

## Work Performed

- Applied only the approved substitutions at `Dockerfile:4` and `Dockerfile:7`; verified exact post-edit hash, two-line semantic diff, patch fingerprint, dependency/lock/Cargo preservation, and rollback fingerprint
- Re-resolved frozen Wolfi, uv, Rust, and UI OCI indexes immediately before build; required exact amd64 children and used no build-argument override
- Ran a disposable native amd64 ABI preflight proving glibc/locale/loader `2.44-r1`, all four Python `3.13.15-r4` packages, Python 3.13.15, x86_64, `cpython-313`, exact SOABI, `math` import, and the math extension's `GLIBC_2.44` need
- Built clean no-cache builder and final targets with an isolated BuildKit instance; recorded immutable config/manifest identities, source labels, package manifests, embedded SPDX counts, exact Rust toolchain identity, and complete build results
- Proved final venv/system linkage, uvloop 0.21.0, Prisma engines, LiteLLM and Rust/native imports, copied ELF interpreters, environment/entrypoint/CMD invariants, HTTP 200 readiness, and clean exit
- Removed all task-owned validation resources, rechecked production through only allowlisted invariant formats, and ran `staticeng_validate` successfully

## Acceptance Criteria Coverage

- **AC-1: PASS.** Root `Dockerfile` is the only non-StaticEng source path changed. Its diff contains exactly the two approved digest substitutions, while application source, Python/Rust/uv/UI pins, APK lists, locks, Cargo, entrypoints, and deployment inputs remain unchanged
- **AC-2: PASS.** Fresh detached `linux/amd64` builder and final targets emitted exact immutable identities and passed Python 3.13.15, glibc 2.44-r1, uvloop 0.21.0, Prisma, Rust bridge, native imports, copied ELF, entrypoint, readiness, and shutdown gates
- **AC-3: PASS FOR IMPLEMENTATION AND COMPATIBILITY.** Dockerfile hash/diff, source preservation, OCI provenance, ABI, package inventory, rollback, cleanup, production invariants, and StaticEng validation pass. Signature/attestation, aggregate SBOM, comparative scan, and immutable APK closure remain explicit promotion blockers because required tools/artifact retention are unavailable
- **AC-4: PENDING TECH LEAD.** No commit or push was performed, as instructed. The exact source diff and evidence are ready for independent Tech Lead review and commit/push authority

## Documentation Impact

No product, public interface, architecture, operator, or CodeMap documentation change is required. This restores the previously reviewed Docker packaging contract without changing navigable source structure or application behavior. Task and evidence records capture the operational verification and mutable-APK boundary

## Open Risks

- Public Wolfi APK resolution remains mutable and retention-bound; this build records the actual selected package manifests and embedded SPDX counts but did not retain exact signed APK index bytes and every downloaded `.apk`
- Cosign, Syft, Grype, Trivy, Docker Scout, and an actual Docker SBOM plugin are unavailable, so exact-subject signature/attestation verification, aggregate SPDX/CycloneDX SBOMs, same-database scans, and Critical/High disposition remain fail-closed promotion gates
- The clean final build displayed the existing non-fatal Tornado test-directory cleanup message and Prisma's Wolfi-to-Debian engine fallback warning; final Prisma/native/runtime gates still passed
- Arm64 remains metadata-only and unauthorized. TASK-011's complete isolated database, real model/tool, OAuth, permission, logging, SBOM, scan, and signature qualification must restart after Tech Lead commits the reviewed correction

## Recommended Next Step

PMA should route this exact Dockerfile diff and Evidence Packet to Tech Lead for independent review. Tech Lead may commit and push only if the exact hash, source boundary, identities, and gates are accepted. Then TASK-011 should restart from the reviewed correction commit. Promotion, publication, Fedora/NAS mutation, deployment, and arm64 remain unauthorized

## Signed Handoff

[Agent Message] From: developer To: product_manager

PASS for authorized implementation and amd64 compatibility. Exactly the two approved root Dockerfile defaults changed, yielding SHA-256 `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`. Fresh detached no-cache amd64 builder `sha256:f4f4c9a09d7a4855c88d9683ae133474e913696a6c21587197efc99114196ccb` and final `sha256:1b4e9b94c71d096ed59a89176af32c7066aecd5d19bfc4ec26727f7f2d183f45` passed ABI, Python, glibc, uvloop, Prisma, Rust bridge, native import, ELF, entrypoint, readiness, shutdown, source, rollback, and static gates. All disposable validation resources were removed and production remained unchanged under credential-safe allowlisted observations. No commit, push, publication, deployment, Fedora/NAS mutation, production configuration access, or arm64 execution occurred. Mutable APK retention plus unavailable signature, aggregate SBOM, and comparative scanner gates remain fail-closed promotion blockers

## Independent Tech Lead Review

Verdict: PASS for source correction and amd64 compatibility. Independent recomputation matched Dockerfile SHA-256 `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`, exact two-substitution scope, patch SHA-256 `269cab0cc2d24322b3b542dc27c10b884cc593c6b5972ba2169056e1287b0a38`, and byte identity with the prior-approved TASK-014 Dockerfile. The retained builder/final identities and ABI/native/runtime results satisfy TASK-002's bounded build gate

Independent cleanup checks found zero TASK-002-labelled containers, images, networks, and volumes, no task Buildx builder, and only the repository root worktree. The production container retained its allowlisted identity and image, running/healthy state, restart count `0`, and OOM state `false`. `git diff --check` and `staticeng_validate` pass

AC-1 through AC-4 pass for TASK-002. Public APK retention, exact signed indexes/artifacts, signatures/attestations, aggregate SBOMs, comparative vulnerability scans, Critical/High disposition, complete TASK-011 behavior qualification, release publication, promotion, deployment, and arm64 remain fail-closed and unauthorized

[Agent Message] From: tech_lead To: product_manager

PASS. Approve the exact correction for commit and non-force push to fork `main`. Reopen TASK-011 only against the pushed commit. Do not publish or deploy a release image yet
