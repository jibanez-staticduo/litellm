# Reopen 5 Verification Ledger

## Exact Subjects

```text
source commit: 3ad43aa9c9eb4c14ed2fedbac734dd0775925dca
source tree: 944cdde5d87f20c7944b2cfc92590ecb05d113ad
Dockerfile SHA-256: 6add9603c86fd595c77b30b35ac3e0caacd9bb16828ac9b18ca189b538cae20b
pyproject.toml SHA-256: 6f7d344eb67fd50e4e95052821034bfb23bf13901ce26c81c97c2516efb81b92
uv.lock SHA-256: c623498311bb698c4c798879e22754c145767febf76383c12de6f75794ddfa5f
builder: sha256:04bba4403ac7de87108c539e5e14982e55e3cecbf39b36a6794025cee23de5ad
final: sha256:836d98e7ace653505888d47826ca47e8075a0e64d559c9c61dce5e6298103f0f
platform: linux/amd64
BuildKit: 0.13.1
```

The detached worktree was clean and the approved merge is an ancestor. Builder and final carry exact `org.opencontainers.image.revision=3ad43aa9c9eb4c14ed2fedbac734dd0775925dca` and `staticeng.task=TASK-2026-09-01-011-r5` labels. Python 3.13.15, uv 0.11.26, Rust 1.97.1 and representative native/Prisma imports passed

## Automated Verification

| Gate | Level | Result |
| --- | --- | --- |
| Packaged unset/HTTP/HTTPS discovery and OpenAPI | E2E | PASS, 4 tests |
| Empty database migrations | Integration | PASS, 161 applied |
| Restart and persistent catalog | E2E | PASS |
| Liveness/readiness/models | E2E | PASS |
| Chat non-stream/stream/usage | E2E | PASS |
| Responses non-stream/stream/usage | E2E | PASS |
| Upstream credential separation | Integration | PASS |
| MCP REST list/call and denied key | E2E | PASS |
| Six discovery aliases and exact metadata | E2E | PASS |
| Aggregate/scoped/toolset exact challenges | E2E | PASS |
| DCR code/access/refresh/replay/cross-audience | E2E | PASS for all three resources |
| LazyMCP initialize/list/describe/call | E2E | PASS for aggregate/scoped/toolset |
| Candidate-bound registered FastMCP `add` | E2E | PASS, result 42 |
| Reconnect | E2E | PASS, 120/120 HTTP 200, zero discovery 404 |
| Spend/preservation | Integration | PASS, 14 spend rows; server/toolset/model preserved |
| StaticEng | Static | PASS, zero warnings |

The isolated environment-name allowlist was `DATABASE_URL`, `LITELLM_MASTER_KEY`, `SYNTHETIC_UPSTREAM_API_KEY`, `PROXY_BASE_URL`, and `LITELLM_LOCAL_MODEL_COST_MAP`. Values remain redacted except reserved public base `https://candidate.invalid`. No production environment, config, credential or mount was inspected or attached

Expected authorization failures produced sanitized tracebacks as part of negative challenge and denied-key tests. No test-owned credential value appeared in captured logs, there were zero positive discovery 404s and zero unexpected HTTP 500 responses. The exact proxy was restarted after the full matrix and returned healthy while preserving its model, MCP server, toolset and six discovery aliases

## Supply Chain

Checksum-pinned Syft 1.51.1 generated exact builder/final SPDX and CycloneDX documents. Grype 0.118.0 scanned both subjects with one frozen DB schema 6.1.9 built `2026-09-03T06:30:55Z`

```text
subject   Critical  High  fixable High  Medium  Low  Unknown
builder          0     1             1      12    2        4
final            0     1             1      10    2        2
```

The sole High in each subject is Tornado 6.5.7 `GHSA-mpf4-983q-p7j4`, with fixed version 6.5.8. No ignore, VEX or path exclusion was used. The zero-fixable-High policy therefore rejects both release subjects

Artifact SHA-256 values generated before fail-closed cleanup:

```text
builder SPDX: f070b4db4538b903798dba888af57443cd486c920767b0b8fbecd04fbea8e8ad
builder CycloneDX: 7ae666f856a00054e1f521535a47e1ea9482d669ecd8e5b3c58218525aea3e01
builder Grype: 20c268d6913f3bc53a51caf4eefa4cc12af936de30f739a7a777a911d81d64be
final SPDX: c43ca1104478877271aac5ae370e40dfd2f4e748ccfd54a2aea311d359049dbe
final CycloneDX: 58e9bf295078f60991d5ea4747f6a1d58a8cea3be5f048dd2cac699619602855
final Grype: dae360baa04d6db089832bb106c667c7d91e7cf11d7ed46e0e75d9539edd2e68
DB status: 5e2affddaaec16b266d0984a7ef3986a7d4559991ed8f78ee845493ca00c5024
```

The selected Wolfi digest, uv digest and source lock inputs are unchanged from Reopen 4, whose retained provenance verifies the Wolfi publisher identity and uv SLSA provenance. Exact candidate signing was not attempted: publication, signing identity and signing were not authorized. This is separate from the scan rejection

## Cleanup And Preservation

All task-labelled containers, network, PostgreSQL and Grype volumes, Buildx builder/cache, detached worktree, downloaded Syft/Grype/runtime helper images and temporary artifacts were destroyed. Post-cleanup counts are zero task containers, zero task networks, zero task volumes, only the default builder and one repository worktree. Only the two authorized immutable builder/final images remain

Production was observed only through the two credential-safe allowlisted commands. Before and after are identical: container `7bfb357accc8663e7229ecf8e2df471b9d656625106c216f48ca109de1eb2dba`, selector `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, image ID `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`, running/healthy, restart count 0, OOM false

No publication, candidate signature, deployment, Fedora action or NAS mutation occurred
