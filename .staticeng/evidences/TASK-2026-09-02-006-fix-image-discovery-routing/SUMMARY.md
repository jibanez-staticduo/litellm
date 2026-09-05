# TASK-2026-09-02-006 Evidence Summary

## Summary

Added a packaged-runtime regression that starts the normal immutable LiteLLM image entrypoint on disposable internal Docker networks and pins the existing trusted-public-origin boundary. No routing, trust policy or application source changed

The unchanged retained image `sha256:eeb98cc84cd1f3b73ce1dc584ac9922e47515fc3db46beb8825283fddf6b2820` passes the new gate: unset and non-loopback HTTP public bases return generic 404 for all six aliases, while `PROXY_BASE_URL=https://candidate.invalid` returns exact 200 metadata for all six aliases. The packaged OpenAPI contains all six templates

## Work Performed

- Added `tests/proxy_migration_tests/test_image_lazymcp_discovery.py` with normal-entrypoint, non-loopback, live-container coverage
- Added the test to the nearest CodeMap and the monolithic runtime-image CI job
- Updated TASK-011's Reopen 5 harness and evidence contract with exact negative, positive, protocol, preservation and cleanup requirements
- Ran the new gate against the unchanged retained image, focused source/OpenAPI tests, touched-file Ruff, focused basedpyright, whitespace and StaticEng validation
- Verified all disposable test containers and networks were removed

## Acceptance Criteria Coverage

- **AC-1: PASS.** The unchanged exact retained image returns exact aggregate, scoped and toolset metadata for both alias forms under reserved HTTPS `PROXY_BASE_URL`, covering all six aliases
- **AC-2: PASS.** Focused source tests preserve exact resources and OpenAPI route ownership. TASK-011 now requires transports, exact challenges, DCR/audience, reconnect and `/mcp` in its corrected full qualification rerun
- **AC-3: PASS FOR TASK-OWNED GATES.** Packaged runtime, focused source/OpenAPI, Ruff, focused basedpyright, `git diff --check` and `staticeng_validate` pass. The mapped broad suite has four independently reproducible pre-existing failures recorded in `.staticeng/evidences/TASK-2026-09-02-006-fix-image-discovery-routing/logs/02-source-tests.log`
- **AC-4: PASS FOR DEVELOPER SCOPE.** Evidence and disposable-resource cleanup pass. Per PMA instruction, Developer did not commit, push, qualify the full isolated stack or deploy; Tech Lead commit/push and QA qualification remain next-stage gates

## Documentation Impact

No product or steady-state architecture documentation changed because behavior is unchanged. The nearest CodeMap, image CI qualification wiring, TASK-011 harness contract and task evidence were updated

## Open Risks

- TASK-011's complete isolated functional rerun, including challenges, DCR/audience, initialize/tool, reconnect and preservation, is still pending QA
- Candidate signing and attestations remain independent TASK-011 blockers
- The original attempt exposed four integration failures and local uv 0.10.9 drift; Reopen 1 resolves the failures and proves exact uv 0.11.26 passes

## Recommended Next Step

Tech Lead should review the test-only source/CI/CodeMap/task-contract changes, commit and push if approved, then PMA should return TASK-011 to QA for the full corrected qualification matrix

## Reopen 1

### Summary

Closed every Tech Lead finding. The image harness now collects and passes with clean host Python and no Pydantic dependency, the CodeMap command is valid shell, Responses API midstream exceptions produce typed terminal `response.failed` events while chat streams keep their existing error shape, `/introspect` and `/revoke` belong to the gateway data plane, and discoverable endpoints now use lazy-only runtime registration without duplicate routes

### Work Performed

- Replaced Pydantic parsing in the image test with typed standard-library validation and proved it under `/usr/bin/python3`
- Restored typed Responses stream failures for ordinary and HTTP exceptions with mutation-sensitive positive and non-Responses preservation tests
- Assigned `/introspect` and `/revoke` to `GATEWAY_EXACT_PATHS` and extended component ownership tests
- Removed eager discoverable-router registration from `proxy_server.py`, kept cold first-request loading, prevented registration from mutating the shared router, and moved snapshot generation onto an isolated FastAPI app
- Regenerated the lazy OpenAPI snapshot and dashboard API types; the dashboard type file is unchanged
- Corrected earlier uv evidence: host uv 0.10.9 is stale local tooling, while exact pinned uv 0.11.26 parses the package override, checks the lock and passes `make check`

### Acceptance Criteria Coverage

