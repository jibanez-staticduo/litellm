# Conflict Ledger

Reviewer is pending Tech Lead for every row. Verification references are under this task's `.staticeng/evidences/TASK-2026-09-01-010-integrate-upstream-main/logs/` directory

| Conflict path/group | Resolution | Preserved requirement | Verification |
| --- | --- | --- | --- |
| `Dockerfile` | Adopted upstream Wolfi digest; retained fork Rust 1.97.1/Python 3.13/uv/venv pins | Reproducible candidate inputs | lock/dependency log; image build prohibited |
| `Makefile` | Combined upstream test-quality gates and command moves with fork-configurable `LINT_BASE_REF`; made missing private staging ref fall back to the configured local base | Fork checkout must run source gates without a nonexistent remote branch | `make-check.log` records remaining budget blockers |
| `litellm/_logging.py` | Kept fork uvicorn access-record shape validation/redaction; adopted upstream color message, structured redaction, truncation, and stream routing | Access and query secrets never leak; malformed access records fail closed | focused preservation tests |
| `litellm/caching/caching_handler.py` | Kept streaming-result cache bypass; adopted upstream captured cache reference and shutdown-safe writes | Streaming iterators are not cached as completed responses | focused preservation tests |
| Responses bridge handler and test | Preserved forced native ChatGPT stream; adopted upstream provider-prefix restoration and typed result handling; retained both test sets | Native ChatGPT streaming, no double provider-prefix stripping | focused preservation tests |
| `litellm/llms/chatgpt/authenticator.py` | Combined profile selection, locks, atomic owner-only writes, and merge-safe account IDs with upstream typed JSON validation and claim parsing | Multi-account isolation and refresh safety | focused preservation tests |
| MCP admission auth and tests | Combined exact LazyMCP challenge/resource checks with upstream bearer normalization, public-resource helpers, and admission APIs | Exact audience before DB/permission lookup; standard MCP remains compatible | focused preservation tests |
| MCP DB delete path | Retained injectable cache invalidator and adopted upstream return typing | Delete clears user OAuth token cache and remains testable | focused preservation tests |
| DCR flow and tests | Carried both LazyMCP canonical `resource` and upstream `audience`/`team_id`; adopted upstream issuer, revocation, introspection, and single-use flow | Code/refresh remain exact-resource-bound; upstream RS256/introspection remains effective | focused preservation tests |
| MCP manager and server plus tests | Adopted upstream deferred OAuth discovery, credential resolution, OpenAPI auth, and guardrail logging; retained LazyMCP toolset context, public routes, credential separation, and direct/short-name behavior | No inbound gateway token forwarding; permissions/toolsets/BYOK/delegation preserved | focused preservation tests |
| Session token and tests | Extended upstream HS256/RS256 claims with fork canonical `resource`; round-trips `resource`, `audience`, and `team_id` | Exact LazyMCP resource plus signing rotation/introspection | focused preservation tests |
| Proxy auth/pre-call/server/utils conflicts and tests | Combined fork cached-dict compatibility, request secret resolution, onboarding/route behavior, spend sanitization with upstream model budgets, destination validation, lazy OpenAPI, and logo hardening | Auth fails closed without dropping legacy cached shapes or operational fixes | focused preservation tests and Prisma validation |
| Budget/spend conflicts and tests | Adopted upstream paginated/capped reads, rollover/window rows, statement batching; retained filter requirement, null-byte sanitization, poison isolation | Bounded spend paths without malformed JSON/NUL write failures | focused preservation tests |
| Router/fallback conflicts and tests | Combined ChatGPT cross-profile prohibition and logical identity with upstream access checks, attempted-target dedupe, and provider-scoped resource protections | Fallback cannot cross auth profile by default or widen caller access | focused preservation tests |
| `tests/e2e/proxy_client.py` | Adopted upstream E2E config imports and added missing typed key-info request/response models | E2E harness remains fully typed | `e2e-basedpyright.log` |
| Hosted-vLLM/OpenAI Responses/streaming/secret-redaction tests | Kept fork regressions and accepted upstream coverage additions | DeepSeek, Responses, and redaction behaviors remain mutation-sensitive | focused preservation tests |
| Dashboard `mcp_connect.tsx` | Adopted upstream shadcn/Tabs redesign while retaining dynamic `/mcp` versus `/lazymcp` URLs, labels, server identity, and LazyMCP explanatory text | LazyMCP connect instructions never point users at standard MCP | UI focused tests and build |
| Generated `schema.d.ts` | Did not hand-merge; regenerated from resolved backend OpenAPI using `npm run gen:api` | Generated API type integrity | UI generation/types/build logs |
| Generated dashboard output CodeMap | Kept final upstream build-ID location and mapped current generated manifest files | No stale build-directory pointer | no-unmerged and StaticEng validation |
| Test-tree implicit renames and 10 CodeMap location conflicts | Chose final upstream `tests/test_litellm/**` and `components/ui` layout; retained existing local maps at those destinations | CodeMaps follow actual source after upstream moves | no-unmerged and StaticEng validation |

## Completeness

- Initial explicit unmerged paths: 46
- Final `git diff --name-only --diff-filter=U`: empty
- Final `git ls-files -u`: empty
- Conflict-marker scan: no Git markers in maintained source; separator-only documentation strings excluded
- No broad `ours`/`theirs` checkout was used for behavioral conflicts

