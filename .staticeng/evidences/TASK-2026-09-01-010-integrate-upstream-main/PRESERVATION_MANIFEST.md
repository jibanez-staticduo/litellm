# Fork Preservation Manifest

## Frozen Subjects

- Fork tip before merge: `51b5f7e474e6de50bdec2eea64e33f4878fadf4b`
- Reviewed upstream target: `10631eb834c7802aa61611e807474170b8a4d425`
- Merge base: `bc6e7df05b018eefe6c7293790ca3f4de38709ac`
- Strategy: `git merge --no-ff --no-commit 10631eb834c7802aa61611e807474170b8a4d425`

## Preserved Behaviors

| Behavior | Owning task/commit | Principal paths | Upstream overlap and resolution | Mutation-sensitive verification |
| --- | --- | --- | --- | --- |
| DeepSeek hosted-vLLM reasoning policy | `TASK-2026-08-25-003`, `0f972ca3d5` | `litellm/llms/hosted_vllm/**`, mapped tests | Retained final-payload validation and zero-forwarding rules while adopting upstream provider/test changes | Hosted-vLLM chat/Responses suites in focused log |
| LazyMCP exact public resources and OAuth audience isolation | `TASK-2026-08-31-003`, `b60759def6` | `lazymcp_routes.py`, `_lazy_features.py`, `discoverable_endpoints.py`, `lazymcp_public_resource.py`, admission auth, DCR, session token, server, dashboard | Restored proxy-root root/scoped/toolset transports through exact lazy matching; made discoverable endpoints the sole canonical/alternate metadata owner; kept canonical `resource` through route identity, flow/code/access/refresh, and admission; combined it with upstream `audience`, `team_id`, RS256, revocation, and introspection | Cold-start discovery, direct route, lazy registry/OpenAPI, public-resource, admission, DCR, session-token, server, and dashboard tests |
| Standard MCP auth/permission/credential separation | Prior fork MCP tasks plus `b60759def6` | MCP manager/server/db/auth/Responses handlers | Adopted upstream credential resolver, deferred discovery, and OpenAPI auth while retaining no inbound session forwarding, toolset, BYOK, delegated auth, permission, and delete semantics | MCP manager/server/auth and Responses MCP suites |
| ChatGPT multi-profile authentication | `TASK-2026-07-07-005`, `6ccc6ae919`; routing fix `8dcccc5cd2` | `litellm/llms/chatgpt/**`, router/fallback code | Preserved profile-specific paths, process/file locking, atomic owner-only writes, and cross-profile fallback policy; adopted typed JSON parsing and current routing APIs | ChatGPT authenticator/transform tests and router fallback tests |
| Native ChatGPT Responses streaming and failure handling | `TASK-2026-08-18-011`, `b0dfe2e7a7`; `949d9ae28b` | Responses bridge, ChatGPT transformation, streaming iterator | Retained forced ChatGPT stream and failure serialization while adopting upstream provider-prefix restoration and request context | Responses bridge, OpenAI Responses, streaming iterator tests |
| Uvicorn and general secret redaction | `TASK-2026-08-26-023`, `64a3b83bf0`; prior query-redaction work | `litellm/_logging.py`, secret redaction, proxy logging tests | Kept structured five-field access-log fail-closed redaction; adopted upstream color-message, structured JSON, and truncation protections | `test_secret_redaction.py` and logging tests |
| Operational proxy fixes | Governed tasks from June-August 2026 | auth cached-dict access, spend sanitization, budget reset, onboarding, Redis coordination | Combined local compatibility/sanitization behavior with upstream model budgets, rollover, batching, onboarding rollback, and security hardening | Auth, spend management/tracking, budget, proxy focused suites |
| Reproducible candidate build inputs | `TASK-2026-08-31-008/010/012/014`, `514fd6bb8e` | root `Dockerfile` | Adopted newer upstream Wolfi digest; retained pinned Python 3.13, Rust 1.97.1 toolchain stage, uv image, and venv interpreter contract | Dockerfile inspection; image construction prohibited here |
| StaticEng governance and repository CodeMaps | pre-merge closure commits `04d58c6cbc` through `51b5f7e474` | `.staticeng/**`, `**/codemap.yml` | Retained fork-only StaticEng state; accepted upstream source moves and resolved CodeMap file-location conflicts to final paths | `staticeng_validate`, conflict ledger, no-unmerged check |

## Preservation Result

No intentional fork behavior was replaced solely because upstream touched the same file. Upstream equivalents were adopted where stronger or structurally required, with fork-specific observable constraints retained as the smallest compatible delta. Product behavior was not broadened beyond the approved SCR
