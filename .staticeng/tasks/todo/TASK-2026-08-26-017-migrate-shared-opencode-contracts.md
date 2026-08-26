---
id: TASK-2026-08-26-017-migrate-shared-opencode-contracts
complexity: complex
track: implementation
slice: core
status: active
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: null
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 1
---

# Task: TASK-2026-08-26-017 - Migrate Shared OpenCode Contracts

## Objective
Atomically clean known-model overrides from the NAS-authoritative Syncthing-shared OpenCode configuration and prove official OpenCode loads published plugin 0.2.0 across synchronized hosts.

## Acceptance Criteria
- [ ] T3-AC-1: Fresh protected NAS backup and redacted structural baseline prove exactly approved known/retired/defend override keys are removed; all unrelated paths and protected hashes remain unchanged.
- [ ] T3-AC-2: Plugin reference remains exact unversioned `@staticeng/opencode-litellm`, JSON parses, mode remains `0600`, and zero local/file references exist.
- [ ] T3-AC-3: NAS is the only direct writer; Syncthing reaches idle/up-to-date convergence on every expected peer with matching checksums and no conflict files.
- [ ] T3-AC-4: On each reachable synchronized host, invalidate only stale `@staticeng/opencode-litellm` cache state and prove a fresh official OpenCode process resolves installed version `0.2.0`; do not edit peer config.
- [ ] T3-AC-5: Record fresh process/version evidence without terminating the rollout control session or unrelated user sessions; identify any pre-existing processes that require user restart.
- [ ] T3-AC-6: Official OpenCode exposes exact approved named modes for every discovered known alias, no normal GPT-5.3 or defend entry, preserved Spark, and no fabricated aliases.
- [ ] T3-AC-7: Strict isolated captures prove each distinct contract row/default, alias equivalence, intrinsic Default omission, and user-last override precedence.
- [ ] T3-AC-8: Complete evidence contains no credentials, prompts, responses, or unredacted config.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-017-migrate-shared-opencode-contracts/` with `SUMMARY.md` and redacted logs/screenshots where useful.

## Rollback
Restore the exact NAS backup atomically from NAS only, wait for Syncthing convergence, invalidate only plugin cache, and prove prior behavior. Emergency package pin to `@0.1.9` requires blocker evidence.

## Stop Conditions
Stop on unexpected path changes, secret exposure, Syncthing conflict/divergence, package version mismatch, selector/payload failure, or inability to identify/protect active sessions.

## Reopen History

### Reopen 1 - 2026-08-26
- Initial all-peer preflight found 6 connected/complete and 6 offline/incomplete peers, so no mutation occurred.
- User approved immediate scope as NAS plus every currently connected expected peer.
- Offline peers remain untouched and will receive the authoritative NAS file automatically on reconnect; record them as eventual-convergence follow-up.
- Fresh preflight found five of six connected expected peers at 100% completion; one connected expected peer remained below 100% after bounded NAS and peer scans.
- The connected-peer convergence stop condition was enforced before configuration inspection, backup, cache invalidation, or process changes.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Read-only Syncthing preflight found the NAS authoritative folder idle and error-free, but only 6 of 12 expected peers were at 100% completion
- Six expected peers were offline and six were below 100% completion, including one connected stale peer; the required all-peer convergence gate therefore failed
- Execution stopped before reading or backing up `opencode.json`, inspecting protected values, editing any host, invalidating cache, or changing processes
- No rollback was required because mutation count was zero
- Redacted blocker evidence is under `.staticeng/evidences/TASK-2026-08-26-017-migrate-shared-opencode-contracts/`
- Product and architecture documentation are not required for this blocked preflight
- `staticeng_validate` remains blocked by the pre-existing repository-wide manual CodeMap backlog; mandatory repair dry-run and apply found no deterministic fix
- Reopen 1 applied the user-approved connected-peer scope, but one connected expected peer remained incomplete after bounded scans; no production configuration or process mutation occurred
- Resume only after the incomplete connected peer reaches 100% completion and all connected-peer preflight gates pass
