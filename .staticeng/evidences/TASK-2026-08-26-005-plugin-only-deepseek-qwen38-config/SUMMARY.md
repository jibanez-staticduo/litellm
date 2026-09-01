# TASK-2026-08-26-005 Evidence Summary

## Result

Implemented plugin-only generated variants in the implementation repository without editing OpenCode, LiteLLM, active configuration, or any deployment. Official OpenCode 1.18.23 loaded the source checkout in an isolated test harness and strict loopback captured all twelve named mode requests. Shared configuration must instead load the pinned published npm release.

## Acceptance Criteria

- AC-1: PASS. Both exact DeepSeek aliases resolve named `off`, `low`, `high`, `max`; loopback captured `none`, `low`, `high`, `max` respectively.
- AC-2: PASS. Exact Qwen alias resolves named `off`, `low`, `medium`, `xhigh`; loopback captured `off` as `chat_template_kwargs.enable_thinking=false` with no `reasoning_effort`, and exact native efforts for the remaining modes.
- AC-3: PASS. DeepSeek tombstones disable `medium`/`xhigh`; Qwen tombstones disable `none`/`minimal`/`high`/`max` under official additive merge semantics. Official OpenCode 1.18.23 retains intrinsic `Predeterminado`; the plugin does not claim otherwise.
- AC-4: PASS. Exact predicates, near-match tests, and the full existing suite preserve unrelated mappings and overrides.
- AC-5: PASS. Official binary SHA-256 remained `de0724a36eaf3166e7f1ff38d0f4478b95ccc47725e9597b3fe66d3d3e18baa2`; isolated resolved config and strict loopback covered every named mode.
- AC-6: PASS. Source, 47 tests, tracked `dist`, README, CodeMaps, renewed release artifact, and evidence were updated. Shared activation remains unperformed and must use pinned npm package `@staticeng/opencode-litellm@0.1.9`; local paths are prohibited.

## Verification

- `.staticeng/evidences/TASK-2026-08-26-005-plugin-only-deepseek-qwen38-config/logs/build-test-pack.log`: TypeScript build, 47/47 tests, package dry-run, and diff check passed.
- `.staticeng/evidences/TASK-2026-08-26-005-plugin-only-deepseek-qwen38-config/logs/official-opencode-resolved.log`: official 1.18.23 identity and isolated resolved variant summaries.
- `.staticeng/evidences/TASK-2026-08-26-005-plugin-only-deepseek-qwen38-config/logs/strict-loopback.log`: exact twelve-request loopback capture; no production endpoint was contacted.
- `.staticeng/evidences/TASK-2026-08-26-005-plugin-only-deepseek-qwen38-config/logs/release-candidate.log`: registry availability and renewed `0.1.9` tarball review.
- `staticeng_validate` was invoked from the orchestrator workspace and failed only on extensive pre-existing missing CodeMaps throughout the unrelated LiteLLM monorepo. The implementation repo's three maintained CodeMaps were reviewed and updated directly.

## Documentation Impact

`README.md`, `.staticeng/codemap.yml`, `src/codemap.yml`, and `test/codemap.yml` in `opencode-litellm` now document Qwen's serving-compatible non-thinking body, unsupported tombstones, and the official 1.18.23 intrinsic default limitation.

## Constraints

No production request, npm publication, git commit, push, active-config edit, or OpenCode core/binary modification occurred. The isolated local-path harness was test-only and is not package content or intended shared configuration.
