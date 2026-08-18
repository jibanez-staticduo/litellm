# Fedora Codex Canary HTTP 400 Investigation

## Summary

The failed canary did not expose a candidate stream regression. The exact probe requested `chatgpt/gpt-5.3-codex`, which the ChatGPT account-backed Codex provider rejects because that model is unsupported. One bounded read-only reproduction against restored Fedora returned the same HTTP 400 detail across the regular and fallback account paths. The error did not contain `Stream must be set to true`

The candidate's earlier native Responses gate passed the complete SSE lifecycle. Source inspection and isolated transformation validation also show that the ChatGPT adapter converted the failed client request to provider-required `stream=true`, `store=false`, and `include=["reasoning.encrypted_content"]`, while removing unsupported `max_output_tokens`. The remaining invalid field was the model choice

## Work Performed

- Recovered the exact failed client request shape from the originating OpenCode command log
- Correlated the model with prior sanitized provider evidence and one bounded reproduction on restored Fedora
- Inspected the ChatGPT Responses transformation and ran it locally without network access
- Compared the probe with the structural request shape of real Codex session `01a00b76-b1cb-7ab1-a4a2-ef1f08a002ba`
- Defined a deterministic retry gate using the real Codex model family and native SSE assertions
- Performed no deployment, restart, tag movement, or host/config/model mutation

## Root Cause

The canary used a provider-invalid model, `chatgpt/gpt-5.3-codex`. The provider detail is: `The 'gpt-5.3-codex' model is not supported when using Codex with a ChatGPT account.` The same detail was returned on the configured account fallback path. This classifies the failure as invalid probe construction, specifically model selection, rather than candidate code, routing absence, provider availability, or stream handling

The client body itself used a list-form Responses input and was structurally accepted by LiteLLM. The adapter supplied the required ChatGPT fields and discarded `max_output_tokens`, so neither list-vs-string input nor that unsupported optional parameter caused this HTTP 400

## Known-Valid Retry Gate

Send one no-retry, bounded `/v1/responses` request to the regular qualified deployment `chatgpt/gpt-5.6-sol`, matching the model used by the real Codex session. Use a list-form message containing one `input_text`, `store=false`, `stream=true`, `include=["reasoning.encrypted_content"]`, `parallel_tool_calls=false`, and `x-openai-internal-codex-responses-lite: true`. Do not use any `gpt-5.3-codex` deployment

The gate passes only when all of these assertions hold:

1. HTTP status is 200 and content type is `text/event-stream`
2. The stream includes `response.created` or `response.in_progress`, then exactly one terminal `response.completed`
3. No `response.failed`, `error`, `Stream must be set to true`, authentication prompt, or unsupported-model detail appears
4. The selected deployment is the regular `chatgpt/gpt-5.6-sol` path with no cross-profile leakage
5. Health, restart count, OOM state, inventory, routing, and auth metadata remain unchanged after the request

Run the separately required account2 isolation check against `chatgpt-account2/gpt-5.6-sol`; it must select only that profile. A success on one profile must not waive the other isolation assertion

## Acceptance Criteria Coverage

- **AC-1: PASS**. The exact failed request shape and exact provider rejection were recovered and sanitized. The candidate-time client omitted the response body, so the detail was re-established with the task's single permitted bounded request against the restored runtime
- **AC-2: PASS**. Real Codex used Responses API model `gpt-5.6-sol`, native streaming, `store=false`, encrypted reasoning inclusion, list input, Codex tool/history item types, reasoning settings, and `parallel_tool_calls=false`. The failed probe instead selected unsupported `gpt-5.3-codex`. Historical evidence independently records the same unsupported-model rejection
- **AC-3: PASS**. Root cause is invalid probe model construction. Candidate stream code passed its native lifecycle gate; model routing existed and provider state was responsive enough to return a deterministic semantic rejection
- **AC-4: PASS**. The known-valid regular and account2 request shapes and success assertions are defined above
- **AC-5: PASS**. **APPROVE** reactivation of `TASK-2026-08-18-016-deploy-fedora-stream-safe-198`, conditioned on replacing the invalid model gate with the defined `gpt-5.6-sol` gate and rerunning every previously incomplete mandatory gate

## Documentation Impact

No steady-state product, architecture, or CodeMap update is required. This evidence and the task update are the technical record for the operational probe correction

## Open Risks

The candidate remains rolled back and has not been revalidated with the corrected gate. Approval to reactivate the parent task is not approval to promote stable or proceed to NAS. Any corrected Fedora gate failure still requires immediate rollback

`staticeng_validate` remains blocked by pre-existing broken root links and repository-wide missing CodeMaps. The required repair dry run proposed broad unrelated changes and was not applied

## Recommended Next Step

PMA should reactivate the original Fedora deployment task. The developer should redeploy only the already approved immutable candidate, use the known-valid gate above, complete LazyMCP and both profile-isolation checks, and retain the original rollback rules
