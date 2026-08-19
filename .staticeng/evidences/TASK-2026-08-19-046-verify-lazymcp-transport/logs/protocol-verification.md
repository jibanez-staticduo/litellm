# Sanitized Protocol Verification

## Official Semantics

Source reviewed: `https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http`

- Client JSON-RPC messages use HTTP POST
- POST clients advertise both `application/json` and `text/event-stream`
- Successful JSON-RPC notifications return HTTP 202
- JSON-RPC requests return either JSON or SSE
- GET optionally opens a server-to-client SSE stream and must advertise `Accept: text/event-stream`
- HEAD is not defined as a Streamable HTTP MCP operation
- When a server issues `MCP-Session-Id` during initialize, the client sends it on subsequent requests; NAS LazyMCP is configured stateless and does not issue one

## Fresh NAS Flow

| Check | Result |
|---|---|
| Initialize HTTP | 200 |
| Negotiated protocol | `2025-11-25` |
| Session issued | no, expected for stateless LazyMCP |
| Initialized notification HTTP | 202 |
| Tools/list HTTP | 200 |
| Exact gateway tools | `mcp_call`, `mcp_describe`, `mcp_status` |
| `mcp_status` | pass |
| Bounded `memory` / `memory-find` describe | pass |
| Harmless delegated `memory-find` call | pass |
| Generic GET with `Accept: */*` | 406 |
| GET with `Accept: text/event-stream` | 200 |
| HEAD | 405 |

All protocol requests used the configured authorization path without printing or persisting its value. Response bodies were evaluated in memory and only pass/fail, tool names, protocol version, and HTTP statuses were retained

## Runtime Preservation

- Container state: running and healthy
- Restart count: 0
- OOM killed: false
- Image ID: unchanged
- Container start time: unchanged

No restart, recreation, route, MCP registration/access, credential, source, configuration, image, or tag mutation occurred
