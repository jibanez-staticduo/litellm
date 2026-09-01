---
id: TASK-2026-08-31-016-fix-toolset-challenge-order
complexity: standard
track: investigation
slice: logic
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-003-implement-lazymcp-oauth-discovery
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Investigate toolset challenge ordering

## Objective

Determine how `/toolset/{name}/lazymcp` can emit exact OAuth challenges before database-backed toolset resolution while preserving fail-closed toolset existence and permission behavior.

## Acceptance Criteria

- [x] AC-1: Trace current proxy route ordering and explain why database availability/lookup precedes LazyMCP admission.
- [x] AC-2: Determine whether anonymous/invalid bearer requests can safely run admission before toolset existence lookup without leaking identifier existence or broadening access.
- [x] AC-3: Define authenticated request behavior for missing database, unknown toolset, unauthorized toolset, and valid toolset.
- [x] AC-4: Recommend one minimal source/test correction with route/context ordering, security risks, candidate manifest impact, and rollback.
- [x] AC-5: Update task with signed evidence; no source/tests/images/production/deployment mutations.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Read TASK-006 Reopen 5 evidence and approved SCR. Inspect `toolset_lazymcp_route`, auth preparation, context binding, and toolset permission flow. The SCR requires every supported LazyMCP 401 to carry an exact challenge and generic metadata not to reveal existence. Research whether authentication can be performed first using preserved public path, then resolve/bind toolset only after admission. Preserve database-unavailable semantics for authenticated requests. Research only; update task and return exact implementation recommendation.

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

### Summary

Research passes. The explicit toolset route currently resolves database/catalog state before the shared LazyMCP handler can authenticate. Move only explicit toolset name resolution behind admission, while retaining the public path before rewrite and retaining `_apply_toolset_scope()` as the authorization boundary. Anonymous and invalid-credential requests can safely authenticate first because their exact challenge is derived only from the trusted public path and does not require or disclose toolset state

### Work Performed

- Read approved `SCR-2026-08-31-001-lazymcp-oauth-discovery`, the steady-state architecture contract, TASK-006 Reopen 5 summary and challenge smoke result, relevant CodeMaps, and the exact route/auth/context/toolset code and mapped tests
- Traced `toolset_lazymcp_route()` in `litellm/proxy/proxy_server.py`: it checks global `prisma_client`, calls `get_toolset_by_name_cached()`, returns 503 or 404, and only then preserves `_original_path`, rewrites to `/lazymcp`, binds `_mcp_active_toolset_id`, and invokes `handle_streamable_http_lazymcp()`
- Traced the downstream handler: it rewrites `/lazymcp` to `/mcp`, then `_prepare_mcp_request_context()` calls `MCPRequestHandler.process_mcp_request()`. That admission path already reads `_original_path`; `_lazymcp_challenge()` therefore builds the exact toolset challenge before user reload on invalid audience/token. Only after admission does `_prepare_mcp_request_context()` read `_mcp_active_toolset_id` and call `_apply_toolset_scope()`
- Confirmed `_apply_toolset_scope()` preserves the existing fail-closed grant rule: known toolset plus non-admin missing/empty/nonmatching `mcp_toolsets` returns 403; permitted/admin callers resolve tool permissions and replace the active MCP server/tool scope
- Confirmed TASK-006 Reopen 5 observed the same boundary live: all toolset no-token, invalid-key, malformed-session, and selection-header probes stopped at the route's pre-admission 503 and carried no challenge

### Safe Ordering Design

Use one server-owned request ContextVar carrying the explicit route's toolset **name**, separate from the existing resolved-ID ContextVar. This is narrower and safer than authenticating twice in `proxy_server.py`, introducing a second auth API, trusting a client header, or resolving catalog state speculatively

