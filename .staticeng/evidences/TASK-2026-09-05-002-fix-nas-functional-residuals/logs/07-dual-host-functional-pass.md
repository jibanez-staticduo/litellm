# Dual-host functional and bounded resource verification

## Release order and identity

Fedora startup was corrected first without rollback or image substitution. It passed live inference/MCP tests and its complete 900.01-second observation before NAS selector or wrapper mutation. NAS then received that same immutable digest and its independently reviewed startup correction. Fedora was rechecked after NAS's complete 900.00-second observation

Both selectors: docker.staticduo.com/litellm@sha256:4800816a96e35e7e87549e23823b0627148b6dfe2ac3cb7b55dab345dede1258

Application source: 2dee9cd19e329d5c59eb712b8f27b8205ca0ff02

Linux/amd64 manifest: a56f0dc247ad96eb6d13eb6ae6f173d267fef42e3fe0d65390d069a46047f03d

Image config: 071b0d181864f9de5fb0a146a412d758d7dd7fd942953f263ab74c82b309aaba

Fedora container: cfe9b04c31a9f49ef88f2fc6ea4998822994bc34c3bad649ffd6e0bcd6d14683

NAS container: 5a2fbc88aa4b53d635a3f19c828a06fee799496fab0fdecbc6fea702ddc9ddac

Final inspection: both running/healthy, restart count=0, OOMKilled=false, memory=8589934592, memory+swap=8589934592, restart=no. Cgroup memory.swap.max=0 on both. NAS reports the config digest as .Image; Fedora reports the OCI index because of its different engine image store

## Actual final public requests

The verification client used each host's existing administrator credential only in process memory. Requests went through the actual public URLs, after earlier successful container-loopback runs. No raw credentials, headers, tool contents or private payloads were retained. Final model prompts carried fresh nonces to avoid accepting cached responses. Streaming checks required both exact OK text and stream completion

| Final public gate | NAS, https://litellm.staticduo.com | Fedora, https://litellm.defend.tech |
| --- | --- | --- |
| GET /health/readiness | 200, 0.026s | 200, 0.021s |
| POST /reload/model_cost_map | 200, 0.175s | 200, 0.108s |
| Astra catalog after reload | chatgpt/gpt-6-astra mode=responses | chatgpt/gpt-6-astra mode=responses |
| Astra Chat JSON | 200, exact OK, 2.794s | 200, exact OK, 2.952s |
| Astra Chat stream | 200, exact OK and stop, 2.484s | 200, exact OK and stop, 2.150s |
| Astra Responses JSON | 200, exact OK, 2.727s | 200, exact OK, 2.795s |
| Astra Responses stream | 200, exact OK and response.completed, 3.713s | 200, exact OK and response.completed, 3.310s |
| Unscoped /mcp initialize | 200, result, 10.083s | 200, result, 1.038s |
| Unscoped /mcp tools/list | 200, 487 tools, 40.172s | 200, 147 tools, 30.041s |
| Per-peer outcomes | 24 ok, 3 timeout | 11 ok, 1 timeout, 1 auth_required |
| Healthy real tools/call | memory-health, no RPC error/isError, 10.200s | memory_whoami, no RPC error/isError, 1.064s |

The standard NAS listing varied between 30.148 and 40.172 seconds across successful runs: the optional instruction scope may add its bounded ten-second probe before the per-peer thirty-second listing deadline. This is bounded partial availability, not a sub-thirty-second end-to-end latency promise. No registration was removed, disabled or represented as a successful empty server

On NAS the timeout outcomes name frigate_admin, frigate_observe and frigate_breakglass. Fresh container-side TCP connection attempts to their registered endpoints each failed after 3.002, 3.004 and 3.003 seconds respectively. These are real external reachability limitations; the LiteLLM aggregate now remains usable despite them. Fedora's timeout/auth-required outcomes are also retained truthfully, not represented as universal MCP availability

