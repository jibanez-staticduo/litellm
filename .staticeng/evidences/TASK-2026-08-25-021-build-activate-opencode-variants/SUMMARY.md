# TASK-2026-08-25-021 Evidence Summary

## Reopen 1 Rollback - Current State

ROLLED BACK. The user rejected all custom OpenCode binary/core changes after the original verification. The current installed binary is the exact protected pre-task official OpenCode 1.18.23 artifact, and all six task-owned OpenCode source edits have been selectively removed

- Restored checksum: `de0724a36eaf3166e7f1ff38d0f4478b95ccc47725e9597b3fe66d3d3e18baa2`, exactly matching `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/baseline-and-rollback.log` and the protected backup
- Installed binary: owner/group `1000:10`, mode `0755`, size `184584320`, version `1.18.23`; `--help` executable health passed
- Existing active processes were not terminated. They predated the custom installation and did not need restart for rollback
- Active config and local plugin reference remain unchanged and byte-identical to the protected baseline, as requested
- The six task-owned source diffs under `/home/staticduo/git/opencode/packages/app/src/` now match repository `HEAD`; unrelated dirty content was preserved
- Evidence: `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/official-binary-rollback.log`

The original implementation result below is retained only as historical evidence and is superseded by this rollback

## Result

PASS. The reviewed OpenCode compatibility diff was built with the embedded real Web UI, installed through the existing local binary path, and validated in a separate fresh process without disrupting active sessions

The DeepSeek target UI exposes only Off, Low, High, and Max. Initial/current resolution selects the first real variant, keyboard cycling remains within Low -> High -> Max -> Off -> Low, and an unrelated reasoning model retains its Default sentinel and generic variants

Strict Docker loopback with external networking disabled captured exactly eight requests for both aliases and four modes. Visible Off serialized as `reasoning_effort=none`; low, high, and max remained exact. No production inference endpoint was contacted

## Acceptance Criteria

- AC-1: PASS. `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/baseline-and-rollback.log` records binary/config identity, permissions, checksums, owner-only backups, active plugin reference, and exact rollback
- AC-2: PASS. `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/opencode-build.log`, `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/build-artifact-and-scope.log`, and `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/final-install-and-restart.log` prove the reviewed build and installed artifact; unrelated dirty files were preserved
- AC-3: PASS. `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/screenshots/deepseek-target-menu.png` and `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/ui-interaction.log` show the real fresh-process UI contains only Low, High, Max, and Off. The second exact alias uses the same exact model predicate and is covered by focused tests and resolved-catalog/loopback evidence
- AC-4: PASS. `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/ui-interaction.log` records initial Low and keyboard cycling Low, High, Max, Off, Low. `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/app-focused-tests-after-install.log` covers null/current/default-disabled resolution
- AC-5: PASS. `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/network-isolation.log` proves Docker network mode `none` and blocked external routing; `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/sanitized-loopback-bodies.jsonl` contains exactly eight redacted requests with off mapped to none and native modes exact
- AC-6: PASS. `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/screenshots/unrelated-model-default.png` and `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/ui-interaction.log` show Default, Low, Medium, and High remain available for an unrelated reasoning model. `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/logs/config-restore.log` confirms unrelated active model defaults are unchanged
- AC-7: PASS. Screenshots, logs, rollback, restored configuration, and closure evidence are complete

## Verification

- OpenCode app focused tests: 12 passed
- OpenCode app typecheck: passed
- OpenCode package typecheck: passed
- Plugin build and tests: 44 passed, 0 failed, 0 skipped
- OpenCode production build with embedded UI: passed
- Strict-loopback captures: 8 exact requests, external network unavailable
- Real fresh-process UI: target menu, initial/current state, keyboard cycle, and unrelated-model default verified
- Active config restoration: byte-identical to protected baseline, mode `0600`
- `staticeng_validate`: blocked by the pre-existing repository-wide missing-CodeMap backlog; `staticeng_repair` dry-run was reviewed and not applied because unresolved module boundaries are unrelated to this task

## Rollback

Restore the prior binary and config, then restart OpenCode:

```sh
cp -p /home/staticduo/.opencode/backups/TASK-2026-08-25-021/opencode-1.18.23 /home/staticduo/.opencode/bin/opencode
chmod 755 /home/staticduo/.opencode/bin/opencode
cp -p /home/staticduo/.opencode/backups/TASK-2026-08-25-021/opencode.json /home/staticduo/.config/opencode/opencode.json
```

The existing active process was intentionally left running. To activate the installed build for the user's desktop/web process, quit OpenCode completely and relaunch it normally

## Documentation Impact

No additional product or architecture documentation is required. The approved SCR and steady-state architecture contract already document visible Off and private wire `none`; this task performs only the reviewed local build and activation

## Constraints Observed

No Qwen change, LiteLLM/Codex change or deployment, npm publication, production inference request, commit, or push was performed
