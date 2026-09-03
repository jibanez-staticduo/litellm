---
id: TASK-2026-09-02-001-design-coherent-wolfi-closure
complexity: standard
track: investigation
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-02-002-fix-coherent-wolfi-closure
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Design coherent Wolfi package closure

## Objective

Confirm and freeze the smallest reproducible Dockerfile correction after exact fork-main build proved Python 3.13.15-r4 incompatible with the committed glibc 2.43 Wolfi base.

## Acceptance Criteria

- [x] AC-1: Compare current Dockerfile against previously reviewed TASK-013/TASK-014 coherent glibc 2.44 correction and current upstream changes.
- [x] AC-2: Freeze exact build/runtime OCI index and amd64 platform identities plus Python/Rust/uv/package compatibility.
- [x] AC-3: Recommend minimal source changes, tests, manifest impact, rollback, and arm64 boundary.
- [x] AC-4: Update task with signed evidence; no source/image/host mutation.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Read TASK-011 Reopen 2 rejection and prior TASK-013/TASK-014 evidence. Research only. Determine whether restoring both reviewed Wolfi glibc 2.44 defaults is still the exact minimal correction on current fork main, or specify a safer coherent snapshot. Verify immutable OCI identities and mutable-APK risk. Do not edit/build/push/deploy. Return authorization-ready signed handoff.

# Post Implementation Task Updates

## Technical Architect: Post Investigation Expectations

### Summary

PASS for investigation. Restoring both reviewed TASK-014 Wolfi defaults is still the exact minimal coherent correction on current fork main `9374aae27c93d509a12f167c6bb1f83815ed3db1`. The upstream integration changed only the two Wolfi defaults relative to the previously approved Dockerfile and retained the exact Python 3.13.15-r4 pins, absolute uv interpreter selectors, Rust 1.97.1 toolchain stage and assertions, runtime venv contract, Prisma validation, uv image, UI image, and stage layout

