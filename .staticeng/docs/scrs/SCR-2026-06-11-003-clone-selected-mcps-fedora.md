---
scr_id: SCR-2026-06-11-003-clone-selected-mcps-fedora
status: implemented
owner: product_manager
created: 2026-06-11
related_task: TASK-2026-06-11-003-clone-selected-mcps-fedora
---

# SCR-2026-06-11-003: Clone Selected MCPs To Fedora LiteLLM Defend

## Problem

`litellm.defend.tech` was reset and needs only a curated subset of MCP servers from `litellm.staticduo.com`. The selected MCPs must be added according to their deployment type. Docker-backed MCPs should be cloned to Fedora under `~/docker/mcp/` in a single `docker-compose.yaml`. Online MCPs should be registered directly against their upstream URL. Some services with backing databases must have their associated DB/state cloned.

## Approved Scope

Clone/register:
- Notion
- ClickUp
- Exa_Web_Search
- Context7
- Kindly_Web_Search
- Firecrawl
- Memory, including associated DB/state
- Qdrant, including associated DB/state if not already cloned
- Neo4j, including associated DB/state if not already cloned
- 1Password
- LiteLLM_Admin, pointing at `litellm.defend.tech`
- PlayWright

Do not add:
- ComfyUI MCPs
- Agent_Jake_Browser
- Wacli
- Google Workspace
- Keycloak
- Syncthing
- Immich
- Cloudflare
- HomeAssistant
- Plane
- Adguard
- Nginx Proxy Manager

## Constraints

- Do not modify `litellm.staticduo.com` except read-only inventory/export.
- Preserve auth/config for cloned MCPs without exposing secrets in logs.
- Do not use the current session's LiteLLM admin MCP for these operations.
- Fedora Docker path: `/home/staticduo/docker/mcp/`.
- Fedora stack must use one `docker-compose.yaml` for cloned MCP services.

## Acceptance Criteria

AC-1. Fedora has `/home/staticduo/docker/mcp/docker-compose.yaml` with selected Docker-backed MCP services and required support services/state.

AC-2. Online selected MCPs are registered in `litellm.defend.tech` without unnecessary local containers.

AC-3. `litellm.defend.tech` MCP list contains only the selected MCP set from this request plus any explicitly required support registration.

AC-4. LiteLLM_Admin MCP on Fedora points to `litellm.defend.tech`/local Fedora LiteLLM, not `litellm.staticduo.com`.

AC-5. Health/listing checks verify registered MCPs are reachable where possible.
