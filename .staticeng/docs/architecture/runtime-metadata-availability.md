# Runtime metadata availability

Router deployment metadata must survive price-map reloads regardless of whether the router was initially constructed with a model list. DB-only routers start empty and receive deployments later. The live-router weak set includes these routers, while discard removes their contribution. Replay uses current deployments rather than retaining deleted entries. This preserves custom backend Responses mode and other registered metadata without changing fallback or cooldown policy

Standard MCP initialization gathers optional upstream instructions only for allowed servers. Header resolution, credential/client creation and the initialization session share a per-server deadline capped by the smaller of MCP_METADATA_TIMEOUT and MCP_HEALTH_CHECK_TIMEOUT. A failed or expired optional probe contributes no instructions, retains the existing probe cooldown and does not cancel healthy peers. YAML overrides, cached instructions, per-user-auth exclusions and server scope remain unchanged

Aggregate tool listing gives each allowed peer one MCP_TOOL_LISTING_TIMEOUT deadline covering credential/header setup, client creation, listing and permission filtering. Expiry cancels and drains that peer in its own task and contributes a timeout outcome, even when an inner client converts cancellation into a listing fault. Healthy peers remain available; cancellation of the aggregate request propagates and drains its children. Scoped listing continues to use its existing error contract

These deadlines do not change upstream tool execution timeouts, health status or registration state. Tool listing retains its existing per-server fault outcomes and permission filtering. Unavailable integrations must remain visible as unavailable rather than being deleted, disabled or represented as successful empty servers

Verification lives in tests/test_litellm/test_router_model_cost_isolation.py and tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py

## Deployment bootstrap

Fedora and NAS persist their own mounted start-litellm.sh wrappers and invoke the image's /app/docker/prod_entrypoint.sh with exec. Neither wrapper installs PostgreSQL clients or repeatedly alters schema at startup. The source_url column exists in both databases and the maintained Prisma schema; ordinary application migration/startup owns database readiness and schema lifecycle

Fedora retains its pre-existing, guarded synthetic Responses health-check correction before exec. NAS has no such host-specific patch and goes directly to the image entrypoint. These host differences are intentional: the image digest is shared, but Fedora's existing health-file override is not copied to NAS or misrepresented as byte-identical runtime files

The persistent host paths are /home/staticduo/docker/litellm/start-litellm.sh on Fedora and /volume2/docker/litellm/start-litellm.sh on NAS, mounted as /app/start-litellm.sh by each host's actual docker-compose.yaml. Secret-free final wrapper snapshots and checksums are retained in the TASK-2026-09-05-002 evidence config directory. Host-specific .env/configuration and original wrappers remain in owner-only release backups on each host, never in source control
