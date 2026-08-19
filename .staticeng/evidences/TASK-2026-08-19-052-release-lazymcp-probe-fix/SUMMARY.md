# LazyMCP Probe Fix Release

## Summary

Built exactly once from clean detached commit `8589869e1c745ae5c66d96e5475aa816496bc060`, deployed the same immutable LiteLLM 1.98.0 candidate to Fedora and NAS in sequence, passed all compatibility and existing release gates, then promoted `stable` to the exact candidate manifest

Candidate and stable manifest: `sha256:f44690e5203983e00a0d01016d65440bf1c4b83a941a490d22d4e7eea443b42a`

Config digest/image ID: `sha256:84dd79e310f6c5804c50e304fb36479ed6c019ffbff6a64b5b5c91b6b4c4ceed`

## Work Performed

- Created `/tmp/opencode/litellm-release-probe-052` as a clean detached worktree at the exact source commit
- Passed 279 mapped LazyMCP tests and 350 prior stream, Responses, telemetry, logging, Redis/cache, and cache-settings tests
- Built one `linux/amd64` image with exact OCI revision/version/source labels, pushed one unique candidate tag, and passed installed-image imports, contract inspection, and a real MCP SDK repeated-Accept check
- Recreated only Fedora LiteLLM and then only NAS LiteLLM with `--no-deps`; no automatic rollback was used
- Diagnosed NAS root registry authentication failure in place, proved the exact candidate already existed in the shared Docker daemon, and continued from that immutable local image without changing credentials
- Verified authenticated HEAD, generic GET, SSE GET, POST initialize/tools/list/status/describe/call, repeated Accept, quoted parameters, q=0, Responses/Codex, topology, dependencies, health, restart/OOM, preservation, and release-log gates on both hosts
- Promoted `stable` only after both hosts passed; host container identities and start times remained unchanged by promotion

## Acceptance Criteria Coverage

- **AC-1: PASS**. One clean `linux/amd64` build from exact commit `8589869e...bc060` produced LiteLLM 1.98.0 with matching OCI revision/version and inherited stream/telemetry/cache fixes
- **AC-2: PASS**. The mapped LazyMCP suite passed 279 tests, prior release suites passed 350 tests, image imports/contracts passed, and the installed image passed a real MCP SDK repeated-Accept request
- **AC-3: PASS**. Fedora and NAS run manifest `f44690e5...3b42a`; readiness/liveliness are 200, health is healthy, restarts are zero, OOM is false, and dependency/runtime projections are unchanged
- **AC-4: PASS**. Both hosts returned empty 204 for authenticated HEAD, generic `*/*` GET, and JSON GET. SSE GET and MCP initialize/tools/list/status/describe/call returned 200 without 405/406
- **AC-5: PASS**. Both hosts accepted repeated Accept fields and quoted positive-quality parameters through SSE, while quoted and ordinary `q=0` requests returned empty 204
- **AC-6: PASS**. Fedora native account2/direct account2/public fallback Responses passed. NAS native default/direct default/direct account2/public default Responses passed. Both hosts passed harmless LazyMCP calls and clean stream/telemetry/cache/MCP log gates
- **AC-7: PASS**. `stable` resolves exactly to `sha256:f44690e5...3b42a`; Fedora and NAS container IDs/start times were unchanged by promotion
- **AC-8: PASS**. This packet contains sanitized build, deployment, protocol, preservation, incident, and promotion evidence. Primary-worktree Fedora StaticEng artifacts remain unmodified and no commit was created

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. The source behavior was documented and approved in TASK-048; this task changed runtime image selection, the stable tag, and operational evidence only

## Open Risks

- NAS root still lacks private-registry credentials. The exact candidate was already present in the shared daemon, so deployment safely continued without credential mutation, but future cold pulls as root would hit the same operational issue
- `staticeng_validate` remains blocked by inherited repository-wide broken links and missing CodeMaps; broad repair would alter unrelated shared-worktree artifacts

## Recommended Next Step

PMA should route this completed release packet for independent QA and closure
