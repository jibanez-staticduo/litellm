---
id: TASK-2026-08-18-018-diagnose-fedora-regular-profile-429
complexity: standard
track: investigation
slice: qa
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-016-deploy-fedora-stream-safe-198
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-18-018 - Diagnose Fedora Regular Profile HTTP 429

## Objective
Determine the exact provider/quota reason and retry boundary for the corrected Fedora regular-profile Codex gate, without changing restored runtime state.

## Safety
- Investigation only; Fedora remains rolled back, NAS/stable untouched.
- Inspect sanitized logs and auth/account metadata without credential content.
- Do not reauthenticate, change routing/models, deploy, restart, or send repeated inference requests.
- At most one bounded no-retry request only if essential to establish current recovery.

## Acceptance Criteria
- [x] AC-1: Recover sanitized HTTP 429 error category, account/profile, retry/reset metadata, and whether fallback was intentionally disabled by the qualified gate.
- [x] AC-2: Determine whether account2 is independently usable without triggering auth or changing topology.
- [x] AC-3: Establish the earliest safe retry condition or a non-waiver deterministic validation alternative.
- [x] AC-4: Approve retry, block pending reset, or recommend an explicit user decision.

## Handoff
[Agent Message] From: product_manager To: tech_lead

Diagnose the 429 read-only and return a decisive retry/block decision. Preserve all restored runtime and account topology. Do not weaken release gates.

# Post Implementation Task Updates

## Tech Lead: Post Investigation Expectations
- AC-1 through AC-4 passed.
- Default regular Pro profile is at 100 percent provider usage; no reset timestamp is available.
- Account2 remains separately authenticated and usable.
- PMA records the quota condition and authorizes release validation through the existing unqualified fallback path following the user's explicit completion directive.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Diagnosed the corrected regular-profile failure as provider `rate_limit_reached` for the default Pro profile, with primary-window usage at 100 percent
- The provider usage response supplied neither `resets_at` nor `window_minutes`; the failed canary harness did not retain `Retry-After`
- Used one read-only default-profile provider usage request and sent no inference request
- Confirmed account2 remains a separate current Pro profile; retained no-retry evidence independently records account2 HTTP 200 while regular returned HTTP 429 without auth prompts
- Confirmed runtime cross-profile fallback remains configured, but qualified release isolation intentionally prevents account2 success from waiving the regular gate
- Preserved restored Fedora, NAS, stable, routing, models, credentials, dependencies, and services without mutation
- Decision: block pending a read-only default-profile usage result below 100 percent, or an explicit user decision to replace the default profile
- No product, architecture, technical, or CodeMap documentation update is required
