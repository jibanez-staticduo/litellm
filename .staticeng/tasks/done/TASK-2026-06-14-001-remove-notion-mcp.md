---
task_id: TASK-2026-06-14-001-remove-notion-mcp
complexity: tiny
track: implementation
slice: foundation
status: done
assigned_to: product_manager
handoff_from: user
scr: null
parent: null
---

# Remove Notion MCP from LiteLLM

## Request
User asked to remove the Notion MCP from the LiteLLM stack after logs showed repeated Notion MCP OAuth/port-conflict failures.

## Acceptance Criteria
AC-1: The Notion MCP server registration is removed from LiteLLM.
AC-2: LiteLLM MCP server list no longer includes alias `notion`.
AC-3: No Docker restart or unrelated service mutation is performed unless separately authorized.

## Expected Evidence
- LiteLLM admin delete response.
- LiteLLM admin MCP list check after deletion.
- Short residual process/log observation if available.

## Safety Notes
- User explicitly authorized removal with: "quita el mcp de notion".
- This is classified as a tiny, user-authorized operational change; no SCR required.

# Post Implementation Task Updates

## Product Manager: Post Implementation Expectations
- Removed LiteLLM MCP server registration for Notion via LiteLLM admin API.
- Verified the MCP server list no longer includes alias `notion`.
- Cleaned residual Notion `mcp-remote` child processes inside the LiteLLM container to stop the immediate error loop.
- Verified LiteLLM stack remained healthy after cleanup.

## Acceptance Criteria Coverage
- AC-1: Passed. Delete returned accepted status.
- AC-2: Passed. Follow-up MCP list did not include `notion`.
- AC-3: Passed. No Docker restart was performed.

## Documentation Impact
No product documentation required for this tiny operational removal.
