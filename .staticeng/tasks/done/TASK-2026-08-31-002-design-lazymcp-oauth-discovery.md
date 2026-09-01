---
id: TASK-2026-08-31-002-design-lazymcp-oauth-discovery
complexity: complex
track: investigation
slice: foundation
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-003-implement-lazymcp-oauth-discovery
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Design LazyMCP OAuth discovery implementation

## Objective

Produce a code-level impact map and safe implementation sequence for the approved SCR, with special attention to exact public-resource preservation, DCR/token audience enforcement, route ordering, root paths, and regression boundaries.

## Acceptance Criteria

- [ ] AC-1: Identify exact implementation and test files, functions, interfaces, and route registration order.
- [ ] AC-2: Define one canonical public-resource parser/builder and fail-closed validation rules.
- [ ] AC-3: Define how authorization codes, access tokens, and refresh tokens retain and enforce exact LazyMCP audience.
- [ ] AC-4: Identify preservation and security risks for `/mcp`, upstream OAuth, permissions, toolsets, groups, reverse proxies, and component allowlists.
- [ ] AC-5: Provide an atomic implementation sequence and evidence/test matrix mapped to the SCR.

## Expected Evidence

- Signed architecture handoff in this task file with exact code references.
- No runtime code, tests, images, credentials, configuration, or deployment changes.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Read this task and the approved SCR fully. Inspect targeted code and tests. Produce an implementation-ready architecture handoff, not code. Preserve all dirty work and CodeMaps. Explicitly resolve whether existing gateway DCR tokens already carry a resource/audience claim and where exact audience admission must be enforced.

## Technical Architect Review

### Current-State Finding

The gateway DCR token family does not currently carry the exact public OAuth resource. `SessionPrincipal` in `litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py` carries `user_id`, `client_id`, and optional `resource_server_id`. The optional field is an internal MCP server UUID used only for existing per-server `/mcp/{server}` restriction. It cannot represent aggregate `/lazymcp`, an access-group scope, or a toolset URL, and it deliberately disappears for unknown or non-per-server resources

`resolve_scoped_resource_server()` in `litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py` currently treats absent, malformed, foreign-origin, aggregate, unknown, and otherwise unresolved resources as unscoped. `_resource_conflicts_with_scope()` also permits an absent resource and ignores every resource when the sealed server id is absent. Those compatibility rules are correct only for the pre-existing `/mcp` flow. Reusing them for LazyMCP would turn invalid LazyMCP resource input into an aggregate bearer and violate the approved fail-closed contract

Exact LazyMCP audience admission must occur in `MCPRequestHandler._admit_gateway_session()` in `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py`, after the bearer has been cryptographically opened but before `_reload_admitted_user()`, database reads, grant resolution, or tool execution. The expected audience must be derived from the trusted external base plus `scope["_original_path"]` (falling back to `scope["path"]` only when no rewrite occurred), never from content-selection headers or catalog lookup

### Canonical Public-Resource Contract

Add one small, dependency-light module, `litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py`, rather than expanding `oauth_utils.py` or duplicating URL logic across routing, metadata, DCR, and admission

The module should expose frozen typed values and total parsing/building functions with this conceptual API:

```python
LazyMcpResourceKind = Literal["aggregate", "scope", "toolset"]

class LazyMcpPublicResource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: LazyMcpResourceKind
    identifier: str | None
    canonical_uri: str
    transport_path: str
    metadata_path: str

def parse_lazymcp_resource(request: Request, candidate: str) -> LazyMcpPublicResource | LazyMcpResourceError: ...
def resource_from_transport_scope(scope: Scope) -> LazyMcpPublicResource | LazyMcpResourceError: ...
def build_lazymcp_metadata(resource: LazyMcpPublicResource, authorization_server: str) -> dict[str, object]: ...
def build_lazymcp_challenge(resource: LazyMcpPublicResource, invalid_token: bool) -> str: ...
```

All public URI construction must delegate external-base resolution to existing `get_request_base_url()` and normalized root-path handling to one hardened owner. The implementation must not reuse `canonical_resource_uri()` or `canonicalize_url_identity()` for admission equality: those functions intentionally lowercase, strip URL components, remove default ports, and remove trailing slashes, while this SCR requires exact code-point equality after only the one permitted transport trailing-slash alias is removed

