---
id: TASK-2026-08-26-015-implement-020-model-contracts
complexity: complex
track: implementation
slice: core
status: done
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 1
---

# Task: TASK-2026-08-26-015 - Implement 0.2.0 Model Contracts

## Objective
Implement the approved internal model-contract catalog in `opencode-litellm@0.2.0` without changing runtime configuration, OpenCode core, Codex, or LiteLLM.

## Governing Artifacts
- `.staticeng/docs/scrs/SCR-2026-08-26-002-client-model-contracts-020.md`
- `.staticeng/docs/plans/client-model-contracts-020-plan.md`

## Acceptance Criteria
- [ ] T1-AC-1: Package version is `0.2.0`; one immutable typed catalog contains every exact active/retired alias from the SCR with no collision.
- [ ] T1-AC-2: Every active discovered alias maps to exact ordered modes, official default metadata, and exact legacy/V2 bodies; absent aliases are not fabricated.
- [ ] T1-AC-3: Near-matches, future namespaces, `defend/gpt-5.5`, and unlisted names do not inherit a contract.
- [ ] T1-AC-4: GPT-5.6 includes `max`; GPT-5.4/Mini/5.5/Spark do not; no contract emits `ultra`.
- [ ] T1-AC-5: DeepSeek and Qwen Off serialize exactly as approved, with no Qwen reasoning effort.
- [ ] T1-AC-6: Incomplete/conflicting discovery cannot weaken built-in defaults; explicit model/provider overrides apply last for known and unknown models.
- [ ] T1-AC-7: Normal GPT-5.3 Codex aliases are filtered while every discovered Spark alias remains.
- [ ] T1-AC-8: Legacy/V2 outputs are semantically equivalent and UI-only metadata never reaches requests.
- [ ] T1-AC-9: Build, full tests, pack dry-run, tracked-dist comparison, package inventory, and official OpenCode isolated behavior pass.
- [ ] T1-AC-10: README, architecture docs, tests, evidence, and CodeMaps match implementation; unrelated StaticEng/worktree artifacts remain untouched.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-26-015-implement-020-model-contracts/` with `SUMMARY.md` and redacted logs mapping T1-AC-1 through T1-AC-10.

## Rollback
Revert only the task-owned plugin commit before release. This task has no runtime/client mutations.

## Reopen History

### Reopen 1 - 2026-08-26
- Architecture review rejected release because catalog `v2Body` is validated but runtime V2 rendering reconstructs payloads from legacy instead of consuming `v2Body` directly.
- Code review rejected release because catalog `defaultMode` is not consumed; official OpenCode without an explicit variant sends generic `medium` for every GPT row, breaking GPT-5.4, Mini, and Spark defaults.
- Required correction: render built-in V2 bodies directly from the catalog, make every contract row's default effective through supported plugin metadata/options without OpenCode core changes, preserve user-last overrides, and add fresh official-client default-wire tests for all nine contract rows.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Implementation completed in `/home/staticduo/git/opencode-litellm` without staging, committing, pushing, publishing, or changing runtime configuration.
- Exact task-owned implementation paths are listed in `.staticeng/evidences/TASK-2026-08-26-015-implement-020-model-contracts/SUMMARY.md`.
- Verification completed: clean `npm ci`, build, **59/59** tests with no skips, deterministic tracked-dist rebuild comparison, pack dry-run, 19-file package inventory, content scans, and official OpenCode **1.18.23** isolated legacy/V2/wire checks.
- Candidate artifact SHA-256: `0c7b349213ba9998975e3c7062cf68970452dbfa009da36b97d115ff48789b77`.
- Documentation closure completed in README, architecture documentation, and root/source/test CodeMaps.
- `staticeng_validate` remains blocked by unrelated pre-existing missing CodeMaps in the governing LiteLLM workspace. Required repair dry-run was performed; safe apply was withheld because it proposed unrelated generated/runtime mutations and still required broad manual architecture decisions. See evidence log `10-staticeng-validation.log`.
- Pre-existing unrelated dirty and untracked implementation-repository `.staticeng` artifacts remain unstaged and otherwise untouched.

### Reopen 1 - Developer Correction

- Corrected built-in V2 rendering to use each `ModelContractMode.v2Body` directly; generic legacy derivation remains for unknown and user-defined variants.
- Applied each row's `defaultMode` through plugin-generated model options. Explicit named variants merge afterward, and explicit model/provider overrides can replace the default.
- Added Qwen explicit-Off request cleanup so the model-level `xhigh` default cannot leak alongside `chat_template_kwargs.enable_thinking=false`.
- Verification completed: clean install/build, **62/62** tests with no skips, deterministic dist comparison, 19-file package inventory, content scans, and **55/55** fresh official OpenCode 1.18.23 strict-loopback probes (**9 defaults + 46 explicit modes**).
- Reopen 1 candidate artifact SHA-256: `40b2ce710ec8cba570742d8f86c541ef06dba0e8d119db0d66bb91185487fcba`.
- No staging, commit, push, publish, runtime configuration, OpenCode core, Codex, or LiteLLM mutation occurred.