The authorized correction is a root-`Dockerfile`-only atomic replacement of both current Wolfi index defaults `sha256:a31344ab2cb8618db84f535eec56f76f6178b142cb92cb2e48676cc2dcebea72` with reviewed index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`. The proposed file is byte-identical to the TASK-014-approved Dockerfile and has SHA-256 `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`

This correction restores proven amd64 ABI coherence, not a reproducible APK snapshot. The public Chainguard repository retains non-latest packages for a bounded period and may change package/index contents. Exact Python pins protect the direct interpreter choice but unversioned direct and transitive APK packages remain mutable. Release promotion therefore requires retention of the exact signed APK indexes and artifacts or digest-pinned internally published foundation images, plus exact-image SBOM, provenance, signature, and same-database scan evidence

### Work Performed

- Read TASK-011 Reopen 2 and its secret-free build/cleanup ledger, TASK-013, TASK-014 and its independent evidence, the prior successful amd64 candidate packaging evidence, the approved upstream-integration SCR, current root `Dockerfile`, merge conflict ledger, and current task state
- Confirmed current commit `9374aae27c93d509a12f167c6bb1f83815ed3db1`, current Dockerfile SHA-256 `e7e669bfd09b5beb9ec27fc1a976bf90232adf7144fda5def7a761e2ddbcad11`, and an exact two-line semantic difference from TASK-014's approved Dockerfile
- Reconstructed the proposed correction without changing the repository. Its SHA-256 is `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`, and it is byte-identical to `514fd6bb8eb76760b6daf04db1dcfa8fd655b00f:Dockerfile`
- Re-resolved both current and replacement Wolfi OCI indexes read-only. The current index maps amd64 to `sha256:52604323e2a19f5e6d37dffa7e6a7ef30e2f98506a73a11cdfa3ef25100131be`; the replacement maps amd64 to `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd`. Replacement arm64 is `sha256:fce2a4534bdae72009371dab1c87d322f255b40daff82b857e98c4a0890b361e`, metadata only
- Re-resolved preserved uv, Rust, and UI OCI indexes and amd64 children. Reviewed prior native amd64 evidence proving replacement-base glibc/loader 2.44-r1, Python 3.13.15-r4, `math`, `cpython-313-x86_64-linux-gnu`, uvloop 0.21.0, Prisma, Rust bridge, representative native imports, and normal entrypoint compatibility
- Checked current official Chainguard package-model and verification guidance. Public package versions have bounded retention and should be mirrored internally when pinned; image signatures and attestations require separate exact-subject Cosign verification

### Exact Frozen Contract

Authorize only this atomic source correction:

```diff
-ARG LITELLM_BUILD_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:a31344ab2cb8618db84f535eec56f76f6178b142cb92cb2e48676cc2dcebea72
+ARG LITELLM_BUILD_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d
@@
-ARG LITELLM_RUNTIME_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:a31344ab2cb8618db84f535eec56f76f6178b142cb92cb2e48676cc2dcebea72
+ARG LITELLM_RUNTIME_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d
```

Freeze these effective identities for `linux/amd64` qualification:

| Input | OCI index | Required amd64 child |
| --- | --- | --- |
| Wolfi build/runtime | `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d` | `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd` |
| uv 0.11.7 | `sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a` | `sha256:733b4042187702f832f7fdecb3aff14a61b288c4ca37af188bb5715c1caebaf8` |
| Rust 1.97.1 | `sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3` | `sha256:39f68a3e8e3ff425f8945ffa91128e60ff930d53e17fbb5214e95824bdd46f1b` |
| Node 24.19 UI | `sha256:d32cdf619f63fe0471182d08996dd516c6275bb5fd31ae06e55a570bd9e1ad43` | `sha256:2a49bdf71e9fd965a58c1703fd9ddd205b34e5782b692a72dd1d248abb0beb43` |

The Wolfi amd64 manifest config is `sha256:a7b2e90a205a20887d43148b4509171ac7f321cf9812e3bc3154a88e6775d140`. The same replacement index's arm64 child is `sha256:fce2a4534bdae72009371dab1c87d322f255b40daff82b857e98c4a0890b361e`; uv arm64 is `sha256:40edad71a1710a9d5d988c6a034304e9c414d7f794dab44a0781d619bba41d33`; Rust arm64/v8 is `sha256:b28e5606d830400fabf789f910f9ed2ea22cdd6d51d463c5d0baa30bb2bedb2d`; UI arm64/v8 is `sha256:0e6f1567e269207c28295276928277a030139cbc5a0fb7d5bd2674f0401a9082`. These arm64 identities are provenance only and authorize no arm64 build, promotion, or deployment

Preserve every other current Dockerfile byte and repository input. In particular, retain builder `python-3.13=3.13.15-r4` and `python-3.13-dev=3.13.15-r4`, runtime `python-3.13=3.13.15-r4`, both `--python /usr/bin/python3.13` selectors, `/app/.venv/bin/python` Prisma assertion, Rust identity assertions, APK package lists, locks, Cargo inputs, source/tests, alternate Dockerfiles, entrypoints, and deployment files. No new direct package pin, Python downgrade, glibc overlay, loader copy, base override at build time, or foundation-image redesign belongs in this correction

### Required Implementation And Qualification Evidence

1. Before editing, require current commit `9374aae27c93d509a12f167c6bb1f83815ed3db1`, a clean source baseline apart from attributed StaticEng state, and current Dockerfile SHA-256 `e7e669bfd09b5beb9ec27fc1a976bf90232adf7144fda5def7a761e2ddbcad11`. Apply exactly the two substitutions and require post-edit SHA-256 `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`, `git diff --check`, and no third source line
2. Re-resolve every frozen OCI index immediately before build. Require `linux/amd64` children above, reject current Wolfi index `sha256:a31344...bea72` and child `sha256:526043...131be` from all effective build/runtime `FROM` inputs, and build only from the committed defaults without argument overrides
3. Before first uv sync, require glibc, locale, and loader 2.44-r1; all four Python runtime/base/dev packages at 3.13.15-r4; Python 3.13.15; x86_64; `cpython-313`; SOABI `cpython-313-x86_64-linux-gnu`; `import math`; math's `GLIBC_2.44` need; exact Rust 1.97.1 identity/host/LLVM assertions; and no uv-managed Python download
4. Build exact builder and final targets in the approved disposable isolated `linux/amd64` environment. Record immutable builder/final config IDs, source revision labels, installed APK manifests, and signed-index/artifact hashes. Require both frozen syncs, Maturin/Rust bridge, Prisma generation, copied-ELF resolution, venv realpath `/usr/bin/python3.13`, uvloop 0.21.0, Prisma, LiteLLM, Rust bridge and representative native imports, venv-first PATH, absent `VIRTUAL_ENV`, unchanged `ENTRYPOINT`/`CMD`, normal startup, readiness, and clean shutdown
5. Re-run TASK-011 from the beginning against the independently reviewed correction commit. All SCR-required isolated migration, health, model, Responses, MCP, LazyMCP, OAuth, permission, reconnect, real-tool, logging, preservation, cleanup, signature, attestation, SBOM, same-database scan, and Critical/High disposition gates remain mandatory. Prior TASK-014/TASK-006 images prove compatibility only and cannot qualify current source
6. Re-freeze current candidate scope after the edit. At minimum, record current Git source commit, the root Dockerfile pre/post fingerprints, ordered hashes for every source/build input required by TASK-011, aggregate manifest checksum, source patch checksum, dependency/lock/Cargo fingerprints, OCI index/platform identities, APK indexes/artifacts, builder/final image identities, and evidence checksums. Do not reuse TASK-014's old eight-path manifest or patch checksums because current upstream source and locks differ

### Mutable APK Risk And Stronger Closure

The two-default correction is the smallest source fix and is authorized for TASK-002. It is not sufficient for a claim that future rebuilds are bit-for-bit reproducible. The root Dockerfile installs unversioned `bash`, GCC, OpenSSL, Node, npm, libsndfile, and tzdata plus mutable transitive dependencies from `https://apk.cgr.dev/chainguard`; even the exact Python r4 packages depend on repository retention and changing signed index bytes

