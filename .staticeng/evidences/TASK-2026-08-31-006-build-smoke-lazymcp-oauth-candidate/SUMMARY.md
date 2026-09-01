# Candidate Build and Smoke Summary

## Verdict

REJECT. The exact detached candidate manifest passed, but the authorized Docker build failed before producing an image. Runtime smoke therefore could not begin. Production remained unchanged and healthy, and disposable runtime/worktree artifacts were cleaned up

## Work Performed

- Verified base `9af49e5b34e25cdc9ad40f9bb50a178f40320417`, tracked patch SHA-256 `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`, and parser SHA-256 `b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462`
- Created `/tmp/opencode/lazymcp-oauth-candidate/worktree` detached at the authorized base, applied only the six-path binary patch, installed only the authorized parser, obtained `manifest-ok`, and passed `git diff --check` and parser comparison
- Ran the exact authorized build command with `--pull=false`; `uv sync` selected CPython 3.14.4 and failed building `uvloop==0.21.0` because `/usr/bin/file` is absent in the unchanged builder image
- Stopped without modifying the Dockerfile, dependency locks, candidate source, or production. No candidate image, container, network, config, database, or credential mount was created
- Removed the detached worktree. The source-only frozen patch remains under `/tmp/opencode` for diagnosis; production identity and health match the preflight baseline
- Ran `staticeng_validate`; it remains blocked by the known pre-existing repository-wide missing-CodeMap inventory and was not repaired in this isolated QA task (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/05-staticeng-validation.log`)

## Acceptance Criteria Coverage

- **AC-1: PASS.** Exact authorized base, seven-path manifest, frozen fingerprints, diff check, and parser comparison passed (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/01-manifest.log`)
- **AC-2: FAIL.** Docker build exited 1 at `uvloop==0.21.0`; no immutable candidate image identity exists (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/03-build.log`)
- **AC-3: UNVERIFIED.** No image existed from which to run isolated discovery and 401 challenge smoke
- **AC-4: UNVERIFIED.** Initialize, tool behavior, and repeated reconnect smoke could not run. No credential-dependent gate was attempted
- **AC-5: UNVERIFIED.** Candidate readiness, `/mcp`, MCP REST, and upstream-preservation smoke could not run. This is a build-bound limitation and is not claimed as success
- **AC-6: PASS.** Production container and image IDs remained identical, production remained running and healthy, no candidate runtime artifacts remain, and the detached worktree was removed (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/02-production-pre.log`, `.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/04-production-post-cleanup.log`)

## Documentation Impact

No product or architecture documentation change is required. This packet records a candidate-build failure only

## Open Risks

The candidate packaging path currently resolves Python 3.14.4 while locking `uvloop==0.21.0`, which has no usable wheel in this build and falls back to a source build requiring `/usr/bin/file`. Runtime behavior remains wholly unverified until a separately authorized packaging fix or build-environment correction produces the exact candidate

## Recommended Next Step

PMA should reopen packaging/build remediation under a separate task and obtain Tech Lead authorization for any Dockerfile, Python-version, or dependency change. After that fix is reviewed, rerun this candidate task from a newly frozen base and fingerprints; do not reuse this failed build as evidence of runtime success

## Signed Handoff

[Agent Message] From: qa_engineer To: product_manager

REJECT. Exact manifest and production-invariant gates passed, but the authorized Docker build failed at `uvloop==0.21.0` because `/usr/bin/file` is absent, so no image or runtime smoke exists. Detached worktree, containers, and networks are cleaned; production remains on the identical image, running healthy

## Reopen 1 Verdict

REJECT. The newly authorized eight-path manifest, all fingerprints, combined patch checksum, manifest checksum, and OCI index matched exactly. The amd64 build installed Python 3.13.15-r4 and completed the dependency sync with `uvloop==0.21.0`, but failed during the second frozen sync while building the LiteLLM Rust extension. `rustc` could not start because installed `libLLVM.so.22.1` requires `GLIBC_2.44`, which is unavailable in the authorized builder filesystem

### Reopen 1 Work Performed

