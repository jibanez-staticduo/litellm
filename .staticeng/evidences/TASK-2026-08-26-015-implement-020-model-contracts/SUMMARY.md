# TASK-2026-08-26-015 Evidence Summary

## Result

PASS after Reopen 1, with one unrelated validation blocker documented below. `@staticeng/opencode-litellm` is implemented at version `0.2.0` with one immutable typed internal contract catalog. Reopen 1 makes catalog V2 bodies and defaults authoritative at runtime. No runtime configuration, OpenCode core, Codex binary, LiteLLM source/registry, publish surface, commit, push, or release was changed.

## Reopen 1 Corrections

- Built-in V2 variants now render directly from `ModelContractMode.v2Body`. Generic conversion remains only for unknown and user-authored variant bodies.
- The selected catalog `defaultMode` is emitted through model options for no-variant requests. Named variants merge afterward; model and provider overrides remain last.
- Qwen explicit `off` removes the model-level `xhigh` default in the request hook, leaving only `chat_template_kwargs.enable_thinking=false`.
- Official OpenCode 1.18.23 passed 55 fresh strict-loopback processes: nine default-wire rows and all 46 explicit named modes.

## Acceptance Criteria Coverage

- **T1-AC-1: PASS.** `package.json` and both package-lock version locations are `0.2.0`. The frozen catalog has 31 unique active aliases across nine contract rows and four unique retired aliases, with no active/retired collision. See `04-full-tests.log` and `08-content-scans.log`.
- **T1-AC-2: PASS.** Table-driven tests cover every active alias against exact ordered modes, effective defaults, legacy bodies, and direct catalog V2 bodies. Catalog defaults are GPT-5.4/Mini `none`, GPT-5.5 `medium`, GPT-5.6 `medium`, Spark `high`, DeepSeek `max`, and Qwen `xhigh`; all nine passed fresh official no-variant wire probes. Undiscovered aliases are not created. See `13-reopen1-full-tests.log` and `14-reopen1-opencode-1.18.23.log`.
- **T1-AC-3: PASS.** Exact negative fixtures cover `defend/gpt-5.5`, account4, case changes, suffixes, and DeepSeek/Qwen near-matches; all retain unknown-model behavior and none receives a built-in contract. See `04-full-tests.log` and `08-content-scans.log`.
- **T1-AC-4: PASS.** Only GPT-5.6 rows include native `max` among GPT contracts; DeepSeek also has its approved native `max`. GPT-5.4/Mini/5.5/Spark omit it, and no built-in contract contains or emits `ultra`. See `04-full-tests.log` and `08-content-scans.log`.
- **T1-AC-5: PASS.** DeepSeek `off` renders `none` in legacy and V2. Qwen `off` renders only `chat_template_kwargs.enable_thinking=false`, with no reasoning effort. Official wire probes match. See `13-reopen1-full-tests.log` and `14-reopen1-opencode-1.18.23.log`.
- **T1-AC-6: PASS.** Conflicting discovery cannot weaken catalog reasoning/defaults/modes. Explicit model overrides and provider overrides apply after built-ins for known and unknown models on legacy and V2 surfaces, including explicit replacement of model-option defaults. Arrays/scalars retain 0.1.9 replacement behavior. See `13-reopen1-full-tests.log`.
- **T1-AC-7: PASS.** All four exact normal GPT-5.3 Codex aliases are filtered from stale discovery while all four exact Spark aliases remain. Fresh official OpenCode catalog verification resolved all nine active rows, retained Spark, and omitted normal GPT-5.3. See `13-reopen1-full-tests.log` and `19-reopen1-official-catalog.log`.
- **T1-AC-8: PASS.** Every built-in V2 mode consumes catalog `v2Body` directly and is compared with its legacy semantic pair. Official default and explicit wire probes validate all rows. `variantDefault` is removed by the provider/model-scoped request hook, and Qwen Off removes the default effort before wire serialization. See `13-reopen1-full-tests.log` and `14-reopen1-opencode-1.18.23.log`.
- **T1-AC-9: PASS.** Clean install, TypeScript/declaration build, 62/62 full tests, deterministic dist hash comparison, pack dry-run, 19-file package inventory, 55 official-client probes, and content scans passed. Reopen 1 artifact SHA-256: `40b2ce710ec8cba570742d8f86c541ef06dba0e8d119db0d66bb91185487fcba`. See logs `11` through `18`.
- **T1-AC-10: PASS for task-owned documentation and CodeMaps; unrelated validator blocker evidenced.** README, architecture documentation, root/source/test CodeMaps, tests, and generated dist match the implementation. The available validator is bound to the governing LiteLLM workspace and remains blocked only by its large pre-existing unrelated CodeMap backlog. Required dry-run repair proposed unrelated mutations and unresolved manual boundaries, so safe apply was intentionally not run. See `10-staticeng-validation.log`.

## Verification Totals

- Automated tests: **62 passed, 0 failed, 0 skipped, 0 todo**.
- Package inventory: **19 files**, expected `LICENSE`, `README.md`, `package.json`, and `dist/*` only.
- Official OpenCode: **1.18.23**, **55/55** fresh strict-loopback probes passed (**9 defaults + 46 explicit modes**).
- Actual Reopen 1 local pack artifact SHA-256: **`40b2ce710ec8cba570742d8f86c541ef06dba0e8d119db0d66bb91185487fcba`**; a second pack was byte-identical.

## Exact Task-Owned Implementation Diff

`README.md`; `.staticeng/codemap.yml`; `docs/architecture/model-contract-catalog.md`; `package.json`; `package-lock.json`; `src/codemap.yml`; `src/index.ts`; `src/mapping.ts`; `src/model-contracts.ts`; `src/types.ts`; `test/codemap.yml`; `test/mapping.test.mjs`; `test/model-contracts.test.mjs`; `test/model-groups.test.mjs`; `dist/index.js`; `dist/mapping.d.ts`; `dist/mapping.js`; `dist/model-contracts.d.ts`; `dist/model-contracts.js`; `dist/types.d.ts`.

Governing closure artifacts are this evidence directory and the post-implementation section in the task file. All pre-existing dirty/untracked `.staticeng` artifacts in `opencode-litellm` remain unstaged and otherwise untouched.

## Documentation Impact

Product-facing README documentation records the exact mode/default matrix, effective no-variant defaults, wire exceptions, retirement, exact matching, and user-last overrides. `docs/architecture/model-contract-catalog.md` records direct catalog V2 rendering, model-option defaults, Qwen Off cleanup, pipeline boundaries, and verification commands. Root/source/test CodeMaps describe actual navigable source.

## Open Risks

1. The governing LiteLLM workspace's pre-existing StaticEng CodeMap backlog prevents a global validator PASS; repairing it is unrelated and unsafe within this task.
2. Publication and fresh unversioned npm resolution are intentionally deferred to Task 2. The checksum above identifies the local candidate artifact only.
3. Official OpenCode normalizes legacy model display order internally, while the plugin's legacy source object and V2 variant array retain the approved order; official resolved selectable sets and wire payloads are correct without a core patch.
