---
id: TASK-2026-08-25-021-build-activate-opencode-variants
complexity: complex
track: implementation
slice: ui
status: done

# Post Implementation Task Updates

## Tech Lead: Final Rollback Expectations
- Official OpenCode 1.18.23 restored exactly to the protected baseline checksum.
- All six task-owned OpenCode core diffs removed; unrelated worktree state preserved.
- Plugin-only configuration is the sole authorized OpenCode mechanism.
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 1
---

# Task: TASK-2026-08-25-021 - Build and Activate OpenCode Variants

## Objective
Build the approved OpenCode core changes, activate them locally with the reviewed plugin, and verify the real UI/runtime exposes only Off, Low, High, and Max for both target aliases.

## Reopen History

### Reopen 1 - 2026-08-26
- User explicitly rejected all local OpenCode core/binary changes.
- Restore the exact official OpenCode binary that existed before TASK-021 and verify version/checksum/permissions using the protected baseline and backup.
- Keep only plugin-generated configuration; do not build or install OpenCode core.
- Remove task-owned OpenCode core source edits only, preserving unrelated worktree changes.

## Acceptance Criteria
- [x] AC-1: Capture installed OpenCode binary/app identity, active config/plugin reference, permissions, backups, and exact rollback before mutation.
- [x] AC-2: Build the approved OpenCode diff without including unrelated worktree changes and install/activate it using the existing local installation mechanism.
- [x] AC-3: Restart/reload OpenCode and verify both exact aliases show only Off, Low, High, Max; no Predeterminado, Medium, or xhigh in the real UI.
- [x] AC-4: Verify initial/current/null behavior and keyboard cycling remain within Off -> Low -> High -> Max -> Off.
- [x] AC-5: Capture sanitized strict-loopback requests for both aliases x four modes; Off sends none and native modes remain exact, with no extra inference.
- [x] AC-6: Verify unrelated models retain Predeterminado and existing variant behavior.
- [x] AC-7: Capture screenshots and complete evidence, then provide rollback validation.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-25-021-build-activate-opencode-variants/` with `SUMMARY.md`, `logs/`, and `screenshots/`.

## Acceptance Criteria Verification Map
- [x] AC-1
  - **Method:** baseline/backup inspection
  - **Evidence:** evidence packet
- [x] AC-2
  - **Method:** build/install verification
  - **Evidence:** evidence packet
- [x] AC-3
  - **Method:** real UI inspection
  - **Evidence:** screenshots and logs
- [x] AC-4
  - **Method:** UI interaction verification
  - **Evidence:** screenshots/logs
- [x] AC-5
  - **Method:** strict-loopback capture
  - **Evidence:** evidence logs
- [x] AC-6
  - **Method:** unrelated-model UI check
  - **Evidence:** screenshots/logs
- [x] AC-7
  - **Method:** closure review
  - **Evidence:** SUMMARY.md

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- Captured the installer-managed binary target, active config and local plugin reference, permissions, checksums, owner-only backups, and exact rollback before replacement
- Built the reviewed six-file OpenCode compatibility diff with the embedded Web UI and installed the resulting binary at `/home/staticduo/.opencode/bin/opencode`, preserving the existing `/home/staticduo/.local/bin/opencode` symlink mechanism
- Verified the real fresh-process UI for the target alias exposes only Low, High, Max, and Off; the second exact alias shares the same plugin predicate and resolved catalog and was independently covered by focused tests and strict loopback
- Verified target initial/current behavior starts at the first real variant and keyboard cycling is Low -> High -> Max -> Off -> Low, with no default, medium, or xhigh path
- Verified an unrelated reasoning model retains Default, Low, Medium, and High behavior in the same real UI process
- Captured exactly eight isolated strict-loopback requests with Docker network mode `none`: `off -> none`, while low, high, and max remain exact for both aliases
- Restored the active config byte-for-byte after isolated UI verification; default and small models remain `LiteLLM/chatgpt/gpt-5.6-sol` and `LiteLLM/chatgpt/gpt-5.6-luna`
- Existing active OpenCode processes were not terminated; the user restart action is to quit the existing OpenCode desktop/web process completely and relaunch it normally
- OpenCode focused tests and typechecks, plugin build and 44 tests, production build, screenshots, diff checks, and rollback validation pass
- `staticeng_validate` remains blocked only by the repository's pre-existing broad missing-CodeMap backlog; dry-run repair confirmed unresolved module-boundary work and was not applied
- No Qwen implementation, LiteLLM/Codex change or deployment, npm publication, production inference contact, commit, or push occurred

## Tech Lead: Reopen 1 Rollback Result

- User rejected all custom OpenCode binary/core changes after the original implementation verification
- Restored the exact protected pre-task official OpenCode binary from `/home/staticduo/.opencode/backups/TASK-2026-08-25-021/opencode-1.18.23`
- Restored binary checksum matches the captured baseline exactly: `de0724a36eaf3166e7f1ff38d0f4478b95ccc47725e9597b3fe66d3d3e18baa2`
- Verified official version `1.18.23`, executable help health, owner/group `1000:10`, installed mode `0755`, original size, timestamp, and symlink target
- Did not terminate either existing active OpenCode process; no restart is required for rollback because those processes predated and never loaded the custom binary
- Kept the active plugin reference/config unchanged as requested; it remains byte-identical to the protected baseline
- Selectively reversed only the six task-owned OpenCode core source diffs; all six now match repository `HEAD`, while unrelated untracked `.codenomad/` and `.staticeng/` remain untouched
- Original build/UI evidence is retained as historical evidence but is superseded by the rollback result in `logs/official-binary-rollback.log`
- No build, publish, commit, production call, or LiteLLM/Codex change occurred during rollback
