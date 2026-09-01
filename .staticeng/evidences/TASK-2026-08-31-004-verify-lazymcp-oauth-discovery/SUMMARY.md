# QA Verification Summary

## Verdict

**REJECT**

The focused automated selection passes, but the implementation and evidence do not satisfy the approved SCR's required coverage or closure gates. No implementation or test files were edited during QA

## Findings

1. **High: Required Docker candidate and smoke verification are absent.** The implementation evidence explicitly records AC-8 as blocked and provides no immutable digest, aggregate metadata smoke, exact 401 challenge, authorized initialize/tool invocation, reconnect check, `/mcp`, MCP REST, readiness, or upstream integration smoke. SCR AC-6 requires this gate, so the candidate is not promotion-ready
2. **High: Required audience and challenge matrices are materially incomplete.** Admission has one automated mismatch case, scope A token against scope B. There is no admission matrix proving aggregate, scoped, and toolset tokens are accepted only at their exact audience and rejected across aggregate, two scopes, and toolsets. There is also no real transport 401 matrix for all three resource forms, no-token versus invalid-token, selection-header invariance, or legacy unscoped-token rejection on each LazyMCP route
3. **High: Authorization fail-closed coverage is incomplete.** The single DCR test checks three successful resource shapes and one generic mismatch. It does not test malformed, foreign-origin, rewritten `/mcp`, case-different, encoded, or cross-kind replay at authorization, code redemption, and refresh. The implementation's candidate classifier also does not recognize encoded or case-varied LazyMCP paths, allowing them to enter the legacy unscoped authorization branch instead of returning `invalid_target` (`.staticeng/evidences/TASK-2026-08-31-004-verify-lazymcp-oauth-discovery/logs/06-encoded-candidate-gap.log`)
4. **Medium: Discovery security and root-path requirements are unverified.** Tests cover six aliases only at an empty root and generic unknown identifiers. They do not cover non-empty root paths, trusted forwarded external-base handling, hostile header rejection, duplicate roots, trailing-slash discovery aliases, existing/hidden/unauthorized identifier indistinguishability, or route-order collisions
5. **Medium: Static gates do not close cleanly.** Independent focused tests pass 443/443, but an all-touched lint invocation fails in unrelated dirty `proxy_server.py`, and direct basedpyright reveals task-line `Final` redefinition errors in `user_api_key_auth_mcp.py` alongside baseline debt. The implementation-provided focused type log is not sufficient evidence for every touched file. Global `staticeng_validate` and Docker remain unresolved

## Acceptance Criteria Coverage

- **AC-1: FAIL.** Runtime and test diffs were reviewed; missing SCR cases are listed in findings 2 through 4
- **AC-2: PARTIAL.** Independent focused selection passed 443 tests with no failures or skips (`.staticeng/evidences/TASK-2026-08-31-004-verify-lazymcp-oauth-discovery/logs/01-independent-focused.log`), but mandatory Docker/smoke and complete mapped verification cannot be considered closed
- **AC-3: FAIL.** Focused lint passes excluding unrelated `proxy_server.py` (`.staticeng/evidences/TASK-2026-08-31-004-verify-lazymcp-oauth-discovery/logs/04-task-owned-lint-without-unrelated-proxy.log`), but touched-file lint/type closure is not clean and exact cross-resource rejection lacks the required matrix
- **AC-4: FAIL.** Existing mapped unit evidence provides useful `/mcp`, MCP REST, permission, and upstream-auth regression coverage, but the required immutable candidate smoke is missing and preservation is therefore insufficient for promotion
- **AC-5: PASS.** This signed reject report records exact findings and secret-free evidence paths

## Verification Map

- **Unit/integration:** Parser, metadata builders/routes, DCR/session-token persistence, admission mismatch, component allowlist, and mapped auth regressions
- **E2E/smoke:** Required but not run; immutable Docker candidate unavailable in the shared dirty worktree
- **Manual review:** SCR, architecture handoff, implementation task, implementation evidence, task-owned runtime/test diffs, test assertions, and skipped-test output

## Documentation Impact

The steady-state architecture document exists and is cross-linked. No additional product documentation is required. This QA task adds evidence and task updates only

## Open Risks

Audience widening or incorrect challenges can remain undetected across aggregate, scope, and toolset routes. Encoded or case-varied LazyMCP resource requests can enter the legacy unscoped authorization path. Runtime behavior behind a reverse proxy/root path and in the candidate container remains unverified

## Recommended Next Step

PMA should reopen the original implementation task. Require the missing authorization/admission/challenge/discovery matrices, fail-closed candidate handling, clean touched-file static gates, and an isolated immutable Docker candidate with all SCR smoke checks before QA reruns this task

[Agent Message] From: qa_engineer To: product_manager

