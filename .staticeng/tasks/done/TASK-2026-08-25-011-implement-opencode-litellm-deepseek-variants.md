---
id: TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants
complexity: standard
track: implementation
slice: core
status: done
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 3
---

# Task: TASK-2026-08-25-011 - Implement opencode-litellm DeepSeek Variants

## Objective
Make `opencode-litellm` automatically expose exactly `off`, `low`, `high`, and `max` for both DeepSeek V4 aliases, without manual OpenCode model overrides.

## Governing Contract
- `.staticeng/docs/architecture/deepseek-v4-reasoning-contract.md`
- `.staticeng/docs/scrs/SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes.md`

## Acceptance Criteria
- [x] AC-1: Recognize only the exact target groups `deepseek-v4-flash-fp8-mtp` and `deepseek-v4-flash-fp8-mtp-norefusal`.
- [x] AC-2: Generate exactly four variants: `off`, `low`, `high`, and `max`; never generate `medium` or `xhigh` for the targets.
- [x] AC-3: Map `off` to a non-thinking wire control and map `low`, `high`, and `max` to exact native reasoning efforts in both legacy and V2 plugin output.
- [x] AC-4: Ensure plugin/model override merging cannot reintroduce forbidden target variants.
- [x] AC-5: Achieve the exact final OpenCode variant set without a manual DeepSeek entry in `opencode.json`; if the current OpenCode merge API makes plugin-only enforcement impossible, stop and return a precise compatibility blocker rather than editing OpenCode core.
- [x] AC-6: Preserve unrelated model generation and user overrides.
- [x] AC-7: Add focused tests, update README/CodeMaps, and produce complete evidence.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/` with `SUMMARY.md` and `logs/` mapping AC-1 through AC-7.

## Acceptance Criteria Verification Map
- [x] AC-1
  - **Method:** mapping tests
  - **Evidence:** evidence packet
- [x] AC-2
  - **Method:** exact key-set assertions
  - **Evidence:** evidence packet
- [x] AC-3
  - **Method:** exact payload assertions
  - **Evidence:** evidence packet
- [x] AC-4
  - **Method:** override conflict tests
  - **Evidence:** evidence packet
- [x] AC-5
  - **Method:** installed OpenCode merge integration test or compatibility analysis
  - **Evidence:** evidence packet
- [x] AC-6
  - **Method:** non-regression tests
  - **Evidence:** evidence packet
- [x] AC-7
  - **Method:** test, docs, and evidence review
  - **Evidence:** evidence packet

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Implemented exact automatic variants for both target aliases in `/home/staticduo/git/opencode-litellm/src/mapping.ts`
- Enforced target reasoning capability and exact variant replacement after per-model and provider-level override merging
- Added exact legacy/V2 payload, near-match, unrelated-model, override-conflict, and runtime config-hook tests
- Verified plugin-only runtime behavior with installed OpenCode 1.18.21 and no manual model configuration
- Updated README and all tracked implementation-repository CodeMaps, then rebuilt tracked `dist`
- Produced AC-1 through AC-7 evidence under `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/`
- `npm run build`, all 42 tests, `npm pack --dry-run`, and `git diff --check` pass
- `staticeng_validate` remains blocked by the LiteLLM repository's pre-existing broad missing-CodeMap backlog; dry-run repair confirms it is unrelated and was not applied
- No commit, push, npm publish, deployment, OpenCode core change, LiteLLM source change, or live configuration change was performed

## Reopen History

### Reopen 1 - 2026-08-25
- Tech Lead found candidate behavior correct but rejected release readiness.
- Advance the package from already-published immutable version `0.1.8` to the next available version, keeping metadata, lockfiles, and built output consistent.
- Create the required evidence packet in the governing LiteLLM workspace at `.staticeng/evidences/TASK-2026-08-25-011-implement-opencode-litellm-deepseek-variants/` with retained AC-mapped logs.
- Provide a clean intended release diff separating task-owned plugin changes from unrelated worktree artifacts.

### Reopen 2 - 2026-08-25
- Real OpenCode 1.18.21 UI/runtime evidence shows the plugin output is additively merged with generic variants: `Medium` and `Predeterminado` remain visible.
- Real `Off` sends literal `reasoning_effort=off`, which is invalid for vLLM. It must emit the canonical non-thinking wire control (`none` or the approved disabled-thinking representation).
- Required correction: reproduce against the active config/UI path, make the plugin authoritative using supported plugin hooks if possible, and prove exact visible set `off|low|high|max` plus sanitized wire mapping `off -> none`, native values unchanged.
- If OpenCode 1.18.21 cannot support authoritative replacement from a plugin, stop with exact API evidence and propose the smallest OpenCode core compatibility change; do not claim plugin-only completion.

## Developer: Reopen 1 Post Implementation Expectations

- Verified npm publishes versions `0.1.0` through `0.1.8` and that `0.1.9` returns `E404`, establishing `0.1.9` as the next available patch version
- Updated `package.json` and both root package records in `package-lock.json` from `0.1.8` to `0.1.9` using `npm version 0.1.9 --no-git-tag-version`
- Rebuilt tracked distribution output and reran all 42 tests with zero failures, skips, cancellations, or todos
- Re-ran the OpenCode 1.18.21 plugin-only integration and `npm pack --dry-run --json` for `@staticeng/opencode-litellm@0.1.9`
- Retained redacted reopen logs, AC mapping, and the exact intended release-file diff in the governing evidence packet
- Confirmed the intended release consists of exactly ten files; all other dirty worktree entries are unrelated and excluded
- No package publish, commit, push, deployment, live configuration edit, OpenCode core edit, or LiteLLM source edit was performed

## Developer: Reopen 2 Post Implementation Expectations

- Reproduced the active runtime defect with `opencode models LiteLLM --verbose`: OpenCode generically generated `medium`, while plugin `off` resolved to literal `reasoningEffort: off`
- Traced OpenCode provider merge code: config variants are additively merged at `provider.ts:1543-1551` and `provider.ts:1680-1686`; supported `disabled: true` tombstones suppress inherited variants
- Changed semantic `off` to canonical `none` on legacy and V2 mappings
- Added `medium` and `xhigh` disabled tombstones only at the plugin config-hook boundary, retaining exact four-variant public helper output
- Verified the active OpenCode runtime catalog now contains only `low`, `high`, `max`, and `off` for both aliases
- Verified `opencode run --variant off` against a local fixture sends `reasoning_effort: none`; no production request was sent
- Added focused tests; build and all 43 tests pass
- The UI's `Predeterminado` choice is an intrinsic no-variant sentinel, not a model variant; current plugin hooks cannot remove it. Named selectable variants are exact
- No publish, commit, push, deployment, production request, live configuration edit, or OpenCode core edit was performed

## Developer: Authorized UI Compatibility Fallback

- Added generic `modelVariantOptions` behavior in `/home/staticduo/git/opencode`: default remains visible unless a model explicitly sets `options.variantDefault: false`
- Updated both legacy and V2 prompt controls to honor that model-scoped capability
- Plugin sets the opt-out marker only on both exact DeepSeek aliases and strips it in `chat.params` before requests
- Focused OpenCode tests pass 9/9; plugin tests pass 44/44 and strict loopback capture still proves `reasoning_effort: none`
- OpenCode app-wide typecheck is blocked by extensive pre-existing missing workspace dependencies/generated types and unrelated errors; details are retained in evidence
- Screenshots were not produced because the source checkout was not built/deployed into the active UI, consistent with the no-deploy constraint
- OpenCode task-owned files are exactly `model-variant.ts`, `model-variant.test.ts`, `prompt-input.tsx`, and `prompt-input-v2.tsx`

### Reopen 3 - 2026-08-25
- Tech Lead rejected build/activation because the default sentinel remains reachable through current-value fallback and keyboard cycling.
- Make both legacy/V2 controls honor `variantDefault: false` for initial/current state and wrap cycling only among actual target variants.
- Scope marker stripping to the LiteLLM provider plus exact target alias, not model ID alone.
- Investigate and eliminate or explain the preliminary `low` completion request; no inference request may use a mode different from the selected target mode.
- Reconcile the approved contract so client adapters may map semantic UI `off` to wire `none`, while LiteLLM continues accepting public API `off` and normalizing it for direct callers.

## Developer: Reopen 3 Post Implementation Expectations

- OpenCode current-value resolution now chooses the first real variant when `variantDefault=false`; explicit/null default cannot remain selected
- OpenCode cycling wraps from the last real variant to the first real variant when default is disabled; generic models still cycle through the default sentinel
- Both legacy/local and V2 prompt model-selection paths pass the model-scoped default capability into current resolution and cycling
- Plugin `chat.params` stripping now requires both the configured LiteLLM provider identity and an exact target alias; unrelated provider/model combinations are preserved by tests
- Replaced the preliminary capture with eight isolated `opencode run` processes using explicit titles, one unique session per alias/mode, and strict request correlation
- Exactly eight requests were captured for two aliases times four modes; every request matched its selected model and effort (`off -> none`, `low`, `high`, `max`) with no preliminary or extra inference
- The prior preliminary low request was a harness artifact from non-isolated setup rather than task-owned OpenCode inference; explicit title and fresh process/session isolation eliminate title generation, retries, compaction, and cross-run state
- Plugin build and 44 tests, OpenCode focused 12 tests, eight strict loopback cases, pack dry-run, and diff checks pass
- No production contact, publish, active UI build, deployment, commit, push, or live config edit occurred
