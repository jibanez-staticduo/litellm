---
id: TASK-2026-08-31-010-pin-candidate-rust-toolchain
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate
assigned_to: product_manager
handoff_from: tech_lead
reopened_count: 0
---

# Task: Pin candidate Rust toolchain

## Objective

Implement a deterministic Dockerfile-only Rust toolchain stage compatible with the immutable Wolfi glibc baseline, preserving Python pins, locks, source, native build behavior, and production.

## Acceptance Criteria

- [x] AC-1: Tech Lead reviews and approves/rejects TASK-009's exact digest-pinned Rust 1.97.1 recommendation and supply-chain assertions.
- [x] AC-2: Root Dockerfile alone adds the approved Rust toolchain stage/copies/env/assertions and removes only Wolfi `rust`.
- [x] AC-3: Rust/Cargo/LLVM/target assertions fail closed and pass natively on amd64; arm64 remains unauthorized without native validation.
- [x] AC-4: Python pins, `pyproject.toml`, `uv.lock`, Cargo files, application source/tests, runtime stage behavior, and production remain unchanged.
- [x] AC-5: Evidence and a newly frozen eight-path candidate manifest bind Dockerfile, Rust OCI provenance, combined patch, parser, locks, and Cargo fingerprints.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Review TASK-009's governed recommendation and exact current Dockerfile. Do not edit implementation. Resolve/freeze Rust OCI index/platform digests and approve or reject the Dockerfile-only correction with exact Developer constraints. Deployment remains unauthorized.

## Implementation Handoff

[Agent Message] From: product_manager To: developer

Implement only the exact Tech Lead-approved Dockerfile correction and fail-closed assertions recorded in this task. Preserve the existing Python 3.13 pin. Do not change locks, Cargo files, source/tests, runtime behavior, deployment, or production. Produce complete TASK-010 evidence and a newly frozen eight-path manifest; do not perform the full TASK-006 smoke until independent review authorizes it.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

### Findings And Authorization

[Agent Message] From: tech_lead To: product_manager

Verdict: APPROVE for bounded Developer implementation. TASK-009's digest-pinned Rust 1.97.1 toolchain-stage recommendation is the smallest coherent correction for the current root `Dockerfile`. It removes only the incompatible live Wolfi Rust/LLVM resolution while preserving the digest-pinned Wolfi builder/runtime, exact Python 3.13 pins, both frozen syncs, Maturin native build, copied runtime artifact, locks, application behavior, and production

Independent registry resolution on 2026-08-31 confirms `docker.io/library/rust:1.97.1-slim-bookworm` and the digest-only reference resolve to OCI index `sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3`. Its authorized amd64 platform manifest is `sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b`; its metadata-only arm64/v8 platform manifest is `sha256:b28e5606d830400fabf789f910f9ed2ea22cdd6d51d463c5d0baa30bb2bedb2d`. The index also contains unrelated platforms and attestation manifests, which do not expand this authorization

A native amd64 execution probe of that exact index reports `rustc 1.97.1`, commit `8bab26f4f68e0e26f0bb7960be334d5b520ea452`, host `x86_64-unknown-linux-gnu`, LLVM `22.1.6`, Cargo `1.97.1`, and active toolchain `1.97.1-x86_64-unknown-linux-gnu`. The unchanged Wolfi input remains glibc `2.43-r10`; its bare amd64 filesystem has no `/usr/lib/libLLVM.so.22.1`. This independently corroborates TASK-009's identity and isolation claims. Arm64 has immutable manifest provenance only and remains unauthorized for candidate promotion until native arm64 execution, build, and final-image gates pass

The current root `Dockerfile` contains the approved TASK-008 five-line Python correction and still installs only one unpinned `rust` entry in the builder package list. The authorized scope is therefore additive Rust OCI stage/copies/environment/assertions plus removal of that one entry. No runtime-stage package, Python line, sync command, Maturin behavior, Cargo file, source, test, configuration, deployment, or production artifact may change

### Fail-Closed Assertion Contract

