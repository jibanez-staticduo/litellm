---
id: TASK-2026-09-01-013-review-upstream-integration
complexity: complex
track: investigation
slice: qa
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-010-integrate-upstream-main
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: Review upstream main integration

## Objective

Independently review the resolved, uncommitted upstream merge and determine exact corrective work for the remaining `make check`, Rust, advisory, and worktree-state gates.

## Acceptance Criteria

- [x] AC-1: Review every conflict resolution, merge topology, preservation ledger, and unresolved-index state.
- [x] AC-2: Classify every `make check` failure as integration regression, legitimate upstream baseline movement, stale local budget, or unrelated pre-existing debt.
- [x] AC-3: Define a non-container or subsequently authorized isolated Rust validation path without weakening the gate.
- [x] AC-4: Inspect the npm High advisory and determine whether it blocks source merge commit or isolated candidate qualification.
- [x] AC-5: Attribute the three unstaged StaticEng normalizations and return exact fix/review instructions with pass/reject verdict.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Review the still-open merge from TASK-010 read-only. Do not edit source/tests, stage, commit, abort/reset merge, push, build images, or touch hosts. Inspect all conflict resolutions and evidence, rerun bounded diagnostics where needed, and provide findings first. Explicitly decide which blockers require the original Developer session to fix before commit and which can be deferred only to TASK-011 qualification. Update this task/evidence and return a signed verdict.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

### Summary

Independent read-only review rejects the open integration merge. Topology and unresolved-index checks are clean, but the proposed tree does not preserve claimed fork behavior, source gates remain red, Rust is unverified, a fixable npm High remains in the lock, and required CodeMaps are outside the index

### Work Performed

- Verified `HEAD=51b5f7e474e6de50bdec2eea64e33f4878fadf4b`, `MERGE_HEAD=10631eb834c7802aa61611e807474170b8a4d425`, merge base `bc6e7df05b018eefe6c7293790ca3f4de38709ac`, no unresolved index entries, and no cached diff whitespace errors
- Compared all 45 paths recorded by `.git/MERGE_MSG` with base, fork parent, upstream parent, and index; 24 are custom resolutions and 21 are byte-identical to upstream
- Found that the 21 upstream-identical resolutions drop fork-only source and regression tests while the ledger and preservation manifest claim combined behavior, including ChatGPT cross-profile fallback protection and its tests
- Reclassified the logged `make check` results with fresh bounded Ruff, E2E basedpyright, strict-budget, test-quality, and basedpyright diagnostics against the exact upstream parent
- Inspected the npm advisory, current lock ancestry, Rust workflow/toolchain inputs, three unstaged StaticEng normalizations, 42 untracked required CodeMaps, and current StaticEng validation behavior

### Acceptance Criteria Coverage

- **AC-1: PASS FOR REVIEW, MERGE REJECTED.** Merge topology and unresolved index are valid, but the conflict ledger records 46 conflicts while Git records 45, groups paths instead of giving each an auditable decision, and falsely claims preservation for upstream-identical resolutions that dropped fork-only behavior/tests
- **AC-2: PASS.** The old two Ruff and nine E2E type errors were integration regressions already corrected in the current index, but `make check` was not rerun. The large old budget deltas are mostly legitimate upstream baseline movement misattributed by using `HEAD^`; fresh comparison with the exact upstream parent exposes remaining fork-side debt that must be fixed without raising budgets. `EXE002` is additionally distorted by unrelated checkout permissions because disk files are `0777` while the index records normal modes
- **AC-3: PASS.** Use the checksum-pinned non-container rustup 1.28.2 and Rust 1.97.1 path already encoded in CircleCI, with task-local `RUSTUP_HOME` and `CARGO_HOME`, then run rustfmt, both clippy variants, and both test variants from `.github/workflows/test-rust.yml`. This gate cannot be deferred to TASK-011 because Rust source and lock files are part of the source merge
- **AC-4: PASS.** The one High is fixable `browserslist 4.28.2`, advisories `GHSA-c83g-rgw3-j3cx` and `GHSA-73wf-gq98-2v4g`, through a dev-only chain. Production-only audit is clean, but the approved zero-fixable-High policy and source-lock freeze require the lock fix before source commit, not only during candidate qualification
- **AC-5: PASS.** The three unstaged files are deterministic StaticEng Markdown path normalizations previously declared unrelated and not applied. They must be restored to `HEAD` or moved to a separately approved docs change, never staged with this merge. The current task registration/evidence are authorized review artifacts and remain separate from those three normalizations