An early NAS verification-client attempt looked only for Fedora's memory_whoami tool and reported a selector failure after its inference and listing checks passed. NAS exposes the previously verified memory-health tool instead. Selecting that actual read-only NAS tool fixed the test assumption; subsequent loopback and public calls passed. Similarly, an initial inventory request mistakenly used the active health-check endpoint with a twenty-second deadline; inventory was subsequently verified through the non-probing /v1/mcp/server endpoint. Neither attempt is represented as a passing check

## Complete 900-second observations

| Measurement | Fedora | NAS |
| --- | ---: | ---: |
| Duration | 900.01s | 900.00s |
| Readiness samples passed | 31/31 | 31/31 |
| memory.current start | 963883008 | 1143181312 |
| memory.current end | 1107079168 | 1268129792 |
| Observed peak | 1107079168 | 1268129792 |
| Delta | +143196160 | +124948480 |
| Anon start | 894586880 | 1055924224 |
| Anon end | 1036455936 | 1193918464 |
| max/oom/oom_kill events | 0 throughout | 0 throughout |

Both windows sampled every thirty seconds with unchanged container identity and 8-GiB/no-swap containment. There was no forced GC, cache clearing or operator inference/MCP load during the passive observations; ordinary background clients continued. These are bounded readiness/resource passes, not proof of a memory plateau or indefinite absence of leaks. Full memory.current samples are in logs/08-resource-samples.csv

Final health checks after both public reruns returned readiness=200 and liveliness=200 on each host. Final memory.current was 1289379840 bytes on NAS and 1254625280 bytes on Fedora, with all recorded memory event counters still zero

## Log limitations, not hidden passes

Complete time-bounded Docker log streams since each current container started were counted without retaining raw lines. Both commands exited zero. NAS: 83266 lines, 1253 Traceback markers; Fedora: 109016 lines, 1255 Traceback markers. Both have zero MemoryError, P3009, P3018, migration-failed, no-deployments-available and unsupported-health-patch markers in that collection

NAS HTTP statuses included 200=456, 429=201 and 400=114. Fedora included 200=578, 429=1010 and 404=115. These counts include ordinary clients, not just this task's passing synthetic requests. RouterRateLimitError and classified MCP cancellation/list faults remain visible. No rate-limit policy was bypassed

NAS additionally emitted 812 RecursionError lines. Safe stack-only classification points to recursive spend_tracking_utils.py:_sanitize_request_body_for_spend_logs_payload/_sanitize_value, lines 821/784/786. This is an additional real logging-path finding. That source was not changed by this task; whether the release changed the triggering input mix is not established. No unrelated sanitizer repair is included and no error-free logging/all-traffic release claim is made

The baseline OAuth-discovery failure documented in log 04 also remains explicitly outside these scoped corrections. PMA should disposition the separate spend-logging finding and existing unavailable/auth-required peers without confusing them with the now-passing Astra and aggregate-availability acceptance criteria

## Acceptance criteria

AC-1: PASS for the requested routing correction. Actual Astra Chat and native Responses succeed after normal supported price-map reload, without quota/cooldown/fallback policy changes

AC-2: PASS for bounded aggregate partial availability. Healthy tools and real calls remain available; failed peers retain classified outcomes and registrations

AC-3: PASS with explicit external Frigate limitation. NAS live Astra and aggregate calls pass while all three Frigate TCP endpoints remain unreachable

AC-4: PASS for the requested Fedora-first, exact-digest, preserved-config and bounded resource sequence. Host-specific startup functionality was reviewed and retained; no automatic rollback or unrelated service mutation occurred

AC-5: PASS. Source, config snapshots, documentation, checksums, numbered results and truthful limitations are recorded. PMA retains final task closure

Final configuration validation: both shell snapshots pass sh -n and match the live wrapper SHA-256 values; protected configuration comparisons pass on both hosts; git diff --check passes; staticeng_validate passes with zero warnings. No new application source changes were made in this startup continuation, so its source-test evidence remains the 303 passing mapped tests for the exact built commit
