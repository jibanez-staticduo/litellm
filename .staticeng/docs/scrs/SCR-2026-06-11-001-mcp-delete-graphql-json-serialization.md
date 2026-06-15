---
scr_id: SCR-2026-06-11-001-mcp-delete-graphql-json-serialization
status: approved
owner: product_manager
created: 2026-06-11
related_task: TASK-2026-06-11-001-fix-mcp-delete-json-serialization
---

# SCR-2026-06-11-001: MCP Delete JSON Serialization Fix

## Problem

Deleting MCP servers on Fedora `litellm.defend.tech` fails with a Prisma GraphQL parse error while cleaning `LiteLLM_ObjectPermissionTable.mcp_tool_permissions`.

Observed failure:

`prisma.errors.DataError: Error parsing GraphQL query: query parse error`

The delete path updates `mcp_tool_permissions` with a Python dict containing UUID keys. Other object permission write paths serialize this JSON field with `safe_dumps` to avoid Prisma GraphQL parsing issues.

## Approved Behavior

MCP delete cleanup must serialize `mcp_tool_permissions` consistently before Prisma object permission updates, so server deletion succeeds when tool permission maps contain server UUID keys.

## Scope

In scope:
- Fix cleanup serialization in MCP delete references code.
- Add or update regression tests for dict and string `mcp_tool_permissions` cleanup.
- Release/deploy the hotfix to Fedora `litellm.defend.tech`.

Out of scope:
- Direct DB deletion as the primary fix.
- Changes to `litellm.staticduo.com`.

## Acceptance Criteria

AC-1. Deleting an MCP server with object permission `mcp_tool_permissions` keyed by server UUID does not raise Prisma GraphQL parse errors.

AC-2. Cleanup removes the deleted server id from `mcp_servers` and `mcp_tool_permissions`.

AC-3. Regression tests cover the serialization behavior.

AC-4. Fedora `litellm.defend.tech` can delete the Keycloak MCP server or has the MCP removed through the fixed endpoint.
