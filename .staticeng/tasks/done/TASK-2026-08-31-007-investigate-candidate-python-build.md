---
id: TASK-2026-08-31-007-investigate-candidate-python-build
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

# Task: Investigate candidate Python build failure

## Objective

Determine the smallest safe correction for the detached Docker build selecting CPython 3.14.4 and failing to build `uvloop==0.21.0` because `/usr/bin/file` is absent, without changing application behavior or production.

## Acceptance Criteria

- [x] AC-1: Identify why the authorized base resolves Python 3.14.4 and whether the intended image contract pins another supported version.
- [x] AC-2: Compare minimal options: pin supported Python, install missing builder package, update uvloop, or use an existing repository Docker target/configuration.
- [x] AC-3: Recommend one minimal deterministic fix with exact files, tests, compatibility risks, and rollback.
- [x] AC-4: Determine whether the fix belongs in the candidate manifest or can be achieved with an existing build argument/target and no source mutation.
- [x] AC-5: Produce a signed handoff; do not edit source, tests, Dockerfiles, locks, images, or production.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Read the failed build evidence and inspect Dockerfiles, Python constraints, uv/lock metadata, CI build paths, and current production image metadata without secrets. Prefer an existing supported build path over introducing a packaging change. Do not mutate source/runtime. Return findings and a precise recommendation for Tech Lead authorization.

# Investigation Results

## Summary

The unchanged root Dockerfile installs Wolfi's unversioned `python3` and `python3-dev` packages from a live APK repository. The authorized Wolfi image is pinned by OCI index digest, but the APK packages installed later are not pinned. At the failed build, those names resolved to CPython 3.14.4. Both `uv sync` commands explicitly select the resulting `python3`, so uv did not download or independently choose Python 3.14

`pyproject.toml` permits Python `>=3.10,<3.15`, but this range is a package compatibility declaration rather than a deterministic container-runtime selection. `uv.lock` retains `uvloop==0.21.0`. That release publishes Linux wheels through CPython 3.13 but no CPython 3.14 wheel, so Python 3.14 selects the locked source distribution. Its vendored libuv bootstrap then fails because `/usr/bin/file` is absent

The established deployed image contract is CPython 3.13.15 with `uvloop==0.21.0`. Secret-free inspection of the unchanged healthy production container returned Python 3.13.15, ABI tag `cpython-313`, and uvloop 0.21.0. The smallest correction is therefore to pin the root image's builder and runtime to the matching Wolfi Python 3.13.15 package revision and direct both uv invocations to `python3.13`

## Evidence Reviewed

- Failed build: `.staticeng/evidences/TASK-2026-08-31-006-build-smoke-lazymcp-oauth-candidate/logs/03-build.log` records CPython 3.14.4, `uvloop==0.21.0`, missing `/usr/bin/file`, and no output image
- Root image path: `Dockerfile:40`, `Dockerfile:62`, `Dockerfile:83`, and `Dockerfile:104` install/select unversioned `python3`; no `.python-version` or Python-version Docker argument exists
- Supported range and lock: `pyproject.toml:6` permits Python below 3.15; `pyproject.toml:49` allows uvloop 0.21 or newer; `uv.lock:9841` deterministically selects uvloop 0.21.0
- CI path: `.github/workflows/image-scan.yml:111` builds the root `Dockerfile` directly without a Python build argument or alternate target
- Production: the running immutable image uses CPython 3.13.15 and uvloop 0.21.0, proving the proposed minor-version/runtime pairing is the established operational contract
- Upstream package metadata: uvloop 0.21.0 has CPython 3.13 manylinux and musllinux wheels but no CPython 3.14 wheel; uvloop 0.22.1 introduces CPython 3.14 wheels and would be a dependency upgrade rather than a build-selection repair

## Authorized Image And Platform Evidence

The authorized build and runtime argument defaults both reference OCI index `cgr.dev/chainguard/wolfi-base@sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f`. `docker buildx imagetools inspect` resolves exactly two platforms:

- `linux/amd64`, child manifest `sha256:85ecaa3f494ee2339eaf6f74a23f19f934df3019a9a9dfc8c06f53c3aacc4e6b`
- `linux/arm64`, child manifest `sha256:1391b1e3093efd59124d88b3e7389d9e0d6df7a004ec65bf7d9fee22c28d1542`

