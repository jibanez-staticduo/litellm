---
id: TASK-2026-08-31-009-investigate-candidate-rust-llvm
complexity: standard
track: investigation
slice: foundation
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Investigate candidate Rust LLVM failure

## Objective

Identify the smallest deterministic correction for the authorized Wolfi builder's `rustc` failing to load `libLLVM.so.22.1` because it requires unavailable `GLIBC_2.44`, without changing application behavior or production.

## Acceptance Criteria

- [x] AC-1: Trace exact package/base provenance for rustc, LLVM, glibc, maturin, and the LiteLLM native build stage.
- [x] AC-2: Determine whether this is a repository Dockerfile defect, live Wolfi package-set inconsistency, stale index/base mismatch, or unsupported build path.
- [x] AC-3: Compare minimal options including exact compatible package pins, builder-base change, Rust toolchain isolation, skipping/reusing native artifacts, or an existing repository build target.
- [x] AC-4: Recommend one fail-closed deterministic correction with exact files/args, platform scope, tests, rollback, and manifest implications.
- [x] AC-5: Update this task with signed evidence; do not mutate source, Dockerfiles, images, locks, production, or deployment.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Read TASK-006 Reopen 1 build evidence and inspect exact Wolfi OCI/package provenance, Dockerfile stages, Rust/LLVM/Maturin configuration, CI image paths, and current production metadata. Prefer a coherent pinned package/base solution over ad-hoc copying or disabling native builds. Research only. Return an exact recommendation suitable for Tech Lead authorization.

# Post Implementation Task Updates

## Technical Architect: Post Investigation Expectations

### Summary

PASS for investigation. The candidate failure is a deterministic repository packaging defect exposed by a live Wolfi package-set transition: the digest-pinned July builder contains `glibc-2.43-r10`, while unversioned `rust` resolves from the live repository to `rust-1.97-1.97.1-r1` and `libLLVM-22-22.1.8-r3`; that LLVM binary requires `GLIBC_2.44`. APK dependency metadata models only the `libm.so.6` SONAME, so resolution succeeds and `rustc` fails only at execution. The smallest robust correction is to isolate the already repository-standard Rust 1.97.1 toolchain behind a multi-architecture, digest-pinned toolchain stage and stop resolving Rust/LLVM from Wolfi APK

### Work Performed

- Read TASK-006 Reopen 1 evidence. The exact amd64 build used Wolfi index `sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f`, whose amd64 manifest is `sha256:85ecaa3f494ee2339eaf6f74a23f19f934df3019a9a9dfc8c06f53c3aacc4e6b`; the second `uv sync --frozen` invoked Maturin and failed at `rustc -vV`
- Reproduced package resolution read-only against that exact base. Its installed package set has `glibc-2.43-r10` and `ld-linux-2.43-r10`. Live x86_64 APK resolution selects virtual `rust` as `rust-1.97-1.97.1-r1`, which requires `libLLVM-22-22.1.8-r3`; executing `/usr/bin/rustc` reproduces `libm.so.6: version GLIBC_2.44 not found`, required by `/usr/lib/libLLVM.so.22.1`
- Confirmed this is not a stale local index, Maturin defect, unsupported native build, or Rust MSRV problem. `pyproject.toml` pins `maturin==1.9.4` and the `litellm.rust_bridge._native` PyO3 build; `litellm-rust/Cargo.toml` requires Rust 1.88. The first dependency-only sync does not install the project, while the second sync correctly builds the native extension. Repository CircleCI independently pins Rust 1.97.1 before workspace `uv sync`
- Tested lower Wolfi Rust as a correction and rejected it. Exact `rust-1.88=1.88.0-r3` resolves with `libLLVM-20-20.1.8-r19`, but that retained LLVM binary also requires `GLIBC_2.44` on the digest-pinned base. Package pins alone therefore do not produce a coherent retained Wolfi set
- Verified the official Rust 1.97.1 toolchain on the exact Wolfi base: checksum-verified rustup 1.28.2 installed `rustc 1.97.1 (8bab26f4f 2026-07-14)`, Cargo 1.97.1, bundled LLVM 22.1.6, compiled and executed a native probe, and did not install `/usr/lib/libLLVM.so.22.1`. The same versions are the repository CircleCI contract
- Inspected the digest-pinned official image candidate `docker.io/library/rust:1.97.1-slim-bookworm@sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3`. It contains amd64 manifest `sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b` and arm64 manifest `sha256:b28e5606d830400fabf789f910f9ed2ea22cdd6d51d463c5d0baa30bb2bedb2d`; both provide the 1.97.1 toolchain. Production remained container `a4fee331519ed8fa2e0ae851f3e0e4a3533ebcae4f0c4752811a1f7a47f2fc8a`, image `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`, running healthy

### Options Considered

