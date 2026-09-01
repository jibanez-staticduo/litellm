---
id: TASK-2026-08-31-001-spec-lazymcp-oauth-discovery
complexity: standard
track: spec
slice: foundation
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: null
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: Specify LazyMCP OAuth discovery

## Objective

Create an approval-ready behavior contract for RFC 9728 metadata, OAuth challenges, DCR resource binding, and permission isolation across `/lazymcp`, `/lazymcp/{scope}`, and `/toolset/{name}/lazymcp` without changing runtime code.

## Acceptance Criteria

- [x] AC-1: Define both OAuth protected-resource discovery forms clients use for each supported LazyMCP resource.
- [x] AC-2: Require metadata `resource` to equal the canonical public LazyMCP endpoint exactly.
- [x] AC-3: Require every LazyMCP `WWW-Authenticate` challenge to advertise the corresponding metadata URL.
- [x] AC-4: Define DCR resource/audience binding that prevents privilege expansion across aggregate, scopes, and toolsets.
- [x] AC-5: Preserve observable `/mcp`, MCP REST, upstream authentication, and existing permission behavior.
- [x] AC-6: Define focused tests, mapped regression suites, lint, type checking, Docker candidate smoke tests, and rollback requirements.
- [x] AC-7: Record documentation impact, security constraints, non-goals, and Product Owner approval state.

## Expected Evidence

- SCR under `.staticeng/docs/scrs/` with numbered ACs and no secrets.
- Signed handoff mapping AC-1 through AC-7 to document sections.
- No source, test, runtime, credential, image, or deployment mutation.

## Handoff

[Agent Message] From: product_manager To: business_analyst

Use `.opencode/plans/lazymcp-oauth-discovery.md`, the current MCP authorization implementation, and official MCP/RFC 9728 behavior. Produce the smallest complete SCR. The user has explicitly approved implementation of the listed behavior in this session, so record Product Owner approval without broadening scope. Preserve all existing dirty changes and CodeMaps. Return the shared output contract with exact file references.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary

- Created approved SCR `SCR-2026-08-31-001-lazymcp-oauth-discovery` as the implementation behavior contract
- Reconciled the approved plan, current MCP authorization implementation, RFC 9728, and MCP authorization requirements without runtime mutation

### Work Performed

- Defined the canonical aggregate, scoped, and toolset resources and both discovery URL forms
- Defined exact challenge, authorization-code, access-token, refresh-token, audience-isolation, permission-preservation, security, verification, rollout, and rollback requirements
- Added the SCR to the approved registry; no runtime code, tests, credentials, images, deployments, or CodeMaps were changed

### Acceptance Criteria Coverage

- AC-1: PASS. SCR section `Supported Resources and Discovery` defines path-inserted and path-appended forms for all three resource shapes
- AC-2: PASS. SCR sections `Supported Resources and Discovery` and `Security Constraints` require exact canonical public-resource equality and narrowly limit trailing-slash canonicalization
- AC-3: PASS. SCR section `Authentication Challenges` maps each LazyMCP 401 to its exact path-inserted metadata URL and preserves invalid-token behavior
- AC-4: PASS. SCR section `Authorization, DCR, and Audience Isolation` binds authorization, code, access token, and refresh token to one exact resource and prohibits cross-resource privilege expansion
- AC-5: PASS. SCR section `Compatibility and Preservation` protects `/mcp`, MCP REST, per-server MCP, permissions, and all upstream authentication modes
- AC-6: PASS. SCR section `Verification Contract` defines focused tests, mapped suites, lint, type checking, Docker candidate smoke gates, staged promotion, and digest rollback
- AC-7: PASS. SCR sections `Documentation Impact`, `Security Constraints`, `Non-Goals`, and `Approval` record all required decisions and Product Owner approval without secrets

### Documentation Impact

- Added `.staticeng/docs/scrs/SCR-2026-08-31-001-lazymcp-oauth-discovery.md` and registered it as approved in `.staticeng/docs/scrs/current.md`
- Implementation must publish `.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md`; no `PRODUCT_OVERVIEW.md` or `FEATURES_LIST.md` update is required for this protocol correction

### Open Risks

- Current DCR behavior can treat unresolved resource values as aggregate; implementation must fail closed for every LazyMCP resource mismatch rather than preserve that fallback
- The implementation plan shows an empty `scopes_supported` array, but RFC 9728 requires empty multi-value fields to be omitted; the approved SCR follows the RFC requirement
- Repository-wide StaticEng validation remains blocked by pre-existing missing CodeMaps; this task preserved all CodeMaps and introduced no new validation finding

### Recommended Next Step

- PMA should create and dispatch an atomic implementation task using this approved SCR, followed by independent security-focused review and QA before any Docker promotion

## Signed Handoff

[Agent Message] From: business_analyst To: product_manager

SCR `SCR-2026-08-31-001-lazymcp-oauth-discovery` is approved and implementation-ready. AC-1 maps to `Supported Resources and Discovery`; AC-2 maps to `Supported Resources and Discovery` and `Security Constraints`; AC-3 maps to `Authentication Challenges`; AC-4 maps to `Authorization, DCR, and Audience Isolation`; AC-5 maps to `Compatibility and Preservation`; AC-6 maps to `Verification Contract`; AC-7 maps to `Documentation Impact`, `Security Constraints`, `Non-Goals`, and `Approval`

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-001 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
