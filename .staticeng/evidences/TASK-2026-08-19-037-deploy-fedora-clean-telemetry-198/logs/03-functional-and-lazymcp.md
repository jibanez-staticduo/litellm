# Corrected Functional And LazyMCP Gates

All Responses probes used list input, `reasoning.context=all_turns`, reasoning effort `high`, reasoning summary `detailed`, `store=false`, encrypted reasoning inclusion, disabled parallel tool calls, the Codex Responses Lite header, a 180-second bound, and no client retry

| Probe | HTTP | Content type | Completed | Blocked errors | Selected account2 |
|---|---:|---|---:|---:|---|
| Native account2 with client `stream=false` | 200 | `text/event-stream` | 1 | 0 | true |
| Qualified regular profile | 200 | `text/event-stream` | 1 | 0 | true |
| Direct account2 | 200 | `text/event-stream` | 1 | 0 | true |
| Public `gpt-5.6-sol` fallback | 200 | `text/event-stream` | 1 | 0 | true |

The qualified regular and public routes completed through the configured account2 fallback under the preserved primary-profile quota disposition. Exact account2 deployment selection proves profile isolation

LazyMCP results:

- Protocol `2025-11-25`
- Exact gateway tools: `mcp_call`, `mcp_describe`, `mcp_status`
- `mcp_status`: pass
- `mcp_describe` for `defend_memory-find`: pass
- Harmless `mcp_call` to `defend_memory-find`: pass

Reproducible sanitized probes are retained as `functional-probe.sh` and `lazymcp-probe.sh`. They source credentials in-place and never print secret values or response content

Result: **PASS**
