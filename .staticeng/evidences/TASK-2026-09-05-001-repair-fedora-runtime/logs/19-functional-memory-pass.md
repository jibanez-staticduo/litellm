# Fedora functional/memory PASS and exact NAS promotion handoff

## Decision

Tech Lead approves the bounded functional and memory gate for **source 7a9ef0335303d973f3a228dcf7baadff18c82fb5** and authorizes PMA's NAS promotion of exactly:

`docker.staticduo.com/litellm@sha256:7b2368711ff10db3107772d627e03aa89319598f8897ff7431497775926b2eb9`

This approval supersedes the preceding Fedora memory holds for earlier images. It is not a claim of indefinite stability, all-provider credential coverage, clean client-error logs, or a newly completed security/supply-chain audit. No NAS action occurred in this continuation

## Exact source/build/deployment

- Source checkpoint 7a9ef0335303d973f3a228dcf7baadff18c82fb5 committed and non-force pushed to origin/main
- Unchanged repository Dockerfile built on Fedora directly from that exact git archive; no dirty working-tree contents entered the build
- Registry tag task0905-retention-7a9ef0335303d973f3a228dcf7baadff18c82fb5 published successfully; registry digest, local image identity and full revision label agree
- Platform linux/amd64
- Fedora selector changed only by fedora-retention-selector.patch; actual base Compose validated and only litellm recreated with --no-deps
- Running container 164bab0c75f9294a3a7977420c2fda7686acb7a7bc5317af2d0768021b721264
- Persistent memory.max=8589934592, memory.swap.max=0, restart=no; final running/healthy, restart count 0, OOMKilled=false
- No rollback, dependency recreation, security-policy change or maintenance-tool repair

## Actual root cause and correction

Two distinct memory defects were addressed in this task. Full GenericLiteLLMParams serialization during session lookup caused the original explosive native Pydantic allocation. Later, four retry breadcrumbs retained live Logging objects, which owned exception tracebacks and completed Request bodies and could refer back to older history snapshots. The exact long-lived root was captured in log 18

The final source change adds only litellm_logging_obj to the existing retry-breadcrumb exclusion set. It preserves model, exception type/string and metadata diagnostics and does not change retries or error policy. Weak-reference regressions for 25 failed request graphs in both metadata forms fail before the change and pass after it, even when collection is requested to distinguish reachable roots from ordinary temporary cycles

A post-fix ownership diagnostic found 28 Request objects with 3587460 body bytes, rather than the earlier 1373/171099265 snapshot. Breadcrumb logging-owner count was zero; logging queue/running count and spend queue were zero. A single explicit diagnostic GC reduced that later count from 28 to 20. This was not treated as a stability PASS; all final equivalent/drain windows below ran without forced collection or cache clearing

## Verification

- 337 focused isolated tests passed, no skips; existing log_retry test separately passed
- Direct source/test Ruff, test formatting and StaticEng validation passed
- Actual deployed OpenAI SDK: Responses omitted/false stream returns Response objects with exact OK and usage; true Responses stream emits OK and response.completed; Chat false/true returns exact OK
- Sol and Luna real Chat calls returned 200 and exact OK with supported parameters
- Real LazyMCP mcp_call/defend_memory-find: HTTP 200, 0.593s, no RPC error, isError=false
- Real standard MCP defend_memory-memory_whoami: HTTP 200, 31.105s, no RPC error, isError=false
- Readiness/liveliness, authenticated model inventory (29 aliases), protected-resource discovery and authorization-server discovery returned 200

Nine equivalent five-minute windows each sent ten successful Astra JSON Responses requests and ten deliberately invalid Luna requests with a 64-KiB synthetic body, temperature=0 and active reasoning. All 90 positive requests returned 200; all 90 negative cases returned the intended 400. No model policy was loosened. Operator traffic stopped between each batch, leaving natural drain time well beyond the logging worker's 20-second coroutine deadline and spend monitor's maximum 30-second polling backoff. No cache TTL was shortened or cache forcibly cleared; ordinary background clients remained active

Windows 1-3 request-log counts were truncated by the initial 5000-line cap and are lower bounds only. Later windows streamed and counted the complete time-bounded log output without retaining raw payloads

## Separating retained allocations from RSS high-water behavior

Initial RSS still increased after the root correction, so an isolated one-frame tracemalloc interval was used rather than assuming either leak or stability. Three further equivalent windows each sent ten successful JSON calls and ten intended rejections, followed by natural drain. These are another 30 positive and 30 negative calls, all with the expected status

