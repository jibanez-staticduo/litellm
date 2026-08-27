# Spark Pre-Mutation Stop Gate

## Identity And Discovery

NAS freshly exposed the retained Spark public group and exact qualified deployments:

| Route | Exact ID | State |
| --- | --- | --- |
| `gpt-5.3-codex-spark` | `51016fc6-8c1c-4dda-a6ff-a48f440b39f8` | public DB group, unblocked |
| `chatgpt/gpt-5.3-codex-spark` | `847df783-5d2a-44a7-afdd-d4eb2f1dec5a` | default profile deployment |
| `chatgpt-account2/gpt-5.3-codex-spark` | `6bee3424-dbec-4584-908d-2ca491a0fa4a` | account2 profile deployment |

Its authenticated general fallback remained exactly:

```text
gpt-5.3-codex-spark -> chatgpt-account2/gpt-5.3-codex-spark, chatgpt/gpt-5.3-codex-spark
```

Fedora had no Spark route, deployment, or fallback in fresh discovery

## Bounded Requests

- Request count: two, NAS only
- Endpoint: host-local authenticated `/v1/responses`
- Controls: `store=false`, streaming, client `max_retries=0`, encrypted reasoning inclusion, parallel tools disabled, no response content retained
- First status: HTTP 400; safely classified as an incompatible Spark reasoning context (`all_turns`, while Spark reported `auto` and `current_turn` support)
- Second status after using `current_turn`: HTTP 400; response content was not retained and the failure was not safely classified

## Decision

The task requires successful Spark proof before any mutation where Spark is deployed. Discovery alone is insufficient. The second request did not prove Spark functional health, so execution stopped before the Fedora-first write boundary. Fedora and NAS were not mutated