## Reopen 1: 21 Upstream-Identical Paths

TASK-013 identified 21 index blobs equal to upstream. Each was re-reviewed against merge base, fork parent, upstream parent, task ownership, and mapped tests

| Path | Final decision and proof |
| --- | --- |
| `litellm/proxy/common_utils/reset_budget_job.py` | Upstream supersedes the fork pagination patch with complete paginated rollover/window-row logic; restored budget-window tests prove bounded traversal and resets |
| `litellm/proxy/proxy_server.py` | Upstream removed the proxy-root LazyMCP handlers while its `/mcp` mount did not replace them. Reopen 2 restores root, scoped, and toolset route ownership through `litellm/proxy/lazymcp_routes.py` and `_lazy_features.py`; focused route and full LazyMCP suites pass |
| `litellm/proxy/spend_tracking/spend_management_endpoints.py` | Upstream bounded/paginated read path supersedes local legacy query; restored spend endpoint tests pass |
| `litellm/proxy/spend_tracking/spend_tracking_utils.py` | NUL-safe database payload handling is preserved by current upstream write serialization and restored regression coverage |
| `litellm/proxy/utils.py` | Upstream statement batching and poison isolation supersede the local loop; restored spend tests pass |
| `litellm/responses/mcp/chat_completions_handler.py` | Upstream `MCPRequestContext` centralizes auth/header/IP/trace extraction while preserving fork behavior; mapped MCP Responses tests pass |
| `litellm/router.py` | Custom reconciliation restores `allow_chatgpt_cross_profile_fallback`, model-group validation, and immutable logical identity alongside upstream fallback access checks and attempt deduplication |
| `litellm/router_utils/fallback_event_handlers.py` | Custom reconciliation combines profile isolation and immutable identity with upstream authorization, provider-resource pinning, cooldown, and cycle prevention |
| `tests/e2e/proxy_client.py` | Upstream typed E2E harness retained; missing key-info models restored in `tests/e2e/models.py`; E2E basedpyright passes |
| Responses bridge test | Fork/native-stream assertions restored and pass against upstream prefix-restoration implementation |
| Hosted-vLLM chat test | DeepSeek reasoning matrix restored and passes against retained `reasoning_policy.py` |
| Hosted-vLLM Responses test | DeepSeek Responses reasoning matrix restored and passes |
| OpenAI Responses transformation test | Native ChatGPT stream/usage behavior regressions restored and pass |
| MCP admission auth test | LazyMCP challenge, audience, and credential-separation tests restored and pass |
| Gateway DCR test | Exact-resource code/refresh binding tests restored alongside upstream signing/introspection tests; pass |
| MCP server test | LazyMCP routes, catalog, toolset, permissions, probe compatibility, and short-name regressions restored; pass |
| Spend management test | Fork bounded/filter behavior tests restored; pass |
| Spend tracking test | NUL, poison isolation, and batching tests restored; pass |
| Responses streaming iterator test | Empty-output/completed-output and failure serialization regressions restored; pass |
| Fallback handler test | Custom combined implementation has restored cross-profile, spoof-resistance, dedup, authorization, and provider-resource tests; 62 pass |
| Secret-redaction test | Uvicorn access and hostile query redaction tests restored and pass |

## Reopen 2: Proxy-Root LazyMCP Routes

| Requirement | Resolution and proof |
| --- | --- |
| Root/scoped/toolset public routes | Added a dedicated lazily loaded router for `/lazymcp`, `/lazymcp/{scope}`, and `/toolset/{name}/lazymcp`, including trailing-slash aliases; direct route tests pass |
| Public path identity | Every route copies the request scope, retains the exact public value in `_original_path`, and rewrites only the internal `path`; six direct root/scoped/toolset alias assertions pass |
| Admission before toolset DB resolution | Toolset-name context is bound before forwarding and resolved by `_prepare_mcp_request_context` only after `extract_mcp_auth_context`; ordering regression passes |
| Scoped fallback and exact 404 | A scoped name resolves in order as server, toolset, then cached access group. Unknown names return exact 404 without broadening to all allowed servers |
| Safe failure conversion | Unexpected route or LazyMCP handler errors return a generic 500 without exception details; HTTP exceptions preserve their status and headers |
| Lazy loading | `_lazy_features.py` claims only proxy-root LazyMCP families, excludes `/mcp/lazymcp`, and registers the router on first matching request; registry tests pass |

## Reopen 3: Discovery Ownership

| Requirement | Resolution and proof |
| --- | --- |
| Sole discovery owner | `mcp_discoverable` is registered before lazy transport routes and is the only lazy matcher for all six canonical/alternate LazyMCP protected-resource paths |
| Exact transport matching | `lazymcp_routes` now matches only root, one scoped segment, or toolset transport, each with one optional trailing slash; every `/.well-known/` and deeper shape is rejected |
| Discovery precedence | Protected-resource routes are ordered before generic `/{server}/authorize` and other side-effect routes, preventing dynamic paths from consuming canonical or alternate metadata requests |
| OpenAPI ownership | The LazyMCP transport fragment contains no protected-resource route. All six root/scoped/toolset metadata paths remain in `mcp_discoverable` with authoritative operation IDs |
| Cold-start runtime | Six real proxy TestClient cases cover canonical and alternate root/scoped/toolset metadata, exact `resource`, exact authorization server, and prove the transport loader does not claim discovery |
