# Public JSON contract fixed; final-image memory gate remains open

## Exact checkpoint and image

Committed and non-force pushed source `2c6af6ee3aeeaa349f2169e37bfb383d7131e2ba`. Built directly from its exact git archive using the unchanged Dockerfile, linux/amd64, with the full source revision label. Published candidate tag `task0905-json-2c6af6ee3aeeaa349f2169e37bfb383d7131e2ba`

Selected immutable reference:

`docker.staticduo.com/litellm@sha256:e340ea66f58af527dfe56d7b229cc913163639497e03b7d9db154413116894c1`

Registry push and image read-back agree. Applied only fedora-json-selector.patch, validated actual base Compose and recreated only litellm with --no-deps. Container `bf26a22b7a286d49ad1d6af70a6fb5a520fb42a1d5de50b4922ee191de2be042`, persistent memory.max=8589934592, memory.swap.max=0, restart=no. No rollback, NAS mutation, security change or maintenance-tool repair occurred

## Actual client contract verification

Used the deployed image's installed OpenAI SDK against its own HTTP proxy, with the existing administrator credential consumed only from process environment and never printed. Harmless Astra prompt and low reasoning were unchanged

| Actual SDK call | Result |
| --- | --- |
| responses.create, stream omitted | Response object, exact OK, usage.total_tokens=1639, 2.630s |
| responses.create, stream=false | Response object, exact OK, usage.total_tokens=1639, 1.731s |
| responses.create, stream=true | Exact OK deltas and response.completed event |
| chat.completions.create, stream=false | Exact OK |
| chat.completions.create, stream=true | Exact OK |

Ten additional identical direct HTTP /v1/responses stream=false calls all returned HTTP 200, application/json and object=response. A later ten-call JSON repeat also passed. This closes the earlier SSE-for-false defect rather than merely reporting HTTP 200

Final-image real LazyMCP mcp_call/defend_memory-find: HTTP 200, 0.948s, no JSON-RPC error, isError=false. Standard MCP defend_memory-memory_whoami: HTTP 200, 31.073s, no JSON-RPC error, isError=false. Response contents were discarded. Sol and Luna Chat calls returned exact OK. Health readiness/liveliness, authenticated model listing (29 aliases), protected-resource discovery and authorization-server discovery all returned 200

## Automated/direct verification

335 focused isolated tests passed with no skips. Includes the entire HTTP-handler file plus prior ChatGPT, parameter-extraction, Responses body/utils and Responses MCP coverage. Seven existing deprecation warnings and baseline mocked Anthropic background-logger diagnostics remain disclosed. Direct Ruff and formatting passed; StaticEng validation passed without warnings

The previous nine unavailable-provider integration cases remain external coverage limitations, not newly introduced product regressions. No claim of an all-repository test pass is made

## Final-image resource observation

First fresh window: **900.37 seconds, 91 readiness samples, zero failures**, sampled peak 1166143488 bytes. Current memory increased from 933519360 to 1166143488, with anon from 849772544 to 1078456320. No cgroup max/oom/oom_kill events

Extended window after ten successful JSON requests: **927.74 seconds, 31 readiness samples, zero failures**, sampled peak 1428725760 bytes. After the ten calls at elapsed 27.58s, current memory was 1209659392; it continued rising under background traffic to 1428725760 at elapsed 927.74s. Anon rose from 1120739328 to 1338494976 during that interval. No cgroup max/oom/oom_kill events

A later no-operator/repeat/recovery observation still rose:

```text
elapsed_s    current_bytes   anon_bytes
0.00         1479864320      1392005120
30.00        1482838016      1393532928
60.00        1488805888      1400078336
90.00        1492979712      1404026880
             ten identical JSON calls passed
142.60       1507344384      1419264000
172.60       1515913216      1427673088
202.60       1525006336      1436696576
232.60       1525379072      1437089792
262.60       1541648384      1452113920
292.60       1541550080      1453559808
322.60       1555324928      1466208256
```

The older bc9a9123 mature-runtime plateau in log 16 is valid for that observation, but cannot establish stabilization of this exact final image. The final image has not repeated the catastrophic synchronous allocation burst, yet its longer upward trend means a final stability approval would be premature. Read-only samples do not establish whether this is delayed collection, a larger warmup high-water mark, or sustained retention under other incoming traffic

## Bounded existing diagnostics

Memory summary showed only 14 cache entries (3 user/API-key, 10 router, 1 usage), so growing entry count was not demonstrated. Two existing memory/details requests returned count-only diagnostics (one measured 0.748s, each had a five-second client deadline). That existing endpoint walks tracked objects; no heap dump, payload capture, new instrumentation or live code injection was performed

GC was enabled with thresholds 2000/10/10, generation-2 collection count 9, zero reported uncollectable objects. Tracked-object counts were 2491530 then 2499527; getset_descriptor count remained 197876. These snapshots are insufficient to identify an allocating caller or prove absence of a leak. No speculative GC threshold change was made

The existing Luna temperature=0/active-reasoning errors remain client-input policy rejections. No broad model/default/drop_params change was applied. Successful low-reasoning calls without incompatible temperature continue to work

## Decision and NAS handoff

**Fedora API functionality PASS; promotion readiness HOLD on final-image memory stabilization.** Leave the corrected contained image running. The task remains active; do not weaken this into an all-gates release PASS

Conditional NAS compatibility/deployment handoff, not execution authorization:

1. Reuse the exact e340ea66 digest, not a rebuild or mutable tag. The image is linux/amd64; verify NAS architecture before use
2. This task changes no migrations, schema, dependency lock, database contract or credential format. Verify NAS's current schema/image baseline and protected backup before promotion; historical Fedora migration evidence is not a fresh NAS verification
3. Preserve NAS's own environment, database, Redis, model aliases, auth profiles and mounts. Do not copy Fedora credentials or catalog state
4. Confirm the actual NAS Compose path and persist candidate-only memory/no-swap limits there before recreating only litellm with --no-deps. Do not rely on an optional unused override
5. Verify readiness, NAS baseline model inventory, real SDK Responses JSON/stream, Chat, MCP/LazyMCP read-only calls and resource behavior on that exact digest
6. PMA must first resolve the Fedora memory gate and authorize the NAS step. No NAS host, service, database or configuration was accessed or changed in this continuation