For this release, freeze the actual transaction as evidence: retain both architecture-appropriate signed `APKINDEX` bytes used for amd64, every resolved `.apk`, artifact SHA-256, repository/key fingerprints, installed-package manifests, and builder/final SBOMs. If those exact artifacts cannot be retained and independently verified, candidate construction may establish present compatibility but promotion remains blocked under the SCR supply-chain contract

For durable repeatable rebuilds, use a separate approved foundation task to mirror the complete signed closure into immutable internal storage or publish reviewed build/runtime foundation OCI images by digest. That task must define ownership, refresh/CVE policy, signature and attestation identity, per-platform package closure, SBOMs, retention, and rollback. Do not broaden TASK-002 into that architecture change

### Rollback

Before commit or promotion, rollback is a clean reversal of exactly both substitutions, restoring Dockerfile SHA-256 `e7e669bfd09b5beb9ec27fc1a976bf90232adf7144fda5def7a761e2ddbcad11`. Discard any failed disposable images and caches. Never downgrade glibc in place or combine the old runtime base with artifacts built on glibc 2.44

After a separately approved deployment, rollback must redeploy the immutable pre-release production digest recorded immediately before mutation, not a tag and not a historical digest assumed from prior tasks. Verify readiness, migrations/rollback compatibility, model inventory, Responses, MCP/LazyMCP, authorized tool behavior, image/config identity, and logs. This two-line packaging correction introduces no schema or data migration, but current upstream migrations still require TASK-011's isolated upgrade and prior-image compatibility gates

### Acceptance Criteria Coverage

- **AC-1: PASS.** Current fork-main Dockerfile, exact upstream merge decision, TASK-011 Reopen 2 failure, and prior TASK-013/TASK-014 correction were compared. Only the two Wolfi defaults regressed relative to the previously approved Dockerfile
- **AC-2: PASS.** Exact build/runtime Wolfi index, amd64 child/config, metadata-only arm64 child, and preserved uv/Rust/UI index and amd64 identities are frozen. Prior native/full-candidate evidence establishes Python/Rust/uvloop/Prisma/native compatibility on amd64
- **AC-3: PASS.** Exact two-line source correction, no-change boundary, build/runtime/security test matrix, current-manifest refreeze, immutable-APK follow-up, rollback, and arm64 boundary are defined
- **AC-4: PASS.** This task and secret-free Evidence Packet contain the signed handoff. No source, Dockerfile, test, lock, image, container, builder, registry, host, database, production, deployment, Git commit, push, or CodeMap mutation was performed

### Documentation Impact

No product, public interface, steady-state application architecture, or CodeMap change is required. The correction restores the already reviewed packaging contract without adding a maintained module or advertised behavior. If immutable APK snapshots or foundation images become a maintained release mechanism, document their interfaces and operating policy under `docs/architecture/` in a separate approved task

### Open Risks

- Public APK resolution remains mutable and retention-bound, so the two-line correction proves current amd64 compatibility but not future binary-identical rebuilds
- Current source has not built after this correction. Prior TASK-014/TASK-006 results are strong compatibility evidence but do not replace TASK-002 and TASK-011 execution against the new exact commit
- Arm64 has OCI/package metadata only and remains unauthorized pending native arm64 build, ELF scan, final-image imports, normal entrypoint, and equivalent runtime/security qualification
- Signature/attestation verification, aggregate builder/final SBOMs, same-database comparative scans, and independent Critical/High disposition remain fail-closed promotion gates
- TASK-011's real authorized model/tool and isolated database-dependent gates remain mandatory; no prior environment block is waived

### Recommended Next Step

PMA should activate TASK-2026-09-02-002 with the exact two-line correction and frozen contract above. Developer should implement only those substitutions, run the bounded amd64 build/package gates, and hand the exact diff and complete evidence to Tech Lead for independent review and commit. Reopen TASK-011 only against that reviewed exact commit. Keep promotion, Fedora deployment, NAS mutation, and arm64 unauthorized

### Signed Handoff

[Agent Message] From: technical_architect To: product_manager

PASS investigation. Authorize TASK-002 to replace only both current root Dockerfile Wolfi defaults `sha256:a31344ab2cb8618db84f535eec56f76f6178b142cb92cb2e48676cc2dcebea72` with reviewed index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`, requiring `linux/amd64` child `sha256:9e7b7ba0080f84a03d95b42b80dd2e03f2d9169163a390230a3a6e53c03361dd`. The resulting Dockerfile must hash to `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d` and remain byte-identical to the prior TASK-014-approved file. Preserve all Python 3.13.15-r4, uv, Rust, lock, Cargo, source, runtime, entrypoint, and deployment inputs. Rebuild and requalify current source on amd64 from committed defaults; do not reuse prior image success. Treat rolling APK resolution as retention-bound evidence, not immutable closure. Retain exact signed indexes/artifacts now and require a separate immutable mirror or foundation-image design before claiming reproducible promotion. Arm64, promotion, Fedora/NAS mutation, build overrides, and deployment remain unauthorized
