# Actual NAS and final Fedora verification

## NAS SDK and inference

Actual OpenAI SDK through deployed NAS: Astra Responses omitted stream returned a Response object, exact OK and usage in 7.12 seconds; stream=false returned the same contract in 2.66 seconds; stream=true emitted exact OK and response.completed in 2.72 seconds. Final public-route JSON and stream reruns also passed

Sol, Luna and Qwen3.8-Flash-Next Chat JSON and streaming each returned exact OK. Final public Sol Chat passed. Astra Chat returned 429 on initial and final calls; status-only inspection classified the gateway message as no deployments available/cooldown, not a proven provider quota diagnosis. No retry/cooldown setting or credential was changed

## NAS MCP and discovery

Public protected-resource discovery at both path forms returned 200 JSON, equivalent documents and exact https://litellm.staticduo.com/lazymcp resource. Authorization-server discovery returned 200. Unauthenticated /lazymcp and /mcp returned 401 with a challenge. Final LazyMCP challenge used the exact path-inserted resource_metadata; invalid bearer added invalid_token

Public LazyMCP initialize and list passed, exposing exactly three gateway tools. mcp_status passed in 5.04 seconds; Memory/memory-find describe passed in 0.04 seconds; actual mcp_call Memory/memory-find passed in 5.43 seconds with HTTP 200, no RPC error and isError=false. Final real lookup after soak passed again. Tool arguments and returned private content are not retained

Standard public /mcp with x-mcp-servers=memory passed initialize in 0.08 seconds, tools/list with 19 tools in 0.06 seconds, and actual read-only memory-health in 0.15 seconds. Final selected real tool passed again

Unscoped /mcp initialize failed with HTTP 504 in 30 seconds through both public and loopback routes. MCP REST /v1/mcp/server/health returned 200 with 24 healthy and three unhealthy registrations: Frigate_Observe, Frigate_Admin and Frigate_Breakglass. Historical memory includes an external Frigate/administration availability incident, but this execution does not establish an unchanged pre-deployment aggregate result or conclusively attribute the new observation to that incident. Unscoped initialization is not a passed check

Final public model inventory remained 38 and MCP registration count remained 27. All four dependency IDs, start times, image IDs, running state, restart=0 and OOM=false match preflight exactly. Protected config/wrapper bytes and nonselector environment bytes match the backup; no host-specific settings were replaced

## Complete time-bounded log classification

Docker logs were streamed from 2026-09-05T13:49:53Z through final collection without retaining raw lines. Log command exit=0. HTTP access counts: 200=559, 204=244, 307=155, 429=176, 202=6, 401=4, 504=2, 400=25. These include background clients and verification, not only operator traffic

Classified line counts: Traceback=417, no deployments available=994, cooldown=2521, timed out=8. P3009=0, P3018=0, migration failed=0, out of memory=0, Connection refused=0, All connection attempts failed=0, TimeoutError=0. Counts can overlap; they are not independent exception totals. This is not a clean-error-log claim. The unresolved live cooldown and aggregate timeout remain visible despite successful representative calls

## Resource observation

31 complete samples across 900.46 seconds, 30-second cadence, same container throughout. Every health/readiness/liveliness and memory/no-swap assertion passed. Memory.current start=1490055168, end=1465851904, peak=1506947072 bytes, delta=-24203264. Cgroup anon start=1223745536, end=1226432512, delta=2686976 bytes. All memory.max/oom/oom_kill counters remained zero. No forced GC, cache clearing, operator inference or operator MCP load was used during the observation. Ordinary background clients remained active. This bounded gate does not prove indefinite stability

## Fedora final recheck and identity parity

Unchanged Fedora container 164bab0c75f9294a3a7977420c2fda7686acb7a7bc5317af2d0768021b721264 remains running/healthy, restart 0, OOM false, started 2026-09-05T11:56:43.327234193Z. Fresh readiness/liveliness 200, model count 29, actual Astra SDK JSON/stream Responses exact OK, Sol Chat exact OK and real defend_memory-find HTTP 200/no RPC error/isError=false all passed after the NAS soak

Fedora memory.current=2004688896, memory.max=8589934592, memory.swap.max=0, all memory event counters zero. Both hosts have the identical authorized OCI index and full source revision. The sole linux/amd64 child resolves to config 02a12f580ddbaddc0e27529901d629fb54d4ec571257af7afe090f9decf4850f. NAS reports that config as its local image ID; Fedora's containerd image store reports the OCI index as its local image ID. Raw .Image strings are therefore not compared as if the engine representations were identical

## Documentation and deferred findings

No product source, credential, MCP registration, model/fallback configuration, dependency, API or UI changed. No product documentation or screenshot is required. Operational task/SCR/registry/evidence updates are complete for this handoff, but PMA retains final closure authority

No new security scan, signing/attestation verification, DCR issuance or full audience-isolation matrix was performed on this continuation. Previous private-local-output credential rotation recommendations, maintenance-tool findings and additional supply-chain/defense-in-depth review remain deferred as instructed. Their historical evidence is not represented as a new security PASS for the final image

StaticEng validation PASS, all source directories indexed, hierarchy validated, zero warnings. No product tests/build were rerun for this deployment-only task; the exact image inherits the 337 focused tests and clean source/build evidence recorded in Fedora log 19. Historical unavailable-provider integration failures remain disclosed, not reclassified as passing tests
