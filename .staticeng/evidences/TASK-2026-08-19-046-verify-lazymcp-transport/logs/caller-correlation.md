# Sanitized Caller Correlation

## Correlation

LiteLLM runtime logs show the repeated sequence arriving from NPM's container address because NPM is the immediate reverse proxy. NPM access logs preserve the original client and identify:

- Client IP: `10.71.14.220`
- Host mapping: Fedora primary Ethernet address
- User agent for repeated invalid probes: `python-httpx/0.28.1`
- Methods/statuses: `HEAD` 405 and generic `GET` 406
- The same source and user agent also complete successful `POST` 200 requests
- Separate protocol-correct Node client traffic identifies as `undici` and completes POST 200, notification POST 202, and SSE GET 200
- Current OpenCode traffic identifies separately as `opencode/1.18.18`

The NPM daily access-log aggregate for the Fedora source contained thousands of repeated Python HTTPX `HEAD` 405 and `GET` 406 entries alongside successful `POST` 200 entries. This proves transport availability and a client-side probe loop rather than an endpoint outage

## Caller Decision

Fedora has both clients configured for `https://litellm.staticduo.com/lazymcp` with Streamable HTTP:

- Hermes is Python and uses HTTPX
- OpenClaw is Node and uses Undici

The bad probe user agent therefore maps to Hermes with high confidence. OpenClaw accounts for the distinct successful Undici sequences. No secret-bearing configuration line was retained

## Minimum Correction

Correct the Hermes health/reconnect check, not LiteLLM:

1. Do not use HEAD for an MCP endpoint
2. Do not use a generic GET with `Accept: */*`
3. Prefer initialize plus tools/list for readiness
4. If using GET for the optional server stream, send `Accept: text/event-stream` and treat an open 200 stream as success

No client or service mutation was performed during this investigation
