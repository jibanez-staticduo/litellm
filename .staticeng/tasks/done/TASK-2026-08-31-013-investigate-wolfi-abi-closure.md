---
id: TASK-2026-08-31-013-investigate-wolfi-abi-closure
complexity: complex
track: investigation
slice: foundation
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Investigate Wolfi ABI package closure

## Objective

Determine a coherent immutable build/runtime package closure for Python 3.13.15 and required native dependencies after live Wolfi packages proved incompatible with the digest-pinned glibc 2.43 base.

## Acceptance Criteria

- [x] AC-1: Trace the exact glibc requirements and provenance of Python 3.13.15-r4 and all copied native artifacts against current and candidate Wolfi bases.
- [x] AC-2: Identify a coherent digest-pinned Wolfi build/runtime image pair or exact repository snapshot where Python, glibc, and native packages are ABI-compatible.
- [x] AC-3: Compare base-image advancement, complete APK closure pinning/snapshotting, official Python base migration, and reuse of the production image contract.
- [x] AC-4: Recommend one deterministic correction with exact OCI digests/platform scope, Dockerfile/build-arg changes, security implications, tests, rollback, and manifest impact.
- [x] AC-5: Preserve application behavior and update this task with signed evidence; no source/Dockerfile/image/production/deployment mutations.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Read all TASK-006 build failures plus TASK-007 through TASK-012. Inspect exact Wolfi base/index/package provenance and current production image ancestry without secrets. Prefer a coherent immutable base/package snapshot over mixing immutable base libraries with live APK packages. Consider whether the repository's currently configured Wolfi digest is stale and whether advancing both build/runtime base args to one reviewed index resolves Python and package ABI consistently. Research only, update task fully, and return an authorization-ready recommendation.

# Post Implementation Task Updates

## Technical Architect: Post Investigation Expectations

### Summary

PASS for investigation. TASK-006 Reopen 3 confirms the root cause anticipated by TASK-009: the repository combines an immutable Wolfi filesystem with a later live APK package set. The configured Wolfi OCI index contains `glibc-2.43-r10`, but retained `python-3.13-base=3.13.15-r4` contains a `math` extension that directly requires `GLIBC_2.44` on both x86_64 and aarch64. APK metadata records only the `libm.so.6` SONAME, so resolution succeeds and interpreter execution fails

