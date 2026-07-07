---
id: DISCUSSION-003
title: "Fix LazyMCP ClickUp and Vercel registrations"
status: closed
summarized_by: business_analyst
source: runtime-transcript
---

# Discussion Summary

## Topic
Fix slow or broken LazyMCP discovery caused by ClickUp and Vercel MCP registrations.

## Purpose
Identify why LazyMCP/OpenCode MCP discovery is slow or bloated, determine which MCP servers are responsible, and prepare follow-up workflow to make the ClickUp and Vercel MCP registrations functional or remove them from discovery.

## Repository Truth Relevant To This Discussion
- LazyMCP/LiteLLM currently exposes a broad global MCP catalog to OpenCode rather than a scoped toolset.
- Current LazyMCP status reported `route_restricted=false` and `toolset_scoped=false`.
- The gateway currently sees `26` MCP servers and `535` tools.
- Unfiltered `lazymcp_mcp_describe` can produce very large context payloads because it includes tool schemas from many servers.
- `litellm_admin-list_mcp_servers` returns extensive metadata/configuration, potentially sensitive and context-heavy; its full output should not be pasted into chat or used wholesale as context.

## Facts Established
- Initial discovery normally calls `tools/list` per MCP server to build the available tools catalog.
- LazyMCP/LiteLLM may serve some empty or indexed `describe` output from registered metadata such as `allowed_tools`, aliases, and descriptions.
- Full schemas, servers without `spec_path`, cold caches, stdio MCPs, and remote MCPs may require querying or starting upstream servers.
- If discovery queries servers one-by-one, a single slow or broken upstream can add significant cumulative latency.
- Large servers observed in the catalog include `keycloak` with 85 tools, `google_workspace` with 65 tools, `immich` with 47 tools, `plane` with 47 tools, and `comfyui_workflow` with 41 tools.
- `memory-find` took about 46 seconds even though its backend services were fast, suggesting latency in the memory agent/gateway path rather than `lazymcp_describe` itself.
- LiteLLM logs repeatedly showed `clickup` discovery failures: `Timeout while listing tools from clickup`.
- LiteLLM logs repeatedly showed `vercel` discovery failures: `ConnectError: [Errno -2] Name or service not known` while attempting `http://vercel-mcp-compat:8000/mcp`.
- `clickup` appears to be the real slow server because it waits until timeout during `tools/list`.
- `vercel` appears misregistered or broken because hostname `vercel-mcp-compat` does not resolve from the LiteLLM container.
- Both `clickup` and `vercel` appeared with `0 tools` in `lazymcp_describe` while other sampled servers responded.
- No configuration changes were made during the discussion.

## Requirements Captured
- Fix the ClickUp MCP registration so it works reliably or remove it from the active OpenCode discovery path if it is not intended to be used.
- Fix the Vercel MCP registration so LiteLLM can resolve and reach the correct MCP service endpoint, or remove the broken registration.
- Prevent broken or slow MCP servers from blocking or significantly slowing global discovery.
- Prefer filtered LazyMCP inspection for future investigation, using `lazymcp_mcp_describe` with `server` and `tool` when possible.
- Avoid using unfiltered `litellm_admin-list_mcp_servers` output as broad context because it is large and may include sensitive configuration metadata.

## Constraints
- Do not paste sensitive LiteLLM admin MCP server metadata into discussion or task artifacts.
- Avoid unfiltered `lazymcp_mcp_describe` except when only the server index is needed.
- Current setup is not route-restricted or toolset-scoped, so changes should account for the global catalog being loaded by OpenCode.
- ClickUp may be stdio or otherwise slow to initialize/list tools; discovery timeout behavior must be considered.
- Vercel currently points at `http://vercel-mcp-compat:8000/mcp`, which is not resolvable from the LiteLLM container.

## Non-Goals
- Do not optimize every large MCP server in the catalog as part of the immediate fix.
- Do not change the memory MCP latency path unless it becomes part of a separate investigation.
- Do not expose or duplicate full sensitive LiteLLM admin configuration in task notes.
- Do not assume ClickUp should be removed permanently without confirming whether it is needed in OpenCode.

## Decisions Made
- `clickup` and `vercel` are the primary MCP registrations to fix for this issue.
- Recommended remediation order is: first disable/remove `clickup` from the `opencode` group if unused, second fix or remove `vercel`, third add low timeouts and/or remove them from global discovery if they must remain registered.
- Filtered `lazymcp_mcp_describe` calls should be used for targeted MCP inspection, for example `{"server":"memory","tool":"memory-find"}` or at minimum `{"server":"memory"}`.

## Assumptions
- The relevant LiteLLM/OpenCode MCP configuration includes an `opencode` group or equivalent route/toolset grouping.
- The LiteLLM container must be able to resolve any hostname used in MCP server URLs.
- If ClickUp and Vercel are required by users, the desired outcome is working registrations rather than deletion.
- If either MCP is not required for OpenCode, removing it from global discovery is acceptable mitigation.

## Open Questions
- Is ClickUp actually required in the OpenCode MCP group, or can it be disabled/removed from that group?
- What is the intended deployment target and reachable URL for the Vercel MCP server from inside the LiteLLM container?
- Is `vercel-mcp-compat` supposed to be a Docker Compose service, DNS alias, external hostname, or stale registration?
- Where is the authoritative MCP registration stored for ClickUp and Vercel in this repository/environment?
- What timeout value should be used for slow MCP discovery if timeout tuning is supported by the gateway configuration?
- Should the broader OpenCode MCP catalog be route-scoped/toolset-scoped as a follow-up, beyond fixing ClickUp and Vercel?

## Risks Or Concerns
- Leaving `clickup` enabled in global discovery may continue causing startup or discovery delays due to repeated `tools/list` timeouts.
- Leaving `vercel` registered with an unresolvable hostname may continue producing errors and `0 tools` in LazyMCP.
- Removing either registration without confirming usage could break workflows that depend on ClickUp or Vercel tools.
- Full MCP admin metadata may include sensitive configuration and should be handled carefully.
- Large MCP schemas can inflate context and cause avoidable token/cost overhead if unfiltered discovery outputs are used.

## Referenced Files Or Areas
- `.staticeng/.config/runtime/discussions/DISCUSSION-003-transcript.md`
- LazyMCP/LiteLLM MCP gateway configuration and registry
- OpenCode MCP route/toolset grouping, especially the `opencode` group if present
- LiteLLM logs containing ClickUp and Vercel MCP discovery errors
- ClickUp MCP registration
- Vercel MCP registration
- Vercel MCP endpoint `http://vercel-mcp-compat:8000/mcp`

## Recommended Workflow Next Step
- assigned_to: tech_lead
- why: Requires technical investigation of LiteLLM MCP registration storage, container DNS/network reachability, safe configuration changes for ClickUp and Vercel, and verification that LazyMCP discovery no longer times out or reports these servers as broken.
