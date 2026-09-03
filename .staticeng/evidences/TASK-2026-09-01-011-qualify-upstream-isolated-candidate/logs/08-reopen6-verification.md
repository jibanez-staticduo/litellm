# Reopen 6 Verification Ledger

## Exact Subjects

```text
source commit: bf58974a935521fa570fa7e280c51a00b2e5b54e
source tree: 5bb1b3185d25ba851482ee022503178996df3341
Dockerfile SHA-256: 6add9603c86fd595c77b30b35ac3e0caacd9bb16828ac9b18ca189b538cae20b
pyproject.toml SHA-256: aec8efa2370e3dda65d7b8d5bb7383784ac83a732443b99e4a6eefc574b9b53f
uv.lock SHA-256: b81071cfae206e31ed13569b07acf13e4424a901ee584d0e157d9129337bdcf3
builder: sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac
final: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
platform: linux/amd64
BuildKit: 0.32.2
```

The detached worktree was clean at the exact PMA commit. Builder and final carry `org.opencontainers.image.revision=bf58974a935521fa570fa7e280c51a00b2e5b54e` and `staticeng.task=TASK-2026-09-01-011-r6`. Python 3.13.15, uv 0.11.26, Rust 1.97.1, Tornado 6.5.8, representative native imports, Prisma generation and the normal entrypoint passed

## Acceptance Criteria Matrix

| AC | Gate | Level | Result |
| --- | --- | --- | --- |
| AC-1 | Clean exact source, labels, amd64 and retained immutable identities | Integration | PASS |
| AC-2 | Packaged unset/HTTP/HTTPS discovery and OpenAPI | E2E | PASS, 4/4 |
| AC-2 | Six positive aliases and exact metadata | E2E | PASS, 6/6 |
| AC-2 | Aggregate/scoped/toolset exact challenges | E2E | PASS, 3/3 |
| AC-2 | DCR registration, code/access/refresh/replay and audience isolation | E2E | PASS for all three resources |
| AC-2 | LazyMCP initialize/list/describe/call and candidate-bound FastMCP `add` | E2E | PASS for aggregate, scoped server and explicit toolset |
| AC-3 | Empty database migrations and idempotent restart | Integration | PASS, 161 migrations then no pending migrations |
| AC-3 | Liveness/readiness/models, Chat and Responses non-stream/stream/usage | E2E | PASS |
| AC-3 | Upstream credential separation, MCP REST and denied key | E2E | PASS |
| AC-3 | Reconnect, spend and restart preservation | E2E/Integration | PASS, 80/80 reconnect, 15 spend rows |
| AC-3 | Runtime log redaction | Security | PASS, no synthetic credential value present; zero unexpected 500 and zero positive discovery 404 |
| AC-4 | Exact base/uv/builder/final SPDX and CycloneDX SBOMs | Supply chain | PASS |
| AC-4 | One frozen Grype database scan set | Supply chain | PASS, builder/final zero Critical and zero High |
| AC-4 | Source labels and input provenance | Supply chain | PASS |
| AC-5 | Disposable cleanup and production preservation | Manual/Integration | PASS |

The credential-safe environment-name allowlist was `DATABASE_URL`, `LITELLM_MASTER_KEY`, `SYNTHETIC_UPSTREAM_AUTH`, `PROXY_BASE_URL`, and `LITELLM_LOCAL_MODEL_COST_MAP`. Values are omitted except reserved public base `https://candidate.invalid`. No production environment, config, credential or mount was read or attached

## Supply Chain

Checksum-pinned Syft 1.51.1 produced SPDX and CycloneDX SBOMs for exact base, uv, builder and final subjects. Grype 0.118.0 scanned all four documents with frozen DB schema 6.1.9, built `2026-09-03T06:30:55Z`

```text
subject   Critical  High  Medium  Low  Unknown
builder          0     0      11    1        4
final            0     0       9    1        2
base             0     0       1    0        0
uv               0     0       0    0        0
```

No ignore, VEX or path exclusion was used. The prior Tornado High is absent, and both retained release subjects satisfy the required zero Critical/zero High policy. `artifacts/reopen6/SHA256SUMS` covers all exact SBOM, scan, identity and provenance artifacts. The immutable Wolfi and uv inputs are unchanged from Reopen 4; their retained publisher/SLSA evidence is copied into the Reopen 6 provenance directory. Candidate signing, publication and deployment were explicitly out of scope and were not attempted

## Cleanup And Preservation

All task-labelled containers, networks, volumes, temporary test images, builder/cache, detached worktree, downloaded scanner tools/database and synthetic credentials were destroyed. Post-cleanup counts are zero task containers, zero task networks, zero task volumes, zero task builders and zero task worktrees. Only the exact retained builder and final images plus durable evidence remain

Production was observed only through the approved allowlisted commands. Before and after are identical: container `7bfb357accc8663e7229ecf8e2df471b9d656625106c216f48ca109de1eb2dba`, selector `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, image ID `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`, running/healthy, restart count 0 and OOM false

No signing, publication, deployment, Fedora action or NAS production mutation occurred
