---
id: TASK-2026-09-05-002-fix-nas-functional-residuals
complexity: complex
track: implementation
slice: logic
status: active
assigned_to: tech_lead
handoff_from: product_manager
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-004-deploy-lazymcp-oauth-nas
---

# Fix NAS functional residuals

## Scope

Both hosts are healthy on image 7b2368711ff10db3107772d627e03aa89319598f8897ff7431497775926b2eb9. NAS Astra Chat receives 429 while Astra Responses works, and unscoped `/mcp` initialize times out with three unhealthy Frigate MCP registrations. User wants both LiteLLM functional, not security/tooling fixes.

## Acceptance criteria

- AC-1: Identify exact Astra Chat cooldown/deployment failure source vs public Responses path. Correct only proven product/config defect; preserve profile fallback and do not bypass provider limits or invent availability.
- AC-2: Diagnose aggregate MCP timeout; ensure healthy-server tools remain available despite unavailable registrations through existing intended bounded behavior. Do not silently delete/disable registrations. If product fan-out blocks indefinitely, fix with regression tests and preserve access controls.
- AC-3: Validate actual NAS Astra Chat and aggregate MCP or precisely establish external dependency limitation; distinguish real provider unavailability from router state bug.
- AC-4: If source changes, test/review/build then Fedora first and NAS only after renewed Fedora validation. Preserve both running services where possible, all host-specific data/config and containment.
- AC-5: Evidence under `.staticeng/evidences/TASK-2026-09-05-002-fix-nas-functional-residuals/` with SUMMARY.md and logs, numbered coverage. No secrets. No security or harness refactors.

[Agent Message] From: product_manager To: developer

Only implementation owner; previous deployment TL is paused. Inspect current state and task parent evidence. Use bounded read-only diagnosis first and implement minimal proven fixes with focused tests. Do not mask failing registrations, bypass limits, or wipe router/DB state. No commit/push or source-image redeploy until Tech Lead review. Configuration changes through supported APIs may be made only if clearly required and recoverable; record exact impact without secret values. Return root cause/fix and verification, not generic hardening blockers.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

Two scoped source fixes implemented: replay metadata for routers constructed without a model list, and cap optional MCP initialize metadata setup/session by the existing metadata timeout. No runtime config, integration, image, commit or push changed. Evidence: .staticeng/evidences/TASK-2026-09-05-002-fix-nas-functional-residuals/SUMMARY.md

289 mapped router/MCP-server tests pass with no skips. Broader manager validation exposed an OAuth-discovery assertion failure outside the changed instruction-prefetch path; task remains active pending technical disposition, build and review. Do not close or deploy without renewed Fedora-first verification. Frigate TCP reachability remains an external dependency issue

Final focused verification: 297 passed with no skips. A follow-up actual aggregate REST listing exceeded 40 seconds, so the initialize fix alone does not satisfy AC-2. Developer requested Tech Lead guidance through PMA on the full aggregate listing deadline and broader test failure. No completion or build/release approval is claimed

## Tech Lead: Post Implementation Expectations

PMA transferred sole implementation ownership to Tech Lead for the same task. Added a per-peer aggregate deadline around complete setup, listing and permission filtering, using the existing MCP_TOOL_LISTING_TIMEOUT and AnyIO cancellation scopes. Six regression cases cover stuck headers, client creation and listing, healthy peer success, deadline classification, request cancellation and child drain. Scoped error paths and access controls remain unchanged

The two complete mapped router/server files pass 295 tests without skips. Production Ruff and test formatting pass. OAuth-discovery failure reproduces at clean baseline HEAD 1ac8bbeba0 in /tmp/opencode/litellm-residual-baseline: _fetch_oauth_metadata_from_resource calls an absent _fetch_oauth_discovery_url method. It is a pre-existing source failure, not introduced by these changes and not an unavailable Frigate network result. No OAuth repair or failing-test waiver is included

Including the relevant manager cache/interpolation classes, mapped verification totals 303 passed with no skips. Source 2dee9cd19e329d5c59eb712b8f27b8205ca0ff02 was committed and non-force pushed; the unchanged Dockerfile built and published digest 4800816a96e35e7e87549e23823b0627148b6dfe2ac3cb7b55dab345dede1258 from an exact git archive

Fedora alone was recreated on that digest, preserving selector backup/config and 8-GiB/no-swap/restart-disabled containment. Startup is held in the existing mounted wrapper's apk child before LiteLLM listens, running/unhealthy with zero restarts/OOM. No automatic rollback or wrapper repair was performed. PMA was notified. NAS remains unchanged and healthy; deployment, real Astra/MCP acceptance and both resource gates are not complete. Continue the same task at the Fedora bootstrap hold described in logs/05-build-fedora-startup-hold.md
