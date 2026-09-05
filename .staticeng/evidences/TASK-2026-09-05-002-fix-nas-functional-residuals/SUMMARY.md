# NAS functional residuals

Tech Lead continuation completes the three scoped source corrections with 303 passing mapped tests and no skips. The unrelated OAuth assertion is reproduced on clean baseline and remains an explicitly failing pre-existing product path, not an introduced regression. Build and Fedora-first rollout verification remain pending; no live fix PASS is claimed

## Root causes

Astra's four effective deployments retain `mode=responses`, but the running catalog lacks `chatgpt/gpt-6-astra`. The unprefixed entry belongs to OpenAI and is chat-mode. Consequently Chat misses the Responses bridge and reaches the Codex chat/completions endpoint, receiving an HTTP 403 browser challenge. Cooldown then reports no available deployments as HTTP 429. Native Responses succeeds through the configured profile fallback. This is not evidence of exhausted provider quota

NAS configuration enables DB model storage and has no top-level model_list. The proxy constructs Router without a model_list and adds DB deployments later. Such routers were absent from the weak set used to replay deployment metadata after price-map replacement. A focused regression reproduced loss of Responses mode after replay for Router(None), while Router([]) passed. Track both construction paths without retaining discarded routers

Aggregate MCP initialize waits for optional upstream instructions. NAS sets MCP_HEALTH_CHECK_TIMEOUT=30, equal to the observed 30-second gateway deadline, and MCP_CLIENT_TIMEOUT=180. Each Frigate registration currently fails a bounded TCP connection from the LiteLLM container. Optional metadata probes therefore exhaust the gateway deadline despite 24 healthy registrations. The fix bounds header/client resolution and initialization together by the smaller of the existing metadata and health timeouts, using the established AnyIO cancellation pattern. No registration or access control changes

## Acceptance criteria coverage

| Criterion | Status | Verification |
| --- | --- | --- |
| AC-1 | Source correction implemented; live correction pending | Live catalog/deployment mismatch, upstream error classification, successful Responses; router regression fails before and passes after |
| AC-2 | Source correction verified; live validation pending | Full per-peer aggregate setup/list/filter deadline; six timeout/caller-cancellation/drain regressions pass with healthy tools retained |
| AC-3 | Diagnosis complete; deployment verification pending | Running image remains unchanged, so no live fix PASS claimed; Frigate connectivity remains external |
| AC-4 | Review/release gate pending | No image rollout, commit or push; Fedora-first validation remains required |
| AC-5 | Evidence recorded | This summary and logs; no credentials or private payloads retained |

## Verification

Before source correction, focused regressions returned three failures and one pass: missing replay for Router(None), and both metadata timeout phases failed their one-second outer deadline. Router([]) was the passing control

After correction, the complete router cost-isolation and MCP server test files passed: 289 tests, no skips. An attempted broader run including the MCP manager file encountered unrelated OAuth-discovery failures and exceeded its 120-second command deadline. A bounded rerun stopped at TestOAuthDiscoverySSRFGuard.test_cross_origin_allowed_when_resolves_to_public_ip after 130 passes: expected authorization server, got an empty list. This failure is not waived or presented as a passing broad suite. No security or harness fix was attempted

Final mapped run including manager instruction-cache and environment-interpolation coverage: 297 passed, no skips, four warnings, 79.93 seconds. Production-file Ruff passed; both edited test files pass formatting; git diff --check and StaticEng validation passed. Whole-test-file Ruff also reports existing import-order findings and an unused variable outside this change; the new import-order issue was corrected. Package/image build has not been run because technical disposition and completion of aggregate listing remain pending

A later actual aggregate GET /mcp-rest/tools/list exceeded its 40.05-second client deadline. NAS uses the default MCP_TOOL_LISTING_TIMEOUT=30. The manager bounds client.list_tools but not the preceding full setup, and the aggregate awaits all peers. The instruction fix does not resolve this additional listing path. No partial-availability completion is claimed. PMA was asked to route Tech Lead guidance before broadening the timeout boundary

## Documentation impact

Technical availability invariants and relevant CodeMaps are updated. No advertised product feature or UI behavior is added, so product overview and screenshots are not required

## Open risks and next step

Tech Lead source continuation evidence is in logs/04-tech-lead-source-review.md. Build and Fedora-first live validation remain necessary before NAS rollout. On NAS verify Astra Chat JSON/stream, native Responses, persistence after normal price-map reload, aggregate MCP initialize/list with truthful partial outcomes, and real healthy tools. Frigate connectivity requires its service/network owner; it was not repaired or hidden here. The baseline OAuth method absence is not repaired by these scoped changes
