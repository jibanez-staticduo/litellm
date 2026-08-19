---
id: TASK-2026-08-19-048-fix-lazymcp-probe-compatibility
complexity: standard
track: implementation
slice: logic
status: done
scr: null
parent: TASK-2026-08-19-046-verify-lazymcp-transport
assigned_to: developer
handoff_from: product_manager
reopened_count: 3
---

# Task: TASK-2026-08-19-048 - Fix LazyMCP Probe Compatibility

## Objective
Change LiteLLM LazyMCP routes so health/discovery probes using `HEAD /lazymcp` or generic `GET /lazymcp` no longer return 405/406, while preserving protocol-correct MCP POST and SSE GET behavior, authentication, authorization, and scoped routes.

## Required Behavior
- `HEAD /lazymcp` and trailing-slash equivalent return a lightweight successful response through the same route auth boundary, with no body and no MCP session allocation.
- Generic browser/probe `GET /lazymcp` that does not negotiate `text/event-stream` returns a lightweight successful compatibility/health response rather than 406, without exposing server catalogs, tools, credentials, or auth details.
- Protocol-correct GET with `Accept: text/event-stream` continues through the Streamable HTTP MCP handler unchanged.
- MCP POST initialize, notification, tools/list, `mcp_status`, `mcp_describe`, and `mcp_call` remain unchanged.
- Apply equivalent behavior to root/trailing-slash and any shared dynamic/toolset LazyMCP route helper where omission would create inconsistent behavior.

## Safety
- Do not weaken key/auth/access-group/IP restrictions or component allowlists.
- Do not special-case client IP/user-agent.
- Do not deploy until source tests and independent review pass.

