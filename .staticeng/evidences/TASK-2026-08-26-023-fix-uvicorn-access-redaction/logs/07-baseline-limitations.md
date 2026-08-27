# Baseline Limitations

## Delta-aware type gate

`uv run --no-sync python scripts/type_check_gate.py --base origin/litellm_internal_staging` reported aggregate increases in six rules. This shared-worktree comparison includes concurrent changes outside this task's two implementation files. A direct basedpyright diagnostic filter over the exact changed regions reports zero diagnostics in `05-changed-region-type-check.log`

Reopen 1 repeated both checks with the same aggregate shared-worktree result in `14-reopen1-type-check-gate.log` and zero scoped diagnostics in `12-reopen1-changed-region-type-check.log`

## StaticEng validation

`staticeng_validate` reports the repository's existing missing-CodeMap backlog across provider, test, UI, packaging, and documentation directories. The approved design explicitly excludes CodeMap changes, and the handoff requires preserving concurrent untracked CodeMaps, so no repair was applied
