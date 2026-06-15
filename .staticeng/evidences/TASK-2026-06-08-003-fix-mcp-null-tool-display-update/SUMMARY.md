# TASK-2026-06-08-003 Evidence Summary

## Summary

Implemented a focused MCP update fix so explicit `null` values for optional tool override map fields are stripped from Prisma update payloads. Non-null maps still serialize and write normally, and `{}` still serializes to `{}` for explicit clears.

## Changed Files

- `litellm/proxy/_experimental/mcp_server/db.py`
- `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_partial_update.py`

## Verification

- `uv run python -m pytest tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_partial_update.py` passed: 9 tests.
- `uv run python -m ruff check litellm/proxy/_experimental/mcp_server/db.py tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_partial_update.py` passed.

## Evidence Logs

- `.staticeng/evidences/TASK-2026-06-08-003-fix-mcp-null-tool-display-update/logs/tests.log`
- `.staticeng/evidences/TASK-2026-06-08-003-fix-mcp-null-tool-display-update/logs/diff-stat.log`

## Notes

No production deploy, push, commit, or production DB mutation was performed.
