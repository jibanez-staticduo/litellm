# Fedora Account2 And Public Fallback Diagnosis

## Summary

The candidate and account2 authentication were not the cause of the failed gates. All three Reopen 2 requests carried the Codex Responses Lite header but omitted the required `reasoning.context: all_turns`. The account2 provider therefore returned deterministic HTTP 400 `invalid_request_error`, parameter `reasoning.context`, code `unsupported_value`. The public alias did execute its configured fallback after the regular profile returned its documented quota HTTP 429, but account2 rejected the same malformed request. LiteLLM then returned the original 429 with the account2 400 appended as fallback detail

## Work Performed

- Recovered the three exact candidate-time failure rows from retained spend-log metadata without exposing request content, credentials, or identifiers
- Recovered the direct account2 provider error category, parameter, code, and message
- Traced the public request from regular-profile quota exhaustion into the configured account2 fallback
- Read back the persistent router policy and fallback count without changing them
- Inspected only secret-safe auth metadata: both profiles remain readable Pro profiles with current tokens and matching account claims
- Inspected the candidate transformation and router exception path
- Ran an isolated no-network transformation using the corrected reasoning object and confirmed it is preserved with native streaming fields
- Sent no provider or inference requests and performed no deployment, restart, model, routing, auth, database, or tag mutation

## Root Cause

[Agent Message] From: tech_lead To: product_manager

The root cause is probe construction. The request used list input, `stream=true`, `store=false`, encrypted-reasoning inclusion, `parallel_tool_calls=false`, and `x-openai-internal-codex-responses-lite: true`, but it did not supply a reasoning object with `context: all_turns`. Account2 returned HTTP 400 `BadRequestError / ChatgptException`; the provider payload was `invalid_request_error`, parameter `reasoning.context`, code `unsupported_value`, with detail `X-OpenAI-Internal-Codex-Responses-Lite requires reasoning.context to be all_turns.`

The public `gpt-5.6-sol` route first reached the regular profile and received provider quota HTTP 429. It then selected configured fallback `chatgpt-account2/gpt-5.6-sol`, where the same request received the reasoning-context HTTP 400. LiteLLM intentionally re-raised the original primary exception after the fallback failed, which explains the client-facing public HTTP 429. The retained error detail contains the account2 fallback failure, so fallback absence or denial is excluded

Account2 authentication is also excluded: the provider accepted its bearer/account identity far enough to perform semantic request validation, and current read-only metadata shows a readable, current Pro token with a matching account claim. Candidate stream handling is excluded because the adapter forced and preserved `stream=true`; isolated transformation preserves the corrected reasoning object unchanged

## Minimum Safe Correction And Release Gate

Do not change code, routing, models, or authentication. Correct only the canary probe by adding:

```json
"reasoning": {
  "context": "all_turns",
  "effort": "high",
  "summary": "detailed"
}
```

Retain the existing list-form input, `stream=true`, `store=false`, `include=["reasoning.encrypted_content"]`, `parallel_tool_calls=false`, Codex Responses Lite header, and zero-retry bounds

The deterministic retry should test direct account2 first, then the public alias. Each must return HTTP 200 SSE through exactly one `response.completed`, with no failed/error event or stream/auth/model error. The direct gate must select account2. If the regular profile still returns the authorized quota response, the public gate must record initial regular selection followed by `chatgpt-account2/gpt-5.6-sol` and a successful fallback. All original LazyMCP, preservation, observation, log, rollback, NAS-isolation, and stable-tag gates remain mandatory

## Acceptance Criteria Coverage

- **AC-1: PASS**. Direct account2 was HTTP 400 `BadRequestError / ChatgptException`, provider type `invalid_request_error`, parameter `reasoning.context`, code `unsupported_value`. The exact missing requirement and request shape are recorded above
- **AC-2: PASS**. The public route reached regular, received quota HTTP 429, attempted configured account2, and account2 rejected the malformed request with the same HTTP 400. Router behavior then preserved the original 429
- **AC-3: PASS**. Probe construction is causal. Candidate stream code, fallback configuration, and account2 auth/provider availability are not causal
- **AC-4: PASS**. The minimum request-only correction and deterministic release assertions are defined without weakening functionality
- **AC-5: PASS, APPROVE WITH CORRECTED GATE**. Approve reactivation of the parent Fedora canary using the corrected reasoning object and every original stop/rollback condition. This is not approval for NAS deployment or stable promotion before the full Fedora gate passes

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. No steady-state behavior changed; this evidence and task update are the operational correction record

## Open Risks

- A canary retry is still required to prove live account2 completion and public fallback completion with the corrected request
- The existing transformation test for the Codex Responses Lite header does not model the provider-required reasoning context, but that gap did not cause candidate behavior to alter a valid Codex request
- `staticeng_validate` remains subject to the repository's pre-existing broken root links and broad missing CodeMap coverage

## Recommended Next Step

PMA should reactivate the parent Fedora task. The developer should change only the probe body, run direct account2 before the public fallback gate, and preserve all existing rollback and release boundaries
