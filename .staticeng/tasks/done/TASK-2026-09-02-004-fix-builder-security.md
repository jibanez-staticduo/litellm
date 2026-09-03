---
id: TASK-2026-09-02-004-fix-builder-security
complexity: complex
track: implementation
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-011-qualify-upstream-isolated-candidate
assigned_to: developer
handoff_from: product_manager
reopened_count: 1
---

# Task: Fix builder security

## Objective

Apply approved minimal corrections so exact builder and final candidate have no fixable High or Critical findings, then commit/push fork main after review.

## Acceptance Criteria

- [ ] AC-1: Correct only approved package/lock/build inputs.
- [ ] AC-2: Source, Rust, Python, UI, lock, native-build, and behavior regressions pass.
- [ ] AC-3: Exact clean builder/final scans show zero Critical and zero fixable High under one frozen database.
- [ ] AC-4: Evidence, rollback, CodeMaps/docs and disposable cleanup pass.
- [ ] AC-5: Tech Lead reviews, commits, and non-force pushes fork main; no deployment occurs.

## Handoff

[Agent Message] From: product_manager To: developer

TASK-003 architecture approval is complete. Modify only root `pyproject.toml`, generated `uv.lock`, and root `Dockerfile`: add the approved isolated-build setuptools floor `>=78.1.1`, replace uv 0.11.7 with digest-pinned uv 0.11.26 index `sha256:3d868e555f8f1dbc324afa005066cd11e1053fc4743b9808ca8025283e65efa5`, and require amd64 child `sha256:663211e7509e89ff2172cc3ca098afb4ac63028dd065d2b047e4251127a7d47a`. Do not edit application Cargo. Stop if `ml-dtypes` metadata makes the safe resolution impossible. Run source/lock/build/runtime and same-frozen-DB exact builder/final scans, proving zero Critical and zero fixable High; retain identities/evidence and destroy disposable resources. Do not commit/push or mutate Fedora/NAS; Tech Lead reviews first.

## Reopen History

### Reopen 1 - Package-scoped ml-dtypes override

The global setuptools constraint proved unsatisfiable and was fully rolled back. Implement the revised TASK-003 contract: retain RedisVL 0.4.1, add a uv 0.11.26 package-scoped override of its `ml-dtypes` requirement to exact 0.5.4, enforce wheel-only installation and the reviewed CPython 3.13 amd64 wheel hash/provenance, replace Docker uv input with the approved immutable 0.11.26 digest, and align repository-controlled CI uv pins from 0.10.9 to 0.11.26. Do not add the rejected global setuptools floor or edit application Cargo. Run full Redis/Valkey semantic-cache, bfloat16 byte/index compatibility, source/CI/lock/build/runtime and exact same-database scans. Stop on behavior or resolver incompatibility. No commit/push/deployment until Tech Lead review.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary

STOPPED as required because the approved isolated-build setuptools floor conflicts with `ml-dtypes 0.4.1` build metadata during the exact clean amd64 builder build

The generated lock represented the approved constraint without dependency churn, and uv 0.11.26 provenance matched the approved index and amd64 child. The first frozen Docker sync then failed closed because `ml-dtypes 0.4.1` requires `setuptools~=68.1.0`, which is unsatisfiable with `setuptools>=78.1.1`. All three candidate file changes were rolled back byte-for-byte. No Cargo file changed

### Acceptance Criteria Coverage

- **AC-1: BLOCKED.** The approved three-file candidate was attempted and no other source input changed, but the required package constraints are unsatisfiable
- **AC-2: BLOCKED.** Lock checks, local frozen syncs, package imports, and native bridge import passed, but the exact clean builder failed at its first frozen sync. Later source, Rust, UI, runtime, and behavior gates were not run after the mandatory stop
- **AC-3: BLOCKED.** No new builder or final image was emitted, so exact same-database scans could not be performed
- **AC-4: PASS FOR STOP SAFETY.** The candidate diff was fully rolled back, application Cargo remained byte-identical, disposable Buildx state and pulled uv input were removed, and the blocker is retained in task evidence
- **AC-5: NOT APPLICABLE.** No commit, push, publication, signing, deployment, Fedora mutation, or NAS mutation occurred

