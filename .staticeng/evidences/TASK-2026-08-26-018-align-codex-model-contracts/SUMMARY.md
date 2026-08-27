# TASK-2026-08-26-018 Evidence Summary

## Historical Intermediate Summary

Reopen 1 completed successfully under authoritative Codex `0.149.1`. This packet is a historical intermediate snapshot, not the final catalog state: it validated nine rows while Spark was still retained. The active DeepSeek `high` configuration and every unrelated config byte remained unchanged, and fresh isolated app-server/model-list and loopback-only Responses validation passed without production inference, binary changes, generated-cache edits, or termination of historical user processes

Task 004 later removed only the Spark row, leaving the authoritative eight-row Codex `0.149.1` catalog. Task 005 independently verified all eight final rows and wire efforts, and Task 020 provides the final SCR PASS trace. Task 019 proves final registry retirement

## Work Performed

- Recorded current Codex version/processes, active DeepSeek `high`, file modes, checksums, and cache baseline
- Created fresh owner-only mode `0600` Reopen 1 backups for config, custom catalog, and generated cache
- Atomically changed only catalog `default_reasoning_level` and `supported_reasoning_levels` fields
- Proved row order and every unrelated catalog field remained equal to the Reopen 1 backup
- Proved `config.toml` remained byte-identical to its Reopen 1 backup
- Initialized fresh isolated Codex 0.149.1 app-server processes and verified all nine `model/list` rows
- Captured all 45 distinct row/mode requests plus five explicit cross-row switches through a loopback-only Responses endpoint

## Acceptance Criteria Coverage

- T4-AC-1: PASS. Fresh protected backups exist; nine retained families include Spark and exclude normal GPT-5.3
- T4-AC-2: PASS. GPT lists/defaults, DeepSeek `none/low/high/max`, and Qwen `low/medium/xhigh` are exact; no `ultra` exists
- T4-AC-3: PASS. Active model remains DeepSeek with valid `high`; custom catalog, NAS Responses provider, `[execution]`, and unrelated config are byte-identical
- T4-AC-4: PASS. JSON/TOML parse; fresh isolated Codex 0.149.1 app-server initialization and `model/list` pass; fresh PID/version recorded; production generated cache hash/mtime remained unchanged
- T4-AC-5: PASS. Forty-five distinct row/mode captures prove every exposed exact Responses effort, including GPT `none`, GPT-5.6 `max`, DeepSeek `none`, and Qwen `xhigh`
- T4-AC-6: PASS. Selector and wire evidence contain no DeepSeek `off`, Qwen Off, or `ultra`; five cross-row captures prove requested row effort replaces the global DeepSeek `high`
- T4-AC-7: PASS. Backups, modes, checksums, atomic scope, rollback, process isolation, and cache non-mutation are evidenced without credentials or response content

## Documentation Impact

This packet preserves the completed nine-row alignment as history. Its Spark-preserving and nine-row statements are non-normative; use the final SCR/plan and Tasks 004/005/019/020 for current state

## Open Risks

- Historical Codex 0.147 processes continue by explicit scope and were not killed; they are not authoritative validation gates
- Production generated cache retains its pre-existing permissive mode, but this task did not write, remove, or chmod it
- `staticeng_validate` remains blocked by the pre-existing repository-wide missing-CodeMap backlog; dry-run repair requires unrelated module-boundary decisions

## Recommended Next Step

Task 018 remains closed as a successful intermediate alignment. Use Tasks 004/005/019/020 for the final eight-row state