- **AC-1: PASS.** The unchanged retained image still passes all six exact HTTPS metadata aliases and both fail-closed base cases
- **AC-2: PASS.** The complete mapped challenge, DCR/audience, transport, toolset, component, source-discovery and `/mcp` preservation suites pass
- **AC-3: PASS.** Packaged runtime 4/4, mapped source 829/829, mapped MCP 734/734, exact uv 0.11.26 lock and `make check`, Ruff, type/test-quality budgets, basedpyright, generated OpenAPI/types, diff and StaticEng gates pass
- **AC-4: PASS FOR DEVELOPER SCOPE.** Evidence and cleanup pass. Tech Lead review/commit/push remains required before qualification

### Documentation Impact

Updated gateway/backend parent CodeMaps, the image-test CodeMap command, generated Lazy OpenAPI snapshot, CI wiring, TASK-011 qualification contract and task evidence. Product documentation is not required because public routing and trust policy are unchanged

### Open Risks

TASK-011 still requires a new candidate built from the eventual reviewed commit and its complete runtime/security qualification. Signing and attestation remain independent blockers

### Recommended Next Step

Tech Lead should independently review and commit/push the complete Reopen 1 change set, then PMA should reactivate TASK-011 qualification

## Reopen 2

### Summary

Closed the latest Tech Lead findings. Every protected LazyMCP image input now triggers image CI, snapshot generation preserves the complete overlapping route surface without mutating the runtime app, generated contracts are reproducible under exact staged uv 0.11.26, Responses failures preserve non-empty provider codes and accept only actual string IDs, CodeMap hierarchy is parent-child correct, and each source six-alias case starts from a new cold app

### Work Performed

- Added protected proxy, lazy loader/snapshot, LazyMCP route, MCP implementation and gateway allowlist paths to the image workflow trigger
- Seeded snapshot generation with copies of the complete runtime routes, then registered lazy routes on that isolated app
- Added preservation tests for `/mcp`, Anthropic passthrough, access-group and callback routes plus runtime-app identity/unique-ID immutability
- Preserved non-empty provider error codes and selected response IDs only from non-empty strings, with deterministic `resp_failed` fallback
- Corrected gateway/backend nested CodeMap parents and module declarations
- Added a workflow-trigger contract test and made every alias cold-start test build its own FastAPI app
- Regenerated OpenAPI/types and completed exact staged uv 0.11.26 gates

### Acceptance Criteria Coverage

- **AC-1: PASS.** Unchanged retained image and independently cold source cases pass all six aliases
- **AC-2: PASS.** Full mapped discovery, challenge, DCR/audience, transport, toolset, component and `/mcp` suites pass
- **AC-3: PASS.** Packaged/workflow 5/5, source/component 832/832, MCP mapped 734/734, exact staged `make check`, generated sync, lint/type and StaticEng pass
- **AC-4: PASS FOR DEVELOPER SCOPE.** Evidence and cleanup pass; Tech Lead review/commit/push remains required before qualification

### Documentation Impact

Updated gateway/backend CodeMap hierarchy, test CodeMap, workflow triggers, generated contract logic/tests and evidence. Product documentation is not required because routing/trust behavior is unchanged

### Open Risks

TASK-011 must build and qualify a new immutable candidate from the eventual reviewed commit. Candidate signing/attestation remains separate

### Recommended Next Step

Tech Lead should review and commit/push Reopen 2, then PMA should reactivate TASK-011 qualification

## Reopen 3

### Summary

Closed the Reopen 3 findings. Typed terminal failures now cover synchronous and asynchronous Responses call types with provider-code and stable-ID fidelity. Keepalive tests are deterministic without changing runtime behavior. Generated synchronization now passes exact uv 0.11.26 `make check` from a fresh alternate index containing exactly the intended paths

### Work Performed

- Extended typed `response.failed` selection to `responses` and `aresponses`
- Parametrized provider-code, valid-string-ID, non-string-ID and fallback behavior across both call types
- Replaced scheduler-dependent keepalive sleeps/count thresholds with controlled `asyncio.wait` outcomes and exact assertions
- Diagnosed alternate-index drift as inherited `GIT_INDEX_FILE` confusing the real staged generated-file comparison
- Made the pre-commit gate unset external `GIT_INDEX_FILE` after selecting the repository, then proved clean generation from a fresh alternate intended index
- Repeated full mapped source tests and reran MCP, packaged, lint/type/static and cleanup gates

### Acceptance Criteria Coverage

- **AC-1: PASS.** Unchanged retained image still passes all exact discovery cases
- **AC-2: PASS.** Complete mapped transport/challenge/DCR/audience/toolset/`/mcp` suites pass; Responses typed terminal behavior is symmetric
- **AC-3: PASS.** Full mapped source suite passed twice at 834/834, keepalive matrix passed five consecutive runs, MCP 734/734, packaged/workflow 5/5 and exact alternate-index uv 0.11.26 `make check` pass with zero generated diff
- **AC-4: PASS FOR DEVELOPER SCOPE.** Evidence and cleanup pass; Tech Lead review/commit/push remains required

