---
id: TASK-2026-08-31-003-implement-lazymcp-oauth-discovery
complexity: complex
track: implementation
slice: logic
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 7
---

# Task: Implement LazyMCP OAuth discovery

## Objective

Implement the approved RFC 9728 discovery, exact challenges, DCR resource binding, and audience isolation for all three LazyMCP public resource shapes while preserving `/mcp`, MCP REST, permissions, and upstream authentication.

## Acceptance Criteria

- [ ] AC-1: Both discovery forms return HTTP 200 and equivalent valid metadata for aggregate, scoped, and toolset LazyMCP resources.
- [ ] AC-2: Every metadata `resource` exactly equals the trusted canonical public endpoint and generic metadata leaks no identifier existence.
- [ ] AC-3: Every LazyMCP 401 advertises its exact path-inserted metadata URL with correct invalid-token behavior.
- [ ] AC-4: Authorization codes, access tokens, and refresh tokens bind to one exact LazyMCP resource and reject cross-resource replay without granting permissions.
- [ ] AC-5: `/mcp`, MCP REST, LazyMCP selection, unknown-name rejection, toolset/group/key/team/tool permissions, and upstream auth remain unchanged.
- [ ] AC-6: Focused and complete mapped tests pass with no required skips or failures; touched files pass lint and type checking.
- [ ] AC-7: Steady-state architecture documentation and a complete Evidence Packet are produced.
- [ ] AC-8: A candidate Docker image builds and passes secret-free smoke verification without replacing the running production container.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/` with `SUMMARY.md` mapping AC-1 through AC-8 and `logs/` containing focused tests, mapped tests, lint, type checking, Docker build, and smoke outputs. UI screenshots are not required.

## Acceptance Criteria Verification Map

- [ ] AC-1 through AC-5: focused unit/integration regressions and mapped suites
- [ ] AC-6: test, lint, and type logs
- [ ] AC-7: doc review and Evidence Packet
- [ ] AC-8: immutable candidate image identity and isolated smoke logs

## Handoff

[Agent Message] From: product_manager To: developer

Do not begin until PMA supplies the completed architecture handoff and changes status to active. Preserve all unrelated dirty changes and treat all existing CodeMaps as task-owned but do not regenerate or rewrite them unless required for touched module accuracy. Do not replace, restart, or mutate the currently running production container.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

Implemented the approved canonical resource, six discovery aliases, exact LazyMCP challenges, DCR/code/access/refresh binding, exact audience admission, original-path preservation, component allowlisting, mapped tests, architecture contract, local CodeMaps, and evidence packet

AC-1 through AC-7 are satisfied, subject to the repository's pre-existing global StaticEng CodeMap validation debt. AC-8 is blocked because an immutable isolated candidate cannot be produced truthfully from the heavily dirty shared worktree without including unrelated source changes. No production container or deployment was inspected or mutated

Evidence: `.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/SUMMARY.md`

## Reopen History

### Reopen 1 - Independent QA and security rejection

Reopened on 2026-08-31 after TASK-004 and TASK-005 rejected malformed/case-varied LazyMCP fallback, untrusted authority and non-loopback HTTP acceptance, incomplete explicit-key challenge conversion, and missing negative/root/proxy/audience/selection-header/original-path matrices

Developer corrected the runtime boundaries and expanded mutation-sensitive regression coverage. Candidate construction remains intentionally deferred pending independent re-review, as directed by PMA

Reopen verification passed 163 focused tests and 1067 mapped tests. Ruff passed all task-touched Python files. Focused basedpyright passed with zero errors; the QA-reported task-line `Final` redefinition findings are fixed, while the direct broad run continues to report established file-wide legacy debt documented in the evidence packet

### Reopen 2 - Trusted source and classifier preservation

Reopened after the Tech Lead Reopen 1 review identified three remaining issues. Invalid non-empty `PROXY_BASE_URL` now fails closed before request-base fallback. The loopback exception now requires both literal loopback authority and a loopback request peer. LazyMCP candidate classification now recognizes malformed intended path families without searching the entire URL, preserving legacy `/mcp` resources containing `lazymcp`

Reopen 2 verification passed 169 focused tests and 1069 mapped tests. Ruff passed all task-touched Python files and focused basedpyright passed with zero errors. Candidate construction remains intentionally deferred pending independent approval

### Reopen 3 - Slash-containing legacy MCP preservation

Reopened to correct the remaining classifier preservation defect. Once a same-origin resource path enters the legacy `/mcp` namespace, all subsequent segments remain legacy. `/mcp/team/lazymcp` is now covered at classifier/parser and real aggregate authorization/DCR boundaries while malformed intended LazyMCP shapes continue to fail closed

Reopen 3 verification passed 171 focused tests and 783 bounded mapped tests. Ruff passed all task-touched Python files and focused basedpyright passed with zero errors. Candidate construction remains intentionally deferred

### Reopen 4 - Trusted-root-aware classification

Reopened to resolve the configured-root collision. Candidate classification now receives the request and evaluates intended LazyMCP path families relative to the validated trusted base/root. With `PROXY_BASE_URL=https://gateway.example/mcp`, `/mcp/LazyMCP` fails `invalid_target` without a flow; in the normal root context `/mcp/team/lazymcp` remains legacy

