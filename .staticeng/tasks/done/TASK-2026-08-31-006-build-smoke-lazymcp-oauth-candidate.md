---
id: TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate
complexity: standard
track: implementation
slice: qa
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-003-implement-lazymcp-oauth-discovery
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 6
---

# Task: Build and smoke LazyMCP OAuth candidate

## Objective

Construct the Tech Lead-authorized seven-path candidate in a clean detached worktree and verify packaging/runtime behavior without replacing, restarting, or mutating the production container.

## Acceptance Criteria

- [ ] AC-1: Detached build context matches the authorized base, seven-path manifest, and frozen fingerprints exactly.
- [ ] AC-2: Docker candidate builds successfully and immutable image identity is recorded.
- [ ] AC-3: Isolated secret-free runtime smoke proves all six discovery routes, exact resources, and exact 401 challenge behavior.
- [ ] AC-4: Isolated protocol smoke proves authorized initialize/tool behavior where safely possible and repeated reconnects produce zero discovery 404s.
- [ ] AC-5: Readiness, `/mcp`, MCP REST, and upstream-preservation smoke pass or any environment-bound limitation is evidenced without claiming success.
- [ ] AC-6: Production container/image/config/database/credentials remain unchanged and cleanup is verified.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/` with `SUMMARY.md` and logs for manifest, build, image identity, startup, smoke, production invariants, and cleanup. Never log credentials, tokens, codes, cookies, or secret-bearing payloads.

## Handoff

[Agent Message] From: product_manager To: qa_engineer

Follow the exact manifest and detached-worktree procedure authorized in `.staticeng/evidences/TASK-2026-08-31-005-review-lazymcp-oauth-security/SUMMARY.md:216`. First verify the source fingerprints still match; stop if they drift. Build only in `/tmp/opencode`. Run a separate isolated container/network/config suitable for secret-free checks; do not mount production credentials or databases and do not stop/restart/replace the running `litellm` container. Record pre/post production container ID, image ID, status, and readiness without exposing secrets. If a real authorized tool call cannot be performed without credentials, mark only that sub-gate blocked and do not weaken the remaining smoke. Remove the detached worktree/container after evidence capture but retain the candidate image for inspection. Return signed shared output.

## Reopen History

### Reopen 1 - Python 3.13 packaging correction

The initial seven-path build failed because the unversioned Wolfi package resolved CPython 3.14.4 and `uvloop==0.21.0` fell back to an unsupported source build. TASK-007 diagnosed the issue; TASK-008 applied and independently approved an exact five-line Python 3.13 pin. Rebuild only from the newly authorized eight-path manifest, base, OCI index, fingerprints, combined patch checksum, and parser checksum recorded in `.staticeng/tasks/done/TASK-2026-08-31-008-pin-candidate-python313.md:112`. Abort on any mismatch. Validate final-image Python 3.13.15, ABI/SOABI, uvloop 0.21.0, copied native-extension imports, and then run the complete original smoke contract. Deployment remains unauthorized.

### Reopen 2 - Pinned Rust toolchain correction

Reopen 1 resolved Python/uvloop but failed because live Wolfi Rust/LLVM required GLIBC 2.44 while the immutable base contains 2.43. TASK-009 diagnosed the package-set mismatch; TASK-010 implemented and Tech Lead approved a digest-pinned Rust 1.97.1 toolchain stage with fail-closed identity/architecture assertions. Resume only from the exact base, Rust/Wolfi OCI provenance, eight-path fingerprints, manifest checksum `c49a16e0d8e297b3478d08bea399dc011eda3e378c1ace5a1044455300b735a5`, combined patch checksum `c3c336f90eb26366aa35c4eee1ec7058bba78064c91d7c0161469fa3fc251097`, parser checksum, and preserved lock/Cargo fingerprints recorded in `.staticeng/tasks/done/TASK-2026-08-31-010-pin-candidate-rust-toolchain.md:166`. Abort on drift. Build amd64 only, validate final image, execute the full original smoke, and preserve production invariants. Deployment and arm64 remain unauthorized.

### Reopen 3 - System Python-backed venv

Reopen 2 passed Rust/Maturin but failed final validation because uv had downloaded managed CPython 3.13.13 instead of constructing the copied venv from pinned system CPython 3.13.15. TASK-011 diagnosed the mismatch; TASK-012 applied and Tech Lead approved exactly two `/usr/bin/python3.13` uv selectors and one `/app/.venv/bin/python` validation command. Resume only from the frozen inputs in `.staticeng/tasks/done/TASK-2026-08-31-012-pin-venv-system-python.md:202`, including Dockerfile `ab60e645a484ac96b3d43fa23575b9f6aed30f39799bb17e28d1b54dfbe17fbc`, manifest `7b385506ab41f401bb1b6f925611fa3ba793884ea84db8bf3d6c9ff7bb534337`, combined patch `712f8bb20e3a3681694cd523c819d2c9fcfb6a2a99be015f12aee41a75fcf7da`, unchanged application patch, parser, locks, Cargo, and OCI provenance. Abort on drift, build amd64 only, then execute every original final-image and smoke gate. Deployment and arm64 remain unauthorized.

### Reopen 4 - Coherent Wolfi glibc/Python base

Reopen 3 proved pinned Python 3.13.15 packages require GLIBC 2.44 while the old immutable Wolfi base contains 2.43. TASK-013 diagnosed the package closure; TASK-014 atomically advanced both build/runtime Wolfi defaults and passed independent review. Resume only from `.staticeng/tasks/done/TASK-2026-08-31-014-advance-wolfi-base.md:188` with Dockerfile `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`, ordered manifest `f7def12e07e90dbfe2a27651eab73617660191efeab7b97e7d200fc01ebd5e13`, combined patch `501797e94d980f1ed7f1293d4fe57adea61237f9107f0f0025a5a00d6bbd2751`, unchanged application patch, exact Wolfi/Rust/uv OCI provenance, parser, locks, Cargo, and preserved fingerprints. Abort on drift. Build/smoke amd64 only. Missing signature, aggregate SBOM, and comparative scanners do not block isolated smoke but remain fail-closed promotion/deployment blockers. Production and arm64 remain unauthorized.

### Reopen 5 - Corrected trusted-base smoke

TASK-015 proved the retained image is functionally correct at route registration; Reopen 4 smoke omitted the trusted HTTPS public base required by the reviewed security policy, so handlers intentionally returned 404 and challenge construction failed closed. TASK-003 Reopen 5 added and Tech Lead approved test coverage for this exact Docker-bridge boundary. Re-smoke retained image `sha256:0ade7608d10588994a73d45ffb1bb66e994966fe71edd640a9599ffca754fcdf` without rebuild, using only existing secret-free settings plus `PROXY_BASE_URL=https://candidate.invalid`. Assert exact reserved authority, zero discovery 404s, challenges, selection-header invariance, reconnect, readiness and preservation surfaces. Credential-authorized behavior may remain explicitly blocked if unavailable without production DB/credentials. Production, deployment, arm64, and rebuild remain unauthorized.

