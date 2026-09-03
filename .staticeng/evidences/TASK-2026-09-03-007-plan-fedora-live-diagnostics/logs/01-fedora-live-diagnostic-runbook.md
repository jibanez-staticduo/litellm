# Fedora Candidate Live Diagnostic Runbook

## Purpose And Non-Negotiable Boundaries

This runbook is the execution contract for `TASK-2026-09-03-006-diagnose-fedora-candidate-live` under the maintenance amendment in `SCR-2026-09-01-001-upstream-main-integration`

Use only the frozen candidate, config, source, and rollback subjects in `../SUMMARY.md`. Do not change a mutable tag, NAS, production data, credentials, MCP registration, model routing, timeout, healthcheck, container limit, source file, or host configuration during diagnosis. Instrumentation is read-only or ephemeral and must expose no new port. Request arguments, response payloads, tokens, authorization material, database content, and private data must not enter repository evidence

The prior incident was a global OOM kill, so the candidate must never run without the rollback watcher described below. A manual-only memory watch is prohibited

## Evidence Layout And Clock

Before any deployment, create one host-local owner-only attempt under the existing Fedora release root

```sh
set -eu
umask 077
TASK=TASK-2026-09-03-006
ATTEMPT="/home/staticduo/docker/litellm/releases/${TASK}-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -m 0700 "$ATTEMPT" "$ATTEMPT/rollback" "$ATTEMPT/raw" "$ATTEMPT/safe"
date -u +%Y-%m-%dT%H:%M:%SZ >"$ATTEMPT/safe/preflight-wall.txt"
cut -d' ' -f1 /proc/uptime >"$ATTEMPT/safe/preflight-monotonic.txt"
chmod 0600 "$ATTEMPT"/safe/*
```

Raw host-local diagnostics remain mode `0600`. Only allowlisted aggregate metadata moves into repository evidence. The four-hour clock starts immediately before the selector's first atomic change. Record both UTC wall time and `/proc/uptime` monotonic seconds as `T0`

## Phase 0: Fresh No-Go Gates And Rollback Unit

Repeat the full TASK-012 release preflight rather than reusing its old artifacts

1. Verify local and remote fork `main` are unchanged except approved `.staticeng` closure after source `bf58974a935521fa570fa7e280c51a00b2e5b54e`
2. Reverify the candidate registry manifest, config, source label, `linux/amd64` platform, StaticDuo signature, transparency inclusion, and sole-subject SPDX, CycloneDX, and SLSA attestations with the approved public identity
3. Require current selector, runtime config, and source to equal the frozen rollback subjects. Require healthy, restart 0, OOM false, readiness 200, liveliness 200, dependencies healthy, and protected inventory equal to the approved baseline
4. Copy `.env`, Compose, config, startup wrappers, exact inspect output, dependency identity/start times, mounts, networks, ports, ulimits, command, credential metadata, model/fallback/MCP fingerprints, migration state, and bounded log start time to `rollback/` with directories `0700` and files `0600`. Never print file content containing secrets
5. Stream a new custom-format PostgreSQL dump to `rollback/database.dump`, compute SHA-256, produce `pg_restore --list`, and restore into a disposable isolated PostgreSQL using the exact locally inspected database image identity. Require the expected migration ledger, schema/table counts, zero task-artifact tables, successful cleanup, and no production write
6. Prove the exact prior image remains locally inspectable and runnable. Prepare, syntax-check, and independently review an idempotent rollback command that restores only the single `LITELLM_IMAGE` line and runs `docker compose --env-file .env -f docker-compose.yaml up -d --no-deps litellm`
7. Render Compose with the candidate and prove the only semantic delta is `litellm.image`. Stop if any identity, backup, restore, protected state, dependency, migration, or render gate differs

Do not restore the production database automatically under any outcome

## Phase 1: Arm Read-Only Instrumentation Before Deployment

Use independent samplers so a blocked HTTP request cannot stop memory evidence. Prefix every record with UTC nanoseconds and `/proc/uptime`. Start samplers against the rollback image, capture at least 30 seconds of baseline, then keep the same processes running across candidate deployment

### One-Second Memory And Host Sampler

Each second, resolve the current `litellm` container ID and cgroup. Record these allowlisted values only:

