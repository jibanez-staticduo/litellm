---
id: TASK-2026-08-27-004-retire-spark-client-catalogs
complexity: complex
track: implementation
slice: core
status: done
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: TASK-2026-08-26-019-retire-obsolete-model-routes
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-27-004 - Retire Spark Client Catalogs

## Objective
Remove GPT-5.3 Codex Spark from the built-in opencode-litellm contract catalog and NAS Codex custom catalog, publish/activate a corrective plugin release, and prove fresh clients no longer advertise either GPT-5.3 family.

## Acceptance Criteria
- [ ] AC-1: Plugin catalog marks all exact Spark aliases retired alongside normal GPT-5.3, with no impact on other GPT contracts or unknown models.
- [ ] AC-2: Tests/docs/CodeMaps/dist/package version update pass; official OpenCode isolated discovery omits both families and all other reasoning matrices remain exact.
- [ ] AC-3: Independently reviewed corrective release is committed/pushed/published and unversioned reference resolves the new version.
- [ ] AC-4: Reachable-host plugin caches are scoped-refresh to one corrective version; no unrelated cache is touched.
- [ ] AC-5: NAS Codex custom catalog removes Spark row only, preserves all other rows/config, and fresh Codex 0.149.1 omits both families.
- [ ] AC-6: Syncthing connected peers converge/no conflicts; evidence and rollback are complete.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-27-004-retire-spark-client-catalogs/` with `SUMMARY.md` and redacted logs.

## Stop Conditions
No route writes in this task. Stop/rollback clients on package, selector, Syncthing, Codex, or unrelated-diff failure.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Status: PASS for the approved client-only retirement; no LiteLLM route write, inference request, or client binary patch occurred
- `@staticeng/opencode-litellm@0.2.2` retires the four exact normal and four exact Spark aliases while preserving every other contract row, mode, default, near-match behavior, and model/provider override precedence
- Corrective commits `1617d86` and `b14e16c` were pushed to `origin/main`; release `v0.2.2` triggered trusted publishing, which repeated the known npm OIDC PUT 404 after all prior gates, then the authorized protected `.npmjs` fallback published the exact reproducible candidate
- npm `latest` and the registry tarball resolve `0.2.2`; the downloaded tarball is byte-identical to the independently packed candidate
- Scoped exact-identity cache refresh completed on NAS, Fedora, DG2, and Pi5 with fresh official OpenCode `1.18.23` discovery returning 33 models and neither GPT-5.3 family; DG1 has no official OpenCode runtime and its stale exact-identity cache was removed without touching unrelated caches
- NAS Codex received fresh owner-only backups; only the Spark row was removed atomically from the custom catalog, reducing nine rows to eight while preserving byte-identical active DeepSeek `high` config and all other rows
- Fresh isolated Codex `0.149.1` `model/list` returned all eight retained rows and neither GPT-5.3 family; production generated cache was not edited
- Syncthing configuration was unchanged; NAS and all six currently reachable configured instances are idle, complete, error-free, and conflict-free for the shared OpenCode folder
- Required package build, 63 tests, tracked dist, OpenCode matrix, pack, checksum, release, npm, cache, Codex, and Syncthing gates passed; `staticeng_validate` remains blocked only by the pre-existing repository-wide manual CodeMap backlog after repair dry-run
- Product and architecture documentation closure is complete in the approved SCR, plugin README, architecture document, and relevant CodeMaps
