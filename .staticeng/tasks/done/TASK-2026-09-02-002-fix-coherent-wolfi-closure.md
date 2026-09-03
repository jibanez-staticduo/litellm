---
id: TASK-2026-09-02-002-fix-coherent-wolfi-closure
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-011-qualify-upstream-isolated-candidate
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: Fix coherent Wolfi package closure

## Objective

Apply the independently approved minimal Docker packaging correction, verify exact build compatibility, and commit it before candidate qualification restarts.

## Acceptance Criteria

- [ ] AC-1: Change only approved Docker/package inputs and preserve all application behavior.
- [ ] AC-2: Clean detached amd64 build emits exact builder/final images with Python, glibc, uvloop, Prisma, Rust bridge, and native imports passing.
- [ ] AC-3: Dockerfile/static/source gates, provenance and rollback evidence pass; no production mutation.
- [ ] AC-4: Tech Lead reviews and commits/pushes correction to fork main only after gates pass.

## Handoff

[Agent Message] From: product_manager To: developer

TASK-001 architecture approval is complete. Change only `Dockerfile:4` and `Dockerfile:7` to OCI index `sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d`, preserving every other input. Verify resulting Dockerfile hash `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`, run the approved clean detached amd64 build/ABI/import/static gates, retain exact builder/final identities and evidence, and clean disposable resources. Do not commit/push yourself or mutate Fedora/NAS; Tech Lead will review and commit/push only if gates pass.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary

PASS for the authorized implementation and amd64 compatibility scope. Exactly the two approved root `Dockerfile` Wolfi defaults changed. The post-edit Dockerfile SHA-256 is `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`

Fresh no-cache `linux/amd64` builder and final builds from a detached worktree passed. Builder config ID is `sha256:f4f4c9a09d7a4855c88d9683ae133474e913696a6c21587197efc99114196ccb`; final config ID is `sha256:1b4e9b94c71d096ed59a89176af32c7066aecd5d19bfc4ec26727f7f2d183f45`. All disposable resources were removed after evidence capture, and production remained unchanged under credential-safe allowlisted observations

### Work Performed

- Verified source commit `9374aae27c93d509a12f167c6bb1f83815ed3db1`, pre-edit Dockerfile SHA-256 `e7e669bfd09b5beb9ec27fc1a976bf90232adf7144fda5def7a761e2ddbcad11`, exact two-line edit, post-edit hash, source preservation, and rollback
- Re-resolved exact Wolfi, uv, Rust, and UI OCI identities, then ran a native amd64 glibc/Python/math ABI preflight
- Built builder and final targets in a task-owned Docker-container BuildKit instance with `--no-cache`, `--pull=false`, committed defaults, exact source/task labels, and no argument override
- Captured builder/final package and embedded SPDX inventory, exact Rust/Python/glibc identities, venv linkage, Prisma, uvloop, LiteLLM Rust bridge/native imports, copied ELF, entrypoint/CMD, readiness, and shutdown results
- Removed the runtime container, images, builder, builder container, and caches; verified zero task-labelled resources and unchanged production identity/health
- Ran `git diff --check` and `staticeng_validate`; both pass. Full evidence is in `.staticeng/evidences/TASK-2026-09-02-002-fix-coherent-wolfi-closure/SUMMARY.md`

### Acceptance Criteria Coverage

- **AC-1: PASS.** Only the two approved root Dockerfile digest values changed outside StaticEng evidence/task state. Application behavior and every other build input are preserved
- **AC-2: PASS.** Fresh amd64 builder/final identities were emitted, and Python 3.13.15, glibc 2.44-r1, uvloop 0.21.0, Prisma, Rust bridge, native imports, copied ELF, entrypoint/readiness, and shutdown gates pass
- **AC-3: PASS FOR IMPLEMENTATION AND COMPATIBILITY.** Dockerfile/source/static/provenance/rollback/cleanup/production-preservation gates pass. Mutable APK retention and unavailable signature/aggregate-SBOM/comparative-scan tooling remain fail-closed promotion blockers
- **AC-4: PENDING TECH LEAD.** No commit or push was performed. The exact diff and evidence are ready for independent review

### Documentation Impact

No product, architecture, operator, or CodeMap documentation change is required. This correction restores an approved packaging contract without changing application behavior or navigable source structure

### Open Risks

- Public APK resolution is mutable and retention-bound; exact signed index bytes and all downloaded `.apk` files were not retained
- Cosign, Syft, Grype, Trivy, Docker Scout, and a functional Docker SBOM plugin are unavailable, so signature/attestation, aggregate SBOM, comparative scan, and Critical/High disposition remain promotion blockers
- Arm64 and all promotion/deployment paths remain unauthorized. TASK-011 must rerun from the reviewed correction commit

### Recommended Next Step

