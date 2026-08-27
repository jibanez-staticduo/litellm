# TASK-2026-08-27-003 Evidence Summary

## Summary

The supported upstream identifier has not been renamed: current official Codex documentation still names `gpt-5.3-codex-spark`. Spark is a text-only research preview available to ChatGPT Pro users through Codex CLI, IDE, and desktop, with no API access. It is therefore entitlement-specific rather than generally available

The observed provider-level `param=model` rejection does not establish model retirement. The exact rejection says the model is unsupported when `X-OpenAI-Internal-Codex-Responses-Lite` is used. Codex's upstream-derived cache marks Spark `use_responses_lite=false`, `supported_in_api=false`, text-only, and not supporting the reasoning-summary parameter. The local custom Codex catalog instead marks Spark `use_responses_lite=true`, `supported_in_api=true`, image-capable, and supplies unrelated modern-model metadata. That mismatch selects a transport OpenAI explicitly rejects for Spark

LiteLLM's ChatGPT provider correctly strips the `chatgpt/` namespace before sending the upstream model and targets `https://chatgpt.com/backend-api/codex/responses`. Its request transformation forces `stream=true`, `store=false`, and encrypted reasoning inclusion. The registered NAS routes also map both profile-qualified deployments to upstream `chatgpt/gpt-5.3-codex-spark`. No stale alias spelling or namespace error was found

## Architecture Decision

**REPAIR THROUGH A NEW SCR/TASK, WITH CONDITIONAL RETIREMENT.** Do not rename the upstream model and do not alter Task 019 directly. Correct the Spark custom Codex catalog contract to match the upstream catalog at minimum: standard Responses transport (`use_responses_lite=false`), text-only input, no API availability claim, no unsupported reasoning-summary claim, and no copied GPT-5.6 capability metadata. In the same bounded task, establish whether at least one registered ChatGPT profile has the documented Pro entitlement

If no registered profile produces a successful direct standard Codex-backend Responses lifecycle after the client metadata correction, approve an SCR scope change that retires Spark routes and client entries together. A provider `param=model` rejection on every registered profile is sufficient evidence that the deployment has no usable entitlement, even though the identifier remains officially valid for eligible users

## Direct Provider Gate

Exactly one upstream request was sent for an existing registered profile, directly to the Codex backend and outside LiteLLM router fallback. The request used the exact official identifier, list-form input, streaming, `store=false`, encrypted reasoning inclusion, `current_turn`, and a supported effort. No prompt, response, credential, account identifier, authorization material, or profile identity was retained

Result: HTTP 400, with no response body retained. This does not prove functional support and does not safely distinguish profile entitlement from a remaining request-contract mismatch. No second direct request is authorized by this task's one-request boundary

## Task 019 Unblock Condition

Task 019 may reopen only after one of these mutually exclusive gates is approved and evidenced:

1. **Retain Spark:** a separate correction task fixes the Spark custom catalog contract, then one direct request to a single exact qualified deployment, bypassing public-group fallback, reaches `response.completed` using `gpt-5.3-codex-spark`, list input, `stream=true`, `store=false`, encrypted reasoning inclusion, standard Responses transport, and no retained content. Task 019 must then repeat its pre-mutation Spark proof against the retained public route and verify the exact qualified deployment selected
2. **Retire Spark:** an approved SCR changes Task 019 and the parent product contract to remove Spark from LiteLLM routes, fallbacks, OpenCode contracts, and the custom Codex catalog. Task 019 must then replace every preserve-Spark acceptance gate with absence, no-redirect, dependency, and rollback gates

Discovery, official documentation, a catalog entry, or a provider 400 alone does not unblock Task 019 under the retain-Spark path

## Acceptance Criteria Coverage

- **AC-1: PASS.** Compared official Codex model documentation, installed Codex 0.149.1 behavior and upstream-derived cache, LiteLLM source and model metadata, registered route evidence, and the custom Codex catalog
- **AC-2: PASS.** Exact identifier remains valid; Responses Lite is a proven transformation/catalog mismatch; Pro entitlement is required and remains unproven for registered profiles; retirement is not established
- **AC-3: PASS WITH NEGATIVE RESULT.** One bounded direct request bypassed fallback and returned HTTP 400; no content was retained and functional support was not proven
- **AC-4: PASS.** Recommend a separate correction SCR/task with conditional Spark retirement; no route, account, configuration, or source mutation occurred
- **AC-5: PASS.** The two exact and mutually exclusive Task 019 unblock conditions are defined above

## Documentation Impact

No steady-state architecture document changes in this investigation. The current approved SCR remains inaccurate until either the proposed Spark correction SCR proves a functional entitled deployment or an approved scope change retires Spark

## Official Sources

- `https://developers.openai.com/codex/models.md`
- `https://developers.openai.com/codex/models`
- `https://github.com/openai/codex/blob/main/codex-rs/models-manager/src/manager.rs`
- `https://github.com/openai/codex/blob/main/codex-rs/protocol/src/openai_models.rs`

## Open Risks

- The local `models_cache.json` payload is upstream-derived but records client version 0.147.0 and an August 12 fetch time; installed runtime is 0.149.1. Official documentation independently confirms the same identifier, Pro restriction, surfaces, and lack of API access
- The direct request's HTTP 400 body was intentionally not retained, so the registered profile's entitlement cannot be conclusively classified
- LiteLLM static metadata currently claims vision support for Spark while official and Codex cache sources say text-only; that metadata defect belongs in the proposed correction task

## Validation

- `git diff --check`: PASS
- Evidence credential and profile-identity scan: PASS
- `staticeng_validate`: FAIL on pre-existing repository-wide missing CodeMaps outside this investigation scope
- `staticeng_repair` dry-run: no deterministic repair for the missing CodeMaps; resolving them requires unrelated module-boundary decisions, so no repair was applied
