---
id: SCR-2026-08-31-001-lazymcp-oauth-discovery
status: implemented
requested_by: product_owner
approved_by: product_owner
date: 2026-08-31
---

# SCR: LazyMCP OAuth Discovery

## Problem and Outcome

OAuth clients connecting to a public LazyMCP transport can probe protected-resource metadata URLs that do not exist, then receive a challenge or metadata document describing the internally rewritten `/mcp` route instead of the public LazyMCP resource. Strict RFC 9728 clients can reject that mismatch

LazyMCP must expose protected-resource metadata and challenges for each public transport identity, and its gateway authorization flow must issue tokens bound to that exact identity. The internal `/mcp` rewrite remains an implementation detail and must not change the OAuth resource or audience

## Supported Resources and Discovery

`{origin}` is the trusted externally visible scheme and authority. `{root}` is the configured public root path, normalized to either empty or one leading-slash path without a trailing slash. `{base}` is `{origin}{root}`. Route generation must use the existing trusted proxy and root-path policy; untrusted `Host` or forwarded headers must not control these URLs

Transport aliases with one trailing slash resolve to the corresponding canonical resource without that slash. No other path, case, percent-encoding, dot-segment, query, or fragment normalization is permitted

| Canonical public resource | RFC 9728 path-inserted discovery | Compatibility path-appended discovery |
| :--- | :--- | :--- |
| `{base}/lazymcp` | `{origin}/.well-known/oauth-protected-resource{root}/lazymcp` | `{base}/lazymcp/.well-known/oauth-protected-resource` |
| `{base}/lazymcp/{scope}` | `{origin}/.well-known/oauth-protected-resource{root}/lazymcp/{scope}` | `{base}/lazymcp/{scope}/.well-known/oauth-protected-resource` |
| `{base}/toolset/{name}/lazymcp` | `{origin}/.well-known/oauth-protected-resource{root}/toolset/{name}/lazymcp` | `{base}/toolset/{name}/lazymcp/.well-known/oauth-protected-resource` |

Both discovery forms for one resource must return HTTP 200, `application/json`, and equivalent metadata. The `resource` value must equal the canonical public resource exactly. `authorization_servers` must contain the existing gateway authorization-server identifier `{base}/mcp`. Empty multi-value metadata fields, including `scopes_supported`, must be omitted as required by RFC 9728 rather than emitted as empty arrays

Metadata for a syntactically valid `{scope}` or `{name}` is generic and must not reveal whether that identifier exists, is hidden, is unauthorized, denotes a server, denotes an access group, or denotes a toolset. Discovery does not grant access and must not query or expose the protected catalog. Unknown transport identifiers remain fail-closed and must never fall back to aggregate access

## Authentication Challenges

Every HTTP 401 emitted by a supported LazyMCP transport must include a Bearer `WWW-Authenticate` challenge whose absolute `resource_metadata` value is that transport's RFC 9728 path-inserted discovery URL from the table

A request carrying an invalid, expired, or revoked bearer token retains `error="invalid_token"`. A request without a bearer token does not add that error. `x-mcp-servers` and similar content-selection headers do not change the public resource identity or its challenge

Challenges for `/mcp`, per-server MCP, delegated OAuth, OAuth pass-through, on-behalf-of flows, and upstream servers retain their existing resource metadata and error behavior

## Authorization, DCR, and Audience Isolation

The existing gateway authorization server and dynamic client registration endpoints are reused. This SCR does not create a new issuer, registration service, token endpoint, client type, or credential store

For a LazyMCP authorization flow:

- The client must send the exact canonical LazyMCP `resource` in both authorization and token requests
- The authorization server must validate same trusted origin and one of the three supported path shapes, then preserve the complete canonical resource through consent state, authorization code, access token, and refresh token
- Authorization-code redemption must require the same client, redirect URI, PKCE verifier, and exact resource bound to the code. Missing, malformed, foreign-origin, rewritten `/mcp`, or mismatched resources fail closed with an OAuth error and mint no token
- Refresh-token redemption must remain bound to the original exact resource. A caller cannot exchange or rotate it into another aggregate, scope, or toolset audience
- Admission must accept a gateway token only at its exact audience: aggregate tokens at `/lazymcp`, scoped tokens at their exact `/lazymcp/{scope}`, and toolset tokens at their exact `/toolset/{name}/lazymcp`. Tokens are not interchangeable between these resources
- Resource binding limits where a token is accepted; it never grants a server, group, tool, or toolset permission. Existing identity, key, team, access-group, tool, IP, and toolset permission checks still apply after token validation
- A syntactically valid scope is resolved through the existing authenticated LazyMCP permission pipeline. DCR and discovery must not reinterpret an access group or toolset as an individual server

One registered public client may start separate authorization sessions for distinct resources, but every code and token remains isolated to the resource of its own session

## Compatibility and Preservation

- `/mcp` transport, protected-resource metadata, authorization metadata, DCR, and challenge behavior remain unchanged
- MCP REST endpoints, standard and legacy per-server MCP routes, route ownership, and split-component behavior remain unchanged except for adding the explicit LazyMCP metadata routes required here
- LazyMCP server selection, aggregate discovery, access groups, toolsets, tool filtering, unknown-name rejection, and all existing permission decisions remain unchanged
- LiteLLM admission credentials and gateway session tokens remain separate from upstream MCP credentials. No inbound bearer is passed through to an upstream service
- Delegated OAuth, OAuth pass-through, on-behalf-of auth, BYOK, static headers, and per-user upstream OAuth behavior remain unchanged
- No database migration, registration mutation, credential change, catalog redesign, model-routing change, or access-log suppression is part of this change

## Security Constraints

