---
id: TASK-2026-08-18-019-diagnose-fedora-account2-fallback
complexity: standard
track: investigation
slice: logic
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-016-deploy-fedora-stream-safe-198
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-18-019 - Diagnose Fedora Account2 And Fallback

## Objective
Find and resolve the exact fault boundary behind direct account2 HTTP 400 and the public alias failing to complete through configured fallback, while Fedora remains restored.

## Safety
- Investigation first; no deployment, restart, DB/config/model/auth mutation, or tag movement.
- Inspect exact sanitized error detail and routing/fallback configuration.
- Use isolated transformation/router checks and at most two bounded no-retry requests only if essential.
- Do not trigger device authentication.

## Acceptance Criteria
- [ ] AC-1: Recover exact direct account2 HTTP 400 category/detail and request shape.
- [ ] AC-2: Trace public alias fallback execution and explain why account2 did not produce a successful completion.
- [ ] AC-3: Determine whether the fault is probe construction, candidate code, account2 auth/provider state, or fallback configuration.
- [ ] AC-4: Define the minimum safe correction and deterministic release gate without weakening required functionality.
- [ ] AC-5: Approve a parent retry or create an explicit implementation requirement.

## Handoff
[Agent Message] From: product_manager To: tech_lead

Diagnose the direct account2 400 and failed public fallback read-only. The user requires completion without questions. Return the minimum actionable correction and retry decision.

# Post Implementation Task Updates

## Tech Lead: Post Investigation Expectations
- AC-1 through AC-4 passed; AC-5 approved parent retry.
- Missing `reasoning.context: all_turns` caused account2 HTTP 400; public fallback did execute but account2 rejected the same malformed request.
- Candidate code, routing, and auth profiles are not causal.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Recovered direct account2 HTTP 400 as provider `invalid_request_error`, parameter `reasoning.context`, code `unsupported_value`
- Confirmed the Codex Responses Lite probe omitted required `reasoning.context: all_turns`
- Confirmed the public alias reached regular quota HTTP 429 and then attempted account2, where the malformed request received the same HTTP 400
- Excluded candidate streaming, fallback configuration, and account2 authentication as causal boundaries
- Defined a request-only correction using the real Codex reasoning object with `context=all_turns`, `effort=high`, and `summary=detailed`
- Approved parent retry only with the corrected gate and all existing stop, rollback, preservation, LazyMCP, observation, NAS-isolation, and stable-tag requirements
- Sent no inference/provider requests and performed no deployment, restart, or state mutation
- Product documentation is not required because steady-state behavior did not change