The assertion must run in the builder after the Rust directories are copied and after `apk add`, but before the first `uv sync`. It must use `ARG TARGETARCH`, map only `amd64` to `x86_64` and `arm64` to `aarch64`, and exit nonzero for an empty or any other architecture. It must parse `rustc -vV` as exact full lines and require all of: `release: 1.97.1`, `commit-hash: 8bab26f4f68e0e26f0bb7960be334d5b520ea452`, `host: ${expected_arch}-unknown-linux-gnu`, and `LLVM version: 22.1.6`. It must require Cargo output to begin exactly `cargo 1.97.1 ` and require `/usr/lib/libLLVM.so.22.1` to be neither an existing path nor a symlink. A command failure, missing field, duplicate/changed value, unsupported architecture, Cargo mismatch, or Wolfi LLVM path must fail the Docker layer before dependency installation

`CARGO_HOME=/usr/local/cargo` and `RUSTUP_HOME=/usr/local/rustup` must be explicit builder environment values, and `/usr/local/cargo/bin` must precede both `/app/.venv/bin` and the inherited path. This prevents an APK or later environment entry from silently selecting another Rust binary. The existing `UV_PROJECT_ENVIRONMENT` and `UV_LINK_MODE` values remain unchanged

### Exact Developer Handoff

[Agent Message] From: tech_lead To: developer

Modify only the root `Dockerfile`. Add global `ARG RUST_TOOLCHAIN_IMAGE=docker.io/library/rust:1.97.1-slim-bookworm@sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3`; add `FROM $RUST_TOOLCHAIN_IMAGE AS rust-toolchain` before the builder; in the builder declare `ARG TARGETARCH`, copy `/usr/local/cargo` and `/usr/local/rustup` from that stage to the same absolute paths, remove only the existing Wolfi `rust` package entry, and extend the builder environment with `CARGO_HOME`, `RUSTUP_HOME`, and a path beginning `/usr/local/cargo/bin:/app/.venv/bin:`. Do not add a tag-only fallback, rustup network install, Wolfi LLVM package, glibc upgrade, or whole-builder replacement

Before the first `uv sync`, add one fail-closed assertion layer implementing the exact Rust/Cargo/LLVM/`TARGETARCH` contract above. Use exact-line checks for `rustc -vV`, reject unsupported or empty `TARGETARCH`, and test both nonexistence and non-symlink status for `/usr/lib/libLLVM.so.22.1`. Do not weaken a failed assertion, select binaries by a non-approved path, or authorize arm64 based on OCI metadata or emulation

Produce `.staticeng/evidences/TASK-2026-08-31-010-pin-candidate-rust-toolchain/SUMMARY.md` and secret-free logs. Record the exact Dockerfile diff, `git diff --check`, pre/post Dockerfile SHA-256, the frozen Rust index and amd64/arm64 platform digests above, native amd64 assertion output, and scoped unchanged fingerprints. Re-freeze exactly the existing eight candidate paths, with the corrected `Dockerfile` replacing its old fingerprint, and record a new ordered manifest checksum. Also bind the new combined binary patch checksum from base `9af49e5b34e25cdc9ad40f9bb50a178f40320417`, unchanged parser fingerprint, unchanged `pyproject.toml` and `uv.lock` fingerprints, and unchanged `litellm-rust/Cargo.toml` and `litellm-rust/Cargo.lock` fingerprints. Abort on any path-set, digest, fingerprint, package, or assertion drift

TASK-010 does not authorize the complete candidate build or smoke reserved for TASK-006 unless PMA explicitly reassigns those gates. It never authorizes deployment, production replacement, production restart, credentials, database access, or arm64 promotion. Rollback before promotion is the inverse root-Dockerfile-only change and restoration of the prior frozen Dockerfile/manifest fingerprints; any later deployment rollback remains redeployment of the separately recorded prior immutable image

### Acceptance Criteria Coverage

- **AC-1: PASS.** The exact recommendation, immutable OCI index, two relevant platform manifests, amd64 toolchain identity, fail-closed assertions, architecture boundary, and scope were independently reviewed and approved
- **AC-2: PENDING DEVELOPER.** Authorization is restricted to the root `Dockerfile` additions and removal of only Wolfi `rust`
- **AC-3: PENDING DEVELOPER/TASK-006.** Native amd64 toolchain identity is independently proven; the implemented assertion and complete candidate build remain required, and arm64 remains unauthorized without native validation
- **AC-4: PENDING DEVELOPER.** The review found no need to change the preserved files or behavior; scoped unchanged evidence remains required after implementation
- **AC-5: PENDING DEVELOPER.** The exact eight-path replacement manifest and supplementary OCI, patch, parser, Python lock, and Cargo fingerprints must be newly frozen after the Dockerfile change