The parser must accept exactly these canonical shapes relative to the trusted `{base}`: `/lazymcp`, `/lazymcp/{identifier}`, and `/toolset/{identifier}/lazymcp`. A single terminal slash is accepted and removed before comparison. The identifier is one non-empty RFC 3986 unreserved ASCII segment (`[A-Za-z0-9._~-]+`) other than `.` or `..`. Reject empty identifiers, additional segments, `%` in any form, encoded separators, dot segments, backslashes, controls, non-ASCII, userinfo, query, fragment, foreign origin, wrong scheme/authority/port, duplicate root path, and every `/mcp` rewrite shape. Case is preserved and compared exactly. This conservative syntax keeps discovery generic without querying the catalog and prevents the route layer and authorization layer from interpreting ambiguous encodings differently

`resource_from_transport_scope()` must recognize only the three public LazyMCP paths. `x-mcp-servers`, `x-mcp-access-groups`, `x-mcp-auth`, and per-server authorization headers are not inputs. The returned `metadata_path` is always the RFC 9728 path-inserted form. The path-appended route is only an alias serving the same metadata object

`build_lazymcp_metadata()` must produce `resource` and `authorization_servers` only for the currently empty metadata shape. It must omit `scopes_supported` rather than emit `[]`. Future multi-value fields must follow the same omit-if-empty rule

### Route and Rewrite Design

Register all six explicit route templates on `mcp_discoverable_endpoints_router` in `litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py`:

```text
/.well-known/oauth-protected-resource{root}/lazymcp
/.well-known/oauth-protected-resource{root}/lazymcp/{scope}
/.well-known/oauth-protected-resource{root}/toolset/{name}/lazymcp
/lazymcp/.well-known/oauth-protected-resource
/lazymcp/{scope}/.well-known/oauth-protected-resource
/toolset/{name}/lazymcp/.well-known/oauth-protected-resource
```

Define fixed aggregate and toolset templates before the scoped parameter template, and define all six before the existing parameterized MCP protected-resource routes. Do not route discovery through `dynamic_lazymcp_route()` or `toolset_lazymcp_route()`: metadata must stay unauthenticated, generic, catalog-free, permission-free, and indistinguishable for syntactically valid identifiers

`proxy_server.py` currently includes `mcp_discoverable_endpoints_router` before declaring direct LazyMCP transports, which is the correct outer registration order and must remain unchanged. In `root_lazymcp_route()`, `dynamic_lazymcp_route()`, and `toolset_lazymcp_route()`, copy the incoming path to `scope["_original_path"]` before rewriting `scope["path"]`. The toolset context variable and all existing scope/server/toolset resolution remain unchanged

The split gateway currently retains `/lazymcp` and `/toolset/` but not `/.well-known/`; the backend retains `/.well-known/`. Add the narrow `/.well-known/oauth-protected-resource` prefix to `GATEWAY_PATH_PREFIXES` in `gateway/routes/allowlist.py` so OAuth discovery is colocated with the LazyMCP data plane. Do not remove it from the backend allowlist in this change. Extend `tests/test_litellm/proxy/test_component_allowlists.py` to pin all six route templates to the gateway and preserve union coverage

### DCR, Code, Access-Token, and Refresh-Token Binding

Preserve the existing gateway issuer, DCR registration, client id, endpoints, cookie mechanism, PKCE, redirect checks, single-use guards, and storage model. Add an optional exact `resource: str | None` claim to `_ConnectFlow`, `_GatewayAuthCode`, `SessionPrincipal`, and `_SessionClaims`. Keep `resource_server_id` unchanged for existing per-server `/mcp` sessions. The new exact field is additive because the strict sealed/JWT models already serialize optional claims with `exclude_none=True`; pre-existing `/mcp` artifacts therefore retain their old wire shape

Flow rules:

