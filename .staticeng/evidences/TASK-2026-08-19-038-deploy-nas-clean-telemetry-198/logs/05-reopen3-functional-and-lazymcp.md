# Reopen 3 Functional And LazyMCP

All four Responses probes returned HTTP 200 `text/event-stream`, nine valid events, exactly one ordered created/in-progress/completed lifecycle, zero blocked errors, and the expected deployment ID

| Probe | HTTP | SSE lifecycle | Selection | Quota disposition |
|---|---:|---|---|---|
| Native default with client `stream=false` | 200 | PASS | default-qualified | successful |
| Direct default | 200 | PASS | default-qualified | successful |
| Direct account2 | 200 | PASS | account2-qualified | successful |
| Public `gpt-5.6-sol` | 200 | PASS | public deployment backed by default `chatgpt/gpt-5.6-sol` | successful |

The prior public failure was a harness expectation defect: it compared the selected public deployment ID with the separate qualified-default deployment ID. Reopen 3 persisted status, content type, lifecycle, blocked errors, provider model, and selected deployment independently

LazyMCP:

- Protocol `2025-11-25`: PASS
- Exact gateway tools `mcp_call`, `mcp_describe`, `mcp_status`: PASS
- `mcp_status`: PASS
- Current configured `Memory` / `memory-find` describe: PASS
- Harmless configured memory call: PASS

Result: **PASS**