1. `toolset_lazymcp_route()` copies the request scope, stores the untouched path in `_original_path`, rewrites `path` to `/lazymcp`, sets a new `_mcp_active_toolset_name` ContextVar to `toolset_name`, streams the shared handler, and resets the token in `finally`. It performs no Prisma check and no toolset lookup
2. `handle_streamable_http_lazymcp()` retains `_original_path`, rewrites only internal `path` to `/mcp`, and enters `_prepare_mcp_request_context()` as today
3. `_prepare_mcp_request_context()` first calls `process_mcp_request()`. Missing/invalid credentials therefore return the existing exact path-derived 401 before any toolset lookup. Trusted-base failure remains generic/fail-closed under the existing challenge policy
4. After successful admission, `_prepare_mcp_request_context()` reads `_mcp_active_toolset_name`. If present, it obtains `proxy_server.prisma_client`, returns the existing 503 when absent, calls `get_toolset_by_name_cached()`, returns the existing 404 when unknown, and obtains the resolved `toolset_id`
5. It then applies `_apply_toolset_scope(user_api_key_auth, toolset_id)` exactly once before `set_auth_context()`. Existing `_mcp_active_toolset_id` behavior remains unchanged for legacy `/toolset/{name}/mcp` and `/lazymcp/{name}` toolset fallback routes. The explicit route must set only the name ContextVar, never both, to prevent duplicate scoping

The new ContextVar must be server-only and must not be populated from `x-mcp-toolset-id` or any other inbound header. Continue stripping `x-mcp-toolset-id`. Public resource identity remains `_original_path`; the internal rewrite and resolved database ID must never participate in audience/challenge construction

### Observable State Contract

| Request state | Toolset lookup | Result |
| :--- | :--- | :--- |
| Missing credential where gateway admission requires auth | Never | 401 with bare Bearer challenge for `/.well-known/oauth-protected-resource/toolset/{name}/lazymcp` |
| Invalid, expired, revoked, malformed-session, legacy-unscoped, or wrong-audience credential | Never when rejected during admission | 401 with matching `error="invalid_token"` challenge |
| Validly authenticated caller, database unavailable | Attempt stops before lookup | Preserve 503 `Database not available`, no fabricated 401 |
| Validly authenticated caller, unknown toolset | One cached name lookup | Preserve 404 and no aggregate fallback |
| Validly authenticated caller, known but unauthorized toolset | Name lookup, then grant check | Preserve 403 from `_apply_toolset_scope()`; do not expose tools |
| Validly authenticated caller, known and permitted/admin toolset | Name lookup, grant check, permission resolution | Existing scoped initialize/list/call behavior |

An installation intentionally configured for anonymous LiteLLM admission is not forced into a new 401: admission succeeds and the authenticated-phase database/toolset outcomes continue. This design changes ordering, not the gateway's authentication policy

### Tests Required

- Extend `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py` route tests, not a new file. Replace the current unconditional no-database 503 assertion with an admitted-caller 503 case and add route-level no-token/invalid-token cases proving exact challenges and asserting the toolset lookup is not awaited
- Add a route-level selection-header invariant case for explicit toolset transport. Unit challenge-builder parameterization is insufficient because it previously passed while the live route returned 503
- Preserve and strengthen route ownership: assert `_original_path == "/toolset/dev/lazymcp"`, internal `path == "/lazymcp"` at the proxy bridge, and name ContextVar visibility/reset across success and exception
- Add authenticated matrix cases in the same mapped route suite: absent Prisma -> 503; lookup `None` -> 404; known toolset plus `_apply_toolset_scope` denial -> 403; known permitted toolset -> successful stream and exactly one scope application/permission resolution
- Keep `tests/test_litellm/proxy/_experimental/mcp_server/auth/test_user_api_key_auth_mcp.py` exact three-resource challenge/audience matrix and `test_mcp_toolset_scope.py` permission tests unchanged except where an additional assertion is needed. Run focused route/auth/toolset suites, complete mapped MCP suites required by the SCR, Ruff, basedpyright, `git diff --check`, then repeat the retained-image secret-free smoke with trusted `PROXY_BASE_URL`

Mutation-sensitive requirements: deleting `_original_path`, moving lookup above `process_mcp_request()`, deriving the name from a header, setting both toolset contexts, skipping `_apply_toolset_scope()`, or converting authenticated 503/404/403 to 401 must each fail at least one focused test

### Security And Compatibility Risks