## Acceptance Criteria
- [ ] AC-1: Exact route/method/Accept dispatch is implemented with successful HEAD and generic GET compatibility responses and unchanged SSE GET/POST dispatch.
- [ ] AC-2: Compatibility responses expose no MCP catalogs/tool data and create no session/stream.
- [ ] AC-3: Existing auth/authorization/IP/access-scope checks apply identically; unauthorized requests remain unauthorized.
- [ ] AC-4: Tests cover root/trailing slash, HEAD, generic GET (`*/*` and JSON), SSE GET, POST, unauthorized access, and dynamic/toolset consistency where applicable.
- [ ] AC-5: Existing LazyMCP/MCP focused suites plus targeted lint/format/type/compile/diff checks pass with no failures/skips.
- [ ] AC-6: Evidence maps every AC and defines image/release impact.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-048-fix-lazymcp-probe-compatibility/` with `SUMMARY.md` and complete logs.

## Handoff
[Agent Message] From: product_manager To: developer

Inspect the current LazyMCP route source and implement this compatibility fix in LiteLLM itself. Preserve all security boundaries and protocol-correct MCP behavior. Add focused regressions, run the relevant suites/checks, create complete evidence, and do not deploy or commit yet.

## Reopen History

### Reopen 1 - 2026-08-19
- Tech Lead approved auth/session/route placement but rejected commit due incomplete Accept negotiation.
- Combine all repeated Accept header field values rather than reading only the first.
- Parse comma-separated media ranges case-insensitively and honor quality parameters; `text/event-stream;q=0` is not acceptable.
- Mixed/repeated values containing an acceptable SSE range must continue through the MCP session manager.
- Add regressions for repeated fields, mixed comma values, case/parameters, q=0, and malformed/empty quality values with deterministic fail-safe behavior.

### Reopen 2 - 2026-08-19
- Tech Lead confirmed ordinary repeated/quality handling but found delimiter parsing invalid for quoted HTTP parameters.
- Replace raw comma/semicolon splitting with a standards-aware parser or quote-aware tokenizer that preserves quoted commas, semicolons, escaped quotes, and backslashes.
- Add route-level regressions for quoted comma, quoted semicolon, escaped quote/backslash, and q-values following quoted parameters.
- Preserve all prior auth, sessionless compatibility, SSE/POST dispatch, route consistency, and malformed-q behavior.

### Reopen 3 - 2026-08-19
- Tech Lead confirmed quote-aware dispatch but reproduced real MCP SDK 406 for repeated Accept fields because SDK reads only the first field.
- Before invoking `lazy_session_manager`, normalize repeated Accept fields into one combined field preserving order and exact quoted content.
- Do not normalize compatibility responses that bypass the session manager.
- Add a non-mocked route regression through the real MCP SDK/session manager for repeated fields.
- Reverify repeated/combined q=0 remains compatibility 204 and cannot become acceptable through normalization.

## Developer: Reopen 3 Final Result
- AC-1 through AC-6 passed.
- HEAD and non-SSE GET return authenticated empty 204 without session allocation.
- SSE GET/POST remain protocol-correct; repeated Accept fields are quote-aware, quality-aware, and normalized before the real MCP SDK.
- Complete mapped suite: 279 passed; focused suite: 62 passed; toolset suite: 24 passed.

## Tech Lead: Final Approval
- Commit and replacement-image release approved.
- Real SDK repeated-header regression passed five consecutive runs.
- No blocking protocol, security, session, route, or information-leak findings remain.

## PMA Final Closure
- AC-1 through AC-6 accepted.
- Authorized scoped commit and replacement image deployment to NAS and Fedora.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Implemented authenticated `204 No Content` compatibility handling for LazyMCP `HEAD` and non-SSE `GET`
- Preserved SSE `GET` and all `POST` dispatch through the existing LazyMCP Streamable HTTP session manager
- Applied behavior through the shared handler used by root, trailing-slash, dynamic, and toolset routes
- Added regressions for all required dispatch, security, no-body, and no-session cases
- Verified 242 mapped tests pass with no failures or skips; Ruff, compile, and diff checks pass
- Recorded repository-wide MCP, type-check, and StaticEng baseline limitations in task evidence
- Product documentation is not required; no endpoints or architecture boundaries changed
- No image build, deploy, restart, tag move, commit, or push was performed

## Developer Reopen 1 Updates

- Combined all repeated `Accept` fields and comma-separated media ranges
- Matched `text/event-stream` and `q` parameter names case-insensitively while allowing unrelated media parameters
- Honored valid quality values: `q=0` rejects the range and any `q>0` accepts it
- Deterministically rejected malformed, empty, duplicate, or out-of-range quality parameters for the affected range
- Ensured any other valid acceptable SSE range still dispatches to the existing MCP session manager
- Added focused negotiation and route regressions; 52 Reopen 1 cases and all 269 mapped tests pass with no skips
- Reran Ruff format/check, Python compile, and diff checks successfully
- Updated AC-mapped evidence; no deployment, image, commit, or push occurred

## Developer Reopen 2 Updates

- Replaced raw comma/semicolon splitting with quote-aware delimiter tokenization
- Preserved commas and semicolons inside quoted parameter values
- Preserved escaped quotes and backslashes without ending the quoted value early
- Added route-level positive-q and zero-q regressions with quoted comma, quoted semicolon, and escaped content
- Preserved repeated-header, mixed-range, malformed-q, authentication, sessionless compatibility, SSE/POST, and scoped-route behavior
- Verified 59 focused Reopen 2 cases and all 276 mapped tests pass with no skips
- Reran Ruff format/check, Python compile, and diff checks successfully
- Updated AC-mapped evidence; no deployment, image, commit, or push occurred

## Developer Reopen 3 Updates

- Normalized repeated `Accept` fields into one field immediately before LazyMCP session-manager dispatch
- Preserved original field order and exact quoted content while joining values with the standard comma separator
- Kept compatibility handling before normalization so sessionless 204 responses remain untouched
- Added a non-mocked route regression through a fresh real MCP SDK `StreamableHTTPSessionManager`
- Added route regressions proving repeated and combined `q=0` remain empty 204 responses without session handling
- Preserved all prior authentication, authorization, route, quoted-value, malformed-q, SSE, and POST behavior
- Verified 62 focused Reopen 3 cases and all 279 mapped tests pass with no skips
- Reran Ruff format/check, Python compile, and diff checks successfully
- Updated AC-mapped evidence; no deployment, image, commit, or push occurred