- cgroup `memory.current`, `memory.peak`, `memory.swap.current`, `memory.events`, `pids.current`, and `pids.max`
- for every PID in `cgroup.procs`: PID, parent PID, command name, `VmRSS`, `VmSize`, `VmSwap`, `Threads`, file-descriptor count, and `smaps_rollup` fields `Rss`, `Pss`, `Anonymous`, `Private_Dirty`, and `Swap`
- `/proc/meminfo`: `MemAvailable`, `SwapTotal`, `SwapFree`, `Committed_AS`, `CommitLimit`, and `PageTables`
- `/proc/pressure/memory` and `/proc/pressure/cpu`
- `docker stats --no-stream` CPU, memory, PIDs, network I/O, and block I/O for `litellm`, `postgresql`, `litellm-redis`, `defend-memory-mcp`, `defend-memory-memory-agent-gateway`, `defend-memory-postgres`, `defend-memory-qdrant`, and `defend-memory-neo4j`
- container health, restart count, OOM flag, PID, start time, configured image, and runtime image

Never record `/proc/<pid>/environ`, command arguments that may contain credentials, mounted file content, request bodies, or network packet payloads

Capture candidate baseline `B` as the maximum `memory.current` over 30 healthy seconds immediately before the real-tool call. The watchdog evaluates every one-second sample and invokes the pre-reviewed rollback command when any immediate gate below fires

### Two-Second Event-Loop And Health Sampler

Against `http://127.0.0.1:4000`, run each with `curl --silent --show-error --output /dev/null --write-out` and `--max-time 5`. Retain status and total duration only

```text
GET /health/liveliness
GET /health/readiness
```

With the existing protected admin credential loaded from its owner-only source without printing it, also sample these every five seconds and retain only numeric/count fields

```text
GET /health/backlog
GET /debug/asyncio-tasks
GET /debug/memory/summary
```

`/health/liveliness` proves event-loop service. `/health/readiness` additionally traverses the bounded DB check. `/health/backlog` reports in-flight HTTP work. `/debug/asyncio-tasks` reports count and coroutine names. `/debug/memory/summary` reports process RSS, cache item counts, and GC counts. Do not call `/debug/memory/details` during growth because its full object walk perturbs the process

### Five-Second Pool And Dependency Sampler

For LiteLLM PostgreSQL, run an aggregate-only `pg_stat_activity` query as the established local database administrator. Group by database, application name, state, and wait-event class. Retain counts, oldest transaction age, total/max connections, and lock-wait counts. Never select query text, client address, user content, or row data

Discover the Prisma query-engine port from its own process arguments inside the container and read its loopback `/metrics`. Retain only these series

```text
prisma_client_queries_wait
prisma_pool_connections_busy
prisma_pool_connections_idle
prisma_pool_connections_open
prisma_pool_connections_opened_total
prisma_pool_connections_closed_total
prisma_client_queries_wait_histogram_ms
```

For Redis, use the credentials already present inside `litellm-redis`, passed through `REDISCLI_AUTH` rather than a command argument. Retain only `connected_clients`, `blocked_clients`, `maxclients`, `used_memory`, `used_memory_peak`, `evicted_keys`, `rejected_connections`, `total_connections_received`, and instantaneous operations per second. Do not run `KEYS`, `SCAN`, `MONITOR`, `CLIENT LIST`, or any command that exposes keys or payloads

Every five seconds, retain status, health, restart, OOM, CPU, memory, PIDs, network counters, and health latency for the Defend MCP, gateway, PostgreSQL, Qdrant, and Neo4j. The allowed active checks are TCP connect to `defend-memory-mcp:8000`, gateway `GET /health`, Qdrant `GET /healthz`, PostgreSQL `pg_isready`, and the existing Neo4j healthcheck result. Do not query memory records or graph content

### Correlation And Log Filters

Generate a safe correlation identifier `diag-<UTC>-<8 hex>` and send it as `X-LiteLLM-Trace-ID`. Record its value and exact monotonic start/end, but no request arguments or response body

Capture Docker events and kernel journal continuously from T0. For application logs, retain only lines in the bounded interval from 30 seconds before the call until the call settles or rollback begins, then reduce them to timestamp, service, severity, route class, HTTP status, duration, exception class, timeout class, restart/OOM marker, and the safe correlation ID. Redact URL query strings, headers, bodies, bearer material, keys, credentials, prompts, model input/output, MCP arguments/results, database queries, and private identifiers before repository transfer