- Reconstructed the detached candidate from base `9af49e5b34e25cdc9ad40f9bb50a178f40320417` using only the eight authorized paths
- Verified exact path fingerprints, tracked patch SHA-256 `8fa57ee3dc13968fd66cff04d4309e707f6af940196af8cb05b6f9acfb7ef6c7`, manifest SHA-256 `5ffff56cabaa5cf064166b17bac3c67ed4f95f8b99a26fbacdee6fc1d7e6c5ef`, and authorized Wolfi OCI index/platform manifests (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/06-reopen1-manifest.log`)
- Built only `linux/amd64` with `--pull=false`; no final image was emitted (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/07-reopen1-build.log`)
- Stopped at the authorized build failure without changing source, packaging, locks, or build arguments. Final-image Python/ABI/native-import validation and the full smoke contract could not run
- Verified production identity/health and removed the detached worktree. No candidate image, container, or network remains (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/08-reopen1-cleanup-production.log`)

### Reopen 1 Acceptance Criteria Coverage

- **AC-1: PASS.** Eight-path detached context, base, OCI index, fingerprints, patch checksum, and manifest checksum matched exactly
- **AC-2: FAIL.** The amd64 build failed at the project/workspace sync; no immutable image identity exists
- **AC-3: UNVERIFIED.** Six discovery aliases, exact resources, and exact 401 challenges could not be exercised without an image
- **AC-4: UNVERIFIED.** Authorized initialize/tool behavior and reconnect checks could not run
- **AC-5: UNVERIFIED.** Candidate readiness, `/mcp`, MCP REST, and preservation checks could not run
- **AC-6: PASS.** Production container/image remained identical, running, and healthy; no production secrets/DB/config were used; cleanup completed

### Reopen 1 Documentation Impact

No product or architecture documentation change is required. The failure is in the candidate packaging toolchain rather than application behavior

### Reopen 1 Open Risks

The exact Python pin resolves the original uvloop/Python 3.14 failure, but the authorized Wolfi builder currently installs a Rust/LLVM toolchain whose `libLLVM.so.22.1` requires unavailable `GLIBC_2.44`. Final-image ABI/import behavior and all runtime surfaces remain unverified

### Reopen 1 Recommended Next Step

PMA should route a new bounded packaging investigation and Tech Lead review for the Rust/LLVM/glibc incompatibility. Any builder package, base image, Rust toolchain, or project-build change requires new authorization and newly frozen candidate inputs before TASK-006 is resumed

### Reopen 1 Signed Handoff

[Agent Message] From: qa_engineer To: product_manager

REJECT. The exact eight-path amd64 candidate inputs passed, and Python 3.13.15 plus uvloop 0.21.0 resolved, but the build failed when `rustc` required unavailable `GLIBC_2.44` through `libLLVM.so.22.1`. No final image or runtime smoke exists. Production is unchanged and healthy; detached and runtime artifacts are cleaned

## Reopen 2 Verdict

REJECT. Every TASK-010 base, OCI, platform, path, fingerprint, manifest, patch, parser, Python lock, and Cargo gate matched. The pinned Rust assertions passed, both frozen Python 3.13 syncs passed, and the LiteLLM Maturin/Rust bridge built. The final runtime layer then failed because system `python` could not import generated `prisma` from the copied virtual environment. Docker emitted no final image, so final-image ABI/import validation and runtime smoke could not start

### Reopen 2 Work Performed

- Reconstructed the exact eight-path candidate in a clean detached `/tmp/opencode` worktree and verified all TASK-010 provenance and immutable fingerprints (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/09-reopen2-manifest-provenance.log`)
- Built only `linux/amd64` with `--pull=false`. Rust identity/isolation assertions, dependency sync, Maturin build, and Prisma generation passed
- Observed final runtime validation execute system `python` and fail `from prisma.client import BINARY_PATHS` with `ModuleNotFoundError`, despite Prisma having been generated under `/app/.venv/lib/python3.13/site-packages/prisma` (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/10-reopen2-build.log`)
- Stopped without altering the frozen Dockerfile or any candidate input. No image/container/network was created, and no runtime smoke was attempted
- Verified unchanged production container/image/readiness and removed the detached worktree (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/11-reopen2-cleanup-production.log`)

