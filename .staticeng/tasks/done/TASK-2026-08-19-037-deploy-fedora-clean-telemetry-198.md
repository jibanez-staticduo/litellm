---
id: TASK-2026-08-19-037-deploy-fedora-clean-telemetry-198
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-035-build-clean-telemetry-198-candidate
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-037 - Deploy Fedora Clean-Telemetry 1.98.0

## Objective
Deploy the replacement candidate to Fedora first and prove clean Responses telemetry plus cache poller logs over the full functional/observation gate.

## Safety
- NAS remains unchanged on prior candidate; stable held.
- Recreate only Fedora LiteLLM by immutable digest with `--no-deps`; preserve topology/state.
- Use all corrected Codex payload/quota/fallback gates.
- Roll back on any genuine health, preservation, functional, LazyMCP, telemetry/cache-log, or observation failure.

## Acceptance Criteria
- [ ] AC-1: Fresh baseline/rollback captured; only Fedora LiteLLM is recreated on manifest `35fc5209...f2d3`/config `9975f878...c9a3a`.
- [ ] AC-2: Identity, health, readiness/liveliness, restart/OOM, exact 27-model topology/preservation, dependencies, and unrelated services pass.
- [ ] AC-3: Native Responses, corrected Codex account2/public fallback, quota disposition, profile isolation, and LazyMCP pass.
- [ ] AC-4: Ten-minute observation spans multiple cache-poller intervals with zero telemetry `standard_logging_object` failures, success callback tracebacks, `resolved_usage_cache`/cache NameErrors, or other release-blocking errors.
- [ ] AC-5: NAS and stable remain unchanged; rollback remains ready.
- [ ] AC-6: Complete evidence approves/rejects NAS deployment.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-037-deploy-fedora-clean-telemetry-198/` with `SUMMARY.md` and sanitized logs.

## Handoff
[Agent Message] From: product_manager To: developer

Deploy only Fedora by the replacement digest. Execute all corrected functional/preservation gates and a ten-minute clean-log observation spanning cache polls. Keep NAS/stable unchanged, roll back on genuine failure, and do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1 through AC-6 passed.
- Fedora runs replacement digest `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3` healthy on 1.98.0.
- Functional, topology, profile isolation, LazyMCP, preservation, and 629-second clean telemetry/cache observation passed.
- NAS deployment approved; NAS/stable remained unchanged.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-6 passed with sanitized evidence under `.staticeng/evidences/TASK-2026-08-19-037-deploy-fedora-clean-telemetry-198/`
- Fedora runs manifest `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`, config `sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a`, version 1.98.0, revision `177c66ef727710a455f058b99f653df9b3e4c0a4`
- Native Responses, corrected account2/public fallback, profile isolation, and full LazyMCP gates passed
- The 629-second observation found zero telemetry, callback, usage-cache, cache-poller, stream, auth, migration, schema, patch, response-failure, or traceback errors
- Exact 27-model/24-fallback two-account topology, protected state, credentials metadata, dependencies, and unrelated services were preserved
- NAS and stable remained unchanged; Fedora rollback remains ready
- The candidate is approved for PMA-authorized NAS deployment
- No product/architecture/CodeMap documentation change was required and no commit was created
- `staticeng_validate` remains blocked by inherited broken links and repository-wide missing CodeMaps; broad unrelated repair output was not applied
