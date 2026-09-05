# TASK-2026-09-03-007 Evidence Summary

## Summary

The Fedora candidate failure is now bounded to candidate-process resource exhaustion. At `2026-09-03T21:49:23Z`, the kernel global OOM killer selected the candidate LiteLLM process at about 100.3 GiB anonymous RSS. Docker recorded exit 137 and restarted it five seconds later. The registered Defend MCP, gateway, PostgreSQL, Qdrant, and Neo4j services remained running without restart or OOM, and the gateway continued returning health 200 across the kill

The exact allocation site remains unproven. The highest-value boundary is the reentrant path where `defend_memory-find` reaches the Defend memory MCP, which calls Fedora LiteLLM again for embedding and rerank while the original LazyMCP request remains open. The execution runbook captures this path with bounded, secret-safe observability and fails closed before memory can threaten the host again

## Work Performed

- Read the failed release task/evidence, amended SCR, parent execution task, release authorization, source CodeMaps, health endpoints, LazyMCP routes, MCP manager, and Defend memory source
- Inspected Fedora topology, healthchecks, container identities, network membership, mounts, cgroup limits, process shape, resource state, pool metrics, kernel OOM evidence, and bounded service logs read-only
- Defined the exact diagnostic, correlation, reproduction, decision, correction, timing, rebuild/sign, soak, and rollback contract in `.staticeng/evidences/TASK-2026-09-03-007-plan-fedora-live-diagnostics/logs/01-fedora-live-diagnostic-runbook.md`
- Retained only secret-free facts in `.staticeng/evidences/TASK-2026-09-03-007-plan-fedora-live-diagnostics/logs/00-read-only-findings.md`

## Acceptance Criteria Coverage

- **AC-1: PASS.** Exact healthcheck and all requested process, event-loop, pool, transport, route, upstream, and host observability are mapped in the runbook
- **AC-2: PASS.** Prior timestamps are correlated and the reproduction is one deterministic call, concurrency one, with a 75-second external timeout and 60-second MCP server timeout
- **AC-3: PASS.** Instrumentation has fixed cadence, allowlisted output, protected local storage, no argument or payload retention, and automatic rollback thresholds
- **AC-4: PASS.** The decision tree separates configuration, healthcheck, route/auth, pool, upstream MCP, infrastructure, and source-code outcomes
- **AC-5: PASS.** Fresh rollback preparation, exact deployment, T+120 checkpoint, T+165 correction cutoff, T+180 final deployment cutoff, T+225 rollback cutoff, T+240 hard deadline, governed correction, rebuild/signing, 900-second soak, and rollback are explicit

## Documentation Impact

No steady-state documentation or CodeMap update is required. These artifacts describe a one-time governed release investigation and do not change supported behavior or source structure

## Open Risks

- The candidate image remains unsafe to leave unmonitored because the live service has no cgroup memory ceiling
- Removed-container application logs do not identify the exact allocation stack
- The direct cause may be candidate source behavior on the reentrant embedding/rerank path, but that needs the bounded reproduction to prove

## Recommended Next Step

Tech Lead should execute `TASK-2026-09-03-006-diagnose-fedora-candidate-live` exactly from the runbook, with the watchdog armed before deployment and no correction made outside a separately reviewed and authorized task

## Signed Handoff

[Agent Message] From: technical_architect To: product_manager

PASS TASK-007. Prior failure evidence proves global OOM killed the exact candidate LiteLLM process at about 100.3 GiB anonymous RSS, followed by Docker exit 137 restart. The attached runbook provides the safe one-call reproduction, full correlation surface, automatic stop gates, root-cause decision tree, governed correction path, checkpoints, rebuild/sign flow, complete verification, soak, and exact rollback. No mutation was performed