1. `aggregate_authorize()` first calls the canonical LazyMCP parser when `resource` is present. A valid LazyMCP resource is sealed verbatim as the canonical URI in `_ConnectFlow`; malformed or foreign LazyMCP-shaped input returns `invalid_target` and creates no cookie. Existing `/mcp` and supported per-server `/mcp` behavior continues through its current resolver
2. `complete_connect_flow()` copies the exact optional resource from flow to authorization code without rebuilding or resolving it
3. `_authorization_code_grant()` requires exact equality between the code's LazyMCP resource and the token request's `resource`. Missing, terminal-slash alias, differently cased, rewritten `/mcp`, foreign-origin, or cross-scope/toolset input returns `invalid_target` before claiming the code and mints no token. Parse the supplied value for shape/security, then compare the resulting canonical URI to the sealed canonical URI. The authorization request may use the one trailing-slash transport alias; the token request must send the canonical value advertised in metadata
4. `_session_token_pair()` mints access and refresh tokens from one `SessionPrincipal`, so both token kinds carry the same exact resource claim. `_refresh_token_grant()` requires the request resource to parse and exactly equal `opened.principal.resource`; missing or changed input returns `invalid_target` before refresh-token claim/rotation. Rotation reuses the unchanged principal
5. Existing `/mcp` flows whose principal has `resource is None` retain current behavior, including existing optional per-server `resource_server_id`. This is required by the preservation AC. A root gateway authorization request with no `resource` is indistinguishable from an existing `/mcp` request and therefore remains the legacy `/mcp` flow; a LazyMCP flow is identified by its required valid LazyMCP resource. This is the only design that simultaneously reuses one DCR client and leaves `/mcp` unchanged

No registration record or database field changes are needed. One registered client can produce independently sealed codes and token pairs for several exact resources

### Exact Audience Admission

In `_admit_gateway_session()`, after `resolve_session_bearer()` returns `SessionBearerAdmitted`:

1. If `principal.resource` is non-null, parse the original public transport path with `resource_from_transport_scope()` and require its canonical URI to equal the signed claim exactly
2. Reject a missing/invalid original path, `/mcp` internal rewrite, aggregate/scope/toolset mismatch, different identifier, or hostile external-base result with the matching LazyMCP `invalid_token` challenge
3. Only after the equality gate passes, reload the user and run existing live policy, key/team/org/IP/rate-limit/server/group/tool/toolset checks
4. Do not derive server ids, access groups, toolsets, tools, or grants from the resource claim. For `/lazymcp/{scope}`, the existing authenticated LazyMCP path resolver decides whether the identifier denotes a server or access group and keeps unknown-name rejection. For toolsets, existing `_mcp_active_toolset_id` and `_apply_toolset_scope()` remain the authority
5. If `principal.resource` is null, preserve the existing `/mcp` admission and `resource_server_id` ceiling exactly. A LazyMCP route must reject such a legacy/unscoped gateway session token rather than accept it by identity alone

Invalid-token challenge construction must use the parsed requested LazyMCP transport identity, not the token claim, so the client is directed to metadata for the endpoint it actually called. No-token challenges use the same builder without `error="invalid_token"`. Non-LazyMCP paths continue through `_gateway_dcr_challenge()` and per-server passthrough helpers unchanged

### Impact Surface

Implementation owners and expected edits:

- `litellm/proxy/_experimental/mcp_server/lazymcp_public_resource.py`: new canonical parser, public-path parser, metadata builder, and challenge builder
- `litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py`: six explicit unauthenticated routes and shared metadata handler; preserve existing `/mcp`, per-server, pass-through, delegated, BYOK, and authorization-server metadata
- `litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py`: exact resource persistence and strict code/refresh redemption while retaining legacy `/mcp` behavior
- `litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py`: additive signed exact-resource claim in access and refresh tokens
- `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py`: LazyMCP challenge selection and pre-policy exact-audience admission
- `litellm/proxy/proxy_server.py`: preserve `_original_path` for all three LazyMCP route forms; do not alter existing catalog, access-group, toolset, or internal rewrite behavior
- `gateway/routes/allowlist.py`: expose the protected-resource discovery prefix on the gateway component
- `litellm/proxy/_experimental/mcp_server/codemap.yml`: list the new source file
- `tests/test_litellm/proxy/_experimental/mcp_server/test_lazymcp_public_resource.py`: new parser/builder unit matrix, including exact rejection cases
- `tests/test_litellm/proxy/_experimental/mcp_server/test_discoverable_endpoints.py`: real route order, both discovery aliases, root paths, generic unknown identifiers, content type, equivalent metadata, trusted proxy, and hostile headers
- `tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py`: flow/code/token/refresh persistence and cross-resource replay matrix
- `tests/test_litellm/proxy/_experimental/mcp_server/outbound_credentials/test_session_token.py` and `test_session_credentials.py`: exact claim round trips, strict malformed-claim rejection, and access/refresh parity
- `tests/test_litellm/proxy/_experimental/mcp_server/auth/test_user_api_key_auth_mcp.py`: no-token/invalid-token challenge matrix and admission mismatch rejection before user reload
- `tests/test_litellm/proxy/test_dynamic_mcp_route.py`: original-path preservation and unchanged root/scoped/toolset rewrites; add LazyMCP cases without weakening existing unknown-name tests
- `tests/test_litellm/proxy/test_component_allowlists.py`: split-component ownership for inserted and appended discovery routes
- `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py`, `test_mcp_toolset_scope.py`, `test_mcp_oauth_passthrough.py`, `test_mcp_oauth_passthrough_tools.py`, and `test_rest_endpoints.py`: mapped preservation selections, changed only where an assertion must explicitly pin the new boundary
- `.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md`: implementation-time steady-state contract required by the SCR

