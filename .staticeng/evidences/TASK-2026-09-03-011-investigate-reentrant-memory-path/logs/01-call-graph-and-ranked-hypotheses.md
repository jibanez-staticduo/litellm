# Reentrant Memory Path Investigation

## Scope And Confidence

This is a source and existing-evidence investigation only. It made no production request, read no secret value, changed no source or runtime configuration, accessed no production datastore content, and performed no deployment

The source proves one intentional reentry from Defend memory into the same Fedora LiteLLM process for embedding and reranking. It does not prove an unbounded recursive cycle by itself. The strongest remaining explanation for approximately 100 GiB anonymous RSS is request multiplication caused by candidate-specific model routing or callback/cache feedback on that reentrant edge, with deterministic-memory fan-out and in-process buffering acting as amplifiers

## Frozen Incident Facts

- Candidate source was `bf58974a935521fa570fa7e280c51a00b2e5b54e`; rollback source was `64a3b83bf0bdd8813890d20ba7b6b57fc034bb95`
- Existing kernel evidence records the candidate LiteLLM process at `105,143,272 KiB` anonymous RSS and `105,946,196 KiB` virtual memory at `2026-09-03T21:49:23Z`, followed by Docker exit 137 and restart
- Defend MCP, gateway, PostgreSQL, Qdrant, and Neo4j remained running without restart or OOM, and gateway health remained 200 through the kill
- Candidate startup later remained bounded at `33,992,704` to `1,482,137,600` bytes across 112 one-second samples when no real tool request was sent
- The exact rollback image completed a real `defend_memory-find` with HTTP 200, JSON-RPC result present, and `isError=false`
- Candidate and rollback used the same protected runtime configuration shape, model/fallback/MCP projections, data services, and Defend deployment; the selector image was the only normalized Compose delta

These facts strongly tie the expansion to candidate request-path behavior triggered after the real memory call, but they do not identify the nested route, callback, or allocation stack

## Complete Call Graph

### 1. Public LazyMCP admission and ASGI bridge

```text
authorized client
  -> POST /toolset/defend_memory/lazymcp
  -> litellm/proxy/lazymcp_routes.py:toolset_lazymcp_route
  -> _mcp_active_toolset_name ContextVar
  -> _forward_lazymcp
  -> proxy_server._stream_mcp_asgi_response
     -> handler task
     -> response-start future
     -> body queue, max 1024 chunks
  -> handle_streamable_http_lazymcp
  -> internal path rewrite to /mcp
  -> auth and exact-resource admission
  -> lazy_session_manager.handle_request
```

`_stream_mcp_asgi_response` bounds queue item count but not aggregate bytes. Its `body_iter` cancels and awaits the handler when the downstream consumer closes. This bridge is not new in principle: the rollback source already used the same 1024-item queue and cancellation structure, while the candidate moved public LazyMCP routing into a dedicated lazy-loaded router and added exact public-resource context handling

### 2. LazyMCP gateway tool resolution

```text
MCP JSON-RPC tools/call name=mcp_call
  -> lazymcp_tool_call
  -> _lazymcp_call
     -> get admission/auth context
     -> resolve allowed Defend server
     -> _get_lazymcp_server_tools
        -> open temporary MCP client/session
        -> initialize
        -> tools/list
     -> resolve defend_memory-find in the already filtered tool set
     -> call_mcp_tool
```

One outer `mcp_call` performs a tool-list round trip before the actual call. This is bounded serial setup, not recursive dispatch

### 3. LiteLLM managed MCP execution

```text
call_mcp_tool
  -> execute_mcp_tool
     -> permission and parameter checks
     -> pre_mcp_call guardrails
     -> _handle_managed_mcp_tool
  -> MCPServerManager.call_tool
     -> during_mcp_call guardrail task when guardrails exist
     -> _call_regular_mcp_tool
        -> create MCPClient
        -> create one upstream tool-call task
        -> asyncio.wait_for(asyncio.gather(during-hook?, tool-call), 60s)
        -> MCPClient.run_with_session
           -> new httpx AsyncClient
           -> streamable HTTP transport
           -> ClientSession.initialize
           -> ClientSession.call_tool
           -> close session, transport, and AsyncClient in finally paths
     -> post_mcp_call guardrails and standard logging
```