### Reopen 2 Acceptance Criteria Coverage

- **AC-1: PASS.** Base, both OCI indexes, Rust amd64 manifest, exact eight paths, ordered manifest, both patch checksums, parser, Python metadata/lock, and Cargo metadata/lock matched
- **AC-2: FAIL.** The build reached the final runtime layer but exited 1; no immutable image identity exists
- **AC-3: UNVERIFIED.** Six discovery aliases/resources and exact LazyMCP 401 challenges require a runnable image
- **AC-4: UNVERIFIED.** Authorized initialize/tool behavior and repeated reconnect checks could not run
- **AC-5: UNVERIFIED.** Candidate readiness, `/mcp`, MCP REST, and upstream-preservation smoke could not run
- **AC-6: PASS.** Production identity/readiness remained unchanged; no production secrets/DB/config were used; candidate artifacts and detached worktree were cleaned

### Reopen 2 Documentation Impact

No product or architecture documentation change is required. This is another packaging/runtime-image construction defect, not an application contract change

### Reopen 2 Open Risks

The Rust toolchain correction works through native LiteLLM compilation, but the final runtime validation does not select `/app/.venv/bin/python`. No final-image Python 3.13.15 ABI/SOABI, uvloop, native extension, or Rust bridge import evidence exists, and every isolated protocol/preservation check remains unverified

### Reopen 2 Recommended Next Step

PMA should route a bounded Docker runtime-interpreter investigation and independent authorization. Any `PATH`, `VIRTUAL_ENV`, explicit interpreter, or final validation-line correction changes the frozen Dockerfile and requires a newly frozen manifest before resuming TASK-006

### Reopen 2 Signed Handoff

[Agent Message] From: qa_engineer To: product_manager

REJECT. TASK-010's exact amd64 inputs and Rust assertions passed, and the LiteLLM Rust bridge built, but the final Docker layer used system `python` and failed to import generated `prisma` from `/app/.venv`. No final image or smoke exists. Production remains identical and healthy; cleanup is complete

## Reopen 3 Verdict

REJECT. Every TASK-012 frozen base, OCI, path, fingerprint, manifest, patch, parser, Python lock, and Cargo gate matched. The exact amd64 build selected `/usr/bin/python3.13` and did not download managed CPython, but uv could not inspect that interpreter: its standard-library `math` extension requires `GLIBC_2.44`, unavailable in the authorized immutable Wolfi base. No sync or final image completed, so all final-image and isolated smoke gates remain unverified

### Reopen 3 Work Performed

