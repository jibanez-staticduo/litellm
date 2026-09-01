# TASK-2026-08-26-009 Evidence Summary

## Result

Merged remote `c489ac9` into local release commit `45d1762` non-interactively. The reconciliation retains remote CI, trusted publishing, metadata/types, generic reported-effort mapping, unknown-output sentinel, and expanded tests while preserving the exact plugin-only DeepSeek and Qwen3.8 contracts.

## Acceptance Criteria

- AC-1: PASS. `.staticeng/evidences/TASK-2026-08-26-009-reconcile-plugin-remote/logs/semantic-overlap.log` maps both parents across source, types, tests, workflows, package metadata, docs, and generated dist before recording the minimal conflict decisions.
- AC-2: PASS. Merge commit `af92f31` has parents `45d1762` and `c489ac9`; no rebase, force, or amend was used. Conflicts were limited to generated `dist/mapping.js`, `src/mapping.ts`, and the two CodeMaps.
- AC-3: PASS. Official OpenCode 1.18.23 made exactly twelve isolated strict-loopback requests: DeepSeek `off/low/high/max` serialized as `none/low/high/max`; Qwen3.8 `off/low/medium/xhigh` serialized as non-thinking control and exact native efforts.
- AC-4: PASS. Clean `npm ci`, TypeScript/declaration build, 52/52 tests with zero failures/skips/todos, tracked-dist diff, workflow static checks, and dry-run pack passed. `staticeng_validate` remains blocked only by pre-existing missing CodeMaps in the unrelated LiteLLM orchestrator workspace.
- AC-5: PASS. Two consecutive packs were byte-identical at SHA-256 `b4c8e8d800b794cef692e02ca4ab6296f3a12b5501cd1d07eb7f5a55d3de28d2`. Both contain the exact 17-file scope in `.staticeng/evidences/TASK-2026-08-26-009-reconcile-plugin-remote/logs/artifact.log`; scans exclude credentials, local absolute paths, `.npmjs`, source/tests/workflows/evidence, and shared config. The sole literal `file://` is the README prohibition.
- AC-6: PASS. No push, npm publication, production request, or active OpenCode config edit occurred.

## Verification

- `.staticeng/evidences/TASK-2026-08-26-009-reconcile-plugin-remote/logs/semantic-overlap.log`: parent deltas and resolution decisions.
- `.staticeng/evidences/TASK-2026-08-26-009-reconcile-plugin-remote/logs/verification.log`: toolchain, clean install/build, test totals, dist/workflow/package checks, and validation limitation.
- `.staticeng/evidences/TASK-2026-08-26-009-reconcile-plugin-remote/logs/strict-loopback.log`: all twelve official OpenCode wire bodies against loopback only.
- `.staticeng/evidences/TASK-2026-08-26-009-reconcile-plugin-remote/logs/artifact.log`: reproducible checksum, exact package scope, and clean scan results.

## Documentation Impact

`README.md`, `src/codemap.yml`, and `test/codemap.yml` now jointly document generic LiteLLM-reported efforts, exact DeepSeek/Qwen exceptions, the output-limit sentinel, workflow safety, and trusted publishing. No product contract change beyond the approved SCR was introduced.

## Rereview Scope

Tech Lead should rereview merge lineage through commit `1e32745`, the 17 publish files listed in `.staticeng/evidences/TASK-2026-08-26-009-reconcile-plugin-remote/logs/artifact.log`, and SHA-256 `b4c8e8d800b794cef692e02ca4ab6296f3a12b5501cd1d07eb7f5a55d3de28d2`. Pre-existing dirty `.staticeng` files in the implementation repository are excluded.