Fresh signed Wolfi APK indexes for both `x86_64` and `aarch64` contain exact packages `python-3.13=3.13.15-r4` and `python-3.13-dev=3.13.15-r4`. On both architectures, the dev package declares exact dependencies on `python-3.13-base-dev=3.13.15-r4` and `python-3.13=3.13.15-r4`; the runtime package declares `python-3.13-base=3.13.15-r4` and provides `python3=3.13.15-r4` plus `python-3=3.13.15-r4`

Exact index verification commands:

```bash
docker buildx imagetools inspect \
  cgr.dev/chainguard/wolfi-base@sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f

for arch in x86_64 aarch64; do
  curl -fsSL "https://apk.cgr.dev/chainguard/${arch}/APKINDEX.tar.gz" \
    | tar -xzO APKINDEX \
    | rg -n -A12 -B1 '^P:python-3\.13(-dev)?$|^V:3\.13\.15-r4$'
done
```

The native `linux/amd64` install probe against the authorized image succeeded with the exact packages and returned CPython 3.13.15, cache tag `cpython-313`, SOABI `cpython-313-x86_64-linux-gnu`, platform `linux-x86_64`, executable `/usr/bin/python3.13`, and development header `/usr/include/python3.13/Python.h`

```bash
docker run --rm --platform linux/amd64 \
  cgr.dev/chainguard/wolfi-base@sha256:42df77a9974d6ec8b17a5ee8bc23b532600a44d705acef2409e0933c1251b45f \
  sh -lc 'apk update >/dev/null && apk add --no-cache \
    "python-3.13=3.13.15-r4" "python-3.13-dev=3.13.15-r4" >/dev/null && \
    python3.13 -c "import sys,sysconfig; print(sys.version); print(sys.implementation.cache_tag); \
    print(sysconfig.get_config_var(\"SOABI\")); print(sysconfig.get_platform())" && \
    test -x /usr/bin/python3.13 && test -e /usr/include/python3.13/Python.h'
```

The current Docker daemon executes `linux/amd64` and has no arm64/QEMU execution support, so an arm64 runtime install was not falsely claimed. The arm64 child manifest and exact signed APK index entries establish package availability and dependency alignment. TASK-008 must perform the full build for every platform it authorizes; if only the failed candidate's native `linux/amd64` platform is authorized, the amd64 proof is sufficient for that candidate. A multi-platform release must run an arm64-capable builder and verify the same image assertions on arm64 before promotion

## ABI And Runtime Compatibility

Builder and runtime use the same authorized Wolfi OCI index and the exact same `python-3.13=3.13.15-r4` package revision. Builder-only `python-3.13-dev=3.13.15-r4` depends on that exact runtime package and matching base development package. The virtual environment copied from builder to runtime therefore remains on CPython ABI `cpython-313`; no 3.14 extension or interpreter can enter through either uv invocation when both use the explicit executable `python3.13`

uvloop 0.21.0 supplies platform-specific CPython 3.13 wheels for both x86_64 and aarch64 on Linux, including musllinux. This avoids its source-build path and the missing `file` executable entirely. Runtime validation must assert Python 3.13, ABI `cpython-313`, uvloop 0.21.0, and successful imports after the final venv is copied

## Option Comparison

1. **Pin Python 3.13: recommend.** It restores the established production pairing, uses the locked uvloop wheel, removes dependence on an unsupported source build, and changes only five Dockerfile lines
2. **Install `file`: reject.** It addresses only the first configure failure while retaining a source build of uvloop 0.21.0 on Python 3.14, a version for which that release publishes no wheel or classifier. Further build or runtime incompatibilities remain possible
3. **Update uvloop: defer.** uvloop 0.22.1 publishes CPython 3.14 wheels, but updating it changes `uv.lock` and the resolved runtime dependency. It requires broader compatibility and performance verification and is not the smallest correction for this candidate
4. **Use an existing Docker target/configuration: reject.** `docker/Dockerfile.non_root`, `gateway/Dockerfile`, `backend/Dockerfile`, and `migrations/Dockerfile` also install unversioned Wolfi Python. `docker/build_from_pip/Dockerfile.build_from_pip` uses Python 3.13 but installs a published package instead of this detached source candidate and cannot satisfy the reviewed manifest

## Exact Five-Line Proposal

Only `Dockerfile` changes, after separate Tech Lead authorization:

```diff
-    python3 \
-    python3-dev \
+    python-3.13=3.13.15-r4 \
+    python-3.13-dev=3.13.15-r4 \
@@
-    --python python3
+    --python python3.13
@@
-    --python python3
+    --python python3.13
@@
-RUN apk add --no-cache bash openssl tzdata nodejs python3 libsndfile
+RUN apk add --no-cache bash openssl tzdata nodejs python-3.13=3.13.15-r4 libsndfile
```