The reviewed correction is to advance both `LITELLM_BUILD_IMAGE` and `LITELLM_RUNTIME_IMAGE` together to the same immutable Wolfi OCI index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`. That index embeds the coherent glibc 2.44 family and has exact child manifests `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd` for `linux/amd64` and `sha256:fce2a4534bdae72009371dab1c87d322f255b40daff82b857e98c4a0890b361e` for `linux/arm64`. A native amd64 read-only probe installed the already pinned Python `3.13.15-r4` runtime/development packages on that exact index and successfully imported `math`, reporting CPython 3.13.15 and `cpython-313-x86_64-linux-gnu`

This is the smallest coherent ABI correction, but the distinction between ABI coherence and rebuild immutability is important. Advancing the base eliminates the demonstrated ABI mismatch. It does not by itself freeze unversioned `bash`, GCC, OpenSSL, Node, npm, libsndfile, tzdata, or their transitive APK closure. Tech Lead may authorize the bounded candidate correction now, but release-grade reproducibility requires retaining the resolved APK artifacts and signed index bytes in an immutable internal snapshot or publishing reviewed build/runtime foundation images by digest. A version pin against Wolfi's rolling repository is retention-dependent and is not an immutable repository snapshot

### Work Performed

- Read TASK-006's initial build and Reopens 1 through 3, TASK-007 through TASK-012, their evidence summaries, and the raw Reopen 3 ABI failure. No prior runtime-smoke result was reused as success
- Re-resolved the configured Wolfi index `sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f`: amd64 child `sha256:85ecaa3f494ee2339eaf6f74a23f19f934df3019a9a9dfc8c06f53c3aacc4e6b`, arm64 child `sha256:1391b1e3093efd59124d88b3e7389d9e0d6df7a004ec65bf7d9fee22c28d1542`, with installed amd64 `glibc-2.43-r10`, `glibc-locale-posix-2.43-r10`, and `ld-linux-2.43-r10`
- Re-resolved the reviewed replacement index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d` and its two platform manifests. Both platform configs were created `2026-08-30T18:47:32Z`. The amd64 config is `sha256:a7b2e90a205a20887d43148b4509171ac7f321cf9812e3bc3154a88e6775d140`; the arm64 config is `sha256:d9ddf07ef939c7a0781d2ac48082beb9d70a8a6eb449288f0918cdcf59311f46`
- Inspected the replacement filesystems without changing the repository. Both embed `glibc-2.44=2.44-r1`, `glibc-2.44-locale-posix=2.44-r1`, `ld-linux-2.44=2.44-r1`, `apk-tools=2.14.10-r13`, and `wolfi-baselayout=20230201-r29`
- Downloaded retained Python package artifacts read-only and inspected ELF version requirements. `python-3.13-base=3.13.15-r4` `math` requires `GLIBC_2.44` on both architectures. The preceding `3.13.15-r1` artifacts require at most `GLIBC_2.38`; this explains why the healthy production image can run Python 3.13.15 on glibc 2.43 while the corrected candidate cannot use r4 on the old base
- Ran one disposable native amd64 probe from the replacement digest. Installing `python-3.13=3.13.15-r4` and `python-3.13-dev=3.13.15-r4` selected the complete r4 Python family while retaining the embedded glibc 2.44 family; `import math` passed and reported the expected version, cache tag, and SOABI. The pulled probe image was removed after inspection
- Inspected the unchanged production image without secrets. Image ID `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`, registry manifest `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, and label version `task-20260827-008-64a3b83bf0` use glibc 2.43 with Python `3.13.15-r1`. Its venv imports `math`, Prisma, uvloop 0.21.0, and the LiteLLM Rust bridge and reports `cpython-313-x86_64-linux-gnu`. This is valid ancestry evidence, not a source candidate or deploy authorization

### Exact ABI And Provenance Trace

The copied runtime-native surface is broader than Python itself. The builder creates `/app/.venv`, Maturin builds `litellm.rust_bridge._native`, and uv installs CPython-specific/native wheels including uvloop. Prisma engines and the Node-based CLI are copied under `/opt/prisma`; runtime additionally installs Node and libsndfile. Every copied ELF object inherits the builder's libc floor, so builder and runtime must use one platform, one libc family, and the same exact Python package revision. The existing digest equality satisfies the stage-ancestry rule but fails the package-epoch rule because live r4 Python was built after that digest's glibc 2.43 epoch

Exact Python artifact provenance from the signed rolling indexes at investigation time:

| Artifact | x86_64 APK checksum | aarch64 APK checksum | Exact dependency |
| --- | --- | --- | --- |
| `python-3.13=3.13.15-r4` | `Q1D/li6YCvrplSh51sM7tU+Gbouos=` | `Q1x6Ye3uk9RCK65Kr6NUqUkoxdtXI=` | matching `python-3.13-base` |
| `python-3.13-base=3.13.15-r4` | `Q1pj8MtLqQALa+pjWvUlyCL61Qut4=` | `Q16eKRSBBBudL6uuBAVkYvhF+al9Y=` | platform SONAME closure |
| `python-3.13-dev=3.13.15-r4` | `Q1YranbnwNSiQNIJh+8+TT2z1ZW4k=` | `Q1acI+pFI21Y/JMJ1q896sK5zgqwY=` | matching base-dev and runtime |
| `python-3.13-base-dev=3.13.15-r4` | `Q1FaOZRF+XBJf8sETFFDLRoQ5CXS4=` | `Q1bWS0J8Ei+NOIhzNaHoJ9V+UvGDM=` | matching runtime and libpython |

These checksums prove the exact artifacts inspected, but Wolfi's public rolling index URL is not a historical snapshot contract. The observed compressed index hashes are time-scoped evidence only and must not be used as future authorization because the x86_64 and aarch64 index bytes can change independently. Any implementation must re-resolve the four exact packages and compare their APK checksums above, or consume a newly published immutable snapshot/foundation-image digest

### Options Considered

1. **Advance both Wolfi bases together: RECOMMEND for TASK-006 Reopen 4.** Change only the two root `Dockerfile` default base arguments to index `sha256:57108e...735d`. It directly supplies the required glibc 2.44 family, preserves APK semantics, Python 3.13.15-r4, Rust isolation, uv/venv fixes, runtime layout, and application behavior. It is the smallest correction with an exact reviewed amd64 proof
2. **Complete APK closure pinning/snapshotting: RECOMMEND as the release-hardening follow-up, not as an improvised Dockerfile pin list.** Resolve builder and runtime transactions per architecture, retain every `.apk` plus signed `APKINDEX` and keys in an immutable internal OCI artifact/repository snapshot, then publish separate reviewed foundation images by digest. Pinning only direct versions against the rolling public repository is insufficient because transitive packages, repository retention, and index bytes remain mutable
3. **Official Python base migration: REJECT for this candidate.** Official `python:3.13.15-slim-bookworm` currently resolves to index `sha256:c45a22ea000adfd9cda29364bbe7edd23001ce5cc2ad15857cfbf7766943b9ca` with relevant amd64 child `sha256:b6bd71b0dd3811ddbcbc523ec2965fd1e1bcfdf7a20ab24679273d3bee726129` and arm64 child `sha256:e424b523c9296fdef9d2533c368facee1dc45be4c1f8e1555f90c4feac439594`. Migration would replace APK with apt, translate all native packages, revisit the copied venv/base-prefix contract, and revalidate security/nonroot behavior. It is a separate architecture change, not a bounded ABI repair
4. **Reuse the production image contract: REJECT as a build base; retain as rollback/baseline.** Production proves the older coherent pairing `glibc-2.43-r10` plus Python `3.13.15-r1`, but the image is an application runtime with deployed artifacts, not a reviewed clean builder/runtime foundation. Pinning retained r1 Python could make the old base work but relies on public repository retention and regresses from reviewed r4 package content. Deriving a new candidate from production also obscures source/build provenance

### Authorization-Ready Correction

Authorize a root-`Dockerfile`-only implementation that replaces both existing defaults, atomically:

```diff
-ARG LITELLM_BUILD_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f
+ARG LITELLM_BUILD_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d
@@
-ARG LITELLM_RUNTIME_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f
+ARG LITELLM_RUNTIME_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d
```

Do not alter Python r4 pins, the Rust/uv/UI image digests, uv selectors, venv assertion, locks, Cargo files, source, tests, alternate Dockerfiles, runtime environment, entrypoint, deployment, or production. Re-freeze the existing ordered eight-path candidate with only the root Dockerfile fingerprint changed. Bind the new Wolfi index and amd64 child manifest into authorization. Keep `linux/arm64` metadata-only and unauthorized until native build/runtime validation; the amd64 correction must not imply multi-platform release readiness

For stronger supply-chain closure, the implementation evidence must record `apk list --installed` and an SBOM for builder and final runtime, compare exact Python package checksums, and fail if either stage does not contain the same Python r4 runtime plus glibc/loader 2.44-r1. This detects transaction drift for this candidate. It does not substitute for the separately recommended immutable APK snapshot/foundation images

### Required Tests And Manifest Impact

1. Re-resolve the new OCI index and require the exact amd64 child. Verify the old index and old child cannot enter any `FROM`. Verify exact Python APK checksums before build. Abort on any digest, platform, package checksum, manifest, path, lock, Cargo, Rust, uv, or patch drift
2. Build only `linux/amd64` with `--pull=false`. Before the first sync require installed glibc/locale/loader `2.44-r1`, all four Python packages `3.13.15-r4`, successful `import math`, Python 3.13.15, `cpython-313`, x86_64 SOABI, Rust assertions, and no managed Python download
3. Require both frozen syncs, Maturin/Rust bridge build, Prisma generation, and explicit venv assertion to pass. Generate builder and runtime installed-package manifests/SBOMs. Scan every copied ELF object and Python extension with `ldd`/version-needs tooling; reject unresolved libraries, architecture mismatch, or any GLIBC requirement above the runtime provider
4. In the final image directly invoke `/app/.venv/bin/python`; verify venv/system linkage, Python and SOABI, and imports of `math`, Prisma, uvloop 0.21.0, LiteLLM, Rust bridge, and representative native dependencies. Require Prisma engines under `/opt/prisma`
5. Preserve final image config: venv-first PATH, absent `VIRTUAL_ENV`, unchanged Prisma environment, nonroot/runtime ownership contract, `ENTRYPOINT`, and `CMD`. Record immutable candidate image ID and, if published later under separate authorization, its repository manifest digest and SBOM/provenance identity
6. Execute every original TASK-006 isolated gate with the normal entrypoint: readiness, six discovery aliases and exact resources, exact 401 challenges, safely available initialize/tool behavior, reconnects with zero discovery 404s, `/mcp`, MCP REST, upstream preservation, production pre/post identity/readiness, and cleanup. Credential-bound checks remain blocked rather than weakened
7. Arm64 promotion requires a native arm64 builder to require child `sha256:fce2...361e`, install and execute the same r4/glibc closure, complete the full build, scan native artifacts, and repeat final-image/import/entrypoint smoke. OCI and APK metadata alone are not execution evidence

Manifest impact is limited to `Dockerfile` within the existing eight-path candidate; its SHA-256, ordered manifest checksum, and combined tracked patch checksum must be replaced and independently reviewed. The seven application/parser fingerprints, application-only patch checksum, `pyproject.toml`, `uv.lock`, Cargo files, Rust/uv/UI OCI inputs, and Git base must remain the TASK-012 frozen values unless a separate governed task authorizes change

### Security Implications

Advancing from glibc 2.43 to 2.44 changes the foundational C runtime and all package transactions resolve against a newer ABI epoch. This removes the demonstrated unsupported mixed-epoch state and avoids downgrading Python to retained r1. It also changes the base SBOM and vulnerability surface, so image/SBOM scanning, signature/provenance verification, and policy comparison against production are promotion gates. A digest is immutable identity, not automatic trust; registry provenance and package signatures still require verification

The current public Wolfi rolling repository is the remaining supply-chain risk. Direct-package version pins prevent silent Python minor/revision changes but do not freeze transitive APK bytes. Release engineering should mirror the exact signed closure or publish internal foundation images and attach SBOM/provenance before claiming reproducible rebuilds. No temporary repository, `--allow-untrusted`, signature bypass, glibc overlay, or copied loader/library workaround is acceptable

### Rollback

Before promotion, rollback is to discard the failed candidate and reverse only the two base-argument substitutions, restoring TASK-012's Dockerfile/manifest/combined-patch fingerprints. Do not attempt an in-place glibc downgrade inside a built image

After a separately approved deployment, rollback is digest-based redeployment of the recorded prior production manifest `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, followed by readiness, baseline behavior, image/config identity, and dependency checks. This investigation changes no schema or data, so no database rollback is expected. If the production reference changes before authorization, capture and use the then-current immutable manifest rather than assuming this recorded digest remains current

