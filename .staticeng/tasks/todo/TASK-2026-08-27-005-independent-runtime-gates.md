---
id: TASK-2026-08-27-005-independent-runtime-gates
complexity: complex
track: investigation
slice: qa
status: active
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: TASK-2026-08-26-020-verify-client-model-contracts-020
assigned_to: tester
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-27-005 - Independent Runtime Gates

## Objective
Produce the missing independent fresh OpenCode, Codex, and Fedora runtime evidence required for final SCR closure without mutating state.

## Acceptance Criteria
- [x] AC-1: Fresh isolated official OpenCode 1.18.23 against current NAS/Fedora discovery captures complete retained selector/default/wire matrix for plugin 0.2.2 and audits scoped logs for stale/double-load errors.
- [x] AC-2: Fresh isolated Codex 0.149.1 captures all eight rows and every exposed Responses effort after Spark retirement, including ordered row-switch no-leak checks.
- [x] AC-3: Current Fedora host-local API and raw PostgreSQL read checks prove both GPT-5.3 families absent, dependencies/fallbacks absent, and access integrity.
- [x] AC-4: Bounded Fedora retired-alias probes prove unavailable without deployment identity, fallback, or redirect; no content retained.
- [x] AC-5: Evidence is independent of implementation task logs, read-only, redacted, complete, and suitable to reopen Task 020 closure.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-27-005-independent-runtime-gates/` with `SUMMARY.md` and redacted logs.

## Constraints
No config/cache/process/route mutation. Use isolated fresh processes and status-only loopback captures; no production response content retained.

# Post Implementation Task Updates

## Tester: Independent Findings

- Decision: PASS; no blocker found
- Fresh official OpenCode `1.18.23` plus installed plugin `0.2.2` passed current sanitized NAS and Fedora discovery matrices, exact selector/default/wire behavior, 21 deployed alias equivalence, retirement absence, and scoped single-load/no-stale-error checks
- Fresh isolated Codex `0.149.1` passed all eight rows, 40 every-mode Responses captures, eight ordered no-leak row switches, and production config/catalog/cache non-mutation checks
- Fedora authenticated read APIs, read-only PostgreSQL aggregates, access integrity, and eight retired normal/Spark aliases passed absence, dependency, unavailable, no-deployment, and no-redirect gates
- Evidence and signed findings-first handoff are in `.staticeng/evidences/TASK-2026-08-27-005-independent-runtime-gates/`