This is five substitutions: two builder package lines, two uv interpreter selectors, and one runtime package line. No change is proposed to `pyproject.toml`, `uv.lock`, application source, tests, other Dockerfiles, deployments, or production

## Manifest And Build-Argument Decision

The correction cannot be expressed by an existing Python build argument because none exists. `LITELLM_BUILD_IMAGE` and `LITELLM_RUNTIME_IMAGE` replace whole base images, not the Python package selected inside them. Supplying custom bases would introduce two new external image identities and still require proof of their package/ABI contents

The root `Dockerfile` must therefore enter the re-frozen candidate manifest with its pre/post SHA-256 fingerprints. The authorized six application paths remain unchanged. Candidate construction must not reuse TASK-006's old manifest or claim its failed build as runtime evidence

## Required Verification For TASK-008 And Reopened TASK-006

```bash
git diff --check
git diff --exit-code -- pyproject.toml uv.lock
docker build --pull=false --progress=plain \
  -t litellm:lazymcp-oauth-candidate \
  /tmp/opencode/lazymcp-oauth-candidate/worktree
docker run --rm --entrypoint python litellm:lazymcp-oauth-candidate -c \
  'import sys,sysconfig,uvloop; assert sys.version_info[:2] == (3,13); assert sys.implementation.cache_tag == "cpython-313"; assert uvloop.__version__ == "0.21.0"; print(sys.version); print(sysconfig.get_config_var("SOABI")); print(uvloop.__version__)'
docker image inspect --format '{{.Id}} {{.Architecture}}/{{.Os}}' \
  litellm:lazymcp-oauth-candidate
```

TASK-008 must additionally retain exact five-line diff, Dockerfile fingerprints, package-resolution logs, scoped unchanged-file proof, and per-authorized-platform evidence. After TASK-008 passes, TASK-006 must be reopened and all SCR smoke gates rerun; a successful image build alone does not satisfy the SCR

## Compatibility Risks And Rollback

- Exact APK revisions are served by Wolfi's live repository rather than embedded in the base image. Verify both exact packages immediately before every authorized platform build; fail closed if either revision is unavailable
- A future multi-platform release must not infer arm64 runtime success from index metadata. Build and execute the validation on an arm64-capable builder
- Python 3.13 intentionally excludes dependencies marked `python_version >= '3.14'` and includes those marked `< '3.14'`; this matches the established deployed runtime but means the full frozen sync and application smoke remain mandatory
- Rollback before deployment is to discard the candidate image and revert only the five Dockerfile substitutions. Rollback after an independently authorized deployment is digest-based redeployment of the current immutable production image, followed by health and baseline verification. No schema or data rollback is expected

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

- Investigation completed read-only except for this governed task closure update
- No Dockerfile, source, test, lock, image, container, deployment, configuration, database, credential, or production mutation was performed
- Product documentation is not required. This is a packaging determinism correction; candidate manifest and evidence updates are mandatory in TASK-008/TASK-006

## Acceptance Criteria Evidence

- **AC-1: PASS.** Root Dockerfile, uv behavior, supported range, lock, failure evidence, and production runtime establish why 3.14.4 was selected and why 3.13.15 is the intended operational pairing
- **AC-2: PASS.** All four required options and existing Docker paths are compared with explicit dispositions
- **AC-3: PASS.** The exact five-line Dockerfile-only recommendation, per-platform constraints, ABI contract, validation commands, risks, and rollback are recorded
- **AC-4: PASS.** No existing build argument or target can express the correction without changing whole base-image identities; `Dockerfile` must be added to a newly frozen candidate manifest
- **AC-5: PASS.** This signed handoff records completion; investigation did not mutate runtime or production

## Signed Completion Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-007 is complete and recommended for acceptance. Authorize renewed Tech Lead review of the exact five-line root `Dockerfile` Python 3.13.15-r4 pin recorded here. Exact runtime and development packages exist for both platforms in the authorized Wolfi OCI index, builder/runtime ABI alignment is explicit, and the native amd64 install probe passes. Existing build arguments and targets cannot implement the correction without changing broader image inputs. TASK-008 must fail closed on package drift, build and validate every authorized target platform, re-freeze the manifest with `Dockerfile`, and return the resulting immutable image to reopened TASK-006 for the complete smoke contract

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-007 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
