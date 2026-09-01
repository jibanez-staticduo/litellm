---
id: TASK-2026-08-28-009-define-resilient-lazymcp-discovery
complexity: standard
track: spec
slice: foundation
status: active
scr: SCR-2026-08-28-001-resilient-lazymcp-discovery
parent: TASK-2026-08-26-022-diagnose-lazymcp-log-errors
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: Define resilient LazyMCP discovery behavior

## Objective

Create and drive approval-ready shared requirements for resilient LazyMCP discovery after the verified 27-server/149-tool regression. Define per-server isolation, classified failure outcomes, degraded-cache behavior, bounded timeout/concurrency behavior, redaction, and individual server disposition reporting without changing runtime code or deployments.

## Classification

- complexity: standard
- track: spec
- slice: foundation

## Acceptance Criteria

- [ ] AC-1: Create `SCR-2026-08-28-001-resilient-lazymcp-discovery` with the observed baseline, user-visible behavior, non-goals, rollback expectations, and numbered acceptance criteria.
- [ ] AC-2: Require one broken, slow, unauthorized, or unavailable MCP server not to prevent healthy sibling listings.
- [ ] AC-3: Define stable classified outcomes for timeout, authentication, permission, connectivity/external dependency, protocol/version, configuration, adapter/internal error, optional/disabled, and recovered states without leaking secrets.
- [ ] AC-4: Define cache and retry semantics that do not preserve broad transient false negatives while retaining bounded resource use and isolation.
- [ ] AC-5: Require before/after per-server counts and one final disposition per affected server: recovered, optional/disabled, blocked by authentication, or blocked by external dependency.
- [ ] AC-6: Require focused and regression tests with no skips/failures, independent review, immutable commit-attributable image publication, identical digest deployment to Fedora and NAS, bounded post-deploy observation, and documented rollback.
- [ ] AC-7: State whether steady-state product/technical documentation must change and identify the source-of-truth document.

## Expected Evidence

- SCR under `.staticeng/docs/scrs/` with no secrets or sensitive payloads.
- Signed handoff tracing AC-1 through AC-7 to document sections.
- No source, runtime, credential, image, or deployment mutation.

## Handoff

[Agent Message] From: product_manager To: business_analyst

Use the explorer handback recorded in the parent task and inspect governing docs plus relevant existing SCR conventions. Produce the smallest approval-ready behavior contract. Preserve unrelated dirty changes and all CodeMaps. Do not implement, test, restart, reauthenticate, build, publish, deploy, or expose secrets. Return the shared output contract with exact file references.
