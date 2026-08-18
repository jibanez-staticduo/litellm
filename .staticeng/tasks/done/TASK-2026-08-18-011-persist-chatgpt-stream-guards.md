---
id: TASK-2026-08-18-011-persist-chatgpt-stream-guards
complexity: standard
track: implementation
slice: logic
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-010-design-stream-safe-198-release
assigned_to: developer
handoff_from: product_manager
reopened_count: 1
---

# Task: TASK-2026-08-18-011 - Persist ChatGPT Stream Guards

## Objective
Implement both historical ChatGPT Responses streaming corrections on current `main` with focused regression coverage, without changing public APIs or non-ChatGPT behavior.

## Scope
- Modify only:
  - `litellm/llms/custom_httpx/llm_http_handler.py`
  - `litellm/llms/openai/responses/transformation.py`
  - `tests/test_litellm/llms/custom_httpx/test_llm_http_handler.py`
  - `tests/test_litellm/llms/openai/responses/test_openai_responses_transformation.py`
- Do not build/deploy images, edit host files, or mutate runtime.

## Acceptance Criteria
- [ ] AC-1: Sync and async native Responses handlers preserve provider-required `stream=True` for ChatGPT after merging `extra_body`, including when it contains `stream=false`.
- [ ] AC-2: Non-ChatGPT providers retain current `extra_body` precedence and ChatGPT is not forced to stream unless provider transformation required it.
- [ ] AC-3: `should_fake_stream` returns false for ChatGPT native streaming even on capability metadata miss, while non-ChatGPT capability behavior is unchanged.
- [ ] AC-4: Focused sync, async, fake-stream, and non-ChatGPT control regressions fail without the fix and pass with it.
- [ ] AC-5: Both mapped test files and inherited ChatGPT Responses tests pass with no skips/failures; relevant lint/type checks pass.
- [ ] AC-6: Implementation evidence packet maps every AC and records no product documentation impact.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/` with `SUMMARY.md` and complete test/lint logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Implement exactly the architected two ChatGPT-only guards and focused tests. Keep the four-file application/test scope. Do not build, deploy, edit host files, or commit. Return a signed shared-contract handback with AC-by-AC evidence.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Implemented the two ChatGPT-only stream guards and focused regressions within the authorized four-file source and test scope
- AC-1 through AC-4 and AC-6 pass. AC-5 is blocked only at the repository-wide `make check` gate; all required targeted and inherited test suites pass with no skips or failures
- Verification evidence is under `.staticeng/evidences/TASK-2026-08-18-011-persist-chatgpt-stream-guards/`
- `make check` cannot establish a valid repository baseline because `origin` lacks `litellm_internal_staging`; the fallback against available baselines reports unrelated pre-existing budget deltas
- `staticeng_validate` remains blocked by the documented repository-wide missing and broken CodeMap debt. Baseline repair was not attempted or broadened into this task
- No product documentation update is required. No deployment, host edit, runtime mutation, or commit was performed
- PMA decision on 2026-08-18: hand back with blockers and route the completed implementation to Tech Lead review

## Blocker Report

- Repository gate: `make check` fails while fetching absent remote branch `origin/litellm_internal_staging`; fallback lint-gate runs report unrelated pre-existing budget deltas outside the four-file task scope
- Workflow gate: `staticeng_validate` remains non-green due documented repository-wide CodeMap debt requiring separate baseline repair
- The implementation itself and required targeted suites are green; no additional source work is requested under this task

## Reopen History

### Reopen 1 - 2026-08-18
- Tech Lead independently confirmed source behavior is correct but rejected commit readiness.
- Both modified test files fail `ruff format --check` and must be formatted.
- The async mutation proof must be stabilized so the pre-fix failure reaches the intended stream assertion instead of an incidental callback mock error.
- Correct conflicting evidence claims and rerun the 146-test combined suite, targeted Ruff, formatter check, and `git diff --check`.

## Tech Lead: Reopen 1 Approval
- APPROVED for commit after independent rerun: 146 passed, 0 failed, 0 skipped.
- Formatter, targeted Ruff, and `git diff --check` pass.
- Async mutation proof now fails at the intended outbound stream assertion before the fix and passes after it.
- Unavailable remote baseline and repository-wide CodeMap debt are separately dispositioned and do not block this task-scoped commit.

## PMA Final Closure
- AC-1 through AC-6 passed with Tech Lead approval.
- No product, architecture, or technical documentation update is required.
- Authorized for source commit before release work proceeds.

#### Developer Resolution

- Formatted both modified test files; `ruff format --check` now passes
- Set the async regression's dynamic callback list explicitly to empty. With the async guard temporarily removed, the test now fails at the intended outbound `stream` assertion; the guard was restored immediately afterward
- Corrected the evidence summary, preserved the original failing formatter and mutation logs as historical pre-reopen evidence, and added superseding Reopen 1 logs
- Combined mapped and inherited suite: 146 passed, 0 failed, 0 skipped
- Targeted Ruff and `git diff --check`: pass
- No baseline or CodeMap repair, deployment, host edit, runtime mutation, or commit was performed
