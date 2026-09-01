# TASK-2026-08-25-011 Evidence Summary

## Result

Implemented plugin-owned automatic reasoning variants for the exact LiteLLM model groups `deepseek-v4-flash-fp8-mtp` and `deepseek-v4-flash-fp8-mtp-norefusal` in `/home/staticduo/git/opencode-litellm`

Reopen 1 advances the release candidate from already-published `0.1.8` to available patch version `0.1.9`. Package metadata and lockfile root records agree, tracked distribution output was rebuilt, and no registry write occurred

Reopen 2 corrects the active-runtime defect: semantic `off` emits canonical `none`, and supported disabled-variant tombstones suppress OpenCode-generated `medium` and `xhigh` after additive merge

The authorized compatibility fallback adds a generic model-scoped OpenCode UI capability: models with `options.variantDefault: false` omit the default sentinel. The plugin sets and strips this marker only for the two exact aliases, producing the required UI set Off, Low, High, Max

Reopen 3 closes current-state, keyboard-cycle, provider-scope, and capture-isolation findings. Default-disabled models resolve and cycle only among real variants; strict loopback captured exactly eight correlated user requests with no extra inference

## Acceptance Criteria

- AC-1: PASS. Mapping tests cover both exact aliases plus case and suffix near-matches
- AC-2: PASS. Helpers expose exactly `off`, `low`, `high`, and `max`; active OpenCode runtime output contains only those keys after tombstone filtering
- AC-3: PASS. Semantic `off` maps to canonical `none`; strict loopback observed exact selected efforts on all eight alias/mode requests
- AC-4: PASS. Overrides are sanitized and OpenCode-generated `medium`/`xhigh` are disabled at the config merge boundary
- AC-5: PASS. Active discovery resolves four variants; current state and cycling cannot reach default when opted out, while unrelated models retain default behavior
- AC-6: PASS. Near-match and unrelated-model tests prove generic variants, custom model fields, provider overrides, and reasoning behavior remain unchanged
- AC-7: PASS. Plugin build/44 tests, pack dry-run, OpenCode focused 12 tests, eight-case correlated wire capture, docs, `dist`, evidence, and scoped diffs were verified

## Verification

- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/build-and-tests.log`: `npm run build && npm test`, 42 passed, 0 failed, 0 skipped
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/opencode-1.18.21-integration.log`: installed OpenCode plugin-only runtime config result for both surfaces
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/package-dry-run.log`: publish artifact inspection only; no package was published
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/staticeng-validation.log`: repository validation limitation and scoped CodeMap review
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/diff-check.log`: whitespace validation
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen1-version-availability.log`: registry versions and explicit `0.1.9` absence proof
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen1-build-and-tests.log`: retained `0.1.9` build and 42-test result
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen1-package-dry-run.log`: retained `0.1.9` package identity and contents summary
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen1-opencode-integration.log`: retained OpenCode 1.18.21 plugin-only output
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen1-intended-release-diff.log`: exact task-owned release files and separation from unrelated dirty work
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen2-active-runtime-before.log`: active catalog incident reproduction
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen2-merge-analysis.log`: OpenCode merge/request evidence and UI limitation
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen2-active-runtime-after.log`: final active catalog
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen2-off-wire-capture.log`: local `off -> none` request capture
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen2-build-test-pack.log`: 43 tests and pack result
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen2-opencode-ui-fallback.log`: model-scoped UI compatibility change and verification
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen3-strict-eight-case-capture.log`: exact all-alias/all-mode correlation proof
- `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/logs/reopen3-focused-verification.log`: current/cycle/provider-scope verification

## Documentation Impact

`README.md`, `.staticeng/codemap.yml`, `src/codemap.yml`, and `test/codemap.yml` in `opencode-litellm` now document the target-specific exception and verification ownership. The governing architecture contract was reconciled with the approved SCR clarification: visible `off` serializes as private wire `none` in the trusted OpenCode adapter, while direct LiteLLM API callers may still send public `off` for proxy normalization

## Constraints Observed

No LiteLLM source, live configuration, npm registry, deployment, git commit, or remote was modified. OpenCode source was changed only by the authorized model-scoped UI compatibility fallback

No production inference request was sent during Reopen 2

## Intended Release Files

Exactly these sixteen files in `/home/staticduo/git/opencode-litellm` belong to the release candidate:

1. `.staticeng/codemap.yml`
2. `README.md`
3. `dist/helpers.d.ts`
4. `dist/helpers.js`
5. `dist/index.js`
6. `dist/mapping.d.ts`
7. `dist/mapping.js`
8. `package-lock.json`
9. `package.json`
10. `src/codemap.yml`
11. `src/helpers.ts`
12. `src/index.ts`
13. `src/mapping.ts`
14. `test/codemap.yml`
15. `test/mapping.test.mjs`
16. `test/model-groups.test.mjs`

All other dirty entries in that repository predate or are unrelated to this task and are excluded from the release diff

## OpenCode Compatibility Files

Exactly these six files in `/home/staticduo/git/opencode` are task-owned:

1. `packages/app/src/context/model-variant.ts`
2. `packages/app/src/context/model-variant.test.ts`
3. `packages/app/src/components/prompt-input.tsx`
4. `packages/app/src/components/prompt-input-v2.tsx`
5. `packages/app/src/context/local.tsx`
6. `packages/app/src/pages/session/composer/prompt-model-selection.ts`
