---
id: TASK-2026-09-03-020-authorize-disposable-dependency-pull
complexity: tiny
track: spec
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-018-fix-dcr-maintenance-client
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: Authorize disposable dependency pull

## Objective

Authorize one replacement disposable run after pinning and pre-pulling immutable PostgreSQL and Redis dependency images before task-resource creation.

## Acceptance Criteria

- [x] AC-1: Permit only exact digest-pinned PostgreSQL and Redis images with recorded platform/config IDs.
- [x] AC-2: Require pulls and identity verification before creating network, volume, or containers.
- [x] AC-3: Image pulls may remain cached; every task resource must be removed automatically on all failures.
- [x] AC-4: Authorize exactly one replacement TASK-019 disposable lifecycle run after source review.
- [x] AC-5: Preserve synthetic-only, internal-network, production-invariant, no deployment, and Fedora/NAS production boundaries.

## Handoff

[Agent Message] From: product_manager To: business_analyst

The first authorized run failed only because immutable dependencies were not pre-acquired, and Tech Lead cleaned the one leaked owned volume. PMA authorizes one replacement run after source freezes exact PostgreSQL 16 and Redis 7 digests, pulls/verifies them before creating any task resource, and regression-proves cleanup on missing-image container failure. Amend SCR; no runtime mutation now.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary

Amended the approved integration SCR to authorize exactly one replacement TASK-018 disposable lifecycle after exact `linux/amd64` PostgreSQL 16.15 and Redis 7.4.11 manifest/config identities are frozen, source-reviewed, pulled, and verified before any task resource exists

### Work Performed

- Froze PostgreSQL child manifest `sha256:075f7ba66bc9b3ce7d6b8b635208ff61cd7cf1a67d71ec530eec5d7ae0cbe571` with config `sha256:75f5a96988cdf694a215073c3e9c001b706b371e2f94df3967f2efdec2787f6b`
- Froze Redis child manifest `sha256:1db42ccef14898aa29bae778452d567534b59c107129cbc1163fb552de184d3c` with config `sha256:5509c0097c6064aa8a3b1df58f1d950e67090fffa6678ae8f3f1dc2385f12deb`
- Required one explicit `linux/amd64` pull of each exact digest and local repository-digest, config/image-ID, OS, and architecture verification before network, volume, or container creation
- Required missing-image and partial-create regression coverage plus automatic ownership-checked reverse cleanup and exact zero-resource proof on every failure
- Allowed acquired image layers to remain cached while prohibiting image removal, prune, mutable references, automatic create-time pulls, fallback, retag, and production image mutation
- Preserved every TASK-019 daemon, namespace, synthetic-state, internal-network, loopback, cancellation, production-invariant, no-deploy, and Fedora/NAS production boundary
- Performed no Docker pull, resource creation, host access, service change, database access, registry write, deployment, Fedora action, or NAS runtime mutation

### Acceptance Criteria Coverage

- **AC-1: PASS.** The SCR records exact official PostgreSQL 16.15 and Redis 7.4.11 `linux/amd64` child-manifest and OCI config identities; source tags and indexes are provenance only
- **AC-2: PASS.** Both exact-platform pulls and all local identity checks must pass through the selected daemon before any task network, volume, or container can be created
- **AC-3: PASS.** Cached image layers may remain because they are not task resources. Every failure must automatically clean all ownership-proven current-run resources and prove zero retained names, IDs, and complete-label matches; manual cleanup cannot rescue acceptance
- **AC-4: PASS.** The first authorization remains consumed. Exactly one replacement lifecycle is authorized only after Developer implementation and Tech Lead source/test approval, and it is consumed by the first task-resource create command
- **AC-5: PASS.** All TASK-019 synthetic-only, internal-network, loopback-only, active-cancellation, exact-ownership, NAS production-invariant, no-deployment, and Fedora/NAS production boundaries remain mandatory

### Documentation Impact

Updated `.staticeng/docs/scrs/SCR-2026-09-01-001-upstream-main-integration.md` as the approved operational source of truth and updated task registries. `.staticeng/docs/scrs/current.md` remains correct. No product overview, feature list, architecture, technical, or CodeMap update is required because this is a one-run qualification exception and changes no steady-state product behavior

### Open Risks

The current TASK-018 source still uses mutable dependency tags and has not proved automatic cleanup for the failure that left a volume. No dependency pull or replacement lifecycle is authorized until Developer implements the exact identities and operation order, the missing-image cleanup regression passes, and Tech Lead returns source approval. Any pull/preflight failure must stop before task resources and return to PMA without retry; any automatic residue is a blocking incident

### Recommended Next Step

PMA should hand TASK-018 Reopen 9 to Developer for the narrowly specified dependency and cleanup changes, then route it to Tech Lead for source/test review. Only after that PASS may Tech Lead execute the one replacement disposable lifecycle. TASK-006 and Fedora remain blocked

### Signed Handoff

[Agent Message] From: business_analyst To: product_manager

TASK-020 PASS. SCR `SCR-2026-09-01-001-upstream-main-integration` now authorizes exactly one replacement TASK-018 disposable lifecycle after source freezes and uses the exact official `linux/amd64` PostgreSQL 16.15 manifest/config pair `sha256:075f7ba66bc9b3ce7d6b8b635208ff61cd7cf1a67d71ec530eec5d7ae0cbe571` / `sha256:75f5a96988cdf694a215073c3e9c001b706b371e2f94df3967f2efdec2787f6b` and Redis 7.4.11 pair `sha256:1db42ccef14898aa29bae778452d567534b59c107129cbc1163fb552de184d3c` / `sha256:5509c0097c6064aa8a3b1df58f1d950e67090fffa6678ae8f3f1dc2385f12deb`. Tech Lead must approve source/tests first. The selected daemon must then pull each exact digest once with explicit `linux/amd64` and verify repository digest, config/image ID, OS, and architecture before any network, volume, or container exists. Cached images may remain; every task resource must clean automatically on every failure with retained name/ID and complete-label zero proof. The prior run remains consumed, and a pull/preflight failure, retry, identity change, residue, or second lifecycle requires new PMA authorization. All TASK-019 isolation, synthetic-only, internal-network, loopback, cancellation, NAS production-invariant, no-deploy, and Fedora/NAS production boundaries remain unchanged. No runtime mutation occurred