### Acceptance Criteria Coverage

- **AC-1: PASS.** Exact old/new Wolfi platform provenance, glibc families, Python r1/r4 artifact requirements, builder/copied-native surface, and production ancestry are traced
- **AC-2: PASS.** One coherent build/runtime pair is identified by exact OCI index and platform manifests. The limit of the rolling APK repository is explicit, with immutable snapshot/foundation-image closure defined as release hardening
- **AC-3: PASS.** Base advancement, complete APK snapshotting, official Python migration, and production-image reuse are compared with explicit dispositions
- **AC-4: PASS.** The recommendation includes exact OCI digests, amd64-only authorization, two Dockerfile substitutions, package and ABI gates, security implications, complete tests, rollback, and eight-path manifest impact
- **AC-5: PASS.** Only this governed task was updated. No source, Dockerfile, lock, test, image retained by the probe, container, configuration, database, deployment, production, architecture document, or CodeMap was changed

### Documentation Impact

No product or steady-state architecture documentation change is required for this investigation. The bounded recommendation corrects build supply-chain coherence without changing application interfaces or behavior. If immutable APK foundation images become a maintained release mechanism, their snapshot format, ownership, refresh policy, signing/SBOM contract, and rollback procedure must be documented in `docs/architecture/` under a separate approved task. No CodeMap changes are required now

