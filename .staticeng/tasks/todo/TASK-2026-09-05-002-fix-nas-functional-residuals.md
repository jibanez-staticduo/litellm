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
- AC-6: Reproduce and eliminate active spend-sanitizer recursion on cyclic/deep values; preserve normal spend fields, shared-graph handling and callbacks without serializing arbitrary runtime state. Verify the exact correction Fedora first, then NAS, with real public calls and bounded resource/log observation

## Reopen History

2026-09-05: PMA resumed the same task for the real NAS spend-log RecursionError, explicitly classified as product logging rather than security/tooling work. Fresh bounded five-minute NAS logs contain 148 RecursionError lines in _sanitize_request_body_for_spend_logs_payload/_sanitize_value. Existing functional deployments and corrected startup wrappers must remain intact until a verified source fix is built. Inspect the missing OAuth discovery helper only for supported-flow impact; do not conceal external auth-required peers

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

### Runtime startup continuation

PMA explicitly classified the mounted wrapper stall as a runtime deployment defect and authorized the minimal backed-up startup correction, retaining the selected candidate and host-specific functionality. Fedora's wrapper installed postgresql-client only for a legacy source_url column repair. Read-only schema checks confirmed this column already exists on both hosts; psql itself is absent from the candidate. The stalled apk was noninteractive and sleeping in a poll wait. The obsolete dependency and repeated DDL repair were removed, while Fedora's separate guarded synthetic Responses health patch was preserved byte-for-byte. Both wrappers now exec the image's normal prod_entrypoint.sh

Fedora then passed actual Astra reload/Chat/Responses, aggregate listing with truthful partial outcomes and a healthy real tool, followed by 900.01 seconds with 31/31 readiness checks and no memory-limit/OOM event. Only after this pass was the same digest promoted to NAS. Its own schema/bootstrap compatibility was checked, original wrapper and configuration backed up, obsolete DB repair removed and only LiteLLM recreated. NAS retains 38 model deployments and 27 MCP registrations with matching before/after alias and server-ID digests

NAS passes actual Astra Chat and Responses JSON/stream after manual price reload, aggregate initialize/list with 487 tools and 24 successful peers despite all three Frigate registrations timing out, and the real memory-health tool. Fresh bounded TCP tests confirm Frigate remains unreachable. NAS completed 900.00 seconds with 31/31 readiness checks and no memory-limit/OOM event. Final uncached-prompt checks passed on both hosts through loopback and public URLs; Fedora was rechecked after NAS soak

Both hosts remain on digest 4800816a96e35e7e87549e23823b0627148b6dfe2ac3cb7b55dab345dede1258, source 2dee9cd19e329d5c59eb712b8f27b8205ca0ff02, running/healthy with zero restarts/OOM and persistent 8-GiB/no-swap/restart-disabled containment. The bounded resource windows passed but memory was not flat; retain measured growth in final evidence rather than claiming indefinite leak-free operation. Task is ready for PMA acceptance/closure with external Frigate limitations explicitly retained

### Reopen 1 source expectations

Active recursion was confirmed by 148 NAS RecursionError lines in five minutes. Local deep dict/list and list-cycle regressions failed before correction. Sanitization now bounds depth at 32, tracks container identities, preserves typed response and normal spend fields, and nulls arbitrary runtime objects without inspecting or mutating callbacks. Supported RFC 9728 discovery actually reaches the missing OAuth helper; its existing guarded fetch path was restored at resource and issuer metadata sites rather than adding speculative OAuth behavior

All four mapped files pass in isolated Python processes: 951 tests total, no skips. Direct production/spend-test Ruff, all changed-file formatting and diff checks pass. A combined single-process run timed out and existing whole-manager-test lint findings remain disclosed. See logs/09-reopen1-source.md. Both existing functional deployments remain unchanged at this source checkpoint; build and Fedora-first/NAS live verification are still required

### Reopen 1 final expectations

Source 6ba4b3b366386e16364a6723c43319f4e52cc7a0 is committed/pushed and built from an exact clean archive using the unchanged Dockerfile. Both hosts now run the same index 0c8009530d20ca8a5306f38ff4f6aecb6e3261ded0c5e7336237033b6557717c. Fedora passed first, including its complete 900-second observation, then NAS passed and Fedora was rechecked. Corrected startup wrappers, all nonselector config/environment and containment are preserved

The active NAS recursion is resolved in the observed workload: 148 errors in five minutes before versus zero since candidate startup through the complete soak and final public reruns. Both installed-image synthetic deep/cycle/callback checks pass. The final ten-minute NAS spend aggregate contains 169 rows, 28 with token counts and 24 with structured response fields. Both public Astra reload/Chat/Responses and MCP healthy-tool/partial-availability checks pass; Frigate remains externally unreachable and auth-required peers remain visible

Both containers are running/healthy, zero restarts/OOM, 8-GiB/no-swap/restart-disabled. Each renewed observation passed 31/31 readiness samples across 900 seconds with no memory-limit/OOM event. Finite-window memory growth and ordinary client/provider failures remain disclosed; no indefinite leak-free or all-traffic claim is made. AC-6 and renewed AC-1 through AC-5 verification are recorded in logs/10-reopen1-dual-host-pass.md and logs/11-reopen1-resource-samples.csv. Ready for PMA final closure