PMA should route the exact diff and Evidence Packet to Tech Lead for independent review and commit/push. Do not resume promotion, publication, Fedora/NAS mutation, deployment, or arm64 work

### Signed Handoff

[Agent Message] From: developer To: product_manager

PASS for authorized implementation and amd64 compatibility. Exactly the two approved root Dockerfile defaults changed, yielding SHA-256 `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d`. Fresh detached no-cache amd64 builder `sha256:f4f4c9a09d7a4855c88d9683ae133474e913696a6c21587197efc99114196ccb` and final `sha256:1b4e9b94c71d096ed59a89176af32c7066aecd5d19bfc4ec26727f7f2d183f45` passed ABI, native import, runtime, source, rollback, and static gates. All disposable resources were removed and production remained unchanged. No commit, push, deployment, Fedora/NAS mutation, production configuration access, or arm64 execution occurred. Mutable APK and unavailable supply-chain tooling remain fail-closed promotion blockers

## Tech Lead: Post Implementation Expectations

### Summary

PASS for the authorized source correction and amd64 compatibility gate. Independent review reproduces the exact two substitutions, Dockerfile SHA-256, patch SHA-256, prior-approved Dockerfile identity, cleanup state, production safety state, and StaticEng validation. The retained build evidence records exact builder/final config and manifest identities plus passing ABI, native import, entrypoint, readiness, and shutdown gates

### Work Performed

- Reviewed the task, parent rejection, approved architecture task, governing SCR, CodeMap, repository status, full diff, evidence, remotes, and recent history
- Recomputed Dockerfile SHA-256 `9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d` and patch SHA-256 `269cab0cc2d24322b3b542dc27c10b884cc593c6b5972ba2169056e1287b0a38`; confirmed byte identity with `514fd6bb8eb76760b6daf04db1dcfa8fd655b00f:Dockerfile`
- Confirmed the only application/build-source path changed is root `Dockerfile`, with exactly the approved build/runtime digest substitutions and no third semantic edit
- Reviewed retained builder/final identities and the Python, glibc, uvloop, Prisma, Rust bridge, representative native import, copied ELF, entrypoint, readiness, and shutdown evidence
- Independently confirmed zero task-labelled Docker resources, one repository worktree, no task Buildx builder, unchanged healthy production identity under the allowlisted formats, `git diff --check`, and `staticeng_validate`

### Acceptance Criteria Coverage

- **AC-1: PASS.** The application/build-source diff is exactly the two approved Wolfi digest substitutions; all other inputs and behavior remain unchanged
- **AC-2: PASS.** Retained evidence binds fresh no-cache amd64 builder config `sha256:f4f4c9a09d7a4855c88d9683ae133474e913696a6c21587197efc99114196ccb`, builder manifest `sha256:cfbbd3002425c510b3b4efef4e1bb4a8de5249422397f3d1f5a932dcbf3c80ac`, final config `sha256:1b4e9b94c71d096ed59a89176af32c7066aecd5d19bfc4ec26727f7f2d183f45`, and final manifest `sha256:71dac661d00ecf05693932ea88011625acc5e9500b53bdc7bcc0e7c5c455f12b` to passing ABI/native/runtime gates
- **AC-3: PASS FOR SOURCE AND COMPATIBILITY.** Exact diff/hash, OCI inputs, build labels, package inventories, rollback, production preservation, cleanup, and static gates pass. Mutable APK retention, signatures/attestations, aggregate SBOMs, comparative scans, and Critical/High disposition remain fail-closed release blockers
- **AC-4: PASS.** Tech Lead independently approved the correction for commit and a non-force push to fork `main`; publication, promotion, deployment, and arm64 remain unauthorized

### Documentation Impact

No product, architecture, operator, technical, or CodeMap documentation update is required. The task and evidence capture the packaging correction and its explicit release blockers

### Open Risks

- Public APK resolution remains mutable, and exact signed index bytes plus every downloaded APK were not retained
- Required signature, attestation, aggregate SBOM, comparative vulnerability scan, and Critical/High disposition gates remain unavailable and block release promotion
- TASK-011 must restart from the committed correction for complete isolated database, model, Responses, MCP/LazyMCP, OAuth, permission, real-tool, logging, and supply-chain qualification
- Arm64 remains metadata-only and unauthorized

### Recommended Next Step

PMA should reopen TASK-011 against the exact pushed correction commit. Do not publish a release image, promote a digest, deploy, mutate Fedora/NAS, or execute arm64 work yet

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. TASK-002 is technically complete for the exact two-line source correction and amd64 compatibility scope. Commit and push the reviewed correction to fork `main` without force, then restart TASK-011 from that exact commit. Release publication, promotion, deployment, Fedora/NAS mutation, and arm64 remain unauthorized
