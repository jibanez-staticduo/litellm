# Source, Tests, Build, And Image SDK

- Source worktree: `/tmp/opencode/litellm-release-probe-052`
- Worktree mode: detached and clean
- Source revision: `8589869e1c745ae5c66d96e5475aa816496bc060`
- Package version: 1.98.0
- Build count: 1
- Build platform: `linux/amd64`
- OCI revision/version/source: exact source commit / 1.98.0 / repository URL
- Candidate tag: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260819-probe-fix-8589869e1c`
- Candidate manifest: `sha256:f44690e5203983e00a0d01016d65440bf1c4b83a941a490d22d4e7eea443b42a`
- Config digest/image ID: `sha256:84dd79e310f6c5804c50e304fb36479ed6c019ffbff6a64b5b5c91b6b4c4ceed`
- Manifest media type: `application/vnd.docker.distribution.manifest.v2+json`

Verification:

| Gate | Result |
|---|---|
| Mapped LazyMCP/MCP server suite | 279 passed, 0 failed, 0 skipped |
| Prior stream/Responses/telemetry/cache suites | 350 passed, 0 failed, 0 skipped |
| Installed image package version | 1.98.0 |
| Installed image LazyMCP compatibility contract | pass |
| Installed image release-module imports | pass |
| Real MCP SDK repeated Accept with quoted bytes | HTTP 200, one combined Accept field |

The initial `uv run --no-sync` attempt created an empty isolated virtual environment and failed on missing `openai`. No source changed. The clean worktree tests were rerun successfully with the repository's existing dependency-complete Python environment while imports resolved source from the clean worktree

Result: **PASS**