### Open Risks

The complete candidate has not been built on the replacement index. The native amd64 probe establishes the exact Python/glibc prerequisite only; full sync, Maturin, copied extension, Prisma, entrypoint, and protocol gates remain TASK-006 responsibilities. Arm64 remains unexecuted. The rolling repository can remove retained r4 artifacts or change unpinned direct/transitive packages. The replacement digest was reviewed on 2026-08-31 and must be re-resolved at authorization rather than inferred from `latest`

Repository-wide `staticeng_validate` is not required by this task-only research update and remains affected by the known pre-existing CodeMap inventory. No architecture or CodeMap structure changed, and no unrelated repair is authorized

### Recommended Next Step

PMA should create one bounded foundation implementation/review task for the exact two-line root Dockerfile base advancement, newly frozen eight-path inputs, package-checksum gates, and amd64 preflight. After independent Tech Lead review, reopen TASK-006 as Reopen 4 for the complete amd64 build and smoke contract. In parallel only as a non-conflicting specification task, define the immutable APK snapshot/foundation-image publishing contract before release promotion. Keep arm64 and deployment unauthorized

### Signed Handoff

[Agent Message] From: technical_architect To: product_manager

PASS investigation. Authorize a root-Dockerfile-only atomic advance of both Wolfi base defaults to OCI index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`, requiring amd64 child `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd`. It embeds glibc/loader 2.44-r1 and natively runs the exact Python 3.13.15-r4 closure that fails on the old glibc 2.43 digest. Preserve every other TASK-012 input, re-freeze the eight-path manifest, verify exact APK checksums and complete ELF/import/runtime gates, then resume TASK-006 on amd64 only. Treat public rolling APK resolution as candidate evidence, not reproducible snapshot closure; define immutable mirrored APK or foundation-image digests before promotion. Production, deployment, and arm64 remain unchanged and unauthorized

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-013 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
