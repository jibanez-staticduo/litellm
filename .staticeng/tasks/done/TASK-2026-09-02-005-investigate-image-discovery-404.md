---
id: TASK-2026-09-02-005-investigate-image-discovery-404
complexity: complex
track: investigation
slice: logic
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-02-006-fix-image-discovery-routing
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Investigate image-only LazyMCP discovery 404

## Objective

Explain why source cold-start tests pass all six RFC 9728 aliases while the exact built image advertises them in OpenAPI but returns 404, then define the smallest deterministic correction.

## Acceptance Criteria

- [x] AC-1: Reproduce exact image behavior and compare loaded modules/routes/feature registry/environment with source-test runtime.
- [x] AC-2: Trace Docker packaging, lazy discovery, OpenAPI generation, import order, root path, component mode, and precedence.
- [x] AC-3: Identify the exact discriminating input and prove root cause.
- [x] AC-4: Recommend minimal source/build/test correction, preservation gates, rollback, and candidate impact.
- [x] AC-5: Update task/evidence with signed handoff; no mutations.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Read TASK-011 Reopen 4 evidence and TASK-010 routing work. Use retained exact final image read-only. Compare cold source runtime with container runtime including installed package contents and lazy registry state, without production config. Research only; no edit/build/push/deploy. Return exact root cause and fix.

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

### Summary

The reported image-only routing regression is disproven. Exact image `sha256:eeb98cc84cd1f3b73ce1dc584ac9922e47515fc3db46beb8825283fddf6b2820` contains and registers all six routes. Its 404 responses are the intended fail-closed result when the non-loopback Docker request has no trusted public origin. `PROXY_BASE_URL=https://candidate.invalid` is the exact discriminating input: adding only that environment value changes all six responses from 404 to exact HTTP 200 metadata

### Work Performed

- Compared exact image and source bytes for `_lazy_features.py`, `proxy_server.py`, `discoverable_endpoints.py`, `lazymcp_public_resource.py`, and `_lazy_openapi_snapshot.json`; every SHA-256 matches exact source commit `a826c38dc0737afd9eef00a2e9f50d2413ca92eb`
- Inspected installed distribution metadata, console entrypoint, package contents, `sys.path`, route table, lazy registry ownership, OpenAPI, root path, final image entrypoint, and component packaging
- Reproduced six 404s with an unset or HTTP non-loopback `PROXY_BASE_URL`, then six exact 200 responses by setting only `PROXY_BASE_URL=https://candidate.invalid`
- Confirmed source cold-start tests explicitly set a valid HTTPS `PROXY_BASE_URL`, while TASK-011 Reopen 4's recorded isolated runtime configuration does not provide that required trusted-origin input
- Confirmed cleanup left zero `task005-*` containers and made no production, source, test, build, registry, host, push, or deployment change

### Acceptance Criteria Coverage

- [x] **AC-1:** Exact image behavior, installed modules/routes, lazy registry, package metadata, image environment and source runtime were compared read-only
- [x] **AC-2:** Docker packaging, OpenAPI snapshot injection, eager and lazy registration, route precedence, root path, component mode, and final monolithic entrypoint were traced
- [x] **AC-3:** The exact discriminator is proven as trusted public-origin configuration, specifically a valid HTTPS `PROXY_BASE_URL` for this non-loopback Docker harness
- [x] **AC-4:** The minimal correction is to fix the qualification harness and add a packaged-image regression; no application routing or build change is justified
- [x] **AC-5:** Evidence and signed handoff are complete, with no prohibited mutation

### Documentation Impact

Product and steady-state architecture documentation do not require changes because runtime behavior matches `.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md`. No CodeMap changes are required because no maintained source path or command changed

### Open Risks

- The app eagerly includes `discoverable_endpoints` but also leaves the same module in the lazy registry, so the first matching request re-includes duplicate route objects. This does not cause the 404 and must not be bundled into the qualification-harness correction without a separate scoped review
- OpenAPI describes route availability but cannot encode whether a request supplies a trusted public origin, so OpenAPI presence alone does not prove a request will receive metadata
- Candidate signing and attestation remain separate TASK-011 blockers and are not changed by this finding

### Recommended Next Step

PMA should revise TASK-006 from a routing fix to a qualification-harness and packaged-runtime regression task. The harness must start the candidate with `PROXY_BASE_URL=https://candidate.invalid`, assert all six exact resource documents over the live container, and assert the negative unset/non-loopback case remains 404. Rerun the corrected functional matrix first against this unchanged retained digest. If a repository image-level regression is then committed, build a new candidate from that reviewed test commit as required by the SCR. Do not weaken trusted-origin checks or infer a public origin from an untrusted Docker `Host` header

Evidence: `.staticeng/evidences/TASK-2026-09-02-005-investigate-image-discovery-404/SUMMARY.md`

## Signed Technical Architect Handoff

[Agent Message] From: technical_architect To: product_manager

ROOT CAUSE PROVEN. Exact image `sha256:eeb98cc84cd1f3b73ce1dc584ac9922e47515fc3db46beb8825283fddf6b2820` has all six live routes and matching source/package bytes. TASK-011 omitted the valid HTTPS `PROXY_BASE_URL` required for a non-loopback Docker peer, so the security contract intentionally returned 404. Setting only `PROXY_BASE_URL=https://candidate.invalid` makes all six aliases return exact HTTP 200 metadata. Correct the qualification harness and add image-level positive and fail-closed regressions; do not change routing or weaken origin trust
