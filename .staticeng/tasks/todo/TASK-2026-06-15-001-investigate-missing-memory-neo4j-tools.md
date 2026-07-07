---
id: TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools
complexity: standard
track: investigation
slice: logic
status: done
scr: null
parent: null
assigned_to: explorer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-06-15-001 - Investigate Missing Memory Neo4j MCP Tools

## Classification
- complexity: standard
- track: investigation
- slice: logic

## Discussion Record
- Active discussion: DISCUSSION-003 (`.staticeng/.config/runtime/discussions/DISCUSSION-003-transcript.md`)

## Objective
Determine why `https://litellm.staticduo.com/v1/mcp/tools` does not return the `neo4j_expand_neighbors` and `neo4j_shortest_paths` tools even though the LiteLLM UI shows them under the Memory MCP server.

## Context
Observed runtime endpoint with the configured OpenCode LazyMCP key returns 516 tools and includes Memory/Neo4j tools such as `memory-neo4j_read_cypher`, `memory-neo4j_write_cypher`, `neo4j-read_cypher`, and `neo4j-write_cypher`, but not `neo4j_expand_neighbors` or `neo4j_shortest_paths`.

The LiteLLM UI screenshot shows the Memory MCP server listing 19 tools, including `neo4j_expand_neighbors` and `neo4j_shortest_paths`.

## Scope
Investigate only. Do not implement code changes unless PMA creates a follow-up implementation task.

Review:
- LazyMCP tool-listing and prefixing logic in this repository.
- LiteLLM MCP server/admin UI tool listing logic if present in this repository.
- Relevant runtime configuration such as MCP server definitions, tool filters, access groups, virtual key/team filters, and caching.
- Relevant non-secret logs from the local/runtime LiteLLM deployment, if accessible.

Do not expose API keys, tokens, cookies, or secrets in output or evidence.

## Acceptance Criteria
- [ ] AC-1: Identify the code path used by `/v1/mcp/tools` for tool enumeration and any filtering/prefixing that applies.
- [ ] AC-2: Identify the code path or API likely used by the UI Memory MCP Tools page and how it differs from `/v1/mcp/tools`.
- [ ] AC-3: Check logs/configuration for evidence of stale cache, server mismatch, toolset/access-group filtering, naming normalization, or registration drift.
- [ ] AC-4: Provide the most likely root cause with confidence level and concrete next diagnostic or fix steps.
- [ ] AC-5: Record evidence without secrets.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/` with:
- `SUMMARY.md` mapping AC-1 through AC-5 to findings.
- `logs/` containing sanitized command outputs, search summaries, and relevant log excerpts.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - Method: code inspection
  - Evidence: `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/SUMMARY.md`
- [ ] AC-2
  - Method: code inspection and endpoint comparison
  - Evidence: `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/SUMMARY.md`
- [ ] AC-3
  - Method: config/log inspection
  - Evidence: `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/logs/`
- [ ] AC-4
  - Method: investigation synthesis
  - Evidence: `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/SUMMARY.md`
- [ ] AC-5
  - Method: evidence review
  - Evidence: `.staticeng/evidences/TASK-2026-06-15-001-investigate-missing-memory-neo4j-tools/`

## Reopen History

### Reopen 1 - Exact OpenCode Key Still Missing Prefixed Tools
After the first investigation, PMA re-ran `/v1/mcp/tools` with the exact configured OpenCode LazyMCP key from `/home/staticduo/.config/opencode/opencode.json`. The endpoint returned 516 tools and still did not include `memory-neo4j_expand_neighbors` or `memory-neo4j_shortest_paths`. Continue same-scope investigation to identify the key-specific permission, route, team/org, cache, or gateway reason.

## PMA Handoff
[Agent Message] From: product_manager To: explorer
Please investigate why the runtime MCP tools endpoint omits `neo4j_expand_neighbors` and `neo4j_shortest_paths` while the LiteLLM UI shows those Memory MCP tools. This is investigation only. Read the task frontmatter first, inspect relevant code/config/logs, avoid secrets, and return a signed handoff with Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, and Recommended Next Step.