1. **Digest-pinned Rust toolchain stage: RECOMMEND.** Add one immutable multi-arch input, copy its `/usr/local/cargo` and `/usr/local/rustup` into the unchanged Wolfi builder, and remove Wolfi `rust`. This preserves the runtime/base, native build, lockfiles, Maturin contract, and repository Rust version while eliminating live Rust/LLVM APK coupling
2. **Wolfi package pins: REJECT.** Current retained Rust 1.88 and 1.97 paths both pull retained LLVM binaries requiring GLIBC 2.44. Pinning every older transitive APK would be larger, retention-dependent, and still not bind APK index bytes
3. **Upgrade the Wolfi base/glibc: REJECT FOR THIS CORRECTION.** A current Wolfi image exposes separate `glibc-2.44`, but replacing or surgically upgrading the digest-pinned base changes the complete builder and runtime package foundation. The old image pins `glibc`, `ld-linux`, and locale packages at 2.43, so an in-place 2.44 replacement conflicts rather than forming a minimal coherent transaction
4. **Change the whole builder base: REJECT.** A Debian/Rust builder would require translating every APK dependency and proving binary compatibility with the Wolfi runtime. It has a much larger impact surface than toolchain isolation
5. **Skip/reuse the native artifact: REJECT.** The root package deliberately builds `litellm.rust_bridge._native`; bypassing it changes the shipped package and evades required final-image native-import gates. No existing repository target produces the same full Python wheel/runtime image from a reusable, manifest-bound artifact
6. **Use `litellm-rust/crates/ai-gateway/Dockerfile`: REJECT.** It builds the standalone gateway binary, not the root Maturin Python extension, and its `rust:1.90-slim-bookworm` input is tag-only

### Exact Recommended Correction

Tech Lead should authorize only root `Dockerfile` changes equivalent to the following, with the Rust digest re-resolved and frozen immediately before authorization:

```dockerfile
ARG RUST_TOOLCHAIN_IMAGE=docker.io/library/rust:1.97.1-slim-bookworm@sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3

FROM $RUST_TOOLCHAIN_IMAGE AS rust-toolchain

FROM $LITELLM_BUILD_IMAGE AS builder

COPY --from=rust-toolchain /usr/local/cargo /usr/local/cargo
COPY --from=rust-toolchain /usr/local/rustup /usr/local/rustup
```

Remove only `rust` from the builder `apk add` list and extend the existing builder environment with `CARGO_HOME=/usr/local/cargo`, `RUSTUP_HOME=/usr/local/rustup`, and `/usr/local/cargo/bin` before the prior `PATH`. Declare `ARG TARGETARCH` in the builder stage. Do not change the runtime stage, Maturin settings, Cargo files, Python pins, uv lock, source, tests, or smoke contract. Add a fail-closed builder assertion before the first sync: `rustc -vV` must report release 1.97.1, commit `8bab26f4f68e0e26f0bb7960be334d5b520ea452`, host matching `TARGETARCH`, and LLVM 22.1.6; `cargo -V` must report 1.97.1; `/usr/lib/libLLVM.so.22.1` must be absent. Use shell case mapping `amd64 -> x86_64` and `arm64 -> aarch64`; reject every other `TARGETARCH`

This corrects amd64 now. The pinned image also contains arm64, but arm64 promotion remains unauthorized until a native arm64 builder performs equivalent build and runtime gates. Rollback is the inverse Dockerfile-only change and restoration of the previously frozen Dockerfile fingerprint; no data or runtime rollback is involved because deployment remains prohibited

### Acceptance Criteria Coverage

- **AC-1: PASS.** Exact base/index/platform, glibc, Rust, LLVM, Maturin, Cargo MSRV, and two-sync build-stage provenance is recorded
- **AC-2: PASS.** Classification is repository Dockerfile defect plus live Wolfi package-set inconsistency: immutable base libraries are mixed with unbound live APK packages. It is not an unsupported build path or stale local index
- **AC-3: PASS.** Package pins, base/glibc change, whole-builder change, toolchain isolation, artifact reuse/skip, and existing gateway target were compared
- **AC-4: PASS.** One fail-closed correction includes exact root Dockerfile inputs, assertions, amd64/arm64 scope, verification, rollback, and manifest requirements
- **AC-5: PASS.** Only this governed task was updated. No source, Dockerfile, retained image, lock, production, deployment, or CodeMap was changed; the read-only probe pulled one Rust image locally and removed it after inspection

### Documentation Impact

No product or steady-state architecture documentation is required. This is a builder supply-chain correction with no application behavior or integration-boundary change. The next authorization must replace the current eight-path candidate manifest with a newly frozen eight-path manifest containing the corrected `Dockerfile`, plus separately bind the new Rust OCI index and per-platform manifests, exact Dockerfile SHA-256, combined patch SHA-256, and unchanged fingerprints for `pyproject.toml`, `uv.lock`, `litellm-rust/Cargo.toml`, and `litellm-rust/Cargo.lock`

### Open Risks

The recommended Rust OCI index is immutable but external; Tech Lead must re-resolve its index and platform manifests at authorization time. Toolchain execution was proven on amd64 Wolfi, but the complete candidate build and copied native extension imports remain TASK-006 gates. Arm64 metadata exists but native execution remains unverified. Wolfi APK installs other unpinned live packages, so broader APK-index reproducibility remains outside this correction. `staticeng_validate` remains blocked by the repository's pre-existing missing-CodeMap inventory; this task changed no architecture or CodeMap structure and did not repair unrelated metadata

### Recommended Next Step

PMA should create a bounded foundation implementation task for the root `Dockerfile` correction, followed by independent review that freezes a replacement eight-path candidate manifest and Rust OCI provenance. Resume TASK-006 only after those checks pass; build amd64 with `--pull=false`, assert toolchain identity before sync, then retain all original Python ABI, native import, runtime smoke, production-invariant, and cleanup gates

### Signed Handoff

[Agent Message] From: technical_architect To: product_manager

PASS investigation. Authorize a Dockerfile-only, digest-pinned Rust 1.97.1 toolchain stage and remove Wolfi `rust`; do not pin older Wolfi Rust, upgrade glibc in place, change the full builder, or skip the native extension. Freeze the Rust OCI index/platform manifests and a new candidate manifest, require fail-closed rustc/Cargo/LLVM identity assertions, then resume TASK-006 on amd64. Production and all product artifacts remain unchanged

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-009 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
