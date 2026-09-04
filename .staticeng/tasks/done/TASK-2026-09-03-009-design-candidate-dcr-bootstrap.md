---
id: TASK-2026-09-03-009-design-candidate-dcr-bootstrap
complexity: standard
track: investigation
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Design candidate DCR bootstrap

## Objective

Define a safe maintenance-window sequence that deploys the exact candidate under armed rollback, completes its supported DCR flow, and immediately executes the single bounded diagnostic tool request without requiring the rollback runtime to mint an unsupported credential.

## Acceptance Criteria

- [x] AC-1: Map exact candidate DCR endpoints/PKCE flow and existing-principal authorization mechanism without exposing credentials.
- [x] AC-2: Define deployment, health gate, DCR mint, cross-audience proof, immediate reproduction, token destruction, and rollback timing.
- [x] AC-3: Ensure watchdog remains armed before deployment and covers mint plus request, with safe memory thresholds and no circular prerequisite.
- [x] AC-4: Define fallback if interactive authorization cannot complete within a bounded pre-reproduction interval.
- [x] AC-5: Update task/evidence with signed execution handoff; no mutation.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Read TASK-006/007/008 evidence and DCR implementation/tests. The rollback image cannot mint candidate-only DCR tokens. Design the supported candidate-live bootstrap under the already authorized four-hour maintenance window: watcher armed first, deploy candidate, complete S256 PKCE with existing authorized principal, store token owner-only,, prove audience, immediately call once, destroy token, then continue/rollback. Research only; no deploy/auth flow/secret/source/host mutation.

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

### Summary

PASS. The supported bootstrap is candidate-live and fail-closed. TASK-007's independent rollback watchdog is armed before deployment, the frozen candidate starts without a bearer prerequisite, and only then does the operator complete public DCR plus S256 PKCE with the existing authorized LiteLLM principal. The exact-resource bearer is audience-proven, used immediately for the one diagnostic call, then destroyed with refresh revocation

### Work Performed

- Read prior TASK-006/007/008 and release evidence, the amended SCR, architecture contract, CodeMaps, DCR and admission source, dashboard consent UI, and focused tests
- Mapped exact discovery, registration, authorization, consent completion, token, revocation, and transport routes and their security bindings
- Defined owner-only Fedora tmpfs handling, browser-to-host manual code delivery, serial audience proofs, immediate one-call reproduction, unconditional cleanup, and a T+7-minute rollback cutoff
- Preserved TASK-007's exact image identities, one-second watcher, stop thresholds, request contract, maintenance clock, verification, soak, and rollback rules
- Performed no runtime, auth, host, source, config, database, container, registry, Git ref, or NAS mutation and accessed no secret material

### Acceptance Criteria Coverage

- **AC-1: PASS.** Evidence maps the exact endpoints, public client, S256 verifier/challenge, existing UI-session principal, deliberate consent, manual delivery, exact-resource redemption, and live user revalidation
- **AC-2: PASS.** Evidence orders deployment, health, DCR, positive and cross-audience proof, immediate reproduction, revocation, destruction, and rollback with monotonic cutoffs
- **AC-3: PASS.** The watchdog is armed before deployment and remains active through mint, proof, request, settlement, cleanup, and rollback. The bearer is a post-deployment artifact, removing the circular prerequisite
- **AC-4: PASS.** No credential substitution is allowed. Failure to complete and prove the bearer by T+7 minutes triggers artifact destruction and exact rollback without a reproduction
- **AC-5: PASS.** Task and evidence include signed execution handoffs; research performed no forbidden mutation

### Documentation Impact

No steady-state product, architecture, technical, or CodeMap update is required. The existing architecture contract remains authoritative; this task adds only one-time operational composition evidence

### Open Risks

- Candidate memory behavior remains unsafe without the already armed watchdog
- Interactive completion depends on the existing authorized principal and current browser session; the runbook does not permit identity or grant repair
- `/revoke` burns refresh tokens only. Access-token invalidation remains expiry, live principal deactivation, and immediate owner-only unlink
- A successful one-call result does not satisfy release qualification without root cause, full gates, and the 900-second soak

### Recommended Next Step

PMA should hand `logs/01-candidate-live-dcr-bootstrap.md` to Tech Lead and reopen TASK-006 only for one fresh protected attempt under the existing maintenance amendment

### Signed Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-009 PASS. Arm TASK-007's independent watchdog and rollback before deploying the exact candidate. After bounded healthy startup, use candidate discovery and root `/register`, `/authorize`, `/authorize/complete`, and `/token` with S256 PKCE, exact toolset resource binding, the existing authorized principal, manual loopback delivery, and owner-only Fedora tmpfs. Prove matching toolset admission and rejection at aggregate LazyMCP, one distinct scope, and `/mcp`, then immediately send the single 75-second diagnostic call. Revoke refresh, destroy every OAuth artifact, and continue TASK-006 only after absence is verified. If the audience-proven bearer is not ready by T+7 minutes or any gate fails, destroy and roll back without a legacy key, alternate principal, or request. Research made no deploy, auth, host, source, config, database, container, registry, Git ref, or NAS mutation
