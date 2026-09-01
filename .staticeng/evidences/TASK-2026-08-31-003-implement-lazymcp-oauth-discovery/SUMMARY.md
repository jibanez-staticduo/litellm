# Evidence Summary

## Acceptance Criteria Coverage

- **AC-1: PASS.** All six aggregate, scoped, and toolset discovery aliases return equivalent HTTP 200 JSON metadata in focused tests (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/01-focused-tests.log`)
- **AC-2: PASS.** The canonical parser enforces exact trusted-origin resource identities, generic unknown identifiers, one trailing-slash alias, and rejects ambiguous encodings and paths (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/01-focused-tests.log`)
- **AC-3: PASS.** Challenge builders and admission tests pin exact path-inserted metadata URLs and `invalid_token` semantics, with audience rejection before user reload (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/01-focused-tests.log`)
- **AC-4: PASS.** Authorization flow, code, access token, refresh token, strict redemption, rotation, and cross-resource rejection are covered for aggregate, scoped, and toolset resources (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/01-focused-tests.log`)
- **AC-5: PASS.** Complete mapped discovery, routing, admission, DCR, toolset, component, and MCP server suites passed: 1042 tests (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/02-mapped-tests.log`)
- **AC-6: PASS WITH EXTERNAL VALIDATION DEBT.** Focused 113 tests and mapped 1042 tests pass. Ruff and focused basedpyright pass (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/03-lint.log`, `.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/04-typecheck.log`). StaticEng remains blocked only by pre-existing broad CodeMap debt (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/05-staticeng-validation.md`)
- **AC-7: PASS.** The steady-state architecture contract, SCR cross-link, local source/test CodeMaps, task update, and complete secret-free evidence packet are present
- **AC-8: BLOCKED.** An isolated Docker candidate cannot be truthfully built from the heavily dirty shared worktree without incorporating unrelated source and CodeMap changes. Production was not mutated (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/06-docker-smoke.md`)

## Implementation

The implementation adds a single exact LazyMCP public-resource parser/builder, six explicit catalog-free metadata routes, exact challenge selection, resource persistence through gateway OAuth artifacts, strict code/refresh redemption, pre-policy exact audience admission, original-path preservation, and gateway component allowlisting. Existing `/mcp`, per-server, permission, and upstream authentication paths remain covered by mapped regressions

## Reopen 1

Independent QA and security findings are corrected. Malformed, encoded, foreign-origin, and case-varied LazyMCP authorization candidates now fail closed without creating a connect-flow cookie. Public authorities require configured `PROXY_BASE_URL`, the existing trusted-proxy policy, or a literal loopback request; non-loopback HTTP is rejected. Explicit-key and all tested LazyMCP 401 paths receive the exact resource challenge, independent of selection headers. Aggregate, two-scope, cross-kind, toolset, legacy-token, root-path, trusted/hostile proxy, HTTPS, and all route-owner `_original_path` matrices are covered