### Documentation Impact

No product or steady-state architecture documentation is required. This is a build supply-chain correction that preserves application behavior and the approved LazyMCP contract. Task and evidence closure are required; no CodeMap change is warranted because no source module, route, contract, or verification command is added or moved

### Open Risks

The Rust image is an external immutable supply-chain input, so any registry mismatch must abort rather than re-resolve to a tag. The broader Wolfi APK transaction remains live and unbound outside the Rust correction. Complete amd64 Maturin build, copied native-extension imports, final runtime checks, and all TASK-006 smoke gates remain unproven. Arm64 metadata does not establish native compatibility or promotion readiness. `staticeng_validate` remains blocked by the repository's pre-existing missing-CodeMap inventory; `staticeng_repair` dry-run confirms the unresolved items require separate module-boundary decisions, so no unrelated repair was applied in this review

### Recommended Next Step

PMA should route the exact handoff above to Developer, then return the Dockerfile and TASK-010 evidence for independent Tech Lead post-implementation review. Only after that review freezes the replacement authorization should PMA reopen TASK-006 for the complete amd64 candidate build and isolated smoke

## Developer: Post Implementation Expectations

### Summary

Implemented the exact authorized root `Dockerfile` correction. The builder imports Rust 1.97.1 from the approved digest-pinned OCI stage, removes only Wolfi `rust`, explicitly selects the copied Cargo/Rustup directories, and runs fail-closed identity and isolation assertions before the first dependency sync

### Work Performed

- Added the approved Rust OCI argument and toolchain stage, builder `TARGETARCH`, two absolute directory copies, and required environment ordering
- Removed only the Wolfi `rust` package entry and retained every Python 3.13 pin, sync selector, non-Rust package, runtime-stage line, source file, test, and lock
- Added exact full-line rustc field assertions with duplicate-field rejection, exact Cargo prefix validation, supported-architecture mapping, and both path and symlink absence checks for Wolfi LLVM
- Passed a bounded native amd64 Docker assertion probe and verified unsupported architecture fails closed; did not run the full candidate build or TASK-006 smoke
- Re-froze the exact eight-path manifest and bound Rust OCI provenance, combined patch, parser, Python lock, and Cargo fingerprints in the evidence packet

### Acceptance Criteria Coverage

- **AC-1: PASS.** Tech Lead approval and immutable provenance are recorded above
- **AC-2: PASS.** The implementation delta is restricted to the authorized root Dockerfile correction
- **AC-3: PASS WITH ARM64 BOUNDARY.** Native amd64 identity and isolation assertions pass; unsupported architecture fails closed; arm64 remains unauthorized without native validation
- **AC-4: PASS.** Preserved fingerprints and empty scoped diffs prove locks and Cargo files unchanged; runtime behavior and production were not exercised or modified
- **AC-5: PASS.** Evidence records post-change Dockerfile SHA-256 `30e2932754e61078f28401daac7029c4cdf4b591a67cceca551139ab1b6ed03c`, manifest SHA-256 `c49a16e0d8e297b3478d08bea399dc011eda3e378c1ace5a1044455300b735a5`, and combined patch SHA-256 `c3c336f90eb26366aa35c4eee1ec7058bba78064c91d7c0161469fa3fc251097`

### Documentation Impact

No product or steady-state architecture documentation is required. No CodeMap update is warranted because this builder supply-chain correction adds no source module, route, contract, or verification command

### Open Risks

The complete amd64 Maturin build, copied native-extension imports, final runtime checks, and TASK-006 smoke remain pending independent authorization. Arm64 has OCI metadata only and remains unauthorized. `staticeng_validate` remains blocked by the pre-existing missing-CodeMap inventory; repair dry-run identified unrelated module-boundary work, so no repair was applied

