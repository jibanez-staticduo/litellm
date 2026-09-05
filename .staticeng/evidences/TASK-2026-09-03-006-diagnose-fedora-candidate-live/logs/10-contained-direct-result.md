# Contained Fedora Direct Probe

Latest PO direction supersedes automatic rollback. The retained exact candidate was deployed using the existing Compose definition plus a candidate-only override: memory 8 GiB, total memory-plus-swap 8 GiB (no swap), restart disabled. Recovery backup remains under `/home/staticduo/docker/litellm/releases/TASK-006-r9-live/rollback`. No legacy rollback controller was run. No matching legacy watchdog/rollback processes were observed; user timers contained no task rollback timer.

## Actual Results

- Candidate runtime image: `sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`.
- Readiness after deployment: HTTP 200.
- Cgroup memory.max: 8589934592; memory.swap.max: 0, verified before request.
- Exactly one diagnostic POST to aggregate `/lazymcp`, calling `mcp_call` for `defend_memory-find`.
- Existing admin key loaded from owner-owned, owner-only `.env` inside the diagnostic child process; no key output or separate credential artifact.
- Response: HTTP 200, JSON-RPC result present, `isError=false`, 2.045 seconds.
- Memory observation: 19 samples including 15 seconds after client settlement; peak and final memory 1061855232 bytes (about 0.989 GiB).
- No retry, fallback request, second diagnostic request, temporary principal, or DCR bootstrap.

## Remaining Verification

The 15-second observation proves only sampled memory behavior, not complete asynchronous task/socket drain. A five-minute access-log count returned 9 embedding matches, 3 rerank matches, and 9 LazyMCP POST matches. This interval includes unrelated traffic; these are NOT request-correlated counts and do not establish the one-embedding/three-rerank/zero-nested constraints. No conclusion about nested-request causality is justified.

Full Chat/Responses/model/MCP/audience gates and 900-second soak have not run. Candidate remains selected under the containment override per PO direction; this is not a release PASS. NAS remains untouched. Product root cause of the historical 100-GiB exhaustion remains unresolved; this one direct request did not reproduce the historical timeout.
