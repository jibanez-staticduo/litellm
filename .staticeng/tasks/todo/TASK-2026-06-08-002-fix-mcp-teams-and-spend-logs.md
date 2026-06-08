---
id: TASK-2026-06-08-002
title: Fix LiteLLM MCP UI session teams and spend logs timeout
status: active
complexity: standard
track: implementation
slice: logic
assigned_to: developer
handoff_from: product_manager
created_at: 2026-06-08
scr: none
parent: TASK-2026-06-08-001
---

# Task: Fix LiteLLM MCP UI Session Teams and Spend Logs Timeout

## Classification

- Complexity: `standard`
- Track: `implementation`
- Slice: `logic`

## Production Evidence

Production LiteLLM image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260601`.

Live symptoms:

- MCP edit/list/health routes return 500.
- Recent logs show repeated `AttributeError: 'dict' object has no attribute 'teams'` from `ui_session_utils.py` while resolving UI session teams.
- `/spend/logs` without filters times out.
- `LiteLLM_SpendLogs` is ~56 GB / ~724k rows.
- Recent 1000-row sample shows heavy columns are significant: avg `response` ~100 KB and avg `proxy_server_request` ~73 KB, max `proxy_server_request` ~550 KB. So yes, storing content/payloads in spend logs is a major contributor to legacy spend-log timeout.

## Required Fixes

1. Make MCP UI session team resolution dict/object safe.
2. Make legacy `/spend/logs` safe enough not to hang production when called without filters, while preserving supported paginated endpoints.
3. Prefer using `/spend/logs/v2` or `/spend/logs/ui` for UI/admin callers where applicable.
4. Avoid returning heavy content columns in list responses unless a detail endpoint explicitly asks for one request.

## Acceptance Criteria

- AC-1: `resolve_ui_session_team_ids()` handles cached user objects that are dicts or model objects and does not use direct `.teams` only.
- AC-2: Add focused regression coverage for dict user object with `teams` in MCP UI session team resolution.
- AC-3: Legacy `/spend/logs` without any filters no longer performs an unbounded full-table/full-row fetch. It must either reject with clear guidance to use `/spend/logs/v2` with date range/pagination, or internally route to a bounded/paginated lightweight query.
- AC-4: Legacy `/spend/logs` list paths avoid selecting heavy columns (`messages`, `response`, `proxy_server_request`) unless querying a specific `request_id`/detail path.
- AC-5: Add/adjust tests for the `/spend/logs` no-filter safety behavior and any lightweight-list behavior changed.
- AC-6: Run focused tests for MCP UI session utils and spend logs endpoint behavior.
- AC-7: Document whether product docs need updates; otherwise state no docs required for operational bugfix.

## Constraints

- Do not mutate production data.
- Do not deploy unless PMA explicitly authorizes after review.
- No secrets in logs/evidence.
- Keep scope to the two production bugs.
- Preserve existing production fork branch structure.

## Expected Evidence

Create/update `.staticeng/evidences/TASK-2026-06-08-002-fix-mcp-teams-and-spend-logs/` with:

- `SUMMARY.md` mapping AC-1..AC-7.
- `logs/tests.log` with focused test output.
- `logs/diff-stat.log`.
- Any notes on why heavy spend-log columns caused timeout.

## Handoff

[Agent Message] From: product_manager To: developer

Please fix the production LiteLLM MCP edit crash and spend-log timeout root causes on `staticduo-production-main`. Implement dict-safe MCP UI session team access, make legacy `/spend/logs` safe from unbounded heavy fetches, add focused tests, and produce evidence. Do not deploy.