### Recommended Next Step

PMA should route the corrected Dockerfile and TASK-010 evidence to Tech Lead for independent post-implementation review. TASK-006 must remain closed until that review freezes replacement authorization

### Signed Handoff

[Agent Message] From: developer To: product_manager

TASK-010 implementation is complete within the exact authorization. Root `Dockerfile` now uses the digest-pinned Rust 1.97.1 toolchain stage and fail-closed pre-sync assertions; native amd64 identity passes and unsupported architecture fails closed. Python pins, locks, Cargo files, application paths, runtime stage behavior, and production remain unchanged. The new eight-path manifest and all required provenance/fingerprints are frozen under the TASK-010 evidence packet. No complete candidate build, TASK-006 smoke, deployment, production access, commit, or push was performed. Return this packet to Tech Lead for independent review

## Tech Lead Post-Implementation Review

### Summary

[Agent Message] From: tech_lead To: product_manager

Verdict: PASS. No blocking findings remain. The root `Dockerfile` implements the authorized digest-pinned Rust 1.97.1 stage, absolute Cargo/Rustup copies, explicit environment precedence, Wolfi `rust` removal, and pre-sync fail-closed assertions without expanding TASK-010 scope

### Work Performed

Independently inspected the exact current Dockerfile diff and all TASK-010 evidence logs. Recomputed the current Dockerfile, Python metadata/lock, Cargo metadata/lock, and eight candidate-path fingerprints; all equal the frozen evidence. Recomputed the ordered eight-path manifest checksum, combined tracked binary patch from the authorized base, and unchanged six-application-path patch; all equal the recorded values

The assertion layer is correctly ordered after the toolchain copies and unchanged non-Rust APK transaction but before dependency metadata and the first `uv sync`. `TARGETARCH` accepts only `amd64` and `arm64`; empty and unsupported values use the failing default branch. Each required `rustc -vV` field is constrained to one occurrence and one exact full-line value. Cargo must start with `cargo 1.97.1 `, and both file existence and symlink existence checks reject `/usr/lib/libLLVM.so.22.1`. The copied Cargo path precedes the virtual environment and inherited path. Native amd64 evidence proves the exact release, full commit, x86_64 host, LLVM 22.1.6, Cargo 1.97.1, and absent Wolfi LLVM path; the unsupported-architecture probe exits 1 before Rust execution

Independent registry inspection reconfirmed Rust OCI index `sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3`, amd64 platform manifest `sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b`, and metadata-only arm64/v8 manifest `sha256:b28e5606d830400fabf789f910f9ed2ea22cdd6d51d463c5d0baa30bb2bedb2d`. Other index platforms and attestations do not expand authorization

### Acceptance Criteria Coverage

- **AC-1: PASS.** The implemented image and identity contract exactly match the prior Tech Lead approval and independently re-resolved OCI provenance
- **AC-2: PASS.** Relative to the TASK-008 pre-change Dockerfile, TASK-010 changes only the approved root-Dockerfile Rust stage, copies, builder argument/environment/assertions, and removal of Wolfi `rust`
- **AC-3: PASS WITH ARM64 BOUNDARY.** The fail-closed contract and native amd64 probe pass; unsupported architecture fails. Arm64 remains unauthorized because no native arm64 build/runtime validation exists
- **AC-4: PASS.** Python pins/selectors, `pyproject.toml`, `uv.lock`, Cargo files, seven application paths, runtime stage behavior, deployment, and production are preserved for TASK-010
- **AC-5: PASS.** All path fingerprints, OCI digests, manifest checksum, tracked patch checksums, parser fingerprint, and Python/Cargo fingerprints independently reproduce

### Documentation Impact

No product or steady-state architecture documentation is required. The change affects builder supply-chain selection only and adds no source module, route, public behavior, or CodeMap command

### Open Risks

TASK-010 proves the bounded toolchain stage, not the complete candidate. The full Maturin build, final-image Python/ABI and copied-extension imports, isolated protocol smoke, and production-invariant/cleanup gates remain TASK-006 Reopen 2 responsibilities. Arm64 remains unauthorized for promotion. Repository-wide `staticeng_validate` remains blocked by the pre-existing missing-CodeMap inventory and is not a defect in this bounded correction