| Traced window | Complete Chat/Responses requests | Live traced bytes | Tracer bookkeeping bytes |
| --- | ---: | ---: | ---: |
| 1 | 230 | 257980348 | 74358352 |
| 2 | 199 | 174685261 | 45187184 |
| 3 | 235 | 190802002 | 14672400 |

With another 434 requests after the first sample, live traced allocations ended **67178346 bytes lower**, not cumulatively higher. Request decoding, outbound JSON and Pydantic allocations varied with live work, while their live total did not grow proportionally to completed requests. Tracer bookkeeping was reported separately. Tracing was stopped and diagnostic variables removed before final drain; no forced GC occurred during these three traced windows or the final drain

## Final uninstrumented natural drain/soak

No operator model or MCP calls were made during this final **900.75-second** period. Only bounded readiness/resource sampling and time-bounded access-log counting continued. Background clients made **538 Chat/Responses requests**

| Window | Background requests | Python RSS start -> end | RSS delta | Cgroup anon start -> end |
| --- | ---: | --- | ---: | --- |
| 1 | 208 | 1856430080 -> 1876062208 | 19632128 | 1860997120 -> 1882681344 |
| 2 | 172 | 1876062208 -> 1884372992 | 8310784 | 1882681344 -> 1891823616 |
| 3 | 158 | 1884372992 -> 1884377088 | 4096 | 1891823616 -> 1892466688 |

The late Python RSS slope is **819.2 bytes/minute** despite 158 more requests, rather than the previous sustained multi-MB/minute trend. Cgroup anon changed by 643072 bytes in that same last window; it includes other container processes as well as Python. File cache remained exactly 63623168 bytes throughout all three windows

Final cgroup current=1982148608, observed drain peak=1983602688 bytes. All **33/33** readiness samples passed. All memory.max/oom/oom_kill counters remained zero; limits were checked throughout. Final Python RSS=1884377088 bytes, RssAnon=1837342720. The resident high-water mark is not confused with live traced allocations or attributed to file cache

Together, the rooted-lifetime fix, deterministic release regression, non-cumulative live-heap samples and decreasing-to-flat uninstrumented RSS slopes establish no continuing request-proportional retention over these meaningful bounded repeated trials. This is sufficient for functional promotion, without asserting impossible indefinite stability

## Acceptance criteria

- AC-1 PASS: actual persistent Compose/cgroups/restart containment survived recreation
- AC-2 PASS: native allocator and later retained logging/request graph explicitly attributed; anonymous RSS distinguished from file cache, active workload, queues and temporary/cyclic allocation
- AC-3 PASS: minimal proven corrections, mapped regression tests and direct validation; no unrelated policy/harness change
- AC-4 PASS for the requested functional/memory gate: real SDK/models/MCP, repeated success/rejection trials, natural drain and final 900-second observation passed
- AC-5 PASS: exact identities, measurements, limitations and handoff recorded; technical CodeMaps updated. No new public feature documentation is required because repairs restore intended existing behavior

The historical broad suite's unavailable-provider cases remain disclosed. Existing incoming 429 and unknown-model 404 requests also remain visible in traffic counts; valid representative calls pass and the memory gate now tolerates rejected traffic without retaining completed requests. Neither those client/integration limitations nor the two out-of-scope maintenance findings were silently converted into successful tests

## NAS compatibility and deployment handoff

Technical authorization: promote **only the exact 7b236871 digest above**, using PMA's existing deployment path. No NAS action is authorized for or performed by this current step

1. Verify NAS is linux/amd64 and capture its current Compose/image/schema state through the existing process. Obtain the protected backup required by that process
2. This repair changes no schema, migrations, dependency lock or credential format. Confirm the NAS baseline against the already-approved integration/migration plan; do not infer current NAS state from Fedora
3. Preserve NAS-specific environment, database/Redis, aliases, auth-profile files and mounts. Do not copy Fedora credentials or model configuration
4. Persist the exact digest selector and suitable memory/no-swap containment in the actual NAS Compose recreation path. Recreate only litellm with --no-deps; do not mutate unrelated dependencies
5. Verify NAS baseline inventory, SDK Responses JSON/stream, Chat, read-only MCP/LazyMCP and a resource observation on the exact digest
6. Keep routine resource monitoring and the containment limit. A later workload-dependent regression should resume the original task with new evidence, not invalidate this bounded PASS retroactively

PMA owns final task closure and the NAS execution decision. Unrelated shared-worktree artifacts remain preserved and unstaged