### Documentation Impact

No steady-state product or architecture documentation was changed. Review evidence is at `.staticeng/evidences/TASK-2026-09-01-013-review-upstream-integration/SUMMARY.md` and `.staticeng/evidences/TASK-2026-09-01-013-review-upstream-integration/logs/01-review-diagnostics.md`

### Open Risks

- The current index lacks the fork's cross-profile ChatGPT fallback guard and drops many fork regression tests while claiming preservation
- Forty-two required CodeMaps are untracked, so the passing `staticeng_validate` result validates the working tree, not the proposed commit
- Full dashboard unit coverage, source migration execution/upgrade coverage, and Rust verification are absent
- The source lock still contains a fixable High advisory

### Recommended Next Step

PMA should reopen TASK-010 for the original Developer. The Developer must redo all 21 upstream-identical conflict resolutions as explicit three-way reconciliations or document and prove an upstream equivalent, restore mutation-sensitive fork regressions, include reviewed CodeMaps, fix all exact-upstream-relative source gates and the npm High, run the pinned Rust matrix and missing source tests, then return a new complete evidence packet for Tech Lead rereview

## Signed Tech Lead Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT / REOPEN TASK-010. The open merge has correct parents and no unresolved index entries, but it is not preservation-safe or source-qualified. Twenty-one conflict paths equal upstream byte-for-byte and drop fork-only behavior/tests despite contrary ledger claims; exact-upstream-relative Ruff, test-quality, and basedpyright gates remain red; Rust is unrun; a fixable npm High remains; and 42 required CodeMaps are outside the index. Do not commit, activate TASK-011, push, build an image, or deploy. Return the original Developer to the exact remediation sequence in this task and its evidence, then request a fresh independent review

## Re-review 1

### Summary

Reopen 1 is rejected without commit. The Developer fixed the exact-upstream source gate, Rust matrix, dashboard/audits, migration execution, CodeMaps, budgets, and unrelated normalization drift, but the staged merge deletes the proxy-owned public LazyMCP routes. An independent focused run fails all six retained route-preservation tests with HTTP 404

### Work Performed

- Reverified exact open-merge parents, zero unmerged entries, zero unstaged/untracked paths, budget monotonicity, excluded normalization hashes, CodeMaps, and StaticEng validation
- Reviewed all 21 dispositions and confirmed router/fallback source is now a custom reconciliation, exact-resource admission/DCR tests are restored, and many fork behaviors have current upstream implementation equivalents
- Inspected exact-upstream `make check`, pinned Rust matrix, full dashboard/audits, and disposable migration evidence
- Independently ran `uv run --no-sync pytest -q tests/test_litellm/proxy/test_dynamic_mcp_route.py -k lazymcp`; result was 6 failed, 21 deselected
- Independently ran five repaired preservation files spanning hosted-vLLM, admission, DCR, and fallback; result was 585 passed with six warnings

### Acceptance Criteria Coverage

- **TASK-010 AC-1: PASS.** Exact parents and unresolved-index state remain correct
- **TASK-010 AC-2: FAIL.** Public `/lazymcp`, `/lazymcp/{scope}`, and `/toolset/{name}/lazymcp` behavior is not preserved
- **TASK-010 AC-3: FAIL.** Retained route-preservation tests fail 6/6; the claim that all mapped regressions pass is false
- **TASK-010 AC-4: PASS FOR REVIEWED GATES.** Exact-upstream `make check`, Rust matrix, dashboard matrix/audits, and empty-DB migration/restart evidence are green. The two Rust live tests remain upstream-ignored and belong to candidate/runtime qualification, not this source regression
- **TASK-010 AC-5: FAIL.** CodeMaps and StaticEng validate, but the evidence packet incorrectly claims the LazyMCP route tests pass and does not record the independent failure
- **TASK-010 AC-6: FAIL.** Tech Lead rejected and did not commit