### TASK-006 Reopen 2 Authorization

[Agent Message] From: tech_lead To: qa_engineer

Authorize TASK-006 Reopen 2 candidate construction and isolated amd64 smoke from exact Git base `9af49e5b34e25cdc9ad40f9bb50a178f40320417`. Use build/runtime OCI index `cgr.dev/chainguard/wolfi-base@sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f` and Rust OCI index `docker.io/library/rust:1.97.1-slim-bookworm@sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3`; require Rust amd64 platform manifest `sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b`. The arm64/v8 manifest `sha256:b28e5606d830400fabf789f910f9ed2ea22cdd6d51d463c5d0baa30bb2bedb2d` is provenance only and does not authorize an arm64 build or promotion

Construct a clean detached worktree under `/tmp/opencode` from exactly the following ordered eight-path manifest and no other shared-worktree change:

```text
30e2932754e61078f28401daac7029c4cdf4b591a67cceca551139ab1b6ed03c  Dockerfile
1aa2a86213d076d2e1addc751e0b3ea9660e8c8cd4a9e86cb00144b0ff34f723  gateway/routes/allowlist.py
440044fcf74a5afc8d35f94f8bad5b71e1702f8b7227933757c0f848f2bc858b  litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py
5e1ff87728492396a609c886c124fb639624b58f4d21f105ba53853ce1e10fd4  litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py
1a0cf095cf037b32461b17301adea1f95b5dd62d111a45ae924a818da98b2967  litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py
2eec9a86b1fe514faebc64356842cca1901ba648185b9e49d4e91e13f122ec9f  litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py
886d5b443d75e6477bd8f609543bdf0160f9105ce71c137f7f6426791f0d308f  litellm/proxy/proxy_server.py
b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462  litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py
```

Require ordered line-oriented manifest SHA-256 `c49a16e0d8e297b3478d08bea399dc011eda3e378c1ace5a1044455300b735a5`. Apply/reproduce only the Dockerfile plus six tracked application-path binary patch whose SHA-256 from the base is `c3c336f90eb26366aa35c4eee1ec7058bba78064c91d7c0161469fa3fc251097`; copy the untracked parser separately and require its SHA-256 above. The unchanged six-application-path tracked patch remains `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`

Before build, require `pyproject.toml` SHA-256 `3b8240e1f70307caf0c1641639577060eda2d7070b8962a008f91dc949b12117`, `uv.lock` `a7cc57875c67de85bbae0f82b834f31fc9d0c029073ef29e0883787a31a985e8`, `litellm-rust/Cargo.toml` `65cb1ec9ed32ebc0f450c0649a03159943a1f21625f61f1c993448b2ff60b83a`, and `litellm-rust/Cargo.lock` `ef6ae9d1e34b0bf82d93f06a3ef62694a1489a2a890b3cadecdbd74120e2273d`. Abort on any base, path set, fingerprint, patch, manifest, OCI index/platform, package-resolution, or assertion mismatch

Build only `linux/amd64` with `--pull=false`, record immutable candidate image identity, and require the Dockerfile Rust assertions to pass before either frozen sync. Then execute every original TASK-006 gate: final-image Python 3.13.15, `cpython-313`, x86_64 SOABI, `python`/`python3.13` identity, uvloop 0.21.0, representative copied native-extension imports including the LiteLLM Rust bridge, all six discovery routes and exact resources, exact no-token/invalid-token 401 challenges, safely available authorized initialize/tool behavior, repeated reconnects with zero discovery 404s, readiness, `/mcp`, MCP REST, upstream-preservation checks, production pre/post identity and readiness invariants, and complete cleanup. Mark credential-bound checks blocked rather than weakening them, never expose secrets, and do not use production credentials or databases

This authorization permits detached candidate construction and isolated smoke only. It does not authorize deployment, production restart/replacement, data/configuration mutation, or arm64 promotion

### Recommended Next Step

PMA should reopen TASK-006 as Reopen 2 and route the exact authorization above to QA Engineer. Return the immutable image identity and complete secret-free evidence for final technical review before any promotion decision

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-010 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
