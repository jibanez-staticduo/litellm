# TASK-2026-08-27-008 Evidence Summary

## Summary

PASS. Governing documentation now yields one final contract directly: `@staticeng/opencode-litellm@0.2.2`, official OpenCode `1.18.23`, Codex `0.149.1`, eight retained families and Codex rows, normal and Spark GPT-5.3 retired everywhere, NAS defend retired, explicit official-default transmission, and explicit model/provider overrides applied last

This was documentation-only work. No runtime, source, plugin artifact, client configuration, route, cache, process, database, credential, or secret-bearing evidence changed

## Work Performed

- Rewrote the approved SCR so its normative matrix, aliases, precedence, client behavior, retirement state, and AC-1 through AC-14 describe the final deployed state without relying on append-only corrections
- Recast the plan as a completed execution record with final architecture, completed sequence, current gates, rollback boundaries, traceability, and clearly non-normative superseded decisions
- Labeled Task 017's plugin `0.2.1`, nine-family, Spark-preserving, and default-omission evidence as a successful historical intermediate snapshot
- Labeled Task 018's nine-row Spark-preserving Codex evidence as a successful historical intermediate snapshot
- Kept Task 019's final PASS authoritative and moved its obsolete preservation-gate stop reason into clearly superseded history
- Corrected Task 005's arithmetic-only OpenCode total to 41 named plus eight default captures per source, 98 total, matching its evidence index and Task 020 audit
- Completed and moved Task 008 from `todo` to `done`; no separate task registry artifact exists in the repository

## Acceptance Criteria Coverage

- **AC-1: PASS.** The normative SCR uses plugin `0.2.2`, official OpenCode `1.18.23`, Codex `0.149.1`, eight retained rows, dual GPT-5.3 retirement, NAS defend retirement, explicit official defaults, and user-last override precedence
- **AC-2: PASS.** The completed plan states the final `0.2.2`/Spark-retired/eight-row outcome and labels earlier releases, Spark preservation, Codex `0.147`, nine-row state, omission semantics, and the initial stop as non-normative history
- **AC-3: PASS.** Task 017 and 018 summaries identify their intermediate state explicitly and point to Tasks 004, 005, 019, and 020 for final client, runtime, registry, and closure truth
- **AC-4: PASS.** Task 019 opens with one final PASS and final AC trace; the earlier HTTP-400 stop is labeled a superseded intermediate event that does not qualify final closure
- **AC-5: PASS.** Task 008 frontmatter and location record `done`; the plan records `completed`; the approved SCR remains `approved` for PMA-owned final closure; no implementation or runtime artifact changed

## Verification

- `git diff --check`: PASS
- Targeted contradiction scans: PASS; governing SCR/plan contain no normative Spark-preservation, Codex `0.147`, `0.2.0` activation, or intrinsic-default-omission statement
- `staticeng_validate`: FAIL only on the established repository-wide missing-CodeMap backlog outside this documentation task
- `staticeng_repair` dry-run: confirms unresolved CodeMaps require module-boundary decisions; no broad repair was applied

## Documentation Impact

Changed exactly these documentation artifacts

- `.staticeng/docs/scrs/SCR-2026-08-26-002-client-model-contracts-020.md`
- `.staticeng/docs/plans/client-model-contracts-020-plan.md`
- `.staticeng/evidences/TASK-2026-08-26-017-migrate-shared-opencode-contracts/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-08-26-018-align-codex-model-contracts/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-08-26-019-retire-obsolete-model-routes/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-08-27-005-independent-runtime-gates/SUMMARY.md`
- `.staticeng/tasks/done/TASK-2026-08-27-008-reconcile-final-contract-docs.md`
- `.staticeng/evidences/TASK-2026-08-27-008-reconcile-final-contract-docs/SUMMARY.md`

The former `.staticeng/tasks/todo/TASK-2026-08-27-008-reconcile-final-contract-docs.md` was moved to the `done` path above

## Open Risks

- Offline Syncthing peers still require automatic convergence and normal cache refresh when reachable
- npm trusted publishing retains its known authorization defect; release `0.2.2` used the approved protected fallback after exact artifact verification
- The unrelated repository-wide CodeMap backlog remains outside this documentation-only scope

## Recommended Next Step

PMA should hand the reconciled contract to final architecture and Tech Lead closure review, then decide final SCR closure

[Agent Message] From: business_analyst To: product_manager

Documentation reconciliation PASS. AC-1 through AC-5 are satisfied with no runtime/source/config changes; final architecture and Tech Lead closure may resume
