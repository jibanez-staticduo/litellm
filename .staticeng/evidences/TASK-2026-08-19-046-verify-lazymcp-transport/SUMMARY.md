# LazyMCP Transport Investigation

## Summary

NAS LazyMCP is **WORKING**. A fresh protocol-correct Streamable HTTP flow and the connected LazyMCP client both passed discovery, status, bounded description, and harmless delegated-call checks. No LiteLLM fix or runtime/configuration mutation is needed

The 406 and 405 responses are valid protocol enforcement against a noisy client probe pattern, not LazyMCP failures. Generic `GET` does not advertise SSE support and `HEAD` is not a Streamable HTTP operation. The same Fedora client continues to complete successful MCP `POST` requests

## Work Performed

- Reviewed the active task, repository guidance, relevant CodeMap, prior NAS/Fedora LazyMCP evidence, current LiteLLM route wiring, and the official MCP Streamable HTTP specification
- Ran a fresh stateless initialize, initialized notification, tools/list, `mcp_status`, bounded `mcp_describe`, and harmless `mcp_call` flow against NAS
- Compared generic `GET`, protocol-compatible SSE `GET`, and `HEAD` behavior
- Correlated LiteLLM and Nginx Proxy Manager access logs with source IP, user agent, method, and status
- Mapped the caller IP to Fedora and compared the configured Python Hermes and Node OpenClaw clients without reading or persisting credential values
- Rechecked NAS container identity and health after investigation

## Acceptance Criteria Coverage

- **AC-1: PASS**. Streamable HTTP sends JSON-RPC through `POST` with `Accept: application/json, text/event-stream`; successful notifications return 202 and requests return JSON or SSE. `GET` is an optional server-to-client SSE stream and must advertise `Accept: text/event-stream`; a generic `GET` therefore returns 406. `HEAD` is not an MCP Streamable HTTP operation and returns 405. NAS LazyMCP is intentionally stateless, so initialize does not issue `MCP-Session-Id`; stateful servers would require the issued session ID on subsequent requests. See `.staticeng/evidences/TASK-2026-08-19-046-verify-lazymcp-transport/logs/protocol-verification.md`
- **AC-2: PASS**. Initialize negotiated protocol `2025-11-25`, the initialized notification returned 202, and tools/list returned exactly `mcp_call`, `mcp_describe`, and `mcp_status`. See `.staticeng/evidences/TASK-2026-08-19-046-verify-lazymcp-transport/logs/protocol-verification.md`
- **AC-3: PASS**. `mcp_status`, bounded `memory` / `memory-find` describe, and one harmless delegated `memory-find` call completed without JSON-RPC or tool error. See `.staticeng/evidences/TASK-2026-08-19-046-verify-lazymcp-transport/logs/protocol-verification.md`
- **AC-4: PASS**. NPM identifies repeated 405/406 requests as Fedora `10.71.14.220` with user agent `python-httpx/0.28.1`; the same source also sends successful POST requests. Fedora has Python Hermes and Node OpenClaw configured for this endpoint. OpenClaw traffic identifies as `undici`, while the bad probes identify as Python HTTPX, making Hermes the high-confidence caller. See `.staticeng/evidences/TASK-2026-08-19-046-verify-lazymcp-transport/logs/caller-correlation.md`
- **AC-5: PASS**. LiteLLM needs no correction. The minimum client correction is to remove Hermes `HEAD` readiness probes and generic `GET` probes, then verify connectivity with initialize/tools-list or an SSE `GET` carrying `Accept: text/event-stream`. NAS remained healthy and unchanged

## Documentation Impact

No product, architecture, technical, or CodeMap documentation update is required. This investigation confirms existing protocol behavior and identifies a correction in an external client configuration/implementation boundary

## Open Risks

The Hermes probe loop creates avoidable access-log noise and request volume until corrected. It does not currently prevent successful LazyMCP POST traffic. The exact Hermes function producing the probes was not instrumented because attaching packet/syscall tooling would have exceeded the read-only scope; source IP, runtime, user agent, language stack, and contrasting OpenClaw user agent provide high-confidence attribution

## Recommended Next Step

PMA should route a separate Hermes client task to replace the `HEAD` plus generic `GET` health/reconnect sequence with a protocol-correct Streamable HTTP readiness check. Do not change LiteLLM
