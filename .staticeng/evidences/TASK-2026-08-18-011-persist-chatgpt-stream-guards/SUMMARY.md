# Persist ChatGPT Stream Guards Evidence

## Summary

Implemented both ChatGPT Responses streaming guards in the authorized four-file scope. Reopen 1 corrected test formatting and stabilized the async mutation regression. The required combined suite passes without skips or failures. Repository-wide closure remains blocked by unavailable baseline and pre-existing CodeMap debt

## Work Performed

- Preserved provider-required native streaming for ChatGPT in both sync and async Responses handlers after `extra_body` merging
- Bypassed fake streaming for native ChatGPT Responses streaming while retaining non-ChatGPT capability behavior
- Added mutation-sensitive sync, async, fake-stream, and provider-control regressions
- Configured the async regression with an empty dynamic callback list so its pre-fix run reaches the intended outbound stream assertion
- Formatted both modified test files and ran the combined mapped and inherited suite, targeted Ruff, formatter check, and diff check
- Attempted `make check`; no deployment, host edit, runtime mutation, or commit was performed

## Acceptance Criteria Coverage

- **AC-1: PASS**. Sync and async handler regressions confirm ChatGPT preserves provider-required `stream=True` even when `extra_body` supplies `stream=False`. See `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/logs/post-fix-handler-regressions-final.log` and `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/logs/test-llm-http-handler.log`
- **AC-2: PASS**. Provider-control regressions confirm non-ChatGPT retains `extra_body` precedence and ChatGPT is not forced to stream when its transformation did not require it. See `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/logs/post-fix-handler-regressions-final.log`
- **AC-3: PASS**. ChatGPT returns false from `should_fake_stream` on a capability miss, while the non-ChatGPT control retains capability-driven fake streaming. See `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/logs/post-fix-fake-stream-regressions-final.log`
- **AC-4: PASS**. The sync and fake-stream regressions fail without their guards, and the stabilized async regression now fails at the intended outbound `stream` assertion rather than callback setup. All pass with the guards restored. The original handler log is retained as historical evidence but its incidental async callback TypeError is superseded by the Reopen 1 run. See `logs/pre-fix-handler-regressions-original.log`, `logs/reopen1-pre-fix-async-regression.log`, `logs/pre-fix-fake-stream-regression.log`, `logs/post-fix-handler-regressions-final.log`, and `logs/post-fix-fake-stream-regressions-final.log`
- **AC-5: PASS FOR REQUIRED TARGETED VERIFICATION; REPOSITORY GATE BLOCKED**. The combined mapped HTTP handler, mapped OpenAI Responses transformation, and inherited ChatGPT Responses transformation run passes 146 tests with no skips or failures. Targeted Ruff passes with documented exclusions for pre-existing import and banned-API debt, both modified tests pass `ruff format --check`, and `git diff --check` passes. The earlier formatter failure is retained as `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/logs/pre-reopen-ruff-format-targeted.log` and is superseded by the Reopen 1 formatter check. `make check` remains unable to complete because `origin/litellm_internal_staging` does not exist; it was not rerun. See `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/logs/reopen1-combined-146-tests.log`, `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/logs/reopen1-targeted-ruff.log`, `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/logs/reopen1-ruff-format-check.log`, `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/logs/reopen1-git-diff-check.log`, and `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/logs/make-check.log`
- **AC-6: PASS**. This packet maps every AC and records documentation impact

## Blockers

`make check` is blocked because the configured remote lacks `litellm_internal_staging`. Its fallback lint-budget comparisons include broad unrelated working-tree and baseline deltas, including pre-existing budget failures outside this task's four files. PMA directed handback without baseline repair

`staticeng_validate` remains blocked by documented repository-wide missing CodeMaps and broken root CodeMap links. Prior validation and repair dry-run evidence is recorded in `.staticeng/evidences/TASK-2026-08-18-009-finalize-stream-fix-investigation/logs/verification.log`. Applying broad repair is outside this atomic implementation task

## Documentation Impact

No product, architecture, or technical documentation update is required. This task, its approved SCR, and this evidence packet capture the implementation truth

## Open Risks

Technical review can assess the completed four-file implementation, but PMA cannot declare full repository workflow closure until the unavailable lint baseline and repository-wide CodeMap debt are resolved separately
