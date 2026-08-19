---
id: TASK-2026-08-19-046-verify-lazymcp-transport
complexity: standard
track: investigation
slice: qa
status: done
scr: null
parent: null
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-046 - Verify LazyMCP Transport

## Objective
Verify whether NAS LazyMCP is functional and determine why generic GET and HEAD probes return 406/405 while MCP POST requests return 200.

## Safety
- Read-only investigation first; do not restart/recreate LiteLLM, alter MCP registrations/access/routing/credentials, deploy images, or move tags.
- Use protocol-correct Streamable HTTP MCP requests and inspect sanitized logs/status only.
- If a real defect exists, identify the minimum fix and return it to PMA before mutation.

## Acceptance Criteria
- [ ] AC-1: Explain protocol semantics for POST, GET, and HEAD on `/lazymcp`, including required Accept headers/session behavior.
- [ ] AC-2: Run a protocol-correct initialize/list-tools flow and confirm exactly `mcp_status`, `mcp_describe`, and `mcp_call` are exposed.
- [ ] AC-3: Execute `mcp_status`, bounded describe, and one harmless `mcp_call` against a configured server.
- [ ] AC-4: Correlate 406/405 requests with client IP/user-agent/header behavior and identify the caller when possible.
- [ ] AC-5: Decide whether any LiteLLM fix/config/client correction is needed; preserve runtime if healthy.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-046-verify-lazymcp-transport/` with sanitized protocol/status logs.

## Handoff
[Agent Message] From: product_manager To: tech_lead

Verify NAS LazyMCP end-to-end using protocol-correct Streamable HTTP. Explain 406/405 probes and identify the caller/header mismatch when possible. Do not mutate healthy runtime. Return explicit working/broken decision and minimum correction.

# Post Implementation Task Updates

## Tech Lead: Initial Investigation Results
- AC-1 through AC-5 passed for protocol-correct behavior.
- POST initialize/list-tools/status/describe/call works end-to-end; generic GET returns 406 and HEAD returns 405 under current implementation.
- Repeated probes correlate to a Fedora `python-httpx/0.28.1` caller, likely Hermes.
- User explicitly requested source-level compatibility review before accepting client-only disposition.

## PMA Final Closure
- Protocol-correct LazyMCP functionality passed, and the repeated 405/406 compatibility problem was accepted as a LiteLLM source issue for TASK-048.
- Source correction and release verification supersede the initial client-only disposition.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- AC-1 through AC-5 passed
- NAS LazyMCP is working; no LiteLLM source, configuration, proxy, or runtime correction is required
- A protocol-correct stateless initialize/initialized/list-tools flow negotiated MCP `2025-11-25`, exposed exactly `mcp_call`, `mcp_describe`, and `mcp_status`, and completed status, bounded describe, and harmless delegated call checks
- Generic `GET` with `Accept: */*` correctly returned 406, session-compatible `GET` with `Accept: text/event-stream` returned 200, and unsupported `HEAD` correctly returned 405
- NPM and runtime logs attribute the repeated 406/405 probes to Fedora `10.71.14.220` using `python-httpx/0.28.1`; the configured Python Hermes Streamable HTTP client is the high-confidence source, while OpenClaw uses `undici` and protocol-correct POST/GET traffic
- The minimum correction belongs in the Hermes client health/reconnect probe: remove `HEAD`, do not send generic `GET`, and use protocol-correct initialize/list-tools or an SSE `GET` with `Accept: text/event-stream`
- LiteLLM remained healthy on the unchanged image and start time with zero restarts and no OOM event; no service, route, registration, access, credential, source, configuration, image, or tag mutation occurred
