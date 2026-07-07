# Evidence Summary

Task: TASK-2026-06-29-001-fix-clickup-vercel-mcp

## Summary

Reopen completed. The authorized ClickUp skill/config under `fedora:/home/staticduo/.config/opencode_defend/skills/clickup` was located using read-only SSH inspection, then synced into the current installed ClickUp skill. The ClickUp MCP registration in LiteLLM was rebuilt from the authorized config/token without printing or persisting secret values in evidence. Vercel MCP was removed from this LiteLLM instance.

## Reopen Acceptance Criteria Coverage

- RAC-1: Met. Read-only SSH inspection located `opencode_defend` at `/home/staticduo/.config/opencode_defend` and found the authorized ClickUp skill at `/home/staticduo/.config/opencode_defend/skills/clickup`. Evidence records only file paths, sizes, and env key names, not values.
- RAC-2: Met. The local installed ClickUp skill at `/home/staticduo/.config/opencode/skills/clickup` was synced from the authorized `fedora` skill. LiteLLM ClickUp MCP was registered from the authorized env via the admin API inside the `litellm` container; token values were never printed and are not included in evidence.
- RAC-3: Met. Vercel MCP was removed. Final LazyMCP discovery no longer lists `vercel`, and `lazymcp_mcp_describe(server="vercel")` returns that the MCP server is unavailable.
- RAC-4: Met. `lazymcp_mcp_describe(server="clickup")` returns usable ClickUp tool metadata, and all-server LazyMCP discovery lists `clickup` with 13 tools. Vercel is no longer visible.
- RAC-5: Met. Evidence was appended under this packet with sanitized reopen logs: `.staticeng/evidences/TASK-2026-06-29-001-fix-clickup-vercel-mcp/logs/reopen_registry_status_sanitized.log` and `.staticeng/evidences/TASK-2026-06-29-001-fix-clickup-vercel-mcp/logs/reopen_verification_sanitized.log`.

## Original Acceptance Criteria Coverage

- AC-1: Met on reopen. ClickUp discovery returns tools and no final verification-window ClickUp timeout was observed.
- AC-2: Superseded by reopen decision. The user explicitly changed the Vercel requirement to removal rather than repair.
- AC-3: Met on reopen for ClickUp; Vercel unavailable by design after removal.
- AC-4: Met on reopen. Final verification logs show no repeated ClickUp timeout and no `vercel-mcp-compat` DNS failure in the final post-restart window.
- AC-5: Met. The evidence packet contains `SUMMARY.md` plus sanitized logs.

## Commands And Tools

- `ssh fedora` read-only path/config discovery with redacted output.
- `rsync` from the authorized `fedora` ClickUp skill to the local installed ClickUp skill.
- LiteLLM admin MCP/API for Vercel deletion and ClickUp MCP registration.
- `docker restart litellm` to refresh the in-memory MCP registry.
- `lazymcp_mcp_status`, `lazymcp_mcp_describe()`, `lazymcp_mcp_describe(server="clickup")`, and `lazymcp_mcp_describe(server="vercel")` for verification.
- Sanitized in-container `/v1/mcp/server` inspection and filtered `docker logs` checks.

## Sanitization

Evidence intentionally omits credential values, tokens, static headers, API keys, and raw env values. Logs record only env key names and sanitized registry metadata.

## Remaining External Action

No blocker remains for LazyMCP discovery. If runtime ClickUp tool calls later fail, the safest next check is a redacted direct tool smoke test against a known non-sensitive ClickUp object or a token validity check that does not print the token.
