# NAS Account2 HTTP 429 Disposition

## Summary

**APPROVE one final NAS deployment under the exact non-waiver gate below.** Direct account2 HTTP 200 is not required. The only acceptable direct account2 alternative is HTTP 429 classified as external provider quota/rate limit, with correct qualified account2 selection and no auth, device-flow, payload, stream, unsupported-model, routing, or candidate error

This approves a final deployment attempt, not the currently rolled-back candidate as already promoted. Promotion is approved only after every assertion below passes on the candidate. No retained assertion may be skipped because account2 is quota-bound

## Classification

The direct account2 HTTP 429 is an external provider quota/rate-limit condition. Before the 1.98.0 attempt, the NAS 1.92.0 supported refresh succeeded for account2 and a bounded direct account2 Responses check returned the same HTTP 429 without an auth error. On the candidate, the identical proven request shape passed on the native and direct default paths with HTTP 200 and a complete SSE lifecycle. Candidate identity, health, topology, dependencies, mounts, networks, and credential gates also passed before the account2 request

That retained sequence excludes authentication, malformed payload, stream parsing, deployment routing, and the 1.98.0 candidate as causes. The evidence does not retain a narrower provider subtype, reset time, response body, or `Retry-After`, so none is asserted

## Exact Final Deployment Assertions

1. Run only immutable manifest `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`, config/image ID `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`, LiteLLM 1.98.0, revision `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`
2. Recreate only NAS `litellm` with `--no-deps`; preserve the tested rollback image and wrapper/Compose pair and make no model, routing, credential, database, dependency, or tag mutation
3. Pass fresh T0, corrected lock-file ctime handling, health, readiness, liveliness, zero restart/OOM, startup/schema/migration, dependency, mount, network, and clean-log gates
4. Preserve exactly 32 model rows, model hash `ba61d2feac5508f98652eaf154dbc7a5e6da6cf53f6d5f5a74cd0068230788e2`, inventory-pair hash `c1b02458b0870214482918880ce8c01735bee34e00fa01cd90d7981c225273d4`, 16 fallback rules with hash `d0841f275e4c4cdeafd89c4e8e24062438e70441edcb8a287974b8566b798262`, eight default-qualified deployments, eight account2-qualified deployments, and zero account3 deployments/references
5. Preserve all eight public GPT aliases with default as primary and account2 as the retained fallback. No reorder, substitution, quarantine, or silent routing waiver is allowed
6. Require the native client `stream=false` gate and direct default `chatgpt/gpt-5.6-sol` gate to return HTTP 200 `text/event-stream`, valid blank-line JSON SSE, ordered created/in-progress/completed lifecycle, one terminal completion, consistent ID and contiguous sequence, correct default selection, and zero forbidden errors
7. Run direct `chatgpt-account2/gpt-5.6-sol`. Accept either the same valid HTTP 200 SSE contract or HTTP 429 only when it is the provider quota/rate-limit category on the correctly selected account2 deployment with no auth/device, payload, stream, unsupported-model, routing, or candidate error. Do not use fallback success to satisfy this direct assertion
8. Require public `gpt-5.6-sol` to return HTTP 200 with the same valid SSE contract and correct default-primary selection. HTTP 429, fallback exhaustion, or account2 quota is not acceptable for the public gate
9. Require the full LazyMCP status, describe, tool-list, and harmless configured-tool smoke matrix to pass
10. Require the complete candidate observation and preservation gates to pass, including corrected credential metadata, zero auth/device-flow failures, exact protected hashes and dependency identities, and current Fedora/stable isolation. Roll back immediately on any failure

## Acceptance Criteria Coverage

- **AC-1: PASS**. Retained pre-candidate and candidate evidence classifies account2 HTTP 429 as provider quota/rate limit and excludes auth, payload, stream, routing, and candidate causes
- **AC-2: PASS**. Native and direct default candidate gates passed HTTP 200 SSE. The exact topology gate passed with public default primaries and account2 fallbacks preserved
- **AC-3: PASS**. Assertions 1-10 preserve every mandatory release and public-functionality gate while allowing only the narrow direct account2 quota result
- **AC-4: PASS, APPROVE**. Approve one final NAS deployment without requiring direct account2 HTTP 200. Promotion remains contingent on all assertions passing

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. This investigation records a transient provider quota disposition and release gate without changing steady-state behavior

## Open Risks

- Account2 may remain unavailable as a fallback until its provider quota resets; no defensible reset timestamp was retained
- Public functionality on 1.98.0, LazyMCP, and the candidate observation were not reached in the rolled-back attempt and remain mandatory in the final gate
- Repository StaticEng validation retains the parent task's pre-existing broken links and missing CodeMaps

## Recommended Next Step

PMA should authorize the final NAS deployment using assertions 1-10 verbatim. Approve promotion only after all pass; otherwise require immediate rollback and reject promotion
