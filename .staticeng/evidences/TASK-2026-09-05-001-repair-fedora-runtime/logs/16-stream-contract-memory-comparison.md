# Stream contract correction and mature-runtime memory comparison

## Contract finding

The OpenAI Responses create reference (`https://platform.openai.com/docs/api-reference/responses/create`, checked 2026-09-05) says stream=true streams generated data using server-sent events. String input is equivalent to a user text input. The normal non-stream SDK call expects a Response object, not an SSE iterator. Context7 was unavailable, so the official reference was fetched directly

Pre-integration parent of 0573332425 already combined caller stream with transformed provider stream at both sync/async HTTP handler sites. Therefore the SSE-for-false behavior was not introduced by the memory/profile repair or the integration. It nevertheless violates the public client contract. The earlier tests conflated the upstream requirement with the downstream mode and did not establish a justified public exception

The minimal correction changes two expressions: ChatGPT's provider-required body stream remains true, but it no longer forces the public/HTTP-client streaming path when the caller omitted stream or set false. The existing non-stream HTTP read buffers the upstream SSE, and ChatGPT's existing transform_response_api_response parser aggregates it into ResponsesAPIResponse. Streaming requests, extra_body protection of upstream stream=true, other providers, hooks and normal response logging remain intact. No new aggregation framework or parser was added

Four new regressions drive the real ChatGPT transformation through sync and async handlers with omitted/false stream, asserting upstream body stream=true, buffered transport, Response type, output text, function-call ID, usage and non-stream logging. Before the correction all four failed; after it all four pass. Existing upstream-stream-protection tests now explicitly request public stream=true and preserve their assertions

The complete HTTP-handler test file initially had eight baseline failures from unconstrained Mock.finalize_request returning Mock rather than request_data, reproduced on detached unpatched 2b3123c667 (91 passed/8 failed). Added the missing identity-finalization behavior only to those product-test provider doubles. No production finalize logic or maintenance harness changed. The full focused matrix now passes **335 tests**, no skips, seven existing deprecation warnings. Existing mocked Anthropic logging cases also emit baseline background logger diagnostics; they are not new live failures

## Memory comparison on mature bc9a9123 image

The image was started at 2026-09-05T10:02:04.846201843Z and remained running/healthy roughly 2.5 hours later, with no restart or OOM. The same persistent 8-GiB/no-swap limit remained effective

Using numeric cgroup memory.current and memory.stat without heap dumps or injected instrumentation, measured 120 seconds without operator model calls, ten identical sequential real Astra Chat calls, then 120 seconds recovery. Every fixed call returned HTTP 200 and exact OK. Cgroup file memory remained 63389696 bytes throughout

```text
phase                   elapsed_s   current_bytes   anon_bytes
no operator calls       0.00        1331015680      1242427392
no operator calls       30.00       1333788672      1245659136
no operator calls       60.00       1333018624      1245687808
no operator calls       90.00       1333534720      1245687808
no operator calls       120.00      1333211136      1245704192
after fixed call 1      122.12      1333702656      1245704192
after fixed call 10     141.95      1333329920      1245704192
recovery                171.95      1334165504      1245724672
recovery                201.95      1334075392      1245724672
recovery                231.95      1333141504      1245724672
recovery                261.95      1332789248      1245724672
```

Fixed calls increased current memory by only 118784 bytes versus their pre-call sample, with anonymous memory unchanged. Recovery ended 421888 bytes below that pre-call current sample; anonymous memory was only 20480 bytes higher. There is no sustained per-call retention in this bounded repeat test. Compared with the earlier first-15-minute growth, the mature plateau supports warmup/high-water allocation rather than extrapolating a linear 231-MB-per-window leak

The environment was not globally idle: 34 Chat access entries occurred during the comparison, including ten operator calls. Zero Responses/LazyMCP access entries were counted. Other clients were not stopped or reconfigured. Thus the idle phase means no operator calls, with observed background traffic, not a fabricated traffic-free experiment

No cgroup max/oom/oom_kill events occurred. Existing debug endpoints reported 22 asyncio tasks in the preceding bounded read. No Luna parameter policy or routing defaults were changed; incompatible temperature=0 plus active reasoning remains caller error

## Next deployment gate

Checkpoint only this product correction, test coverage, technical invariant and same-task evidence. Build exact clean source with the existing Dockerfile, deploy Fedora contained without rollback, verify SDK/non-stream JSON and real streaming/MCP behavior, then repeat a 900-second observation. NAS remains untouched until the functional readiness handoff
