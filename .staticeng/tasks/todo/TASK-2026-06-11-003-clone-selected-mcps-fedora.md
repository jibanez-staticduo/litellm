---
task_id: TASK-2026-06-11-003-clone-selected-mcps-fedora
complexity: complex
track: implementation
slice: core
status: done
assigned_to: product_manager
handoff_from: product_manager
scr: SCR-2026-06-11-003-clone-selected-mcps-fedora
parent: none
discussion: DISCUSSION-002
---

# Clone Selected MCPs To Fedora LiteLLM Defend

## Classification

- complexity: complex
- track: implementation
- slice: core

## Context

The user wants selected MCPs from `litellm.staticduo.com` available in `litellm.defend.tech`, but deployed differently per MCP. Docker-backed MCPs must be cloned to Fedora under `/home/staticduo/docker/mcp/` in a single `docker-compose.yaml`. Some online MCPs should be registered directly. Memory/Qdrant/Neo4j require associated DB/state cloning.

Do not touch `litellm.staticduo.com` except read-only inventory/export. Do not add excluded MCPs.

## Requested MCP Decisions

Clone/register selected:
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

## Acceptance Criteria

AC-1. Fedora has `/home/staticduo/docker/mcp/docker-compose.yaml` with selected Docker-backed MCP services and required support services/state.

AC-2. Online selected MCPs are registered in `litellm.defend.tech` without unnecessary local containers.

AC-3. `litellm.defend.tech` MCP list contains only the selected MCP set from this request plus any explicitly required support registration.

AC-4. LiteLLM_Admin MCP on Fedora points to `litellm.defend.tech`/local Fedora LiteLLM, not `litellm.staticduo.com`.

AC-5. Health/listing checks verify registered MCPs are reachable where possible.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-06-11-003-clone-selected-mcps-fedora/` with:
- `SUMMARY.md` mapping ACs to verification.
- logs for inventory, compose validation, deploy, MCP registration/listing, and health checks.
- do not include secrets in evidence.

## Handoff

[Agent Message] From: product_manager To: technical_architect
Please perform a read-only impact map and implementation plan first. Inventory `/volume2/docker/mcp/docker-compose.yaml`, related env/build contexts, current `litellm.staticduo.com` MCP definitions via API if needed, and Fedora `/home/staticduo/docker/mcp` state. Classify each selected MCP as online-only, clone-local, or clone-with-state. Identify exact files/dirs/volumes to copy, registration payloads, risks, and recommended execution order. Do not modify files yet. Return the plan and blockers.
