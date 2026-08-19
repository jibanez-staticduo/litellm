---
id: TASK-2026-08-19-031-diagnose-success-telemetry-tracebacks
complexity: standard
track: investigation
slice: logic
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-030-verify-cross-host-stream-safe-198
assigned_to: explorer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-031 - Diagnose Success Telemetry Tracebacks

## Objective
Identify the exact source, trigger, and minimum correction for repeated success-telemetry `NameError`/`ValueError` callback tracebacks on both 1.98.0 hosts.

## Safety
- Read-only investigation; do not edit source/runtime, deploy, restart, change callbacks/config/database, or move tags.
- Correlate sanitized logs from bounded successful probes; do not expose request/response content or credentials.

## Acceptance Criteria
- [ ] AC-1: Capture exact exception types/messages, callback names, source stacks, and affected request paths.
- [ ] AC-2: Determine whether both hosts share one source defect and reproduce it in a focused local test.
- [ ] AC-3: Identify exact source/test files and minimum behavior-preserving fix.
- [ ] AC-4: Return implementation and release impact, including whether a new image is required.

## Handoff
[Agent Message] From: product_manager To: explorer

Diagnose the repeated success-telemetry tracebacks read-only. Return exact source/tests and minimum fix, with no runtime or source mutation.

# Post Implementation Task Updates

## Explorer: Post Investigation Expectations
- AC-1 through AC-4 passed.
- Provider-forced native streaming was not synchronized into logging state, causing successful Responses callbacks to receive no standard logging object.
- `_init_cache` retained undefined variables after a partial revert, causing periodic Redis cache poller NameError tracebacks.
- Both source defects require one replacement image for both hosts.
