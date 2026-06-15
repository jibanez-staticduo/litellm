# TASK-2026-06-08-002 Evidence Summary

## Changes

- `resolve_ui_session_team_ids()` now handles cached user objects returned as dicts, model objects, or unexpected objects without a `teams` attribute while preserving duplicate/empty team filtering.
- Legacy `/spend/logs` with no filters now fails fast with a 400 `ProxyException` that directs callers to `/spend/logs/v2` with `start_date`, `end_date`, `page`, and `page_size` instead of calling unbounded `get_data(table_name="spend", query_type="find_all")`.
- Legacy `/spend/logs` list paths with filters now avoid `messages`, `response`, and `proxy_server_request` unless `request_id` is provided, preserving request-specific detail behavior. The lightweight projection keeps `request_id`, which is the primary key for `LiteLLM_SpendLogs` and the identifier used by detail routes.

## Acceptance Criteria

- AC-1: Covered. MCP UI session team resolution uses dict-safe `teams` access and `getattr(..., None)` for non-dict objects.
- AC-2: Covered. Added `test_resolve_ui_session_team_ids_handles_dict_user_object`.
- AC-3: Covered. No-filter legacy `/spend/logs` raises a clear 400 instead of unbounded full-table fetch.
- AC-4: Covered. Filtered legacy list paths use a lightweight raw SQL projection excluding `messages`, `response`, and `proxy_server_request`; `request_id` still uses the existing full-row path.
- AC-5: Covered. Added no-filter safety test and adjusted the summarize=false test mock for the lightweight list query.
- AC-6: Covered. Focused tests passed; see `.staticeng/evidences/TASK-2026-06-08-002-fix-mcp-teams-and-spend-logs/logs/tests.log`.
- AC-7: No product docs required for this operational bugfix. API callers using deprecated no-filter `/spend/logs` should switch to `/spend/logs/v2` with date range and pagination.

## Heavy Column Notes

Production evidence showed `LiteLLM_SpendLogs` was about 56 GB with average `response` around 100 KB and average `proxy_server_request` around 73 KB. The old no-filter path selected every row and every column, including heavy TOAST-backed payload columns, which could timeout or overload production. The fix rejects the unbounded path and keeps legacy filtered list responses lightweight.

## Verification

- `uv run pytest tests/test_litellm/proxy/_experimental/mcp_server/test_ui_session_utils.py tests/test_litellm/proxy/spend_tracking/test_spend_management_endpoints.py::test_view_spend_logs_without_filters_rejects_unbounded_query tests/test_litellm/proxy/spend_tracking/test_spend_management_endpoints.py::test_view_spend_logs_summarize_parameter`
- `uv run ruff check litellm/proxy/_experimental/mcp_server/ui_session_utils.py litellm/proxy/spend_tracking/spend_management_endpoints.py tests/test_litellm/proxy/_experimental/mcp_server/test_ui_session_utils.py tests/test_litellm/proxy/spend_tracking/test_spend_management_endpoints.py`
- Result: 10 tests passed and ruff passed.