No schema, migration, registration, catalog, credential, image, deployment configuration, or upstream OAuth module belongs in the code change. `litellm/proxy/_types.py` should change only if implementation tests prove a server-only exact-resource field is needed there; the preferred design compares the signed principal directly during admission and avoids another mutable auth-model field

### Atomic Implementation Sequence

1. Add the pure parser/builder module and its exhaustive unit tests. Update only the local MCP CodeMap for the new maintained source/test files
2. Add all six metadata routes and route-order/root-path/trusted-base tests. Add the gateway component allowlist entry and its ownership tests in the same commit so no componentized state serves partial discovery
3. Add optional exact-resource fields through connect flow, code, session principal, access token, and refresh token. Add focused mint/open and full DCR matrices before changing admission
4. Add strict code and refresh equality gates, including missing-resource and cross-resource replay rejection for all three LazyMCP forms. Preserve existing `/mcp` and per-server DCR fixtures byte-for-shape when the new field is absent
5. Preserve `_original_path` in the three proxy routes, then add exact admission and challenge generation at the auth edge. Verify the equality gate runs before user reload and permission/catalog access
6. Run focused preservation suites for LazyMCP resolution, toolsets, access groups, tool permissions, unknown names, MCP REST, gateway DCR, session credentials, delegated/pass-through/OBO/BYOK/upstream auth, route checks, and component allowlists
7. Publish the architecture contract, run lint/type checks and mapped complete suites, run `staticeng_validate` after CodeMap changes, then build and exercise the immutable candidate and rollback gates from the SCR

Do not split steps 2, 3/4, or 5 across deployable commits or images. A metadata-only deployment advertises a token contract admission cannot enforce; a token-only deployment creates credentials an older admission edge may accept too broadly

### Verification and Evidence Matrix

| SCR AC | Focused evidence | Preservation evidence |
| :--- | :--- | :--- |
| AC-1 / AC-2 | Parser unit matrix plus real FastAPI GETs for all six templates, aliases, root paths, exact metadata equality, omitted empty fields, generic identifiers, hostile headers, and route collisions | Existing aggregate/per-server discovery tests and bare-origin discovery remain unchanged |
| AC-3 | Auth-edge tests for all three no-token and invalid-token challenges; selection headers do not alter URL | Existing `/mcp`, per-server, pass-through, delegated, and upstream challenge suites |
| AC-4 | DCR authorize/code/token/refresh tests for aggregate, two scopes, and two toolsets; missing/malformed/foreign/rewritten/cross-resource replay; token claim round trips; admission mismatch before reload | Existing client/redirect/PKCE/single-use/user-revalidation tests, permission unions, IP filtering, toolset scope, and egress credential scrub |
| AC-5 | Original-path tests and authenticated LazyMCP initialize/list/call tests using existing resolution pipeline | `test_mcp_server.py`, `test_mcp_toolset_scope.py`, `test_mcp_oauth_passthrough*.py`, `test_rest_endpoints.py`, `test_dynamic_mcp_route.py`, route checks, and component allowlists |
| AC-6 | Focused tests first, complete mapped suites, touched-file lint/type checks with zero new suppressions, `staticeng_validate`, immutable Docker smoke and health baseline | Same reviewed digest staged and prior digest recorded for rollback |
| AC-7 | Steady-state architecture contract cross-linked from the SCR, secret-free task evidence, and no raw OAuth artifacts in logs | Product overview and feature inventory explicitly unchanged |

Secret-free smoke evidence must assert exact JSON fields and challenge URLs but must never print bearer tokens, authorization codes, refresh tokens, cookies, client ids that embed registration state, or raw authorization payloads

### Risks and Required Guardrails

