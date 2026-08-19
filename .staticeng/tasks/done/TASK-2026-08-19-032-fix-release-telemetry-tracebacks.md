---
id: TASK-2026-08-19-032-fix-release-telemetry-tracebacks
complexity: standard
track: implementation
slice: logic
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-030-verify-cross-host-stream-safe-198
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-032 - Fix Release Telemetry Tracebacks

## Objective
Fix the two shared 1.98.0 source defects causing successful Responses telemetry tracebacks and periodic Redis cache poller NameErrors, with focused regression coverage.

## Scope
- Synchronize effective returned-stream state into `logging_obj.stream` and `logging_obj.model_call_details["stream"]` in sync/async Responses handlers.
- Restore the complete `_init_cache` Redis usage-cache/auth-cache contract in `litellm/proxy/proxy_server.py`.
- Extend only mapped existing tests for HTTP handler logging, terminal Responses success payload, proxy cache initialization, Redis auth cache flag, and cache settings poller.
- Do not build/deploy, edit hosts, change configuration/database/models, or move tags.

## Acceptance Criteria
- [ ] AC-1: Sync/async provider-forced native streaming updates logging state to effective stream behavior without altering client/provider semantics.
- [ ] AC-2: Terminal `ResponseCompletedEvent` produces a non-null standard logging payload for success callbacks.
- [ ] AC-3: `_init_cache` accepts/restores the auth-cache flag, initializes/resolves usage cache safely, attaches it, and returns it without undefined references.
- [ ] AC-4: Existing environment/backend/fallback and poller behavior remain covered; non-Redis paths are unchanged.
- [ ] AC-5: Focused mapped suites, targeted lint/format/type/compile/diff checks pass with no failures/skips.
- [ ] AC-6: Evidence packet maps all ACs and records replacement-image requirement.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-032-fix-release-telemetry-tracebacks/` with `SUMMARY.md` and complete logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Implement the two diagnosed source corrections with focused existing-file regressions. Do not build/deploy/edit hosts or commit. Return AC-mapped evidence and replacement-image impact.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1 through AC-6 passed with 81 tests and targeted checks green.
- Both hosts require a replacement image.

## Tech Lead: Post Implementation Expectations
- Independent review approved commit and replacement-image build.
- 14 focused tests, source Ruff, and diff checks passed with no failures/skips.

## PMA Final Closure
- Authorized for direct-path commit.
- No product or architecture documentation update required.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1 through AC-6 passed with evidence under `.staticeng/evidences/TASK-2026-08-19-032-fix-release-telemetry-tracebacks/`
- Sync and async Responses handlers now persist effective returned-stream state for terminal success telemetry
- `_init_cache` again resolves, attaches, and returns the usage cache while honoring the Redis auth-cache flag and safe fallback behavior
- Final mapped tests completed with 81 passes and no skips; targeted lint, format, delta-aware type, compile, and diff checks passed
- Product and architecture documentation are unchanged because this restores approved behavior and an existing technical contract
- `staticeng_validate` remains blocked by pre-existing repository-wide CodeMap debt; repair dry-run would create hundreds of unrelated files and was not applied under this task's exact-scope constraint
- Both hosts require one replacement image containing these shared source corrections before stable promotion
- No build, deployment, host edit, configuration/database/model change, tag move, or commit was performed
