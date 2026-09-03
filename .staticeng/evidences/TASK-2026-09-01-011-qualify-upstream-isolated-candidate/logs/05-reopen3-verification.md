# Reopen 3 Verification Ledger

## Exact Subjects

```text
source commit: 165a94ecfbf21d7ff4626815ac6b298ac34e2adb
source tree: e371115d08e1b8adc1d1a5f774166573768a895b
Dockerfile SHA-256: 9e1200cd6d602548ec3932751b37d88f17a899295840f5c50812cde95a6d391d
builder: sha256:e0c530bb94b6fb9fde38d1d32d2662177ebef280cdcb4bc7b3c8e68e4d71e104
final: sha256:00b239d81b428a143d50a695c59839e0c387df0f66da116d80e5b79c8c524889
platform: linux/amd64
Buildx: 0.32.1
BuildKit: 0.13.1
```

The detached worktree was clean. Both reviewed upstream commit `10631eb834c7802aa61611e807474170b8a4d425` and approved merge `0573332425de92ad8f17f6eb3196fce0d3ce7f22` are ancestors. Builder and final labels bind the full source revision and task identity. Python 3.13.15, glibc 2.44, Rust 1.97.1, native imports, Prisma client/engines, entrypoint and final command passed

## Isolated Runtime

The disposable stack used only uniquely labelled `task011r3-*` objects: one network, PostgreSQL 16 volume/container, synthetic OpenAI-compatible upstream, synthetic FastMCP upstream, and exact final proxy. It attached no production network, volume, bind mount, config, database, credential, or Docker socket

- Empty PostgreSQL migration: 161 migrations applied; restart remained 161 and readiness returned healthy/connected
- Inventory: exactly one synthetic model
- Chat Completions: non-stream and stream passed with content and 40-token usage
- Responses: non-stream and stream passed with completed response and 30-token usage
- Upstream auth: the synthetic provider independently required its distinct bearer; candidate calls passed without forwarding the inbound LiteLLM credential
- MCP REST: registered DB server listed only permitted `add`; authorized call returned 42; ungranted key call returned 403
- LazyMCP: aggregate, access-group-scoped and DB-toolset initialize/list passed; aggregate and toolset `mcp_call` invoked the registered real synthetic upstream and returned 42
- Discovery/challenges: all six RFC 9728 aliases returned exact reserved resources; aggregate/scoped/toolset no-token, selection-header, malformed-session and invalid-key challenges were exact
- DCR: aggregate/scoped/toolset register, authorize, code, exact-resource access, refresh rotation, code replay rejection, old-refresh replay rejection and cross-resource rejection passed
- Reconnect: 360/360 discovery requests returned 200 with zero 404; proxy restart preserved migrations, DB registrations, inventory and real tool execution
- Logs: no traceback, unhandled exception, 404/500 burst, migration failure, or synthetic credential value appeared in captured service logs
- Spend/log rows recorded successful `acompletion`, `aresponses`, and `call_mcp_tool` outcomes

## Supply Chain

Checksum-verified standalone tools were Syft 1.51.1, Grype 0.118.0 and Cosign 3.1.3. Syft emitted durable exact-subject SPDX JSON and CycloneDX JSON artifacts. Both scans used frozen Grype DB schema 6.1.9, built `2026-09-02T06:35:12Z`, database SHA-256 `e9b663f8ea64d5a2bd2d850b8eebfee762fd7a835e3220fff9084d3832838eb6`

```text
builder SPDX: 6e2d42f6e2d32a0cdd0faf16c90e4ef23b409e72c1f2c88a482620f741239805
builder CycloneDX: b03b0176fed13940daf227bd9d04aca7e84028391c1cd59353de700ff974dcdf
builder Grype: 7ecbe4f503176bdd60cf29b142e25a43ecfc0d691b188ba307a6a08a7305ae01
final SPDX: 42dcdb053613e3b1112422f1d593dcd20c8b26e03dd8c59b644b3e7d2f8ff5f0
final CycloneDX: 1d5e61af1b75fb2dce9f6e2ccfb1d34cb06a314bcbd01432485588d695725241
final Grype: f0f0ae307304bb005b8f29e5a82df9bbc7cb6091e9da57413a58d3079eded3c6
```

Final scan: 0 Critical, 0 High, 9 Medium, 2 Low. Builder scan: 0 Critical, 6 fixable High, 26 Medium, 13 Low. The six builder High matches are setuptools 68.1.2 (`GHSA-cx63-2mw6-8hw5`, `GHSA-5rjg-fvgr-3xxf`), quinn-proto 0.11.14 (`GHSA-4w2j-m93h-cj5j`, duplicate package evidence), and rustls-webpki 0.103.10 (`GHSA-82j2-j2ch-gfr8`, duplicate package evidence). Policy requires zero fixable High across release subjects, so this is blocking

The Wolfi base signature, SPDX attestation, SLSA v1 provenance and apko image-configuration attestation verified. The uv digest exposes SLSA provenance but has no Cosign signature. Rust and Node official image digests have no Cosign signatures. No approved candidate signing identity or keyless OIDC token existed, and registry publication was unauthorized; therefore exact builder/final signature and attestation gates are unfulfilled

## Cleanup And Preservation

All disposable containers, network, volume, task BuildKit builder/cache, detached worktree, downloaded tools, frozen 2 GiB Grype database and temporary artifacts were destroyed. Post-cleanup counts for task-labelled containers/networks/volumes were zero, only the pre-existing default builder remained, and `/tmp/opencode/task011-r3` was absent. The two retained immutable images and repository evidence are the only allowed remnants

Production was observed only through the two allowlisted commands. Before and after values were identical: container `7bfb357accc8663e7229ecf8e2df471b9d656625106c216f48ca109de1eb2dba`, selector `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, image ID `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`, running/healthy, restart count 0, OOM false

No mutable tag, registry publication, fork-main push, deployment, Fedora action, NAS production mutation, or production secret/config/data read occurred

`staticeng_validate` passed with all source directories indexed, hierarchy valid and zero warnings
