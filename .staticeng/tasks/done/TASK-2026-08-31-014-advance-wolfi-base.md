---
id: TASK-2026-08-31-014-advance-wolfi-base
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: Advance coherent Wolfi base

## Objective

Review and implement an atomic Dockerfile-only advancement of both Wolfi build/runtime defaults to the coherent glibc 2.44 base recommended by TASK-013.

## Acceptance Criteria

- [ ] AC-1: Tech Lead independently verifies TASK-013 OCI index/platform provenance, Python package ABI evidence, security implications, and rollback.
- [ ] AC-2: Root Dockerfile alone changes both Wolfi base defaults to the exact approved digest; no other mutation is made.
- [ ] AC-3: Disposable amd64 checks prove glibc/loader/Python 3.13.15/math/SOABI compatibility; arm64 remains unauthorized without native validation.
- [ ] AC-4: Python/Rust pins, locks, Cargo, source/tests, entrypoints, deployment, and production remain unchanged.
- [ ] AC-5: New eight-path fingerprints/manifest/combined patch and OCI provenance are independently reviewed before TASK-006 resumes.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Review TASK-013 fully and independently verify the proposed Wolfi OCI index plus amd64/arm64 manifests and ABI/security evidence. Do not edit Dockerfile. Approve/reject only an atomic change of both existing Wolfi base defaults to the exact reviewed digest, and define Developer evidence and re-freeze requirements. Deployment and arm64 remain unauthorized.

## Implementation Handoff

[Agent Message] From: product_manager To: developer