Allowlisted incident classes are `timeout`, `cancelled`, `disconnect`, `memory`, `oom`, `health`, `readiness`, `liveliness`, `backlog`, `pool`, `connection`, `MCP`, `LazyMCP`, `embedding`, `rerank`, `traceback`, `exception`, `restart`, and `exit 137`

## Phase 2: Deploy Exact Candidate And Stabilize

Immediately before the atomic selector change, record T0 wall and monotonic times. Change only the single `LITELLM_IMAGE` value, preserving owner, mode, and all normalized non-image bytes. Pull only the exact digest and recreate only `litellm` with `--no-deps`

Within 180 seconds require exact manifest/config/source, the same container identity throughout startup, migration count 161 with no failure state, healthy, readiness/liveliness 200, restart 0, OOM false, unchanged dependencies and protected projections, and memory no more than `B + 512 MiB`. Any other failed gate rolls back immediately. The amended timeout exception does not apply before the one approved real-tool call

After initial health, collect 30 seconds of candidate baseline. Do not run broad Chat, Responses, discovery, or model suites before reproduction; TASK-012 already showed they pass and extra traffic weakens causality

## Phase 3: One Bounded Reproduction

Use the existing protected exact-audience OAuth credential. Keep it in its owner-only file or process environment and never place it in shell history, process arguments, stdout, or evidence. Build the harmless JSON-RPC request in memory or a `0600` tmpfs file, delete it on exit, and discard the response body after extracting the safe verdict

Call exactly one request at a time against `/toolset/defend_memory/lazymcp`:

```json
{
  "jsonrpc": "2.0",
  "id": "<safe-correlation-id>",
  "method": "tools/call",
  "params": {
    "name": "mcp_call",
    "arguments": {
      "server": "defend_memory",
      "tool": "defend_memory-find",
      "arguments": {
        "query": "fedora diagnostic probe",
        "strategy": "deterministic",
        "top_k": 1,
        "candidate_k": 5,
        "graph_top_k": 0
      }
    }
  }
}
```

Use `Content-Type: application/json`, `Accept: application/json, text/event-stream`, `Authorization: Bearer <from-protected-source>`, and `X-LiteLLM-Trace-ID: <safe-correlation-id>`. Set the client deadline to 75 seconds. This exceeds LiteLLM's effective 60-second MCP deadline enough to capture its bounded 504 outcome but remains below the Defend service's 180-second outer budget. Disable client retries. Do not launch a second attempt, a parallel discovery, or any unrelated workload while the call is in flight

Retain only start/end timestamps, HTTP status, whether a JSON-RPC result existed, `isError` boolean, timeout/error class, and whether each observed layer accepted/completed the correlation. Never retain the query, arguments, result content, token counts, memory text, or response hash

When the request ends or the watchdog fires, wait at most 15 seconds for all in-flight counters to return to baseline. If they do not, rollback. A client timeout does not prove server cancellation

## Immediate Stop And Rollback Gates

The watcher kills only the diagnostic client, records the safe trigger, and immediately invokes exact digest rollback when any condition occurs

- Candidate `memory.current >= max(B + 2 GiB, 8 GiB)`
- Candidate memory rises at least 512 MiB per second for three consecutive one-second intervals
- Candidate `VmRSS`, cgroup memory, anonymous/private dirty memory, thread count, PID count, or file descriptors continue monotonically upward for five samples after the request ends
- Host `MemAvailable < 32 GiB`, swap use exceeds 512 MiB, memory PSI `full avg10 > 0.10`, any new kernel OOM event appears, or candidate cgroup `memory.events` increments `oom` or `oom_kill`
- Candidate restart count becomes nonzero, container/start identity changes, OOM flag becomes true, exit 137 occurs, or required instrumentation loses the candidate for more than two samples
- CPU exceeds 800 percent for 10 seconds, PIDs exceed 500, file descriptors exceed 8192, PostgreSQL connections reach 80, Redis clients reach 500, blocked Redis clients exceed 0 for 10 seconds, or disk free falls below 20 GiB or 15 percent
- Data-integrity risk, unexpected production-data mutation, security or authorization regression, secret exposure, permission/audience expansion, protected-state drift, dependency restart/change, NAS access, candidate identity mismatch, or loss of backup/rollback confidence
- Any failed gate other than the one authorized real-tool timeout/unhealthy transition
- Remaining time no longer supports correction, full verification, 900-second soak, verdict, and verified rollback