- Production resource and metadata URLs require HTTPS. Loopback HTTP may be used only where existing local-development policy permits it
- URL construction must use the established trusted external-base calculation and must resist host-header and forwarded-header injection, duplicate root paths, fragments, queries, dot segments, and ambiguous encodings
- Metadata endpoints are unauthenticated but disclose only generic gateway metadata. They must not reveal catalog membership, grants, credentials, upstream URLs, or identifier existence
- Exact code-point URL equality is required after the narrowly defined trailing-slash canonicalization. Tokens, authorization codes, refresh tokens, cookies, credentials, and raw authorization payloads must not be logged or included in evidence
- Route ordering and component allowlists must prevent parameterized MCP or LazyMCP routes from capturing a more specific well-known route
- Any unknown resource shape, audience mismatch, permission failure, or unresolved transport identity fails closed without aggregate fallback

## Verification Contract

Focused tests must cover:

- Both discovery forms for aggregate, scoped, and toolset resources, with exact metadata equality, content type, canonical `resource`, gateway `authorization_servers`, trailing-slash aliases, empty and non-empty root paths, trusted external-base handling, and hostile header rejection
- Generic indistinguishable metadata for existing, hidden, unauthorized, and unknown identifiers, plus route-order collisions and fail-closed unknown transport behavior
- Exact `WWW-Authenticate` challenges for all three LazyMCP resource forms, including no-token and invalid-token cases, and proof that selection headers do not alter audience
- Preservation of the public route before internal rewrite and unchanged LazyMCP resolution and permission outcomes
- Full authorization-code and refresh flows for all three resource forms; exact resource persistence; rejection of missing or changed resource; and replay attempts across aggregate, two scopes, and toolsets
- Existing `/mcp`, per-server MCP, MCP REST, OAuth pass-through, delegated OAuth, on-behalf-of, BYOK, upstream authentication, component ownership, key/team/group/tool/toolset permissions, IP filtering, and unknown-name regression behavior

Implementation verification must run the focused selections first, then the complete mapped suites for discoverable endpoints, MCP server routing, MCP admission authentication, gateway DCR, toolset scope, and component allowlists. All task-touched files must pass repository lint and type checking with zero new suppressions or budget regressions

A candidate immutable Docker image must be tested in the lower-risk environment before promotion. Secret-free smoke evidence must prove both aggregate metadata forms return 200 and the exact canonical resource, unauthenticated `/lazymcp` advertises the path-inserted metadata URL, a real authorized client initializes and invokes a permitted tool, repeated reconnections produce no discovery 404s, and `/health/readiness`, `/mcp`, MCP REST, and upstream MCP integrations remain healthy

Before deployment, record the current immutable digest, health baseline, and discovery error baseline. Promote the same reviewed digest only after all gates pass. On any authentication, audience-isolation, permission, route, toolset, `/mcp`, MCP REST, or upstream regression, redeploy the prior digest and verify the baseline surfaces. No data rollback or migration is expected

## Documentation Impact

Implementation must publish `.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md` as the steady-state technical source of truth and cross-link it from this SCR. The contract must retain the resource matrix, challenge rules, audience isolation, preservation boundaries, security constraints, and rollback behavior

Steady-state contract: `.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md`

Public or operator documentation for configuring a LazyMCP URL must describe the canonical resource and discovery behavior if such a reference exists or is introduced. `PRODUCT_OVERVIEW.md` and `FEATURES_LIST.md` do not require changes because this specification corrects protocol interoperability without adding a product capability or changing the advertised feature inventory

## Non-Goals

- Redesigning LazyMCP discovery, compact tools, catalog contents, server grouping, or toolsets
- Changing model fallbacks, provider tokens, MCP registrations, upstream credentials, grants, retries, timeouts, or cache behavior
- Replacing the gateway authorization server, changing DCR client registration policy, or implementing a new OAuth issuer
- Making metadata prove that a scope exists or that the caller may access it
- Silencing 404 or authentication logs without implementing the required protocol behavior
- Editing runtime code, tests, images, credentials, configuration, or deployments during this specification task

## Numbered Acceptance Criteria

- **AC-1:** Both path-inserted and path-appended protected-resource discovery forms return equivalent valid metadata for `/lazymcp`, `/lazymcp/{scope}`, and `/toolset/{name}/lazymcp`
- **AC-2:** Every metadata document declares a `resource` exactly equal to the canonical trusted public LazyMCP endpoint, with only a known trailing slash canonicalized away
- **AC-3:** Every LazyMCP 401 advertises the matching absolute path-inserted metadata URL and preserves `invalid_token` semantics, while non-LazyMCP challenges remain unchanged
- **AC-4:** Authorization, code exchange, access tokens, and refresh tokens bind to one exact LazyMCP resource, reject cross-resource replay, never infer grants from the resource, and preserve all existing permission checks
- **AC-5:** Observable `/mcp`, MCP REST, per-server MCP, LazyMCP selection and permissions, delegated and upstream authentication, BYOK, component ownership, and unknown-name rejection remain unchanged
- **AC-6:** Focused and complete mapped suites, lint, type checking, immutable Docker candidate smoke tests, staged promotion gates, and digest-based rollback readiness pass with no skipped required gate
- **AC-7:** Security constraints, non-goals, steady-state documentation impact, and explicit Product Owner approval are recorded without secrets

## Approval

Approved by the Product Owner on 2026-08-31 through explicit session approval relayed by the Product Manager. Approval is limited to the behavior and boundaries in this SCR

## Implementation State

Implemented and archived on 2026-08-31 for source/candidate scope only through `TASK-2026-08-31-018-close-lazymcp-oauth-workflow`

Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates
