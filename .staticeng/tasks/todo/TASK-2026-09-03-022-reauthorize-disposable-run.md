---
id: TASK-2026-09-03-022-reauthorize-disposable-run
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

# Task: Reauthorize disposable run

## Objective

Authorize one final replacement disposable lifecycle after the exact Redis acquisition failure was proven to be reference normalization and corrected.

## Acceptance Criteria

- [x] AC-1: Retain exact TASK-020 PostgreSQL/Redis identities and cached-image policy.
- [x] AC-2: Authorize exactly one run only after Tech Lead source approval of canonical comparison.
- [x] AC-3: Preserve all TASK-019 isolation, ownership, secret, cleanup, production-invariant, and no-deployment controls.
- [x] AC-4: Any failure consumes authorization and returns to PMA; no automatic retry.
- [x] AC-5: No runtime mutation while specifying.

## Handoff

[Agent Message] From: product_manager To: business_analyst

TASK-021 proved Redis availability and Reopen 13 fixes only canonical repository spelling without changing immutable identity. PMA authorizes one final replacement run after Tech Lead source approval, under every TASK-019/020 boundary, with no retry. Amend SCR/task; no runtime mutation.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary

Amended the approved integration SCR to authorize exactly one final replacement TASK-018 disposable lifecycle after Tech Lead approves the canonical Docker Hub repository-digest comparison and tests. The authorization is consumed when the runner is invoked, and every outcome prohibits retry

### Work Performed

- Retained the exact TASK-020 PostgreSQL 16.15 and Redis 7.4.11 `linux/amd64` child-manifest, OCI config, version, digest-reference, and verified-cache subjects without substitution
- Required Tech Lead approval that canonicalization changes repository spelling only while preserving exact registry trust, official-image namespace, and full manifest digest checks
- Preserved exact config/image ID, operating system, architecture, version, explicit daemon endpoint, and `--pull never --platform linux/amd64` create-time checks
- Defined invocation as the consumption boundary so startup, preflight, resource, lifecycle, cancellation, timeout, ambiguity, cleanup, evidence, and tooling failures all consume the one final authorization
- Prohibited automatic or manual retry, continuation through another invocation, replacement command, second lifecycle, mutable reference, fallback, retag, image removal, and prune while retaining TASK-020 acquisition order
- Preserved every TASK-019 isolation, ownership, secret, cancellation, cleanup, production-invariant, zero-resource, no-deployment, and Fedora/NAS production control
- Performed no Docker command, image operation, host or service access, database or registry action, deployment, Fedora action, or NAS runtime mutation

### Acceptance Criteria Coverage

- **AC-1: PASS.** The SCR retains the exact TASK-020 PostgreSQL manifest/config pair `sha256:075f7ba66bc9b3ce7d6b8b635208ff61cd7cf1a67d71ec530eec5d7ae0cbe571` / `sha256:75f5a96988cdf694a215073c3e9c001b706b371e2f94df3967f2efdec2787f6b` and Redis pair `sha256:1db42ccef14898aa29bae778452d567534b59c107129cbc1163fb552de184d3c` / `sha256:5509c0097c6064aa8a3b1df58f1d950e67090fffa6678ae8f3f1dc2385f12deb`, all on `linux/amd64`; verified cached layers may remain
- **AC-2: PASS.** Exactly one final invocation is authorized only after Tech Lead approves canonical Docker Hub repository identity plus exact full-digest comparison and hostile near-match tests
- **AC-3: PASS.** All TASK-019 exact-daemon, run-unique ownership, collision, synthetic-state, owner-only secret, internal-network, loopback-only exposure, cancellation, cleanup, NAS production-invariant, zero-resource, no-deploy, and Fedora/NAS controls remain mandatory
- **AC-4: PASS.** Authorization is consumed at runner invocation. Every success, failure, stop, cancellation, timeout, ambiguity, pre-resource outcome, cleanup result, or evidence failure ends the authorization and returns control to PMA without retry
- **AC-5: PASS.** This specification task changed documentation and governance artifacts only; no runtime action or mutation occurred

### Documentation Impact

Updated `.staticeng/docs/scrs/SCR-2026-09-01-001-upstream-main-integration.md` as the approved operational source of truth, completed this task, added evidence, and updated task registries. `.staticeng/docs/scrs/current.md` remains correct. No product overview, feature list, architecture, technical, or CodeMap update is required because this is a one-run qualification authorization and changes no steady-state product behavior

### Open Risks

Tech Lead has not yet approved Reopen 13 canonical comparison and tests, so invocation remains prohibited. Once invoked, any failure consumes the final authorization even if no task resource is created. Cleanup and zero-resource proof remain mandatory after failures but cannot restore authorization. TASK-006 and Fedora remain blocked unless the final run succeeds and receives the separately required reviews

### Recommended Next Step

PMA should route TASK-018 Reopen 13 to Tech Lead for source/test review. On PASS, Tech Lead may invoke the runner exactly once under the amended SCR, then must stop and return the result to PMA without retry

### Signed Handoff

[Agent Message] From: business_analyst To: product_manager

TASK-022 PASS. The SCR now authorizes exactly one final TASK-018 disposable invocation only after Tech Lead approves canonical Docker Hub repository-plus-exact-digest comparison and hostile tests. Exact TASK-020 PostgreSQL/Redis identities and cache policy remain unchanged, and all TASK-019 isolation, security, ownership, cancellation, cleanup, production-invariant, zero-resource, no-deployment, and Fedora/NAS boundaries remain mandatory. Invocation consumes authorization; every outcome, including pre-resource failure, cancellation, timeout, or ambiguity, prohibits retry and returns to PMA. No runtime mutation occurred
