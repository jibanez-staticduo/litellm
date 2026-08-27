---
id: TASK-2026-08-27-002-investigate-spark-400
complexity: standard
track: investigation
slice: qa
status: done
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: TASK-2026-08-26-019-retire-obsolete-model-routes
assigned_to: explorer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-27-002 - Investigate Spark 400

## Objective
Determine why bounded NAS GPT-5.3 Codex Spark preflight requests return HTTP 400 and establish a correct non-mutating functional proof or a precise route blocker.

## Acceptance Criteria
- [ ] AC-1: Capture sanitized HTTP status/error type/parameter and request shape for both failed Spark probes without prompts, outputs, credentials, or account identities.
- [ ] AC-2: Compare endpoint/mode/wire schema against live deployment metadata, current ChatGPT Responses transformation, and known stream/store requirements.
- [ ] AC-3: Determine whether failure is probe misuse, unsupported parameter, authentication/account state, route/fallback defect, or model retirement.
- [ ] AC-4: Run the smallest corrected bounded status-only proof if safe; no configuration/route/account mutation.
- [ ] AC-5: Return exact gate recommendation for reopening Task 019.

## Expected Evidence
- Signed read-only diagnosis with redacted error classification and safe corrected probe.
