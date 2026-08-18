# Fedora Regular-Profile HTTP 429 Diagnosis

## Summary

The corrected Fedora canary reached the intended regular `chatgpt/gpt-5.6-sol` deployment and failed with provider HTTP 429. A single read-only provider usage lookup against the same default profile returned HTTP 200 and classified the boundary as `rate_limit_reached`, detail `default`, with the primary window at 100 percent. The profile is a valid Pro account with a current token, so this is quota exhaustion rather than authentication, model support, stream handling, LiteLLM budget, or deployment health

The provider supplied neither `resets_at` nor `window_minutes` in the usage response. The failed canary harness did not retain `Retry-After`. There is therefore no defensible clock-time retry boundary. The safe boundary is state based: do not redeploy or spend another inference request until a read-only usage check for the default profile reports primary-window usage below 100 percent or supplies a reset timestamp that has passed

## Work Performed

- Read the task, approved SCR, parent task, parent summary, all twelve parent logs, prior profile evidence, repository guidance, and available CodeMap state
- Recovered the exact corrected request and its sanitized output from the originating OpenCode session: one qualified regular request, HTTP 429, with no stream-required, unsupported-model, authentication, or device-flow marker
- Verified restored Fedora remains on digest `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`, healthy, with zero restarts and `OOM=false`
- Inspected only auth metadata: default and account2 are separate Pro profiles with current tokens and matching account claims; no credential values were emitted
- Used the task's single essential bounded provider request as a read-only `GET /backend-api/wham/usage` for the default profile, not an inference request
- Read back routing locally without mutation: cross-profile policy remains enabled and exact bidirectional Sol fallback rules remain configured
- Sent no inference request, performed no authentication, and made no deployment, routing, model, credential, NAS, stable-tag, or service change
- Ran `git diff --check` successfully and reverified restored Fedora health and image identity

## Exact Sanitized Quota and Retry Boundary

- Failed gate time: 2026-08-18 22:20 UTC
- Requested group: qualified regular `chatgpt/gpt-5.6-sol`
- Profile: default regular profile, separate from account2
- Account metadata: Pro plan, token current, account claim matches the configured profile file
- Provider category: HTTP 429, `rate_limit_reached`
- Provider detail: `default`
- Primary-window utilization: 100 percent
- Credits: unavailable for overflow, `has_credits=false`, `unlimited=false`, balance `0`
- Provider reset metadata: `resets_at` absent and `window_minutes` absent
- Failed-response retry metadata: `Retry-After` was not retained by the parent harness
- Earliest safe retry: no fixed timestamp can be approved; retry only after a read-only default-profile usage check reports less than 100 percent or a supplied reset timestamp has passed

The runtime fallback topology was not disabled: cross-profile fallback is `true`, with regular Sol to account2 Sol and reverse rules present. The release gate nevertheless intentionally requires the qualified regular profile itself to pass and forbids account2 success from masking regular-profile exhaustion. The failed harness did not retain enough request-scoped provider logs to prove whether the router evaluated the configured fallback, so no stronger routing claim is made

## Acceptance Criteria Coverage

- **AC-1: PASS**. The error is provider `rate_limit_reached` on the default regular Pro profile at 100 percent primary-window usage. No reset/window value was supplied. The parent did not retain `Retry-After`. Runtime fallback stayed configured, while the qualified isolation gate intentionally disallowed fallback success as a waiver
- **AC-2: PASS WITH RECENT RETAINED FUNCTIONAL EVIDENCE**. Account2 is a separate configured Pro profile with a current token and matching account claim. Prior no-retry Fedora evidence returned HTTP 200 from `chatgpt-account2/gpt-5.6-sol` while the regular profile returned HTTP 429, without auth prompts or topology changes. No new account2 request was needed or sent
- **AC-3: PASS**. No clock-time retry is justified. The deterministic precondition is a read-only default-profile usage result below 100 percent or an explicit elapsed provider reset. This precondition does not waive the complete Fedora canary, including regular, account2, LazyMCP, isolation, observation, and clean-log gates
- **AC-4: PASS, BLOCK**. Block candidate redeployment, NAS deployment, and stable promotion pending default-profile quota recovery or an explicit user decision to replace the default profile while preserving qualified isolation

## Documentation Impact

No product, architecture, technical, or CodeMap documentation change is required. This investigation evidence is the operational record, and no steady-state behavior changed

## Open Risks

- The provider exposed no reset timestamp, so elapsed time alone cannot prove recovery
- The failed canary harness discarded the 429 body and response headers, which prevents retrospective recovery of a `Retry-After` value
- Account2's recent independent HTTP 200 does not satisfy or waive the regular-profile release gate
- `staticeng_validate` failed only on the repository's pre-existing broken root links and broad missing CodeMap coverage. The required repair dry run proposed hundreds of unrelated changes and was not applied

## Recommended Next Step

**BLOCK PENDING QUOTA RECOVERY**. PMA should not reopen the Fedora deployment task yet. Recheck the default profile with the same read-only usage endpoint after the user-visible quota state resets. Reopen only when usage is below 100 percent, then rerun the full Fedora canary without weakening profile isolation. If the user wants immediate progress, request an explicit decision to replace the default profile; do not silently route the qualified regular gate through account2
