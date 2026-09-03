# Reopen 4 Verification Ledger

## Exact Subjects

```text
source commit: a826c38dc0737afd9eef00a2e9f50d2413ca92eb
source tree: fd4d309d5d323867361beb868ee9434cea5d40b4
Dockerfile SHA-256: 6add9603c86fd595c77b30b35ac3e0caacd9bb16828ac9b18ca189b538cae20b
pyproject.toml SHA-256: 6f7d344eb67fd50e4e95052821034bfb23bf13901ce26c81c97c2516efb81b92
uv.lock SHA-256: c623498311bb698c4c798879e22754c145767febf76383c12de6f75794ddfa5f
builder: sha256:5b7f6e5ef88d88b0db36473d75ec25b48512dbd4e26fe7484bd7775223aee6f6
final: sha256:eeb98cc84cd1f3b73ce1dc584ac9922e47515fc3db46beb8825283fddf6b2820
platform: linux/amd64
BuildKit: 0.13.1
```

The detached source worktree was clean. Builder and final were wholly new explicit target builds with `--pull=false`. Both carry the exact full revision, task and Reopen 4 labels. Python 3.13.15, uv/uvx 0.11.26, Rust 1.97.1, ml-dtypes 0.5.4, RedisVL 0.4.1, NumPy 2.4.4, uvloop 0.21.0, native bridge, Prisma and cache-removal checks passed

## Isolated Runtime

The credential-safe stack used uniquely labelled `task011r4-*` PostgreSQL 16, config, synthetic OpenAI-compatible provider and FastMCP objects. It attached no production network, volume, config, database, credential, mount or socket

- Empty database startup applied the full schema and exposed 78 public tables; authenticated readiness reported healthy/connected
- Restart retained the same exact container and image identities, healthy database, one-model inventory, MCP server, toolset and candidate-bound real tool execution
- Exact inventory contained only `synthetic-openai`
- Chat Completions non-stream and stream returned content and 40-token usage
- Responses non-stream and stream returned completed output and 30-token usage
- The independently authenticated synthetic upstream rejected the first intentionally malformed harness credential; after correcting the harness to provide the distinct key value, all provider calls passed. This proves the upstream credential was required and distinct from inbound LiteLLM credentials
- MCP REST exposed only permitted `add`; authorized execution returned 42 and the ungranted key returned HTTP 403 `access_denied`
- PostgreSQL recorded 15 successful spend rows across exercised calls

## Functional Blocker

All six required LazyMCP RFC 9728 discovery aliases returned HTTP 404 from the exact runtime, despite the installed module declaring all six routes. Aggregate, access-group and toolset LazyMCP transports therefore could not advertise resource metadata, issue their expected challenges or start DCR. The required DCR access/refresh/replay/audience, LazyMCP initialize/list/call, aggregate/scoped/toolset, reconnect and 360-discovery gates were stopped fail-closed rather than represented as passing

Source inspection identifies the likely routing conflict: `proxy_server.py` eagerly includes `mcp_discoverable_endpoints_router`, then calls `attach_lazy_features(app)`. The LazyMCP discovery warmup invokes `_include_discoverable_router`, which mutates the already-included router's route list but cannot reorder routes already copied into the FastAPI application. This is an implementation finding for Developer to reproduce and fix, not a QA source change

This is a candidate runtime regression, not a test-stack outage: liveness/readiness, models, Chat, Responses, MCP management, MCP REST, permissions, registered FastMCP listing/call and restart preservation passed against the same exact process

## Supply Chain

Checksum-verified Syft 1.51.1 emitted durable SPDX JSON and CycloneDX JSON for selected Wolfi base, uv input, exact builder and exact final. All four were scanned from those exact SBOMs with one frozen Grype 0.118.0 DB schema 6.1.9 built `2026-09-01T06:32:09Z`; database SHA-256 is recorded in `artifacts/reopen4/scans/grype-db.sha256`

```text
subject   Critical  High  fixable High  Medium  Low
builder          0     0             0       4    1
final            0     0             0       4    1
base             0     0             0       0    0
uv               0     0             0       0    0
```

The rejected Reopen 3 builder was rescanned with the same frozen DB and still reports exactly six fixable High matches: two setuptools 68.1.2 findings, two quinn-proto 0.11.14 matches and two rustls-webpki 0.103.10 matches. Reopen 4 removes all six without ignore, VEX or path exclusion

The exact uv OCI index and amd64 child identities match the reviewed pins; GitHub attestation verification returns SLSA provenance for the exact uv index subject. The exact Wolfi index and amd64 child match the reviewed pins, and its keyless Cosign signature verifies against the Chainguard workflow identity

The repository public key SHA-256 remains `ff8869bf14ba9d10af7b64b9d479543b44daec0165e715753c43ff8a998f6dd3`. No approved private key path, KMS URI, keyless OIDC token or frozen candidate signing workflow identity is present. Candidate builder/final signing and attestations remain independently blocked. Because functional qualification already failed, no unique quarantine publication was necessary and no registry tag or manifest was created

## Cleanup And Preservation

All disposable containers, network, PostgreSQL volume, Buildx builder/cache, detached worktree, config, provider/MCP fixtures, generated credentials and temporary logs were destroyed. Post-cleanup task-labelled container/network/volume/builder counts are zero. Only the two authorized immutable local images and durable repository evidence remain

Production was observed only through the two allowed credential-safe commands. Before and after observations are identical: container `7bfb357accc8663e7229ecf8e2df471b9d656625106c216f48ca109de1eb2dba`, selector `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, image ID `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`, running/healthy, restart count 0, OOM false

No mutable tag, quarantine publication, candidate signature, deployment, Fedora action or NAS production mutation occurred. `staticeng_validate` passes with zero warnings