Reopen 4 verification passed 173 focused tests and 784 bounded mapped tests. Ruff passed all task-touched Python files and focused basedpyright passed with zero errors. Candidate construction remains intentionally deferred

### Reopen 5 - Docker-style trusted-base regression coverage

Reopened after TASK-015 proved retained-candidate 404 and challenge fallback were intentional trusted-base failures rather than route-registration defects. Test-only coverage now pins all six discovery aliases to generic 404 for an untrusted non-loopback HTTP Docker peer without `PROXY_BASE_URL`, and exact success under reserved HTTPS `PROXY_BASE_URL=https://candidate.invalid`. Aggregate, scoped, and toolset challenge builders likewise return no Host-derived challenge without trust and exact configured challenges with trust. Runtime source and candidate inputs are unchanged

### Reopen 4 - Trusted-root-aware classification

Tech Lead confirmed the legacy path fix but found a trusted-root collision when the configured external root is `/mcp`: malformed `{base}/LazyMCP` can be mistaken for legacy because classification is not root-aware. Make candidate classification use the trusted normalized root, preserve true `/mcp/team/lazymcp` legacy resources, reject malformed `{trusted-root}/LazyMCP`, and add parser plus real DCR regressions with `PROXY_BASE_URL=https://gateway.example/mcp`

### Reopen 5 - Candidate smoke trust-policy regressions

TASK-015 proved the candidate's six live 404s and challenge fallback were intentional fail-closed behavior because Docker-bridge smoke omitted a trusted HTTPS `PROXY_BASE_URL`; route registration and matching are correct. Add focused regressions proving discovery/challenges fail closed without a trusted public base and succeed with an explicit reserved HTTPS base. Do not weaken runtime trust policy or alter candidate runtime source. Rerun bounded tests/static gates and return for review; the retained image may then be re-smoked without rebuilding because only tests/evidence change.

### Reopen 6 - Toolset admission before database resolution

TASK-006 Reopen 5 proved aggregate/scoped discovery and challenges pass, but `/toolset/{name}/lazymcp` returns 503 before admission when no database exists. Implement TASK-016's reviewed ordering: preserve public toolset name in server-owned context, run shared LazyMCP admission first so missing/invalid credentials receive exact catalog-free challenges, then resolve and bind toolset ID once for admitted requests. Preserve authenticated database-down 503, unknown 404, unauthorized 403, valid scoped success, non-enumeration, and all existing toolset permissions. Add mutation-sensitive route/auth/toolset tests, update evidence/docs if needed, run mapped/static gates, and return for security review before a new candidate freeze.

### Reopen 7 - Anonymous admission cannot bypass toolset scope

Tech Lead rejected Reopen 6 because intentionally anonymous successful admission can return `user_api_key_auth=None`, causing name resolution and `_apply_toolset_scope()` to be skipped and the request to continue as unscoped LazyMCP. Treat admission completion separately from principal presence; every explicit toolset request must resolve the name and reach an explicit safe authorization outcome after admission, never aggregate fallback. Add anonymous DB-down/unknown/known cases, explicit unauthorized 403, exception reset, concurrent name isolation, and name-plus-ID double-binding failure tests. Preserve challenge ordering and existing authenticated behavior, then return to the same review before candidate freeze.

### Reopen 7 - Anonymous-admission authorization closure

Explicit toolset requests now resolve after every successful admission result, including `UserAPIKeyAuth=None`; anonymous database-down and unknown outcomes remain 503/404, while a known toolset reaches explicit 403 rather than unscoped fallback. Added explicit unauthorized 403, exception reset, concurrent different-name isolation, and name-plus-ID fail-closed regressions while preserving challenge-before-lookup ordering

### Reopen 6 - Admission-before-toolset-resolution

Implemented TASK-016's two-owner ordering. The explicit toolset LazyMCP route now preserves `_original_path`, rewrites only the internal path, and sets a server-owned toolset-name ContextVar with guaranteed reset. Shared admission runs before any Prisma or toolset lookup. After admission, the server resolves name to ID once and applies existing toolset scope once, preserving admitted 503/404/403/scoped-success behavior and existing legacy ID-context routes

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. AC-1 through AC-7 pass. AC-8 passes for immutable build, packaging, discovery, challenge, initialize, reconnect, preservation, production invariants, and cleanup; a real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-003 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
