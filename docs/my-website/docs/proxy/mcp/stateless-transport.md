# Stateless Streamable HTTP

Clients that do not need persistent MCP sessions can send `x-litellm-mcp-session-mode: stateless` on every request to `/mcp`, including `initialize`. Use the same LiteLLM admission credential and `x-mcp-servers` filter as usual. This header changes transport selection only; authentication, server permissions, tool permissions and IP restrictions still apply

The gateway creates a request-local MCP transport, returns no `mcp-session-id`, and does not register a stateful session or consume the per-caller stateful session quota. POST responses may still use SSE for the duration of that request. Initialized notifications return HTTP 202

GET and DELETE return HTTP 405 with `Allow: POST`. There is no persistent GET event stream, cross-request session state, resumption, or cross-request sampling/elicitation response channel. Clients requiring these features must keep the default transport

The header accepts exactly one value, `stateless`. Empty, unknown or repeated values return HTTP 400. Combining it with any `mcp-session-id` header also returns HTTP 400, including stale or empty session IDs; the gateway does not strip the ID or delete the existing session. Admission authentication runs before these checks

Without the header, behavior is unchanged: initialize creates a stateful session, existing session IDs retain ownership enforcement, and requests without an ID other than initialize use the existing stateless path. Omitting the opt-in header on a later initialize therefore creates a stateful session

## Rollout And Rollback

Build and validate the patch in an isolated gateway first, with the deployed MCP SDK version. Verify initialize, scoped tool discovery, notification handling, GET rejection, tool execution and client reconnect behavior before changing production

For clients with multiple independent MCP entries, configure the opt-in header on each entry and keep a distinct `x-mcp-servers` value per entry. Test at least four concurrent client instances with 28 entries each and confirm that stateful session registries do not grow. Do not remove an existing gateway integration until direct tool execution has passed

Production deployment and client configuration changes require separate approval. Roll back by removing the opt-in header and reconnecting clients, or restoring the previous gateway build. This returns to the previous stateful quota and lifetime behavior
