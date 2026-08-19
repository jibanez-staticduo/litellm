---
id: TASK-2026-08-19-055-diagnose-local-codex-failure
complexity: standard
track: investigation
slice: qa
status: done
scr: null
parent: null
assigned_to: explorer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-055 - Diagnose Local Codex Failure

## Objective
Identify the current Codex failure on this NAS host by correlating recent local Codex/OpenCode session logs with LiteLLM request/router/provider logs, compare it to the prior Fedora fix, and define the minimum durable correction.

## Safety
- Read-only investigation; do not restart/recreate services, edit source/config/database/routing/auth, deploy images, or move tags.
- The screenshot is unavailable to the current model; rely on timestamp-correlated logs and session state.
- Never expose prompts, response bodies, credentials, tokens, cookies, or auth files.
- Preserve unrelated uncommitted Fedora StaticEng artifacts.

## Acceptance Criteria
- [ ] AC-1: Identify the failing Codex session/request timestamp, endpoint/model, HTTP/error category, selected deployment/profile, and fallback behavior from sanitized logs.
- [ ] AC-2: Correlate the client-side error with exact LiteLLM server/router/provider events.
- [ ] AC-3: Compare with previously fixed Fedora incidents and determine whether the cause is stream handling, payload shape, output assembly, quota/fallback routing, auth, or another regression.
- [ ] AC-4: Reproduce with at most one bounded no-retry sanitized probe if logs alone are insufficient.
- [ ] AC-5: Return exact source/config/runtime fix and tests/deployment impact, or prove no current server defect.

## Handoff
[Agent Message] From: product_manager To: explorer

Inspect recent local Codex/OpenCode session logs and NAS LiteLLM logs, especially the latest failure corresponding to the unavailable screenshot. Correlate timestamps and routing without exposing private content. Compare with historical Fedora fixes and return a decisive root cause and minimum durable correction. No mutation.

# Post Implementation Task Updates

## Explorer: Post Investigation Expectations
- AC-1 through AC-5 passed without a live probe.
- Public NPM upstream `litellm` resolves to both production and stale staging because both register the same Docker DNS alias on `npm_npm-net`.
- Production revision `8589869e1c` contains the stream fix and returned HTTP 200 SSE; stale staging revision `e7991580d2` lacks it and generated the observed HTTP 400 errors.
- No LiteLLM application-source change is required for this incident; production/staging network identity must be separated and staging upgraded or removed from public resolution.