### Reopen 6 - Toolset admission ordering candidate

Reopen 5 passed discovery, aggregate/scoped challenges, reconnect, readiness, initialization, and preservation but exposed pre-admission toolset database resolution. TASK-003 Reopens 6-7 implemented and Tech Lead approved admission-before-resolution with anonymous fail-closed authorization and full context lifecycle tests. The retained prior image is obsolete. Build a new detached amd64 candidate only from the frozen authorization in `.staticeng/evidences/TASK-2026-08-31-005-review-lazymcp-oauth-security/SUMMARY.md:467`, including `server.py`, current Dockerfile and exact checksums/provenance. Smoke with `PROXY_BASE_URL=https://candidate.invalid`; repeat all original gates plus explicit toolset no-token/invalid-token before DB and admitted DB-down semantics. Real authorized tool behavior may remain blocked without production DB/credentials. Promotion remains blocked by signature/SBOM/scans. Production, deployment and arm64 remain unauthorized.

# Post Implementation Task Updates

## QA Engineer: Post Implementation Expectations

Verdict: REJECT. AC-1 and AC-6 pass. AC-2 fails because the exact authorized Docker build selected CPython 3.14.4 and failed compiling `uvloop==0.21.0` when `/usr/bin/file` was unavailable. AC-3 through AC-5 remain unverified because no candidate image was produced

Production container and image identity remained unchanged and healthy. No candidate container or network was created, and the detached worktree was removed. Evidence: `.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/SUMMARY.md`

## QA Engineer: Reopen 1 Post Implementation Expectations

Verdict: REJECT. AC-1 and AC-6 pass. The exact eight-path base, OCI index, path fingerprints, combined patch checksum, and manifest checksum matched. AC-2 fails because the authorized amd64 build stopped during the second frozen sync: `rustc` could not load `libLLVM.so.22.1`, which requires unavailable `GLIBC_2.44`

AC-3 through AC-5 and final-image Python/ABI/native-import gates remain unverified because no final image was produced. Production identity and health remain unchanged; no production secrets, database, or configuration were used. Candidate image/container/network are absent and the detached worktree was removed. Reopen 1 evidence is appended to `.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/SUMMARY.md`

