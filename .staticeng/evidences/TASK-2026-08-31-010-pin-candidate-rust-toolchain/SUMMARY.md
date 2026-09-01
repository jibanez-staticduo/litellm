# TASK-010 Evidence Summary

## Summary

Implemented the Tech Lead-authorized root `Dockerfile` correction. The builder now imports Rust 1.97.1 from the approved digest-pinned OCI stage, removes only Wolfi `rust`, prioritizes the copied toolchain, and fails before dependency sync unless architecture, rustc, Cargo, LLVM, and Wolfi LLVM-path assertions all pass

## Acceptance Criteria Coverage

- **AC-1: PASS.** Tech Lead authorization is recorded in the task and binds OCI index `sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3`, amd64 manifest `sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b`, and metadata-only arm64/v8 manifest `sha256:b28e5606d830400fabf789f910f9ed2ea22cdd6d51d463c5d0baa30bb2bedb2d`
- **AC-2: PASS.** Only the root `Dockerfile` implementation changed. It adds the approved stage, copies, builder environment, and assertion layer and removes only the Wolfi `rust` package entry (`.staticeng/evidences/TASK-2026-08-31-010-pin-candidate-rust-toolchain/logs/01-dockerfile-diff.log`)
- **AC-3: PASS WITH ARM64 BOUNDARY.** A native amd64 Docker probe passed exact rustc 1.97.1 release, commit, x86_64 host, LLVM 22.1.6, Cargo 1.97.1, and absent `/usr/lib/libLLVM.so.22.1`. An unsupported architecture probe failed closed. Arm64 remains unauthorized because no native arm64 execution or build was performed (`.staticeng/evidences/TASK-2026-08-31-010-pin-candidate-rust-toolchain/logs/03-native-amd64-assertions.log`, `.staticeng/evidences/TASK-2026-08-31-010-pin-candidate-rust-toolchain/logs/04-fail-closed-unsupported-arch.log`)
- **AC-4: PASS.** Python pins and selectors remain in place. `pyproject.toml`, `uv.lock`, `litellm-rust/Cargo.toml`, and `litellm-rust/Cargo.lock` have no diff and retain their frozen fingerprints. Application manifest paths retain their prior fingerprints. No source, test, runtime-stage behavior, deployment, or production operation was performed (`.staticeng/evidences/TASK-2026-08-31-010-pin-candidate-rust-toolchain/logs/05-unchanged-scope.log`)
- **AC-5: PASS.** The replacement eight-path manifest checksum is `c49a16e0d8e297b3478d08bea399dc011eda3e378c1ace5a1044455300b735a5`. The combined tracked binary patch from base `9af49e5b34e25cdc9ad40f9bb50a178f40320417` is `c3c336f90eb26366aa35c4eee1ec7058bba78064c91d7c0161469fa3fc251097`; parser and lock/Cargo fingerprints are recorded in `.staticeng/evidences/TASK-2026-08-31-010-pin-candidate-rust-toolchain/logs/02-fingerprints-manifest.log`

## Verification

`git diff --check` passed. Native Docker server architecture was `amd64`. The bounded assertion-stage probe passed without running either `uv sync`, the complete candidate build, or TASK-006 smoke. OCI provenance was independently re-read with `docker buildx imagetools inspect`

`staticeng_validate` remains blocked by the repository's pre-existing missing-CodeMap inventory. The required repair dry-run confirmed those unresolved items require unrelated module-boundary decisions, so no repair was applied (`.staticeng/evidences/TASK-2026-08-31-010-pin-candidate-rust-toolchain/logs/06-staticeng-validation.log`)

## Documentation Impact

Product and steady-state architecture documentation are not required. The correction changes builder supply-chain selection only, without changing application behavior, runtime wiring, or navigable source, so no CodeMap update is warranted

## Open Risks

The complete Maturin candidate build, copied native-extension imports, final runtime checks, and TASK-006 smoke remain unexecuted by explicit authorization boundary. Arm64 has immutable manifest provenance only and remains unauthorized for promotion

## Independent Tech Lead Review

Verdict: PASS. The current Dockerfile exactly implements the approved correction and the fail-closed assertions are correctly ordered and scoped. Independent recomputation matched Dockerfile SHA-256 `30e2932754e61078f28401daac7029c4cdf4b591a67cceca551139ab1b6ed03c`, ordered eight-path manifest SHA-256 `c49a16e0d8e297b3478d08bea399dc011eda3e378c1ace5a1044455300b735a5`, combined tracked patch SHA-256 `c3c336f90eb26366aa35c4eee1ec7058bba78064c91d7c0161469fa3fc251097`, and unchanged application patch SHA-256 `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`

All eight path fingerprints and the preserved `pyproject.toml`, `uv.lock`, `litellm-rust/Cargo.toml`, and `litellm-rust/Cargo.lock` fingerprints reproduce. Independent registry inspection also reconfirmed the frozen Rust index and amd64/arm64 platform manifests. No blocking finding remains; TASK-006 Reopen 2 is authorized for exact detached amd64 candidate construction and isolated smoke using the inputs recorded in the task. Deployment and arm64 promotion remain unauthorized

[Agent Message] From: tech_lead To: product_manager

PASS. TASK-010 is technically complete. Reopen TASK-006 as Reopen 2 using the exact base, eight-path manifest, OCI provenance, checksums, preserved fingerprints, amd64 gates, production invariants, and authorization boundaries recorded in the TASK-010 Tech Lead post-implementation review
