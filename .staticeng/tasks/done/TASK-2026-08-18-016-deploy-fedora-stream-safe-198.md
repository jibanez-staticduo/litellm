---
id: TASK-2026-08-18-016-deploy-fedora-stream-safe-198
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-010-design-stream-safe-198-release
assigned_to: developer
handoff_from: product_manager
reopened_count: 3
---

# Task: TASK-2026-08-18-016 - Deploy Fedora Stream-Safe 1.98.0

## Objective
Deploy the independently approved immutable candidate to Fedora only as a canary, preserving its two-account topology and all unrelated state, then execute the full release gate.

## Safety
- NAS must remain untouched.
- Re-capture Fedora baseline and verify rollback reference before mutation.
- Change only Fedora's LiteLLM image selector to `docker.staticduo.com/litellm@sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`.
- Recreate only `litellm` with `--no-deps`; do not restore DB, edit models/routing/credentials, or recreate dependencies.
- Roll back immediately on any mandatory gate failure.

## Acceptance Criteria
- [ ] AC-1: Re-capture and match Fedora inventory, routing/topology, protected hashes, dependencies, health, and rollback baseline before deployment.
- [ ] AC-2: Fedora runs the pinned candidate digest/version/revision with only the LiteLLM service recreated; dependencies and unrelated services remain unchanged.
- [ ] AC-3: Health/readiness/liveliness pass, restart count remains stable, `OOM=false`, and startup/observation logs contain no release-blocking errors.
- [ ] AC-4: Exact inventory and two-account topology/fallback/isolation hashes match preflight; no auth flow is triggered.
- [ ] AC-5: Known-valid native Responses request with client `stream=false` passes without `Stream must be set to true` and proves native streaming lifecycle.
- [ ] AC-6: Bounded Codex-compatible request, LazyMCP status/describe/tool-list smoke, and regular/account2 isolation checks pass.
- [ ] AC-7: Evidence packet maps every gate and records rollback readiness; stable tag and NAS remain unchanged.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-18-016-deploy-fedora-stream-safe-198/` with `SUMMARY.md` and sanitized logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Deploy only Fedora by the approved digest and execute every mandatory gate. Preserve topology and dependencies. Roll back on any failure. Keep NAS and stable untouched. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Fresh Fedora preflight and rollback readiness passed before mutation
- The exact candidate digest was deployed only to Fedora by changing `LITELLM_IMAGE` and recreating only `litellm` with `--no-deps`
- Candidate identity, health, preservation, topology, and native Responses lifecycle gates passed
- The mandatory regular-profile Codex-compatible probe returned HTTP 400 without `Stream must be set to true`
- The global stop rule was applied immediately; LazyMCP and account2 gates were not run after failure
- Fedora was restored to digest `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9` and the complete health, inventory, routing, protected-file, dependency, and auth-metadata baseline matches
- Stable remains unchanged and NAS was untouched
- No commit was created

## Reopen History

### Reopen 1 - 2026-08-18
- The failed canary selected unsupported `chatgpt/gpt-5.3-codex`; Tech Lead established invalid probe construction, not a candidate defect.
- Retry with regular `chatgpt/gpt-5.6-sol` and account2 `chatgpt-account2/gpt-5.6-sol`.
- Use list-form input, native `stream=true`, `store=false`, encrypted reasoning inclusion, `parallel_tool_calls=false`, and the Codex Responses Lite header.
- Require HTTP 200 SSE through `response.completed`, correct profile selection, and no stream/auth/unsupported-model errors before continuing LazyMCP and isolation gates.

### Reopen 2 - 2026-08-18
- Tech Lead confirmed the Fedora default regular Pro profile is provider-quota-bound at 100 percent usage with no defensible reset timestamp; account2 remains independently authenticated and usable.
- User explicitly requires both releases completed and functional without further questions.
- PMA authorizes release validation through the configured production fallback path without changing topology: qualified regular may return provider 429, but the unqualified public `gpt-5.6-sol` alias must complete HTTP 200 via existing account2 fallback, and direct account2 must complete HTTP 200.
- This does not replace or reorder the default profile; it proves the public route remains functional during temporary primary quota exhaustion.
- Require no `Stream must be set to true`, no auth/device flow, correct fallback/profile evidence, LazyMCP pass, full preservation, observation, and clean logs.

### Reopen 3 - 2026-08-18
- Tech Lead proved Reopen 2 omitted required Codex Lite `reasoning.context: all_turns`; account2 rejected the malformed request with `unsupported_value` and public fallback preserved the original quota 429.
- Retry corrected direct account2 first, then public fallback, with reasoning context `all_turns`, effort `high`, and summary `detailed` plus all prior Codex Lite fields.
- Candidate code, routing, and both auth profiles were independently excluded as causes.

## Developer: Reopen 3 Final Result
- AC-1 through AC-7 passed.
- Fedora runs immutable candidate `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b` healthy on LiteLLM 1.98.0.
- Direct account2 and public fallback completed HTTP 200 native SSE with correct profile selection and no stream-required/auth errors.
- LazyMCP, isolation, exact preservation, 60-second observation, and clean-log gates passed.
- Regular profile remains quota-bound; public availability is maintained by the preserved account2 fallback without topology changes.
- NAS and stable remained untouched.

## PMA Final Closure
- Fedora canary accepted after three same-scope reopen corrections to test construction.
- No steady-state product documentation update is required.

## Developer: Reopen 1 Results

- Re-captured the complete Fedora baseline and verified candidate, rollback, and stable registry digests before mutation
- Redeployed only Fedora LiteLLM using the same immutable candidate and `up -d --no-deps litellm`
- Candidate identity, package version, revision, architecture, health, readiness, liveliness, restart, and OOM gates passed
- Sent exactly one no-retry corrected regular-profile request to `chatgpt/gpt-5.6-sol` with all Tech Lead-approved fields and header
- The corrected regular-profile request returned HTTP 429 without stream-required, unsupported-model, authentication, or device-flow errors
- Applied the mandatory stop rule before account2 and LazyMCP checks and immediately rolled Fedora back
- Restored and re-verified the exact inventory, routing, topology, protected files, auth metadata, dependencies, health, and prior digest
- Stable remained unchanged, NAS was untouched, and no commit was created

## Developer: Reopen 2 Results

- Re-captured and matched the complete Fedora baseline and re-verified candidate, rollback, and stable registry digests
- Redeployed only Fedora LiteLLM using the same immutable candidate and `up -d --no-deps litellm`
- Candidate identity, package version, revision, architecture, health, readiness, liveliness, restart, and OOM gates passed
- The qualified regular `chatgpt/gpt-5.6-sol` request returned the explicitly permitted documented quota HTTP 429 without stream, auth, device-flow, or unsupported-model errors
- The mandatory unqualified public `gpt-5.6-sol` request returned HTTP 429 instead of HTTP 200 through account2 fallback
- The mandatory direct `chatgpt-account2/gpt-5.6-sol` request returned non-quota HTTP 400 without stream, auth, device-flow, or unsupported-model errors
- Applied the stop rule immediately after the non-quota failure; LazyMCP and stable observation were not run
- Restored and re-verified the exact inventory, routing, topology, protected files, auth metadata, dependencies, health, and prior digest
- Stable remained unchanged, NAS was untouched, and no commit was created

## Developer: Reopen 3 Results

- Re-captured and matched the complete Fedora baseline and re-verified candidate, rollback, and stable registry digests
- Redeployed only Fedora LiteLLM using the same immutable candidate and `up -d --no-deps litellm`
- Candidate identity, package version, revision, architecture, health, readiness, liveliness, restart, and OOM gates passed
- Corrected direct `chatgpt-account2/gpt-5.6-sol` completed HTTP 200 SSE through exactly one `response.completed` and selected only its expected deployment
- Corrected public `gpt-5.6-sol` completed HTTP 200 SSE through exactly one `response.completed` and selected the expected account2 fallback deployment
- Both requests used reasoning context `all_turns`, effort `high`, summary `detailed`, list input, native streaming, store false, encrypted reasoning inclusion, disabled parallel tool calls, and the Codex Responses Lite header
- LazyMCP status, describe, and tool-list smoke passed using the Fedora streamable HTTP endpoint
- Exact inventory, routing, topology, protected files, auth metadata, dependencies, health, 60-second observation, and clean-log gates passed
- Fedora remains healthy on the candidate digest with rollback readiness retained
- Stable remained unchanged, NAS was untouched, and no commit was created