- **Existence disclosure:** reduced for unauthenticated/invalid callers because known, unknown, cached, uncached, and database-down names all terminate at the same admission challenge before catalog access. Authenticated callers retain existing 404/403 distinctions, so no new disclosure is introduced
- **Privilege broadening:** the public name and exact token audience grant nothing. Access remains blocked until database name-to-ID resolution and `_apply_toolset_scope()` succeed. Unknown names never fall back to aggregate LazyMCP
- **Context leakage:** incorrect ContextVar reset could scope a later request. Use token/reset in `finally`, relying on `_stream_mcp_asgi_response()` task context copying exactly as the existing ID ContextVar does
- **Double application:** setting both name and ID contexts could resolve/apply twice or clear grants before a second check. Explicit toolset LazyMCP must use name only; existing route families keep ID only
- **Availability semantics:** valid session admission can itself require user reload/database access before toolset resolution. Its existing auth-layer 503 remains authoritative. Once admission succeeds, absent toolset database still returns the existing 503
- **Non-LazyMCP preservation:** do not change `/toolset/{name}/mcp`, aggregate/scoped LazyMCP, discovery, DCR, `/mcp`, REST, upstream auth, cache policy, schemas, or database state

### Candidate Manifest Impact

The minimal runtime correction changes exactly two already-authorized runtime paths:

1. `litellm/proxy/proxy_server.py`
2. `litellm/proxy/_experimental/mcp_server/server.py`

`proxy_server.py` is already in the retained candidate manifest. `server.py` is not in the seven application paths authorized by TASK-005, so implementation invalidates the retained image and requires a newly frozen candidate manifest, source fingerprints, ordered manifest checksum, and combined tracked patch checksum. Preserve the exact approved Git base and all other application, parser, Dockerfile, lock, Cargo, and OCI inputs unless PMA separately authorizes drift. Tests and this governed task remain verification artifacts and are not image-source manifest entries

Do not patch only `proxy_server.py` by calling admission there: that would duplicate request authentication/context work, risk double user reload and policy accounting, and still require passing partially prepared auth into the handler through a new interface. The two-owner change is the minimal consistent architecture

### Rollback

Before promotion, rollback is deletion of `_mcp_active_toolset_name` and restoration of the explicit route's current pre-admission Prisma/name lookup plus `_mcp_active_toolset_id` binding, followed by restoration of prior frozen fingerprints/manifest. If a new image is ever promoted, operational rollback is redeployment of the recorded prior immutable digest and verification of readiness, exact LazyMCP discovery/challenges, `/mcp`, MCP REST, toolset permission behavior, and upstream integrations. No schema, data, cache, credential, or registration rollback is required

### Acceptance Criteria Coverage

- **AC-1: PASS.** Exact pre-admission Prisma/name lookup and downstream auth/context ordering are traced with source owners and Reopen 5 runtime evidence
- **AC-2: PASS.** Admission-first is safe when challenge identity comes only from trusted `_original_path`; it avoids catalog lookup and leaves grants unresolved until authenticated scoping
- **AC-3: PASS.** Missing DB, unknown, unauthorized, valid, and intentionally anonymous-admission states are specified without weakening existing failure semantics
- **AC-4: PASS.** One two-file runtime correction, mapped tests, security boundaries, manifest re-freeze, risks, and rollback are defined
- **AC-5: PASS.** Only this governed task was edited. No source, tests, images, containers, configuration, database, credentials, production, deployment, CodeMaps, or evidence logs were mutated

### Documentation Impact

No product documentation change is required. The approved SCR and `.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md` already state admission-before-permission and exact challenge behavior. Implementation evidence should cite this ordering correction; update the architecture contract only if implementation chooses a materially different interface

### Open Risks

The current `resolve_toolset_tool_permissions()` catches database exceptions and returns an empty map, which can make a permitted known toolset appear empty rather than distinguish a permission-resolution outage. That behavior predates and is outside this task; do not broaden this correction silently. Promotion also remains blocked by TASK-006's outstanding exact-image signature, aggregate SBOM, and comparative scan gates

### Recommended Next Step

PMA should create one bounded implementation task for Developer covering the two runtime files and mapped tests, then route independent security/Tech Lead review. Re-freeze the candidate manifest before rebuilding; do not reuse retained image `sha256:0ade7608d10588994a73d45ffb1bb66e994966fe71edd640a9599ffca754fcdf` as evidence for the corrected ordering

### Signed Handoff

[Agent Message] From: technical_architect To: product_manager

PASS investigation. Implement a server-only toolset-name ContextVar on the explicit route, preserve `_original_path`, run shared LazyMCP admission first, then resolve database name-to-ID and apply existing toolset scope exactly once. Anonymous/invalid requests receive indistinguishable exact challenges without catalog access; admitted missing-DB/unknown/unauthorized/valid outcomes remain 503/404/403/scoped success. The two-file runtime change requires a new candidate manifest and rebuild; production remains unchanged

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-016 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
