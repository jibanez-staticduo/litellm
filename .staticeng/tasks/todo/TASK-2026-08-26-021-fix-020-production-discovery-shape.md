---
id: TASK-2026-08-26-021-fix-020-production-discovery-shape
complexity: standard
track: implementation
slice: logic
status: active
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: TASK-2026-08-26-017-migrate-shared-opencode-contracts
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-021 - Fix 0.2.0 Production Discovery Shape

## Objective
Reproduce and fix the official OpenCode production-discovery initialization failure `models.filter is not a function`, publish a reviewed patch release, and unblock the rolled-back shared-config migration.

## Acceptance Criteria
- [ ] AC-1: Reproduce the failure using the exact live NAS `/model/info` and `/model_group/info` response shapes with credentials and response contents redacted.
- [ ] AC-2: Identify the exact boundary receiving a non-array and normalize it without weakening malformed-response diagnostics.
- [ ] AC-3: Add regression fixtures for the live response shape and nearby valid/invalid shapes; preserve every 0.2.0 contract behavior.
- [ ] AC-4: Official OpenCode 1.18.23 initializes against live discovery in a safe read-only probe and resolves expected model counts/contracts.
- [ ] AC-5: Build, full tests, dist, pack, scans, and package version patch release preparation pass.
- [ ] AC-6: Produce complete evidence and exact rollback; no shared config, Codex, registry route, or OpenCode core mutation.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-021-fix-020-production-discovery-shape/` with `SUMMARY.md` and redacted logs.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Root cause is a duplicate stale `0.1.0` unversioned package instance filtering a response object before normalization, not the reviewed `0.2.0` fetch, merge, provider build, or config merge path.
- Exact live endpoint responses are direct `{ data: array }` shapes; only shape/type/key summaries were retained.
- Prepared version `0.2.1` with exact live config-hook regression coverage and adjacent malformed-envelope diagnostics; runtime source and deterministic dist remain unchanged.
- `npm run build`, 63/63 tests, contract matrices, official OpenCode 1.18.23 live metadata-only initialization, pack inventory, package scan, and production audit pass.
- Candidate tarball SHA-256 is `ce9a42bfab697f1124376d6665619e8b11b4aa009ee9dc03de9fe702fc7b8fd6`.
- No shared config, cache outside isolated temporary state, Codex, LiteLLM route, OpenCode core, publish, commit, or push mutation occurred.
- Product and architecture documentation are not required because package behavior did not change; `test/codemap.yml` records the expanded verification truth.