The live Defend registration has auth type `none`, no row-specific timeout, and no row-specific concurrency limit. Therefore the OBO one-retry branch does not apply, the effective timeout is 60 seconds, and server-call concurrency is unlimited at the registration layer even though the diagnostic client is constrained to one call

### 4. Defend memory deterministic find

The deployed Defend MCP lineage includes the deterministic direct path present in release commit `11c4f510c9f95584b77863e6b037307d741717ab`. A request with `strategy=deterministic` does not call the memory-agent gateway. It executes `_find_compact_impl` inside `defend-memory-mcp`

```text
defend_memory-find strategy=deterministic
  -> memory_rerank.app.find
  -> _find_compact_impl
     -> concurrently schedule Qdrant and Neo4j initial lanes for backend=all
        -> Qdrant lane
           -> _semantic_candidates
           -> _embed_query
           -> POST Fedora LiteLLM /v1/embeddings
              model=qwen3-embedding-8b
           -> Qdrant query without vectors in response
           -> rerank up to 12 clipped documents
           -> POST Fedora LiteLLM /rerank
              model=qwen3-reranker-4b
        -> Neo4j lane
           -> bounded lexical candidate query in a worker thread
           -> rerank up to 60 clipped documents
           -> POST Fedora LiteLLM /rerank
              model=qwen3-reranker-4b
     -> bounded identifier enrichment from Qdrant/PostgreSQL/Neo4j
     -> global rerank of up to 60 clipped bundle documents
     -> POST Fedora LiteLLM /rerank
        model=qwen3-reranker-4b
     -> compact-v2 response
     -> best-effort retrieval telemetry
```

Important source findings:

- `graph_top_k=0` suppresses returned graph seeds but does not suppress the Neo4j lane or its rerank because `_find_compact_impl` schedules Neo4j whenever `backend` is `all` or `neo4j`
- Default and false-valued filter fields remain in `active_filters`, so the Qdrant semantic limit takes the filtered branch `max(candidate_k * 4, 80)`; the diagnostic's `candidate_k=5` can therefore fetch up to 80 semantic candidates
- Documents sent to rerank are clipped to 1,200 characters; Qdrant vectors are not returned; public compact output is bounded to `top_k`
- A low-result Qdrant path can fall back to scrolling memory collections, which can make the Defend process retain more payload data, but incident evidence shows the candidate LiteLLM process, not Defend, was the approximately 100 GiB process
- The direct deterministic path contains no call back to LazyMCP and no call to `/v1/find`; only `strategy=agentic` delegates to the memory-agent gateway

### 5. Fedora LiteLLM model reentry

```text
Defend HTTP client
  -> Fedora LiteLLM /v1/embeddings or /rerank
  -> normal virtual-key admission and request preprocessing
  -> route_request
  -> Router.aembedding or Router.arerank
  -> selected provider deployment
  -> provider HTTP client
  -> external embedding/rerank inference authority
  -> response transform
  -> logging/callback/cache handling
  -> Defend memory
```

This is reentry because the outer LazyMCP request remains live in Fedora LiteLLM while Fedora LiteLLM services nested model requests from Defend. It becomes recursion only if the selected nested deployment, a semantic-cache embedding lookup, a guardrail/callback, or a retry/fallback sends another request back to the same Fedora LiteLLM route without a decreasing budget

## Candidate Versus Rollback Boundaries

