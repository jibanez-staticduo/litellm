# LazyMCP OAuth Discovery Contract

## Public Resources

LazyMCP has three canonical protected-resource identities relative to the trusted external base: `/lazymcp`, `/lazymcp/{scope}`, and `/toolset/{name}/lazymcp`. One terminal slash is accepted as a transport alias and removed. Identifiers are one non-empty unreserved ASCII segment other than `.` or `..`; no other path, encoding, query, fragment, case, or origin normalization is allowed

Each resource has two equivalent unauthenticated RFC 9728 discovery forms. The path-inserted form is `/.well-known/oauth-protected-resource{root}{resource-path}` and the compatibility form appends `/.well-known/oauth-protected-resource` to the resource. Metadata contains the exact canonical `resource` and `authorization_servers: ["{base}/mcp"]`; empty multi-value fields are omitted. Identifier metadata is generic and does not query or disclose catalog state

The proxy exposes all three transport families through a dedicated lazy feature. It claims only exact `/lazymcp`, `/lazymcp/{scope}`, and `/toolset/{name}/lazymcp` shapes, including one optional trailing slash, and claims neither `/mcp/lazymcp` nor any `/.well-known/` path. The discoverable router is the sole owner of all six canonical and alternate protected-resource routes and precedes transport loading. Public `_original_path` remains unchanged while internal dispatch rewrites through the shared LazyMCP handler. Explicit toolset-name lookup occurs only after admission. A scoped name resolves as an MCP server, toolset, or access group and otherwise returns 404

## Challenges And Audience

Every LazyMCP 401 advertises the resource's absolute path-inserted discovery URL. Missing credentials receive a bare Bearer challenge. Invalid, expired, revoked, unscoped, or wrong-audience gateway credentials also include `error="invalid_token"`. Selection headers do not influence the resource identity

Gateway authorization preserves the exact canonical LazyMCP resource through the connect flow, authorization code, access token, and refresh token. Code and refresh redemption require that exact resource. A token is admitted only on the exact public transport identity retained before the internal route rewrite, and this check runs before user reload or permission resolution. The resource is an audience restriction only; existing key, user, team, organization, IP, server, group, tool, and toolset checks remain authoritative

Gateway session claims also retain upstream's audience and team binding. Session credentials use the configured upstream signing mode, including RS256 key identifiers and verification/rotation, revocation, and introspection. LazyMCP's exact canonical `resource` is carried alongside those claims and remains independently mandatory: neither the proxy API audience nor an MCP server scope authorizes a different LazyMCP endpoint

The explicit `/toolset/{name}/lazymcp` route stores only the server-owned public toolset name and preserved path before entering shared admission. No database or catalog lookup occurs for a request rejected during admission. After admission, including an intentionally anonymous successful admission result, the handler resolves the name to an ID once. Anonymous known-toolset access reaches an explicit 403 rather than unscoped fallback; authenticated access applies the existing toolset authorization boundary once. Admitted database-down, unknown, unauthorized, and permitted outcomes remain 503, 404, 403, and scoped success respectively. Simultaneous name and ID contexts fail closed, and route-owned name context is reset on success and exception with request-task isolation

## Preservation And Security

Legacy `/mcp`, per-server MCP, MCP REST, delegated OAuth, pass-through, on-behalf-of, BYOK, and upstream credential behavior retain their existing token and challenge contracts. Legacy session tokens without an exact resource remain valid on their existing MCP surfaces and fail closed on LazyMCP. No inbound gateway session credential is forwarded upstream

Public URL construction accepts authority only from a valid configured `PROXY_BASE_URL`, a request arriving through the configured trusted-proxy policy, or a literal loopback authority received from a loopback request peer for local development. An invalid non-empty configured base fails closed rather than falling back to Host. Non-loopback public resources require HTTPS; loopback HTTP requires both a loopback authority and loopback peer. Untrusted Host and forwarded headers cannot select a public authority. Foreign origins, userinfo, percent encoding, case-varied LazyMCP markers, backslashes, ambiguous paths, dot segments, duplicate segments, queries, and fragments fail closed. Candidate classification evaluates malformed variants of the three LazyMCP families relative to the validated trusted base/root. Thus rootless `/mcp/team/lazymcp` remains legacy, while with trusted base `https://gateway.example/mcp`, `/mcp/LazyMCP` is a malformed aggregate LazyMCP target and fails closed. `lazymcp` in a legacy authority, identifier, query, or unrelated URL text does not change legacy handling. Discovery handlers remain catalog-free and permission-free

## Deployment And Rollback

Metadata, token binding, exact admission, route preservation, and split-component allowlisting must deploy as one immutable image. Do not run mixed versions for this security boundary. Before promotion, verify the candidate digest, readiness, discovery aliases, exact challenge, authorized initialize/tool invocation, reconnect behavior, `/mcp`, MCP REST, and upstream integrations. Roll back to the recorded prior digest on any audience, permission, route, authentication, or integration regression; no data rollback is required