Implement only the exact Tech Lead-approved atomic change of both root Dockerfile Wolfi base defaults to OCI index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`. Do not change any other Dockerfile line or file. Produce required ABI/provenance/SBOM/scan/fingerprint/re-freeze evidence where tools are available; report unavailable gates honestly. Do not resume TASK-006, deploy, touch production, commit, push, or build arm64.

# Post Implementation Task Updates

## Tech Lead: Post Review Expectations

### Summary

APPROVED for the exact bounded implementation, not for promotion. Independently resolving `cgr.dev/chainguard/wolfi-base@sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d` returned OCI index media type and exactly the reviewed `linux/amd64` child `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd` plus `linux/arm64` child `sha256:fce2a4534bdae72009371dab1c87d322f255b40daff82b857e98c4a0890b361e`. A native amd64 pull selected config/image ID `sha256:a7b2e90a205a20887d43148b4509171ac7f321cf9812e3bc3154a88e6775d140`, architecture `amd64`, creation time `2026-08-30T18:47:32Z`, and Chainguard source/vendor labels

The exact current working-tree `Dockerfile` still uses old index `sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f` for both defaults at lines 4 and 7. Its current SHA-256 is `ab60e645a484ac96b3d43fa23575b9f6aed30f39799bb17e28d1b54dfbe17fbc`. The file already contains the governed TASK-010/TASK-012 candidate changes relative to `HEAD`; this review made no implementation edit. Therefore the Developer must edit those two existing argument values only, in one patch, and preserve every other byte of the pre-edit working-tree Dockerfile

### Work Performed

- Read TASK-013 in full, the TASK-014 frontmatter and acceptance criteria, repository guidance, and exact 169-line working-tree `Dockerfile`
- Independently resolved both old and proposed OCI indexes. The old index still maps amd64 to `sha256:85ecaa3f494ee2339eaf6f74a23f19f934df3019a9a9dfc8c06f53c3aacc4e6b` and arm64 to `sha256:1391b1e3093efd59124d88b3e7389d9e0d6df7a004ec65bf7d9fee22c28d1542`; the replacement mappings match TASK-013 exactly
- Pulled and ran the replacement by index digest with native `linux/amd64`. Before package installation it contained `glibc-2.44-2.44-r1`, `glibc-2.44-locale-posix-2.44-r1`, and `ld-linux-2.44-2.44-r1`
- Installed exact `python-3.13=3.13.15-r4` and `python-3.13-dev=3.13.15-r4` from the signed configured APK repository. APK selected all four Python packages at `3.13.15-r4`; Python executed `import math`, reported 3.13.15, x86_64, `cpython-313`, and `cpython-313-x86_64-linux-gnu`; the loader reported glibc 2.44-r1
- Inspected the installed amd64 math extension with `readelf --version-info` and independently observed a `GLIBC_2.44` requirement. Repeating exact Python r4 installation and `import math` on the old digest failed with `libm.so.6: version 'GLIBC_2.44' not found`, confirming the causal ABI boundary
- Reviewed security and rollback implications. The digest and vendor/source labels establish immutable identity and provenance context, not trust or vulnerability clearance. The host lacks Cosign and an image scanner, so signature/SBOM/CVE policy evidence remains a mandatory Developer/promotion gate rather than an unverified PASS here

### Approval And Exact Constraints

The Developer is authorized to replace only these two complete defaults, atomically:

```diff
-ARG LITELLM_BUILD_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f
+ARG LITELLM_BUILD_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d
@@
-ARG LITELLM_RUNTIME_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f
+ARG LITELLM_RUNTIME_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d
```

Reject and stop on any third changed line or any change to Python/Rust/uv/UI pins, APK lists, locks, Cargo, source, tests, alternate Dockerfiles, entrypoints, deployment, or production. Do not substitute either platform child digest into the two defaults; the approved default is the reviewed multi-platform index digest, while execution authorization remains amd64-only. Do not treat OCI metadata inspection as arm64 runtime evidence

### Required Developer Evidence

1. Record the pre-edit Dockerfile SHA-256 `ab60e645a484ac96b3d43fa23575b9f6aed30f39799bb17e28d1b54dfbe17fbc`, apply the two substitutions, and retain a zero-context/root-Dockerfile diff proving exactly two removed and two added lines with no other mutation
2. Re-resolve the approved index immediately before build and record index media type, digest, exact amd64 child, and exact arm64 child. Require the amd64 build to resolve child `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd`; reject the old index and child anywhere in effective `FROM` inputs
3. Before full build, repeat native amd64 checks for glibc, locale, loader `2.44-r1`; all four Python packages `3.13.15-r4`; Python 3.13.15; x86_64; `cpython-313`; SOABI `cpython-313-x86_64-linux-gnu`; `import math`; and math's `GLIBC_2.44` version need. Record APK package checksums and signed-index identity at execution time
4. Verify Chainguard signature/attestation for the exact index and amd64 child with a checksum-pinned trusted Cosign installation and Chainguard's documented identity/issuer policy. Retrieve or generate exact-digest SBOMs and scan old base, new base, builder, and final runtime under the same current database. Record Critical/High comparison and policy disposition; no blanket ignores
5. Record builder and final installed-package manifests and SBOMs. Require builder/runtime glibc and Python parity, then execute TASK-013's copied-ELF, venv, native-import, Prisma, Rust bridge, entrypoint, and application gates. Rolling APK resolution remains non-reproducible unless exact signed indexes and artifacts are retained or foundation images are published by digest
6. Record rollback evidence as a clean reversal of only the two substitutions to this reviewed pre-edit Dockerfile fingerprint. Deployment remains unauthorized; if later authorized, separately capture the then-current immutable production manifest before deployment rather than assuming TASK-013's observed production digest is still current

### Re-freeze Requirements

Recompute all eight ordered TASK-012 path SHA-256 fingerprints after the edit. Seven path fingerprints must equal TASK-012 exactly; only root `Dockerfile` may differ. Recompute and retain the ordered manifest checksum and combined tracked patch checksum. The application-only patch checksum, Git base, `pyproject.toml`, `uv.lock`, Cargo inputs, and all Rust/uv/UI OCI identities must remain frozen. Independently review the exact post-edit Dockerfile, the two-line semantic diff, all eight fingerprints, the ordered manifest, combined patch, OCI provenance, APK checksums, SBOMs, and scan results before TASK-006 resumes

### Acceptance Criteria Coverage

- **AC-1: PASS.** OCI index/platform mappings, amd64 image config, Python ABI cause, security limitations, and rollback were independently verified
- **AC-2: APPROVED, pending Developer implementation evidence.** Exact two-default root-Dockerfile-only advancement is authorized; no implementation was made during review
- **AC-3: PARTIAL by design.** Disposable native amd64 glibc/loader/Python/math/SOABI checks pass. Arm64 remains metadata-only and unauthorized pending native validation
- **AC-4: PASS for review baseline.** Exact current working tree was inspected and the no-mutation boundary is explicit; Developer must prove it after edit
- **AC-5: PENDING.** Developer must produce and submit the new eight-path freeze, manifest, combined patch, and exact OCI/security evidence for independent review

### Documentation Impact

No product or steady-state architecture documentation change is required for this bounded review. The task record contains the authorization, constraints, security evidence requirements, and rollback. A maintained immutable APK snapshot or foundation-image mechanism still requires separate architecture and operational documentation

### Open Risks

The replacement index fixes the demonstrated ABI mismatch but does not freeze Wolfi's rolling APK transactions. Unversioned direct and transitive packages can drift, and retained Python r4 artifacts can disappear. No full candidate image has yet passed copied-native, application, or security policy gates. Cosign verification and comparative vulnerability scanning were unavailable on this host and cannot be inferred from digest pinning. Arm64 has no native execution proof. Repository validation still fails on the known pre-existing missing CodeMap inventory; `staticeng_repair` dry-run reports those module-boundary cases as unresolved and no unrelated repair was applied

### Recommended Next Step

PMA should hand this exact approved two-default edit to the Developer. After Developer evidence and re-freeze are complete, return TASK-014 to Tech Lead for exact-diff and evidence review. Resume TASK-006 only after that PASS, on amd64 only. Keep deployment, production mutation, arm64 promotion, and reproducibility claims unauthorized

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

APPROVED only the atomic replacement of both existing Wolfi defaults with OCI index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`. Independent resolution confirms amd64 child `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd`, metadata-only arm64 child `sha256:fce2a4534bdae72009371dab1c87d322f255b40daff82b857e98c4a0890b361e`, embedded glibc/loader 2.44-r1, and native amd64 Python 3.13.15-r4 math/SOABI compatibility. The old digest independently reproduces the `GLIBC_2.44` import failure. Developer must change exactly two defaults, preserve all other bytes and frozen inputs, provide signature/SBOM/CVE and package/ABI evidence, and re-freeze the eight-path manifest and combined patch. TASK-006, deployment, production, and arm64 remain unauthorized pending independent review

## Developer: Post Implementation Expectations

### Summary

[Agent Message] From: developer To: product_manager

Implemented exactly both approved root `Dockerfile` Wolfi default substitutions. Post-edit Dockerfile SHA-256 is `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`. No TASK-006 full build/smoke, arm64 execution, deployment, production action, commit, or push was performed

### Work Performed

Produced the exact semantic diff and rollback proof, immediate OCI index/platform resolution, native amd64 glibc/Python ABI checks, signed APK repository/key and package artifact checksums, embedded package SPDX evidence, replacement eight-path freeze, and replacement combined patch under `.staticeng/evidences/TASK-2026-08-31-014-advance-wolfi-base/`. Recorded Cosign, aggregate SBOM, and comparative scanner gates as unavailable rather than passing them

### Acceptance Criteria Coverage

- **AC-1: PASS.** Implemented under the exact Tech Lead approval and re-resolved the approved OCI identity
- **AC-2: PASS.** Exactly the two root Dockerfile defaults changed to the approved index; reversal reproduces pre-edit SHA-256 `ab60e645a484ac96b3d43fa23575b9f6aed30f39799bb17e28d1b54dfbe17fbc`
- **AC-3: PASS FOR AUTHORIZED AMD64 PREFLIGHT.** Native amd64 proves glibc/locale/loader `2.44-r1`, Python closure `3.13.15-r4`, Python 3.13.15, x86_64, cache tag, SOABI, math import, and math's `GLIBC_2.44` requirement. Arm64 remains metadata-only and unauthorized
- **AC-4: PASS.** Seven path fingerprints, application patch, Git base, Python/Rust locks and metadata, Cargo, and uv/Rust/UI identities remain frozen
- **AC-5: READY FOR TECH LEAD REVIEW.** Ordered manifest SHA-256 is `f7def12e07e90dbfe2a27651eab73617660191efeab7b97e7d200fc01ebd5e13`; combined tracked patch SHA-256 is `501797e94d980f1ed7f1293d4fe57adea61237f9107f0f0025a5a00d6bbd2751`

