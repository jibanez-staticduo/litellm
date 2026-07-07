---
id: DISCUSSION-003
title: "Investigate missing memory Neo4j MCP tools"
status: closed
summarized_by: business_analyst
source: runtime-transcript
---

# Discussion Summary

## Topic
Missing `neo4j_expand_neighbors` and `neo4j_shortest_paths` tools from the runtime MCP tool catalog despite broader MCP access being restored.

## Purpose
Determine why two Neo4j navigation tools visible in the admin/UI view for the `Memory` server are not exposed through the runtime `/v1/mcp/tools` endpoint for the current key/routing path.

## Repository Truth Relevant To This Discussion
- The investigation concerns LiteLLM MCP/LazyMCP runtime tool exposure and the memory/Neo4j MCP server integration.
- The runtime endpoint checked was `/v1/mcp/tools`.
- The admin/UI view reportedly shows `neo4j_expand_neighbors` and `neo4j_shortest_paths` under the `Memory` server.
- The runtime catalog for the current key returns 516 tools but does not include those two navigation tools.
- Restarting LiteLLM and OpenCode did not change the runtime catalog result.

## Facts Established
- An earlier MCP/LiteLLM check was aborted during or around a system restart/gateway instability, so the original key state was not fully verified.
- After the user changed the key, `/v1/mcp/tools` returned 516 tools, indicating broad MCP access was restored or expanded.
- The following tools were still absent from `/v1/mcp/tools` after the key change:
  - `neo4j_expand_neighbors`
  - `neo4j_shortest_paths`
- The runtime check after key change produced:
  - `total_tools: 516`
  - `has_expand: false`
  - `has_shortest: false`
- Runtime-visible memory/Neo4j-related tools included:
  - `memory-find`
  - `memory-find2`
  - `memory-find-rating`
  - `memory-find_rating`
  - `memory_find_rating`
  - `memory-get_session_raw`
  - `memory-get_session_summary`
  - `memory-health`
  - `memory-list_environments`
  - `memory-list_sources`
  - `memory-metrics`
  - `memory-neo4j_get_schema`
  - `memory-neo4j_read_cypher`
  - `memory-neo4j_write_cypher`
  - `memory-retry_pending_store_operations`
  - `memory-retry_store_operation`
  - `memory-store`
  - `neo4j-get_schema`
  - `neo4j-read_cypher`
  - `neo4j-write_cypher`
- After the user restarted LiteLLM and OpenCode, `/v1/mcp/tools` still returned 516 tools and still did not include `neo4j_expand_neighbors` or `neo4j_shortest_paths`.
- After restart, runtime-visible related tools specifically included:
  - `memory-neo4j_get_schema`
  - `memory-neo4j_read_cypher`
  - `memory-neo4j_write_cypher`
  - `neo4j-get_schema`
  - `neo4j-read_cypher`
  - `neo4j-write_cypher`
- The user requested code and log investigation to explain why the two tools are not visible.

## Requirements Captured
- Investigate code and logs to determine why `neo4j_expand_neighbors` and `neo4j_shortest_paths` are missing from runtime `/v1/mcp/tools`.
- Compare runtime tool catalog behavior with admin/UI tool visibility for the `Memory` server.
- Preserve key secrecy; do not print or store full API keys in outputs or artifacts.
- Identify whether the issue is caused by stale cache/versioning, backend/transport/config mismatch, access filtering, naming/normalization, registration, or another runtime catalog path problem.
- Provide evidence from code paths, configuration, and logs rather than guessing.

## Constraints
- The current key has broad MCP access as evidenced by 516 visible runtime tools, so the issue is not simply lack of general MCP access.
- LiteLLM and OpenCode were restarted and the missing-tool state persisted.
- Investigation should use safe handling for secrets; only redacted key references such as prefix/suffix are acceptable.
- The runtime endpoint of concern is `/v1/mcp/tools`.
- The discrepancy involves the `Memory` server admin/UI view versus runtime catalog publication.

## Non-Goals
- Do not rotate or expose API keys as part of the summary or investigation output.
- Do not assume the missing tools are intentionally unavailable without verifying code/config/log evidence.
- Do not implement a fix before the cause is understood and PMA authorizes implementation work.
- Do not treat broad MCP access as proof that the specific tool discrepancy is resolved.

## Decisions Made
- The changed key resolved or improved broad MCP visibility but did not resolve the two missing Neo4j navigation tools.
- Restarting LiteLLM and OpenCode did not resolve the runtime catalog discrepancy.
- The current working hypothesis is that the problem is specific to runtime publication/cataloging for these tools, not a general access group failure.
- The next step is a code and logs investigation.

## Assumptions
- The admin/UI view is accurately showing `neo4j_expand_neighbors` and `neo4j_shortest_paths` for the `Memory` server.
- The runtime checks against `/v1/mcp/tools` were made with the relevant current key and route.
- The 516-tool count is stable across the key-change and post-restart checks.
- Tool names listed in the transcript are exact enough to use for repository and log searches.

## Open Questions
- Are `neo4j_expand_neighbors` and `neo4j_shortest_paths` actually registered by the active runtime `Memory` MCP server process?
- Does `/v1/mcp/tools` read from a stale cache, different backend, different transport, or different config than the admin/UI view?
- Are the missing tools filtered by access groups, allowed tool lists, server aliases, naming normalization, or hidden-tool rules despite broad MCP access?
- Are the tools present in an administrative registry but absent from the live MCP server's tool list response?
- Are there errors in LiteLLM, LazyMCP, OpenCode, or memory MCP logs when loading or exposing those specific tools?
- Is there a naming mismatch between underscore-style names (`neo4j_expand_neighbors`) and hyphen/prefix-style runtime names such as `memory-neo4j_*` or `neo4j-*`?

## Risks Or Concerns
- Later agents may incorrectly focus on API key permissions even though broad access has already been restored and the issue persisted.
- Stale runtime cache or split admin/runtime data sources could make UI visibility misleading.
- A fix in the wrong layer could expose unintended MCP tools if access filtering is bypassed rather than corrected.
- Logs may contain sensitive key material or tokens and must be handled/redacted carefully.
- Restarting services alone is unlikely to fix the issue based on current evidence.

## Referenced Files Or Areas
- `.staticeng/.config/runtime/discussions/DISCUSSION-003-transcript.md`
- LiteLLM MCP endpoint handling for `/v1/mcp/tools`
- LazyMCP gateway/tool catalog code paths
- MCP server registration and admin/UI registry code paths
- `Memory` MCP server configuration and tool registration
- Neo4j MCP tool registration for schema/read/write/navigation tools
- LiteLLM, LazyMCP, OpenCode, and memory MCP runtime logs
- Access group or allowed-tool filtering configuration for MCP tools

## Recommended Workflow Next Step
- assigned_to: explorer
- why: Perform a read-only repository and log investigation to map the `/v1/mcp/tools` runtime catalog path, compare it to admin/UI registry behavior, and identify where `neo4j_expand_neighbors` and `neo4j_shortest_paths` are lost before any implementation work is scoped.