| Boundary | Rollback control | Candidate delta and implication |
| --- | --- | --- |
| Public LazyMCP route | Direct proxy-root route called the same ASGI bridge and LazyMCP handler | Dedicated lazy-loaded route preserves `_original_path` and toolset name; no loop is visible in this wrapper |
| ASGI response bridge | Same 1024-item queue and handler-task cancellation structure | No material candidate-only buffering delta found |
| LazyMCP call and MCP client | Same list-before-call, temporary streamable session, 60-second call budget, and close paths | Candidate adds broad MCP auth/discovery/guardrail work but no unconditional tool retry for auth type `none` |
| Defend memory service | Same independently deployed service and deterministic callback topology | Existing rollback real call succeeds, so Defend code and data are controls rather than candidate-only subjects |
| Model routing | Rollback 1.98 request path succeeds with the same public aliases | Candidate integrates broad Router, registry read-through, fallback, provider, HTTP, cache, and logging changes; this is the widest behaviorally relevant source delta |
| Semantic cache | Older behavior depended on prior source | Candidate adds a five-second, zero-retry semantic-cache embedding deadline and `cache={no-cache,no-store}` on its internal embedding call, which is safer against direct cache recursion |
| Async cache writes | Bare background tasks did not retain a process-global strong-reference set | Candidate retains cache-write tasks in `_PENDING_CACHE_WRITES` until completion and retries a cancelled write once during event-loop shutdown; this can amplify a recursive request storm but one bounded response cannot explain 100 GiB |
| Hosted vLLM embedding/rerank transforms | Existing provider paths | Relevant candidate changes are typing or request metadata only; normal response sizes are tens of KiB or less for one embedding and a small score list |

Existing release evidence proves model names, fallback projections, and config shape equality, but it does not prove that candidate and rollback selected the same deployment ID or normalized upstream authority for each nested embedding/rerank request. That is the highest-value missing comparison

## Ranked Hypotheses

| Rank | Hypothesis | Confidence | Evidence and disposition |
| --- | --- | --- | --- |
| 1 | Recursive model-route or callback/cache feedback on LiteLLM reentry | Medium-high | Best fit for rapid process-local growth to about 100 GiB while Defend and datastores remain healthy. The source proves the reentrant edge but not the cycle. Candidate-only Router/registry/cache/callback behavior and rollback success make nested route selection the first boundary to measure |
| 2 | Deterministic-memory fan-out amplifies a recursive edge | High as amplifier, low as sole cause | One nominal call can produce one embedding plus up to three reranks, with Qdrant and Neo4j reranks concurrent. `graph_top_k=0` does not disable Neo4j and `candidate_k=5` can still fetch 80 candidates. These bounded calls cannot alone allocate 100 GiB in LiteLLM, but each recursive generation multiplies them |
| 3 | Request/result buffering and payload copies amplify request multiplication | Medium as amplifier, low as sole cause | The path holds decoded request data, logging metadata, model responses, MCP SDK results, post-call guardrail views, and an ASGI queue. The queue is count-bounded but not byte-bounded. Source-side candidate and document caps make a single nominal response far too small; repeated nested requests could retain many copies |
| 4 | Transport/session cancellation leak leaves nested work alive | Low-medium | `wait_for(gather(...), 60s)` cancels children, `MCPClient` closes session/transport/httpx client in finally paths, and the ASGI body iterator cancels and awaits its handler. The test suite lacks a real streamable-transport regression proving accepted upstream work and all nested model calls drain after timeout or client disconnect |
| 5 | Retry/fallback multiplication | Low-medium as amplifier, very low as sole cause | Diagnostic client retries are disabled, httpx makes no application retry here, Defend calls once per phase, and auth type `none` bypasses the MCP OBO retry. Candidate semantic-cache embeddings explicitly use `num_retries=0`. Router deployment retries/fallbacks remain a candidate-only multiplier to count, not an explanation without repeated failures |
| 6 | One malformed response or allocator bug requests approximately 100 GiB directly | Low | Embedding output is one vector, rerank output is a bounded score list, documents are clipped, and MCP output is compact. No source computes an allocation near host memory size. Keep this hypothesis only until route counters prove there was no request multiplication; allocator stack sampling would then become decisive |

## Bounded Maintenance Instrumentation

The existing TASK-007 watchdog remains mandatory and must be armed before candidate deployment. Add only the following secret-free observations to its one-call run

### Ingress and phase counters

Record one-second counts and latency/status classes, never bodies or headers, for these Fedora LiteLLM route classes

