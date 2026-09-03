# TASK-2026-09-02-005 Evidence Summary

## Summary

The exact retained image does not have a discovery routing or packaging defect. The six HTTP 404 responses are produced inside the matched discovery handlers because the TASK-011 Docker request has no trusted public origin. This is the required fail-closed behavior for a non-loopback peer without a configured public base

`PROXY_BASE_URL=https://candidate.invalid` is the proven discriminating input. With the variable unset, or set to non-loopback HTTP, all six aliases return 404. With only that variable changed to reserved HTTPS, the unchanged exact image returns HTTP 200 and exact aggregate, scoped, and toolset metadata for all six aliases

## Proven Root Cause

`oauth_protected_resource_lazymcp*` calls `_lazymcp_protected_resource_metadata`, which calls `parse_lazymcp_resource`. `_trusted_base` accepts authority only from a valid configured `PROXY_BASE_URL`, a trusted proxy request, or literal loopback authority from a loopback peer. It also rejects non-loopback HTTP. The isolated candidate is reached from another Docker peer over internal HTTP and the recorded Reopen 4 runtime configuration provides no `PROXY_BASE_URL`, so `_trusted_base` returns `None`, parsing returns `LazyMcpResourceError`, and the already-matched handler deliberately raises `HTTPException(404, "Not Found")`

The source cold-start test is not equivalent to that candidate invocation. It sets `PROXY_BASE_URL=https://gateway.example` before requesting the six paths. The existing dedicated security regression also pins both sides: an untrusted Docker peer without a public base must receive 404, while the same peer with `PROXY_BASE_URL=https://candidate.invalid` must receive all six 200 documents

## Runtime And Packaging Comparison

- Exact final image: `sha256:eeb98cc84cd1f3b73ce1dc584ac9922e47515fc3db46beb8825283fddf6b2820`, linux/amd64, revision label `a826c38dc0737afd9eef00a2e9f50d2413ca92eb`
- Final entrypoint is `docker/prod_entrypoint.sh`, command is `--port 4000`, working directory is `/app`, and the console script resolves to `litellm:run_server`
- The runtime is the monolithic proxy image. `/app/gateway` and `/app/backend` are absent, so component route trimming is not active. The gateway allowlist nevertheless covers `/lazymcp`, `/toolset/`, and `/.well-known/oauth-protected-resource`
- Installed `litellm` version is `1.100.0`; `direct_url.json` records non-editable `file:///app`; required Python modules and the OpenAPI snapshot are present in site-packages
- Installed SHA-256 values match commit `a826c38` exactly: `_lazy_features.py` `27fd14e943b0dc04c4d15a4e1b127c8be143f7ccb6f8a7f63d5ebe5a32c8ac23`, `proxy_server.py` `f7f8bfc58529f3fcfdc108f48dfa2f7dfd68a53da8b9462de36a9a1e55f9ea1f`, `discoverable_endpoints.py` `c4e5e367e43dddaad31a30a9a0c1761ebdfefd8a8a7849b370203dd979b71de3`, `lazymcp_public_resource.py` `7f94d367f4f046a17283201c9f3d3f0d7ff2dea0b40ad21de03d4559f014b7ca`, and `_lazy_openapi_snapshot.json` `12489392505e1c66f50bbf148d07c4260c6335a693d487d541b6e7d58310081e`
- `mcp_discoverable` is the sole lazy matcher for each discovery path; `lazymcp_routes` rejects all `/.well-known/` forms; `SERVER_ROOT_PATH` and app root path are empty in the reproduced image
- All six concrete APIRoutes exist before the first request at app route indices 559 through 564 and match their requests with `Match.FULL`
- OpenAPI advertises all six paths both with and without `PROXY_BASE_URL` because it describes declared routes, while the trusted-origin decision is request-time security behavior

## Discriminator Matrix

| Exact image input | Peer/base shape | Six discovery results |
| --- | --- | --- |
| `PROXY_BASE_URL` unset | non-loopback Docker/internal HTTP | 6 x HTTP 404 `{"detail":"Not Found"}` |
| `PROXY_BASE_URL=http://candidate.invalid` | configured non-loopback HTTP | 6 x HTTP 404 `{"detail":"Not Found"}` |
| `PROXY_BASE_URL=https://candidate.invalid` | configured reserved HTTPS origin | 6 x HTTP 200 with exact resources and `authorization_servers: ["https://candidate.invalid/mcp"]` |

The HTTPS run returns resources `https://candidate.invalid/lazymcp`, `https://candidate.invalid/lazymcp/team-a`, and `https://candidate.invalid/toolset/tools-a/lazymcp`, identically across path-inserted and appended aliases

