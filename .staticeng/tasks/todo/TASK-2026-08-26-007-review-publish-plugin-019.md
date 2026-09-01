---
id: TASK-2026-08-26-007-review-publish-plugin-019
complexity: standard
track: implementation
slice: polish
status: active

## Reopen History

### Resume 1 - 2026-08-26
- Fresh independent artifact review approved the current candidate.
- Exact approved tarball SHA-256: `2c6ae123b8e00fd318410703fcaa7abe0889a65ec51043c848dacc8dddb4f49c`.
- Resume commit, push, npm publication, registry verification, and shared-config repin using only the approved 17-file scope.
scr: SCR-2026-08-26-001-qwen38-native-reasoning-modes
parent: TASK-2026-08-26-005-plugin-only-deepseek-qwen38-config
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-007 - Review and Publish Plugin 0.1.9

## Objective
Independently verify and publish `@staticeng/opencode-litellm@0.1.9`, then repin Syncthing-shared OpenCode configuration from the prohibited local reference to the exact npm package.

## Acceptance Criteria
- [ ] AC-1: Review complete plugin diff and prove DeepSeek/Qwen3.8 named variants and wire payloads with official OpenCode 1.18.23.
- [ ] AC-2: Re-run build, all tests, pack inspection, local-path scan, and compare artifact checksum to the reviewed candidate.
- [ ] AC-3: Inspect git status/diff/log and stage/commit/push only intended release files, excluding `.npmjs` and unrelated artifacts.
- [ ] AC-4: Publish `0.1.9` transiently with `.npmjs`, verify registry version, integrity, and package contents.
- [ ] AC-5: Back up and change only the active plugin reference in `/home/staticduo/.config/opencode/opencode.json` to `@staticeng/opencode-litellm@0.1.9`; preserve mode `0600` and all options.
- [ ] AC-6: Verify official OpenCode resolves the npm plugin and correct named variants for DeepSeek and Qwen3.8; no `file://` remains in active shared config.
- [ ] AC-7: Produce complete evidence and exact rollback to `0.1.8`.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-007-review-publish-plugin-019/` with `SUMMARY.md` and redacted logs.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Independent build, 47/47 tests, dry-run pack, package-content inspection, git inspection, and official OpenCode `1.18.23` identity checks passed.
- The rebuilt package SHA-256 was `2c6ae123b8e00fd318410703fcaa7abe0889a65ec51043c848dacc8dddb4f49c`, which does not match approved SHA-256 `0af33f08ce4e8c42da24954dcbdad3345406aad748f3bd184ff6d94478077eea`.
- The mandatory artifact identity gate failed. Work stopped before staging, commit, push, npm publish, backup, active-config mutation, or npm-resolution verification.
- The active config remains mode `0600` at pre-change SHA-256 `66772b3d57d1b6c8983c7ec4884d348ca48e1c91f63ed6f1315b6441c172f75f` and still has its pre-existing local reference.
- PMA must authorize a fresh independent review of the changed artifact or restore the previously approved exact artifact before this task resumes.

### Resume 2 Closure - 2026-08-26

- Pushed reconciled head `1e32745a9d30d3a83d37a37dc197b47c86fb5339` to `origin/main` without force after 52/52 tests and reproducible 17-file pack verification.
- Published `@staticeng/opencode-litellm@0.1.9`; registry tarball SHA-256 is `b4c8e8d800b794cef692e02ca4ab6296f3a12b5501cd1d07eb7f5a55d3de28d2`.
- Backed up the active config to `/home/staticduo/.config/opencode/opencode.json.backup-task-007-20260826T063449Z`, preserving mode `0600`.
- Replaced only the local plugin tuple reference with exact user-requested unversioned `@staticeng/opencode-litellm`; tuple options are unchanged.
- Active config is valid JSON, mode `0600`, contains zero `file://` or local plugin repository strings, and has SHA-256 `77167c4b2aba293dd8215529b09ccc250c9204b7cc68008ce5f3c2f12edb6bc2`.
- Official OpenCode 1.18.23 resolves the active published plugin and 29 discovered LiteLLM models. No production inference was performed.