```text
/toolset/*/lazymcp
/v1/embeddings and /embeddings
/rerank, /v1/rerank and /v2/rerank
/health/liveliness and /health/readiness
```

The expected envelope for the exact diagnostic is one outer LazyMCP call, no nested LazyMCP request, at most one nested embedding request, and at most three nested rerank requests. More than one embedding, more than three reranks, any nested LazyMCP request, or continued route arrivals after the client has settled is direct evidence of multiplication and triggers immediate rollback

### Selected-route and egress topology

For each nested model request retain only:

```text
route class
requested alias
selected deployment-id digest prefix
selected provider class
attempt ordinal
fallback count
normalized upstream authority equality booleans
```

The normalized authority evidence must record only booleans or non-reversible digests for comparison among candidate proxy authority, rollback-selected authority, and expected inference authority. It must not retain URL paths, query strings, userinfo, headers, credentials, or raw configuration

If an already-installed kernel/BPF tool is available, collect a fixed 90-second, PID/cgroup-filtered `tcp connect` and `inet socket state` count keyed only by process name, destination address/port digest, and state. Do not install a tracer, capture packets, resolve payloads, or retain raw endpoint URLs. This distinguishes repeated self-connects from a single external model call without exposing traffic

### Process and task cardinality

Continue TASK-007's cgroup and `/proc` sampling and add these bounded deltas relative to the final pre-call baseline

```text
asyncio task count by coroutine name
executor thread count
open sockets by state
MCP ClientSession and httpx task-name counts where visible
pending cache-write task count
GC generation counts
```

Use existing `/debug/asyncio-tasks` and `/debug/memory/summary` only. Do not invoke the perturbing full object walk. If an already-installed Python stack sampler can attach without locals, capture at most three two-second stack-only samples at baseline, first 512 MiB growth, and immediately before rollback. Do not install tooling or capture locals, arguments, environment, or heap content

### Phase correlation

The memory service does not propagate the outer trace header to its nested LiteLLM HTTP calls. Correlate by monotonic windows and route counts instead of adding a production header during this retry

```text
P0 outer LazyMCP accepted
P1 Defend tools/list completed
P2 Defend find accepted
P3 first nested embedding accepted/completed
P4 each nested rerank accepted/completed
P5 MCP result serialization began/completed
P6 client settled, then 15-second drain
```

At P6 require nested route counts, task counts, sockets, threads, file descriptors, and RSS growth to stop and return toward baseline. A 60-second MCP timeout or 75-second client timeout is not proof of cancellation

## Isolated Confirmation Tests

Before building any corrected image, add a production-equivalent isolated regression around the exact topology with test-owned services and no production data

1. A stub Defend MCP executes deterministic find and calls the candidate's embedding route once plus rerank three times with small fixed responses; assert route cardinality, no LazyMCP recursion, one outer result, all tasks drained, and bounded RSS across repeated serial calls
2. Cancel the client before the nested model call completes; assert the MCP handler, gather children, MCP ClientSession, httpx client, sockets, and nested provider work all terminate within a fixed drain budget
3. Configure a nested embedding or rerank deployment to point deliberately back to the same proxy authority; assert the request fails closed before a second same-route hop rather than recursing
4. Enable each supported cache mode in turn; assert internal semantic-cache embeddings carry `no-cache`, cache-write task count returns to zero, and cancellation cannot retain response/request graphs
5. Run the actual Defend deterministic implementation with `top_k=1`, `candidate_k=5`, and `graph_top_k=0`; assert the documented current route counts, then separately test any fan-out reduction before treating it as a fix

RSS assertions should use a warm baseline, fixed serial iteration count, and a small slope/peak budget rather than an exact byte total. Tests must fail before the identified correction and must not accept a timeout as success

## Minimal Correction Decision

Do not change timeouts, add retries, increase RAM/swap, or qualify the candidate from an unexplained successful retry