REJECT. Independent focused tests pass, but mandatory Docker smoke is absent, exact audience/challenge/security matrices are incomplete, and malformed LazyMCP-shaped authorization inputs can fall into the legacy unscoped branch. Reopen the implementation task using the findings and evidence in this packet

## Reopen 1 Review

### Verdict

**PASS FOR DOCKER CANDIDATE BUILD**

The reopened implementation closes the prior code, test, and static-gate findings. The immutable Docker candidate and smoke gate remain intentionally pending and are the next required verification stage before final implementation closure

### Prior Finding Closure

1. **Docker candidate:** Not yet executed by design. The reviewed code and automated gates are now sufficient to allow an isolated immutable candidate build to proceed. Final SCR AC-6 and implementation AC-8 remain pending until candidate smoke passes
2. **Audience and challenge matrices: CLOSED.** Tests now prove exact admission for aggregate, scope, and toolset audiences; reject legacy unscoped sessions on all three; reject cross-scope and cross-kind replay; verify no-token and invalid-key challenges; and prove selection headers do not alter resource identity
3. **Authorization fail-closed coverage: CLOSED.** Authorization now detects case-varied, encoded, malformed, and foreign LazyMCP-shaped candidates and returns `invalid_target` without a connect-flow cookie. Code and refresh matrices cover missing, trailing-slash, `/mcp`, two-scope, aggregate, and toolset mismatches
4. **Discovery/root/proxy security coverage: CLOSED.** Tests cover non-loopback HTTPS enforcement, loopback HTTP, configured external base, trusted-proxy root paths, hostile untrusted host/forwarded headers, exact generic metadata aliases, and original-path preservation for all route owners and trailing-slash aliases
5. **Static gates: CLOSED FOR TASK CHANGES.** Independent Ruff and focused basedpyright pass. The prior task-line `Final` redefinition errors are gone, no new suppressions were added, and `git diff --check` passes. Broad legacy type debt remains outside this task's changed contract

### Independent Verification

- Critical unit/integration matrix: **493 passed, 0 failed, 0 skipped** (`.staticeng/evidences/TASK-2026-08-31-004-verify-lazymcp-oauth-discovery/logs/07-reopen1-independent-critical.log`)
- Task-touched focused Ruff: **PASS** (`.staticeng/evidences/TASK-2026-08-31-004-verify-lazymcp-oauth-discovery/logs/08-reopen1-independent-lint.log`)
- Canonical resource and signed token basedpyright: **0 errors** (`.staticeng/evidences/TASK-2026-08-31-004-verify-lazymcp-oauth-discovery/logs/09-reopen1-independent-typecheck.log`)
- Repository diff whitespace validation: **PASS** (`.staticeng/evidences/TASK-2026-08-31-004-verify-lazymcp-oauth-discovery/logs/10-reopen1-diff-check.log`)
- Independent malformed/case/encoding/foreign-origin probes: **PASS** (`.staticeng/evidences/TASK-2026-08-31-004-verify-lazymcp-oauth-discovery/logs/11-reopen1-independent-boundary-probes.log`)
- Developer complete mapped regression: **1067 passed, 0 failed, 0 skipped** (`../TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/08-reopen1-mapped-tests.log`)

### Acceptance Criteria Coverage After Reopen

- **AC-1: PASS.** Updated runtime and test diffs cover the approved SCR and close every prior missing-case finding
- **AC-2: PASS FOR PRE-CANDIDATE GATE.** Independent critical tests and the complete mapped suite have no failures or skips; Docker smoke remains the next distinct gate
- **AC-3: PASS.** Focused lint/type gates pass and exact cross-resource rejection is independently verified
- **AC-4: PASS FOR PRE-CANDIDATE GATE.** Mapped regressions sufficiently cover `/mcp`, MCP REST, permissions, route ownership, and upstream auth to authorize candidate construction; live candidate preservation smoke remains mandatory
- **AC-5: PASS.** This signed reopen review records closure status and exact evidence paths

### Docker Decision

**Docker candidate build may proceed.** Build one isolated immutable candidate from the reviewed task changes and intended base revision. Do not promote it until secret-free smoke verifies the exact discovery aliases and challenge, authorized initialize/tool invocation, reconnects without discovery 404s, readiness, `/mcp`, MCP REST, and upstream MCP integrations using the same digest

### Remaining Risk

No unresolved code-level QA blocker remains. Runtime packaging, component wiring, and integration behavior are unverified until the immutable candidate smoke gate completes. Global StaticEng CodeMap debt and broad legacy type debt remain external repository concerns, not regressions introduced by this task

[Agent Message] From: qa_engineer To: product_manager

PASS FOR DOCKER CANDIDATE BUILD. Reopen 1 closes all prior code, matrix, proxy/root, audience, challenge, and task-static findings. The immutable candidate may now be built; final closure still requires the SCR smoke suite on that exact digest
