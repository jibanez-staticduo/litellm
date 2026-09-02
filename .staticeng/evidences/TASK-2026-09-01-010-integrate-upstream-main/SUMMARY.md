# TASK-2026-09-01-010 Evidence Summary

## Exact Merge State

- `HEAD`: `51b5f7e474e6de50bdec2eea64e33f4878fadf4b`
- `MERGE_HEAD`: `10631eb834c7802aa61611e807474170b8a4d425`
- `upstream/main`: `10631eb834c7802aa61611e807474170b8a4d425`
- `origin/main`: `9af49e5b34e25cdc9ad40f9bb50a178f40320417`
- Merge remains open and uncommitted; index has no unmerged entries

## Acceptance Criteria Coverage

- **AC-1: PASS pending commit.** Frozen upstream and all prior fork commits are represented by the two open merge parents. Every explicit conflict is resolved, `git ls-files -u` is empty, and no conflict markers remain
- **AC-2: PASS.** `PRESERVATION_MANIFEST.md` and `CONFLICT_LEDGER.md` trace fork behavior to merged resolutions. `pyproject.toml` declares `RestrictedPython>=8.5,<9.0`; `uv.lock` resolves 8.5
- **AC-3: PASS for mapped source regressions.** Two focused Python batches passed 782 and 717 tests. Dashboard MCP/connect tests passed 8 tests total; UI types, lint, knip, OpenAPI generation, and production build passed
- **AC-4: BLOCKED.** Focused Ruff/format, `uv lock --check`, compile, Prisma validation, UI checks, and E2E basedpyright pass. Repository `make check` fails because the imported upstream tree raises fork-wide strict-rule/test-quality/basedpyright totals against the pre-upstream base. Rust checks cannot run because `cargo` is absent and Docker image builds are prohibited
- **AC-5: PASS.** Architecture contract, task update, preservation manifest, conflict ledger, generated OpenAPI artifacts, CodeMaps, and this evidence packet are present. `staticeng_validate` result is retained in logs
- **AC-6: PENDING.** Tech Lead has not reviewed or committed. No push, image build/publication, Fedora mutation, or NAS mutation occurred

## Verification Results

- Python preservation batch A: 782 passed, no failures/skips
- Python preservation batch B: 717 passed, no failures/skips
- Integration regression discovered and repaired: one MCP OpenAPI ContextVar import failure; rerun passed
- Timezone-sensitive auth regression discovered and repaired: expiry fixture now uses aware UTC; rerun and batch passed
- Dashboard focused component tests: 1 MCP connect plus 7 OAuth hook tests passed
- Dashboard `format:check`, lint, `test:types`, `knip:ci`, `gen:api`, and production build passed; build emitted one AVIF optimization warning
- Prisma validate passed for root, core proxy, and proxy-extras schemas with a synthetic local URL; no database connection or migration was performed
- `uv lock --check` passed; RestrictedPython lock is 8.5
- E2E basedpyright passed after restoring typed `KeyInfoParams`/`KeyInfoResponse`
- Rust command failed before execution because `cargo` is not installed on this host
- `make check` failed on repository-wide upstream deltas and is a release-blocking open risk, not waived

## Documentation Impact

The LazyMCP architecture contract now states that canonical LazyMCP `resource` binding coexists with upstream audience/team and RS256/revocation/introspection claims. No product overview or feature-list update is required because this merge preserves behavior rather than advertising a new feature

## UI Evidence

The dashboard change is an upstream refactor plus preservation of existing LazyMCP copy and dynamic endpoint values. Automated focused tests and production build were used; no screenshot is claimed because no browser session was run

## Reopen 1 Closure

- Reconciled all 21 paths identified by TASK-013. Eighteen retain the current upstream implementation while restored fork tests prove the current source equivalents; router source and tests now explicitly combine upstream access/dedup/resource protections with the fork's cross-profile ChatGPT fallback guard and immutable logical identity
- Restored mutation-sensitive fork regressions for DeepSeek policy, LazyMCP admission/DCR/catalog/toolsets/routes, native ChatGPT Responses behavior, spend handling, and uvicorn/secret redaction
- The final LazyMCP admission and DCR restorations pass a 141-test focused run against the merged upstream interfaces
- `LINT_BASE_REF=10631eb834c7802aa61611e807474170b8a4d425 make check` passes from the fully staged snapshot. Strict Ruff, test-quality, type-discipline, basedpyright, E2E basedpyright, dashboard lint, and generated API checks are green. The four gate modules' in-progress/completed-merge base-selection tests pass in a 118-test focused run. Budgets were only ratcheted down for violations removed; no limit increased
- Checksum-pinned rustup 1.28.2 and Rust 1.97.1 were installed only under `/tmp/opencode/TASK-2026-09-01-010-rust`. Rust fmt, both clippy variants, workspace tests, and bedrock-auth tests pass
- `browserslist` resolves to 4.28.8 through a package-lock-only update. Full and production-only audits report zero vulnerabilities. Full dashboard unit, component, integration, type, format, lint, knip, and production-build gates pass
- Empty disposable PostgreSQL applied all 161 migrations; status was current and a second deploy had no pending migrations. The container was removed. This verifies empty-DB and restart/idempotence; no production/sanitized Fedora database was accessed
- All required CodeMaps, TASK-010 closure artifacts, and TASK-013 review artifacts are staged. `staticeng_validate` passes with zero warnings and no unstaged or untracked path remains
- The three unrelated deterministic StaticEng Markdown normalizations named by TASK-013 were verified and restored to `HEAD`; they are not staged

## Reopen 2 Closure

- Restored all three proxy-root LazyMCP route families through a dedicated `lazymcp_routes` lazy feature rather than broad-mounting the MCP application
- Root, scoped, and toolset routes preserve trailing-slash aliases, exact `_original_path`, internal rewrites, admission-before-toolset lookup, server/toolset/access-group resolution, exact unknown-target 404, and generic safe 500 conversion
- Direct route and lazy-registry coverage passes 20 tests; the full mapped LazyMCP suite passes 767 tests with eight existing warnings
- `LINT_BASE_REF=10631eb834c7802aa61611e807474170b8a4d425 make check` passes after regenerating the 34-fragment lazy OpenAPI snapshot and dashboard API types
- Dashboard types, format, lint, and knip gates pass. All staged raw logs were sanitized so `git diff --cached --check` passes

## Reopen 3 Closure

- Made `mcp_discoverable` the sole owner of canonical and alternate protected-resource routes and registered that contract before LazyMCP transport lazy loading
- Narrowed the transport matcher to exact root, one scoped segment, and toolset transport shapes with optional trailing slash; every `/.well-known/` and deeper path is excluded
- Prevented protected-resource routes imported as side effects from entering the `lazymcp_routes` OpenAPI fragment; all six routes remain only in the authoritative discoverable fragment
- Six true proxy runtime cases pass for canonical/alternate root, scoped, and toolset metadata with exact resource and authorization-server values. The complete mapped command passes 1,123 tests with nine existing warnings
- Regenerated the 34-fragment OpenAPI snapshot and dashboard types. Exact-upstream `make check`, cached diff check, CodeMaps, and StaticEng validation pass
