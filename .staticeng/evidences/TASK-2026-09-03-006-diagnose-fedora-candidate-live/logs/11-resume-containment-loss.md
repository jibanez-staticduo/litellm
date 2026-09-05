# Resume: Fedora containment missing and readiness failure

## Actual host observation

On resume the candidate remained selected and running as manifest `sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`, container `24d94f97ccaca6f8415794ad815d287446b4eb78f23aac27d54ea4799c1eb8e4`. Docker reported restart count 39 and OOMKilled false. Readiness returned no bytes before its five-second deadline (HTTP code 000). The previous successful direct-tool observation does not establish current health.

Current cgroup values were memory.current=31176536064 bytes, memory.max=max, memory.swap.max=max, pids.current=48, and zero recorded cgroup oom/oom_kill events. The previously created containment override file still exists, but its limits are not effective on the running container. The reason those settings changed has not been established.

Given prior 100-GiB exhaustion and now roughly 29 GiB of uncapped usage, the operator disabled this candidate's restart policy and stopped only `litellm` (10-second graceful stop). No rollback or selector change occurred. Final Docker state is exited/unhealthy, restart count 39, OOMKilled false; candidate remains selected. Fedora service is intentionally unavailable pending repair. NAS was not accessed or changed.

## Bounded log findings

Payloads and raw log messages were not returned or copied. In the last 3000 log lines within 30 minutes, class/string counts included RateLimitError=28, HTTPStatusError=8, and 'No deployments available'=56. These are log occurrences, not distinct requests. Earlier stack-frame extraction showed Router acompletion/retry/fallback/deployment selection, SSE request processing, and HTTP handler frames. No causal link between those errors and memory growth is proven.

## Actionable same-task repair

PMA should delegate the smallest configuration correction ensuring the candidate-only 8-GiB/no-swap containment and restart policy survive the actual service recreation path. Do not rely on an optional overlay unless that recreation path consistently includes it. Verify cgroup limits after recreation before functional traffic. Separately identify the affected model deployment from protected local logs and validate its upstream availability/cooldown; do not weaken auth or increase retries/timeouts based on these class counts. A specific LiteLLM source patch cannot yet be justified; allocator and restart cause remain unknown.

## AC coverage

- AC-1: Current containment no longer matches prior verification; prior backup/recovery retained, no new restore.
- AC-2: Current readiness failure and cgroup measurements captured; no new real-tool request sent.
- AC-3: Missing effective memory limit established; root cause of setting loss, restarts, and product allocation remains unresolved.
- AC-4: No product patch, auth change, or destructive DB action. Only candidate restart disable and stop for containment.
- AC-5: FAIL current readiness; functional matrix and 900-second soak not completed.
- AC-6: No automatic rollback under controlling PO direction. NAS untouched and not eligible for promotion.
- AC-7: Evidence and original task/registry updated; overall task remains incomplete.

Known pending normalization and optional-health source changes remain preserved and unqualified by this execution. No new code was implemented. Deferred security items remain separate from the functional repair.
