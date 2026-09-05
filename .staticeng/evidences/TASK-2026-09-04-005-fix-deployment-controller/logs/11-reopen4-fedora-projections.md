# Reopen 4: Real Fedora Read-Only Verification

SSH alias `fedora`, fixed container projection only; command exited zero for all seven named dependencies. No configuration, environment, full object, credential, restart, deployment, or runtime-source access.

Exact tested projection:

```text
[{{json .Id}},{{json .Image}},{{json .State.StartedAt}},{{json .State.Status}},{{with index .State "Health"}}{{json .Status}}{{else}}"none"{{end}},{{json .RestartCount}},{{json .State.OOMKilled}}]
```

Invocation: `docker inspect --type container --format '<projection>' postgresql litellm-redis defend-memory-mcp defend-memory-memory-agent-gateway defend-memory-postgres defend-memory-qdrant defend-memory-neo4j`

| Dependency | State | Health | Restarts | OOM |
| --- | --- | --- | --- | --- |
| postgresql | running | healthy | 0 | false |
| litellm-redis | running | healthy | 0 | false |
| defend-memory-mcp | running | healthy | 0 | false |
| defend-memory-memory-agent-gateway | running | healthy | 0 | false |
| defend-memory-postgres | running | healthy | 0 | false |
| defend-memory-qdrant | running | none | 0 | false |
| defend-memory-neo4j | running | healthy | 0 | false |

All returned scalar ID/image/start fields were populated. `none` explicitly means absent healthcheck, not healthy. Healthy/unhealthy/absent semantics also pass real Go template execution with `missingkey=error`, not merely mocked Docker output.

Baseline uses the same maintained `DEPENDENCY_FORMAT` via `WATCHDOG_COMMAND_TEST=dependency-baseline bash <generated>/collect-watchdog-sample.sh`; it emits only the complete dependency TSV SHA256 on success. Executor must require exit zero and discard any failed/partial digest. Collector sample path uses the identical template and dependency order.
