# Bounded NAS diagnosis

Daemon identity verified: nas, 8d5cc9c3-ebfb-43e7-b6ff-bb2112a49b4f. Container remains 6b6f8743c69dab2a768dc76bef046511c7486bf0627d3fc0bc0a587bd4ff314c, healthy, restart=0, OOM=false, approved image index 7b2368711ff10db3107772d627e03aa89319598f8897ff7431497775926b2eb9

Supported API reads were issued through container loopback with the existing administrator credential held only in process memory. Returned records were projected before output. No raw exception payload, credential, MCP URL or tool content was retained

GET /model/info: all four Astra aliases use chatgpt/gpt-6-astra, mode=responses. Public and account2/account3 aliases have a configured profile; default alias does not. GET /router/settings preserves public fallback [chatgpt-account2/gpt-6-astra, chatgpt/gpt-6-astra], cross-profile fallback=true, retries=1, allowed_fails=1, cooldown=30

GET /public/litellm_model_cost_map: chatgpt/gpt-6-astra absent; gpt-6-astra openai/chat; chatgpt/gpt-5.6-sol chatgpt/responses. Targeted config search found store_model_in_db=true and no top-level model_list. Source proxy_server.py builds router_params without model_list in this case

POST /v1/chat/completions, public gpt-6-astra, synthetic Reply only OK, stream=false: HTTP 403 in 8.33 and 8.90 seconds. Error classification: ChatgptException/APIError, Codex chat/completions URL, browser-challenge markers Enable JavaScript and cf_chl. No usage_limit_reached or insufficient_quota marker. Historical 429 no-deployment/cooldown is recorded in the parent evidence, not reproduced as a fresh quota result

POST /v1/responses with same alias and synthetic input: HTTP 200 in 6.21 seconds, object=response, status=completed, deployment ID matches account2. No retries, cooldowns, fallback order or provider constraints were altered

POST /mcp initialize with protocolVersion=2025-03-26 and empty capabilities: HTTP 504 in 30.01 seconds. GET /v1/mcp/server/health: 24 healthy, three unhealthy matching frigate_observe, frigate_admin and frigate_breakglass. Each registered host/port failed socket.create_connection(timeout=3) from the LiteLLM container in 3.00 seconds. This establishes TCP unavailability from the gateway, not its remote infrastructure cause

Environment projection: LITELLM_MCP_HEALTH_CHECK_TIMEOUT=30, LITELLM_MCP_CLIENT_TIMEOUT=180, LITELLM_MCP_METADATA_TIMEOUT unset (default 10). Optional initialize instructions previously waited for the health timeout; client/header setup had no encompassing metadata deadline

No production mutation or deployment was performed

Follow-up GET /mcp-rest/tools/list without a server selector exceeded a 40.05-second client deadline. LITELLM_MCP_TOOL_LISTING_TIMEOUT is unset, default=30. This is an additional unresolved aggregate path, not a passed listing check. The targeted source instruction-prefetch change has not been loaded into the running service
