# LazyMCP Probe Compatibility

## Summary

LiteLLM now returns an authenticated empty `204 No Content` response for LazyMCP `HEAD` requests and `GET` requests that do not accept `text/event-stream`. The compatibility path runs only after the existing MCP admission and toolset scope checks, and it returns before session-manager initialization or request handling

SSE-negotiated `GET` and every `POST` continue to dispatch to the existing LazyMCP Streamable HTTP session manager

Reopen 1 corrected negotiation across repeated `Accept` fields and comma-separated media ranges. Matching is case-insensitive, valid quality values are honored, and malformed, empty, duplicate, or out-of-range `q` parameters deterministically reject that SSE range. Any other valid `text/event-stream` range with `q > 0` still dispatches to MCP

Reopen 2 replaced raw delimiter splitting with quote-aware tokenization. Commas and semicolons inside quoted parameter values, including escaped quotes and backslashes, are preserved while delimiters outside quoted values continue to separate ranges and parameters

Reopen 3 normalizes repeated `Accept` fields into one ordered field only after a request is selected for MCP dispatch. This gives the real MCP SDK the complete negotiation value while preserving each field's exact quoted bytes. Sessionless compatibility responses return before normalization

## Work Performed

- Added exact LazyMCP method and `Accept` dispatch in `litellm/proxy/_experimental/mcp_server/server.py`
- Preserved MCP authentication, authorization, IP filtering, access-group resolution, and toolset scoping by running compatibility dispatch after `_prepare_mcp_request_context`
- Preserved `ProxyException` authentication status codes instead of allowing LazyMCP auth failures to become generic 500 responses
- Added focused root, trailing-slash, dynamic, and toolset route regressions in `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py`
- Verified empty responses and asserted that compatibility requests never call the LazyMCP session manager
- Verified SSE `GET` and `POST` still call the existing session manager
- Added Reopen 1 regressions for repeated fields, mixed ranges, casing, media parameters, positive/zero quality, and malformed quality values
- Added route-level Reopen 2 regressions for quoted commas, quoted semicolons, escaped quotes/backslashes, and quality values following quoted parameters
- Added a Reopen 3 regression through a fresh real MCP SDK `StreamableHTTPSessionManager`, plus repeated/combined `q=0` route regressions

## Acceptance Criteria Coverage

- **AC-1: PASS**. `HEAD` and non-SSE `GET` return 204; any valid SSE range with `q > 0` across all repeated/comma-separated `Accept` values and every `POST` dispatch to the unchanged session manager. Repeated fields are combined in original order before real SDK dispatch, preserving quoted bytes. See `logs/focused-tests.log` and `logs/verification.log`
- **AC-2: PASS**. Compatibility responses have an empty body, and regression mocks fail if the session manager is invoked. Session managers are not initialized and repeated headers are not normalized on this early-return path. See `logs/focused-tests.log`
- **AC-3: PASS**. Compatibility dispatch follows `_prepare_mcp_request_context`, including admission, IP, access-group, and toolset checks. A `ProxyException(401)` regression remains 401 and never reaches the session manager. See `logs/focused-tests.log`
- **AC-4: PASS**. Tests cover root and trailing slash, `HEAD`, `GET` with `*/*` and JSON, SSE `GET`, `POST`, unauthorized access, dynamic/toolset routes, repeated `Accept` fields, mixed values, casing/parameters, `q=0`, malformed/empty quality, quoted content, real SDK dispatch, and repeated/combined zero-quality compatibility. See `logs/focused-tests.log`
- **AC-5: PASS WITH REPOSITORY BASELINE LIMITATIONS**. The complete mapped LazyMCP/MCP server test file passes 279 tests with no skips, including 62 focused Reopen 3 cases. Ruff format/check, Python compile, and diff checks pass. The broader MCP directory run exceeded 20 minutes after exposing failures in unrelated modules. Direct basedpyright reports the file's existing strict-type backlog, and delta budget gates include concurrent shared-worktree changes outside this task. StaticEng validation also fails on repository-wide missing/stale CodeMaps. See `logs/verification.log` and `logs/baseline-limitations.md`
- **AC-6: PASS**. This evidence maps all ACs. The change affects source and tests only; no container image was built, tagged, deployed, restarted, or released

## Documentation Impact

No product, architecture, or CodeMap documentation update is required. The change is a compatibility dispatch refinement within the existing LazyMCP route handler and does not add or move an endpoint, module, or source file

## Image And Release Impact

The next LiteLLM image build will include the compatibility behavior. No image build, deployment, tag move, restart, or runtime configuration change occurred in this task

## Open Risks

The repository-wide MCP test directory and StaticEng validation have pre-existing failures outside this task's files. The directly mapped LazyMCP/MCP server suite and targeted source checks pass cleanly

## Recommended Next Step

PMA should route this source and evidence for independent technical review before any image build or deployment