- Reconstructed the exact eight-path candidate in a clean detached `/tmp/opencode` worktree and verified all TASK-012 provenance and frozen fingerprints (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/12-reopen3-manifest-provenance.log`)
- Built only `linux/amd64` with `--pull=false`; the exact Rust assertion layer passed and uv selected the required `/usr/bin/python3.13`
- Confirmed there was no managed Python download. The first frozen sync failed while importing Python's own `math.cpython-313-x86_64-linux-gnu.so`, which requires unavailable `GLIBC_2.44` (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/13-reopen3-build.log`)
- Stopped without changing the frozen Dockerfile, package set, OCI inputs, or source. No final-image or runtime gate was attempted
- Verified unchanged production identity/readiness and removed the detached worktree; no candidate image/container/network exists (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/14-reopen3-cleanup-production.log`)

### Reopen 3 Acceptance Criteria Coverage

- **AC-1: PASS.** Exact base, OCI provenance, eight paths, manifest, patch/parser checksums, Python lock, Cargo files, and diff checks matched
- **AC-2: FAIL.** The build failed at the first frozen sync; no immutable image identity exists
- **AC-3: UNVERIFIED.** Six discovery aliases/resources and exact LazyMCP 401 challenges require a runnable image
- **AC-4: UNVERIFIED.** Authorized initialize/tool behavior and reconnect checks could not run
- **AC-5: UNVERIFIED.** Final-image linkage/imports, normal entrypoint, readiness, `/mcp`, MCP REST, and upstream preservation could not run
- **AC-6: PASS.** Production remained identical, running, and healthy; no production secrets/DB/config were used; complete cleanup passed

### Reopen 3 Documentation Impact

No product or architecture documentation change is required. The candidate remains blocked by live package/base ABI incompatibility

### Reopen 3 Open Risks

TASK-012 correctly forces system interpreter selection, but current `python-3.13=3.13.15-r4` artifacts are not runnable against the immutable base's glibc. No venv linkage, final ABI/SOABI, uvloop, Prisma, Rust bridge/native imports, normal entrypoint, or protocol/preservation behavior is verified

### Reopen 3 Recommended Next Step

PMA should route a bounded supply-chain/ABI investigation. A compatible immutable Wolfi base or a fully frozen Python package closure may be required; any OCI or package change must be independently reviewed and re-frozen before TASK-006 resumes

### Reopen 3 Signed Handoff

[Agent Message] From: qa_engineer To: product_manager

REJECT. TASK-012's exact inputs matched and `/usr/bin/python3.13` was selected without managed downloads, but that interpreter cannot import its own `math` extension because it requires unavailable `GLIBC_2.44`. No final image or smoke exists. Production remains identical and healthy; cleanup is complete

## Reopen 4 Verdict

REJECT FOR FUNCTIONAL CANDIDATE; PROMOTION BLOCKED. The exact TASK-014 amd64 candidate builds and passes all final-image Python, ABI, glibc, venv linkage, uvloop, Prisma, Rust/native-import, package-inventory, and normal-entrypoint gates. However, all six required LazyMCP discovery aliases return 404, repeated reconnect probes produce 60/60 discovery 404s, and required LazyMCP challenge behavior fails. The candidate therefore does not satisfy AC-3 or AC-4 and cannot proceed. Independently, unavailable signature, aggregate-SBOM, and vulnerability-scan tooling blocks promotion

### Reopen 4 Work Performed

- Reconstructed and built the exact frozen `linux/amd64` candidate; recorded final image `sha256:0ade7608d10588994a73d45ffb1bb66e994966fe71edd640a9599ffca754fcdf` and builder image `sha256:d183ac76440db78f118361aecf29f80a50ea173085ffe3db51e780e80cf0e6df` (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/15-reopen4-manifest-build-image.log`)
- Proved Python 3.13.15, system-linked venv, x86_64 `cpython-313` SOABI, glibc 2.44-r1, uvloop 0.21.0, Prisma engines, LiteLLM Rust bridge and representative native imports; captured builder/final APK and embedded SPDX inventory (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/16-reopen4-final-runtime-packages-security.log`)
- Ran the unchanged normal entrypoint in an isolated read-only container/network with no production mounts. Readiness, `/mcp`, MCP REST, and management tool-list surfaces were present
- Tested all six exact discovery aliases, no-token/invalid-token challenges, and repeated reconnect discovery. Discovery and challenge requirements failed; credential-authorized initialize/tool behavior remained blocked without a DB and was not weakened (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/17-reopen4-smoke.log`)
- Preserved production identity/readiness and removed candidate container/network/worktree; retained immutable candidate/builder images for technical inspection (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/18-reopen4-production-cleanup.log`)

### Reopen 4 Acceptance Criteria Coverage

- **AC-1: PASS.** Exact frozen base, OCI children, path manifest, patches, parser, locks, Cargo, and provenance matched
- **AC-2: PASS.** Candidate and builder images built; immutable image IDs and package inventories are recorded
- **AC-3: FAIL.** All six discovery aliases returned 404 and exact LazyMCP challenges were absent/wrong
- **AC-4: FAIL.** Reconnect produced 60/60 discovery 404s instead of zero. Authorized initialize/tool behavior is separately BLOCKED by the intentionally absent DB/credential
- **AC-5: PARTIAL.** Readiness, `/mcp`, MCP REST, and management tool-list surfaces pass preservation; LazyMCP runtime preservation fails
- **AC-6: PASS.** Production remained identical and healthy; no production secrets/DB/config were used; cleanup passed

### Reopen 4 Documentation Impact

No product or architecture documentation update is warranted for this rejected candidate. Task/evidence records now document the successful packaging correction and independent runtime route regression

### Reopen 4 Open Risks

The OpenAPI schema lists all six discovery paths, but live routing returns 404, indicating registration/routing precedence or middleware behavior diverges from schema generation. Challenges fall through legacy/generic admission and DB-dependent behavior instead of the reviewed LazyMCP challenge contract. Promotion is also blocked until exact-image signature/attestation, aggregate SBOM, and same-database comparative scans receive independent review

### Reopen 4 Recommended Next Step

PMA should route a focused runtime investigation to reproduce why OpenAPI-listed LazyMCP discovery routes return 404 and why transport authentication bypasses the intended challenge builder. Preserve the successful immutable images for review; any source fix requires independent authorization and newly frozen candidate inputs

### Reopen 4 Signed Handoff

[Agent Message] From: qa_engineer To: product_manager

REJECT. Exact amd64 build and final-image packaging gates pass, but all six LazyMCP discovery aliases return 404, reconnects produce 60/60 discovery 404s, and exact challenge behavior fails. Production is unchanged and healthy; runtime artifacts are cleaned, images retained. Promotion additionally remains blocked by unavailable signature/SBOM/scans

## Reopen 5 Verdict

PARTIAL / REJECT FOR CLOSURE. Corrected trusted-base smoke proves the retained image's six discovery aliases, exact resources, selection-header invariance for aggregate/scoped challenges, zero discovery 404 reconnects, readiness, `/mcp`, MCP REST, management listing, and authorized aggregate initialize. However, toolset transport requests fail before admission with HTTP 503 `Database not available`, including no-token and malformed-session cases, so the required exact toolset 401 challenges are not produced. The original full challenge contract is therefore not complete

### Reopen 5 Work Performed

- Verified and reused retained `linux/amd64` image `sha256:0ade7608d10588994a73d45ffb1bb66e994966fe71edd640a9599ffca754fcdf` without rebuild
- Ran the unchanged normal entrypoint in a disposable read-only container/network with prior isolated settings plus only `PROXY_BASE_URL=https://candidate.invalid`
- Proved all six aliases return 200 with exact aggregate/scoped/toolset resources and authorization server `https://candidate.invalid/mcp`; 60 reconnect requests returned 200 with zero discovery 404s (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/19-reopen5-retained-image-discovery.log`)
- Proved exact aggregate and scoped no-token/invalid-token challenges and selection-header invariance. Toolset challenge cases returned 503 without `WWW-Authenticate`, preventing full closure (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/20-reopen5-challenges-protocol.log`)
- Proved readiness, aggregate `/mcp` authorized initialize, MCP REST and management tool-list preservation. Authorized real tool behavior remained blocked by the intentionally absent DB/server authorization (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/21-reopen5-preservation-cleanup.log`)
- Preserved production identity/readiness and removed disposable container/network; retained image remains unchanged

### Reopen 5 Acceptance Criteria Coverage

- **AC-1: PASS by retained provenance.** Exact immutable image identity verified; no rebuild or candidate mutation occurred
- **AC-2: PASS by retained image.** Existing immutable amd64 image remains available and unchanged
- **AC-3: FAIL.** All six discovery aliases/resources pass, but required exact toolset no-token/invalid-token 401 challenges fail with DB-dependent 503
- **AC-4: PARTIAL.** Aggregate initialize passes and reconnect discovery has zero 404s; authorized real tool execution remains BLOCKED by absent DB/credential
- **AC-5: PASS.** Readiness, `/mcp`, MCP REST, management tool-list, and upstream-preservation surfaces pass in the isolated environment
- **AC-6: PASS.** Production remained identical and healthy; no production mounts/secrets/DB used; cleanup completed

### Reopen 5 Documentation Impact

No product or architecture documentation change is required. The corrected smoke confirms the trusted-base contract and isolates the remaining toolset admission-order/DB dependency

### Reopen 5 Open Risks

Toolset LazyMCP transport resolves toolset state before producing the reviewed admission challenge in a database-free runtime. This conflicts with the required all-resource challenge contract even though direct challenge-builder tests pass. Credential-authorized real tool behavior and independent promotion security gates remain blocked

### Reopen 5 Recommended Next Step

PMA should route a focused investigation/review of toolset transport admission ordering. Determine whether anonymous/invalid-token toolset requests must challenge before DB resolution or whether the acceptance contract needs an approved environment prerequisite. Do not promote or deploy this partial result

### Reopen 5 Signed Handoff

[Agent Message] From: qa_engineer To: product_manager

PARTIAL / REJECT FOR CLOSURE. Corrected retained-image smoke passes six discovery aliases, exact reserved resources, aggregate/scoped challenges, selection-header invariance, 60/60 reconnects with zero 404s, readiness and preservation. Toolset no-token/invalid-token requests return DB-dependent 503 without required challenges, so AC-3 remains failed. Production is unchanged and cleanup complete

## Reopen 6 Verdict

PASS FOR CANDIDATE BUILD/ISOLATED SMOKE; PROMOTION BLOCKED. The exact nine-path `linux/amd64` candidate builds as image `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. Packaging, final runtime, all six discovery aliases/resources, aggregate/scoped/toolset challenge variants, selection-header invariance, reconnect, readiness, preservation surfaces, aggregate initialize, and admitted toolset DB-down semantics pass. Authorized real tool execution remains environment-blocked without production DB/credentials. Separate signature/SBOM/scanner gates continue to prohibit promotion or deployment

### Reopen 6 Work Performed

- Reconstructed the exact frozen nine-path candidate including `server.py`; verified base, manifest, both patches, parser, locks, Cargo and OCI provenance before building (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/22-reopen6-manifest-build-runtime.log`)
- Built only `linux/amd64`; validated Python 3.13.15 system venv, ABI/SOABI, glibc 2.44-r1, uvloop 0.21.0, Prisma engines, Rust bridge/native imports, normal entrypoint and embedded SPDX inventory
- Ran the normal entrypoint in an isolated read-only network/container with `PROXY_BASE_URL=https://candidate.invalid` and an isolated non-production key
- Passed all discovery/challenge/reconnect/preservation gates, aggregate initialize, and explicit toolset admitted DB-down behavior (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/23-reopen6-smoke.log`)
- Preserved production identity/readiness and removed disposable container/network/worktree; retained immutable candidate image for review (`.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/24-reopen6-cleanup-promotion.log`)

### Reopen 6 Acceptance Criteria Coverage

- **AC-1: PASS.** Exact authorized base, nine paths, fingerprints, manifest, patches, parser, locks, Cargo and OCI inputs matched
- **AC-2: PASS.** Candidate built and immutable amd64 image identity is recorded
- **AC-3: PASS.** Six discovery aliases/resources and all aggregate/scoped/toolset no-token/invalid-token/selection-header challenges are exact
- **AC-4: PASS WITH ENVIRONMENT BLOCK.** Aggregate initialize and reconnect zero-404 gates pass; admitted toolset DB-down semantics pass; real authorized tool execution is BLOCKED without DB/server credentials
- **AC-5: PASS.** Readiness, `/mcp`, MCP REST, management listing and upstream-preservation surfaces pass
- **AC-6: PASS.** Production remained identical and healthy; no production secrets/DB/config were used; cleanup passed

### Reopen 6 Documentation Impact

No product or architecture documentation change is required. Existing architecture and security contracts match the verified candidate behavior

### Reopen 6 Open Risks

Candidate promotion remains fail-closed pending exact OCI signature/attestation verification, aggregate exact-image SBOM, comparative same-database vulnerability scans, and independent Critical/High disposition. A real authorized upstream tool call remains unverified in the intentionally database-free environment

### Reopen 6 Recommended Next Step

Return image `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e` and this packet for final technical review. Do not promote, publish, or deploy until separate security promotion gates pass

### Reopen 6 Signed Handoff

[Agent Message] From: qa_engineer To: product_manager

PASS FOR BUILD/ISOLATED SMOKE; PROMOTION BLOCKED. Exact nine-path amd64 image `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e` passes packaging, all discovery/challenge/reconnect/preservation gates, aggregate initialize and admitted toolset DB-down semantics. Real tool execution remains environment-blocked; promotion security evidence remains missing. Production is unchanged and cleanup complete
