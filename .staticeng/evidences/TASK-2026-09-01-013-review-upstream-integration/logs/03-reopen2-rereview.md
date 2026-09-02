# Reopen 2 Independent Re-review

## Passing Checks

- Exact parents: fork `51b5f7e474e6de50bdec2eea64e33f4878fadf4b`, upstream `10631eb834c7802aa61611e807474170b8a4d425`
- Unmerged entries: zero
- Before review writes: zero unstaged and untracked paths
- Cached diff check: pass
- Four budget files: no raised limit versus either parent
- Three unrelated normalization files: exact `HEAD` content and excluded from staged diff
- `staticeng_validate`: pass, zero warnings
- Direct transport routes: 11 passed
- Lazy matcher coverage: six passed
- Mapped LazyMCP evidence: 767 passed, eight warnings
- Exact-upstream `make check`: pass
- Prior Rust, dashboard/audit, and migration gates remain documented as passing

## Blocking Runtime Probe

With a cold TestClient against `litellm.proxy.proxy_server.app`:

```text
/lazymcp/.well-known/oauth-protected-resource -> 404
/lazymcp/team-a/.well-known/oauth-protected-resource -> 404
/toolset/tools-a/lazymcp/.well-known/oauth-protected-resource -> 404
```

The same paths are registered in `litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py` and advertised by the generated OpenAPI snapshot and dashboard `schema.d.ts`

## Root Cause

- `lazymcp_routes` uses suffixes `('/lazymcp', '/lazymcp/')`, which claim canonical discovery paths ending in `/lazymcp`
- `lazymcp_routes` uses prefix `/lazymcp`, which claims alternate root/scoped metadata paths
- Import side effects load discovery module code without registering its router, while the transport router's scoped route can consume `/.well-known/oauth-protected-resource` as a scope name
- Snapshot generation attributes side-effect discovery paths to the wrong feature and duplicates them under `mcp_discoverable`

## Verdict

Reject without commit. Separate discovery and transport route ownership, add cold-start runtime metadata tests, regenerate OpenAPI/types, rerun mapped and exact-upstream gates, then return for rereview
