---
id: TASK-2026-08-26-022-investigate-opencode-plugin-cache-policy
complexity: standard
track: investigation
slice: foundation
status: done
scr: null
parent: TASK-2026-08-26-017-migrate-shared-opencode-contracts
assigned_to: tool-specialist
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-022 - Investigate OpenCode Plugin Cache Policy

## Objective
Determine the safest update/restart policy for OpenCode npm plugin caches across hosts, based on the actual NAS `restart_opencode` and per-host `update_opencode` scripts and OpenCode package resolution behavior.

## Acceptance Criteria
- [ ] AC-1: Locate and inspect the exact NAS restart/update scripts and identify host distribution/ownership without exposing secrets.
- [ ] AC-2: Determine whether clearing all `~/.cache/opencode/packages` is safe, what state would be lost, and whether fresh startup redownloads every configured plugin reliably.
- [ ] AC-3: Determine whether npm/OpenCode supports a reliable no-cache or forced-refresh startup option and whether it addresses duplicate specifier caches.
- [ ] AC-4: Compare full cache purge, configured-plugin selective purge, stale-version pruning, and version-aware refresh.
- [ ] AC-5: Recommend an idempotent cross-host design with offline/npm-failure behavior, atomicity, logs, rollback, and tests.

## Expected Evidence
- Signed read-only handoff with script paths, relevant commands/options, risks, and recommended implementation. No edits/restarts/cache deletion.