### Documentation Impact

Updated code-adjacent gate behavior and evidence. Existing CodeMap, CI and qualification-contract updates remain valid; product documentation is not required

### Open Risks

TASK-011 must still build and qualify a new immutable candidate after review/commit. Signing and attestation remain separate blockers

### Recommended Next Step

Tech Lead should review and commit/push Reopen 3, then PMA should reactivate TASK-011 qualification

## Reopen 4

### Summary

Removed the false-green alternate-index behavior. The gate now explicitly rejects true alternate indexes before performing any checks, while continuing to support Git's hook-provided canonical `.git/index`. Generated comparison passes using exactly intended paths staged in the repository index

### Work Performed

- Replaced silent `GIT_INDEX_FILE` switching with deterministic exit-2 rejection for noncanonical index paths
- Added sandbox coverage where only an alternate index stages a gated Python file; proved canonical index cleanliness, explicit rejection, no false Python check, and preservation of alternate staged state
- Preserved commit-hook compatibility where Git sets `GIT_INDEX_FILE` to the canonical repository index
- Staged exactly intended paths in the repository index and reran exact uv 0.11.26 `make check` with zero snapshot/schema drift
- Reran the complete pre-commit script test suite and all required static/cleanup gates

### Acceptance Criteria Coverage

- **AC-1: PASS.** Retained packaged discovery verification remains green
- **AC-2: PASS.** Reopen 3's repeated full mapped and MCP suites remain current and green
- **AC-3: PASS.** Exact canonical staged `make check`, generated zero-diff, pre-commit sandbox 26/26, lint/type/static gates pass; alternate indexes fail explicitly rather than false-green
- **AC-4: PASS FOR DEVELOPER SCOPE.** Evidence and cleanup pass; Tech Lead review/commit/push remains required

### Documentation Impact

Updated the gate's documented index contract, sandbox test and evidence. Product documentation is not required

### Open Risks

Callers using alternate indexes must stage the intended paths in `.git/index` before invoking `make check`; this is now explicit and fail-closed. TASK-011 new-candidate qualification and signing remain pending

### Recommended Next Step

Tech Lead should review and commit/push Reopen 4, then PMA should reactivate TASK-011 qualification

## Reopen 5

### Summary

Closed deterministic cleanup and linked-worktree index findings. Interrupts now terminate and reap every background process before removing one run-owned temporary directory. Canonical index comparison uses Git's worktree-aware absolute index path, noncanonical alternate indexes remain rejected, and a linked-worktree hook regression proves canonical acceptance

### Work Performed

- Consolidated transient .staticeng/evidences/TASK-2026-09-02-006-fix-image-discovery-routing/logs/reports under a run-owned directory with EXIT cleanup
- Made INT/TERM cleanup terminate process groups, wait for all children, remove all run artifacts and exit 130
- Resolved canonical index through `git rev-parse --path-format=absolute --git-path index` with caller `GIT_INDEX_FILE` removed only for that resolution command
- Added a real linked-worktree hook commit using the absolute linked index path
- Repeated the complete pre-commit suite five times and reran exact canonical staged uv 0.11.26 `make check`, mapped/package/static gates

### Acceptance Criteria Coverage

- **AC-1: PASS.** Retained packaged suite passes 5/5
- **AC-2: PASS.** Full mapped source passes 834/834 and retained MCP 734/734 evidence remains current
- **AC-3: PASS.** Pre-commit 27/27 across six total runs, exact staged `make check`, zero generated drift, lint/type/static pass
- **AC-4: PASS FOR DEVELOPER SCOPE.** Strict cleanup assertions and resource inventory pass; Tech Lead review/commit/push remains required

### Documentation Impact

Updated gate implementation, linked-worktree/interrupt tests and evidence. Product documentation is not required

### Open Risks

TASK-011 must still build and qualify a new immutable candidate after review/commit. Signing and attestation remain separate blockers

### Recommended Next Step

Tech Lead should review and commit/push Reopen 5, then PMA should reactivate TASK-011 qualification

## Tech Lead Final Review

No blocking findings remain after Reopen 5. Independent verification passed the retained packaged image/workflow suite (5), complete mapped source suite (835), complete mapped MCP suite (734), Responses/Chat compatibility cases, five repeated keepalive matrices, six repeated complete pre-commit suites (27 each), ten repeated strict interrupt-cleanup cases, alternate-index rejection, linked-worktree canonical hook execution, exact canonical staged uv 0.11.26 `make check`, generated zero-diff, `git diff --check`, and `staticeng_validate` with zero warnings.

AC-1 through AC-4 pass. Cleanup leaves zero task-labelled containers or networks and one repository worktree. Product documentation remains unchanged because public routing and trusted-origin policy did not change. TASK-011 candidate qualification and signing remain separate blocked work.
