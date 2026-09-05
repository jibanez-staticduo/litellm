# Second corrected Fedora image: live results and remaining limits

## Exact source and deployment

Source `fb8943a9cc67573f34e0a56f6cb923f3a2dc845f`, non-force pushed to origin/main after the memory/profile checkpoint `8865c5d20c75552d7db3a79f888c2c79f42fc02f`. Built directly from exact `git archive` through the unchanged repository Dockerfile on Fedora, linux/amd64, with full source revision label. No uncommitted working-tree files entered the build

Published candidate `docker.staticduo.com/litellm:task0905-fb8943a9cc`, selected persistently as `docker.staticduo.com/litellm@sha256:bc9a9123b774f5e2c250d2a9d4b5441397571e54cf41fc64c1192021940d6042`. Registry push returned that digest and local image inspection agreed. The unique tag is publication convenience, not the deployment selector

Applied only `fedora-responses-selector.patch`, validated Compose, recreated only litellm with --no-deps. Container `20fa2788cf3d2a693f16d01f27c1153508dba5ecd7db5ef076af54fa827c021c`. Actual memory.max=8589934592, memory.swap.max=0, restart=no throughout observation. No rollback, NAS deployment, NAS service/configuration mutation, auth rotation or maintenance-tool repair occurred

## Real model matrix

All requests were sent through Fedora localhost:4000 with its existing administrator credential loaded only into process memory. Harmless prompt: `Reply with OK only`, low reasoning, no temperature override. Payloads were discarded; only status/timing/shape indicators were emitted

| Model | Route | Requested stream | HTTP | Time | Observed result |
| --- | --- | --- | --- | --- | --- |
| gpt-6-astra | /v1/chat/completions | false | 200 | 3.841s | JSON body with OK |
| gpt-6-astra | /v1/chat/completions | true | 200 | 1.902s | OK and DONE |
| gpt-6-astra | /v1/responses | false | 200 | 1.827s | SSE, OK and response.completed, not JSON |
| gpt-6-astra | /v1/responses | true | 200 | 1.786s | SSE, OK and response.completed |
| gpt-5.6-sol | /v1/chat/completions | false | 200 | 1.237s | JSON body with OK |
| gpt-5.6-luna | /v1/chat/completions | false | 200 | 5.190s | JSON body with OK |

The input-normalization correction fixes the observed `Input must be a list` rejection. A final post-observation stream=false request confirmed HTTP 200, `text/event-stream; charset=utf-8`, OK and response.completed

**Compatibility limitation:** stream=false Responses is not a JSON non-stream PASS. Existing sync and async tests in `tests/test_litellm/llms/custom_httpx/test_llm_http_handler.py` explicitly assert the provider-forced streaming behavior. The HTTP handler combines caller stream with provider stream at lines 2659/2853. No shared HTTP-handler behavior or those tests were changed. PMA must resolve whether to preserve this fork contract or authorize separation of upstream SSE from downstream JSON semantics

## Real MCP and LazyMCP

On the final image, LazyMCP mcp_describe for defend_memory returned 200 and exposed its actual tool schema. Aggregate LazyMCP mcp_call invoked `defend_memory-find` with a bounded deployment query, top_k=1, candidate_k=5 and graph_top_k=0: HTTP 200, 1.797s, no JSON-RPC error, isError=false, result_count=1, no result error. Returned private memory content was not printed or retained

Standard /mcp invocation of `defend_memory-health`: HTTP 200, 31.121s, no JSON-RPC error, isError=false, structured keys ok/config/backends. Internal health values were not retained, so no all-backend-health assertion is made from this probe

The preceding checkpoint also passed both transport initialize/list exchanges (147 ordinary tools and exactly three LazyMCP gateway tools). Final discovery endpoints `/.well-known/oauth-protected-resource/lazymcp` and `/.well-known/oauth-authorization-server` returned 200. Final unauthenticated LazyMCP POST returned 401 with Bearer challenge. DCR/token mutation and the full historical security/audience matrix were not rerun

## Final 900-second observation

91 samples over **900.36 seconds**, every readiness check 200 with zero failed samples. No memory.max, oom or oom_kill event. Effective limits checked at every sample. A 6-GiB stop threshold was present but never reached

```text
elapsed_s  memory_current_bytes
0.00       956403712
60.03      984981504
120.05     995491840
180.08     1007243264
240.10     1022148608
300.12     1038192640
360.15     1048985600
420.17     1063874560
480.20     1082785792
540.22     1098096640
600.24     1115152384
660.27     1124466688
720.29     1138237440
780.31     1155772416
840.33     1170583552
900.36     1187172352
```

Sampled peak 1187172352 bytes. The historical rapid multi-GiB Pydantic allocation/OOM did not recur across either corrected-image observation. Memory still rose gradually by 230768640 bytes in this final window under incoming traffic; this is not a flat-heap or indefinite-stability claim

Final read-back: running, healthy, restart count 0, OOMKilled=false, exact bc9a9123 digest, memory and memory-plus-swap 8589934592, restart=no. Final /health/readiness and /health/liveliness returned 200, authenticated /v1/models returned 200 with 29 aliases

## Existing traffic errors and remaining gate

Bounded stderr log inspection (last 3000 lines, 20 minutes) counted 342 UnsupportedParamsError markers, 55 `No deployments available` markers and 36 traceback headers. These are occurrences, not unique requests. No OutOfMemory marker appeared

Sanitized error samples identify incoming gpt-5.6-luna requests supplying temperature=0 with active reasoning, which the existing provider policy rejects unless reasoning_effort is none; supported temperature is 1. The live low-reasoning request without a temperature override succeeded. No unrequested drop_params policy, retry increase, model default or caller configuration change was applied. This error traffic prevents a clean-logs claim and needs PMA/caller configuration disposition

## Acceptance criteria and handoff

AC-1 PASS: persistent containment survived both actual recreations. AC-2 PASS for exact synchronous allocator attribution and disappearance of the rapid burst; live graph provenance remains unknown. AC-3 PASS for three minimal product corrections and 232 focused isolated tests, not a full-suite pass. AC-4 PARTIAL: real models, Responses SSE, actual read-only MCP/LazyMCP and the 900-second availability/OOM observation pass, but JSON non-stream semantics, gradual memory growth and rejected caller traffic remain limitations. AC-5 PASS for exact source/image, changed files and honest evidence

Leave Fedora running on the contained corrected digest, retain active task, and route the streaming-contract/caller-policy questions through PMA. Do not promote to NAS or claim full release closure from these results
