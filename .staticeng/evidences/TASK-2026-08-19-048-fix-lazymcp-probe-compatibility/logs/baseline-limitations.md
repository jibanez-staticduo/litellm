# Baseline Limitations

## Broader MCP Directory

`uv run --no-sync pytest tests/test_litellm/proxy/_experimental/mcp_server -q` was attempted. It exposed failures in unrelated test modules and exceeded the 20-minute command limit at roughly 49 percent completion. The directly mapped `test_mcp_server.py` suite passes all 242 tests with no skips

## Type Check

Direct `basedpyright` checks on `server.py` and its 9,000-line mapped test file report hundreds of existing strict-type errors throughout those files. The added source is covered by Ruff, compile checks, and passing regressions. No type suppression or budget change was introduced

The repository's delta budget gates also fail because the shared worktree includes concurrent source changes across ChatGPT, Responses, routing, proxy auth, spend tracking, and MCP files relative to `origin/litellm_internal_staging`. Their reports include existing findings in `server.py`, but no finding points to the new compatibility helper. No unrelated budget or concurrent source file was changed

## StaticEng Validation

`staticeng_validate` reports broken references in `.staticeng/codemap.yml` and missing CodeMaps throughout the repository. `staticeng_repair` dry-run proposes hundreds of unrelated CodeMap files and changes to concurrent StaticEng artifacts, so applying it would violate the task's minimum-change boundary and shared-worktree safety
