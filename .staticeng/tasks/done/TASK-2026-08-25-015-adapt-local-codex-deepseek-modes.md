---
id: TASK-2026-08-25-015-adapt-local-codex-deepseek-modes
complexity: standard
track: implementation
slice: core
status: done
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: null
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-015 - Adapt Local Codex DeepSeek Modes

## Objective
Configure Codex `0.147.0` on this host so the target DeepSeek model exposes and sends only semantic modes `off`, `low`, `high`, and `max`, with no `medium` or `xhigh` availability.

## Acceptance Criteria
- [x] AC-1: Capture protected backups, checksums, permissions, current catalog source/generation path, and exact rollback steps without secrets.
- [x] AC-2: Update the authoritative catalog source, or the local catalog if no generator exists, only for `deepseek-v4-flash-fp8-mtp`, with exactly `off`, `low`, `high`, and `max` and an allowed default.
- [x] AC-3: Remove or replace the current active/global `medium` setting without changing unrelated model semantics; prefer target-local/default behavior and use `max` where a target default is required.
- [x] AC-4: Prove Codex parses the catalog/config and its selector exposes exactly the four approved target modes.
- [x] AC-5: Capture sanitized Responses request shapes proving `off`, `low`, `high`, and `max` are emitted exactly as semantic efforts and `medium`/`xhigh` cannot be selected.
- [x] AC-6: Preserve unrelated catalog rows, provider endpoints, credentials, permissions, and existing Codex behavior.
- [x] AC-7: Produce complete evidence and validate rollback/restoration instructions.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-25-015-adapt-local-codex-deepseek-modes/` with `SUMMARY.md` and redacted `logs/` mapping AC-1 through AC-7.

## Acceptance Criteria Verification Map
- [x] AC-1
  - **Method:** baseline and backup inspection
  - **Evidence:** evidence packet
- [x] AC-2
  - **Method:** scoped catalog diff
  - **Evidence:** evidence packet
- [x] AC-3
  - **Method:** config semantic review
  - **Evidence:** evidence packet
- [x] AC-4
  - **Method:** Codex parser/selector probe
  - **Evidence:** evidence packet
- [x] AC-5
  - **Method:** sanitized local capture endpoint
  - **Evidence:** evidence packet
- [x] AC-6
  - **Method:** checksums and unrelated-row comparison
  - **Evidence:** evidence packet
- [x] AC-7
  - **Method:** closure review
  - **Evidence:** SUMMARY.md

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- AC-1 through AC-7 pass with sanitized evidence under `.staticeng/evidences/TASK-2026-08-25-015-adapt-local-codex-deepseek-modes/`
- Codex `0.147.0` parses and advertises target efforts exactly as `off`, `low`, `high`, and `max`, with target catalog default and active effort `max`
- Isolated loopback capture proves each approved value is transmitted unchanged as Responses `reasoning.effort`; no production prompt or request was sent
- `medium` and `xhigh` remain available to Codex generically for unrelated models but are absent from this target's selector and cannot be selected through the target catalog UI
- Only the target catalog row and active `model_reasoning_effort` changed. Unrelated rows, config fields, endpoints, credential references, ownership, and modes are preserved
- Exact pairwise rollback and protected owner-only backups are documented in the evidence packet
- Product documentation is not required because the approved SCR and steady-state architecture contract already describe the deployed behavior
- `staticeng_validate` remains blocked by pre-existing repository-wide missing CodeMaps unrelated to this local configuration slice; dry-run repair was inspected and not applied
- No repository commit or publication was performed, per handoff
