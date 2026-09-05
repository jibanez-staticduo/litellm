# Runtime metadata availability

Router deployment metadata must survive price-map reloads regardless of whether the router was initially constructed with a model list. DB-only routers start empty and receive deployments later. The live-router weak set includes these routers, while discard removes their contribution. Replay uses current deployments rather than retaining deleted entries. This preserves custom backend Responses mode and other registered metadata without changing fallback or cooldown policy

Standard MCP initialization gathers optional upstream instructions only for allowed servers. Header resolution, credential/client creation and the initialization session share a per-server deadline capped by the smaller of MCP_METADATA_TIMEOUT and MCP_HEALTH_CHECK_TIMEOUT. A failed or expired optional probe contributes no instructions, retains the existing probe cooldown and does not cancel healthy peers. YAML overrides, cached instructions, per-user-auth exclusions and server scope remain unchanged

Aggregate tool listing gives each allowed peer one MCP_TOOL_LISTING_TIMEOUT deadline covering credential/header setup, client creation, listing and permission filtering. Expiry cancels and drains that peer in its own task and contributes a timeout outcome, even when an inner client converts cancellation into a listing fault. Healthy peers remain available; cancellation of the aggregate request propagates and drains its children. Scoped listing continues to use its existing error contract

These deadlines do not change upstream tool execution timeouts, health status or registration state. Tool listing retains its existing per-server fault outcomes and permission filtering. Unavailable integrations must remain visible as unavailable rather than being deleted, disabled or represented as successful empty servers

Verification lives in tests/test_litellm/test_router_model_cost_isolation.py and tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py