## QA Engineer: Reopen 2 Post Implementation Expectations

Verdict: REJECT. AC-1 and AC-6 pass. The exact TASK-010 base, OCI provenance, eight-path manifest, fingerprints, patch/parser checksums, Python locks, Cargo files, and Rust assertions matched. The amd64 build passed both frozen syncs and built the LiteLLM Rust bridge, but AC-2 fails at the final runtime layer because system `python` cannot import generated `prisma` from `/app/.venv`

No final image exists, so final-image Python/ABI/native-import validation and AC-3 through AC-5 smoke remain unverified. Production container/image/readiness remain unchanged; no production credentials, database, or configuration were used. Candidate image/container/network are absent and the detached worktree was removed. Reopen 2 evidence is appended to `.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/SUMMARY.md`

## QA Engineer: Reopen 3 Post Implementation Expectations

Verdict: REJECT. AC-1 and AC-6 pass. All TASK-012 frozen inputs matched, and the amd64 build selected `/usr/bin/python3.13` without a managed Python download. AC-2 fails at the first frozen sync because the pinned system interpreter's `math.cpython-313-x86_64-linux-gnu.so` requires `GLIBC_2.44`, unavailable in the authorized immutable Wolfi base

No final image exists, so venv linkage, Python ABI/SOABI, uvloop, Prisma, Rust bridge/native imports, normal entrypoint, and AC-3 through AC-5 smoke remain unverified. Production container/image/readiness remain unchanged; no production credentials, database, or configuration were used. Candidate image/container/network are absent and the detached worktree was removed. Reopen 3 evidence is appended to `.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/SUMMARY.md`

## QA Engineer: Reopen 4 Post Implementation Expectations

Verdict: REJECT FOR FUNCTIONAL CANDIDATE; PROMOTION BLOCKED. AC-1, AC-2, and AC-6 pass. Exact TASK-014 inputs built as final image `sha256:0ade7608d10588994a73d45ffb1bb66e994966fe71edd640a9599ffca754fcdf`; Python 3.13.15, venv linkage, ABI/SOABI, glibc 2.44-r1, uvloop, Prisma, Rust/native imports, package/SPDX inventory, and normal entrypoint/readiness pass

AC-3 fails because all six required discovery aliases return 404 and exact LazyMCP challenges are absent or incorrect. AC-4 fails because reconnect probes produce 60/60 discovery 404s; credential-authorized tool behavior is separately blocked by the intentionally absent DB. AC-5 is partial: readiness, `/mcp`, MCP REST, and management tool-list surfaces are preserved, but LazyMCP behavior is not. Production is unchanged and healthy; candidate container/network/worktree are removed and images retained. Cosign, aggregate SBOM, and scanners remain unavailable promotion blockers. Evidence is appended to `.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/SUMMARY.md`

## QA Engineer: Reopen 5 Post Implementation Expectations

Verdict: PARTIAL / REJECT FOR CLOSURE. Retained image identity passed with no rebuild. All six discovery aliases return 200 with exact `https://candidate.invalid` resources, aggregate/scoped exact challenges and selection-header invariance pass, reconnect produces 60/60 HTTP 200 with zero discovery 404s, and readiness, `/mcp`, MCP REST, management listing, and aggregate initialize pass

AC-3 remains failed because `/toolset/tools-a/lazymcp` resolves the absent database before admission: no-token, selection-header, malformed-session, and invalid-key requests all return HTTP 503 without the required exact 401 challenge. Authorized real tool behavior remains BLOCKED by absent DB/server credentials. Production is unchanged and healthy; disposable container/network were removed and the retained image remains unchanged. Evidence is appended to `.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/SUMMARY.md`

## QA Engineer: Reopen 6 Post Implementation Expectations

Verdict: PASS FOR CANDIDATE BUILD/ISOLATED SMOKE; PROMOTION BLOCKED. Exact nine-path candidate built as `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. AC-1 through AC-3, AC-5, and AC-6 pass. AC-4 passes for aggregate initialize, reconnect zero-404, and admitted toolset DB-down semantics; only real authorized tool execution remains BLOCKED by the intentionally absent production DB/server credentials

All packaging/runtime, six discovery alias/resource, aggregate/scoped/toolset challenge, selection-header invariance, readiness, `/mcp`, MCP REST, management listing, and preservation gates pass. Production is unchanged and healthy; candidate container/network/worktree are removed and image retained. Signature/attestation, aggregate SBOM, comparative scans, and Critical/High disposition remain mandatory promotion blockers. Evidence is appended to `.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/SUMMARY.md`

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-006 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
