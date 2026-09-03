# Read-Only Findings

Captured on 2026-09-04 without source, host, configuration, database, container, registry, or deployment mutation

## Frozen Subjects

```text
candidate manifest: sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
candidate config: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
candidate source: bf58974a935521fa570fa7e280c51a00b2e5b54e
rollback manifest: sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
rollback config: sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42
rollback source: 64a3b83bf0bdd8813890d20ba7b6b57fc034bb95
```

## Prior Failure Timeline

```text
2026-09-03T21:38:38Z candidate container started
2026-09-03T21:39:30Z candidate identity and initial health recorded healthy
2026-09-03T21:43:41Z Chat, Responses, MCP REST, and MCP initialize recorded 200
2026-09-03T21:46:04Z discovery, challenge, DCR, authorized initialize, and audience gates completed
2026-09-03T21:49:23Z Fedora kernel global OOM killer selected candidate LiteLLM PID 1027522
2026-09-03T21:49:23Z killed process had total VM 105,946,196 KiB and anonymous RSS 105,143,272 KiB, about 100.3 GiB
2026-09-03T21:49:28Z Docker recorded candidate exit 137 and automatic restart count 1
2026-09-03T21:50:14Z exact prior-digest rollback began
2026-09-03T21:53:54Z rollback verification completed
```

The kernel reported no swap use at the kill. The candidate had no container memory limit and `memory.max=max`. The current rollback cgroup peaks near 1.5 GiB, which makes the candidate's 100.3 GiB RSS an abnormal process-specific expansion rather than ordinary baseline use

## Current Healthcheck And Runtime

```text
command: bash -c 'exec 3<>/dev/tcp/127.0.0.1/4000; printf "GET /health/readiness HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n" >&3; head -n 1 <&3 | grep -q "200"'
interval: 30 seconds
timeout: 5 seconds
retries: 3
start period: 20 seconds
restart policy: unless-stopped
memory limit: none
pids limit: none
nofile: 65535
```

`/health/liveliness` is an event-loop-only response. `/health/readiness` also checks the Prisma database path. Candidate source bounds each DB check at 2 seconds and the whole readiness DB path at 4 seconds. Three 5-second healthcheck failures can mark the service unhealthy, but the healthcheck cannot explain a 100.3 GiB candidate process

## Request And Dependency Topology

```text
authorized client
  -> Fedora LiteLLM /toolset/defend_memory/lazymcp
  -> LazyMCP mcp_call
  -> tool resolution/list on defend_memory
  -> HTTP MCP transport at defend-memory-mcp:8000/mcp
  -> deterministic memory find
     -> Fedora LiteLLM /v1/embeddings using qwen3-embedding-8b
     -> Qdrant semantic lookup
     -> Neo4j graph lookup
     -> PostgreSQL enrichment/telemetry where applicable
     -> Fedora LiteLLM /rerank using qwen3-reranker-4b
  -> result returns through MCP and LazyMCP
```

The LiteLLM MCP row is active as alias `defend_memory`, transport `http`, auth type `none`, with no row-specific timeout or concurrency limit. LiteLLM therefore uses `MCP_CLIENT_TIMEOUT=60.0` seconds and unlimited server-call concurrency. The diagnostic still fixes client concurrency at one

The Defend MCP uses a 180-second outer find budget. Its direct deterministic path has 25-second Qdrant/PostgreSQL/Neo4j component bounds, a 30-second embedding HTTP timeout, and a 60-second rerank HTTP timeout. Its current primary `find` delegates to the memory-agent gateway only when `strategy=agentic`; the reproduction pins `strategy=deterministic`

At read-only inspection time, LiteLLM, its PostgreSQL and Redis, Defend MCP, Defend gateway, Defend PostgreSQL, Qdrant, and Neo4j were running with zero restarts and no OOM flags. Defend gateway health returned 200 over the internal network. During the prior candidate window, gateway health remained 200 through `2026-09-03T21:49:23Z`, and bounded Defend service logs contained no timeout, cancellation, OOM, or error class

## Source Impact Surface

The allocating path may involve immediate siblings under these maintained modules if a correction is required:

```text
litellm/proxy/lazymcp_routes.py
litellm/proxy/_experimental/mcp_server/codemap.yml
litellm/proxy/_experimental/mcp_server/server.py
litellm/proxy/_experimental/mcp_server/mcp_server_manager.py
litellm/proxy/health_endpoints/codemap.yml
litellm/proxy/health_endpoints/_health_endpoints.py
litellm/proxy/db/codemap.yml
litellm/proxy/proxy_server.py
tests/test_litellm/proxy/_experimental/mcp_server/
tests/test_litellm/proxy/health_endpoints/
```

An upstream Defend correction belongs to `/home/staticduo/git/agent-memory-platform`, not this repository, and requires that repository's own task, source map, tests, image, and release flow