### Documentation Impact

No steady-state product documentation change is required. TASK-010's conflict ledger, preservation manifest, and summary must be corrected to match the repaired route implementation and verification

### Open Risks

- `_lazy_features.py` only triggers and mounts the MCP sub-app for `/mcp`; it does not claim `/lazymcp` or `/toolset/*/lazymcp`
- The MCP sub-app mounts `/` before `/lazymcp`, so mounting that app elsewhere without route-order review is not a safe substitute
- The staged logs contain whitespace errors, so `git diff --cached --check` is also red despite source checks passing
- The task file still leaves AC-4 and AC-6 unchecked and retains superseded blocker language instead of a final Reopen 1 result

### Recommended Next Step

Reopen TASK-010 again. Restore the three proxy-owned LazyMCP route families through the current lazy-loading architecture, preserve exact `_original_path`, admission-before-toolset lookup, access-group fallback, trailing-slash aliases, and safe error mapping. Restore or replace the deleted direct route/handler regressions, run the full mapped route and LazyMCP suites plus exact-upstream `make check`, sanitize evidence logs so cached diff check passes, correct closure claims, and return for another independent review

## Signed Re-review 1 Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT / REOPEN TASK-010 REOPEN 2. Reopen 1 fixed the source-quality, Rust, UI/security, migration, CodeMap, budget, and unrelated-normalization findings, but the staged tree removed all proxy-owned public LazyMCP route handlers. Independent verification returns HTTP 404 and fails all six retained route-preservation cases. No merge commit was created. Do not activate TASK-011, push, build, publish, or deploy until the exact route fix and corrected evidence pass rereview

## Re-review 2

### Summary

Reopen 2 is rejected without commit. The three Streamable HTTP route families now work and their direct/mapped tests pass, but the lazy matcher steals three approved RFC 9728 discovery aliases from `mcp_discoverable`; all three alternate metadata routes return 404 while generated OpenAPI advertises them

### Work Performed

- Reviewed `lazymcp_routes.py`, `_lazy_features.py`, the server context resolver, direct route tests, generated lazy OpenAPI snapshot, generated dashboard API types, CodeMaps, and complete staged state
- Independently reran 11 direct LazyMCP route tests and six lazy-feature matcher tests; all 17 passed
- Independently probed root/scoped/toolset Streamable HTTP routes and confirmed expected 204/404/503 behavior without redirects
- Independently probed all three alternate protected-resource metadata paths and received 404 for each
- Reverified no budget increase, unrelated normalization exclusion, zero unmerged/unstaged/untracked paths, cached diff cleanliness, and `staticeng_validate` pass

### Acceptance Criteria Coverage

- **TASK-010 AC-1: PASS.** Exact merge parents and unresolved-index state remain correct
- **TASK-010 AC-2: FAIL.** The approved LazyMCP OAuth discovery alias behavior is dropped by lazy-feature ownership collision
- **TASK-010 AC-3: FAIL.** Direct transport tests and 767 mapped tests pass, but runtime discovery aliases fail independently
- **TASK-010 AC-4: PASS FOR REVIEWED GATES.** Exact-upstream `make check`, Rust, dashboard, audits, migration, lock, compile, and static gates remain green
- **TASK-010 AC-5: FAIL.** OpenAPI/types advertise three routes that runtime does not serve, and the evidence packet claims complete route restoration
- **TASK-010 AC-6: FAIL.** Tech Lead rejected and did not commit

### Documentation Impact

No new product documentation is required. Correct the lazy ownership design and regenerate OpenAPI/types so runtime and documentation have one consistent owner per discovery route

