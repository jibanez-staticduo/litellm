# Sanitized live observations

## Commands and containment

All deployment mutations were executed through `ssh fedora`, where hostname returned `fedora`. An initial local hostname check returned `nas`; no local deployment mutation followed. Repository/task writes remain in the provided shared workspace

Applied the retained unified diff with a successful `patch --dry-run`, then `patch -d /home/staticduo/docker/litellm -p0`. Commands against Fedora:

```text
docker compose --project-directory /home/staticduo/docker/litellm -f /home/staticduo/docker/litellm/docker-compose.yaml config -q
docker compose --project-directory /home/staticduo/docker/litellm -f /home/staticduo/docker/litellm/docker-compose.yaml up -d --no-deps --force-recreate litellm
```

Both commands passed. Before startup completed, cgroups returned:

```text
memory.current 99676160
memory.max 8589934592
memory.swap.max 0
memory.events: max=0 oom=0 oom_kill=0
pids.current 6
```

Readiness subsequently returned 200 in 0.004243 seconds at memory.current=999854080. Authenticated GET /v1/models returned 200 with 29 aliases. Credentials were loaded directly from the owner-only Fedora .env in process memory, never emitted or copied

## First run

POST /v1/responses, model gpt-6-astra, harmless input `Reply only OK`, max_output_tokens=64, request correlation `task-0905-responses-1`: HTTP 400 in 1.356 seconds, error code 400. Provider error body was not retained. A later probe with explicit low reasoning effort returned URLError without an HTTP response after the candidate had died

Final inspection: exited, exit 137, OOMKilled=true, restart count 0, memory=8589934592, memory+swap=8589934592, restart=no

Bounded preceding logs: 29 completed POST /v1/chat/completions access entries, one POST /v1/responses, no operator Defend find invocation. UnsupportedParamsError markers named gpt-5.6-luna. The counts were log occurrences, not unique requests. Longest inspected line was 789 characters, so those retained lines did not demonstrate an exponentially growing error message

## Second run

Manually started the same contained candidate. Ran 36 five-second cgroup samples plus existing /debug/memory/summary and /debug/asyncio-tasks reads with two-second deadlines. No new observability endpoint or framework was created

```text
sample 0:  903741440 bytes, 10 tasks
sample 4:  905396224 bytes, 21 tasks
sample 9:  924446720 bytes, 24 tasks
sample 14: 945983488 bytes, 24 tasks
sample 18: 938291200 bytes, 22 tasks
sample 19: 937664512 bytes, 13 tasks
sample 20: 3064434688 bytes, both debug endpoints TimeoutError
sample 21 onward: container no longer running, debug URLError
finished: 2026-09-05T08:27:09.793351454Z, OOMKilled=true
```

The 13-task sample contained one each of LoggingWorker._worker_loop, _monitor_spend_logs_queue, RequestResponseCycle.run_asgi, Server.serve, LifespanOn.main, SlackAlerting._run_scheduled_daily_report, ConfigSyncSubscriber._run, AlertingHangingRequestCheck.check_for_hanging_requests, _cleanup_expired_stateful_session_auth_contexts, _shutdown_watcher, _adaptive_router_flusher_loop, PrismaClient._db_health_watchdog_loop and AuthCacheInvalidationSubscriber._run

Earlier samples contained one MCP GET/SSE session, which had drained before the 13-task sample. This temporal association does not prove MCP cleanup caused growth. Live chat requests and periodic metrics reads were also present

Memory summary reports that psutil is absent, so its RSS field is unavailable. Cgroup readings above are the actual measurements. GC was enabled and the last successful sample reported 1672 objects awaiting collection. No full object walk was invoked

## Third run and bounded native stack

Manually started the same contained candidate. One-second cgroup polling triggered an installed gdb stack-only sample at 1807577088 bytes, after 63-second memory observation of 932409344 bytes. Sampling used an eight-second subprocess deadline, disabled auto-load and `set print frame-arguments none`, `thread apply all bt 12`, then detached. Return code was 0. No locals or heap were requested

Main Python process PID was 850337. Main-thread frames, reduced to symbols/library:

```text
#0 _Py_dict_lookup, libpython3.13.so.1.0
#1 insertdict, libpython3.13.so.1.0
#2-#11 unresolved native frames in pydantic_core/_pydantic_core.cpython-313-x86_64-linux-gnu.so
```

Frames 5/8/11 shared the same instruction address, frames 6/9 shared another, and frames 7/10 shared another. This is consistent with recursive native Pydantic work, but the truncated stack has no Python caller and is not a proven allocation root cause. Four libuv worker threads were waiting on condition variables, two Python queue threads were waiting, one thread was in waitpid and another in a lock wait

The candidate subsequently exited 137/OOMKilled=true for the third time. Final inspection confirmed the same container/image, zero restarts, 8589934592 memory and memory+swap, restart=no and the base Compose file as recreation source. Final `docker compose ... config -q` passed; a protected YAML projection confirmed restart=no, mem_limit=8g, memswap_limit=8g