### Documentation Impact

No product, architecture, or CodeMap update is required because the candidate was rolled back and technical truth did not change

### Open Risks

The security remediation remains unresolved. Any path forward requires PMA-approved scope beyond the current contract, such as a compatible `ml-dtypes` or `redisvl` dependency update or a separately reviewed build-backend override. Removing the builder cache or bypassing metadata is not approved

### Recommended Next Step

PMA should route the confirmed dependency conflict to Technical Architect for a revised remediation. Keep TASK-011 promotion, publication, signing, deployment, Fedora, and NAS blocked

### Signed Handoff

[Agent Message] From: developer To: product_manager

BLOCKED. The exact clean linux/amd64 builder stopped at the first frozen sync: `ml-dtypes 0.4.1` requires `setuptools>=68.1.0,<68.2.dev0`, which cannot coexist with the approved isolated-build floor `setuptools>=78.1.1`. I followed the mandated stop, rolled back root `pyproject.toml`, generated `uv.lock`, and root `Dockerfile` byte-for-byte, left application Cargo unchanged, removed disposable Buildx/image resources, and performed no scan of nonexistent new subjects, commit, push, publication, signing, deployment, Fedora mutation, or NAS mutation. Route a revised dependency or build-backend design through PMA before retrying

## Developer: Reopen 1 Post Implementation Expectations

### Summary

PASS. Implemented the revised package-scoped override and wheel-only contract while retaining RedisVL 0.4.1, NumPy and application Cargo. Exact clean amd64 builder/final runtime and same-frozen-DB security gates pass with zero Critical and zero High

### Work Performed

Root project metadata now requires uv 0.11.26, scopes RedisVL 0.4.1 to ml-dtypes 0.5.4 and disables source builds for ml-dtypes. The generated lock changes only that package version plus required override/wheel records. Docker uses the approved uv index/amd64 child, asserts exact uv and wheel identity, and deletes uv cache only after all build outputs. All 19 repository-controlled CI callers now pin uv 0.11.26

Redis/Valkey unit and real Redis semantic-cache behavior, TTL/filter/isolation/reconnect, bfloat16 bytes and existing-vector round-trip pass. UI, Rust, native build, Prisma, imports, entrypoint/liveliness, SBOM and scanner gates pass. Exact evidence and checksums are under `.staticeng/evidences/TASK-2026-09-02-004-fix-builder-security/`

### Acceptance Criteria Coverage

- **AC-1: PASS.** Approved dependency/build/CI inputs only; no global setuptools floor, RedisVL upgrade, product code, unrelated version or Cargo change
- **AC-2: PASS.** Source/lock/CI, semantic cache, byte/index, UI, Rust, native build and runtime checks pass
- **AC-3: PASS.** Builder and final each report zero Critical and zero High under Grype DB schema 6.1.9 built `2026-09-02T06:35:12Z`
- **AC-4: PASS.** Evidence, checksums, rollback scope, docs/CodeMap no-change decision and disposable cleanup pass
- **AC-5: PENDING TECH LEAD.** No commit, push, signing, publication, deployment, Fedora action or NAS action occurred

### Documentation Impact

No product, architecture or CodeMap update is required because no application/module/API/schema truth changed

### Open Risks

Signing identity remains unresolved. Parent TASK-011 must rerun its full OAuth/MCP release qualification after a reviewed commit and before release

### Recommended Next Step

Route the exact diff and evidence to Tech Lead for review. Keep signing, publication, deployment, Fedora and NAS blocked

### Signed Handoff

[Agent Message] From: developer To: product_manager