### Open Risks

- `lazymcp_routes` suffix matching claims any path ending `/lazymcp`, including `/.well-known/oauth-protected-resource/lazymcp` and the toolset metadata alias
- `/lazymcp/{scope}` also captures `/lazymcp/.well-known/oauth-protected-resource` before `mcp_discoverable` can load
- The generated `lazymcp_routes` fragment contains discovery paths imported only as side effects, duplicating the authoritative `mcp_discoverable` fragment and creating suffixed operation IDs
- A direct `npm run gen:api` attempt outside the repository's uv environment failed on missing `dotenv`; the authoritative generated-sync result remains the passing `make check` evidence

### Recommended Next Step

Reopen TASK-010 again. Make discovery aliases load and route through `mcp_discoverable` before transport routing, narrow `lazymcp_routes` matching to only the three transport families, and prevent side-effect discovery routes from entering the `lazymcp_routes` OpenAPI fragment. Add cold-start runtime tests for all canonical and alternate root/scoped/toolset metadata paths, assert exact metadata resource values, rerun the 767 mapped suite and exact-upstream `make check`, regenerate OpenAPI/types, then return for final rereview

## Signed Re-review 2 Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT / REOPEN TASK-010 REOPEN 3. Streamable HTTP route restoration now passes, but the lazy route feature captures approved RFC 9728 discovery aliases and returns 404 for `/lazymcp/.well-known/oauth-protected-resource`, `/lazymcp/{scope}/.well-known/oauth-protected-resource`, and `/toolset/{name}/lazymcp/.well-known/oauth-protected-resource`. Generated OpenAPI advertises these unreachable paths. No merge commit was created. Keep TASK-011 inactive and do not push, build, publish, or deploy

## Re-review 3

### Summary

No blocking findings remain. Reopen 3 fixes discovery ownership, precedence, runtime behavior, and generated contracts without regressing transport routes or prior source gates. TASK-010 is approved for local no-fast-forward commit

### Work Performed

- Ran six independent cold-start proxy probes, one process per canonical/alternate discovery route, and verified exact metadata plus exclusive discovery-module loading
- Verified matcher ownership, exact transport shapes, discovery exclusions, route precedence, and sole OpenAPI fragment ownership by source inspection and executable assertions
- Reran 14 direct transport/lazy tests and seven discovery/OpenAPI ownership tests; all passed
- Rechecked complete staged merge state, exact parents, no budget increase, unrelated normalization exclusion, cached diff, CodeMaps, StaticEng validation, previous Rust/UI/audit/migration evidence, and secret-like path names

### Acceptance Criteria Coverage

- **TASK-010 AC-1: PASS.** Exact parents and conflict state are correct
- **TASK-010 AC-2: PASS.** Fork preservation and upstream integration contracts are satisfied
- **TASK-010 AC-3: PASS.** Mapped and independent behavioral verification pass
- **TASK-010 AC-4: PASS.** Required source, Rust, dashboard, audit, and migration gates pass
- **TASK-010 AC-5: PASS.** Documentation, generated contracts, CodeMaps, and evidence close cleanly
- **TASK-010 AC-6: PASS.** Tech Lead authorizes and creates the local merge commit without push/deployment

### Documentation Impact

Final runtime, architecture, generated OpenAPI, dashboard types, preservation records, and CodeMaps agree. No further product documentation is required

### Open Risks

Only downstream candidate qualification and deployment risks remain. They are owned by TASK-011 and TASK-012 and are not waived by source approval

### Recommended Next Step

PMA may activate TASK-011 against the exact approved merge commit

## Signed Re-review 3 Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. TASK-010 Reopen 3 is source-approved for the authorized local no-fast-forward merge commit. All six canonical/alternate LazyMCP discovery forms return exact metadata from cold start, transport routes remain correct, generated contracts have sole discovery ownership, and all retained source gates pass. No push, build, publication, deployment, Fedora action, or NAS action occurred