### Documentation Impact

No product, architecture, operator, or CodeMap documentation change is required. The task and evidence packet record the bounded foundation pin and unresolved promotion gates

### Open Risks

Cosign is unavailable, and no aggregate SBOM or comparative Critical/High scan could be produced because Syft, Grype, Trivy, Docker SBOM, and Docker Scout are unavailable. Embedded per-package SPDX material was recorded but does not clear security policy. Rolling APK resolution remains non-reproducible. Builder/final package manifests, parity, complete build, native imports, entrypoint, and smoke remain TASK-006 gates. Arm64 and promotion remain unauthorized

Repository `staticeng_validate` remains blocked by the known pre-existing missing-CodeMap inventory. TASK-014 adds no navigable source and no unrelated repair was applied

### Recommended Next Step

Route TASK-014 to Tech Lead for independent exact-diff, fingerprint, provenance, ABI, SBOM availability, and policy review. Do not resume TASK-006 until that review passes

## Tech Lead Post-Implementation Review

### Summary

[Agent Message] From: tech_lead To: product_manager

Verdict: PASS. No blocking implementation finding remains. The current root `Dockerfile` differs from the authorized pre-edit working-tree file on exactly lines 4 and 7, and both lines atomically replace the old Wolfi index with approved index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`. Reversing only those substitutions exactly reconstructs pre-edit SHA-256 `ab60e645a484ac96b3d43fa23575b9f6aed30f39799bb17e28d1b54dfbe17fbc`; current SHA-256 independently recomputes to `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`

TASK-014 is technically complete and TASK-006 Reopen 4 is authorized for isolated `linux/amd64` candidate construction and smoke only. Unavailable Cosign, aggregate SBOM, and vulnerability scanners do not block building the candidate because builder/final evidence cannot exist before that build. They remain fail-closed promotion gates and prohibit release approval, deployment, or production mutation until completed and reviewed

### Work Performed

Independently recomputed all eight path fingerprints, ordered manifest SHA-256 `f7def12e07e90dbfe2a27651eab73617660191efeab7b97e7d200fc01ebd5e13`, unchanged six-application-path patch SHA-256 `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`, and Dockerfile-plus-six-path patch SHA-256 `501797e94d980f1ed7f1293d4fe57adea61237f9107f0f0025a5a00d6bbd2751` from exact Git base `9af49e5b34e25cdc9ad40f9bb50a178f40320417`. Every value matches Developer evidence

Independently recomputed `pyproject.toml`, `uv.lock`, `litellm-rust/Cargo.toml`, and `litellm-rust/Cargo.lock`; fingerprints match and their working-tree diffs are empty. The seven non-Dockerfile candidate fingerprints and untracked parser fingerprint remain unchanged. Inspection confirms no TASK-014 mutation to Python/Rust pins, APK lists, source/tests, alternate Dockerfiles, entrypoints, deployment, or production

Re-resolved the replacement OCI index and exact platform mapping: amd64 child `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd`, arm64 metadata-only child `sha256:fce2a4534bdae72009371dab1c87d322f255b40daff82b857e98c4a0890b361e`, and native amd64 config/image ID `sha256:a7b2e90a205a20887d43148b4509171ac7f321cf9812e3bc3154a88e6775d140`. Preserved uv, Rust, and UI indexes and amd64 children were independently resolved

Repeated the native amd64 package/ABI probe. Exact Python `3.13.15-r4` runtime/development installation selected all four r4 packages; Python 3.13.15, x86_64, `cpython-313`, SOABI `cpython-313-x86_64-linux-gnu`, `import math`, the math extension's `GLIBC_2.44` need, and loader glibc 2.44-r1 all pass. Independent results are retained in `.staticeng/evidences/TASK-2026-08-31-014-advance-wolfi-base/logs/06-tech-lead-independent-review.log`

### Security-Gate Disposition

Cosign, Syft, Grype, Trivy, Docker Scout, and Docker SBOM are unavailable on this host. The available signed APK transaction, key fingerprints, package artifact hashes, embedded SPDX documents, immutable OCI identity, and native ABI execution are sufficient to authorize a disposable candidate build/smoke, but do not establish release trust or vulnerability-policy compliance

TASK-006 Reopen 4 must record immutable builder/final identities, installed-package manifests, builder/runtime parity, and all available embedded SBOM material. Before promotion, checksum-pinned trusted tooling must verify Chainguard signature/attestation for the exact index and amd64 child, generate aggregate exact-image SBOMs, and run old-base/new-base/builder/final scans with one current database. Critical/High findings require explicit policy disposition without blanket ignores. Failure or continued unavailability blocks promotion, publication as approved release, deployment, and production mutation, but does not retroactively invalidate isolated smoke evidence

### Acceptance Criteria Coverage

- **AC-1: PASS.** OCI provenance, native ABI cause/correction, security boundary, and rollback are independently verified
- **AC-2: PASS.** Reconstruction proves exactly the two approved root-Dockerfile substitutions and no third implementation mutation
- **AC-3: PASS FOR TASK-014 SCOPE.** Disposable native amd64 compatibility passes; arm64 remains metadata-only and unauthorized
- **AC-4: PASS.** Python/Rust pins, locks, Cargo, source/tests, entrypoints, deployment, and production are preserved
- **AC-5: PASS.** Eight-path fingerprints, ordered manifest, application/combined patches, supplementary fingerprints, and OCI provenance are independently recomputed and frozen

### Documentation Impact

No product, architecture, operator, or CodeMap documentation change is required for this bounded base advancement. The task and evidence packet document exact build authorization and the security promotion boundary. A maintained immutable APK snapshot/foundation-image mechanism remains separate architecture work

### Open Risks

TASK-014 proves base/package ABI preflight and exact frozen source inputs, not a successful full image. Wolfi APK transactions remain rolling beyond direct Python pins. Complete sync, copied ELF/native extensions, Rust bridge, Prisma, final runtime, normal entrypoint, LazyMCP behavior, and cleanup remain TASK-006 Reopen 4 gates. Arm64 remains unauthorized. Repository `staticeng_validate` remains blocked by the known pre-existing missing-CodeMap inventory

### TASK-006 Reopen 4 Frozen Authorization

[Agent Message] From: tech_lead To: qa_engineer

Authorize TASK-006 Reopen 4 candidate construction and isolated smoke only for `linux/amd64`, from exact Git base `9af49e5b34e25cdc9ad40f9bb50a178f40320417`. Use Wolfi build/runtime OCI index `cgr.dev/chainguard/wolfi-base@sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d` and require amd64 child `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd`. Arm64 child `sha256:fce2a4534bdae72009371dab1c87d322f255b40daff82b857e98c4a0890b361e` is provenance only and authorizes no arm64 execution or promotion

Use uv index `ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a` with amd64 child `sha256:733b4042187702f832f7fdecb3aff14a61b288c4ca37af188bb5715c1caebaf8`; Rust index `docker.io/library/rust:1.97.1-slim-bookworm@sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3` with amd64 child `sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b`; and UI index `docker.io/library/node:24.19-alpine3.24@sha256:d32cdf619f63fe0471182d08996dd516c6275bb5fd31ae06e55a570bd9e1ad43` with amd64 child `sha256:2a49bdf71e9fd965a58c1703fd9ddd205b34e5782b692a72dd1d248abb0beb43`

Construct a clean detached worktree under `/tmp/opencode` containing exactly this ordered eight-path candidate:

```text
9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d  Dockerfile
1aa2a86213d076d2e1addc751e0b3ea9660e8c8cd4a9e86cb00144b0ff34f723  gateway/routes/allowlist.py
440044fcf74a5afc8d35f94f8bad5b71e1702f8b7227933757c0f848f2bc858b  litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py
5e1ff87728492396a609c886c124fb639624b58f4d21f105ba53853ce1e10fd4  litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py
1a0cf095cf037b32461b17301adea1f95b5dd62d111a45ae924a818da98b2967  litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py
2eec9a86b1fe514faebc64356842cca1901ba648185b9e49d4e91e13f122ec9f  litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py
886d5b443d75e6477bd8f609543bdf0160f9105ce71c137f7f6426791f0d308f  litellm/proxy/proxy_server.py
b02dd1675f11cbdd16450560dcc3e2ccb57170adea0b4471fa6198a44cc11462  litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py
```

Require ordered manifest SHA-256 `f7def12e07e90dbfe2a27651eab73617660191efeab7b97e7d200fc01ebd5e13`, combined tracked patch SHA-256 `501797e94d980f1ed7f1293d4fe57adea61237f9107f0f0025a5a00d6bbd2751`, unchanged application-only patch SHA-256 `6d063a7429514d8600a8fbec9c6847f249e20961481fdbad949d41196767f557`, and the supplementary fingerprints recorded above. Abort on any base, path, fingerprint, patch, manifest, OCI index/child, package, interpreter, ABI, or provenance mismatch

Build only `linux/amd64` with `--pull=false`. Before sync, prove glibc/locale/loader `2.44-r1`, all four Python packages `3.13.15-r4`, Python 3.13.15, x86_64, `cpython-313`, SOABI `cpython-313-x86_64-linux-gnu`, `import math`, and math's `GLIBC_2.44` need. Require both frozen uv syncs to select `/usr/bin/python3.13` without managed Python download, Rust assertions/Maturin bridge, Prisma generation, and the explicit venv assertion

Retain builder and final installed-package manifests, embedded SPDX inventory, and immutable candidate identity. In the final image prove copied-ELF resolution, `/app/.venv/bin/python` executable/prefix/base-prefix/SOABI linkage, Prisma, uvloop 0.21.0, LiteLLM, Rust bridge imports, Prisma engine paths, venv-first PATH, absent `VIRTUAL_ENV`, unchanged Prisma environment, and unchanged `ENTRYPOINT`/`CMD`

Run the normal entrypoint in TASK-006's isolated secret-free environment and complete every original readiness, six discovery alias/resource, exact challenge, safely available initialize/tool, reconnect/zero-404, `/mcp`, MCP REST, upstream preservation, production identity/readiness invariant, and cleanup gate. Credential-bound checks remain blocked rather than weakened; any required failure remains failure

Cosign/aggregate-SBOM/comparative-scanner absence does not block this isolated build/smoke. It does block promotion. No candidate may be promoted, published as an approved release, deployed, or used to mutate production until exact Wolfi index/amd64 signature and attestation are verified and old-base/new-base/builder/final aggregate SBOM plus same-database Critical/High scan results receive independent policy review. This authorization does not permit deployment, production credentials/databases, data/configuration mutation, arm64, commit, or push

### Recommended Next Step

PMA should mark TASK-014 technically reviewed and reopen TASK-006 as Reopen 4 with the exact frozen authorization above. Return the immutable amd64 candidate identity, complete build/smoke logs, installed-package manifests, and security-gate status for technical review before any promotion decision

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-014 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