## Import Order And Precedence

`proxy_server.py` eagerly imports and includes the discoverable router, then attaches lazy middleware. Therefore the routes exist at cold process start. Because the same module also remains in `LAZY_FEATURES` and `app.state.lazy_loaded` begins empty, the first matching request imports the cached module and includes its router a second time. The earlier and duplicate routes point to the same handlers, and route matching is full before and after loading. This duplicate-registration inconsistency is real but is not the 404 cause: the matched handler returns 404 with an untrusted origin and 200 with the one-input HTTPS correction

`_include_discoverable_router` reorders the child router before including it, but it cannot reorder APIRoutes already copied into the app by the eager include. The six LazyMCP routes are already ahead of generic protected-resource routes in the app, so precedence is correct for this case

## Exact Implementation Recommendation

Do not change application routing, origin trust, packaging, root-path handling, or component allowlists to fix this incident

Change the isolated qualification harness to pass `PROXY_BASE_URL=https://candidate.invalid` into the candidate container and use that same canonical external base for expected metadata and challenge/audience assertions. Keep transport to the disposable container internal; the value establishes canonical public identity and does not require DNS resolution or TLS termination inside the isolated network

Add a dedicated `tests/proxy_migration_tests/test_image_lazymcp_discovery.py` image gate, and list it in `tests/proxy_migration_tests/codemap.yml`. Do not put this behavior in `test_component_image_serves_offline.py`, which tests split-component Prisma startup rather than the shipped monolithic proxy. The new live-image matrix must:

1. Starts the built image with a reserved HTTPS `PROXY_BASE_URL`
2. Probes all six aliases from a non-loopback peer and asserts exact HTTP 200 JSON
3. Probes an otherwise identical instance without `PROXY_BASE_URL` and asserts all six remain generic HTTP 404
4. Asserts `/openapi.json` contains the six templates but does not treat that as runtime success
5. Runs against the normal image entrypoint and immutable built subject, not `TestClient` or source imports

No product source or build logic change is needed. First rerun the corrected TASK-011 functional matrix against the unchanged retained digest, which isolates the harness correction without rebuilding. A later test-only repository commit requires a newly built candidate under the SCR identity rules before that new revision can qualify. Rollback is removal of the test/harness commit and continued retention of the rejected digest; no schema or data rollback exists

## Preservation Gates

The next qualification must preserve exact root/scoped/toolset discovery documents, both alias forms, fail-closed untrusted-origin behavior, exact Bearer challenges, DCR resource binding, cross-audience rejection, LazyMCP transports, `/mcp`, MCP REST, route ownership, root-path behavior, component allowlist coverage, OpenAPI snapshot consistency, normal entrypoint startup, and reconnect stability

## Acceptance Criteria Coverage

- **AC-1: PASS.** Exact image and source runtime modules, routes, feature state, environment, entrypoint and response behavior were compared
- **AC-2: PASS.** Packaging, lazy discovery, OpenAPI, import order, precedence, root path and component mode were traced and separated from request-time trust validation
- **AC-3: PASS.** A one-variable A/B run proves valid HTTPS `PROXY_BASE_URL` is the discriminator and the handler's origin trust check is the root cause
- **AC-4: PASS.** The minimal correction, image-level regression, preservation matrix, candidate impact and rollback are specified
- **AC-5: PASS.** Investigation is read-only outside task/evidence records; no source, test, build, registry, production, push or deployment mutation occurred

## Documentation Impact

No steady-state product, architecture, technical, or CodeMap update is required. Existing `.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md` already requires the observed trusted-origin behavior

## Open Risks

The eager plus lazy duplicate registration should be evaluated separately because it increases route-table ambiguity and undermines lazy-state truth, but changing it is unnecessary for this incident and could broaden release risk. Candidate signing and attestation remain independent blockers

## Recommended Next Step

PMA should activate a revised TASK-006 for harness/test correction, not a routing behavior change. Reuse the retained digest for the corrected functional rerun; require a full candidate rebuild only after a repository test commit changes the reviewed source revision

## Signed Handoff

[Agent Message] From: technical_architect To: product_manager

ROOT CAUSE PROVEN. Exact image `sha256:eeb98cc84cd1f3b73ce1dc584ac9922e47515fc3db46beb8825283fddf6b2820` declares and live-registers all six routes. The 404 is intentional trusted-origin rejection because the non-loopback Docker harness omitted `PROXY_BASE_URL`; setting only `PROXY_BASE_URL=https://candidate.invalid` yields six exact 200 responses. Fix the harness and add packaged-image positive and negative regressions. Do not weaken origin validation or alter routing