These are stop thresholds, not tuning recommendations. Do not raise them live

## Root-Cause Decision Tree

Use the first matching terminal branch. Evidence must name one branch and exclude the others

1. **Security, data, identity, or uncontrolled-resource gate:** rollback immediately, classify incident critical, notify PMA, and do not continue diagnosis
2. **Docker unhealthy while direct readiness is 200 and fast:** healthcheck-only. Compare the exact health command exit and timing. A healthcheck correction is a protected Compose change requiring a separate task, review, baseline, and release authorization
3. **Liveliness fast, readiness slow/503, Prisma wait/busy saturated, PostgreSQL connections or waits elevated:** DB/pool. If URL query keys or configured pool values differ from approved baseline, classify configuration-only. If equal and candidate source changes pool/reconnect behavior, classify source-code. Never change pool settings live
4. **Liveliness fast, DB healthy, Redis blocked/rejected or client count saturated:** Redis/infrastructure or candidate Redis-pool source behavior. Use identity/config equality and stable rollback control to distinguish them
5. **401/403/challenge mismatch with stable resources:** route/auth configuration or source. If registered row, grant, audience, and protected hashes are unchanged, classify candidate route/auth source regression. Do not mint broader credentials or weaken audience checks
6. **Request does not enter LazyMCP or fails before `mcp_call`, while liveness and pools remain stable:** LazyMCP proxy/source. Correlate route status, asyncio task names, and no upstream MCP acceptance
7. **LazyMCP accepts, upstream MCP accepts, LiteLLM remains bounded, but upstream completion stalls while Defend service/dependency memory, CPU, pool, or health changes:** upstream MCP/infrastructure. Correct only in the separately governed agent-memory repository/deployment path
8. **Candidate memory surges while Defend services remain bounded:** candidate source/resource. If surge begins before upstream MCP acceptance, inspect LazyMCP tool listing/auth/logging. If it begins after upstream acceptance and with reentrant `/v1/embeddings` or `/rerank`, inspect candidate model request/response, logging, streaming, and callback retention on that reentrant path. If it begins only while serializing the returning MCP result, inspect MCP result/logging/guardrail retention
9. **Liveliness and readiness both stall with stable RSS but high CPU/backlog/tasks:** event-loop/source. A blocked synchronous operation is favored over infrastructure when dependencies remain fast
10. **Call succeeds and all metrics return to baseline:** no root cause. This is an unexplained transient, not release success. Continue only to the two-hour checkpoint if evidence identifies a concrete next discriminating read-only step; otherwise rollback

Prior evidence already excludes healthcheck-only and upstream dependency failure as complete explanations for the 100.3 GiB process. The bounded run must identify which candidate request phase allocated it

## Correction, Review, Rebuild, And Authorization Flow

No correction is made under the diagnostic task itself

- **Configuration-only or healthcheck-only:** create the smallest Fedora configuration task tied to the SCR, document exact old/new normalized values, review security and rollback impact, test against a production-equivalent isolated harness, and obtain explicit release authorization. Because the runtime configuration identity changes, repeat baseline and release gates even if the image digest does not
- **Upstream MCP or Defend infrastructure:** create a separate task in `agent-memory-platform`, identify its CodeMap and source/image subjects, add a regression, qualify and release its exact image/config through that repository, then prove the rollback LiteLLM real-tool baseline before any candidate retry. NAS remains untouched
- **LiteLLM source:** create an atomic implementation task against the identified module. Add a regression that fails before the fix and asserts bounded RSS/task/pool behavior across the exact reentrant call. Run focused MCP, LazyMCP, health, DB, Redis, logging, auth, and memory tests plus all repository gates required by the SCR
- **Infrastructure capacity:** do not solve a source leak by adding RAM, swap, retries, or a larger timeout. Capacity changes require a separate infrastructure task and cannot qualify an unexplained candidate

Any source or image change invalidates the old candidate. Build a new builder and final image from a clean exact reviewed commit, with frozen inputs and `linux/amd64` platform. Repeat isolated migrations, functional and preservation matrix, the memory reproduction/regression, SPDX and CycloneDX SBOMs, same-database vulnerability scans, SLSA provenance, zero Critical and zero fixable High policy, exact registry manifest/config equality, StaticDuo signature, all attestations, transparency verification, and independent QA, security, and Tech Lead approval. PMA must issue a new exact-digest Fedora release authorization before redeployment