- **Public path loss:** current LazyMCP route rewrites do not consistently retain `_original_path`; audience checks or challenges after rewrite would incorrectly describe `/lazymcp` or `/mcp`. Preserve before every rewrite
- **Silent aggregate widening:** current unresolved-resource behavior intentionally falls back to unscoped `/mcp`. Never call it for a LazyMCP-shaped resource; the dedicated parser returns a failure value and the OAuth edge maps it to `invalid_target`
- **Permission confusion:** a scoped resource identifier may match a server, access group, or toolset name. The OAuth layer must not resolve or grant any of them. Existing post-admission path/toolset logic remains authoritative
- **Discovery enumeration:** metadata handlers must not call Prisma, the server registry, access-group lookup, toolset lookup, IP visibility, or permission code. Existing, hidden, unauthorized, and unknown identifiers receive byte-equivalent metadata except for their requested canonical resource
- **Credential leakage:** session access/refresh values remain `SecretStr`; no new logging may include resource-bearing cookies/codes/tokens. The existing egress scrub remains mandatory and unchanged
- **Reverse-proxy injection:** all builders use `get_request_base_url()` and trusted proxy policy. Raw Host/forwarded values never enter the parser's expected base directly
- **Root-path duplication:** `PROXY_BASE_URL` may already carry a path while `SERVER_ROOT_PATH` is configured. The new module must normalize one `{root}` owner and reject inconsistent/duplicated configuration rather than concatenate twice
- **Component 404s:** the gateway currently drops `/.well-known/`. Metadata and gateway allowlist changes ship atomically and are pinned by component tests
- **Rolling-version strict models:** additive optional fields must default to `None` and serialize with `exclude_none=True`. A LazyMCP-bound artifact must not be redeemed or admitted by an older pod; deployment must use the immutable candidate gate rather than mixed-version rollout for this security boundary
- **Legacy ambiguity:** a root DCR authorization request with no `resource` cannot be distinguished from an existing `/mcp` flow. It remains legacy `/mcp` for preservation. Once a valid LazyMCP resource starts a flow, every later artifact and request is strict and missing resource fails closed

## Acceptance Criteria Evidence

- [x] AC-1: The impact surface names each runtime/test file, owning function or interface, six route templates, router inclusion order, and split-component allowlist change
- [x] AC-2: The handoff defines one canonical parser/builder module, exact accepted forms, sole trailing-slash alias, generic catalog-free metadata, and exhaustive fail-closed rejection rules
- [x] AC-3: Current tokens are explicitly shown not to carry exact audience; the handoff defines exact resource persistence through flow, code, access token, refresh token, rotation, and admission while preserving legacy `resource_server_id`
- [x] AC-4: Risks and regression boundaries cover `/mcp`, MCP REST, per-server and LazyMCP routing, upstream/delegated/pass-through/OBO/BYOK auth, all permission axes, toolsets, groups, hostile proxies, root paths, credential egress, and component allowlists
- [x] AC-5: The seven-step atomic sequence and SCR AC evidence matrix define focused, mapped, static, Docker, staging, and rollback verification with no skipped required gate

## Documentation Impact

No steady-state documentation or CodeMap was changed by this investigation. The implementation task must add `.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md`, cross-link it from the SCR, and update the two local MCP CodeMaps for the new source and test files. `PRODUCT_OVERVIEW.md` and `FEATURES_LIST.md` remain unchanged as required by the approved SCR

## Validation Evidence

`git diff --check` passed for this task file. `staticeng_validate` was run and failed only on the repository's pre-existing broad missing-CodeMap inventory, beginning with `litellm/llms/gradient_ai`, `litellm/llms/novita`, and `litellm/llms/llamafile`; this investigation added or changed no CodeMap and did not repair unrelated dirty orchestrator state. Runtime and test suites were not run because the task explicitly prohibits runtime/test edits and requests architecture-only evidence

## Architecture Handoff

[Agent Message] From: technical_architect To: product_manager

Architecture review is complete and implementation-ready. Existing gateway DCR tokens carry only an optional internal `resource_server_id`, not the exact public resource. Implement the dedicated canonical LazyMCP resource module, persist its exact URI through flow/code/access/refresh artifacts, and enforce equality at `_admit_gateway_session()` before any identity or permission resolution. Keep unresolved-resource fallback confined to legacy `/mcp`, preserve every existing authorization and upstream-credential boundary, and execute the atomic sequence and evidence matrix recorded above

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-002 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