PASS Reopen 1 implementation. Exact builder `sha256:c4221442096bb76e0d4fd1d07812b5067dc5ec0fb646123d32fde28188f708c5` and final `sha256:5f62c6a682457c9858e3015890f3a806bbcff05d4d2c582e176e5bf84d66dfe4` pass affected runtime and frozen-DB security qualification with zero Critical and zero High. RedisVL 0.4.1, NumPy and Cargo remain unchanged; ml-dtypes 0.5.4 is wheel-only and provenance-bound; CI uv pins are aligned. Evidence and cleanup are complete. No commit, push, sign, publish, deploy, Fedora or NAS action occurred

## Tech Lead: Post Implementation Expectations

### Summary

PASS. Independent review found no blocking defect. The exact scoped override, wheel-only lock and Docker assertions, uv provenance, 19 CI caller pins, post-build cache cleanup, unchanged application Cargo, semantic-cache and bfloat16 behavior, UI/Rust/runtime evidence, exact SBOMs and same-database scans satisfy AC-1 through AC-4

The repository-wide `make check` was rerun with checksum-matched uv 0.11.26 after fetching exact upstream `litellm_internal_staging` SHA `3cac5e5cd4c12a782e0afe96218aaff986ef3f60` into the wrapper-required local ref `origin/litellm_internal_staging`. It passed without a baseline waiver

### Work Performed

- Reviewed the complete source, lock, Docker, CI and StaticEng diff against fork-main source `165a94ecfbf21d7ff4626815ac6b298ac34e2adb`
- Verified all 19 `setup-uv-with-retries` callers pin exact uv 0.11.26 and no caller remains on 0.10.9
- Verified `uv.lock` changes only scoped override/no-build metadata, ml-dtypes 0.4.1 to 0.5.4, and its generated artifacts; RedisVL 0.4.1, NumPy and application Cargo do not drift
- Rechecked wheel and metadata hashes against current PyPI data and verified the PEP 740 publisher, repository, workflow, release environment and exact wheel subject
- Recomputed artifact checksums, parsed all three Grype reports, and confirmed one exact DB identity with zero Critical and zero High for builder/final and zero findings for uv
- Reran `uv lock --check`, the 82 Redis/Valkey unit tests, `make check` with the exact upstream base, and `staticeng_validate`; all passed
- Verified no task-labelled container, network, volume, image or non-default Buildx builder remains and no production, registry, signing or deployment action occurred

### Acceptance Criteria Coverage

- **AC-1: PASS.** The diff is confined to the approved dependency/lock/Docker/CI pin inputs plus governed task/evidence closure
- **AC-2: PASS.** Developer UI, Rust, native-build, runtime, real Redis and bfloat16 evidence is coherent; independent lock, Redis/Valkey and full `make check` reruns pass
- **AC-3: PASS.** Exact builder and final scans share Grype DB v6.1.9 built `2026-09-02T06:35:12Z`; both contain zero Critical and zero High, with SBOM identities matching the scanned images
- **AC-4: PASS.** Checksums, CodeMap no-change decision, rollback history and disposable cleanup pass; product documentation is not required
- **AC-5: PASS.** Tech Lead approved closure; the non-force fork-main commit and remote SHA are recorded in the final handoff, and no deployment occurs

### Documentation Impact

No product, architecture or CodeMap update is required because the correction changes dependency/build/CI inputs without changing application behavior, API, schema, route, module ownership or maintained command structure

### Open Risks

Signing and publication remain blocked pending an approved release identity. Parent TASK-011 must rerun full release qualification against the committed source and new candidate identities before any release or deployment

### Recommended Next Step

PMA should reopen TASK-011 against the pushed fork-main commit. Keep signing, publication, deployment, Fedora and NAS blocked until that task passes and separate authorization is granted

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. Reopen 1 meets AC-1 through AC-5 after exact upstream-base `make check`, independent evidence/SBOM/scan review, cleanup verification, commit and non-force fork-main push. No image was signed or published and no deployment or production mutation occurred