- Reopen focused tests: 163 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/07-reopen1-focused-tests.log`)
- Reopen mapped tests: 1067 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/08-reopen1-mapped-tests.log`)
- Reopen lint: pass (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/09-reopen1-lint.log`)
- Focused type check: 0 errors (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/10-reopen1-typecheck.log`)
- Broad legacy type debt analysis: task-line `Final` findings fixed; remaining output is established file-wide debt (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/12-reopen1-typecheck-analysis.md`)
- Docker candidate: intentionally not built pending independent re-review, per PMA direction

## Reopen 2

The three Tech Lead Reopen 1 findings are fixed without changing the previously approved behavior. Invalid non-empty `PROXY_BASE_URL` fails closed before request Host fallback. Loopback trust now requires both literal loopback authority and a loopback request peer. Candidate classification is path-family-specific and no longer rejects legacy `/mcp` resources merely because their authority, identifier, query, or unrelated URL text contains `lazymcp`

- Focused tests: 169 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/13-reopen2-focused-tests.log`)
- Mapped tests: 1069 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/14-reopen2-mapped-tests.log`)
- Ruff: pass (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/15-reopen2-lint.log`)
- Focused basedpyright: 0 errors (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/16-reopen2-typecheck.log`)
- Docker candidate: intentionally not built, per PMA direction

## Reopen 3

The final classifier preservation defect is corrected. Same-origin resources under the legacy `/mcp` namespace remain legacy regardless of subsequent slash-containing identifier segments. `/mcp/team/lazymcp` is covered directly by classifier/parser tests and through real aggregate authorization flow construction. Malformed intended LazyMCP shapes and all prior authority protections remain unchanged

- Focused tests: 171 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/17-reopen3-focused-tests.log`)
- Bounded mapped tests: 783 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/18-reopen3-mapped-tests.log`)
- Ruff: pass (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/19-reopen3-lint.log`)
- Focused basedpyright: 0 errors (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/20-reopen3-typecheck.log`)
- Docker candidate: intentionally not built, per PMA direction

## Reopen 4

Candidate classification is now request- and trusted-root-aware rather than relying on an `mcp` segment heuristic. With `PROXY_BASE_URL=https://gateway.example/mcp`, malformed `https://gateway.example/mcp/LazyMCP` is classified relative to `/mcp` and fails `invalid_target` without creating a flow. In the normal root context, genuine legacy `/mcp/team/lazymcp` remains unscoped legacy behavior

- Focused tests: 173 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/21-reopen4-focused-tests.log`)
- Bounded mapped tests: 784 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/22-reopen4-mapped-tests.log`)
- Ruff: pass (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/23-reopen4-lint.log`)
- Focused basedpyright: 0 errors (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/24-reopen4-typecheck.log`)
- Docker candidate: intentionally not built, per PMA direction

## Reopen 5

TASK-015's retained-candidate diagnosis is pinned with test-only regressions. For a non-loopback Docker-style HTTP peer, all six discovery aliases fail closed with generic 404 and aggregate/scoped/toolset challenge construction returns no Host-derived challenge when no trusted public base exists. With reserved `PROXY_BASE_URL=https://candidate.invalid`, the same discovery forms return exact metadata and all three challenge forms return exact configured absolute URLs. No runtime source, Dockerfile, or candidate input changed in Reopen 5

- Focused tests: 35 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/25-reopen5-focused-tests.log`)
- Bounded mapped tests: 710 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/26-reopen5-mapped-tests.log`)
- Ruff: pass (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/27-reopen5-lint.log`)
- Focused basedpyright: 0 errors (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/28-reopen5-typecheck.log`)
- Rebuild/deploy/production operations: not performed, per PMA direction

## Reopen 6

Explicit toolset LazyMCP now enters shared admission before any Prisma or toolset-name lookup. The route preserves the exact public path, carries only a server-owned toolset-name ContextVar, and resets it in `finally`. After admission, the server resolves name to ID once and applies the existing toolset scope once. Missing and invalid credentials receive exact catalog-free toolset challenges without database access; admitted database-down, unknown, unauthorized, and permitted behavior remains 503, 404, 403, and scoped success through existing boundaries

- Focused tests: 9 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/29-reopen6-focused-tests.log`)
- Mapped route/toolset/auth tests: 335 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/30-reopen6-mapped-tests.log`)
- Ruff: pass (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/31-reopen6-lint.log`)
- Focused basedpyright: 0 errors (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/32-reopen6-typecheck.log`)
- Candidate/rebuild/deploy/production/arm64 operations: not performed

## Reopen 7

The anonymous-admission bypass identified by Tech Lead is closed. Every explicit toolset request that completes admission resolves the server-owned name regardless of principal presence. Anonymous DB-down and unknown outcomes remain 503/404; anonymous known-toolset access terminates with explicit 403 rather than aggregate fallback. Authenticated unauthorized access remains 403 and permitted access retains existing scoped behavior. Context reset on exception, concurrent different-name isolation, and simultaneous name-plus-ID fail-closed behavior are mutation-sensitive

- Focused tests: 16 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/33-reopen7-focused-tests.log`)
- Mapped route/toolset/auth tests: 342 passed (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/34-reopen7-mapped-tests.log`)
- Ruff: pass (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/35-reopen7-lint.log`)
- Focused basedpyright: 0 errors (`.staticeng/evidences/TASK-2026-08-31-003-implement-lazymcp-oauth-discovery/logs/36-reopen7-typecheck.log`)
- Candidate/build/deploy/production/arm64 operations: not performed

## Documentation

Steady-state behavior is documented in `.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md` and cross-linked from the approved SCR. Product overview and feature inventory do not change