- If counters show the selected embedding/rerank deployment targets Fedora LiteLLM itself, correct only that model deployment's normalized upstream destination or candidate Router selection, then add a self-target fail-closed regression and rebuild only if source changes
- If a callback or semantic-cache lookup creates the second same-route hop, propagate a request-scoped internal reentry budget and reject a non-decreasing second hop; preserve the existing semantic-cache `no-cache`, zero-retry, and five-second bounds
- If counts are nominal but MCP work survives cancellation, replace implicit gather cancellation with explicit cancel-and-await cleanup around the tool and during-hook tasks, then prove transport/session/socket drain under a real streamable HTTP test
- If counts are nominal and growth begins only after the result returns, add a byte budget to the ASGI bridge and MCP result/logging path, avoid retaining duplicate raw/translated results, and test client disconnect during a maximum allowed result
- Independently, in the agent-memory repository, make `graph_top_k=0` skip the Neo4j initial lane and its rerank when the contract permits, and make `candidate_k=5` remain an actual retrieval bound. This reduces amplification but is not sufficient evidence of the 100 GiB root cause
- Add a separately governed cgroup memory ceiling before any future candidate exposure. A ceiling protects Fedora but does not repair or qualify the source defect

The smallest next action is the already authorized one-call retry with route-cardinality and egress-authority instrumentation added to TASK-007. Roll back at the first repeated nested route or existing resource threshold. Do not attempt a second request in the same window

## Source And Evidence Index

- `.staticeng/evidences/TASK-2026-09-03-007-plan-fedora-live-diagnostics/logs/00-read-only-findings.md`
- `.staticeng/evidences/TASK-2026-09-03-007-plan-fedora-live-diagnostics/logs/01-fedora-live-diagnostic-runbook.md`
- `.staticeng/evidences/TASK-2026-09-03-006-diagnose-fedora-candidate-live/logs/01-execution-result.md`
- `.staticeng/evidences/TASK-2026-09-01-012-release-upstream-main-fedora/SUMMARY.md`
- `litellm/proxy/lazymcp_routes.py:12` and `litellm/proxy/lazymcp_routes.py:53`
- `litellm/proxy/proxy_server.py:18033`
- `litellm/proxy/_experimental/mcp_server/server.py:3130`, `litellm/proxy/_experimental/mcp_server/server.py:3551`, `litellm/proxy/_experimental/mcp_server/server.py:4224`, and `litellm/proxy/_experimental/mcp_server/server.py:5591`
- `litellm/proxy/_experimental/mcp_server/mcp_server_manager.py:5166` and `litellm/proxy/_experimental/mcp_server/mcp_server_manager.py:5616`
- `litellm/experimental_mcp_client/client.py:408`, `litellm/experimental_mcp_client/client.py:466`, and `litellm/experimental_mcp_client/client.py:656`
- `litellm/proxy/route_llm_request.py:423`, `litellm/proxy/rerank_endpoints/endpoints.py:36`, and `litellm/proxy/proxy_server.py:10792`
- `litellm/caching/_embedding_router.py:41` and `litellm/caching/caching_handler.py:128`
- `/home/staticduo/git/agent-memory-platform/apps/memory-rerank-mcp/memory_rerank/app.py:1114`, `/home/staticduo/git/agent-memory-platform/apps/memory-rerank-mcp/memory_rerank/app.py:1126`, `/home/staticduo/git/agent-memory-platform/apps/memory-rerank-mcp/memory_rerank/app.py:1795`, `/home/staticduo/git/agent-memory-platform/apps/memory-rerank-mcp/memory_rerank/app.py:2047`, and `/home/staticduo/git/agent-memory-platform/apps/memory-rerank-mcp/memory_rerank/app.py:2372`
- `/home/staticduo/git/agent-memory-platform/apps/memory-rerank-mcp/memory_rerank/bundles.py:96` and `/home/staticduo/git/agent-memory-platform/apps/memory-rerank-mcp/memory_rerank/bundles.py:180`
- `/home/staticduo/git/agent-memory-platform/.staticeng/evidences/TASK-2026-07-16-deploy-memory-hints-three-hosts/SUMMARY.md`