An unchanged candidate may proceed only if evidence proves a non-candidate root cause, that cause is separately corrected and verified, and PMA reauthorizes the same exact digest. An unexplained successful retry is not such proof

## Maintenance Schedule And Decision Records

All offsets use monotonic elapsed time from T0

```text
T-45 to T0   fresh identity, protected baseline, backup, isolated restore, rollback rehearsal, watcher baseline
T+0          atomic selector change; four-hour clock starts
T+0 to +3    candidate startup and mandatory initial gates
T+3 to +8    30-second candidate baseline and one bounded reproduction
T+8 onward   correlation and root-cause classification; rollback immediately on any stop gate
T+90         advisory feasibility review; no correction path means rollback
T+120        mandatory Tech Lead CONTINUE or ROLLBACK checkpoint and PMA notification
T+165        latest allowed completion of correction review, qualification, signing, and explicit authorization
T+180        latest allowed final exact-digest deployment
T+195        latest allowed completion of all pre-soak gates
T+195 to +210 mandatory continuous 900-second soak
T+210 to +220 full final rerun and evidence review
T+225        internal hard rollback cutoff unless every success gate already has recorded Tech Lead PASS
T+240        SCR hard deadline; no new action may begin, and no unapproved candidate may remain
```

At T+120, continuation requires exact candidate/rollback identity, usable backup, reliable instrumentation, bounded resources, no critical event, a named root cause, a named correction or justified unchanged-candidate path, owners present, and a credible schedule through T+220. Missing evidence or no affirmative signed decision means rollback immediately

At T+165, if corrected artifact approval and signing are incomplete, rollback. At T+180, if the final authorized digest is not deployed, rollback. At T+195, if pre-soak gates are incomplete, rollback. At T+225, if final PASS is incomplete, rollback. These earlier cutoffs preserve time to verify the restored service before T+240

## Final Candidate Verification And Soak

Before soak, require exact manifest/config/source/signature/attestations, migration identity, healthy/readiness/liveliness, restart 0, OOM false, stable memory below `B + 512 MiB`, unchanged dependencies and protected state, exact model/fallback/MCP inventories, Chat Completions, Responses, MCP REST, `/mcp`, all six LazyMCP discovery aliases, exact challenge cases, DCR, audience isolation, authorized initialize/list/call, and one successful real `defend_memory-find`. Retain only safe status/class metadata

Run 900 continuous seconds with 30-second release-gate polls and the one-second memory watchdog still armed. Every poll requires the same container/start identity, exact artifact identity, healthy/readiness/liveliness, restart 0, OOM false, unchanged dependencies, bounded pool/backlog/task counts, and no monotonic memory growth. At minute 15 rerun every functional, inventory, preservation, migration, auth/audience, real-tool, resource, and bounded-log gate. A shortened, interrupted, ambiguous, or unexplained soak is failure

Tech Lead records PASS only after root cause, correction identity, full rerun, and all 900 seconds pass. Success from the rollback image does not qualify the candidate

## Exact Rollback And Verification

On any rollback trigger:

1. Terminate the single diagnostic client and stop new probes that could add traffic. Keep passive samplers and Docker/kernel event capture running
2. Record trigger, UTC, monotonic elapsed time, candidate identity, last safe memory sample, and last observed layer. Record no body or credential data
3. Atomically restore only the protected `PREVIOUS_REF` selector while preserving `.env` owner, mode, and every non-image byte
4. Pull the prior digest only if absent, then run only `docker compose --env-file .env -f docker-compose.yaml up -d --no-deps litellm`
5. Require exact rollback manifest/config/source, healthy, readiness/liveliness 200, restart 0, OOM false, 161-migration compatibility, baseline model/fallback/MCP fingerprints, Responses, MCP REST, standard MCP, all LazyMCP gates, authorized real tool, dependencies, protected state, bounded resources, and clean bounded logs
6. Require memory to remain within the recorded rollback baseline for five minutes. Confirm no new kernel OOM, dependency restart, protected drift, NAS access, or automatic database restore
7. Stop ephemeral samplers, sanitize allowlisted evidence, delete tmpfs request/token-derived material, preserve the owner-only database backup on Fedora, and notify PMA

If exact rollback identity or health cannot be fully verified, declare a critical Fedora incident immediately. Do not restore the database, patch production, broaden credentials, move tags, or touch NAS
